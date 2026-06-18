# Research: sources/distributed-fs/ceph-client/net/core/dev.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006177`: lines 1-10245, `Docs/researches/chunks/subset-b-006177_research.md`
- `subset-b-006178`: lines 10246-13317, `Docs/researches/chunks/subset-b-006178_research.md`

## Chunk Research

### subset-b-006177: lines 1-10245

# sources/distributed-fs/ceph-client/net/core/dev.c lines 1-10245

## Scope

This chunk covers the first 10,245 lines of Linux network core `dev.c`. It starts with global includes and core data structures, then covers packet type registration, netdevice lookup and naming, open/close and notifier dispatch, timestamping static keys, transmit queue and offload validation, the main transmit entry points, receive backlog/RPS/RFS/generic-XDP processing, NAPI scheduling and threaded/busy-poll support, upper/lower netdevice adjacency management, offload extended statistics, device flag/MTU/MAC/port-state mutation, and the first XDP attach helpers.

The range ends immediately after `dev_xdp_prog_count()`. XDP program installation/link attach/detach and netdevice registration/unregistration continue in the next chunk.

## Purpose

This code is the central protocol-independent network-device core. It provides the shared machinery that device drivers, virtual devices, protocol stacks, tc/BPF, netfilter, sysfs, netlink, RPS/RFS, NAPI, and upper/lower stacked devices use to move packets and manage `struct net_device` state.

The main responsibilities in this chunk are:

- Maintain per-net namespace device indexes, name hashes, alternate names, ifindex xarray entries, and RCU-visible device lists.
- Register and unregister `struct packet_type` protocol handlers for `ETH_P_ALL`, per-device taps, per-net namespace handlers, and global protocol hashes.
- Provide lookup helpers for devices by name, ifindex, NAPI ID, hardware address, device type, and flags, with variants for RTNL, RCU, refcounted, and netdev-lock-held access.
- Open and close devices, including netpoll coordination, runtime PM resume, `ndo_open`/`ndo_stop`, qdisc activation/deactivation, RX mode programming, route/netlink notification, and notifier emission.
- Run global and per-network-namespace netdevice notifier chains, including registration replay, rollback, robust notifier calls, and per-device notifier migration across network namespaces.
- Implement core transmit (`__dev_queue_xmit`, `dev_hard_start_xmit`, `__dev_direct_xmit`) and receive (`netif_rx`, `netif_receive_skb`, list variants) paths.
- Manage NAPI scheduling, polling, threaded NAPI, busy polling, NAPI IDs, IRQ affinity notifier integration, CPU rmap support, and GRO flushing.
- Track stacked netdevice relationships for bonds, bridges, VLANs, masters, lowers, and other virtual topology users, including sysfs adjacency links and cycle/depth checks.
- Mutate user-visible device state such as flags, promiscuity/allmulti counts, MTU, TX queue length, MAC address, carrier/proto-down, port parent IDs, and offload statistics state.

## Important APIs, Types, and Data

Important global state includes `ptype_lock`, `ptype_base[]`, per-net `ptype_all`/`ptype_specific`, `netdev_chain`, per-net `netdev_chain`, per-CPU `softnet_data`, per-CPU `system_page_pool`, `napi_hash`, `napi_gen_id`, `xps_needed`, `rps_needed`, `rfs_needed`, `generic_xdp_needed_key`, ingress/egress/tcx static keys, `netstamp_needed_key`, and `dev_addr_sem`.

Important types and fields used in this chunk include:

- `struct net_device`: `name`, `name_node`, `ifindex`, `dev_list`, `index_hlist`, `dev_by_index`, `flags`, `gflags`, `promiscuity`, `allmulti`, `state`, `netdev_ops`, `xdp_state`, `xdp_prog`, `napi_list`, `adj_list`, queue counts, `tc_to_txq`, `xps_maps`, `rx_handler`, `rx_cpu_rmap`, `offload_xstats_l3`, and proto-down fields.
- `struct softnet_data`: per-CPU backlog queues, NAPI poll list, TX completion queue, output qdisc queue, RPS IPI state, process queue, and accounting counters.
- `struct napi_struct`: NAPI state bits, poll function, weight, timer, GRO state, NAPI ID, device list node, kthread, IRQ affinity notifier, config pointer, and busy-poll/defer-hard-IRQ settings.
- `struct packet_type`: protocol handler list nodes, callback functions, optional list callback, target device/netns, and AF_PACKET loopback filtering fields.
- `struct netdev_adjacent`: upper/lower relationship node with device reference tracking, master flag, ignore flag, reference count, private pointer, and RCU lifetime.
- `struct bpf_xdp_link`: BPF link wrapper for XDP program attachment state, introduced here but completed in the following chunk.

Important exported APIs in this range include `dev_add_pack`, `dev_remove_pack`, `dev_get_iflink`, `dev_fill_metadata_dst`, `dev_fill_forward_path`, device lookup helpers, `dev_alloc_name`, `netif_change_name`, `netif_open`, `netif_close`, netdevice notifier registration APIs, timestamp enable/disable, `dev_forward_skb`, XPS/TC queue APIs, queue count APIs, TSO limit APIs, `__netif_schedule`, SKB free helpers, device attach/detach, checksum/offload helpers, `netif_skb_features`, `dev_hard_start_xmit`, `validate_xmit_skb_list`, `__dev_queue_xmit`, `__dev_direct_xmit`, RFS helpers, generic XDP helpers, RX handler registration, `netif_receive_skb`, `netif_receive_skb_list`, NAPI enable/disable/add/delete/schedule/busy-poll APIs, adjacency walk/link/unlink APIs, offload xstats APIs, promiscuity/allmulti/flag/MTU/MAC/carrier/port/proto-down APIs, and `dev_xdp_prog_count`.

## Control Flow

Device list and name flow starts with `list_netdevice()` and `unlist_netdevice()`. Registration code outside this chunk allocates/initializes the device, then these helpers publish it into `net->dev_base_head`, the name hash, the ifindex hash, the alternate-name hashes, and `net->dev_by_index`; each mutation increments `net->dev_base_seq`. Name allocation validates filesystem/sysfs-safe names, supports one `%d` format, scans primary and alternate names, and uses a bitmap to find a free suffix. Rename uses `netdev_rename_lock`, updates the device name, renames the underlying `struct device`, refreshes sysfs adjacency links, re-adds the name node after `synchronize_net()`, and rolls back if `NETDEV_CHANGENAME` notifiers fail.

Packet type flow is split by `ptype_head()`. `ETH_P_ALL` handlers attach to per-device or per-net tap lists, protocol-specific handlers attach to per-device lists, per-net lists, or the global hash. Receive delivery later walks tap lists before ingress classification and protocol-specific lists after VLAN/rx-handler processing. `dev_remove_pack()` synchronizes with `synchronize_net()` so removed packet handlers can be freed safely.

Device open flow is `netif_open()` -> `__dev_open()`: check `IFF_UP`, resume parent runtime PM if needed, disable netpoll polling, emit `NETDEV_PRE_UP`, set `__LINK_STATE_START`, validate address, invoke `ndo_open`, re-enable netpoll, set the device up, program RX mode, activate qdiscs, add address randomness, send rtnetlink state, and emit `NETDEV_UP`. Close flow is batched in `netif_close_many()`: emit `NETDEV_GOING_DOWN`, clear running state, deactivate qdiscs, call `ndo_stop`, clear up state, re-enable netpoll, send rtnetlink, and emit `NETDEV_DOWN`.

Notifier flow uses per-net chains first and the global chain second. `register_netdevice_notifier()` closes races with netns setup/cleanup using `pernet_ops_rwsem` and RTNL, registers the raw notifier, and after boot replays `NETDEV_REGISTER` and `NETDEV_UP` for existing devices, rolling back on error. Per-net and per-device notifier variants repeat the same replay/unregister semantics for scoped chains and migrate callbacks when devices move network namespaces.

Transmit flow begins in `__dev_queue_xmit()`. It resets the MAC header, initializes qdisc packet length/segment accounting, records scheduling TX timestamps, enters BH-disabled RCU, applies cgroup priority mapping, runs egress netfilter/tc/BPF when enabled, handles dst release policy, selects a TX queue through driver `ndo_select_queue`, XPS, socket queue cache, or hash, then sends through the queue's qdisc or through the direct noqueue path. Before driver transmit, `validate_xmit_skb()` handles unreadable/decrypted SKBs, feature discovery, VLAN push-inside fallback, GSO segmentation, linearization, checksum fallback, and XFRM validation. `dev_hard_start_xmit()` calls `netdev_start_xmit()` on each skb or segment list item with tracing and tap cloning. Direct transmit bypasses qdisc, validates that no segmentation changed the skb, locks the selected TX queue, and calls the driver directly.

Receive ingress has two entry styles. `netif_rx()` and `__netif_rx()` enqueue an skb to a per-CPU backlog, using RPS if enabled; `netif_receive_skb()` processes directly in softirq context, again consulting RPS first. RPS/RFS computes a flow hash, uses per-RX-queue maps and socket flow tables to select CPUs while preserving ordering with input queue tail snapshots, and can ask hardware for flow steering through `ndo_rx_flow_steer()`. Backlog processing moves `input_pkt_queue` into `process_queue`, calls `__netif_receive_skb()`, and updates RPS head counters.

`__netif_receive_skb_core()` is the receive demultiplexer. It timestamps, resets headers, optionally runs generic XDP, strips VLAN headers, delivers taps, runs ingress tcx/tc and netfilter hooks, enforces PFMEMALLOC protocol limits, resolves VLAN devices, calls `rx_handler`, handles exact-delivery requests, then dispatches to global, per-net, original-device, and current-device packet type lists. The list receive path batches packets by matching packet-type callback and original device for efficient `list_func` delivery.

Generic XDP flow adapts an skb into an `xdp_buff`, expands/linearizes as needed to meet XDP headroom and writability requirements, runs the BPF program, applies head/tail/data_len/metadata changes back to the skb, and handles `XDP_PASS`, `XDP_DROP`, `XDP_ABORTED`, `XDP_TX`, and `XDP_REDIRECT`. Installing generic XDP updates `dev->xdp_prog`, reference counts old programs, toggles `generic_xdp_needed_key`, and disables LRO/GRO_HW.

NAPI flow uses state bits to serialize scheduling, polling, disable, threaded mode, and busy poll. `____napi_schedule()` either wakes a NAPI kthread or links the NAPI into the current CPU `softnet_data.poll_list` and raises `NET_RX_SOFTIRQ`. `net_rx_action()` drains the poll list within packet and time budgets, repolls full-budget NAPIs, sends pending RPS IPIs, and records time squeeze. `napi_complete_done()` clears scheduled/missed state, flushes GRO, arms watchdog timers for deferred IRQ/GRO behavior, and reschedules if work arrived. Threaded NAPI creates `napi/<dev>-<id>` kthreads, waits on `NAPI_STATE_SCHED_THREADED`, runs polling under BH-disabled context, and coordinates with busy-poll state.

Adjacency flow builds device stacks. Link creation rejects self-links, cycles, too-deep nesting, duplicate non-master links, and multiple masters. It emits `NETDEV_PRECHANGEUPPER`, inserts paired upper/lower adjacency nodes with netdev references and sysfs `upper_*`, `lower_*`, and `master` links, emits `NETDEV_CHANGEUPPER`, and updates upper/lower/nested levels across affected subgraphs. Rollback removes the paired adjacency if notifiers fail. Change-prepare/commit/abort temporarily ignores an old link to validate and stage replacement without creating false loops.

The final control-flow region mutates device flags and attributes. Promiscuity and allmulti maintain reference counts with overflow checks, update `dev->flags`, call driver RX flag callbacks, reprogram RX mode, audit promiscuous changes, and notify userspace. `netif_change_flags()` changes persistent flags, opens/closes on `IFF_UP` transitions, syncs global promisc/allmulti flags, then sends rtnetlink and notifier events. MTU changes validate min/max, call `NETDEV_PRECHANGEMTU`, delegate to `ndo_change_mtu` or write `dev->mtu`, and roll back with another notifier call if `NETDEV_CHANGEMTU` fails. MAC changes call pre-change notifiers, delegate to `ndo_set_mac_address`, mark `NET_ADDR_SET`, notify, and add randomness.

## State and Persistence

Most persistent state is stored in `struct net_device`, per-net namespace objects, and per-CPU `softnet_data`. Device names, ifindexes, alternate names, xarray entries, sysfs links, master/lower relationships, queue mappings, XPS maps, NAPI configs, XDP program pointers, offload stats pointers, flags, MTU, MAC address state, and proto-down state persist until explicit unregister, rename, queue resize, feature change, XDP detach, or link mutation.

RCU is the dominant read-side persistence model. Name nodes, packet type lists, device lists, NAPI hash entries, rx_handler pointers, XPS maps, adjacency lists, and XDP program pointers are published with RCU primitives and removed with grace-period expectations. Functions that return unreferenced pointers document RTNL or RCU requirements; refcounted wrappers use `dev_hold()`/`netdev_hold()` and tracker allocation.

Per-CPU softnet state persists RX backlog queues, processing queues, output qdisc queues, completion queues, RPS IPI lists, and accounting counters. `flush_all_backlogs()` removes packets for unregistering devices from all CPUs. TX skb frees from IRQ context are deferred through `softnet_data.completion_queue` and drained by `net_tx_action()`.

Static keys persist feature enablement and fast-path branching for backlog threads, ingress/egress hooks, tcx, software tc actions, timestamping, XPS, RPS/RFS, and generic XDP. Timestamp enable/disable uses deferred atomic accounting when jump labels are enabled to avoid toggling static branches directly from contexts that cannot safely do so.

NAPI persistence is split between live `struct napi_struct` and optional `dev->napi_config[]`. Disable saves NAPI ID, defer-hard-IRQ, GRO timeout, IRQ suspend timeout, affinity, and threaded mode; enable restores config, re-adds the NAPI ID to the hash, and reactivates threaded state. NAPI IDs are unique in `napi_hash` and reserved away from the `0..NR_CPUS` range.

Adjacency state uses `ref_nr` so repeated links can share a node and only delete when references drop. `master` nodes are forced to the front of upper lists and get a `master` sysfs link. `ignore` temporarily hides an adjacency from traversal/depth calculations during staged replacement.

## Dependencies and Integration Points

This code sits at the integration point for most of the networking stack:

- Driver callbacks in `struct net_device_ops`: `ndo_open`, `ndo_stop`, `ndo_validate_addr`, `ndo_fill_metadata_dst`, `ndo_fill_forward_path`, `ndo_features_check`, `ndo_select_queue`, `ndo_start_xmit` via `netdev_start_xmit`, `ndo_rx_flow_steer`, `ndo_change_rx_flags`, `ndo_change_mtu`, `ndo_set_mac_address`, `ndo_change_carrier`, physical port callbacks, XDP `ndo_bpf`, lower-device selectors, and xmit-slave selection.
- qdisc/scheduler APIs: qdisc enqueue/run/deactivate/reset, qdisc packet length accounting, BQL-ish TX queue state, `sch_direct_xmit()`, qdisc drop reasons, and tc classifier/action integration.
- BPF/XDP/tcx: generic XDP, XDP redirect/TX, BPF multi-program tcx ingress/egress, BPF net context, and later XDP link management in the next chunk.
- netfilter ingress/egress hooks, VLAN receive helpers, DSA checks, XFRM transmit validation/backlog, AF_PACKET taps, IPv4/IPv6 indirect receive callbacks, and socket memory-pressure handling for PFMEMALLOC skbs.
- CPU and IRQ infrastructure: RPS/RFS maps, CPU rmap for hardware steering, per-CPU softnet, smp call function async IPIs, CPU hotplug-aware XPS map updates, IRQ affinity notifiers, and PREEMPT_RT-specific backlog locking/threading behavior.
- Userspace-visible control planes: rtnetlink messages, sysfs adjacency links and device names, audit logs for promiscuity, devlink compatibility for physical port names/parent IDs, netlink extended ACKs, and notifier chains used by subsystems such as bonding, bridges, VLANs, switchdev/offloads, and protocol modules.

## Risks

- Lifetime bugs are high risk. Many helpers return non-refcounted pointers under RTNL or RCU, while others drop a reference after acquiring `netdev_lock()`. Mixing these conventions can produce use-after-free or lock ordering bugs.
- RCU publication/removal order matters. Name nodes, rx handlers, packet types, XDP programs, XPS maps, NAPI hash entries, and adjacency nodes need correct assignment order plus `synchronize_net()` or RCU freeing before data can be reclaimed.
- The TX path has subtle ownership rules: `__dev_queue_xmit()` consumes the skb regardless of return, GSO can turn one skb into a list, direct transmit treats lists as success for TCP semantics, and validation drops increment core stats. Incorrect retry assumptions can double-free or leak packets.
- Queue mapping is sensitive to stale configuration. Reducing real TX queues must update kobjects, qdisc state, shaper state, TC mappings, XPS maps, and reset stale queued packets above the new limit.
- RPS/RFS ordering depends on input queue head/tail snapshots. Incorrect updates to `last_qtail` or flow CPU changes can reorder packets for a flow.
- Generic XDP on skb is semantically close to driver XDP but not identical. It bypasses qdisc/taps for `XDP_TX`, may starve qdisc traffic, requires sufficient headroom/writable data, and must carefully reflect XDP head/tail/metadata changes back to skb fields.
- NAPI state bits are heavily overloaded. Races among disable, threaded polling, busy polling, watchdog timers, netpoll, and normal softirq polling can cause missed polls, double polls, stuck disabled state, or IRQs not being resumed if barriers/state transitions are wrong.
- Adjacency management has graph invariants. Failing cycle checks, depth updates, master exclusivity, rollback, or ignore handling can create invalid stacked topologies, sysfs leaks, or lockdep nested-level problems.
- Notifier failures require rollback. Name changes, upper link changes, MTU changes, offload xstats enablement, and notifier registration replay all contain rollback paths; missing a reverse notifier or state restore leaves subsystems inconsistent.
- Promiscuity/allmulti counters can overflow or desynchronize from `gflags`; the code contains explicit warnings because broken drivers or callers can leave RX filtering state inconsistent.
- The chunk boundary cuts through XDP attach support. `dev_xdp_mode()`, `dev_xdp_bpf_op()`, `dev_xdp_link()`, `dev_xdp_prog()`, and `dev_xdp_prog_count()` are only the setup helpers; full attach/detach/link lifecycle must be reconciled with the next chunk.

## Test and Validation Signals

Useful validation signals for this chunk include:

- Device registration/name tests: create, rename, add alternate names, move between namespaces, and unregister devices while checking `/sys/class/net`, ifindex lookup, rtnetlink events, and absence of stale name lookups after `synchronize_net()`.
- Packet handler tests: AF_PACKET taps, protocol handlers, per-device handlers, and remove-after-use tests under traffic to exercise RCU delivery and `dev_remove_pack()` synchronization.
- Open/close tests: bring devices up/down, include devices with `ndo_open` failures, runtime-suspended parents, netpoll users, and check correct notifier/rtnetlink order.
- TX path tests: qdisc bypass and queued qdisc, lockless qdisc, noqueue virtual devices, XPS queue selection, socket cached queue reselection, GSO segmentation, checksum fallback, VLAN push-inside fallback, unreadable/devmem skb rejection, egress tc/netfilter, recursion detection, and `tx_dropped` counters.
- RX path tests: `netif_rx()` backlog, direct `netif_receive_skb()`, RPS/RFS CPU steering, flow-limit drops, generic XDP pass/drop/tx/redirect/head-tail-adjust, ingress tc/netfilter, VLAN recursion, rx_handler outcomes, PFMEMALLOC filtering, list receive batching, and packet-type delivery order.
- NAPI tests: schedule/complete, budget exhaustion repoll, disable/enable, NAPI ID lookup, threaded mode enable/disable, busy-poll preference, IRQ suspend/resume watchdog, IRQ affinity notifier updates, CPU rmap allocation/release, and GRO timeout behavior.
- Stacked netdevice tests: bridge/bond/VLAN/master links, duplicate/master conflicts, cycle rejection, nesting limit rejection, sysfs upper/lower/master link creation/removal/rename, change prepare/commit/abort, and lower-state/bonding notifier delivery.
- State mutation tests: promiscuity/allmulti reference counts including overflow warnings, flag transitions including `IFF_UP`, MTU notifier rollback, TX queue length rollback, MAC address pre-change rejection, carrier/proto-down toggles, physical port parent recursion, and offload xstats enable/report/disable.
- Built-in runtime signals include tracepoints (`net_dev_queue`, `net_dev_start_xmit`, `net_dev_xmit`, `netif_rx`, `netif_receive_skb`, `napi_poll`, qdisc traces, XDP exception traces), ratelimited warnings, `WARN_ON_ONCE()` checks for bad queue/NAPI states, `softnet_data` counters, core RX/TX dropped/nohandler stats, audit promiscuity records, and rtnetlink notifier observations.

### subset-b-006178: lines 10246-13317

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
