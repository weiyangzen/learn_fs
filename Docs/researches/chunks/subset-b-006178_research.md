# sources/distributed-fs/ceph-client/net/core/dev.c lines 10246-13317

## Scope

This chunk covers the late core network-device management path in `net/core/dev.c`: XDP program and BPF-link attachment, netdev feature reconciliation, RX/TX queue and per-CPU stats allocation, device registration and teardown, network namespace moves, CPU-hotplug queue migration, master-upper feature aggregation, per-net namespace initialization/exit, netdev logging helpers, and the global `net_dev_init()` boot initializer.

The range starts with XDP helpers and ends at `subsys_initcall(net_dev_init)`. It is a lifecycle-heavy chunk: it owns transitions between allocated, registered, unregistering, unregistered, released, namespace-moving, and dummy states, plus the synchronization barriers needed to keep packet processing, notifier callbacks, sysfs/kobject state, qdisc teardown, and BPF/XDP state consistent.

## Purpose

The code makes `struct net_device` usable as a kernel-visible network interface. It validates and installs XDP programs, assigns ifindexes, reconciles feature bits across drivers and stacked devices, allocates queues/statistics/configuration storage, registers devices into a network namespace, publishes notifications to userspace and protocol stacks, and later unwinds all of those pieces during unregister, namespace exit, namespace migration, or final free.

It also initializes core global/per-namespace networking infrastructure at boot: packet type lists, per-CPU `softnet_data`, backlog NAPI, optional page pools, loopback/default-device pernet operations, NET_TX/NET_RX softirqs, CPU hotplug cleanup, and timestamp support.

## Important APIs, Types, and Functions

- `dev_xdp_sb_prog_count()` counts attached non-fragment XDP programs across all XDP modes.
- `netif_xdp_propagate()` forwards a `struct netdev_bpf` request to `ndo_bpf`, rejecting propagation when tcp-data-split or memory-provider RX queues are incompatible with a non-fragment XDP program.
- `dev_xdp_install()` builds an `XDP_SETUP_PROG` or `XDP_SETUP_PROG_HW` request, takes the extra `bpf_prog` ref expected by drivers, invokes the selected `bpf_op_t`, and updates non-HW generic/native XDP program accounting via `bpf_prog_change_xdp()`.
- `dev_xdp_attach()` is the central attach/detach validator for fd-based programs and BPF links. It enforces one XDP mode flag, replace semantics, no active BPF link replacement, upper-device restrictions, drv/skb mutual exclusion, offload/device-bound compatibility, and devmap/cpumap attach-type rejection.
- `bpf_xdp_link_*()` implements `struct bpf_link_ops` for XDP links: release/detach, deallocation, fdinfo/link-info reporting, and program update.
- `bpf_xdp_link_attach()` creates and primes a `BPF_LINK_TYPE_XDP`, attaches it under RTNL and netdev ops lock, settles an fd on success, and deliberately drops the device reference because the link does not own a persistent netdev ref.
- `dev_change_xdp_fd()` is the fd-based userspace entry used to attach, replace, or clear XDP programs after converting file descriptors to `BPF_PROG_TYPE_XDP` references.
- `dev_get_min_mp_channel_count()` scans RX queues for memory-provider state and returns the highest active channel count.
- `dev_index_reserve()` and `dev_index_release()` reserve or release namespace-local ifindexes in `net->dev_by_index` using xarray allocation.
- `netdev_fix_features()`, `__netdev_update_features()`, `netdev_update_features()`, and `netdev_change_features()` normalize feature dependencies, call driver `ndo_fix_features`/`ndo_set_features`, synchronize with upper/lower devices, and refresh VLAN/tunnel offload side state.
- `netif_alloc_rx_queues()`, `netif_alloc_netdev_queues()`, `netif_free_rx_queues()`, and `netif_free_tx_queues()` allocate/free RX and TX queue arrays and register per-RX-queue XDP metadata.
- `register_netdevice()` performs full netdev registration under RTNL: name validation, optional driver init, per-CPU stat allocation, ifindex reservation, feature initialization, post-init notifier, kobject registration, feature update, scheduler/linkwatch setup, namespace hashes, randomness, permanent address copy, `NETDEV_REGISTER`, and `RTM_NEWLINK`.
- `register_netdev()` wraps registration with a namespace RTNL lock.
- `netdev_wait_allrefs_any()` and `netdev_run_todo()` finish deferred unregister work outside RTNL by rebroadcasting unregister notifications, waiting for references to drop to the registration hold, freeing private resources, and dropping the kobject reference.
- `dev_get_stats()`, `dev_get_tstats64()`, `dev_fetch_sw_netstats()`, `dev_fetch_dstats()`, and `netdev_stats_to_stats64()` collate driver, legacy, per-CPU, and core drop/nohandler statistics into `rtnl_link_stats64`.
- `alloc_netdev_mqs()` allocates and initializes `struct net_device`, private storage, refcount tracking, address lists, queues, ethtool/config objects, NAPI config, defaults, namespace, and hook state.
- `free_netdev()` performs final object cleanup, including queues, addresses, NAPI, CPU rmap, ref trackers, per-CPU stats, XDP bulk queues, PHY topology, mutexes, and device-object release.
- `unregister_netdevice_queue()`, `unregister_netdevice_many_notify()`, `unregister_netdevice_many()`, and `unregister_netdev()` batch or wrap removal. The main notify path closes devices, unlists them, flushes backlogs, tears down qdisc/TCX/XDP/memory providers/BPF binding/offload stats, sends notifiers and netlink delete messages, flushes names/RSS contexts, calls `ndo_uninit`, unregisters kobjects, and queues deferred final release.
- `__dev_change_net_namespace()` moves a registered device between net namespaces while preserving registration state: it validates name/ifindex conflicts, reserves the target ifindex, closes/unlists/shuts down in the old namespace, sends unregister/newnet notifications, switches `dev_net` and possibly name, fixes kobjects/ownership, relists in the target namespace, and sends `RTM_NEWLINK`.
- `dev_cpu_dead()` migrates completion, output, poll, RPS, process, and input queues from an offline CPU's `softnet_data`.
- `netdev_increment_features()` and `netdev_compute_master_upper_features()` aggregate feature masks and header/headroom/tailroom/TSO limits from lower devices into a master/upper device.
- `netdev_init()` and `netdev_exit()` allocate/free per-net hash tables and xarray state.
- `default_device_exit_net()` and `default_device_exit_batch()` move eligible devices back to `init_net` and unregister the rest during namespace teardown.
- `net_dev_struct_check()` uses cacheline layout assertions for hot `struct net_device` read groups.
- `net_page_pool_create()`, backlog NAPI helpers, and `net_dev_init()` initialize global receive/transmit infrastructure and register pernet/softirq/hotplug handlers.

## Control Flow

XDP attachment flows through either `bpf_xdp_link_attach()` or `dev_change_xdp_fd()`. Both resolve the target device/program first, enter RTNL, take the device ops lock, and call `dev_xdp_attach()`. `dev_xdp_attach()` validates flags and current state, derives the target mode, rejects incompatible upper devices and program types, installs only when the effective program pointer changes, then records either `xdp_state[mode].link` or `.prog` and drops the old program ref. BPF-link update reuses `dev_xdp_install()` and atomically swaps `link->prog`; BPF-link release detaches from the device if the device has not already auto-detached during teardown.

Feature updates start with `netdev_get_wanted_features()`, optionally pass through driver `ndo_fix_features`, then through core dependency pruning in `netdev_fix_features()`. Upper devices can force features off on lowers through `netdev_sync_upper_features()`, and disabled upper features propagate down through `netdev_sync_lower_features()`. When features change, `ndo_set_features` is called before side-effect subsystems such as UDP tunnel info and VLAN filter state are synchronized in the correct enable/disable order.

Registration begins from an allocated but unregistered `net_device`. `register_netdevice()` validates ethtool ops and the name, allocates name nodes and per-CPU stats, calls `ndo_init`, reserves an ifindex, derives initial feature masks, runs post-init notifiers, registers the kobject, marks the state registered, updates feature state under the ops lock, initializes linkwatch and qdisc scheduler state, holds the registration reference, inserts the device into namespace lists/hashes, records permanent address state, sends `NETDEV_REGISTER`, and finally sends `RTM_NEWLINK` unless link creation is still initializing. Every failure path unwinds only resources acquired so far: ifindex reservation, pcpu stats, driver uninit/destructor, and name node.

Unregistration is split into an RTNL-held phase and a deferred phase. `unregister_netdevice_many_notify()` marks devices dismantling, closes running devices in a lock-depth-aware batch, unlists each device, changes state to `NETREG_UNREGISTERING`, flushes backlogs and synchronizes readers, shuts down qdisc/TC/BPF/XDP/memory-provider state, notifies protocol stacks, builds and sends delete messages, flushes address/name/RSS state, calls pre-uninit and driver uninit, removes kobjects and XPS queues, drops the registration hold, puts the device on `net_todo_list`, and increments `dev_unreg_count`. `netdev_run_todo()` later snapshots that list after RTNL unlock, waits for RCU and all external references, then frees per-CPU stats/private resources/free-netdev ownership and drops the final kobject reference.

Namespace migration is a mini unregister/register sequence that keeps `reg_state == NETREG_REGISTERED`. `__dev_change_net_namespace()` reserves the destination name/ifindex first, closes and unlists the device, marks `moving_ns`, tears down qdisc state, sends unregister/newnet notifications, flushes addresses and old adjacency links, moves per-net notifiers, switches `dev_net` and `ifindex`, optionally renames, fixes kobject name/uevent ownership, relinks adjacency, changes device ownership for the target user namespace, relists in target hashes, sends register notification, and emits `RTM_NEWLINK`.

Boot initialization in `net_dev_init()` is single-threaded while `dev_boot_phase` is true. It checks cacheline layout, initializes proc and kobject support, packet-type lists, pernet netdev state, backlog flushing, per-CPU `softnet_data`, optional page pools, optional threaded backlog NAPI, loopback/default-device pernet ops, softirq handlers, CPU-dead hotplug handling, and timestamp static-key state. On early failure after page-pool creation, it unregisters/destroys per-CPU page pools it created.

## State and Persistence Behavior

Persistent device state in this range includes `dev->xdp_state[]`, `dev->_rx`, `dev->_tx`, `dev->ethtool`, `dev->cfg`, `dev->cfg_pending`, `dev->napi_config`, feature masks, queue counts, statistics pointers, namespace membership, ifindex, name nodes, reg state, linkwatch/qdisc state, notifier list entries, and per-device ref tracking.

XDP state stores either a direct `struct bpf_prog *` or a `struct bpf_xdp_link *` per mode. Drivers own one program ref after `ndo_bpf` succeeds; the net_device/link state owns its own ref semantics. During device teardown, `dev_xdp_uninstall()` asks the driver to detach and then either nulls `link->dev` for auto-detached links or drops the direct program ref.

Ifindexes are namespace-local xarray reservations. A reserved index must either be installed by `list_netdevice()` or explicitly released by `dev_index_release()`. Namespace migration reserves the destination index before unlisting from the old namespace to avoid conflicts.

Feature state is stored in several masks (`features`, `hw_features`, `wanted_features`, `vlan_features`, `hw_enc_features`, `mpls_features`, `gso_partial_features`, `mangleid_features`) and may trigger external state in VLAN and UDP tunnel helpers. Master-upper recomputation persists aggregated lower-device constraints in the upper device and then calls `netdev_change_features()` so stacked VLAN devices can observe changes.

Registration state is guarded with explicit `WRITE_ONCE()` transitions and netdev locks. Valid states touched here include `NETREG_UNINITIALIZED`, `NETREG_REGISTERED`, `NETREG_UNREGISTERING`, `NETREG_UNREGISTERED`, `NETREG_RELEASED`, and `NETREG_DUMMY`. `free_netdev()` defers if the object is still unregistering, directly frees uninitialized/dummy devices, and otherwise relies on device core release after `put_device()`.

Deferred unregister state persists in global `net_todo_list`, `netdev_unregistering_wq`, and `dev_unreg_count`. The todo list is intentionally processed after RTNL is unlocked so sysfs/kobject teardown and reference waits can sleep without deadlocking core networking paths.

Statistics are read from driver callbacks, legacy atomics, or per-CPU structures. Per-CPU stat reads use `u64_stats_fetch_begin/retry` to avoid torn 64-bit values. `core_stats` allocation is lazy and uses `cmpxchg` plus `READ_ONCE` pairing so concurrent increments either share the installed allocation or free the loser allocation.

Per-net namespace state owns `dev_base_head`, `dev_name_head`, `dev_index_head`, `dev_by_index`, and `netdev_chain`. Global boot state owns packet-type lists, per-CPU `softnet_data`, optional `system_page_pool`, backlog threads, softirq registrations, and CPU hotplug callbacks.

## Dependencies and Integration Points

- RTNL and netdev ops locks are the primary serialization points for registration, unregister, namespace moves, feature changes, and XDP attach/detach.
- BPF/XDP integration uses `struct bpf_prog`, `struct bpf_xdp_link`, `struct bpf_link_ops`, `struct netdev_bpf`, `BPF_LINK_TYPE_XDP`, `BPF_PROG_TYPE_XDP`, XDP mode flags, `ndo_bpf`, BPF offload helpers, and dev-bound program checks.
- Driver integration is through `struct net_device_ops`: `ndo_init`, `ndo_uninit`, `ndo_fix_features`, `ndo_set_features`, `ndo_bpf`, stats callbacks, VLAN callbacks, RX-mode callbacks, peer-device callbacks, and rtnl link ops.
- Userspace notification surfaces include netlink `RTM_NEWLINK`/`RTM_DELLINK`, kobject uevents, sysfs/kobject registration, proc/kobject init, and fdinfo/link-info for BPF links.
- Protocol and stack integration uses `call_netdevice_notifiers()` for `NETDEV_POST_INIT`, `NETDEV_REGISTER`, `NETDEV_UNREGISTER`, and `NETDEV_PRE_UNINIT`.
- Queueing and datapath teardown integrate with qdisc scheduler setup/shutdown, linkwatch, backlog flushing, `synchronize_net()`, RCU barriers, NAPI lists, NET_TX/NET_RX softirqs, RPS IPIs, and CPU hotplug.
- Feature side effects integrate with VLAN filter state (`vlan_get/drop_rx_*_filter_info`), UDP tunnel offload state, TLS/GSO/GRO/LRO/checksum feature constraints, tunnel/MPLS/VLAN inherited features, and XFRM offload when configured.
- Memory and allocation dependencies include `kvzalloc_flex`, `kvzalloc`, `kzalloc_obj`, per-CPU allocation/free, xarray APIs, ref tracker APIs, kobject/device APIs, and optional page pool APIs.
- Network namespace integration uses pernet operations, `dev_net_set()`, `peernet2id_alloc()`, `move_netdevice_notifiers_dev_net()`, `netdev_change_owner()`, and namespace exit batching.

## Risks and Edge Cases

- XDP refcounting is delicate: `dev_xdp_install()` increments a program ref before driver handoff because drivers decrement on detach/replace. Missing either the increment or failure-path put would underflow or leak `bpf_prog` references.
- XDP attach with no explicit mode is ambiguous when multiple modes already have programs; `dev_xdp_attach()` rejects this to avoid detaching/replacing the wrong program.
- Generic and native XDP are mutually exclusive, while HW offload can coexist differently. Relaxing these checks can leave the datapath with conflicting XDP execution points.
- Tcp-data-split and memory-provider queues reject non-fragment XDP programs. Drivers using these RX paths need these guards both in direct install and propagation paths.
- BPF XDP links do not hold a netdev reference. The code depends on RTNL and teardown auto-detach (`link->dev = NULL`) to avoid use-after-free when devices unregister before link fd release.
- Feature updates have ordered side effects. UDP tunnel and VLAN helper calls intentionally update `dev->features` before enabling fetches and after disabling drops; reordering can make helpers no-op or leave stale hardware state.
- `__netdev_update_features()` returns `-1`, `0`, or `1` with non-obvious semantics: a negative driver failure maps to a non-zero notification signal because some features may have changed.
- Registration failure paths assume driver `ndo_init`, private destructor, name node, ifindex, and pcpu stats are unwound in reverse acquisition order. Adding resources in the middle requires matching labels.
- `register_netdevice()` sets `dev->needs_free_netdev = false` before unregistering on notifier failure, expecting an explicit `free_netdev()` by the caller.
- `netdev_wait_allrefs_any()` can loop indefinitely for leaked references. It rebroadcasts unregister notifications and prints ref trackers after `netdev_unregister_timeout_secs`, but correctness still depends on consumers dropping refs on `NETDEV_UNREGISTER`.
- `netdev_run_todo()` frees only after refcount reaches one and asserts protocol packet-type lists and IP pointers are gone. Missing notifier cleanup in another subsystem will stall or warn here.
- `unregister_netdevice_many_notify()` must remove all upper/lower adjacency by notifier time. Warnings after `NETDEV_PRE_UNINIT` indicate stacked devices failed to detach.
- Namespace migration keeps `NETREG_REGISTERED`, so notifiers must distinguish a move (`dev->moving_ns`) from final unregister. Incorrect handling can destroy stacked devices that are meant to survive migration.
- `free_netdev()` warns if `cfg` and `cfg_pending` differ, so pending configuration replacement must be committed or rolled back before final free.
- Lazy `core_stats` allocation can fail under `GFP_ATOMIC`; increments are silently dropped in that case.
- CPU hotplug queue migration handles backlog NAPI specially because `process_backlog()` must run on the owning CPU. Incorrect migration can process per-CPU backlog from the wrong context.
- Cacheline layout assertions in `net_dev_struct_check()` are compile-time ABI/performance guards. Field moves in `struct net_device` can break builds or hotpath assumptions.
- Boot failure cleanup only tears down page pools created before failure in this function; additions to `net_dev_init()` need matching cleanup or must be safe to leave absent until boot abort.

## Test Signals

- XDP attach tests should cover fd attach/detach, BPF-link attach/detach/update, replace success/failure with expected old program, invalid multiple mode flags, ambiguous no-mode replacement, active-link replacement rejection, drv/skb mutual exclusion, HW offload mode, device-bound mismatch, devmap/cpumap attach-type rejection, tcp-data-split rejection, and memory-provider rejection.
- XDP teardown tests should unregister a device with active direct XDP and active BPF-link XDP, verifying driver detach is called, direct program refs are dropped, and link fdinfo reports ifindex `0` after auto-detach.
- Feature tests should toggle checksum, SG, TSO/TSO6/TSO_ECN, GSO, GSO partial, RXCSUM/GRO_HW, RXFCS/LRO, TLS TX/RX, and UDP L4 GSO combinations and assert the normalized mask and notifications.
- Stacked-device tests should verify upper-disabled features propagate down, lower feature changes recompute master upper masks, and VLAN/tunnel inherited features update through `netdev_change_features()`.
- Registration tests should exercise duplicate/invalid names, driver `ndo_init` failure, VLAN acceleration missing callbacks, pcpu stat allocation failure, notifier failure, kobject failure, and successful netlink `RTM_NEWLINK` emission.
- Allocation/free tests should cover zero TX/RX queue rejection, RX queue XDP info registration rollback, ethtool/config/NAPI allocation failure unwind, dummy devices, unregistering deferred `free_netdev()`, and `cfg_pending` mismatch warnings.
- Unregistration tests should cover single and batched unregister, running device close, devices never registered during init unwind, linkwatch pending cleanup, leaked reference warning path, RSS context removal, XDP/memory-provider uninstall, netlink delete notification, and final wakeup on `netdev_unregistering_wq`.
- Stats tests should compare driver `ndo_get_stats64`, legacy `ndo_get_stats`, `NETDEV_PCPU_STAT_TSTATS`, `NETDEV_PCPU_STAT_DSTATS`, no-pcpu stats, and lazy `core_stats` additions under concurrent updates.
- Namespace migration tests should move devices with name conflicts, altname conflicts, requested ifindex conflicts, generated fallback names, running state, stacked VLAN/macvlan users, and different owning user namespaces.
- Namespace exit tests should verify migratable devices return to `init_net`, immutable devices are skipped, virtual devices with `dellink` are queued, and reverse registration order is used for teardown.
- CPU hotplug tests should offline CPUs with pending completion/output queues, scheduled NAPI, backlog NAPI, RPS IPIs, and queued input packets, then confirm packets are rescheduled or reinjected without loss.
- Boot/init tests should cover builds with and without `CONFIG_PAGE_POOL`, `CONFIG_RPS`, `CONFIG_XFRM_OFFLOAD`, threaded backlog NAPI, `CONFIG_PREEMPT_RT`, `CONFIG_LOCKDEP`, `CONFIG_XPS`, and namespace support.

## Chunk Boundary Notes

Earlier chunks define many helpers consumed here: device list/name/hash operations, `dev_xdp_prog()`, `dev_xdp_mode()`, `dev_xdp_bpf_op()`, notifier helpers, queue close/open helpers, qdisc and backlog primitives, and receive/transmit hotpath internals. This chunk is the major lifecycle and initialization tail for `net/core/dev.c`, and the final merged file report should connect it to earlier datapath, name-management, adjacency, and notifier sections.
