# subset-b-003906 RDMA InfiniBand core CMA research

This grouped report covers the requested RDMA connection-manager, configfs, trace, counter, and CQ core files. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cma.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/cma.c

## Purpose

`cma.c` implements the kernel RDMA Connection Manager Agent. It translates the public `rdma_cm_id` API into device selection, address and route resolution, port binding, listen/connect/accept/reject/disconnect operations, QP initialization, multicast join/leave, netdevice change notifications, and IB/iWARP CM event delivery. It is the bridge between ULPs using `rdma_cm.h` and the lower RDMA address, SA, IB CM, iWARP CM, GID cache, net namespace, neighbour, and netdevice subsystems.

## Important APIs, types, and functions

The key internal objects are `struct cma_device`, `struct cma_pernet`, `struct rdma_bind_list`, `struct cma_work`, `struct cma_multicast`, `struct cma_hdr`, and `struct cma_req_info`. The private CM identifier state lives in `struct rdma_id_private` from `cma_priv.h`, while per-net port-space xarrays live in `struct cma_pernet`.

Important exported APIs include `__rdma_create_kernel_id()`, `rdma_create_user_id()`, `rdma_destroy_id()`, `rdma_create_qp()`, `rdma_destroy_qp()`, `rdma_init_qp_attr()`, `rdma_bind_addr()`, `rdma_resolve_addr()`, `rdma_resolve_route()`, `rdma_set_ib_path()`, `rdma_listen()`, `rdma_connect()`, `rdma_connect_locked()`, `rdma_accept()`, `rdma_reject()`, `rdma_disconnect()`, `rdma_join_multicast()`, `rdma_leave_multicast()`, `rdma_resolve_ib_service()`, `rdma_read_gids()`, and option setters for service type, ACK timeout, minimum RNR timer, address reuse, AF-only matching, and node-type restriction.

Important internal paths are `cma_acquire_dev_by_src_ip()`, `cma_validate_port()`, `cma_ib_acquire_dev()`, `cma_iw_acquire_dev()`, `cma_resolve_ib_dev()`, `cma_ib_id_from_event()`, `cma_find_listener()`, `cma_work_handler()`, `addr_handler()`, `cma_query_handler()`, `cma_ib_handler()`, `cma_iw_handler()`, `cma_ib_req_handler()`, `iw_conn_req_handler()`, `cma_process_remove()`, and the `cma_add_one()`/`cma_remove_one()` RDMA client callbacks. The module also exports configfs-facing helpers for default RoCE GID type and TOS.

## Control flow

Module initialization allocates an ordered `rdma_cm` workqueue, registers per-net xarray state, registers with the SA client, netdevice notifier, netevent notifier, RDMA device client, and finally configfs. When an RDMA device appears, `cma_add_one()` creates a `cma_device`, initializes per-port default RoCE GID type and TOS, attaches it to `dev_list`, and spawns per-device listeners for any wildcard listeners on `listen_any_list`.

A typical active connection starts with ID creation in `RDMA_CM_IDLE`, optional binding through `rdma_bind_addr()`, address resolution through `rdma_resolve_addr()`, route resolution through `rdma_resolve_route()`, and connection through `rdma_connect()` or `rdma_connect_locked()`. Address resolution either binds loopback, resolves AF_IB directly, or calls `rdma_resolve_ip()` and later `addr_handler()`. Device acquisition validates GID attributes, net namespace access, port protocol, bound netdevice, and VLAN/RoCE/iWARP details before attaching a `cma_device`. Route resolution uses SA path records for IB, constructs path records locally for RoCE, and queues immediate completion for iWARP. Connection uses IB CM REQ/SIDR or iWARP connect, formatting `cma_hdr` private data for IP-based IB CM requests.

A passive path binds a port in a per-net xarray, transitions to `RDMA_CM_LISTEN`, and either creates a transport-specific listener on a bound device or creates internal per-device IDs for wildcard listeners. IB CM and iWARP request callbacks create child IDs, copy address and path information, acquire the matched device/port/GID, deliver `RDMA_CM_EVENT_CONNECT_REQUEST`, and then let the consumer accept or reject. Established, rejected, disconnected, unreachable, and timewait events are translated from lower CM events and delivered under `handler_mutex`.

Asynchronous transitions are serialized through `cma_wq` and `cma_work_handler()`, which performs guarded state transitions before invoking the consumer event handler. Device removal sets IDs to `RDMA_CM_DEVICE_REMOVAL`, sends a removal event, cancels outstanding address, route, or listen operations, and waits for reference completion. Netdevice bonding failover and neighbour updates queue address-change or unreachable events for affected IDs.

## State and persistence

State is in memory only. `rdma_id_private.state` is the central FSM, protected by both `handler_mutex` and a spinlock for selected transitions. ID lifetime uses `refcount_t` plus `completion`, and device lifetime uses `cma_device.refcount` plus `completion`. Per-net port bindings are stored in xarrays keyed by RDMA port space and service number. Device attachments are tracked in `cma_device->id_list`; wildcard listens are tracked in `listen_any_list`; RoCE neighbour monitoring uses the `id_table` red-black tree keyed by bound ifindex and destination IP. Route data, service records, path records, multicast state, GID attrs, and AH attributes are dynamically allocated and released on destroy or leave.

No disk persistence is performed. Configfs changes to default RoCE mode/TOS are runtime-only fields in `cma_device`. Hardware and network state enter through GID cache lookups, SA queries, neighbour updates, netdevice state, and lower CM IDs.

## Dependencies and integration points

The file depends on Linux net namespaces, routing, IPv4/IPv6, VLAN, neighbour, netdevice notifier, workqueue, xarray, rbtree, random, mutex/spinlock/refcount/completion APIs, and RDMA core headers. It integrates with `rdma_addr` for address resolution, `ib_sa` for path/service/multicast records, `ib_cm` for IB CM and SIDR, `iw_cm` for iWARP, GID cache helpers from `core_priv.h`, resource tracking, configfs helpers in `cma_configfs.c`, and tracepoints in `cma_trace.h`. External consumers are kernel RDMA ULPs and user CM plumbing that allocate IDs, receive CM events, and call exported connection APIs.

## Risks

The main risk is concurrency. State changes cross interrupt, workqueue, notifier, CM callback, consumer callback, and destroy contexts, so `handler_mutex`, spinlocks, reference counting, and completion waits must stay paired. Device removal is especially sensitive because callbacks may destroy IDs while removal is in progress. Port binding correctness depends on per-net xarray locking, `reuseaddr`, AF-only semantics, wildcard address matching, service-ID mapping for AF_IB, and privileged-port checks. RoCE handling is sensitive to GID type selection, VLAN and traffic-class mapping, bound netdevice lifetime, neighbour updates, IPv6 link-local scope, and net namespace migration. Private-data header sizing uses offset arithmetic and must not overflow. Multicast join/leave must pair SA multicast, RoCE IGMP, queued work, and AH attribute destruction correctly.

Subtle bugs can also come from one-based versus `rdma_start_port()` port indexing, GID attr reference leaks, stale `dev_put()` calls, address-family mismatches, event-handler return semantics that destroy IDs, or lower CM IDs left attached after send failures.

## Test signals

Useful signals are clean RDMA CM module load/unload, configfs registration, RDMA device add/remove with no leaks or deadlocks, and resource tracking showing expected CM IDs. Functional tests should cover active/passive RC over IB, RoCE, and iWARP; UD SIDR; wildcard listen across multiple devices; bind/reuse/AF-only combinations; IPv4, IPv6, IPv6 link-local, AF_IB, loopback, and specific-source binds; route failure and timeout paths; consumer rejection private data; ECE connect/accept; QP auto transitions; multicast join/leave for IB and RoCE; bonding failover and neighbour MAC-change events; net namespace teardown; and device hot removal during address, route, connect, listen, and multicast operations. Kernel tracepoints under `rdma_cma` and debug messages should show coherent transitions with no WARNs, leaked refs, or stuck work items.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cma_configfs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/cma_configfs.c

## Purpose

`cma_configfs.c` exposes runtime RDMA CM policy knobs through configfs under the `rdma_cm` subsystem. Users create a configfs group named after an RDMA device, and the file presents per-port attributes for the default RoCE GID mode and default RoCE TOS used by CMA when building RoCE paths.

## Important APIs, types, and functions

Local types are `struct cma_dev_group`, representing a configfs device group with a `ports` subgroup, and `struct cma_dev_port_group`, representing one port directory and its parent device group. `filter_by_name()` matches an `ib_device` by `dev_name()`. `cma_configfs_params_get()` resolves the configfs item to a live `cma_device` using `cma_enum_devices_by_ibdev()` and returns the port group; `cma_configfs_params_put()` drops the device reference.

Attributes are `default_roce_mode` and `default_roce_tos`. The show/store callbacks call `cma_get_default_gid_type()`, `cma_set_default_gid_type()`, `cma_get_default_roce_tos()`, and `cma_set_default_roce_tos()`. Group lifecycle is handled by `make_cma_dev()`, `drop_cma_dev()`, `make_cma_ports()`, `release_cma_dev()`, and `release_cma_ports_group()`. Module hooks are `cma_configfs_init()` and `cma_configfs_exit()`.

## Control flow

Initialization builds and registers the `rdma_cm` configfs subsystem. When a user creates a child group named after a registered RDMA device, `make_cma_dev()` looks up the matching CMA device, allocates a `cma_dev_group`, creates a default `ports` subgroup, and creates one default child group for each physical port. Reads of `default_roce_mode` fetch the current CMA default GID type and stringify it through the GID cache helper. Writes parse a GID type string and ask CMA to validate and install it. Reads and writes of `default_roce_tos` fetch or parse an 8-bit value and update the CMA device.

On group removal, `drop_cma_dev()` removes default child groups and drops the config item, eventually freeing the port array and device group in release callbacks.

## State and persistence

The configfs tree contains only runtime objects. The persistent CMA state being manipulated is in the live `cma_device` arrays allocated by `cma.c`: `default_gid_type[]` and `default_roce_tos[]`. Settings disappear when the RDMA device is removed or the module unloads. The configfs group stores the device name string and generated per-port group objects, not a permanent device pointer, so each attribute access re-resolves and refcounts the current device.

## Dependencies and integration points

This file depends on Linux configfs, RDMA verbs, RDMA CM headers, `core_priv.h` for GID type parsing/stringification, and `cma_priv.h` for CMA device accessors. It is conditionally called from `cma.c` when `CONFIG_INFINIBAND_ADDR_TRANS_CONFIGFS` is enabled. The exported user interface is configfs, usually mounted by userspace management tools that tune RoCE defaults before connections are made.

## Risks

Device lookup is name-based, so users can only configure devices that are currently registered and whose names match exactly. Per-port directories are generated from `phys_port_cnt` and use one-based numbering; any future device with a different start port model would need careful review against the CMA accessor validation. Attribute writes race logically with new connection setup, because they update defaults without a separate policy lock; existing IDs keep their selected GID type while future route resolution uses the new value. The port release callback frees only the port array and depends on configfs release ordering.

## Test signals

Validation should mount configfs, create `rdma_cm/<device>`, observe `ports/<n>/default_roce_mode` and `default_roce_tos`, read valid defaults, write supported RoCE GID modes, reject unsupported or malformed modes, accept `u8` TOS values, reject out-of-range TOS strings, and remove groups cleanly. Device hot removal while configfs entries exist should make later attribute operations fail with `-ENODEV` rather than dereferencing stale state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cma_configfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cma_priv.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/cma_priv.h

## Purpose

`cma_priv.h` defines the private RDMA CMA state machine and per-ID state used internally by `cma.c` and related CMA support files. It also declares the CMA configfs hooks and the small set of CMA device accessors needed by `cma_configfs.c`.

## Important APIs, types, and functions

`enum rdma_cm_state` enumerates the internal lifecycle states: idle, address query/resolved/bound, route query/resolved, connect, disconnect, listen, device removal, destroying, and IB service address-info query/resolved. `struct rdma_id_private` embeds the public `struct rdma_cm_id` and adds bind-list membership, device/listen list nodes, multicast list, internal child-ID marker, state, node-type restriction, spinlock, QP mutex, handler mutex, completion/refcount lifetime management, backlog, SA query state, transport CM ID union, sequence number, QKey, QP number, options, SRQ/TOS/timer/reuse/AF-only flags, selected GID type, resource tracking entry, and ECE data.

The header conditionally declares or stubs `cma_configfs_init()` and `cma_configfs_exit()`. It also declares `cma_dev_get()`, `cma_dev_put()`, `cma_enum_devices_by_ibdev()`, default RoCE GID type/TOS getters and setters, and `cma_get_ib_dev()`.

## Control flow

The header itself has no runtime flow, but it is the contract for `cma.c` transitions. New IDs start at `RDMA_CM_IDLE`; bind, address, route, listen, connect, and destroy paths move through the enum with guarded compare-exchange helpers. `handler_mutex` serializes callbacks and destroy, `qp_mutex` serializes QP-related options and pointer changes, and `lock` protects state fields that can be touched outside handler context. List-node unions let the same ID storage represent either device-list membership or wildcard-listen membership and either listen-list head or child-list entry depending on ID role.

## State and persistence

All fields are in-memory runtime state. The private ID owns references to net namespaces, CMA devices, lower CM IDs, SA queries, path/service records, multicast records, and resource-tracker entries through code in `cma.c`. There is no disk persistence. The configfs stubs make CMA buildable without configfs support while preserving the same initialization call sites.

## Dependencies and integration points

The declarations depend on RDMA CM, IB verbs/GID types, SA query, resource tracking, and configfs Kconfig. `cma.c` is the main user, `cma_configfs.c` uses the device accessors, and `cma_trace.h` reads fields such as resource ID, addresses, TOS, and QP number. External drivers should not consume this header for data-path behavior; it is an RDMA core internal contract.

## Risks

Because `rdma_id_private` is shared across many asynchronous contexts, field ownership must remain clear. Reusing list-head storage through unions saves memory but makes role transitions fragile: an ID must not be placed on incompatible lists at the same time. Adding states requires auditing every `cma_comp_exch()` and event handler. Adding flags or timers requires correct locking under `qp_mutex`, the spinlock, or `handler_mutex`. The configfs stubs must stay ABI-compatible with the real hooks so `cma.c` cleanup remains simple.

## Test signals

Build coverage with configfs both enabled and disabled validates the conditional declarations. Runtime signals are mostly exercised through `cma.c`: legal state transitions succeed, invalid API ordering returns `-EINVAL`, destroy waits for outstanding refs, child listen IDs and device IDs leave all lists, and tracepoints show coherent private-state values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cma_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cma_trace.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/cma_trace.c

## Purpose

`cma_trace.c` is the tracepoint instantiation unit for RDMA CMA trace events. It defines `CREATE_TRACE_POINTS`, includes the RDMA CM and IB CM type declarations plus `cma_priv.h`, then includes `cma_trace.h` so the tracepoint definitions generate storage and registration code exactly once.

## Important APIs, types, and functions

There are no runtime functions in this file. Its important interface is the build-time tracepoint pattern: `CREATE_TRACE_POINTS` must be defined before including `cma_trace.h`. The included private and public RDMA headers provide the type information used by trace event prototypes and field extraction.

## Control flow

Control flow is compile/link-time. Other CMA translation units include `cma_trace.h` without `CREATE_TRACE_POINTS` to get tracepoint declarations and inline call sites. This file includes the same header with `CREATE_TRACE_POINTS` so the kernel trace subsystem receives the actual tracepoint definitions for `rdma_cma`.

## State and persistence

The file does not maintain per-object state. Generated tracepoint metadata is registered as part of the kernel/module image and used by ftrace/perf/tracefs when enabled. Trace buffers and enabled/disabled state are owned by the kernel tracing subsystem, not this file.

## Dependencies and integration points

It depends on tracepoint infrastructure, `rdma/rdma_cm.h`, `rdma/ib_cm.h`, `cma_priv.h`, and `cma_trace.h`. It integrates with all `trace_cm_*` call sites in `cma.c`. Removing or duplicating this file would either break tracepoint linkage or create duplicate definitions.

## Risks

The main risk is include-order correctness. `CREATE_TRACE_POINTS` must appear before `cma_trace.h`, and the needed RDMA types must be visible before event definitions are expanded. This file should remain minimal; adding unrelated logic can cause tracepoint compilation dependencies or duplicate symbol issues.

## Test signals

Build success with tracing enabled is the primary signal. Runtime validation is that tracefs lists the `rdma_cma` events defined in `cma_trace.h`, and enabling them captures CMA attach, QP, event, request, and device add/remove activity from `cma.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cma_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cma_trace.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/cma_trace.h

## Purpose

`cma_trace.h` defines the `rdma_cma` trace event set used to observe RDMA CMA state-machine activity, QP creation/destruction, lower CM events, consumer callbacks, and RDMA device add/remove notifications. It gives operators and developers structured visibility into `cma.c` without changing CM behavior.

## Important APIs, types, and functions

The file defines event classes `cma_fsm_class`, `cma_qp_class`, and `cma_client_class`, plus concrete events `cm_send_rtu`, `cm_send_rej`, `cm_prepare_mra`, `cm_send_sidr_req`, `cm_send_sidr_rep`, `cm_disconnect`, `cm_sent_drep`, `cm_sent_dreq`, `cm_id_destroy`, `cm_id_attach`, `cm_send_req`, `cm_send_rep`, `cm_qp_destroy`, `cm_qp_create`, `cm_req_handler`, `cm_event_handler`, `cm_event_done`, `cm_add_one`, and `cm_remove_one`.

Most events record the CMA resource ID, source and destination socket addresses, TOS, and sometimes QP number, PD ID, WR capacities, return code, lower IB CM event, RDMA CM event, or device name. The `IB_QP_TYPE_LIST` helpers register QP type enum values and print them symbolically through `rdma_show_qp_type()`.

## Control flow

At compile time the trace macros emit declarations or definitions depending on whether `CREATE_TRACE_POINTS` is set. At runtime, `cma.c` calls `trace_cm_*` helpers at key transitions: attach, QP create/destroy, send REQ/REP/RTU/REJ/SIDR, disconnect, request handler entry, consumer handler entry/exit, ID destroy, and device client add/remove. The tracepoint fast paths are cheap when disabled and write structured records when enabled by ftrace/perf.

## State and persistence

Trace events copy selected fields into trace buffers at event time. They do not own CMA objects or persist state beyond kernel trace storage. Address fields are copied as `sockaddr_in6`-sized byte arrays so `%pISpc` can print IPv4/IPv6 socket addresses consistently. The data represents a point-in-time snapshot and may not reflect later ID changes.

## Dependencies and integration points

The header depends on Linux tracepoint APIs, `trace/misc/rdma.h` helpers such as RDMA/IB event stringification, RDMA verb QP type definitions, and `struct rdma_id_private` fields. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` are set so `trace/define_trace.h` can find the header from `cma_trace.c`. The primary integration point is `cma.c`; trace consumers are tracefs, perf, and debugging scripts.

## Risks

Tracepoint field layouts become part of tooling expectations, so renaming events or changing fields can break observability. The code assumes source and destination address storage can be meaningfully copied into a `sockaddr_in6`-sized buffer; unusual AF_IB rendering may be less informative than IP rendering. Event prototypes expose private CMA fields, so structure changes must update trace assignments. Tracepoint headers are sensitive to include guards, `TRACE_HEADER_MULTI_READ`, and `TRACE_INCLUDE_*` settings.

## Test signals

Builds with `CONFIG_TRACING` should compile without duplicate definitions. Runtime tests should enable `events/rdma_cma/*`, perform RDMA CM connect/listen/multicast/device add-remove operations, and verify event records contain expected CM IDs, addresses, QP types, statuses, consumer return codes, and device names. `perf list` or tracefs event enumeration should show the `rdma_cma` group.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cma_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/core_priv.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/core_priv.h

## Purpose

`core_priv.h` is a central internal declaration header for RDMA core. It publishes private cross-file contracts for device registration, net namespace metadata, RoCE netdevice/GID management, netlink, address resolution, MAD/SA initialization, security hooks, cgroup charging, QP/CQ helpers, hardware stats, sysfs/client groups, user mmap tracking, and selected CMA dependencies.

## Important APIs, types, and functions

Important local types include `struct pkey_index_qp_list`, `struct rdma_dev_net`, `struct ib_client_nl_info`, `enum ib_cache_gid_default_mode`, and `struct rdma_umap_priv`. The header declares core globals such as `ib_dev_attr_group`, `ib_devices_shared_netns`, and `rdma_dev_net_id`, plus `rdma_net_to_dev_net()`.

Major declaration groups cover device operations (`ib_device_rename()`, `ib_device_set_dim()`, `ib_device_get_by_index()`), RoCE netdevice enumeration and GID updates, GID cache operations and GID type string parsing, setup/cleanup for cache/MAD/SA/address/netlink subsystems, RDMA cgroup charging stubs or real hooks, InfiniBand security stubs or real hooks, netlink resolve handlers, address L2 helpers, hardware stats setup/release, compatibility device toggling, per-port client sysfs groups, net namespace moves, user mmap private initialization, CQ pool cleanup, and privileged QKey policy.

## Control flow

The header itself is declarative. Runtime flow appears in the C files that include it: initialization code calls the `*_init()` declarations, device registration paths call cache/counter/sysfs/security setup, netlink calls the `nldev` and resolve handlers, CMA calls GID and RoCE helpers, and verbs/CQ code calls QP/CQ/cgroup/security helpers. Conditional compilation provides no-op cgroup and security functions when those kernel features are disabled, keeping call sites simple.

## State and persistence

State represented by this header is runtime kernel state: per-net RDMA metadata, per-port P_Key-to-QP lists, GID cache contents, cgroup charges, security caches, hardware stats, client sysfs groups, mmap tracking entries, and CQ pools. There is no disk persistence. Some state is tied to `struct net`, some to `struct ib_device` and per-port data, and some to resource tracking objects.

## Dependencies and integration points

The header depends on Linux list/spinlock/cgroup/net namespace APIs, RDMA verbs, OPA addressing, MAD internals, resource tracking, and local `mad_priv.h`/`restrack.h`. It is consumed broadly across `drivers/infiniband/core`, including CMA, counters, CQ, device registration, cache, sysfs, netlink, address resolution, MAD, SA, verbs, and security code. Because it is private, it coordinates internal implementation without exposing these contracts to external ULPs.

## Risks

This header has high blast radius. Changing declarations, inline stubs, or shared structs can break many RDMA core modules. Conditional stubs must preserve semantics closely enough that call sites do not need feature-specific branching. Net namespace helpers and global IDs must match registration lifetime. GID cache declarations are used by RoCE and CMA path selection, so type parsing, default GID updates, and netdevice association mistakes can break connection setup. Security and cgroup stubs must not accidentally bypass required enforcement when configs are enabled.

## Test signals

Primary signals are full RDMA core builds across configurations with and without `CONFIG_CGROUP_RDMA`, `CONFIG_SECURITY_INFINIBAND`, IPv6, RoCE, and configfs. Runtime validation should include RDMA device registration/unregistration, net namespace moves, netlink enumeration and resolve responses, GID cache updates on netdevice changes, MAD/SA initialization, security policy enforcement where configured, cgroup charging, CQ pool cleanup during device teardown, and sysfs hardware-stat exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/core_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/counters.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/counters.c

## Purpose

`counters.c` implements RDMA core counter management for per-port hardware statistics and QP-bound counters. It supports automatic counter allocation/binding based on QP type and process ID, manual netlink-driven counter allocation/binding/unbinding by QP number and counter ID, optional hardware stat enable/disable, aggregation of live and historical stats, and per-device counter initialization/release.

## Important APIs, types, and functions

The important public/internal entry points are `rdma_counter_set_auto_mode()`, `rdma_counter_modify()`, `rdma_counter_bind_qp_auto()`, `rdma_counter_unbind_qp()`, `rdma_counter_query_stats()`, `rdma_counter_get_hwstat_value()`, `rdma_counter_bind_qpn()`, `rdma_counter_bind_qpn_alloc()`, `rdma_counter_unbind_qpn()`, `rdma_counter_get_mode()`, `rdma_counter_init()`, and `rdma_counter_release()`.

Key helpers include `__counter_set_mode()`, `alloc_and_bind()`, `__rdma_counter_bind_qp()`, `__rdma_counter_unbind_qp()`, `rdma_get_counter_auto_mode()`, `auto_mode_match()`, `counter_history_stat_update()`, `counter_release()`, `rdma_counter_get_qp()`, and `rdma_get_counter_by_id()`. The logic uses `struct rdma_port_counter`, `struct rdma_counter`, `struct rdma_hw_stats`, `struct ib_qp`, resource-tracker roots, xarrays, krefs, and driver counter ops.

## Control flow

Device setup calls `rdma_counter_init()` for each port, initializes port-counter mode and lock, and optionally allocates persistent historical hardware stats through `alloc_hw_port_stats`. Userspace can switch a port into auto mode with a supported mask. In auto mode, QP creation/modification paths call `rdma_counter_bind_qp_auto()`: tracked user QPs either reuse an existing matching counter or allocate a new counter and bind it through the driver. In manual mode, netlink can allocate a counter and bind it to a QP or bind an existing counter to a QP by ID.

Counter allocation creates a driver object, initializes resource tracking, allocates driver stats, updates per-port mode/count, initializes a kref and mutex, calls the device `counter_bind_qp` op, and adds the resource to restrack. Unbind calls the driver unbind op and drops the kref; final release snapshots stats into historical `hstats`, calls driver deallocation, deletes restrack, frees stats, and frees the counter. Query paths call driver `counter_update_stats` under the counter lock. Hardware-stat reads sum live counters plus historical stats from counters that were already freed.

## State and persistence

All state is runtime. Per-port state tracks mode, mask, bind operation count flag, number of counters, lock, and historical stats. Each `rdma_counter` stores device, port, mode, mask parameters, stats, resource tracking, kref, and lock. `qp->counter` is owned by driver bind/unbind behavior and validates whether a QP is already attached. Historical stats preserve values from released counters in memory so sysfs/netlink reads can include past QP activity until device teardown.

## Dependencies and integration points

The file depends on RDMA verbs, RDMA counter UAPI definitions, core private hardware-stat access, restrack, xarray iteration, netlink extack messages, and driver ops: `counter_alloc_stats`, `counter_init`, `counter_bind_qp`, `counter_unbind_qp`, `counter_update_stats`, `counter_dealloc`, `modify_hw_stat`, and `alloc_hw_port_stats`. Integration points include verbs QP setup/destruction, nldev netlink counter commands, sysfs hardware-stat reads, and device registration/release.

## Risks

Mode transitions are sensitive: auto mode rejects unsupported masks and cannot be enabled while counters are bound, while manual mode must fall back to none after the last counter is freed. Kref and restrack interactions must prevent use-after-free during xarray iteration and netlink operations. Manual binding must reject cross-device, cross-port, kernel/user resource mismatches, wrong counter IDs, and raw packet QPs without device raw capability. Stats aggregation can race with live counter updates, so each counter query must hold the counter lock and restrack refs. The failure path in `rdma_counter_init()` should be reviewed carefully because cleanup loops must free the intended per-port hstats.

## Test signals

Tests should cover devices with and without counter ops, auto mode by QP type and PID, automatic counter reuse, manual allocate/bind/unbind, binding errors for wrong QP/counter/port/device/mode, optional stat enable/disable through `rdma_counter_modify()`, counter stats query, historical stat aggregation after QP destroy, netlink extack on busy auto-mode changes, device teardown with live and freed counters, and concurrent QP creation/destruction while netlink enumerates counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/counters.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/cq.c

## Purpose

`cq.c` implements kernel RDMA completion queue allocation, polling, notification, shared CQ pooling, and optional RDMA DIM interrupt moderation. It provides higher-level CQ helpers for in-kernel users that process `wr_cqe` callbacks in direct, softirq, bound workqueue, or unbound workqueue contexts.

## Important APIs, types, and functions

Exported entry points are `ib_process_cq_direct()`, `__ib_alloc_cq()`, `__ib_alloc_cq_any()`, `ib_free_cq()`, `ib_cq_pool_get()`, and `ib_cq_pool_put()`. `ib_cq_pool_cleanup()` is declared in `core_priv.h` for device teardown.

Important helpers are `__poll_cq()`, `__ib_process_cq()`, `ib_poll_handler()`, `ib_cq_completion_softirq()`, `ib_cq_poll_work()`, `ib_cq_completion_workqueue()`, `ib_cq_completion_direct()`, `rdma_dim_init()`, `rdma_dim_destroy()`, `ib_cq_rdma_dim_work()`, and `ib_alloc_cqs()`. The file uses `struct ib_cq`, `struct ib_wc`, `struct ib_cqe`, `struct irq_poll`, `struct dim`, device CQ ops, trace events from `rdma_core`, and global RDMA completion workqueues.

## Control flow

`__ib_alloc_cq()` validates the requested CQE count, allocates a driver CQ object and polling WC buffer, creates resource-tracker state, calls the driver `create_cq` op, optionally initializes DIM, then installs a completion handler based on polling context. Direct CQs warn on unsolicited completion and must be polled by the caller. Softirq CQs initialize `irq_poll`, request notification, and schedule polling from the completion handler. Workqueue CQs initialize work and queue polling on either `ib_comp_wq` or `ib_comp_unbound_wq`.

Polling uses `__ib_process_cq()` to call `ib_poll_cq()` in batches, invoke each `wr_cqe->done()` callback, count completions, and stop on budget or short poll. Softirq and workqueue pollers re-arm notifications with `IB_CQ_NEXT_COMP | IB_CQ_REPORT_MISSED_EVENTS`; if the device reports missed events or the workqueue budget is exhausted, they reschedule themselves. DIM samples completion counts and schedules `modify_cq` work to change moderation profile when enabled.

`ib_free_cq()` refuses to free CQs with users or pooled CQEs, runs optional pre-destroy, disables polling context, destroys DIM, calls driver post-destroy or destroy, removes restrack, and frees buffers. Shared CQ pooling finds a CQ with matching completion vector and enough unused CQEs, or allocates one CQ per vector/CPU into a per-device pool. `ib_cq_pool_put()` returns the reserved CQE count.

## State and persistence

State is runtime only. Each CQ tracks poll context, completion vector, WC batch buffer, optional DIM state, work/irq-poll objects, resource-tracker entry, use count, shared-pool flag, and `cqe_used` reservations for pooled CQs. Device-level state includes `cq_pools[]` and `cq_pools_lock`. There is no disk persistence; CQ state is destroyed on CQ free or device teardown.

## Dependencies and integration points

The file depends on RDMA verbs, device CQ ops (`create_cq`, `destroy_cq`, `pre_destroy_cq`, `post_destroy_cq`, `modify_cq`), resource tracking, Linux workqueues, irq_poll, DIM, online CPU counts, and RDMA core trace events. It integrates with kernel ULPs allocating CQs, verbs code that directly polls CQs, device cleanup through `ib_cq_pool_cleanup()`, and drivers that support CQ moderation.

## Risks

The main risks are concurrency and accounting. A CQ must not be freed while usecnt or pooled CQE reservations remain. Completion rearming must handle missed events or completions can stall. Direct polling on non-direct CQs can race with automatic polling. Workqueue budget rescheduling must avoid livelock while still draining busy CQs. Shared CQ allocation uses global/static vector counters and per-device pool locks; incorrect `cqe_used` accounting can overcommit or leak CQEs. DIM work must be canceled before CQ destruction and must not call `modify_cq` after the device object is gone.

## Test signals

Validation should allocate/free CQs in each poll context, post WRs with `wr_cqe` callbacks, verify direct polling drains completions, verify softirq/workqueue polling re-arms and handles missed events, stress shared pool get/put with vector hints and capacity limits, run device teardown with pooled CQs, enable DIM on capable devices and observe `modify_cq` calls, and check trace events for CQ allocation, polling, scheduling, rescheduling, modification, and free. WARNs on usecnt, `cqe_used`, unsolicited direct completions, or destroy failures indicate regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cq.c -->
