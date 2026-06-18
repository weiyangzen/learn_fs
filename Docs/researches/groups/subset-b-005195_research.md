# Research: subset-b-005195

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/qcom_glink_rpm.c -->
# sources/distributed-fs/ceph-client/drivers/rpmsg/qcom_glink_rpm.c

Purpose: Qualcomm GLINK transport for the Resource Power Manager message RAM. It maps the RPM message RAM table of contents, finds AP-to-RPM and RPM-to-AP FIFOs, implements `qcom_glink_pipe` callbacks over MMIO ring buffers, and binds those pipes to the shared GLINK native protocol engine.

Important APIs, types, and functions: `struct rpm_toc` and `struct rpm_toc_entry` describe the 256-byte tail TOC in message RAM. `struct glink_rpm_pipe` wraps a `qcom_glink_pipe` with MMIO `head`, `tail`, and FIFO pointers. `glink_rpm_rx_avail()`, `glink_rpm_rx_peek()`, and `glink_rpm_rx_advance()` implement RX ring inspection and tail movement. `glink_rpm_tx_avail()`, `glink_rpm_tx_write_one()`, `glink_rpm_tx_write()`, and `glink_rpm_tx_kick()` implement TX space accounting, wrapped writes, 8-byte GLINK padding, and mailbox notification. `glink_rpm_parse_toc()` validates `RPM_TOC_MAGIC`, bounds entry count, locates `RPM_RX_FIFO_ID` and `RPM_TX_FIFO_ID`, and assigns pipe descriptors. `glink_rpm_probe()` wires OF resources, IRQ, mailbox, pipe callbacks, initial pointers, and `qcom_glink_native_probe()`.

Control flow: probe parses the `qcom,rpm-msg-ram` phandle, maps memory, parses the TOC, requests an initially disabled IRQ, acquires mailbox channel 0, fills pipe callbacks, resets TX head and RX tail, creates the GLINK native instance with `intentless` support enabled, stores driver data, and enables IRQ delivery. Interrupts call `qcom_glink_native_rx()` to drain the shared pipe. TX writes copy header and payload using 32-bit MMIO helpers, move unaligned payload tails into a local padding buffer, align total messages to GLINK's 8-byte boundary, update the head pointer, and kick the RPM over mailbox. Remove disables IRQ, tears down native GLINK, and frees the mailbox.

State and persistence: persistent state lives in RPM message RAM: FIFO contents plus head and tail indices. The driver keeps only runtime pointers and `struct qcom_glink *`. It resets its TX head and RX tail on probe, so remote firmware and Linux must agree on startup sequencing. Ring wrap is explicit; malformed TOC entries are skipped unless required FIFOs are missing.

Dependencies and integration points: depends on platform OF data (`qcom,glink-rpm`, IRQ, `qcom,rpm-msg-ram`), mailbox framework, MMIO helpers, and `qcom_glink_native`. It exposes rpmsg channels indirectly through GLINK native and the rpmsg core. `IRQF_NO_SUSPEND` keeps the RPM communication interrupt active across suspend paths.

Risks: TOC bounds check uses `offset + size > msg_ram_size`, so integer overflow would be worth auditing even though values are firmware-controlled 32-bit fields promoted to `size_t`. FIFO copy helpers assume 4-byte aligned lengths for MMIO access; `WARN()` rejects unaligned headers and the padding path handles unaligned payload tails. A failed native probe manually frees the mailbox, while devm handles IRQ/mapping. Missing or stale message-RAM contents can prevent probe or corrupt GLINK framing.

Test signals: boot on a Qualcomm RPM GLINK platform should show successful `qcom_glink_rpm` probe and rpmsg services. Negative tests include invalid TOC magic/count, missing FIFO IDs, mailbox request deferral/failure, wrapped FIFO RX/TX messages, unaligned payload lengths, suspend/resume interrupt behavior, and removal while IRQs are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/qcom_glink_rpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/qcom_glink_smem.c -->
# sources/distributed-fs/ceph-client/drivers/rpmsg/qcom_glink_smem.c

Purpose: Qualcomm GLINK transport over SMEM shared memory. It allocates/acquires SMEM descriptors and FIFOs for a remote PID, exposes RX/TX `qcom_glink_pipe` callbacks, and registers a child device representing the GLINK edge.

Important APIs, types, and functions: `struct qcom_glink_smem` owns the synthetic device, IRQ, mailbox, remote PID, and GLINK native handle. `struct glink_smem_pipe` wraps FIFO pointers and little-endian head/tail fields. `qcom_glink_smem_register()` and `qcom_glink_smem_unregister()` are exported integration APIs. Pipe callbacks include `glink_smem_rx_avail()`, `glink_smem_rx_peek()`, `glink_smem_rx_advance()`, `glink_smem_tx_avail()`, `glink_smem_tx_write()`, and `glink_smem_tx_kick()`.

Control flow: registration allocates a standalone child `struct device`, reads `qcom,remote-pid`, allocates or reuses SMEM descriptor item 478, allocates/reuses TX FIFO item 479, lazily maps RX FIFO item 480 on first RX availability check, requests the edge IRQ with `IRQF_NO_AUTOEN`, acquires mailbox channel 0, installs pipe callbacks, clears local RX tail and TX head, and starts `qcom_glink_native_probe()` with `GLINK_FEATURE_INTENT_REUSE`. The IRQ handler simply calls `qcom_glink_native_rx()`. Unregister disables IRQ, removes GLINK native, frees the mailbox, and unregisters the child device.

State and persistence: shared state is the SMEM descriptor array (`tx.tail`, `tx.head`, `rx.tail`, `rx.head`) and FIFO memory. The driver maintains cached FIFO virtual addresses and the GLINK native pointer. TX reserves `FIFO_FULL_RESERVE + TX_BLOCKED_CMD_RESERVE` bytes to avoid full/empty ambiguity and leave room for read notifications. `wmb()` orders FIFO writes before publishing the head pointer.

Dependencies and integration points: depends on Qualcomm SMEM (`qcom_smem_alloc/get`), mailbox, OF IRQ and `qcom,remote-pid`, and GLINK native. It is not a platform driver itself; another Qualcomm subsystem driver calls the exported register/unregister functions for each edge.

Risks: RX FIFO acquisition is lazy, so early interrupts before item 480 exists produce zero available bytes and logs. Descriptor size must be exactly 32 bytes. Shared head/tail values are remote-controlled little-endian fields, so corruption can break ring accounting. TX alignment rounds head to 8 bytes without explicit padding writes, relying on GLINK framing and reserved FIFO space.

Test signals: exercise SMEM allocation reuse (`-EEXIST`), remote PID parsing, deferred/missing SMEM, RX FIFO lazy acquisition, wrapped RX/TX copies, mailbox failures, intent reuse behavior, and unregister while interrupts are pending. Runtime traces should show GLINK channels appearing over the SMEM edge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/qcom_glink_smem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/qcom_glink_ssr.c -->
# sources/distributed-fs/ceph-client/drivers/rpmsg/qcom_glink_ssr.c

Purpose: rpmsg client for Qualcomm GLINK subsystem restart cleanup. It lets remoteproc stop paths notify a remote GLINK SSR service and wait briefly for a cleanup acknowledgement before restart proceeds.

Important APIs, types, and functions: `struct do_cleanup_msg` and `struct cleanup_done_msg` encode the GLINK SSR protocol. `struct glink_ssr` stores the rpmsg endpoint, notifier block, sequence number, and completion. `qcom_glink_ssr_notify()` is an exported symbol that calls the global blocking notifier chain. `qcom_glink_ssr_callback()` validates `cleanup_done` responses, and `qcom_glink_ssr_notifier_call()` sends `do_cleanup` requests.

Control flow: when an rpmsg device named `glink_ssr` is probed, the driver initializes a completion, records `rpdev->ept`, and registers a notifier. A remoteproc user calls `qcom_glink_ssr_notify(ssr_name)`, which invokes every registered instance. Each instance increments its sequence number, fills a cleanup request with version 0, command 0, name length, and a bounded subsystem name, sends it with `rpmsg_send()`, then waits up to one second for `qcom_glink_ssr_callback()` to receive matching response 1 and complete the waiter. Remove unregisters the notifier.

State and persistence: only in-memory sequence number and completion state are kept. There is no persisted cleanup state; failures are logged and notifier returns `NOTIFY_DONE` regardless, so cleanup is best-effort.

Dependencies and integration points: integrates the rpmsg bus, Qualcomm GLINK service name `glink_ssr`, Linux notifier chains, and remoteproc Qualcomm restart code via exported `qcom_glink_ssr_notify()`.

Risks: `name_len` uses `strlen(ssr_name)` while `name` is truncated to 32 bytes by `strscpy()`, so a long input can advertise a length larger than the transmitted fixed buffer. Notifications serialize through the blocking notifier call chain, but per-instance `seq_num` is not otherwise locked. A timeout does not fail the notifier, so callers must tolerate incomplete remote cleanup.

Test signals: bind an rpmsg channel named `glink_ssr`, call `qcom_glink_ssr_notify()` with normal and long names, validate cleanup messages on the remote side, inject wrong version/response/sequence replies, and confirm timeout logs when no response arrives.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/qcom_glink_ssr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/qcom_glink_trace.h -->
# sources/distributed-fs/ceph-client/drivers/rpmsg/qcom_glink_trace.h

Purpose: tracepoint definitions for the Qualcomm GLINK native protocol. It gives ftrace/perf users structured visibility into command exchange, channel IDs, intent flow, data chunks, read notifications, and signal changes.

Important APIs, types, and functions: the file defines `TRACE_SYSTEM qcom_glink` and multiple `TRACE_EVENT()` blocks: `qcom_glink_cmd_version`, `qcom_glink_cmd_version_ack`, `qcom_glink_cmd_open`, `qcom_glink_cmd_close`, `qcom_glink_cmd_open_ack`, `qcom_glink_cmd_intent`, `qcom_glink_cmd_rx_done`, `qcom_glink_cmd_rx_intent_req`, `qcom_glink_cmd_rx_intent_req_ack`, `qcom_glink_cmd_tx_data`, `qcom_glink_cmd_close_ack`, `qcom_glink_cmd_read_notif`, and `qcom_glink_cmd_signal`. For most events, `_tx` and `_rx` convenience macros append a direction boolean.

Control flow: this header is included by the GLINK native implementation with trace generation enabled. Each tracepoint captures immutable event fields via `TP_fast_assign()` and formats them via `TP_printk()`. `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `trace/define_trace.h` make the header self-contained for trace event generation.

State and persistence: no runtime state is owned by this file. Trace data is transient in the kernel tracing buffers and enabled only when selected tracepoints are active.

Dependencies and integration points: depends on Linux tracepoint infrastructure and `qcom_glink_native.h` for protocol-related types. It is an observability integration point for GLINK transports such as RPM and SMEM and for the GLINK core state machine.

Risks: tracepoint field schemas become user-visible ABI-like diagnostics; renaming fields or changing types can break tracing scripts. String capture uses `__string()`/`__assign_str()`, so callers must pass valid NUL-terminated remote and channel names. High-rate data events can add overhead when enabled.

Test signals: compile with tracing enabled, inspect `/sys/kernel/tracing/events/qcom_glink/*`, enable each event during GLINK channel open/data/close traffic, and verify tx/rx macros report correct direction, IDs, intent IDs, chunk sizes, and signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/qcom_glink_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/qcom_smd.c -->
# sources/distributed-fs/ceph-client/drivers/rpmsg/qcom_smd.c

Purpose: Qualcomm Shared Memory Driver transport for rpmsg. It discovers SMD packet channels from SMEM allocation tables, manages SMD channel handshakes and ring buffers, registers rpmsg devices for active channels, and exposes a control device for creating endpoint char devices.

Important APIs, types, and functions: `struct qcom_smd_edge` represents a remote processor edge with IRQ/mailbox or syscon IPC, channel list, allocation bitmap, and work items. `struct qcom_smd_channel` represents a packet channel with local/remote states, info structures, TX/RX FIFOs, locks, wait queues, bounce buffer, endpoint, and registration state. `qcom_smd_register_edge()`/`qcom_smd_unregister_edge()` are exported. Core helpers include `qcom_smd_channel_reset()`, `qcom_smd_channel_intr()`, `__qcom_smd_send()`, `qcom_smd_channel_open()`, `qcom_smd_channel_close()`, `qcom_smd_create_ept()`, `qcom_channel_scan_worker()`, and `qcom_channel_state_worker()`.

Control flow: platform probe checks SMEM availability and registers one edge for each child node. Edge registration creates a device, parses `qcom,smd-edge`, optional `qcom,remote-pid`, mailbox or legacy `qcom,ipc` syscon signaling, label, and IRQ, registers an rpmsg control device, then schedules a scan. The scan worker walks two SMEM allocation tables, filters packet channels for the target edge, maps channel info/FIFO items, resets new channels, adds them to the edge list, and wakes endpoint creators. The state worker registers rpmsg devices when the remote side is opening/opened and unregisters them when the remote closes. Endpoint creation waits for the named channel, allocates a `qcom_smd_endpoint`, performs the opening/opened handshake, then serves rpmsg callbacks. Interrupts process state changes, TX block-read wakeups, packet headers, packet payload delivery, tail updates, and optional remote signaling.

State and persistence: channel state is split between persistent SMEM info structures and runtime kernel state. The SMEM fields hold state flags, head/tail indices, and flow-control bits in byte- or word-aligned formats. Runtime state tracks `remote_state`, `pkt_size`, registration, endpoint pointer, and bounce buffer. Channels never truly disappear from SMEM; they change state. TX writes include a 20-byte packet header and update `fHEAD` after a write barrier.

Dependencies and integration points: depends on Qualcomm SMEM, mailbox or syscon/regmap IPC, OF child edge descriptions, IRQs, workqueues, and the rpmsg core. It registers rpmsg devices using `rpmsg_register_device()`, control devices using `rpmsg_ctrldev_register_device()`, and exposes endpoint ops for send, trysend, sendto, trysendto, and poll.

Risks: remote-controlled SMEM tables and states drive channel creation; malformed sizes or non-power-of-two FIFO assumptions can break ring masking. Word-aligned channels reject unaligned payloads. `__qcom_smd_send()` sleeps while waiting for TX space and relies on `fBLOCKREADINTR` signaling to avoid polling. State worker drops and reacquires the channel list lock around registration/unregistration, so registration flags and remote state transitions must be reasoned about carefully. `qcom_smd_unregister_edge()` calls `mbox_free_channel()` even if the edge used legacy syscon IPC and `mbox_chan` is NULL; mailbox API tolerance is assumed.

Test signals: boot Qualcomm SMD platforms and verify edge devices, `rpmsg_name`, rpmsg control device, channel discovery, `rpm_requests` special handling, open/close handshakes, wrapped packet RX with bounce buffer, TX wait/nonwait behavior, syscon fallback, mailbox signaling, remove ordering, and malformed SMEM item sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/qcom_smd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/rpmsg_char.c -->
# sources/distributed-fs/ceph-client/drivers/rpmsg/rpmsg_char.c

Purpose: character-device interface for rpmsg endpoints. It exposes `/dev/rpmsgN` endpoint devices that userspace can open, read, write, poll, use for flow-control ioctls, and destroy when dynamically created.

Important APIs, types, and functions: `struct rpmsg_eptdev` owns the device, cdev, parent `rpmsg_device`, channel info, endpoint lock, endpoint pointer, optional default endpoint, SKB RX queue, read waitqueue, and remote flow-control flags. Exported functions are `rpmsg_chrdev_eptdev_create()` and `rpmsg_chrdev_eptdev_destroy()`. File ops are `rpmsg_eptdev_open()`, `release()`, `read_iter()`, `write_iter()`, `poll()`, and `ioctl()`. The rpmsg driver binds `rpmsg-raw` and `rpmsg_chrdev`.

Control flow: probe allocates an endpoint char device for matching rpmsg channels and reuses `rpdev->ept` as `default_ept`; dynamically created endpoints use `rpmsg_chrdev_eptdev_create()`. Open enforces single-open, gets a device reference, creates an endpoint if needed, sets `flow_cb`, and stores private data. RX callback copies inbound payloads into SKBs and wakes readers. Read blocks unless nonblocking, dequeues one SKB, copies up to user buffer length, and drops excess from that message. Write copies the iov into a kernel buffer and sends via `rpmsg_sendto()` or `rpmsg_trysendto()`. Poll reports readable data, flow-control priority updates, and backend TX readiness. Destroy detaches the endpoint, wakes readers, removes cdev/device, and drops the device reference.

State and persistence: all state is in memory and tied to rpmsg device lifetime. The incoming queue persists messages until read or release. `ept_lock` serializes endpoint pointer changes; `queue_lock` protects SKB queue operations. `remote_flow_updated` is cleared by `RPMSG_GET_OUTGOING_FLOWCONTROL`.

Dependencies and integration points: depends on rpmsg core APIs, `rpmsg_internal.h`, `rpmsg_char.h`, uapi `linux/rpmsg.h`, cdev/IDA allocation, SKB queues, wait queues, and backend support for flow control where available. `rpmsg_ctrl.c` uses the exported create/destroy helpers.

Risks: one open per endpoint is enforced; userspace expecting multi-reader semantics will get `-EBUSY`. Reads truncate messages larger than the supplied buffer and discard the remainder because the whole SKB is freed. `RPMSG_SET_INCOMING_FLOWCONTROL` calls backend flow control on `eptdev->ept`; callers must avoid ioctl after endpoint teardown. Allocation of write buffer equals user write length and can be large until backend rejects oversize messages.

Test signals: create static `rpmsg-raw` and dynamic endpoints, verify single-open, blocking and nonblocking read/write, poll for RX/TX and `EPOLLPRI`, flow-control ioctls, endpoint destroy ioctl, parent rpmsg removal while readers block, and message truncation semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/rpmsg_char.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/rpmsg_char.h -->
# sources/distributed-fs/ceph-client/drivers/rpmsg/rpmsg_char.h

Purpose: internal header for rpmsg character endpoint helpers shared by `rpmsg_char.c` and `rpmsg_ctrl.c`.

Important APIs, types, and functions: when `CONFIG_RPMSG_CHAR` is enabled, it declares `rpmsg_chrdev_eptdev_create(struct rpmsg_device *, struct device *, struct rpmsg_channel_info)` and `rpmsg_chrdev_eptdev_destroy(struct device *, void *)`. When disabled, inline stubs return `-ENXIO`.

Control flow: there is no runtime control flow beyond compile-time selection. `rpmsg_ctrl.c` can call the helper unconditionally and receive `-ENXIO` if char endpoints are not built.

State and persistence: no state is stored in this header.

Dependencies and integration points: depends on `struct rpmsg_device`, `struct device`, and `struct rpmsg_channel_info` definitions from rpmsg/device headers included by users. It is the contract between the control device and endpoint char-device implementation.

Risks: stale prototypes here would break cross-file builds. The disabled stubs make runtime ioctl failures possible if control support is enabled without endpoint char support.

Test signals: compile with `CONFIG_RPMSG_CHAR=y/m` and disabled; verify `rpmsg_ctrl.c` builds and `RPMSG_CREATE_EPT_IOCTL` reports `-ENXIO` through the helper when endpoint char support is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/rpmsg_char.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/rpmsg_core.c -->
# sources/distributed-fs/ceph-client/drivers/rpmsg/rpmsg_core.c

Purpose: generic rpmsg bus core. It registers the `rpmsg` class and bus, provides exported helper APIs for endpoint/channel/message operations, handles driver matching/probe/remove, and exposes rpmsg device sysfs attributes.

Important APIs, types, and functions: exported wrappers include `rpmsg_create_channel()`, `rpmsg_release_channel()`, `rpmsg_create_ept()`, `rpmsg_destroy_ept()`, `rpmsg_send()`, `rpmsg_sendto()`, `rpmsg_trysend()`, `rpmsg_trysendto()`, `rpmsg_poll()`, `rpmsg_set_flow_control()`, `rpmsg_get_mtu()`, `rpmsg_find_device()`, `rpmsg_register_device_override()`, `rpmsg_register_device()`, `rpmsg_unregister_device()`, `__register_rpmsg_driver()`, and `unregister_rpmsg_driver()`. `rpmsg_class` and the private `rpmsg_bus` are central objects.

Control flow: backend transports create `rpmsg_device` instances with ops and call `rpmsg_register_device()`. The bus matches devices by `driver_override`, rpmsg id table service name, or OF match. During probe, the core attaches a PM domain, creates a default endpoint if the driver supplied a callback, calls the driver's probe, and optionally announces channel creation to the remote. Remove announces destruction, calls driver remove, and destroys the default endpoint. Message APIs validate pointers and dispatch to endpoint ops supplied by the backend.

State and persistence: core state lives in the Linux driver model: class, bus, devices, drivers, sysfs attributes, driver overrides, and endpoint pointers stored in `rpdev`. No messages are persisted in the core; backends own queues and buffers.

Dependencies and integration points: depends on `rpmsg_internal.h` operation tables, Linux device model, OF modalias helpers, PM domains, and backend transports such as virtio, GLINK, and SMD. Userspace sees sysfs attributes `name`, `src`, `dst`, `announce`, `driver_override`, and `modalias`.

Risks: backend ops are only partially checked; missing required endpoint ops can surface as `-ENXIO` or backend crashes. Probe error paths must destroy endpoints and detach state through the driver model correctly. `driver_override` changes affect matching and modalias behavior. Destroy announcement runs before driver remove and endpoint destruction.

Test signals: register/unregister rpmsg drivers, dynamic channel create/release, service-name and OF matching, driver override sysfs store/show, default endpoint creation, announce_create/destroy callbacks, PM domain attach failures, send wrappers against missing ops, and class/bus init/exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/rpmsg_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/rpmsg_ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/rpmsg/rpmsg_ctrl.c

Purpose: rpmsg control character device. It exposes `/dev/rpmsg_ctrlN` for userspace to create endpoint char devices, request backend-created rpmsg channels, and release channels via ioctls.

Important APIs, types, and functions: `struct rpmsg_ctrldev` holds the backing `rpmsg_device`, cdev, device, and `ctrl_lock`. File ops are `rpmsg_ctrldev_open()`, `release()`, and `rpmsg_ctrldev_ioctl()`. The ioctl path accepts `struct rpmsg_endpoint_info` and handles `RPMSG_CREATE_EPT_IOCTL`, `RPMSG_CREATE_DEV_IOCTL`, and `RPMSG_RELEASE_DEV_IOCTL`. Probe/remove manage one control cdev per rpmsg control device.

Control flow: backend transports register a control rpmsg device, commonly through `rpmsg_ctrldev_register_device()`. Probe allocates a minor and control ID, initializes cdev, adds `rpmsg_ctrl%d`, and stores the control device in parent driver data. Open pins the device. Each ioctl copies endpoint info, builds `rpmsg_channel_info`, takes `ctrl_lock`, and either creates an endpoint char device below the control device, asks the backend to create a channel, or releases a channel. Remove serializes against ioctls, destroys all child endpoint devices, removes the cdev, and drops the reference.

State and persistence: state is runtime-only: IDA allocations, cdev lifetime, parent rpmsg pointer, and child endpoint devices. `ctrl_lock` serializes ioctl operations and removal.

Dependencies and integration points: depends on rpmsg core channel ops, `rpmsg_char.h` endpoint helpers, uapi `linux/rpmsg.h`, and `rpmsg_class`. Virtio and Qualcomm SMD create control rpmsg devices so userspace can instantiate endpoints.

Risks: the ioctl copies `struct rpmsg_endpoint_info` before switching on `cmd`, so even release/create-dev commands require a valid user pointer. If `CONFIG_RPMSG_CHAR` is disabled, endpoint creation returns `-ENXIO`. Backend create/release support is optional and can return `-ENXIO`. Removal relies on child endpoint destruction to wake blocked readers.

Test signals: open/close control devices, issue all three ioctls with valid and invalid user memory, create endpoint devices and communicate through them, create duplicate channels, release nonexistent channels, race removal with ioctl, and build with `CONFIG_RPMSG_CHAR` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/rpmsg_ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/rpmsg_internal.h -->
# sources/distributed-fs/ceph-client/drivers/rpmsg/rpmsg_internal.h

Purpose: private rpmsg core/backend interface. It defines internal conversion macros, exported class declaration, backend operation tables, channel helper prototypes, and the inline control-device registration wrapper.

Important APIs, types, and functions: `to_rpmsg_device()` and `to_rpmsg_driver()` convert device model objects. `struct rpmsg_device_ops` defines backend channel and endpoint operations plus optional announce hooks. `struct rpmsg_endpoint_ops` defines endpoint destroy/send/sendto/trysend/trysendto/poll/set_flow_control/get_mtu hooks. `rpmsg_find_device()`, `rpmsg_create_channel()`, and `rpmsg_release_channel()` are declared. `rpmsg_ctrldev_register_device()` wraps `rpmsg_register_device_override(rpdev, "rpmsg_ctrl")`.

Control flow: no runtime code except the inline control registration helper. Backends fill these ops tables and the core dispatches exported rpmsg APIs through them.

State and persistence: no state is stored here; it describes function-pointer contracts used by runtime objects.

Dependencies and integration points: includes public `linux/rpmsg.h` and `linux/poll.h`. It is included by rpmsg core, virtio, Qualcomm transports, char/control drivers, and name service.

Risks: operation table comments mark required and optional hooks, but runtime enforcement is uneven. A backend with missing required ops can pass compile and fail at runtime. The header is internal, so changes affect many transport implementations.

Test signals: compile all rpmsg backends after changing ops, exercise every exported rpmsg API against transports with and without optional hooks, and confirm control-device override binding to `rpmsg_ctrl`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/rpmsg_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/rpmsg_ns.c -->
# sources/distributed-fs/ceph-client/drivers/rpmsg/rpmsg_ns.c

Purpose: rpmsg name-service driver. It receives remote name-service announcements and creates or destroys rpmsg channels for advertised services.

Important APIs, types, and functions: `rpmsg_ns_register_device()` prepares an rpmsg device for the name-service address and registers it with driver override `rpmsg_ns`. `rpmsg_ns_cb()` parses `struct rpmsg_ns_msg`. `rpmsg_ns_probe()` creates the endpoint bound to `RPMSG_NS_ADDR` and name `name_service`.

Control flow: a backend that supports name service registers a special rpmsg device through `rpmsg_ns_register_device()`. Probe creates an endpoint at source and destination `RPMSG_NS_ADDR`. Incoming announcements are length-checked, name-terminated defensively, converted to `rpmsg_channel_info` with dynamic local source and advertised remote destination, and either passed to `rpmsg_create_channel()` or `rpmsg_release_channel()` depending on `RPMSG_NS_DESTROY`.

State and persistence: no private persistent state beyond `rpdev->ept`. Created channels become normal rpmsg devices owned by the backend/core. The callback mutates the received message buffer to force NUL termination.

Dependencies and integration points: depends on `linux/rpmsg/ns.h`, rpmsg core channel helpers, byteorder helpers through `rpmsg32_to_cpu()`, and backend name-service support such as virtio feature `VIRTIO_RPMSG_F_NS`.

Risks: malformed sizes are rejected, but remote announcements still control service names and destination addresses. Duplicate creates depend on backend duplicate detection. Destroy requests for nonexistent channels log backend errors. The log message intentionally reports create/destroy decisions but has the historical `"creat"` string for create.

Test signals: send valid create and destroy NS messages, malformed lengths, unterminated maximum-length names, duplicate creates, destroy missing channel, and verify dynamic channel devices bind to matching rpmsg drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/rpmsg_ns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/virtio_rpmsg_bus.c -->
# sources/distributed-fs/ceph-client/drivers/rpmsg/virtio_rpmsg_bus.c

Purpose: virtio transport backend for rpmsg. It owns the virtqueues, coherent TX/RX buffer pool, endpoint IDR, name-service/control devices, channel creation, message send/receive, and virtio driver registration for `VIRTIO_ID_RPMSG`.

Important APIs, types, and functions: `struct virtproc_info` tracks the virtio device, RX/TX virtqueues, buffers, DMA handle, TX lock, endpoint IDR, and sender waitqueue. `struct rpmsg_hdr` is the wire header. `struct virtio_rpmsg_channel` embeds `struct rpmsg_device`. Endpoint ops are implemented by `virtio_rpmsg_send*()`, `virtio_rpmsg_trysend*()`, `virtio_rpmsg_poll()`, `virtio_rpmsg_get_mtu()`, and `virtio_rpmsg_destroy_ept()`. Channel ops are `virtio_rpmsg_create_channel()`, `virtio_rpmsg_release_channel()`, `virtio_rpmsg_create_ept()`, and announce hooks.

Control flow: probe allocates `virtproc_info`, initializes IDR/locks/waitqueue, finds input/output virtqueues, sizes a 512-byte buffer pool up to 512 buffers, allocates coherent DMA memory, posts half the buffers to the RX virtqueue, registers an rpmsg control device, optionally registers the name-service device when feature bit 0 is present, prepares an RX kick, marks the virtio device ready, and notifies the remote. TX gets an unused or recycled send buffer, optionally waits up to 15 seconds, validates addresses and MTU, fills `rpmsg_hdr`, adds an outbuf, and kicks the TX virtqueue. RX callback drains used RX buffers, validates payload length, looks up endpoint by destination address under the IDR lock, pins it by kref, calls its callback under `cb_lock`, reposts the buffer, and kicks the RX virtqueue after processing messages.

State and persistence: runtime state includes endpoint IDR allocations, `last_sbuf` simple allocator state, coherent buffers, virtqueue state, and child rpmsg devices. No state persists beyond virtio device lifetime. Local dynamic endpoint addresses start at 1024 to reserve low addresses for predefined services.

Dependencies and integration points: depends on virtio core, DMA coherent memory, scatterlists, rpmsg core/internal APIs, rpmsg name service, and rpmsg control device. It exports user-facing dynamic behavior through rpmsg devices created from NS announcements and `/dev/rpmsg_ctrlN`.

Risks: the TX allocator is intentionally simple; a failed `virtqueue_add_outbuf()` can lose a TX buffer until broader buffer management is changed. Blocking sends use a fixed 15-second timeout and return `-ERESTARTSYS` on timeout. RX length validation is critical because the remote controls headers. Endpoint lifetime uses IDR plus kref plus callback mutex; regressions here risk use-after-free. Remove destroys child devices after virtio reset, then destroys IDR and frees coherent memory.

Test signals: virtio probe/remove, vring size variations, NS feature on/off, control-device registration, channel duplicate detection, dynamic endpoint address allocation, MTU enforcement, blocking and nonblocking send exhaustion, TX completion wakeups, malformed RX headers, no-recipient RX, endian conversions, and hot-unplug while endpoints are open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rpmsg/virtio_rpmsg_bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/rtc/Kconfig

Purpose: Kconfig menu for the Linux RTC subsystem and its chip/platform drivers. It defines core RTC library/class features, user interfaces, clock synchronization policy, optional tests/NVMEM, and hundreds of transport- or SoC-specific RTC driver symbols.

Important APIs, types, and functions: this is declarative Kconfig rather than C. Key symbols are `RTC_LIB`, `RTC_MC146818_LIB`, `RTC_CLASS`, `RTC_HCTOSYS`, `RTC_HCTOSYS_DEVICE`, `RTC_SYSTOHC`, `RTC_SYSTOHC_DEVICE`, `RTC_DEBUG`, `RTC_LIB_KUNIT_TEST`, `RTC_NVMEM`, `RTC_INTF_SYSFS`, `RTC_INTF_PROC`, `RTC_INTF_DEV`, and `RTC_INTF_DEV_UIE_EMUL`. Driver symbols follow `RTC_DRV_*` naming and are grouped mainly under I2C, SPI, shared I2C/SPI, legacy/platform, SoC, and special firmware/EC sections.

Control flow: selecting `RTC_CLASS` enables the core menu and selects `RTC_LIB`. Interface symbols default to `RTC_CLASS`, so sysfs/proc/dev support normally follows the class unless disabled. `RTC_HCTOSYS_DEVICE` and `RTC_SYSTOHC_DEVICE` choose the RTC device name used for system-clock initialization/resume and periodic NTP-to-hardware-clock synchronization. Individual driver entries set dependencies (`depends on I2C`, `SPI_MASTER`, `MFD_*`, architecture symbols, `COMPILE_TEST`) and select helper subsystems such as `REGMAP_I2C`, `WATCHDOG_CORE`, `NVMEM`, or `HWMON`.

State and persistence: Kconfig output persists in the kernel `.config` and controls which objects are compiled into vmlinux or modules. It does not store runtime state, but choices directly affect RTC class behavior and which hardware can register.

Dependencies and integration points: feeds `drivers/rtc/Makefile`, RTC core C files, per-chip drivers, KUnit, NVMEM, watchdog, hwmon, MFD, I2C, SPI, platform, architecture, and firmware interfaces. It also controls user ABI availability for `/sys/class/rtc`, `/proc/driver/rtc`, and `/dev/rtcN`.

Risks: defaulting `RTC_HCTOSYS` and `RTC_SYSTOHC` to yes can affect system time if the chosen RTC is not battery-backed or not UTC. Driver dependencies must stay aligned with actual source includes and bus APIs. Shared chips with watchdog/hwmon features can silently select extra subsystems. Menu sprawl makes duplicate or stale driver entries easy to introduce.

Test signals: run Kconfig olddefconfig/allmodconfig/randconfig, verify selected objects match Makefile mappings, check `RTC_CLASS=n` hides drivers, validate interface combinations, exercise KUnit via `RTC_LIB_KUNIT_TEST`, and boot configs with different `RTC_HCTOSYS_DEVICE`/`RTC_SYSTOHC_DEVICE` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/rtc/Makefile

Purpose: build mapping for the RTC subsystem. It maps Kconfig symbols to core objects, optional interface objects, test objects, and ordered per-driver modules.

Important APIs, types, and functions: `ccflags-$(CONFIG_RTC_DEBUG) := -DDEBUG` enables debug builds. `obj-$(CONFIG_RTC_LIB) += lib.o`, `obj-$(CONFIG_RTC_CLASS) += rtc-core.o`, and `obj-$(CONFIG_RTC_MC146818_LIB) += rtc-mc146818-lib.o` build core libraries. `rtc-core-y := class.o interface.o` is extended by `rtc-core-$(CONFIG_RTC_NVMEM) += nvmem.o`, `rtc-core-$(CONFIG_RTC_INTF_DEV) += dev.o`, `rtc-core-$(CONFIG_RTC_INTF_PROC) += proc.o`, and `rtc-core-$(CONFIG_RTC_INTF_SYSFS) += sysfs.o`. `obj-$(CONFIG_RTC_LIB_KUNIT_TEST) += test_rtc_lib.o` adds tests.

Control flow: Kbuild evaluates each `CONFIG_RTC_*` symbol and links built-in or module objects accordingly. The file keeps the driver list ordered and maps each `RTC_DRV_*` symbol to its `rtc-*.o` object, including I2C, SPI, platform, SoC, MFD, firmware, and EC-backed drivers. `rtc-core.o` is a composite object whose contents change with interface and NVMEM config.

State and persistence: no runtime state. Build artifacts and module availability are determined by this mapping.

Dependencies and integration points: integrates Kconfig symbols with the kernel build system and all source files in `drivers/rtc`. It must stay synchronized with `Kconfig` names and actual `rtc-*.c` filenames.

Risks: a typo in an object mapping silently drops or misbuilds a driver for that config. Composite `rtc-core` contents must match exported symbols expected by drivers and userspace interfaces. The list is ordered, so new entries should preserve maintainability and avoid duplicate object inclusion.

Test signals: build `RTC_CLASS=y`, interface permutations, allmodconfig, randconfig, `RTC_DEBUG=y`, `RTC_LIB_KUNIT_TEST=m/y`, and representative drivers from each bus group. Use `make drivers/rtc/` or full kernel builds to catch missing files and symbol mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/class.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/class.c

Purpose: RTC class core registration and managed device lifecycle. It allocates `struct rtc_device`, assigns IDs, initializes timers/queues/features, registers cdev/proc/sysfs-facing class devices, optionally sets system time from RTC, and handles suspend/resume time injection.

Important APIs, types, and functions: `rtc_class` is the exported class object. `rtc_device_release()` tears down timer queues, work, IDA, mutex, and memory. `devm_rtc_allocate_device()`, `__devm_rtc_register_device()`, and deprecated `devm_rtc_device_register()` are exported driver-facing APIs. `rtc_hctosys()` reads RTC and calls `do_settimeofday64()`. PM hooks `rtc_suspend()` and `rtc_resume()` track RTC/system deltas and inject sleep time. `rtc_device_get_offset()` computes range expansion offset from `start-year`.

Control flow: subsystem init registers the class and initializes char-device support. Drivers allocate a managed RTC device, set ops and ranges/features, then register it. Registration verifies ops, clears unsupported alarm feature, marks correction support, computes offset, reads existing alarm into RTC timer state, prepares the char device, adds cdev/device, adds proc entry, logs registration, optionally runs hctosys for the configured device, and installs a devm unregister action. Release removes pending timers and cancels IRQ work after device references drain.

State and persistence: runtime state includes IDA-assigned `rtcN`, feature bits, ops pointer, alarm/update/periodic timers, timerqueue, IRQ work, offset/start-year fields, and the global `rtc_hctosys_ret`. Actual time persists in RTC hardware; the class stores only kernel-side metadata. Suspend/resume stores global old RTC/system/delta snapshots for the configured hctosys device.

Dependencies and integration points: depends on RTC core interfaces from `rtc-core.h`, char device setup from `dev.c`, proc/sysfs/nvmem optional pieces, timekeeping APIs, OF aliases, device properties, PM, timerqueue, hrtimer, IDA, and devres. It is the central integration point for all chip drivers using `rtc_class_ops`.

Risks: hctosys assumes the configured device stores UTC and whole seconds; wrong devices can set system time badly. ID allocation honors OF aliases but falls back if an alias is unavailable. Offset calculation for limited-range hardware is subtle and must handle overflow/range mapping. Registration continues if char device creation fails by setting `RTC_NO_CDEV`, so tests must check degraded interface availability.

Test signals: allocate/register/unregister RTC devices, OF alias collisions, char-device failure path, alarm initialization from hardware, hctosys success/error and 32-bit range checks, start-year offset mappings, suspend/resume sleep-time injection, and feature bit exposure for alarm/correction/update interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/class.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/dev.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/dev.c

Purpose: `/dev/rtcN` character-device implementation for the RTC subsystem. It handles single-open access, blocking interrupt reads, poll/fasync, legacy and modern RTC ioctls, optional update-interrupt emulation, and char-device preparation.

Important APIs, types, and functions: `rtc_dev_open()` enforces `RTC_DEV_BUSY` and clears IRQ data. Optional UIE emulation uses `rtc_uie_task()`, `rtc_uie_timer()`, `set_uie()`, `clear_uie()`, and exported `rtc_dev_update_irq_enable_emul()`. User operations include `rtc_dev_read()`, `rtc_dev_poll()`, `rtc_dev_ioctl()`, compat ioctl handling, `rtc_dev_fasync()`, and `rtc_dev_release()`. Setup APIs are `rtc_dev_prepare()` and `rtc_dev_init()`.

Control flow: `rtc_dev_init()` allocates up to 16 RTC char-device numbers. `rtc_dev_prepare()` assigns `devt`, initializes optional UIE emulation work/timer, and initializes `char_dev` with file ops. Open rejects concurrent users, stores the RTC in `private_data`, and clears pending IRQ data. Read waits on `irq_queue` until `rtc->irq_data` is nonzero, nonblocking returns `-EAGAIN`, and signal interruption returns `-ERESTARTSYS`; it copies an `unsigned int` or `unsigned long` event word. Ioctl checks permissions, handles alarms, time read/set, PIE/AIE/UIE toggles, IRQ frequency, wake alarms, feature/correction params, driver-specific params, and fallback driver ioctls. Release disables UIE and PIE but leaves one-shot alarms intact, then clears busy.

State and persistence: state lives in the `rtc_device`: busy flag, IRQ data, IRQ frequency, max user frequency, async queue, UIE emulation flags/timer/work, and ops pointer. Time and alarms persist in hardware through `rtc_class_ops`.

Dependencies and integration points: depends on RTC interface helpers (`rtc_read_time`, `rtc_set_time`, `rtc_read_alarm`, `rtc_set_alarm`, `rtc_irq_set_state`, `rtc_update_irq_enable`, `rtc_alarm_irq_enable`, `rtc_read_offset`, `rtc_set_offset`), Linux cdev, wait queues, fasync, capabilities, compat ioctl, timers, and workqueues.

Risks: only one process can open a given RTC char device. `RTC_ALM_SET` emulates 24-hour wrap and cannot support wildcard periodic alarms. Permission checks are centralized and must stay aligned with security expectations (`CAP_SYS_TIME`, `CAP_SYS_RESOURCE`). UIE emulation polls hardware repeatedly and can be expensive. Release invokes ioctl-style UIE disable while tearing down, so ops locking and driver removal interactions matter.

Test signals: open exclusivity, blocking/nonblocking reads, poll/fasync delivery from `rtc_handle_legacy_irq()`, all standard ioctls with permission boundaries, compat ioctl translations, UIE emulation on hardware without update IRQs, release cleanup of repeating interrupts, and behavior when `rtc->ops` disappears during unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/dev.c -->
