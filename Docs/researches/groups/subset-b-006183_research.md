# Research group subset-b-006183

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/neighbour.c -->
# sources/distributed-fs/ceph-client/net/core/neighbour.c

## Purpose

`neighbour.c` implements the generic Linux neighbor cache used by ARP and IPv6 Neighbor Discovery. It owns neighbor table allocation, lookup, creation, update, garbage collection, proxy-neighbor state, packet queueing during address resolution, rtnetlink APIs, procfs statistics, and sysctl registration for per-table and per-device neighbor parameters.

## Important APIs, Types, And Functions

The central types are `struct neigh_table`, `struct neighbour`, `struct neigh_parms`, `struct pneigh_entry`, `struct neigh_hash_table`, and `struct neigh_statistics`. Exported entry points include `neigh_lookup()`, `__neigh_create()`, `neigh_update()`, `__neigh_event_send()`, `neigh_resolve_output()`, `neigh_connected_output()`, `neigh_direct_output()`, `neigh_ifdown()`, `neigh_carrier_down()`, `neigh_changeaddr()`, `pneigh_create()`, `pneigh_delete()`, `pneigh_enqueue()`, `neigh_parms_alloc()`, `neigh_parms_release()`, `neigh_table_init()`, `neigh_table_clear()`, `neigh_xmit()`, `neigh_for_each()`, `__neigh_for_each_release()`, `neigh_sysctl_register()`, and `neigh_sysctl_unregister()`.

Important internal routines are `___neigh_create()` for allocation plus hash insertion, `__neigh_update()` for NUD state/address/flag transitions, `neigh_timer_handler()` for reachability state progression, `neigh_periodic_work()` and `neigh_forced_gc()` for cleanup, `neigh_proxy_process()` for delayed proxy replies, and the rtnetlink handlers `neigh_add()`, `neigh_delete()`, `neigh_get()`, `neigh_dump_info()`, `neightbl_set()`, and `neightbl_dump_info()`.

## Control Flow

Normal transmit resolution starts with `neigh_xmit()` or a protocol-specific lookup. If no entry exists, `__neigh_create()` allocates one, calls table/device/parameter constructors, grows the RCU hash table if needed, inserts into both the hash bucket and per-device neighbor list, and optionally returns a reference. Output then goes through the function pointer in `neigh->output`. `neigh_resolve_output()` calls `neigh_event_send()` to trigger solicitation and queue packets while incomplete; once valid, it builds the link header and sends via `dev_queue_xmit()`. `neigh_connected_output()` is the fast path for valid connected entries.

State transitions are centralized in `__neigh_update()`. It validates administrative versus protocol updates, updates extended flags (`NTF_EXT_LEARNED`, `NTF_MANAGED`, `NTF_EXT_VALIDATED`), handles `NUD_FAILED`, `NUD_STALE`, `NUD_REACHABLE`, `NUD_DELAY`, `NUD_PROBE`, and permanent states, updates cached hardware addresses under `ha_lock`, adjusts timers, refreshes the header cache, replays queued packets when an entry becomes valid, updates GC and managed lists, emits rtnetlink notifications, calls netevent notifiers, and emits tracepoints.

Timers and workqueues maintain liveness. `neigh_timer_handler()` advances reachable entries to delay, stale, probe, or failed states and sends solicitations until `neigh_max_probes()` is reached. `neigh_periodic_work()` recomputes randomized reachable time and removes old failed/stale entries when thresholds require it. `neigh_managed_work()` periodically probes entries marked `NTF_MANAGED`. Forced GC runs when allocation pressure reaches `gc_thresh2`/`gc_thresh3`.

Proxy neighbor flow uses a separate fixed-size hash (`phash_buckets`) protected by `phash_lock`. `pneigh_create()` and `pneigh_delete()` maintain entries; `pneigh_enqueue()` queues SKBs with a randomized proxy delay; `neigh_proxy_process()` later calls the table `proxy_redo` callback if the device still runs.

## State And Persistence Behavior

All state is in kernel memory. Neighbor entries are reference counted and RCU-freed, with `tbl->entries` tracking live allocations and `tbl->gc_entries` tracking entries subject to GC. Entries can be exempt from GC when permanent, externally learned, externally validated, or on loopback. Neighbor parameters are cloned per device and inherit default table values; sysctl writes mark overridden data-state bits and default writes propagate to device parameter blocks that have not overridden that field.

Hash table state is RCU-protected and can grow dynamically. `neigh_table_init()` allocates per-CPU stats, primary and proxy hashes, delayed work, proxy timer, and procfs stats. `neigh_table_clear()` tears those down. Device teardown flushes both regular and proxy entries and purges queued proxy packets. Sysctl and procfs registration creates user-visible but non-persistent control/state views.

## Dependencies And Integration Points

This file integrates with `struct net_device`, `dst_entry`, header operations, rtnetlink, netevent notifiers, procfs, sysctl, RCU, timers, delayed work, per-CPU counters, and tracepoints from `trace/events/neigh.h`. Protocol tables such as ARP and NDISC provide constructors, hash functions, solicit/error callbacks, proxy callbacks, and family-specific parameter registration.

Rtnetlink exposes `RTM_NEWNEIGH`, `RTM_DELNEIGH`, `RTM_GETNEIGH`, `RTM_GETNEIGHTBL`, and `RTM_SETNEIGHTBL`. Procfs exposes table statistics under `init_net.proc_net_stat`. Sysctl paths are registered as `net/ipv4/neigh/<dev-or-default>` and `net/ipv6/neigh/<dev-or-default>`.

## Risks

The implementation is concurrency-sensitive: table buckets require `tbl->lock`, entries require `neigh->lock`, link-layer address reads use `ha_lock`, proxy hash uses `phash_lock`, and hash readers rely on RCU. Incorrect lock ordering can deadlock with protocol callbacks or device unregister paths. GC threshold logic must not underflow `gc_entries` for exempt allocations. Timer reference handling is subtle because `neigh_add_timer()` takes a reference and `neigh_del_timer()`/timer completion releases it. Netlink validation must preserve strict checks for newer attributes and reject invalid combinations such as permanent plus managed or externally validated invalid states.

## Test Signals

Strong signals are ARP/ND neighbor add/delete/get/dump tests via rtnetlink, namespace-aware dumps, sysctl writes for reachable/retrans/proxy/queue parameters, forced GC threshold tests, packet queue overflow behavior, device unregister/carrier-down flush tests, managed entry refresh behavior, and tracepoint coverage for create/update/timer/event-send/cleanup paths. KASAN, lockdep, RCU stall detection, and refcount debug builds are especially relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/neighbour.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/net-procfs.c -->
# sources/distributed-fs/ceph-client/net/core/net-procfs.c

## Purpose

`net-procfs.c` creates procfs views for core network device and softnet state. It implements `/proc/net/dev`, `/proc/net/softnet_stat`, `/proc/net/ptype`, and `/proc/net/dev_mcast`, with per-network-namespace registration through pernet operations.

## Important APIs, Types, And Functions

The file uses seq_file iterators around `struct net_device`, `struct softnet_data`, and `struct packet_type`. `dev_seq_start()`, `dev_seq_next()`, and `dev_seq_stop()` iterate devices under RCU and `dev_seq_show()` prints the `/proc/net/dev` header and statistics using `dev_get_stats()`. Softnet iteration uses `softnet_get_online()` and `softnet_seq_show()` to expose per-online-CPU counters and queue lengths. Packet type iteration uses `struct ptype_iter_state`, `ptype_get_idx()`, `ptype_seq_next()`, and `ptype_seq_show()` to list packet handlers from device-specific, namespace, and global ptype lists. Multicast address output uses `dev_mc_seq_show()`.

Registration is performed by `dev_proc_net_init()`, `dev_proc_net_exit()`, `dev_mc_net_init()`, `dev_mc_net_exit()`, and exported initialization entry `dev_proc_init()`.

## Control Flow

When a network namespace is initialized, `dev_proc_net_init()` creates `dev`, `softnet_stat`, and `ptype` entries under `net->proc_net`, then initializes wireless extensions proc support. Failure unwinds entries in reverse order. A second pernet registration creates `dev_mcast`. Reads enter seq_file callbacks, take RCU where needed, locate the current object from the logical position, format one row, then release locks in `stop`.

The packet-type iterator first walks each device `ptype_all` list, then namespace-level `ptype_all`, namespace-level `ptype_specific`, and finally the global `ptype_base` hash buckets. It stores the current device in `ptype_iter_state` so formatting can show the device column and so next iteration can continue efficiently.

## State And Persistence Behavior

The file owns no durable state. It exposes live counters and lists from `net_device`, `softnet_data`, packet type registries, and multicast address lists. Proc entries are per-netns and are removed when the namespace exits.

## Dependencies And Integration Points

It depends on procfs, seq_file, net namespace proc directories, RCU device iteration helpers, per-CPU `softnet_data`, wireless extension proc hooks, packet type lists, and multicast address locking. `/proc/net/dev` output is a compatibility ABI consumed by many user-space tools.

## Risks

Iterator correctness is the main risk. Position handling must remain stable enough for seq_file even when devices or packet handlers change concurrently. The ptype traversal spans several list families and must filter by namespace to avoid leaking handlers across namespaces. `/proc/net/dev` formatting is ABI-sensitive; column changes can break parsers. Softnet output intentionally skips offline CPUs, so the printed CPU index must remain explicit.

## Test Signals

Useful tests read these proc files in multiple network namespaces while creating/removing interfaces, registering packet sockets, changing multicast memberships, and toggling CPUs if possible. Regression checks should compare `/proc/net/dev` column compatibility and validate that ptype/dev_mcast output does not expose another namespace's devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/net-procfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/net-sysfs.c -->
# sources/distributed-fs/ceph-client/net/core/net-sysfs.c

## Purpose

`net-sysfs.c` implements the `net` device class and its sysfs ABI. It exposes net_device attributes, statistics, physical-port metadata, RX queue controls, TX queue controls, BQL/XPS/RPS settings, namespace ownership, uevents, OpenFirmware lookup helpers, and netdev kobject registration/unregistration.

## Important APIs, Types, And Functions

Public functions include `netdev_kobject_init()`, `netdev_register_kobject()`, `netdev_unregister_kobject()`, `net_rx_queue_update_kobjects()`, `netdev_queue_update_kobjects()`, `netdev_change_owner()`, `netdev_class_create_file_ns()`, `netdev_class_remove_file_ns()`, `rps_cpumask_housekeeping()`, and `of_find_net_device_by_node()` when OF is enabled.

The file defines `net_class`, `net_ns_type_operations`, RX queue and TX queue kobject types, sysfs ops wrappers for queue attributes, and large attribute groups for netdev fields, statistics, physical-port fields, wireless placeholder directories, RX queue RPS attributes, TX queue XPS/maxrate/traffic-class attributes, and BQL attributes.

## Control Flow

`netdev_register_kobject()` initializes the embedded `struct device`, binds it to `net_class`, attaches default and device-specific groups, calls `device_add()`, creates the `queues` kset, then adds RX and TX queue kobjects. `netdev_unregister_kobject()` suppresses uevents for dead namespaces, holds a kobject reference, removes queue kobjects, disables memalloc-noio runtime PM behavior, and calls `device_del()`. Final memory release happens in `netdev_release()` after the device kobject refcount reaches zero.

Attribute reads generally use `netdev_show()` with RCU and `dev_isalive()`. Writes use `netdev_store()` for RTNL-protected changes or `netdev_lock_store()` for netdev-lock-protected changes after `CAP_NET_ADMIN` checks. `sysfs_rtnl_lock()` is a key deadlock-avoidance helper: it takes a temporary device reference, breaks kernfs active protection, obtains RTNL interruptibly, checks the device is still alive, then restores active protection.

RX queue setup creates `rx-N` kobjects, optional RPS attributes, optional driver queue groups, and default RPS masks. TX queue setup creates `tx-N` kobjects, default queue groups, optional BQL groups, and XPS/maxrate attributes. Queue update functions add kobjects for new queue counts and remove groups/kobjects for shrinking counts, suppressing uevents when the namespace is already dying.

## State And Persistence Behavior

State is mostly live kernel object state projected into sysfs. Some writes mutate net_device fields or driver state: MTU, flags, carrier, tx queue length, alias, group, protocol-down state, GRO flush timeout, deferred hard IRQs, threaded NAPI, RPS maps, RPS flow tables, XPS maps, TX maxrate, and BQL tunables. Queue kobject release callbacks clear kobject memory so queues can be re-registered later and drop device references. Ownership changes are persisted in sysfs inode ownership until the device moves again or is removed.

## Dependencies And Integration Points

This file integrates with sysfs/kernfs, device core, net namespaces, user namespaces, RTNL, netdev locking, ethtool link settings, linkwatch, RPS/XPS internals, BQL/DQL, runtime PM, OpenFirmware, namespace kobject operations, and driver `netdev_ops`. User space depends on `/sys/class/net/<ifname>/` and `/sys/class/net/<ifname>/queues/{rx,tx}-N/`.

## Risks

The major risk is lock ordering with sysfs active references and RTNL during unregister; `sysfs_rtnl_lock()` exists specifically to avoid an ABBA deadlock. Queue kobject re-addition can race with pending sysfs operations; the code detects initialized kobjects and returns `-EAGAIN`. Bitmap parsing for RPS/XPS must respect housekeeping CPUs and queue counts. Owner changes across namespaces must update device and queue groups consistently. Many attributes are ABI-stable, so names, permissions, and formatting are hard to change.

## Test Signals

Test with interface registration/unregistration under concurrent sysfs reads/writes, namespace moves with different owning user namespaces, queue count changes, RPS/XPS bitmap writes, BQL sysfs writes, carrier/MTU/flags changes, and driver paths with/without optional operations. Lockdep and KASAN are important for unregister races; user-space ABI tests should compare `/sys/class/net` layout and permissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/net-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/net-sysfs.h -->
# sources/distributed-fs/ceph-client/net/core/net-sysfs.h

## Purpose

`net-sysfs.h` is the internal header for network device sysfs integration. It declares the kobject lifecycle and queue-update helpers implemented by `net-sysfs.c` and shared with core netdevice code.

## Important APIs, Types, And Functions

The header declares `netdev_kobject_init()`, `netdev_register_kobject()`, `netdev_unregister_kobject()`, `net_rx_queue_update_kobjects()`, `netdev_queue_update_kobjects()`, and `netdev_change_owner()`. It also exposes `rps_default_mask_mutex` and declares the `skb_defer_disable_key` static key.

## Control Flow

Callers initialize the net class once through `netdev_kobject_init()`. Individual devices call `netdev_register_kobject()` during registration and `netdev_unregister_kobject()` during teardown. Queue count changes call the RX/TX update helpers. Namespace moves call `netdev_change_owner()` to adjust sysfs ownership.

## State And Persistence Behavior

The header owns no state. It exposes synchronization and static-key symbols owned elsewhere. The functions it declares mutate sysfs/device-core state and queue kobject state.

## Dependencies And Integration Points

It depends on `struct net_device`, `struct net`, `struct mutex`, and jump-label static-key infrastructure. The declarations are part of the boundary between netdevice registration code and sysfs implementation.

## Risks

Because these functions participate in registration, unregister, namespace moves, and queue resizing, misuse can leak kobjects, leave stale sysfs files, or expose wrong user namespace ownership. Callers must already satisfy the locking rules expected by `net-sysfs.c`.

## Test Signals

Compile coverage is the main direct signal. Behavioral coverage comes from netdevice registration/unregistration, queue resize, namespace move, and sysfs ownership tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/net-sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/net-traces.c -->
# sources/distributed-fs/ceph-client/net/core/net-traces.c

## Purpose

`net-traces.c` centralizes creation and export of networking tracepoints. By defining `CREATE_TRACE_POINTS` and including networking trace event headers, it emits the storage/metadata for tracepoints used across the networking stack.

## Important APIs, Types, And Functions

The file has no regular functions. Its important operations are trace-event header inclusion and `EXPORT_TRACEPOINT_SYMBOL_GPL()` calls for selected tracepoints. Exported tracepoints include bridge FDB/MDB events when bridge is enabled, neighbor events (`neigh_update`, `neigh_update_done`, `neigh_timer_handler`, `neigh_event_send_done`, `neigh_event_send_dead`, `neigh_cleanup_and_release`), `kfree_skb`, `napi_poll`, TCP reset/checksum events, UDP receive queue failure, and `sk_data_ready`.

## Control Flow

At build time, trace event headers expand into tracepoint definitions because `CREATE_TRACE_POINTS` is set before inclusion. At module/link time, the selected tracepoints are exported so GPL modules can attach or reference them. Conditional includes depend on `CONFIG_BRIDGE` and `CONFIG_PAGE_POOL`.

## State And Persistence Behavior

Tracepoint definitions are static kernel instrumentation state. Runtime tracing state is controlled by ftrace/perf/BPF/tracing subsystems, not by this file. No persistent data is stored here.

## Dependencies And Integration Points

This file integrates with the kernel tracepoint subsystem and networking trace headers for skb, net, napi, sock, udp, tcp, fib, qdisc, bridge, page_pool, and neigh events. It is an observability bridge for core networking, protocol code, and loadable modules.

## Risks

Tracepoint ABI stability matters because BPF and tracing tools can depend on event names and fields defined in the included headers. Missing exports can break modules that reference tracepoints; exporting too broadly can expose unstable instrumentation. Conditional compilation must match the availability of trace headers and features.

## Test Signals

Build tests across configs with and without bridge/page_pool are important. Runtime signals include listing events under tracefs, attaching perf/ftrace/BPF programs to exported tracepoints, and verifying neighbor, NAPI, skb drop, TCP, UDP, and bridge trace events fire in expected paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/net-traces.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/net_namespace.c -->
# sources/distributed-fs/ceph-client/net/core/net_namespace.c

## Purpose

`net_namespace.c` implements network namespace lifetime, per-namespace subsystem registration, generic pernet storage, namespace ID mapping, namespace rtnetlink operations, proc namespace operations, ownership helpers, and cleanup sequencing.

## Important APIs, Types, And Functions

Core globals include `init_net`, `net_namespace_list`, `net_rwsem`, `pernet_list`, `pernet_ops_rwsem`, and the generic ID allocator. Exported APIs include `peernet2id_alloc()`, `peernet2id()`, `peernet_has_id()`, `get_net_ns_by_id()`, `get_net_ns_by_pid()`, `get_net_ns_by_fd()`, `net_ns_get_ownership()`, `net_ns_barrier()`, `__put_net()`, `get_net_ns()`, `register_pernet_subsys()`, `unregister_pernet_subsys()`, `register_pernet_device()`, and `unregister_pernet_device()`.

Important internal functions include `net_alloc_generic()`, `net_assign_generic()`, `ops_init()`, `ops_undo_list()`, `preinit_net()`, `setup_net()`, `copy_net_ns()`, `cleanup_net()`, `unhash_nsid()`, rtnetlink handlers `rtnl_net_newid()`, `rtnl_net_getid()`, `rtnl_net_dumpid()`, and boot initializer `net_ns_init()`.

## Control Flow

Boot initialization allocates generic storage for `init_net`, preinitializes core fields, runs all registered pernet operations through `setup_net()`, adds the namespace to global lists/tree, registers netns pernet debug ops, and registers rtnetlink NSID handlers.

Creating a namespace through `copy_net_ns()` checks `CLONE_NEWNET`, charges the user namespace ucount, allocates `struct net` and generic storage, initializes namespace metadata, takes `pernet_ops_rwsem` for a consistent initializer list, and calls `setup_net()`. Failure unwinds user namespace references, ucounts, key domains, namespace common state, and passive references.

Destruction starts in `__put_net()`, which queues `cleanup_net()` on a single-thread workqueue. Cleanup removes namespaces from the global list and namespace tree, marks them dying, deletes peer nsid references from other namespaces, destroys IDRs, calls pernet `pre_exit`, `exit_rtnl`, `exit`, `exit_batch`, and generic free callbacks in reverse registration order, waits for RCU callbacks, frees deferred namespaces, drops ucounts/userns/key-domain references, and decrements passive references.

Pernet registration inserts operations either before device operations for subsystems or at the device boundary for pernet devices. Registration initializes all existing namespaces; failure undoes only those already initialized. Unregistration removes the operation and runs exit callbacks for all namespaces.

## State And Persistence Behavior

Network namespace state is in-memory and reference counted with active and passive references. `net->gen` is an RCU-managed expandable pointer array for subsystem private data. `net->netns_ids` is an IDR mapping peer namespaces to local NSIDs, protected by `nsid_lock`. Namespace membership is tracked in `net_namespace_list` under `net_rwsem` and in the namespace tree. State persists only while references exist; cleanup is asynchronous.

## Dependencies And Integration Points

The file integrates with nsproxy, proc namespace operations, rtnetlink, user namespaces and ucounts, key domains, debugfs ref tracker support, IDR, RCU, RTNL, workqueues, and every network subsystem using `struct pernet_operations`. It also provides sysfs ownership data consumed by net sysfs code.

## Risks

Ordering is critical. Pernet init/exit must be serialized against namespace creation/destruction; `pernet_ops_rwsem` and reverse unwinding enforce this. Cleanup must remove namespaces from discoverable lists before running exits to prevent new nsid references to dying namespaces. Generic storage resizing relies on RCU and never-changing assigned pointers. `copy_net_ns()` error paths are easy to leak references. Rtnetlink NSID operations must validate target and peer references while respecting namespace capability and lifetime rules.

## Test Signals

Signals include namespace create/destroy stress, module pernet register/unregister under concurrent namespace churn, NSID add/get/dump netlink tests, setns permission tests, user namespace ownership checks, refcount tracker leak checks, RCU/lockdep coverage, and fault-injection of setup failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/net_namespace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/net_test.c -->
# sources/distributed-fs/ceph-client/net/core/net_test.c

## Purpose

`net_test.c` is a KUnit suite for selected networking core helpers. It currently tests GSO segmentation behavior for different SKB layouts and compatibility conversion for IP tunnel flag bitmaps.

## Important APIs, Types, And Functions

The GSO section defines `struct gso_test_case`, a table of cases, `__init_skb()`, parameter generation with `KUNIT_ARRAY_PARAM()`, and `gso_test_func()`. It exercises `build_skb()`, SKB frags, `frag_list`, `skb_segment()`, `GSO_BY_FRAGS`, and expected segment sizing/header placement.

The tunnel section defines `struct ip_tunnel_flags_test`, flag bit arrays, `IP_TUNNEL_FLAGS_TEST`, and `ip_tunnel_flags_test_run()`. It exercises `ip_tunnel_flags_is_be16_compat()`, `ip_tunnel_flags_to_be16()`, and `ip_tunnel_flags_from_be16()`. The suite is registered as `net_core`.

## Control Flow

Each GSO test allocates an SKB backed by a page, writes a dummy MAC header, configures GSO size and protocol, optionally adds page frags or frag-list SKBs, sets feature flags, runs `skb_segment()`, then validates segment count, segment lengths including header size, MAC/network header positions, copied header bytes, and `segs->prev` last-segment linkage before consuming all SKBs.

Each tunnel flag test constructs source and expected bitmaps, checks whether source flags are compatible with legacy `__be16` representation, compares the converted big-endian value, converts back, and validates the expected bitmap.

## State And Persistence Behavior

This file has no persistent state. It allocates temporary pages and SKBs per test and consumes them before returning. Test cases are static const-like data in the module.

## Dependencies And Integration Points

It depends on KUnit, SKB/GSO internals, page allocation, network feature flags, and IP tunnel flag helpers. It provides regression coverage for behavior used by transport offload and tunnel implementations.

## Risks

The GSO tests manipulate low-level SKB internals, so incorrect setup can test an artificial invalid state rather than real stack behavior. Some cases depend on feature flags such as `NETIF_F_SG`, `NETIF_F_HW_CSUM`, and `NETIF_F_GSO_PARTIAL`. The tunnel flag tests depend on endian-specific legacy conflicts and must remain correct on both little-endian and big-endian builds.

## Test Signals

The main signal is KUnit execution of suite `net_core` across architectures/endian variants and configs with relevant SKB/GSO support. Failures indicate regressions in segmentation sizing, header propagation, frag-list handling, `GSO_BY_FRAGS`, or tunnel flag compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/net_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netclassid_cgroup.c -->
# sources/distributed-fs/ceph-client/net/core/netclassid_cgroup.c

## Purpose

`netclassid_cgroup.c` implements the legacy `net_cls` cgroup subsystem, which associates a 32-bit classid with tasks and propagates that classid into sockets for traffic classification.

## Important APIs, Types, And Functions

The main state type is `struct cgroup_cls_state`, reached from `struct cgroup_subsys_state` by `css_cls_state()`. Exported `task_cls_state()` retrieves a task's classid cgroup state under the appropriate RCU/BH/trace locking context. Cgroup callbacks are `cgrp_css_alloc()`, `cgrp_css_online()`, `cgrp_css_free()`, and `cgrp_attach()`. The control file callbacks are `read_classid()` and `write_classid()`.

Socket propagation is handled by `update_classid_task()` and `update_classid_sock()`, which iterate a thread-group leader's file descriptors and call `sock_cgroup_set_classid()` for socket files.

## Control Flow

When a cgroup CSS is allocated, the file creates zeroed `cgroup_cls_state`. When brought online, it inherits the parent's classid if present. When tasks attach to a cgroup, `cgrp_attach()` updates sockets for each task in the taskset. When users write `classid`, `write_classid()` stores the new value in the CSS and iterates all tasks in that CSS to update currently open sockets.

`update_classid_task()` only processes thread-group leaders to avoid duplicate file-table traversal for multithreaded processes. It locks the task, iterates file descriptors in batches of 1000, unlocks and reschedules between batches to avoid long stalls, then resumes from the returned descriptor index.

## State And Persistence Behavior

The classid is stored per cgroup in memory and inherited by child cgroups at online time. Existing sockets are updated on attach and classid write; new sockets are expected to pick up the current cgroup classid through socket cgroup data initialization elsewhere. No state persists beyond cgroup lifetime.

## Dependencies And Integration Points

This file integrates with the cgroup subsystem, task CSS lookup, file descriptor tables, socket file detection, and `net/cls_cgroup.h` socket cgroup data. It defines `net_cls_cgrp_subsys` with a legacy cftype named `classid`.

## Risks

The main risk is consistency versus latency when updating many open descriptors. The batching avoids holding `file_lock` too long but means concurrent socket creation may race; the comment notes new sockets should already receive the new classid. Only processing thread-group leaders assumes shared file tables in threaded tasks. Locking context for `task_cls_state()` must match cgroup RCU expectations.

## Test Signals

Tests should cover reading/writing `net_cls.classid`, child inheritance, task migration between cgroups, updating existing sockets, creating sockets during classid changes, large descriptor tables, and classification behavior in qdisc/classifier paths that consume socket classid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netclassid_cgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netdev-genl-gen.c -->
# sources/distributed-fs/ceph-client/net/core/netdev-genl-gen.c

## Purpose

`netdev-genl-gen.c` is generated YNL kernel code for the generic netlink `netdev` family described by `Documentation/netlink/specs/netdev.yaml`. It defines attribute validation policies, split operation dispatch, multicast groups, per-socket private-data hooks, and the `genl_family` object.

## Important APIs, Types, And Functions

The file exports policy arrays for common nested types: `netdev_lease_nl_policy`, `netdev_page_pool_info_nl_policy`, and `netdev_queue_id_nl_policy`. It defines command-specific policies for device get, page-pool get/stats, queue get/create, NAPI get/set, qstats get, dmabuf bind RX/TX, and queue creation. The `netdev_nl_ops` array maps commands to implementation callbacks declared in the generated header but implemented elsewhere. `netdev_nl_mcgrps` declares `mgmt` and `page-pool` multicast groups. `netdev_nl_family` is the exported family object.

## Control Flow

Generic netlink registration code consumes `netdev_nl_family`. Incoming requests are validated using the policy associated with the matching `genl_split_ops` entry, then dispatched to callbacks such as `netdev_nl_dev_get_doit()`, `netdev_nl_queue_get_dumpit()`, `netdev_nl_napi_set_doit()`, or `netdev_nl_queue_create_doit()`. Dump and do operations are split when both forms exist. Per-netlink-socket private data is initialized and destroyed through wrappers around `netdev_nl_sock_priv_init()` and `netdev_nl_sock_priv_destroy()`.

## State And Persistence Behavior

The generated file stores static validation metadata and the global `genl_family` descriptor. Runtime request state belongs to generic netlink and the implementation callbacks. Family socket private state has size `sizeof(struct netdev_nl_sock)` and is managed by the callback hooks.

## Dependencies And Integration Points

It depends on generic netlink, netlink policy helpers, UAPI `linux/netdev.h`, and implementation functions from `net/netdev_netlink.h`. Conditional operations depend on `CONFIG_PAGE_POOL` and `CONFIG_PAGE_POOL_STATS`. Administrative commands are marked with `GENL_ADMIN_PERM`; the family is namespace-aware with `netnsok = true` and permits `parallel_ops`.

## Risks

Because this file is generated, manual edits would be overwritten and may desynchronize from the YAML spec. Policy mistakes can reject valid user requests or accept invalid attributes. Range checks are security-relevant for IDs, ifindexes, queue types, NAPI settings, and dmabuf binding. `parallel_ops = true` means callbacks must provide their own synchronization.

## Test Signals

Signals include YNL selftests generated from the spec, generic netlink family introspection, command validation tests for accepted/rejected attributes, namespace tests, page-pool config matrix builds, and admin-permission checks for privileged operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netdev-genl-gen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netdev-genl-gen.h -->
# sources/distributed-fs/ceph-client/net/core/netdev-genl-gen.h

## Purpose

`netdev-genl-gen.h` is the generated header for the generic netlink `netdev` family. It declares the generated policy arrays, operation callbacks to be provided by implementation code, multicast group IDs, the family object, and per-socket private hooks.

## Important APIs, Types, And Functions

The header declares `netdev_lease_nl_policy`, `netdev_page_pool_info_nl_policy`, and `netdev_queue_id_nl_policy`; doit/dump callbacks for device, page-pool, queue, NAPI, qstats, dmabuf bind, NAPI set, and queue create commands; multicast group enum values `NETDEV_NLGRP_MGMT` and `NETDEV_NLGRP_PAGE_POOL`; `extern struct genl_family netdev_nl_family`; and `netdev_nl_sock_priv_init()`/`netdev_nl_sock_priv_destroy()`.

## Control Flow

Implementation files include this header to provide the declared callbacks and register or reference `netdev_nl_family`. The generated C file includes this header to build the split operation table and family descriptor.

## State And Persistence Behavior

The header owns no runtime state. It defines link-time contracts for static policy arrays and the family descriptor.

## Dependencies And Integration Points

It depends on generic netlink headers, UAPI `linux/netdev.h`, and `net/netdev_netlink.h` for callback/private state types. It is tied to `Documentation/netlink/specs/netdev.yaml` and `tools/net/ynl/ynl-regen.sh`.

## Risks

Regenerating the YAML output can change callback declarations, group IDs, policy array names, or family wiring. Consumers must stay in sync with this generated contract. Missing callbacks or signature drift will fail builds; semantic drift can break user-space netdev netlink clients.

## Test Signals

Build coverage is the direct signal. Runtime signals come from generic netlink registration and YNL command tests that exercise every declared callback path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netdev-genl-gen.h -->
