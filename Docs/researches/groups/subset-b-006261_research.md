# subset-b-006261 Research

This grouped report covers PSP netlink/socket glue, Qualcomm QRTR core/transports/nameservice, and RDS core plus RDS/IB connection and memory-registration paths. Each section preserves the original source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/psp/psp_nl.c -->
# sources/distributed-fs/ceph-client/net/psp/psp_nl.c

## Purpose
`psp_nl.c` implements PSP generic-netlink management operations. It exposes device discovery/configuration, key rotation, RX/TX association setup for TCP sockets, and PSP device statistics. It is the control-plane bridge between userspace netlink clients and PSP device/socket internals.

## Important APIs, Types, And Functions
Key public entry points are `psp_device_get_locked()`, `psp_device_unlock()`, `psp_nl_dev_get_doit()`, `psp_nl_dev_get_dumpit()`, `psp_nl_dev_set_doit()`, `psp_nl_key_rotate_doit()`, `psp_assoc_device_get_locked()`, `psp_nl_rx_assoc_doit()`, `psp_nl_tx_assoc_doit()`, `psp_nl_get_stats_doit()`, and `psp_nl_get_stats_dumpit()`. Helpers `psp_nl_reply_new()` and `psp_nl_reply_send()` create single-message generic-netlink replies. `psp_nl_dev_fill()` and `psp_nl_stats_fill()` serialize device and stats attributes. `psp_nl_parse_key()` and `psp_nl_put_key()` translate nested key attributes with SPI and raw key bytes.

The code depends on generated PSP netlink policy and family definitions from `psp-nl-gen.h`, and on core PSP structures and operations from `psp.h`/`net/psp.h`: `struct psp_dev`, `struct psp_assoc`, `struct psp_key_parsed`, `struct psp_dev_config`, and driver `psd->ops`.

## Control Flow
Device operations first resolve a device id from `PSP_A_DEV_ID`, take the global `psp_devs_lock`, look up `psp_devs` by xarray id, then take the device mutex and check namespace/device access. Get/dump paths serialize device state into generic-netlink messages. Set validates requested enabled PSP versions against device capabilities, calls `psd->ops->set_config()`, updates cached config, and emits a management notification.

Key rotation creates both an immediate reply and a use-notification. It suggests a next generation number, calls the driver `key_rotate()`, validates the resulting generation, marks associations rotated via `psp_assocs_key_rotated()`, increments stats, multicasts on `PSP_NLGRP_USE`, and replies.

Association operations resolve a TCP socket fd, infer or validate the PSP device attached to the socket route, lock that device, parse version/key attributes, and call socket-layer functions. RX association allocates a `psp_assoc`, asks the driver for an RX SPI/key, returns that key to userspace, and attaches the association to the socket. TX association parses a userspace-provided key and upgrades the existing RX association for transmit.

## State And Persistence
Persistent kernel state touched here is PSP device config, device generation, per-device stats, active association lists indirectly through `psp_assoc_create()`/socket setters, and per-socket PSP association pointers. There is no disk persistence. Lifetime is governed by device mutexes, socket references from `sockfd_lookup()`, PSP device references, and association refcounts.

## Dependencies And Integration Points
This file integrates with generic netlink, xarray device registration, TCP sockets, PSP driver callbacks (`set_config`, `key_rotate`, `rx_spi_alloc`, stats), and PSP socket helpers in `psp_sock.c`. Notifications use `genlmsg_multicast_netns()` for management and use groups.

## Risks
The file is lock-order sensitive: global device lock precedes per-device lock, and association commands keep socket references until post-op unlock. Key material is copied from netlink attributes and returned in netlink responses, so validation of key size and SPI is critical. `psp_nl_reply_send()` assumes a single message per skb. Version checks use `1 << version`, so callers must keep version values in a sane range through policy/ABI. Errors during RX setup must release both the temporary association and reply skb correctly.

## Test Signals
Useful coverage includes netlink policy rejection for missing attributes, unsupported versions, key length/SPI validation, device id/socket mismatch, non-TCP socket fds, set-config no-op versus changed config, key-rotation notifications, dump filtering by namespace access, and stats behavior when driver leaves required counters unset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/psp/psp_nl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/psp/psp_sock.c -->
# sources/distributed-fs/ceph-client/net/psp/psp_sock.c

## Purpose
`psp_sock.c` binds PSP security associations to TCP sockets and time-wait sockets. It provides association allocation/lifetime management, route-device discovery, RX/TX association installation, transmit validation, key-rotation stale handling, and a helper to mark replies decrypted.

## Important APIs, Types, And Functions
Important exported or cross-file functions are `psp_dev_get_for_sock()`, `psp_assoc_create()`, `psp_dev_tx_key_del()`, `psp_assoc_put()`, `psp_sk_assoc_free()`, `psp_sock_assoc_set_rx()`, `psp_sock_assoc_set_tx()`, `psp_assocs_key_rotated()`, `psp_twsk_init()`, `psp_twsk_assoc_free()`, and `psp_reply_set_decrypted()`. Internal helpers include `psp_validate_xmit()`, `psp_assoc_dummy()`, `psp_dev_tx_key_add()`, `psp_assoc_free_queue()`, and `psp_sock_recv_queue_check()`.

## Control Flow
`psp_dev_get_for_sock()` uses RCU to inspect the socket destination cache, read the netdevice's PSP device, and take a weak device ref. Association creation requires the PSP device lock, allocates a flexible structure sized for driver private association data, snapshots device id and generation, takes a device ref, initializes the association refcount, and links it into the device active list.

RX setup copies the allocated key into `pas->rx`, locks the socket, rejects sockets with existing PSP state, takes another association ref, and publishes `sk->psp_assoc` with RCU assignment. TX setup requires an existing RX association on the same device/version and no existing TX SPI. It scans TCP out-of-order and receive queues for PSP skb extensions that do not match the association, creates a dummy association for the driver `tx_key_add()` callback, copies driver private data and TX key into the real association, installs `psp_validate_xmit`, fences TCP write collapse, records the upgrade sequence, and increases TCP external header length before recomputing MSS.

Freeing is RCU-delayed and then workqueue-based because driver key deletion takes the PSP device mutex. Time-wait initialization copies the association ref to the time-wait socket and installs transmit validation. Key rotation moves active associations to previous, previous to stale, and poisons old generations so RX can reject stale traffic.

## State And Persistence
State is in `sk->psp_assoc`, `tw->psp_assoc`, association refcounts, per-device active/previous/stale lists, association generation, driver private data, and TCP socket header/MSS fields. It is volatile and tied to socket/device lifetimes.

## Dependencies And Integration Points
The file integrates with TCP internals (`tcp_sk`, receive queues, out-of-order rb tree, MSS sync), skb extensions (`SKB_EXT_PSP`), destination/netdevice PSP pointers, driver TX key callbacks, and RCU/workqueue lifetime rules. `psp_nl.c` drives RX/TX setup through this file.

## Risks
The TX path must avoid attaching TX keys if any queued received segments belong to different PSP state; otherwise data may be misclassified. The dummy association is a deliberate guard against drivers keeping transient pointers. Lifetime spans RCU and workqueue contexts, so association list deletion and device op availability (`psd->ops`) are sensitive during unregister. TCP header-length mutation must stay paired with PSP overhead semantics.

## Test Signals
Tests should cover duplicate RX/TX setup rejection, device/version mismatch, queued incompatible skb extensions, driver `tx_key_add()` failure, association release after socket close and time-wait conversion, key-rotation list movement/stale stats, and transmit validation dropping skbs whose association device differs from the egress netdevice.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/psp/psp_sock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/qrtr/Kconfig -->
# sources/distributed-fs/ceph-client/net/qrtr/Kconfig

## Purpose
This Kconfig file declares build-time options for Qualcomm IPC Router support and its endpoint transports. QRTR provides datagram-style communication with services on Qualcomm system components.

## Important APIs, Types, And Functions
The config symbols are `QRTR`, `QRTR_SMD`, `QRTR_TUN`, and `QRTR_MHI`. `QRTR` is the core AF_QIPCRTR protocol. `QRTR_SMD` enables RPMSG/SMD channels, `QRTR_TUN` enables a userspace misc-device endpoint, and `QRTR_MHI` enables MHI channels for external modems.

## Control Flow
There is no runtime control flow in this file. Build selection gates which source files are compiled by the QRTR Makefile. Transport options are only visible inside `if QRTR`, so transport drivers cannot be selected without core QRTR support.

## State And Persistence
This file contributes only Kconfig state. Selected options become kernel build configuration and module availability; they do not define runtime persistence.

## Dependencies And Integration Points
`QRTR_SMD` depends on `RPMSG` or compile-test without RPMSG. `QRTR_MHI` depends on `MHI_BUS`. `QRTR_TUN` has no extra dependency. The help text notes that service lookups require a userspace daemon maintaining a service listing, even though this tree also includes an in-kernel nameservice implementation.

## Risks
Misconfigured builds can include core QRTR without a transport, yielding local socket support but no external endpoint. `QRTR_SMD`'s compile-test condition allows build coverage when RPMSG is absent, so runtime assumptions must remain guarded in the driver.

## Test Signals
Build matrix signals are core-only, SMD with RPMSG, TUN, MHI with MHI_BUS, modular versus built-in combinations, and compile-test coverage for SMD.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/qrtr/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/qrtr/Makefile -->
# sources/distributed-fs/ceph-client/net/qrtr/Makefile

## Purpose
The Makefile maps QRTR Kconfig symbols to kernel objects. It defines the composition of the core `qrtr` module and optional transport modules.

## Important APIs, Types, And Functions
`obj-$(CONFIG_QRTR) += qrtr.o` builds the core from `af_qrtr.o` and `ns.o`. `CONFIG_QRTR_SMD`, `CONFIG_QRTR_TUN`, and `CONFIG_QRTR_MHI` build `qrtr-smd.o`, `qrtr-tun.o`, and `qrtr-mhi.o` from `smd.o`, `tun.o`, and `mhi.o`.

## Control Flow
There is no runtime flow. The important build flow is that nameservice `ns.o` is linked into the core QRTR object, while each physical/userspace transport is a separate module/object.

## State And Persistence
The file affects build artifacts only. Runtime state is owned by the compiled source files.

## Dependencies And Integration Points
The object layout means transport modules depend on exported symbols from the core, primarily `qrtr_endpoint_register()`, `qrtr_endpoint_unregister()`, and `qrtr_endpoint_post()`.

## Risks
Because `ns.o` is part of the core object, QRTR core initialization includes nameservice setup and failure paths. Transport modules must handle core module unload and endpoint unregister ordering.

## Test Signals
Build tests should verify object composition for built-in and modular QRTR, and symbol resolution when SMD/TUN/MHI are built as modules against a modular or built-in core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/qrtr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/qrtr/af_qrtr.c -->
# sources/distributed-fs/ceph-client/net/qrtr/af_qrtr.c

## Purpose
`af_qrtr.c` implements the AF_QIPCRTR socket family and the QRTR endpoint core. It manages local QRTR sockets/ports, remote endpoint nodes, packet header parsing/serialization, broadcast/local/remote routing, and QRTR transmit flow control.

## Important APIs, Types, And Functions
Public endpoint APIs are `qrtr_endpoint_register()`, `qrtr_endpoint_unregister()`, and `qrtr_endpoint_post()`. Socket operations include `qrtr_create()`, `qrtr_bind()`, `qrtr_connect()`, `qrtr_sendmsg()`, `qrtr_recvmsg()`, `qrtr_getname()`, `qrtr_ioctl()`, and `qrtr_release()`. Core structures include `struct qrtr_sock`, `struct qrtr_node`, `struct qrtr_tx_flow`, packet headers `qrtr_hdr_v1`/`qrtr_hdr_v2`, and skb control block `struct qrtr_cb`.

## Control Flow
Endpoint drivers register a `struct qrtr_endpoint` with an `xmit` callback. Registration allocates a `qrtr_node`, initializes flow-control xarray and RX queue, optionally assigns a node id, links it into the global node list, and stores the node in the endpoint. Incoming endpoint data enters `qrtr_endpoint_post()`, which validates alignment and header version, extracts source/destination/type/confirm fields, validates payload size and control packet constraints, assigns node ids learned from packets, handles `QRTR_TYPE_RESUME_TX`, or queues the skb to the destination port socket.

Outgoing socket data flows through `qrtr_sendmsg()`. The socket is autobound if needed, destination is selected from msg name or connected peer, and routing chooses broadcast, local enqueue, or node enqueue. Remote sends call `qrtr_node_enqueue()`, which runs `qrtr_tx_wait()` flow control, prepends a v1 QRTR header, pads to 4-byte alignment, and invokes the endpoint `xmit` callback under `ep_lock`. Local and broadcast enqueue copy/queue skbs to local sockets and all known nodes.

Receive dequeues datagrams, returns the source address, and sends a resume-tx control packet if the incoming packet requested confirmation. Endpoint unregister clears the endpoint pointer, emits BYE notifications for all node ids backed by the endpoint, wakes flow-control waiters, and drops the node reference.

## State And Persistence
Global runtime state includes `qrtr_local_nid`, `qrtr_nodes` radix tree, `qrtr_all_nodes` broadcast list, and `qrtr_ports` xarray. Per-node state includes endpoint pointer, kref, nid, flow-control entries, and rx queue. Per-socket state includes bound local sockaddr and connected peer. State is volatile and reset on module unload or socket/endpoint release.

## Dependencies And Integration Points
The file registers `AF_QIPCRTR` as a datagram socket family and initializes QRTR nameservice via `qrtr_ns_init()`. Transport drivers in `mhi.c`, `smd.c`, and `tun.c` use the endpoint API. It uses Linux socket, skb, radix-tree, xarray, RCU, mutex, and waitqueue primitives.

## Risks
Packet parser correctness is critical because endpoint transports pass raw remote data. Flow-control waiters can stall if resume packets are lost; `qrtr_tx_flow_failed()` mitigates lost confirm messages. Node unregister races are controlled by `ep_lock`, node refs, and wakeups, but endpoint removal still stresses blocked senders. Port assignment treats control port as xarray index 0 and requires capability checks for privileged low ports. Broadcast copies may partially fail under memory pressure.

## Test Signals
Coverage should include v1/v2 packet parsing, malformed size/alignment/control packets, auto node assignment, bridge node assignment through NEW_SERVER, local/broadcast/remote send routing, flow-control low/high watermark behavior, resume-tx handling, endpoint unregister wakeups, privileged port binding, socket release DEL_CLIENT broadcast, `TIOCINQ`/`TIOCOUTQ`, and module init failure unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/qrtr/af_qrtr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/qrtr/mhi.c -->
# sources/distributed-fs/ceph-client/net/qrtr/mhi.c

## Purpose
`mhi.c` implements a QRTR endpoint transport over the MHI bus, typically for Qualcomm external modem communication. It converts MHI download buffers into QRTR packets and QRTR outgoing skbs into MHI upload transfers.

## Important APIs, Types, And Functions
The device wrapper is `struct qrtr_mhi_dev`, containing a `qrtr_endpoint`, `mhi_device`, and device pointer. Main callbacks are `qcom_mhi_qrtr_dl_callback()`, `qcom_mhi_qrtr_ul_callback()`, `qcom_mhi_qrtr_send()`, `qcom_mhi_qrtr_queue_dl_buffers()`, `qcom_mhi_qrtr_probe()`, `qcom_mhi_qrtr_remove()`, and suspend/resume helpers.

## Control Flow
Probe allocates driver state, sets endpoint `xmit`, stores drvdata, prepares MHI channels, registers a QRTR endpoint with auto node id, then queues all available downlink buffers. Downlink callback ignores absent state and most failed transactions; `-ENOTCONN` frees reset buffers. Successful transfers call `qrtr_endpoint_post()`, report invalid packets, and recycle the same buffer back to MHI. QRTR transmit linearizes the skb, holds `skb->sk` while queued to MHI, and submits via `mhi_queue_skb()`. Upload completion drops the socket ref and consumes the skb.

Suspend late unprepares transfers unless the controller is already in M3. Resume early prepares channels and refills downlink buffers unless still in M3.

## State And Persistence
State is per-MHI-device and devm-managed. Download buffers are devm allocations recycled through MHI. QRTR endpoint registration owns a `qrtr_node` until remove. Socket refs are temporarily held across asynchronous upload completion.

## Dependencies And Integration Points
The file depends on MHI client driver APIs, QRTR endpoint APIs, skb linearization, DMA direction constants, and PM callbacks. It matches MHI channel `"IPCR"`.

## Risks
Buffer recycling must avoid leaks on queue failures and channel reset. Holding socket refs across MHI upload is necessary for skb ownership accounting; missing release would leak sockets. `skb_linearize()` may fail under memory pressure. Resume must requeue enough buffers to avoid receive starvation.

## Test Signals
Tests should cover probe failure unwind, invalid QRTR packet logging, MHI reset `-ENOTCONN`, upload queue failure, upload completion socket ref release, suspend/resume in M3 and non-M3 states, and remove after partial initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/qrtr/mhi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/qrtr/ns.c -->
# sources/distributed-fs/ceph-client/net/qrtr/ns.c

## Purpose
`ns.c` implements the QRTR nameservice/control-plane socket. It tracks nodes, advertised services, and lookup subscribers, then broadcasts or unicasts service lifecycle notifications using QRTR control packets.

## Important APIs, Types, And Functions
External lifecycle APIs are `qrtr_ns_init()` and `qrtr_ns_remove()`. Important types are `struct qrtr_server_filter`, `struct qrtr_lookup`, `struct qrtr_server`, and nameservice-local `struct qrtr_node`. Important helpers include `node_get()`, `server_match()`, `server_add()`, `server_del()`, `service_announce_new()`, `service_announce_del()`, `lookup_notify()`, `announce_servers()`, and command handlers for HELLO, BYE, DEL_CLIENT, NEW_SERVER, DEL_SERVER, NEW_LOOKUP, and DEL_LOOKUP.

## Control Flow
Initialization creates a kernel AF_QIPCRTR datagram socket, creates an ordered workqueue, hooks `sk_data_ready`, binds to `QRTR_PORT_CTRL`, records the local node id, and broadcasts HELLO. Data-ready queues `qrtr_ns_worker()`, which drains control packets with `kernel_recvmsg(MSG_DONTWAIT)`, decodes `qrtr_ctrl_pkt.cmd`, emits tracepoints, and dispatches command handlers.

HELLO replies with HELLO and local server announcements. NEW_SERVER adds or replaces a server entry and broadcasts local services; it also notifies matching lookups. DEL_SERVER removes a service. DEL_CLIENT removes lookups and the service for a closing port, and notifies local servers. BYE removes all servers for a remote node and notifies local servers. NEW_LOOKUP accepts only local observers, stores the lookup with bounded count, sends current matches, then sends an empty end-of-list notification. DEL_LOOKUP removes matching subscriptions.

Removal restores the original data-ready callback, cancels work, destroys the workqueue, restores module references that were dropped after creating the in-module kernel socket, and releases the socket.

## State And Persistence
Global nameservice state is `nodes` xarray, `node_count`, and `qrtr_ns` singleton fields: kernel socket, broadcast address, lookup list/count, workqueue/work item, saved callback, and local node id. Each node owns an xarray of services keyed by port and a bounded server count. This state is memory-only and rebuilt after module load.

## Dependencies And Integration Points
The file integrates with AF_QIPCRTR sockets, `qrtr_ctrl_pkt` ABI, kernel send/receive APIs, ordered workqueues, socket callbacks, module reference accounting, and QRTR tracepoints.

## Risks
The nameservice has explicit caps (`QRTR_NS_MAX_NODES`, `QRTR_NS_MAX_SERVERS`, `QRTR_NS_MAX_LOOKUPS`) to prevent unbounded memory growth; exceeding them drops new state. Spoofing checks exist for DEL_CLIENT and local server unregister, but other control traffic relies on QRTR node/port routing semantics. The worker serializes through an ordered workqueue but list/xarray state is not protected by a broad lock, so callback/work ordering is important. Module refcount manipulation is delicate because the kernel socket is owned by the same module.

## Test Signals
Coverage should include HELLO exchange, service add/replace/delete, lookup subscription and end-of-list notification, BYE cleanup, DEL_CLIENT spoof rejection, local-only NEW_LOOKUP restriction, cap enforcement, invalid command handling, data-ready restoration on init failure/remove, and module unload after nameservice socket creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/qrtr/ns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/qrtr/qrtr.h -->
# sources/distributed-fs/ceph-client/net/qrtr/qrtr.h

## Purpose
`qrtr.h` is the private QRTR core/transport interface. It defines the endpoint abstraction used by transport drivers and declares core endpoint and nameservice lifecycle functions.

## Important APIs, Types, And Functions
The central type is `struct qrtr_endpoint`, with an `xmit()` callback and private `struct qrtr_node *node`. Public functions are `qrtr_endpoint_register()`, `qrtr_endpoint_unregister()`, `qrtr_endpoint_post()`, `qrtr_ns_init()`, and `qrtr_ns_remove()`. `QRTR_EP_NID_AUTO` requests node id auto-assignment from incoming traffic.

## Control Flow
Transports fill `ep.xmit`, call register, pass inbound bytes to `qrtr_endpoint_post()`, and unregister on device/file removal. The core calls `xmit()` with skbs it no longer owns; transport drivers must consume or free them.

## State And Persistence
The header exposes only the endpoint handle. The private `node` pointer is owned by QRTR core and persists from register to unregister.

## Dependencies And Integration Points
This file is shared by `af_qrtr.c`, `ns.c`, and transport drivers `mhi.c`, `smd.c`, and `tun.c`. It intentionally hides `struct qrtr_node` internals from transports.

## Risks
The ownership contract for `xmit()` is critical: transport code must free or consume skbs exactly once. Endpoint users must not access the private node pointer except through core APIs.

## Test Signals
Test signals are mostly integration-level: endpoint register rejection for missing `xmit`, unregister cleanup, inbound post after registration, and transport skb ownership behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/qrtr/qrtr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/qrtr/smd.c -->
# sources/distributed-fs/ceph-client/net/qrtr/smd.c

## Purpose
`smd.c` implements the QRTR endpoint transport over Qualcomm SMD/RPMSG channels.

## Important APIs, Types, And Functions
The per-device wrapper is `struct qrtr_smd_dev`. Main functions are `qcom_smd_qrtr_callback()`, `qcom_smd_qrtr_send()`, `qcom_smd_qrtr_probe()`, and `qcom_smd_qrtr_remove()`. The driver matches RPMSG service `"IPCRTR"`.

## Control Flow
Probe allocates state, stores the RPMSG endpoint, sets QRTR endpoint `xmit`, registers with QRTR using auto node id, and stores drvdata. RPMSG receive callback fetches drvdata and posts inbound data to QRTR; invalid QRTR packets are logged but reported as consumed so RPMSG drops them. QRTR transmit linearizes the skb and sends bytes through `rpmsg_send()`, consuming the skb on success or freeing it on failure. Remove unregisters the endpoint and clears drvdata.

## State And Persistence
State is devm-managed per RPMSG device, with QRTR endpoint state existing between probe and remove. There is no persistent storage.

## Dependencies And Integration Points
The file depends on RPMSG driver APIs, QRTR endpoint APIs, and skb linearization. It is built as `qrtr-smd` when `CONFIG_QRTR_SMD` is enabled.

## Risks
The driver must return `0` for invalid received packets after logging, otherwise lower layers may retry/drop differently than intended. `rpmsg_send()` and `skb_linearize()` failures must free the skb. Remove must not race with callbacks using drvdata.

## Test Signals
Tests should cover probe/register failure, inbound valid and invalid packet handling, transmit success/failure skb ownership, no-drvdata callback behavior, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/qrtr/smd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/qrtr/tun.c -->
# sources/distributed-fs/ceph-client/net/qrtr/tun.c

## Purpose
`tun.c` exposes a `/dev/qrtr-tun` misc device that lets userspace implement or test QRTR endpoints by reading outgoing QRTR frames and writing inbound QRTR frames.

## Important APIs, Types, And Functions
The per-open state is `struct qrtr_tun`, containing a QRTR endpoint, skb queue, and read waitqueue. File operations are `qrtr_tun_open()`, `qrtr_tun_read_iter()`, `qrtr_tun_write_iter()`, `qrtr_tun_poll()`, and `qrtr_tun_release()`. Endpoint transmit callback is `qrtr_tun_send()`.

## Control Flow
Open allocates per-file state, initializes queue/waitqueue, sets endpoint `xmit`, stores private data, and registers the endpoint. When QRTR sends to the endpoint, `qrtr_tun_send()` queues the skb and wakes readers. Reads block until an skb is available unless nonblocking, copy up to the user iov length, and free the skb. Writes allocate a kernel buffer of the user-provided length, copy data from userspace, pass it to `qrtr_endpoint_post()`, free the buffer, and return either the posted length or the QRTR error. Poll reports readable when the queue is non-empty. Release unregisters endpoint, purges queued skbs, and frees state.

## State And Persistence
Each open file has an independent endpoint and queue. State is volatile and ends on close.

## Dependencies And Integration Points
The file integrates with miscdevice registration, poll/read/write iter APIs, QRTR endpoint APIs, skb queues, waitqueues, and usercopy helpers.

## Risks
Read truncates silently to the user buffer length without preserving the remainder because it frees the skb. Large writes up to `KMALLOC_MAX_SIZE` may pressure memory. Release does not explicitly wake blocked readers after unregister; normal file teardown handles close paths, but concurrent blocking I/O deserves attention. Written data must already be a valid aligned QRTR packet.

## Test Signals
Coverage should include open/register failure, blocking and nonblocking reads, poll readiness, short-buffer reads, invalid/zero/oversized writes, valid write injection, and close with queued packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/qrtr/tun.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/Kconfig -->
# sources/distributed-fs/ceph-client/net/rds/Kconfig

## Purpose
This Kconfig file declares Reliable Datagram Sockets core and transport options. RDS provides reliable sequenced datagram delivery over InfiniBand/RDMA or TCP.

## Important APIs, Types, And Functions
Symbols are `RDS`, `RDS_RDMA`, `RDS_TCP`, `RDS_DEBUG`, and `GCOV_PROFILE_RDS`. `RDS` depends on `INET`; `RDS_RDMA` depends on RDS, InfiniBand, and InfiniBand address translation; `RDS_TCP` depends on RDS and has an IPv6 compatibility dependency; debug and gcov options affect instrumentation.

## Control Flow
No runtime control flow exists here. Configuration controls object selection in the RDS Makefile and whether debug/gcov flags are added.

## State And Persistence
The file affects kernel build configuration only.

## Dependencies And Integration Points
`RDS_RDMA` enables the RDMA-capable transport implemented by the `ib*` and `rdma_transport` files. `RDS_TCP` enables the TCP transport. The core can be built without either transport but then cannot communicate unless transports are loaded separately.

## Risks
Selecting RDS without transports can surprise users at runtime. RDMA support is intentionally gated by InfiniBand and address-translation support. Debug flags change compiled logging behavior.

## Test Signals
Build tests should cover core-only, TCP-only, RDMA-only, combined transports, module/built-in combinations, debug builds, and gcov profile builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/Makefile -->
# sources/distributed-fs/ceph-client/net/rds/Makefile

## Purpose
The Makefile defines RDS core, RDMA transport, and TCP transport object composition.

## Important APIs, Types, And Functions
`rds.o` includes core socket, bind, congestion, connection, info, message, receive, send, stats, sysctl, thread, transport, loopback, page, and RDMA helper objects. `rds_rdma.o` includes RDMA transport, IB CM/send/recv/ring/stats/sysctl/RDMA/FRMR pieces. `rds_tcp.o` includes TCP transport implementation files. `ccflags-$(CONFIG_RDS_DEBUG)` adds `-DRDS_DEBUG`; `CONFIG_GCOV_PROFILE_RDS` enables gcov.

## Control Flow
No runtime flow exists, but link composition determines initialization ordering through module init calls in the object files.

## State And Persistence
The file affects build artifacts only.

## Dependencies And Integration Points
Core RDS exports transport registration APIs consumed by `rds_rdma` and `rds_tcp`. RDMA object composition shows `ib_frmr.o` and `ib_mr.h` belong to memory-registration support.

## Risks
Object omissions or modular dependency issues can break transport registration. Debug/gcov flags may alter performance and coverage behavior.

## Test Signals
Build tests should verify all configured object groups link, RDS debug builds compile, gcov flag propagation works, and modular transports resolve core symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/af_rds.c -->
# sources/distributed-fs/ceph-client/net/rds/af_rds.c

## Purpose
`af_rds.c` implements the AF_RDS socket family and module lifecycle for Reliable Datagram Sockets. It owns socket creation/destruction, socket options, connect/getname/poll/ioctl behavior, global socket accounting, and RDS info exports for sockets and queued receive messages.

## Important APIs, Types, And Functions
Main socket operations are `rds_release()`, `rds_getname()`, `rds_poll()`, `rds_ioctl()`, `rds_setsockopt()`, `rds_getsockopt()`, `rds_connect()`, and `rds_create()`. Lifecycle functions are `rds_init()` and `rds_exit()`. Helpers include `rds_wake_sk_sleep()`, option helpers for bools, congestion monitor, transport selection, receive timestamp, receive latency tracing, and socket info exporters for IPv4/IPv6.

## Control Flow
Module init seeds `rds_gen_num`, initializes bind/connections/threads/sysctl/stats/proto/socket registration, then registers info callbacks. Socket create requires `SOCK_SEQPACKET` and protocol 0, allocates `struct rds_sock`, initializes send/receive/notify/congestion/RDMA/zcopy queues and locks, and adds it to the global socket list.

Release orphans the socket, clears receive queue, removes congestion monitoring, unbinds, drops pending sends/RDMA keys/notifications/zerocopy completions, removes from global list, drops transport ref, clears `sock->sk`, and puts the sock. Poll reports readability for receive data, notifications, zerocopy completions, and congestion changes; writability is based on send-buffer accounting but not a guarantee that a destination is uncongested.

Socket options dispatch RDS-specific cancellation, memory region management, receive errors, congestion monitoring, transport selection, timestamping, and receive path latency tracing. Connect validates IPv4/IPv6 unicast destinations, records peer address/port, and handles IPv6 link-local scope consistency.

## State And Persistence
Global state includes `rds_sock_list`, `rds_sock_count`, `rds_poll_waitq`, and generated `rds_gen_num`. Per-socket state includes bound and connected addresses/ports/scope, selected transport, TOS, queues, congestion monitor fields, RDMA keys, and zcopy notification queues. State is in-memory only.

## Dependencies And Integration Points
This file integrates with `bind.c`, `cong.c`, `connection.c`, send/recv/RDMA/message/stat/sysctl/thread subsystems, transport registration, Linux proto/socket registration, and RDS info getsockopt.

## Risks
Release ordering is important because receive paths can race with close; `SOCK_DEAD`, receive locks, and queue clearing are relied on. Poll semantics are intentionally non-intuitive and apps may misinterpret EPOLLOUT. Transport selection is restricted for non-TCP transports outside `init_net`. TOS cannot be changed after a connection/transport is attached. IPv6 link-local scope must stay consistent across bind/connect.

## Test Signals
Coverage should include create type/protocol rejection, release while receives are queued, poll for congestion notifications and zcopy/errors, all socket option validation paths, transport selection before bind, non-init-net RDMA rejection, IPv4/IPv6 connect validation, getsockname/getpeername for unbound and connected sockets, and info export buffer sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/af_rds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/bind.c -->
# sources/distributed-fs/ceph-client/net/rds/bind.c

## Purpose
`bind.c` implements RDS local address binding and bound-socket lookup. It validates IPv4/IPv6 addresses, selects or verifies a transport, allocates ports, and maintains a hash table keyed by local address, port, and IPv6 scope id.

## Important APIs, Types, And Functions
Primary APIs are `rds_find_bound()`, `rds_remove_bound()`, `rds_bind()`, `rds_bind_lock_init()`, and `rds_bind_lock_destroy()`. Helpers include `__rds_create_bind_key()` and `rds_add_bound()`. The central data structure is `bind_hash_table`, an `rhashtable` keyed by `rs_bound_key`.

## Control Flow
`rds_bind()` validates the sockaddr family and rejects wildcard, broadcast, and multicast addresses. IPv4 addresses are stored as IPv4-mapped IPv6 addresses. IPv6 addresses must be unicast or valid mapped IPv4; link-local addresses require a nonzero scope id. Under the socket lock it rejects rebinding, checks scope consistency with any connected peer, then either validates a preselected transport via `laddr_check()` or asks for a preferred transport. It sets `SOCK_RCU_FREE` and calls `rds_add_bound()`.

`rds_add_bound()` either uses a requested nonzero port or randomly starts an ephemeral scan, skipping port 0 and `RDS_FLAG_PROBE_PORT`. It checks for existing keys, copies address/key state into the socket, takes a socket ref, inserts into the rhashtable, and records scope id. Lookup uses RCU and increments the socket ref only if the socket is not dead and refcount is nonzero. Removal erases the hash entry, drops the bind ref, and resets the bound address to any.

## State And Persistence
State is the global rhashtable and per-socket bound key/address/port/scope/hash seed. Bind entries hold a socket reference until removal. No disk persistence exists.

## Dependencies And Integration Points
The file integrates with transport selection (`rds_trans_get_preferred`, `laddr_check`), socket lifetime, receive-path lookup, IPv6 address classification, and RCU/rhashtable synchronization.

## Risks
Port allocation can loop over a large range under contention. Insert failure after socket state mutation must reset address and ref. Lookup races with release are handled with `SOCK_DEAD` and refcount increment; changes there could reintroduce UAF risk. Scope-id handling is essential for IPv6 link-local correctness.

## Test Signals
Tests should cover invalid address forms, link-local scope requirements, rebinding rejection, requested-port collisions, ephemeral allocation, probe-port rejection, transport unavailable errors, preselected transport `laddr_check` failure, lookup during release, and removal idempotence for unbound sockets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/bind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/cong.c -->
# sources/distributed-fs/ceph-client/net/rds/cong.c

## Purpose
`cong.c` implements RDS receive-side congestion tracking. It maintains per-local-address bitmaps of congested ports, associates connections with congestion maps, propagates bitmap updates, and supports socket-level congestion monitoring.

## Important APIs, Types, And Functions
Important functions are `rds_cong_get_maps()`, `rds_cong_add_conn()`, `rds_cong_remove_conn()`, `rds_cong_queue_updates()`, `rds_cong_map_updated()`, `rds_cong_updated_since()`, `rds_cong_set_bit()`, `rds_cong_clear_bit()`, `rds_cong_add_socket()`, `rds_cong_remove_socket()`, `rds_cong_wait()`, `rds_cong_update_alloc()`, and `rds_cong_exit()`. State centers on `struct rds_cong_map`, `rds_cong_tree`, `rds_cong_lock`, and `rds_cong_monitor`.

## Control Flow
Connections call `rds_cong_get_maps()` to allocate or find local and foreign congestion maps. Maps are unique per address and own bitmap pages for all ports. When a local port becomes congested/uncongested, bit operations update the bitmap and `rds_cong_queue_updates()` queues send work on all connections tied to the local map. Incoming congestion bitmap updates call `rds_cong_map_updated()`, increment a global generation, wake map waiters and poll waiters, and notify sockets that registered congestion monitors for affected ports.

Senders call `rds_cong_wait()` before sending to a destination port. Nonblocking sends return `-ENOBUFS` if still congested and optionally record a monitor mask. Blocking sends sleep on the map waitqueue until the bit clears. Closing a monitored socket removes it from the monitor list and clears its own bound-port congestion bit if needed.

## State And Persistence
Global state includes an rb-tree of maps, a global generation counter, and a monitored-socket list. Each map owns pages containing little-endian port bits and a list of associated connections. Maps are freed only during module exit after connections are gone.

## Dependencies And Integration Points
This file integrates with RDS send workers, receive-buffer accounting, poll behavior in `af_rds.c`, connection setup in `connection.c`, and message allocation for congestion bitmap sends.

## Risks
The global congestion lock is used in paths that may run with interrupts masked, so queued work is required instead of inline transmit. Bitmap pages are long-lived and freed at exit, making connection lifetime assumptions important. Nonblocking congestion monitor uses a 64-bit mask subset and may lose detail beyond its representable ports. Incorrect update queuing can leave peers with stale congestion state and cause send stalls or ENOBUFS storms.

## Test Signals
Coverage should include map uniqueness, allocation failure, set/clear/test bit for boundary ports, blocking wait wakeup, nonblocking monitor mask behavior, update generation observed by poll, queueing send work for all map connections, close clearing congestion, and module exit freeing all map pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/cong.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/connection.c -->
# sources/distributed-fs/ceph-client/net/rds/connection.c

## Purpose
`connection.c` owns RDS connection object allocation, lookup, state reset/shutdown/destroy, reconnect triggering, and connection-related info exports. Connections persist across underlying transport reconnects to preserve retransmission and sequencing state.

## Important APIs, Types, And Functions
Key APIs are `rds_conn_create()`, `rds_conn_create_outgoing()`, `rds_conn_shutdown()`, `rds_conn_destroy()`, `rds_for_each_conn_info()`, `rds_conn_init()`, `rds_conn_exit()`, `rds_conn_path_drop()`, `rds_conn_drop()`, `rds_conn_path_connect_if_down()`, `rds_check_all_paths()`, `rds_conn_connect_if_down()`, and `__rds_conn_path_error()`. Important helpers include `rds_conn_bucket()`, `rds_conn_lookup()`, `rds_conn_path_reset()`, and `__rds_conn_create()`.

## Control Flow
Connection creation hashes local/foreign address pairs and looks up an existing connection under RCU. If none exists, it allocates `struct rds_connection` and one or more `struct rds_conn_path` entries depending on transport multipath capability, initializes congestion maps, detects loopback preference, initializes per-path workqueues and delayed works, calls the transport `conn_alloc()`, then inserts under `rds_conn_lock` unless a racing creator won.

Shutdown transitions a path to disconnecting, waits for transmit/refill flags to clear, calls the transport shutdown hook, resets send path state without clearing `next_rx_seq`, transitions to down, cancels pending reconnect work, and requeues reconnect for still-hashed live connections. Destroy removes from the hash under RCU, destroys each path, drops queued messages and retransmits, removes congestion map linkage, frees path memory and slab object, and decrements the global count.

Info export walks connection hash buckets under RCU, optionally walks send/retrans queues under path locks, zeroes per-item buffers before copying to userspace, and reports IPv4/IPv6 connection state.

## State And Persistence
Global state includes `rds_conn_hash`, `rds_conn_lock`, `rds_conn_count`, and `rds_conn_slab`. Each connection stores local/foreign addresses, net, transport, TOS, device index, loopback/passive status, generation numbers, congestion maps, and per-path state including send/retrans queues, sequence numbers, delayed works, waitqueues, flags, and transport private data.

## Dependencies And Integration Points
The file integrates with RDS transports, loopback, congestion maps, send/recv workers, reconnect scheduling, info getsockopt, IPv6 hashing, and RCU hash traversal. Transport hooks include `conn_alloc`, `conn_free`, `conn_path_shutdown`, `conn_slots_available`, and multipath flags.

## Risks
Creation handles races by allocating outside the global lock then rolling back if another connection appears; rollback must free all per-path transport data and workqueues. Passive loopback IB connections are special and not hashed like normal connections. Reset intentionally preserves receive sequence state for reliability. Shutdown waits can hang if transport flags or fast-reg completions never drain. Info APIs currently report only the first multipath path for some records.

## Test Signals
Tests should cover duplicate creation races, passive loopback creation, transport allocation failure rollback, multipath path allocation, shutdown from UP/ERROR/RESETTING states, reconnect scheduling suppression after destroy, queued message cleanup, info export buffer zeroing, IPv4/IPv6 filtering, and module exit with empty hash.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/connection.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/ib.c -->
# sources/distributed-fs/ceph-client/net/rds/ib.c

## Purpose
`ib.c` registers and manages the RDS InfiniBand transport. It tracks IB devices, allocates protection domains and MR pools, validates local addresses, exposes IB connection info, and registers the `rds_ib_transport` callbacks with the RDS core.

## Important APIs, Types, And Functions
Important globals are `rds_ib_devices`, `rds_ib_devices_lock`, `rds_ib_client`, `ib_nodev_conns`, and `rds_ib_transport`. Main functions include `rds_ib_add_one()`, `rds_ib_remove_one()`, `rds_ib_get_client_data()`, `rds_ib_dev_put()`, `rds_ib_laddr_check()`, `rds_ib_laddr_check_cm()`, `rds_ib_init()`, and `rds_ib_exit()`. Helper paths include nodev reconnect, device shutdown/free, info visitors, and unload state checks.

## Control Flow
When the IB core adds a device, RDS accepts only IB channel adapters with memory-management extensions. It allocates `rds_ib_device`, initializes locks/lists/refcount/free work, records hardware limits and ODP capability, allocates completion-vector load tracking, protection domain, and 1M/8K MR pools, adds the device to the global RCU list, stores IB client data, and retries connections that were waiting without a device.

Device removal drops active connection paths, clears IB client data, removes the device from the global list, waits for RCU readers, and drops references so deferred free tears down MR pools, PD, IP list, vector load, and device state. Address validation restricts RDS/IB to `init_net`, checks IPv4-mapped addresses against known RDS IB devices, otherwise uses RDMA CM bind checks and special IPv6 link-local validation. Init initializes MR support, registers the IB client, sysctls, receive path, transport, and info callbacks; exit reverses this with an unloading flag and RCU grace period.

## State And Persistence
State includes global device list, per-device refcounts, IP address list, connection list, MR pools, PD, hardware limits, vector load counters, and unloading flag. It is volatile and tied to IB device/module lifetimes.

## Dependencies And Integration Points
This file integrates with the RDMA/IB client API, RDMA CM address binding, RDS transport registration, MR pool code, receive/sysctl/stats/info subsystems, and connection management in `connection.c`/`ib_cm.c`.

## Risks
Device removal races with incoming connections and MR fast paths; RCU plus refcounts protect client data and list readers. MR pool sizing depends on device limits and module parameters. Address validation currently treats RDS/IB as not network-namespace aware. Vector load accounting must be balanced by connection setup/teardown. Deferred device free relies on `rds_wq` flushing during unregister.

## Test Signals
Coverage should include unsupported device rejection, MR pool allocation failure unwind, client-data ref behavior during remove, nodev connection retry after device add, laddr checks for IPv4, IPv6, link-local scope, non-init-net rejection, info export for up/down IB connections, and init/exit failure unwind at each stage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/ib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/ib.h -->
# sources/distributed-fs/ceph-client/net/rds/ib.h

## Purpose
`ib.h` is the central private header for RDS/IB. It defines protocol constants, connection-private negotiation formats, send/receive work descriptors, rings, ack state, IB connection/device structures, statistics, inline DMA sync wrappers, and cross-file function prototypes.

## Important APIs, Types, And Functions
Key types include `struct rds_ib_connection`, `struct rds_ib_device`, `struct rds_ib_send_work`, `struct rds_ib_recv_work`, `struct rds_ib_work_ring`, `struct rds_ib_ack_state`, `struct rds_ib_refill_cache`, `union rds_ib_conn_priv`, `struct rds_ib_conn_priv_cmn`, and `struct rds_ib_statistics`. Important constants define default WR counts, supported protocols, SGE counts, ACK WR id, credit bit packing, and MR pool ids. The header declares transport, CM, RDMA, recv, ring, send, stats, and sysctl functions.

## Control Flow
This header does not execute control flow, but it encodes the data contracts used by `ib.c`, `ib_cm.c`, `ib_recv.c`, `ib_send.c`, `ib_ring.c`, `ib_rdma.c`, and `ib_frmr.c`. Connection setup fills private data structures, send/recv paths consume work descriptors/rings, completion handlers update ack and credit fields, and MR operations use connection/device fields.

## State And Persistence
The structures describe persistent in-memory RDS/IB runtime state: CM ids, PDs, CQs, work rings, DMA header arrays, tasklets, ack flags, credits, MR pools, device limits, connection lists, vector load, and statistics. None is disk-persistent.

## Dependencies And Integration Points
The header depends on RDMA verbs, RDMA CM, PCI/slab primitives, RDS core headers, and RDMA transport definitions. It is the integration point for all RDS/IB implementation files.

## Risks
ABI-sensitive private connection data warns that fields must be appended rather than reordered. Credit packing assumes `atomic_t` is at least 32 bits. The fallback DMA sync macros shadow missing IB APIs. Structure fields are used across interrupt/tasklet/workqueue/process contexts, so lock and lifetime assumptions are spread across files.

## Test Signals
Validation is compile- and integration-heavy: protocol negotiation structure sizes for IPv4/IPv6, credit packing/unpacking, ring sizing, stats layout, ODP/MR pool fields, and cross-file prototype consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/ib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/ib_cm.c -->
# sources/distributed-fs/ceph-client/net/rds/ib_cm.c

## Purpose
`ib_cm.c` implements RDS/IB RDMA connection management. It negotiates protocol and flow control, creates/destroys QPs/CQs/DMA header resources, handles CM connect/accept paths, polls completion queues via tasklets, and allocates/frees per-connection IB state.

## Important APIs, Types, And Functions
Important APIs are `rds_ib_cm_connect_complete()`, `rds_ib_cm_handle_connect()`, `rds_ib_cm_initiate_connect()`, `rds_ib_conn_path_connect()`, `rds_ib_conn_path_shutdown()`, `rds_ib_conn_alloc()`, `rds_ib_conn_free()`, and `__rds_ib_conn_error()`. Major helpers include `rds_ib_set_protocol()`, `rds_ib_set_flow_control()`, `rds_ib_cm_fill_conn_param()`, CQ handlers/tasklets, DMA header alloc/free helpers, `rds_ib_setup_qp()`, and `rds_ib_protocol_compatible()`.

## Control Flow
Outgoing connect creates an RDMA CM id, binds source/destination sockaddr from RDS addresses, resolves address, sets proposed protocol/flow control, sets up QP resources, fills private data, and calls `rdma_connect_locked()`. Incoming connect validates protocol private data, extracts IPv4/IPv6 addresses and TOS, finds link-local interface if needed, creates or finds an RDS connection, transitions it to CONNECTING, attaches the CM id, sets up QP resources, fills response private data, and accepts.

QP setup obtains an `rds_ib_device`, adds the connection to the device, sizes send/recv rings, creates send/recv CQs with balanced completion vectors, requests notifications, creates an RC QP, allocates DMA-mapped send/recv header arrays and ACK header, allocates send/recv work arrays, and initializes ACK state. Completion handlers schedule send/recv tasklets. Tasklets poll CQs, dispatch send/MR/recv completions, update ACK state, drop acked messages, attempt ACK sends, and resume RDS send xmit when appropriate.

Connect complete parses peer private data, sets negotiated protocol and flow control, rejects unsupported old versions, initializes rings, refills receives, updates IB device IP address, processes piggyback ACK, and calls `rds_connect_complete()`. Shutdown disconnects RDMA CM, flushes MRs, waits for receive ring/signaled sends/fastreg state to drain, kills tasklets, quiesces CQs, destroys QP/CQs, frees DMA headers/work arrays, removes the connection from the device, resets ACK/flow-control/ring state, and frees partial incoming state.

## State And Persistence
Per-connection state includes CM id, PD, CQs, tasklets, send/recv rings, DMA headers, ACK header, credits, flow-control flag, active/passive role, CQ quiesce flag, vector indexes, and work arrays. Nodev/device lists are maintained through `rds_ib_conn_alloc()` and device add/remove helpers.

## Dependencies And Integration Points
The file integrates with RDMA CM, IB verbs, RDS core connection state machine, send/recv/MR handlers, MR flushing, sysctl flow-control settings, device management in `ib.c`, and protocol definitions in `ib.h`.

## Risks
Setup and teardown are highly staged; every failure path must free only resources already initialized and balance vector/device refs. Private data parsing handles legacy/zeroed RDMA CM buffers and unaligned ACK sequence loads. Shutdown waits can deadlock if completions or fastreg counters are lost. Incoming/outgoing connect races intentionally drop or wait on existing connections. The code currently reports only single-path assumptions in several places despite broader RDS multipath support.

## Test Signals
Tests should cover protocol compatibility negotiation, IPv4/IPv6 private data, link-local ifindex lookup, incoming race states, QP setup failure at each allocation step, CQ vector balance/unbalance, send/recv CQ polling, MR completion dispatch, connect complete with piggyback ACK, shutdown after partial setup, shutdown with in-flight FRMRs, and active/passive loopback cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/ib_cm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/ib_frmr.c -->
# sources/distributed-fs/ceph-client/net/rds/ib_frmr.c

## Purpose
`ib_frmr.c` implements RDS/IB fast memory registration (FRMR/FRWR) allocation, registration, invalidation, completion handling, and pool return behavior for RDMA memory regions.

## Important APIs, Types, And Functions
Externally used functions are `rds_ib_mr_cqe_handler()`, `rds_ib_unreg_frmr()`, `rds_ib_reg_frmr()`, and `rds_ib_free_frmr_list()`. Key helpers are `rds_transition_frwr_state()`, `rds_ib_alloc_frmr()`, `rds_ib_free_frmr()`, `rds_ib_post_reg_frmr()`, `rds_ib_map_frmr()`, and `rds_ib_post_inv()`. State is stored in `struct rds_ib_mr` and its `struct rds_ib_frmr` union member.

## Control Flow
Registration chooses the 8K or 1M MR pool based on page count, tries to reuse a clean MR, otherwise allocates a new `rds_ib_mr` and `ib_mr`. Mapping tears down old state, stores the scatterlist, DMA maps it, validates page-boundary constraints and pool page limits, posts an `IB_WR_REG_MR`, waits for registration completion, and returns the rkey. Work-request availability is throttled with `i_fastreg_wrs`; in-use registrations increment `i_fastreg_inuse_count`.

Invalidation posts `IB_WR_LOCAL_INV` for in-use MRs and waits for state to become free or stale before DMA unmap/teardown. Completion handling transitions state on errors, drops the RDS connection if needed, wakes registration/invalidation waiters, and returns a fastreg WR credit. Unregistration first posts invalidations for all mapped MRs, then tears down DMA mappings and either frees MRs up to a goal or leaves still-in-use entries. Freeing returns MRs to pool free/drop llist and queues pool flush work when pinned/dirty thresholds are exceeded.

## State And Persistence
FRMR state includes `fr_state`, registration/invalidation booleans and waitqueues, WR storage, DMA page count, sg byte length, rkey-generating remap count, associated connection/device/pool, scatterlist DMA mapping, and pool dirty/free/drop lists. State is memory-only and tied to MR pool/device/connection lifetime.

## Dependencies And Integration Points
The file integrates with IB verbs (`ib_alloc_mr`, `ib_map_mr_sg_zbva`, `ib_post_send`, `ib_update_fast_reg_key`, `ib_dereg_mr`, DMA mapping), RDS/IB send CQ MR completion dispatch in `ib_cm.c`, MR pool helpers in other IB RDMA files, and connection teardown wait conditions.

## Risks
The busy-wait loops around `i_fastreg_wrs` can spin if credits are never returned. Registration and invalidation deliberately wait for completions to avoid remote access and DMA teardown races. State transitions must decrement `i_fastreg_inuse_count` exactly once when leaving INUSE. Error completions mark MRs stale and may reconnect. Scatterlist boundary validation is strict; incorrect handling can expose invalid remote access or DMA bugs.

## Test Signals
Coverage should include MR reuse/allocation, 8K versus 1M pool selection, DMA map failure, page-boundary rejection, max-page rejection, registration post failure, registration completion wakeup, invalidation post failure, stale-state cleanup, CQ error reconnect, pool dirty/free threshold flush queuing, and teardown during connection shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/ib_frmr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/ib_mr.h -->
# sources/distributed-fs/ceph-client/net/rds/ib_mr.h

## Purpose
`ib_mr.h` defines the RDS/IB memory-region pool and FRMR structures used by RDMA registration and invalidation code.

## Important APIs, Types, And Functions
Key constants are `RDS_MR_1M_POOL_SIZE`, `RDS_MR_1M_MSG_SIZE`, `RDS_MR_8K_MSG_SIZE`, `RDS_MR_8K_SCALE`, and `RDS_MR_8K_POOL_SIZE`. Important types are `enum rds_ib_fr_state`, `struct rds_ib_frmr`, `struct rds_ib_mr`, and `struct rds_ib_mr_pool`. Declared APIs include MR pool create/destroy/info, get/sync/free/flush MR, MR init/exit, lkey retrieval, teardown, reuse, flush, FRMR registration/unregistration, and free-list handling.

## Control Flow
The header itself has no executable flow. It defines contracts used by MR pool implementation and `ib_frmr.c`: MRs move between free, in-use, and stale states; pools maintain free/drop/clean lists and delayed flush work; callers can request MR registration for scatterlists and later free or invalidate them.

## State And Persistence
`struct rds_ib_mr` stores work item, owning device/pool/connection, llist/list nodes, scatterlist and DMA lengths, ODP flag, and either FRMR state or direct `ib_mr`. `struct rds_ib_mr_pool` stores item/dirty counts, drop/free/clean lists, flush waitqueue, clean-list lock, pinned-memory accounting, max item/page limits, and delayed flush worker. State is per-device and volatile.

## Dependencies And Integration Points
The header depends on RDS core and `ib.h`, and it is included by IB RDMA/FRMR/device code. It is the shared contract between transport MR operations exposed in `rds_ib_transport` and lower-level pool/FRWR mechanics.

## Risks
Pool sizing constants directly affect pinned memory pressure. State-machine misuse can leak pinned pages, deregister in-use MRs, or leave stale MRs reusable. The delayed flush worker and waitqueue require careful synchronization with connection/device teardown.

## Test Signals
Validation should cover pool limit calculations, state transitions, pinned/free/dirty accounting, flush worker behavior, ODP versus FRMR selection paths, and compile-time consistency with `ib_frmr.c` and transport callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/ib_mr.h -->
