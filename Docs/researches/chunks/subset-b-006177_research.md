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
