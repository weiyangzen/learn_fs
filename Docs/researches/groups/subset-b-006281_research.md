# Research Group: subset-b-006281

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_core.c -->
# sources/distributed-fs/ceph-client/net/smc/smc_core.c

## Purpose
`smc_core.c` is the central lifetime and resource manager for Linux SMC link groups, links, connections, buffers, remote RMB tokens, and SMC-R/SMC-D teardown. It bridges connection setup from CLC negotiation into reusable link groups, allocates and maps SMC-R RDMA memory or SMC-D DMBs, exposes link-group state through generic netlink dump helpers, and reacts to RDMA/ISM device shutdown.

## Important APIs, Types, and Functions
Key exports include `smc_conn_create()`, `smc_conn_free()`, `smc_buf_create()`, `smcd_buf_attach()`, `smcr_link_init()`, `smcr_link_clear()`, `smcr_link_down_cond_sched()`, `smc_smcr_terminate_all()`, `smc_smcd_terminate_all()`, `smc_rtoken_add()`, `smc_rtoken_delete()`, and generic netlink dump entry points for system, SMC-R link groups, SMC-R links, and SMC-D link groups. The file owns global `smc_lgr_list`, `lgr_cnt`, and the `lgrs_deleted` wait queue for SMC-R groups. It uses `struct smc_link_group`, `struct smc_link`, `struct smc_buf_desc`, and `struct smc_rtoken` from `smc_core.h`.

## Control Flow
Connection setup starts in `smc_conn_create()`. It selects an SMC-D device list or global SMC-R list, tries to match an existing group with `smcd_lgr_match()` or `smcr_lgr_match()`, registers the connection under `conns_lock`, or creates a new group via `smc_lgr_create()`. New SMC-R groups allocate per-group WR memory, initialize LLC, create the first link with `smcr_link_init()`, and register in `smc_lgr_list`; SMC-D groups take an ISM device reference and are registered on the device's group list. Teardown flows through delayed free work, scheduled terminate work, device-wide termination, or early cleanup paths. SMC-R link loss routes through `smcr_link_down_cond_sched()`, `smc_link_down_work()`, `smc_switch_conns()`, LLC delete-link handling, and finally `smcr_link_clear()`.

## State and Persistence
All state is in-memory kernel state: link groups in lists, connections in an rb-tree keyed by alert token, reusable send/RMB buffer lists per compressed size, rtoken bitmaps, per-link reference counts, and delayed work items. No durable persistence exists. Refcounts (`smc_lgr_hold/put`, `smcr_link_hold/put`), socket holds, delayed work, wait queues, rwsems, spinlocks, and atomics preserve lifetime while link groups are visible to sockets, netlink, RDMA callbacks, and workqueues. Buffer descriptors may be reused after `used` is cleared and memory is zeroed.

## Dependencies and Integration Points
This file depends on RDMA verbs and SMC WR helpers for SMC-R mapping, QP setup, memory registration, and send/receive wakeups; ISM helpers for SMC-D DMB registration and peer shutdown signaling; LLC for link add/delete and rkey negotiation; CDC/close/stat/trace modules for connection state and diagnostics; and generic netlink for state dumps. It is initialized through `smc_core_init()` and cleaned by `smc_core_exit()`, with a reboot notifier that shuts down SMC-R and SMC-D devices before unregistering lower clients.

## Risks
The main risks are concurrency and lifetime bugs: link groups can be removed from public lists while connections, work items, and device callbacks still hold references; LLC and buffer registration paths must not race link deletion; reusable buffers must be fully unmapped, deregistered, zeroed, or freed after registration errors; and alert-token rb-tree updates require correct `conns_lock` coverage. SMC-D peer GID matching has different behavior for emulated devices, so incorrect matching can terminate or reuse the wrong group. Netlink dump paths hold locks while filling skbs, so message-size failures must leave cursor state coherent.

## Test Signals
Useful tests include SMC-R and SMC-D connect/reuse/close cycles, repeated connection churn to exercise delayed free work, link failover with two active RoCE paths, device removal during traffic, DMB no-copy attach/detach, VLAN negotiation, memory-pressure buffer downgrade, rtoken add/delete under parallel connection creation, generic netlink dumps for link groups and links, and reboot/module-unload teardown with no leaked references or hung waits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_core.h -->
# sources/distributed-fs/ceph-client/net/smc/smc_core.h

## Purpose
`smc_core.h` is the shared contract for the SMC core, SMC-R link, SMC-D group, buffer, token, and initialization structures. It defines the in-memory model consumed by the connection setup, RDMA, LLC, CDC, ISM, diagnostics, and netlink code.

## Important APIs, Types, and Functions
The header defines `struct smc_lgr_list`, `enum smc_lgr_role`, `enum smc_link_state`, WR buffer types, `struct smc_link`, `struct smc_buf_desc`, `struct smc_rtoken`, `enum smc_lgr_type`, `enum smcr_buf_type`, `enum smc_llc_flowtype`, `struct smc_llc_flow`, `struct smc_link_group`, `struct smc_init_info_smcrv2`, and `struct smc_init_info`. Inline helpers include `smc_lgr_find_conn()`, `smc_conn_lgr_valid()`, `smc_link_usable()`, `smc_link_sendable()`, `smc_link_active()`, `smc_link_shared_v2_rxbuf()`, `smc_gid_be16_convert()`, `smc_set_pci_values()`, and `smc_get_lgr()`. It declares exported core lifecycle, buffer, link, rtoken, VLAN, netlink, and termination functions.

## Control Flow
The header does not execute flow itself, but it encodes the control boundaries. `struct smc_init_info` carries CLC negotiation results into `smc_conn_create()`. `struct smc_link_group` unifies SMC-R and SMC-D through a tagged union, so most core code first checks `is_smcd` before interpreting either RoCE link arrays and LLC state or ISM peer/device state. Link state helpers distinguish receive-capable links from fully sendable RTS links, which is important during first contact and link add flows.

## State and Persistence
All fields are transient kernel memory. `struct smc_link_group` persists while refcounted by connections, links, work items, or global/device lists. It stores buffer pools, connection rb-tree, workqueue, delayed free/terminate work, SMC protocol version details, peer identity, SMC-R rtoken table, LLC flow state, and SMC-D peer GID/device state. `struct smc_link` carries QP, CQ-facing WR vectors, DMA addresses, GIDs, QP numbers, PSNs, link IDs, UID fields, work items, and counters.

## Dependencies and Integration Points
The header includes Linux atomics, PCI, RDMA verbs, generic netlink, `net/smc.h`, local SMC, IB, and CLC headers. Its declarations are used by `smc_core.c`, `smc_llc.c`, `smc_ib.c`, `smc_ism.c`, `smc_diag.c`, and netlink code. It also exposes netlink dump entry points consumed by the generic netlink operation table.

## Risks
Because this header centralizes cross-module layout, field changes have broad ABI-like internal impact. The union in `struct smc_link_group` requires strict `is_smcd` checks. Inline link state helpers have subtly different semantics, so using `smc_link_usable()` where `smc_link_sendable()` is required can send on a QP that is not RTS. The buffer descriptor union also requires callers to know whether a descriptor belongs to SMC-R or SMC-D.

## Test Signals
Compile coverage across SMC-R, SMC-D, IPv6, s390, and non-s390 configurations is important. Runtime signals include correct link-group reuse, netlink dumps, link failover, SMC-D DMB handling, SMC-R v2 shared receive buffers, PCI metadata reporting, and no lockdep or KASAN reports around connection and buffer lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_diag.c -->
# sources/distributed-fs/ceph-client/net/smc/smc_diag.c

## Purpose
`smc_diag.c` implements SOCK_DIAG support for AF_SMC sockets. It lets user space dump SMC socket state, fallback reason, connection cursors, SMC-R link details, and SMC-D DMB details through the standard netlink socket diagnostics path.

## Important APIs, Types, and Functions
The local cursor type is `struct smc_diag_dump_ctx`, stored in `netlink_callback->ctx`. `smc_diag_msg_common_fill()` copies common address and cookie information from the SMC socket and its CLC TCP socket. `__smc_diag_dump()` emits one `struct smc_diag_msg` plus optional attributes. `smc_diag_dump_proto()` walks one SMC protocol hash table, and `smc_diag_dump()` dumps IPv4 then IPv6 SMC sockets. Module init/exit register and unregister `smc_diag_handler` for `AF_SMC`.

## Control Flow
A `SOCK_DIAG_BY_FAMILY` dump request enters `smc_diag_handler_dump()`, which starts a netlink dump with `smc_diag_dump()`. The dump scans `smc_proto` and, if IPv6 is enabled, `smc_proto6`, applying net namespace filtering and using per-protocol position cursors. For each socket, `__smc_diag_dump()` creates a netlink message, selects diagnostic mode as fallback TCP, SMC-D, or SMC-R, fills common attrs, then conditionally appends `SMC_DIAG_CONNINFO`, `SMC_DIAG_LGRINFO`, or `SMC_DIAG_DMBINFO` based on requested extensions and connection validity.

## State and Persistence
The file persists no state beyond module registration. Dump progress is held in callback context positions. It reads live socket and link-group state, so output is a snapshot under protocol hash lock plus checks such as `smc_conn_lgr_valid()` and `list_empty()`.

## Dependencies and Integration Points
It depends on Linux sock_diag/inet_diag/netlink APIs, `smc_proto`, `smc_proto6`, socket helpers from `smc.h`, core link-group helpers from `smc_core.h`, and ISM GID conversion from `smc_ism.h`. It exposes module aliases for NETLINK_SOCK_DIAG AF_SMC and the SMC-R generic netlink family name.

## Risks
Diagnostic dumps read a large amount of live state with minimal stabilization beyond hash locking and validity checks. Races with close, fallback, or link-group teardown could produce partial data, so every optional block must tolerate missing descriptors and removed groups. Message-size failures must cancel the current netlink message correctly. IPv6 paths are compiled conditionally and need coverage when enabled.

## Test Signals
Use `ss`, `sock_diag`, or SMC-specific diagnostic tools to dump AF_SMC sockets in fallback, SMC-R, and SMC-D modes. Validate extension masks for connection, link-group, and DMB info. Exercise sockets while closing or during link-group teardown and confirm no kernel warnings, malformed netlink messages, or stale namespace leakage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_hs_bpf.c -->
# sources/distributed-fs/ceph-client/net/smc/smc_hs_bpf.c

## Purpose
`smc_hs_bpf.c` adds BPF `struct_ops` support for SMC handshake control. It allows validated BPF-provided `struct smc_hs_ctrl` instances to be registered by name and later found by handshake code under RCU.

## Important APIs, Types, and Functions
The file maintains `smc_hs_ctrl_list` protected by `smc_hs_ctrl_list_lock` and read via RCU. `smc_hs_ctrl_reg()` rejects duplicate names and adds controls with `list_add_tail_rcu()`. `smc_hs_ctrl_unreg()` deletes with `list_del_rcu()` and waits for `synchronize_rcu()`. `smc_hs_ctrl_find_by_name()` is the exported lookup helper. BPF integration is provided by `bpf_smc_hs_ctrl_ops`, `smc_bpf_hs_ctrl_reg()`, `smc_bpf_hs_ctrl_unreg()`, `smc_bpf_hs_ctrl_init_member()`, and `bpf_smc_hs_ctrl_init()`.

## Control Flow
At SMC initialization, `bpf_smc_hs_ctrl_init()` registers the `smc_hs_ctrl` struct_ops type. A BPF struct_ops registration is copied and validated member-by-member; only `name` and `flags` receive special initialization, with flags masked by `SMC_HS_CTRL_ALL_FLAGS`. Registration refuses bpf_link-backed attach (`-EOPNOTSUPP`) and inserts the object into the global RCU list. Consumers call `smc_hs_ctrl_find_by_name()` while holding `rcu_read_lock()`.

## State and Persistence
State is the in-memory RCU list of registered handshake controllers. The code uses static CFI stub callbacks that return success-like values, making indirect-call validation safe before BPF implementations are attached. No persistent storage exists.

## Dependencies and Integration Points
The implementation depends on BPF verifier, BTF, BPF struct_ops, RCU list APIs, and `net/smc.h` for `struct smc_hs_ctrl`. It is compiled only when `CONFIG_SMC_HS_CTRL_BPF` is enabled, with a no-op inline init in the header otherwise. Handshake code can look up named controls without depending on BPF details.

## Risks
The lookup contract requires callers to hold `rcu_read_lock()`; violating that can race unregister. Duplicate-name prevention is under a spinlock but lookup itself is RCU, so all list updates must keep the unregister synchronize point. Member initialization currently accepts only name and flags specially; future `struct smc_hs_ctrl` fields need explicit verifier/copy semantics. Returning `-EOPNOTSUPP` for link-backed registrations should match expected user-space attach behavior.

## Test Signals
Test with `CONFIG_SMC_HS_CTRL_BPF=y`, register a valid struct_ops controller, reject duplicate names and invalid flags, unregister while concurrent lookups run, and confirm SMC init succeeds with and without the config. BPF verifier tests should check name-copy failure, flag masks, and allowed helper prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_hs_bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_hs_bpf.h -->
# sources/distributed-fs/ceph-client/net/smc/smc_hs_bpf.h

## Purpose
`smc_hs_bpf.h` declares the handshake-control lookup and conditional BPF struct_ops initialization hook for SMC handshake customization.

## Important APIs, Types, and Functions
The header exposes `smc_hs_ctrl_find_by_name(const char *name)` and `bpf_smc_hs_ctrl_init()`. The lookup comment documents that `name` must be a C string and callers must hold `rcu_read_lock()`. When `CONFIG_SMC_HS_CTRL_BPF` is disabled, `bpf_smc_hs_ctrl_init()` is an inline no-op returning 0.

## Control Flow
SMC initialization can call `bpf_smc_hs_ctrl_init()` without config-specific branches. Handshake code can search for a named `struct smc_hs_ctrl`, but the implementation expects the caller to provide RCU read-side protection.

## State and Persistence
The header owns no state. It defines access to an implementation-managed RCU list when BPF support is enabled.

## Dependencies and Integration Points
It includes `net/smc.h` for `struct smc_hs_ctrl` and is implemented by `smc_hs_bpf.c`. It is an integration seam between core SMC handshake code and optional BPF struct_ops support.

## Risks
The most important risk is misuse of the RCU contract. A caller that stores the returned pointer after leaving the read-side critical section can race unregister. The no-op init path also means feature availability must be checked by registration/lookup behavior, not by init success alone.

## Test Signals
Build both enabled and disabled BPF configurations. Confirm callers compile without conditional code, lookup returns NULL for absent names, and RCU usage is covered by lockdep or targeted concurrency tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_hs_bpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_ib.c -->
# sources/distributed-fs/ceph-client/net/smc/smc_ib.c

## Purpose
`smc_ib.c` is the SMC-R RDMA/InfiniBand client layer. It discovers RoCE devices and ports, tracks PNET IDs and network-device indexes, creates protection domains, completion queues, queue pairs, memory regions, and DMA mappings, transitions QPs through INIT/RTR/RTS, and notifies the SMC core when ports or devices appear, disappear, or lose valid GIDs.

## Important APIs, Types, and Functions
Global state includes `smc_ib_devices` and `local_systemid`. Public functions include `smc_ib_register_client()`, `smc_ib_unregister_client()`, `smc_ib_setup_per_ibdev()`, `smc_ib_create_protection_domain()`, `smc_ib_create_queue_pair()`, `smc_ib_ready_link()`, QP state modifiers, `smc_ib_determine_gid()`, `smc_ib_find_route()`, memory-region and DMA-sync helpers, `smc_ib_ndev_change()`, and `smcr_nl_get_device()`. The RDMA client callbacks are `smc_ib_add_dev()` and `smc_ib_remove_dev()`.

## Control Flow
Registration initializes a random local system ID prefix and calls `ib_register_client()`. Device add allocates `struct smc_ib_device`, registers an IB event handler, derives PNET IDs from device/port or the PNET table, records netdev ifindexes, and schedules port attribute work. Port event work refreshes `ib_port_attr` and MAC, marks ports going away on errors, calls `smcr_port_err()` on loss, calls `smcr_port_add()` on activation, and verifies existing link GIDs. Link creation uses `smc_ib_create_protection_domain()`, `smc_ib_create_queue_pair()`, and `smc_ib_ready_link()` to transition QPs and post initial receives. Device removal unregisters from lists, terminates affected SMC-R groups, destroys per-device CQs, unregisters event handlers, and frees state.

## State and Persistence
State is in-memory per RDMA device: port attributes, CQ pointers, tasklets owned by WR code, MACs, PNET IDs, port going-away bitmaps, link counters, netdev ifindexes, and a mutex protecting setup/cleanup. Memory mappings are represented in `smc_buf_desc` SG tables and MRs per link index. No durable state is written.

## Dependencies and Integration Points
The file integrates RDMA verbs/cache APIs, IPv4 route and neighbour lookup, VLAN/netdevice APIs, SMC PNET lookup, SMC core link failover/termination, SMC WR CQ handlers, and generic netlink device dump output. `smc_core.c` calls it during link and buffer setup, while RDMA event callbacks call back into core for failover and termination.

## Risks
RDMA device events can arrive in IRQ context and are deferred to workqueues, so port bitmaps and going-away flags must avoid lost transitions. GID selection differs between SMC-R v1 RoCE and SMC-R v2 RoCE UDP encapsulation, including route and subnet checks; mistakes can bind a link to an unusable GID or gateway. DMA mapping assumes the SMC protocol can use one contiguous DMA mapping result; partial or chained mappings must fail cleanly. Device removal must wait for link counters to drain to avoid freeing RDMA resources still used by links.

## Test Signals
Exercise RoCE device add/remove, port up/down, GID change, VLAN and non-VLAN paths, SMC-R v1 and v2 route selection, gateway and direct modes, QP fatal events, memory registration/unregistration under traffic, netlink device dumps, and module unload while links are active. Lockdep, KASAN, RDMA resource leak checks, and failover traffic continuity are strong signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_ib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_ib.h -->
# sources/distributed-fs/ceph-client/net/smc/smc_ib.h

## Purpose
`smc_ib.h` defines the SMC-R RDMA device abstraction and declares the RDMA helper API used by core, LLC, PNET, and netlink code.

## Important APIs, Types, and Functions
The header defines `SMC_MAX_PORTS`, `SMC_GID_SIZE`, `SMC_IB_MAX_SEND_SGE`, `struct smc_ib_devices`, and `struct smc_ib_device`. It declares the global `smc_ib_devices` and `smc_lgr_list`. Inline helpers are `smc_ib_gid_to_ipv4()` and `smc_ib_net()`. Function declarations cover RDMA client registration, port activity, protection domains, QPs, QP readiness and error transitions, per-device setup, memory region registration, SG DMA mapping/syncing, GID determination, route lookup, local system ID validity, netdevice change handling, and netlink device dumping.

## Control Flow
The header establishes the flow expected by callers: discover/track devices through `smc_ib_register_client()`, initialize per-device CQs lazily through `smc_ib_setup_per_ibdev()`, create PD/QP resources per link, move QPs into a usable state with `smc_ib_ready_link()`, map buffers and MRs per link index, and call error/cleanup APIs during link teardown.

## State and Persistence
`struct smc_ib_device` keeps device-list linkage, RDMA device pointer, per-port attrs, CQs, tasklets, MAC and PNET IDs, initialized flag, work item, port masks, link counters, deletion wait queue, setup mutex, per-port link counters, and netdev ifindexes. The state is transient and tied to the RDMA client lifetime.

## Dependencies and Integration Points
The header depends on interrupt, Ethernet, mutex, wait, RDMA verbs, and SMC public headers. It is included by `smc_core.h`, `smc_ib.c`, and other SMC modules needing RDMA state. `smc_ib_net()` uses RDMA core network namespace state, and `smc_ib_gid_to_ipv4()` is used by SMC-R v2 routing and LLC add-link logic.

## Risks
The two-port maximum is encoded in arrays and counters, so any future hardware or protocol expansion needs careful resizing. Callers must use one-based RDMA port numbers when indexing with `ibport - 1`. DMA sync helpers require correct direction and link index. `smc_ib_net()` can return NULL if device state is absent, so callers need valid RDMA device lifetime.

## Test Signals
Compile with RDMA and IPv6 variations, then run SMC-R traffic over one and two ports, verify PNET table interactions, netdevice index updates, GID-to-IPv4 extraction for v2, and cleanup after RDMA client unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_ib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_inet.c -->
# sources/distributed-fs/ceph-client/net/smc/smc_inet.c

## Purpose
`smc_inet.c` registers SMC as an `IPPROTO_SMC` stream protocol under the IPv4 and optional IPv6 inet protocol switch. It maps normal socket operations to SMC socket handlers while creating the internal CLC TCP socket during socket initialization.

## Important APIs, Types, and Functions
Key objects are `smc_inet_prot`, `smc_inet_stream_ops`, `smc_inet_protosw`, and, under IPv6, `struct smc6_sock`, `smc_inet6_prot`, `smc_inet6_stream_ops`, and `smc_inet6_protosw`. Public lifecycle functions are `smc_inet_init()` and `smc_inet_exit()`. `smc_inet_init_sock()` initializes the common SMC socket and creates the CLC socket.

## Control Flow
`smc_inet_init()` registers the IPv4 proto, registers the IPv4 protosw, then conditionally registers IPv6 proto and protosw. Error paths unwind previously registered components in reverse order. Socket creation invokes `smc_inet_init_sock()`, which calls `smc_sk_init(net, sk, IPPROTO_SMC)` and `smc_create_clcsk()`. Socket operations then dispatch to SMC implementations such as `smc_connect`, `smc_accept`, `smc_sendmsg`, and `smc_recvmsg`.

## State and Persistence
The registered proto objects are static module state. Per-socket state is allocated as `struct smc_sock` for IPv4 and `struct smc6_sock` for IPv6, with `SLAB_TYPESAFE_BY_RCU` and protocol hash integration. No persistent storage exists.

## Dependencies and Integration Points
It depends on inet protocol registration APIs, socket/proto infrastructure, and the common SMC socket implementation in `smc.h`. It is the user-facing entry path for applications that create `IPPROTO_SMC` sockets through PF_INET or PF_INET6.

## Risks
Registration ordering and unwind correctness are critical, especially when IPv6 registration partially fails. The IPv6 object embeds `ipv6_pinfo` after `struct smc_sock`, so `ipv6_pinfo_offset` must remain correct. Any missing socket op can break expected stream behavior. CLC socket creation failure must propagate so partially initialized SMC sockets are not exposed.

## Test Signals
Create IPv4 and IPv6 `IPPROTO_SMC` stream sockets, bind/listen/connect/accept, exercise send/recv/poll/ioctl/shutdown/options, and inject registration failure in test kernels to verify cleanup. Check `/proc` or diag visibility through the SMC hash tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_inet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_inet.h -->
# sources/distributed-fs/ceph-client/net/smc/smc_inet.h

## Purpose
`smc_inet.h` declares the lifecycle hooks for registering SMC as `IPPROTO_SMC` in the inet protocol tables.

## Important APIs, Types, and Functions
The header exposes `smc_inet_init()` and `smc_inet_exit()`. It intentionally contains no state structures, keeping inet registration details private to `smc_inet.c`.

## Control Flow
SMC module initialization can call `smc_inet_init()` to publish IPv4 and optional IPv6 protocol-switch entries. Module exit calls `smc_inet_exit()` to unregister them in the reverse path.

## State and Persistence
The header owns no state. Registered protocol state lives in static objects in `smc_inet.c` and per-socket allocations in the networking stack.

## Dependencies and Integration Points
It is included by top-level SMC initialization code and implemented by `smc_inet.c`. It provides a narrow integration point so other SMC modules do not need inet registration internals.

## Risks
Because the header only declares lifecycle calls, risk is mostly ordering: callers must invoke init after dependencies such as common socket operations are ready, and exit before those operations are unavailable.

## Test Signals
Build coverage and module init/exit tests should confirm that callers can register and unregister `IPPROTO_SMC` cleanly in IPv4-only and IPv6-enabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_inet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_ism.c -->
# sources/distributed-fs/ceph-client/net/smc/smc_ism.c

## Purpose
`smc_ism.c` implements SMC-D support over ISM/DIBS devices. It registers as a DIBS client, discovers and orders SMC-D devices, manages VLAN IDs, registers/attaches/detaches DMBs, maps DMB indexes to SMC connections, handles ISM events and interrupts, provides SMC-D netlink device dumps, and signals peer shutdown/testlink events.

## Important APIs, Types, and Functions
Global state includes `smcd_dev_list`, `smc_ism_v2_capable`, and `smc_ism_v2_system_eid`. Public APIs include `smc_ism_cantalk()`, `smc_ism_set_conn()`, `smc_ism_unset_conn()`, `smc_ism_get_vlan()`, `smc_ism_put_vlan()`, `smc_ism_register_dmb()`, `smc_ism_unregister_dmb()`, `smc_ism_support_dmb_nocopy()`, `smc_ism_attach_dmb()`, `smc_ism_detach_dmb()`, `smc_ism_signal_shutdown()`, `smc_ism_get_system_eid()`, `smc_ism_get_chid()`, `smc_ism_is_v2_capable()`, `smc_ism_init()`, `smc_ism_exit()`, and `smcd_nl_get_device()`.

## Control Flow
`smc_ism_init()` resets v2 capability, creates a system EID, and registers `smc_dibs_client`. Device add allocates `struct smcd_dev`, creates a connection pointer table and ordered event workqueue, sets PNET ID, detects v2 capability through loopback or reserved VLAN support, and inserts the device in preference order. DMB registration fills a `dibs_dmb` with peer GID and VLAN, then stores returned token, index, CPU address, DMA address, and length in the buffer descriptor. IRQ handling looks up a connection by DMB number under a spinlock and schedules its RX tasklet. Device and software events are copied from IRQ context into event work, where peer shutdown triggers core link-group termination and testlink requests can be answered.

## State and Persistence
All state is transient: global device list, per-device VLAN refcount list, per-DMB connection table, event workqueue, link-group count, going-away flag, and v2 system EID. VLAN IDs are refcounted and added to hardware only for the first user, then removed on the last put.

## Dependencies and Integration Points
The file integrates DIBS/ISM device ops, SMC core termination and buffer descriptors, PNET lookup, generic netlink, PCI metadata helpers, VLAN constants, and SMC-D CDC receive tasklets. Core calls ISM helpers during SMC-D connection creation, buffer creation, no-copy attach, close, and module shutdown.

## Risks
DIBS callbacks can run in interrupt context, so allocation, queueing, and connection table access must remain IRQ-safe. VLAN reference handling must match link-group lifetime or hardware VLAN entries can leak or be removed too early. No-copy DMB attach creates a connection-owned "ghost" send buffer that must detach exactly once. Device unregister sets `going_away`, terminates groups, destroys the event queue, and frees connection arrays, so queued work must be drained by workqueue destruction.

## Test Signals
Test SMC-D connect/close with and without VLANs, DMB registration failure paths, loopback no-copy attach/detach, ISM device add/remove, peer shutdown events, IRQ-driven receive tasklet scheduling, v2 EID reporting, generic netlink SMCD device dumps, and unload while SMC-D groups are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_ism.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_ism.h -->
# sources/distributed-fs/ceph-client/net/smc/smc_ism.h

## Purpose
`smc_ism.h` defines the SMC-D device-list, VLAN, system-EID, DIBS-GID conversion, and helper API used by SMC-D core and diagnostics.

## Important APIs, Types, and Functions
The header defines `SMC_EMULATED_ISM_CHID_MASK`, `SMC_ISM_IDENT_MASK`, `struct smcd_dev_list`, `struct smc_ism_vlanid`, and `struct smc_ism_seid`. It declares the SMC-D device list and all ISM helpers implemented in `smc_ism.c`. Inline helpers include `smc_ism_write()`, `__smc_ism_is_emulated()`, `smc_ism_is_emulated()`, `smc_ism_is_loopback()`, `copy_to_smcdgid()`, and `copy_to_dibsgid()`.

## Control Flow
Callers use `smc_ism_cantalk()` during negotiation, `smc_ism_get_vlan()`/`put_vlan()` around VLAN-scoped link-group lifetime, `smc_ism_register_dmb()`/`unregister_dmb()` for RMB allocation, and `smc_ism_set_conn()`/`unset_conn()` for interrupt routing. Data transfer uses `smc_ism_write()` to call the DIBS `move_data` operation and normalize positive returns to 0.

## State and Persistence
The header describes transient device-list and VLAN-refcount state. Conversion helpers translate between SMC-D wire GID fields and DIBS UUIDs without storing data. Emulated and loopback checks are computed from DIBS fabric IDs.

## Dependencies and Integration Points
It depends on Linux UIO/types/mutex/DIBS APIs and local SMC structures. It is consumed by SMC core, diagnostics, netlink, and ISM implementation code. The conversion helpers are important for CLC negotiation, DMB registration, diagnostics, and event handling.

## Risks
Endian conversion for GIDs must stay consistent between CLC, diagnostics, and DIBS callbacks. Emulated ISM matching uses GID extension semantics that differ from native devices. `smc_ism_write()` assumes valid DIBS operations and maps nonnegative device returns to success, so callers cannot distinguish partial positive progress.

## Test Signals
Validate GID round trips, emulated and loopback CHID classification, DMB write behavior, VLAN refcount paths, v2 capability reporting, and compile coverage with different DIBS providers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_ism.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_llc.c -->
# sources/distributed-fs/ceph-client/net/smc/smc_llc.c

## Purpose
`smc_llc.c` implements SMC-R Link Layer Control protocol handling. It sends and receives LLC messages for confirm-link, add-link, delete-link, test-link, confirm-rkey, and delete-rkey flows, manages local and remote LLC flow serialization, coordinates multi-link failover and redundancy state, exchanges RMB rkeys for new links, and registers LLC receive handlers with the SMC WR layer.

## Important APIs, Types, and Functions
The file defines packed wire structures for all LLC message variants and `struct smc_llc_qentry`. Public functions include `smc_llc_send_confirm_link()`, `smc_llc_send_add_link()`, `smc_llc_send_delete_link()`, `smc_llc_srv_delete_link_local()`, `smc_llc_lgr_init()`, `smc_llc_lgr_clear()`, `smc_llc_link_init()`, `smc_llc_link_active()`, `smc_llc_link_clear()`, `smc_llc_do_confirm_rkey()`, `smc_llc_do_delete_rkey()`, `smc_llc_flow_initiate()`, `smc_llc_flow_stop()`, `smc_llc_wait()`, `smc_llc_cli_add_link()`, `smc_llc_srv_add_link()`, `smc_llc_add_link_local()`, `smc_llc_eval_conf_link()`, and `smc_llc_init()`.

## Control Flow
Incoming WR completions enter `smc_llc_rx_handler()`, which validates length and enqueues messages. Responses are matched immediately to the active local flow; requests are processed on `system_highpri_wq`. Add-link flows allocate an alternate link, initialize RDMA state, map and register existing buffers, exchange rkeys through continuation messages for v1 or in v2 extensions, perform confirm-link handshakes, and update link-group type to single, symmetric, or asymmetric. Delete-link flows switch connections away from a link, send or forward delete messages, clear links, and may terminate the group or trigger a new asym add-link. Rkey flows run as remote or local flows and update the core rtoken table. Test-link work periodically sends keepalives and schedules link-down on timeout.

## State and Persistence
LLC state is held inside `struct smc_link_group`: event queue, delayed event pointer, flow lock, local and remote flow structs, wait queues, configuration rwsem, add/delete/event work items, testlink interval, and termination reason. Per-link state includes testlink delayed work and completion. This is all transient and tied to link-group lifetime.

## Dependencies and Integration Points
LLC depends on RDMA WR transmit/receive slot management, SMC core link and buffer APIs, IB QP state transitions, PNET alternate RoCE discovery, CLC constants, and core rtoken helpers. It is initialized through `smc_llc_init()` by registering WR receive handlers for v1 and v2 LLC message types. Core calls LLC for link-group initialization, link activation/clear, rkey registration/deletion, add-link invitations, and link-delete-all on termination.

## Risks
This file has dense concurrency: tasklet-context receive handling, workqueue request handling, wait queues, delayed events, local and remote flows, and `llc_conf_mutex` must agree. Unexpected parallel add/delete messages can be delayed or dropped; mistakes can deadlock link reconfiguration or lose a protocol message. Packed wire structure lengths differ between v1 and v2, and v2 shared receive buffers require copying before interpretation. Rkey exchange must stay synchronized with buffer lists and link indexes. Test-link false positives can tear down healthy links if completions are delayed.

## Test Signals
Run SMC-R v1 and v2 with one and two RoCE paths, add-link and delete-link initiated by client and server, asymmetric-to-symmetric transitions, link failure under load, rkey confirm/delete for newly allocated and freed RMBs, LLC protocol violation injection, testlink timeout, short/invalid LLC message drops, and high connection counts during add-link rkey exchange. Lockdep and fault injection around WR slot allocation are valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_llc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_llc.h -->
# sources/distributed-fs/ceph-client/net/smc/smc_llc.h

## Purpose
`smc_llc.h` exposes the LLC protocol constants and public link-control API used by core SMC-R code.

## Important APIs, Types, and Functions
The header defines LLC response flags, wait intervals, `enum smc_llc_reqresp`, and `enum smc_llc_msg_type` for v1 and v2 message IDs. It provides `smc_link_downing()` plus inline helpers `smc_llc_usable_link()` and `smc_llc_set_termination_rsn()`. It declares transmit APIs, link-group and link lifecycle hooks, rkey operations, flow control helpers, add/delete link entry points, and `smc_llc_init()`.

## Control Flow
Core code uses `smc_llc_lgr_init()` when creating an SMC-R group, `smc_llc_link_init()` and `smc_llc_link_active()` around RDMA link setup, and `smc_llc_link_clear()` during teardown. Link loss paths use `smc_link_downing()` to atomically transition active links to inactive. Buffer code initiates `SMC_LLC_FLOW_RKEY` before confirm/delete rkey operations. Device and core failover paths use add/delete link helpers to reconfigure groups.

## State and Persistence
The header owns no state. It defines constants and function signatures for state stored in `struct smc_link_group` and `struct smc_link`.

## Dependencies and Integration Points
It includes `smc_wr.h` and relies on core types from `smc_core.h` through inclusion order in C files. It is the main contract between `smc_core.c` and `smc_llc.c`, and it defines reason codes shared across teardown paths.

## Risks
Message type and reason code constants must match the SMC protocol. `smc_link_downing()` only transitions from `SMC_LNK_ACTIVE` to `SMC_LNK_INACTIVE`; callers using it on activating links will not act. `smc_llc_usable_link()` returns the first usable link, not necessarily sendable, so send paths must still hold and validate WR availability.

## Test Signals
Compile-time coverage should catch missing prototypes. Runtime signals include correct DELETE LINK reason propagation, no duplicate link-down processing, successful rkey flow initiation, and expected add/delete behavior when multiple links are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_llc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_netlink.c -->
# sources/distributed-fs/ceph-client/net/smc/smc_netlink.c

## Purpose
`smc_netlink.c` defines and registers the SMC generic netlink family. It maps SMC netlink commands to dump and administrative handlers implemented across core, IB, ISM, CLC, and stats modules.

## Important APIs, Types, and Functions
The file defines `smc_gen_ueid_policy`, `smc_gen_nl_ops[]`, `smc_gen_nl_policy`, global `smc_gen_nl_family`, and lifecycle functions `smc_nl_init()` and `smc_nl_exit()`. Operations include system info, SMC-R link groups, SMC-R links, SMC-D link groups, SMC-D devices, SMC-R devices, stats, fallback stats, UEID dump/add/remove/flush, SEID dump/enable/disable, and handshake-limitation dump/enable/disable.

## Control Flow
`smc_nl_init()` registers `smc_gen_nl_family`. User-space generic netlink commands dispatch through `smc_gen_nl_ops[]`; unprivileged dumps call `dumpit` functions, while mutating UEID/SEID/handshake-limitation operations require `GENL_ADMIN_PERM`. `smc_nl_exit()` unregisters the family.

## State and Persistence
This file stores static registration metadata and a UEID string policy. The data returned or mutated by handlers lives in other modules. Generic netlink registration is runtime kernel state only.

## Dependencies and Integration Points
It includes Linux module/list/ctype/mutex/if/SMC APIs and local core, ISM, IB, CLC, stats, and netlink headers. `smc_gen_nl_family` is used by dump helpers in `smc_core.c`, `smc_ib.c`, and `smc_ism.c` when constructing messages.

## Risks
Command permissions must remain correct because several operations mutate negotiation identity or limitations. `maxattr` is intentionally small with a reject policy for command-level attrs, while per-operation policies are attached where needed; incorrect policy updates can reject valid user-space requests or accept malformed ones. Adding new commands requires updating `resv_start_op` and policy coverage.

## Test Signals
Use `genl` or SMC tooling to dump every command, attempt admin-only operations as unprivileged and privileged users, fuzz attrs for UEID commands, verify netns-aware dumps, and unload/reload the module without family registration leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_netlink.h -->
# sources/distributed-fs/ceph-client/net/smc/smc_netlink.h

## Purpose
`smc_netlink.h` declares the SMC generic netlink family, shared policies, dump cursor context, and registration lifecycle.

## Important APIs, Types, and Functions
It exposes `smc_gen_nl_family`, `smc_gen_ueid_policy[]`, `struct smc_nl_dmp_ctx`, `smc_nl_dmp_ctx()`, `smc_nl_init()`, and `smc_nl_exit()`. `struct smc_nl_dmp_ctx` has three integer positions for multi-dimensional dump cursors.

## Control Flow
Dump handlers cast `netlink_callback->ctx` through `smc_nl_dmp_ctx()` and use the position array to resume multi-part dumps. Module init and exit register and unregister the generic netlink family through the declared lifecycle calls.

## State and Persistence
The header owns no runtime state. It defines the shape of callback cursor memory used during netlink dump operations and references static family/policy objects in `smc_netlink.c`.

## Dependencies and Integration Points
It depends on netlink and generic netlink headers. It is included by core, IB, ISM, and stats/CLC code that either fills generic netlink messages or registers command handlers.

## Risks
All dump handlers sharing `pos[3]` must agree on index meaning; misuse can skip or repeat objects across multipart dumps. The cast from callback context assumes the context is large enough for `struct smc_nl_dmp_ctx`, matching generic netlink callback storage expectations.

## Test Signals
Multipart dumps with small skb sizes should resume correctly for device lists, link-group lists, and nested link dumps. Build tests should catch family/policy declaration drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_netns.h -->
# sources/distributed-fs/ceph-client/net/smc/smc_netns.h

## Purpose
`smc_netns.h` defines SMC per-network-namespace private data. It lets the SMC subsystem keep namespace-local PNET configuration and network-device PNET ID tracking.

## Important APIs, Types, and Functions
The header declares external `smc_net_id` and defines `struct smc_net` with `struct smc_pnettable pnettable` and `struct smc_pnetids_ndev pnetids_ndev`.

## Control Flow
The header has no executable flow. Net namespace initialization code elsewhere allocates or looks up `struct smc_net` by `smc_net_id`, then PNET and device-notifier code uses the embedded tables for namespace-local SMC path selection.

## State and Persistence
State is per-netns and in-memory. It persists for the lifetime of the network namespace and is destroyed with that namespace. It does not write durable data.

## Dependencies and Integration Points
It includes `smc_pnet.h` and is consumed by SMC namespace, PNET, and device handling code. The state influences SMC-R and SMC-D device selection through PNET IDs.

## Risks
Namespace isolation depends on all PNET lookups using the correct `struct net` and `smc_net_id`. Cross-namespace leakage would cause wrong device selection or expose configuration. Cleanup ordering must ensure device notifier state is gone before namespace memory is freed.

## Test Signals
Create multiple network namespaces with different PNET tables and devices, verify SMC path selection remains isolated, and tear namespaces down under SMC traffic while checking for use-after-free reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_netns.h -->
