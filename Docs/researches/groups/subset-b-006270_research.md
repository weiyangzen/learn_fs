# subset-b-006270 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_api.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_api.c

## Purpose
`sch_api.c` is the packet scheduler API front end for Linux traffic control. It owns qdisc registration, qdisc lookup by handle/name, root and class grafting, netlink create/change/delete/get/dump handlers for qdiscs and traffic classes, common size/rate table support, qdisc watchdog timers, class hash helpers, and hardware offload helper calls. The file deliberately keeps algorithm-specific scheduling out of this layer; concrete qdisc modules provide `Qdisc_ops` and optional `Qdisc_class_ops`.

## Important APIs, Types, and Functions
The exported qdisc registry entry points are `register_qdisc()`, `unregister_qdisc()`, `qdisc_get_default()`, and `qdisc_set_default()`. Lookup and topology helpers include `qdisc_lookup()`, `qdisc_lookup_rcu()`, `qdisc_hash_add()`, `qdisc_hash_del()`, `qdisc_leaf()`, `qdisc_alloc_handle()`, and `qdisc_tree_reduce_backlog()`.

Common resource helpers include `qdisc_get_rtab()` / `qdisc_put_rtab()` for legacy rate tables, `qdisc_get_stab()` / `qdisc_put_stab()` plus `__qdisc_calculate_pkt_len()` for size tables, `qdisc_watchdog_init*()`, `qdisc_watchdog_schedule_range_ns()`, and `qdisc_watchdog_cancel()`. Class hash helpers are `qdisc_class_hash_init()`, `qdisc_class_hash_insert()`, `qdisc_class_hash_grow()`, `qdisc_class_hash_remove()`, and `qdisc_class_hash_destroy()`.

The central netlink paths are `tc_modify_qdisc()`, `__tc_modify_qdisc()`, `tc_get_qdisc()`, `__tc_get_qdisc()`, `tc_dump_qdisc()`, `tc_ctl_tclass()`, `__tc_ctl_tclass()`, and `tc_dump_tclass()`. Serialization helpers are `tc_fill_qdisc()` and `tc_fill_tclass()`. Offload helpers are `qdisc_offload_dump_helper()`, `qdisc_offload_graft_helper()`, `qdisc_offload_query_caps()`, and the root-specific `qdisc_offload_graft_root()`.

## Control Flow
Module initialization in `pktsched_init()` registers per-netns `/proc/net/psched` support, built-in qdiscs (`pfifo_fast`, `pfifo`, `bfifo`, head-drop pfifo, `mq`, `noqueue`), rtnetlink handlers for qdisc and class messages, and the tc wrapper layer. Individual modules later call `register_qdisc()` to add their `Qdisc_ops` to the global registry guarded by `qdisc_mod_lock`.

For qdisc creation/change, `tc_modify_qdisc()` parses `rtm_tca_policy`, optionally requests a qdisc module, resolves the target net device, takes the device ops lock, and delegates to `__tc_modify_qdisc()`. That function interprets `tcm_parent`, `tcm_handle`, and netlink flags to choose one of three paths: change an existing qdisc, create a new qdisc and graft it, or graft an existing handle. It rejects ingress children, handle minor bits on qdisc handles, parent loops via `check_loop()`, and moves between parents. `qdisc_create()` resolves `TCA_KIND`, allocates the qdisc, validates ingress/root handle rules, assigns automatic handles, applies shared block indexes and STABs, invokes `ops->init()`, installs rate estimators, hashes the qdisc, and emits tracepoints. `qdisc_graft()` then attaches the qdisc to either a root/ingress device queue or a classful parent, handling device deactivate/activate, offload notifications, refcounts, and rtnetlink notifications.

For qdisc get/delete, `tc_get_qdisc()` resolves the qdisc by parent/class leaf or explicit handle. Delete requires a nonzero class id and nonzero qdisc handle, then calls `qdisc_graft()` with `new == NULL`; get sends a `RTM_NEWQDISC` reply through `qdisc_get_notify()`. Dump walks all devices and their root plus ingress qdiscs, skipping built-in and invisible qdiscs unless requested.

Traffic class operations follow the same netlink pattern. `__tc_ctl_tclass()` normalizes parent/handle major IDs, locates a classful qdisc, uses the qdisc's `Qdisc_class_ops` to find/delete/get/change a class, rejects shared block attrs on classes, and rebinds classifier references when a class is created or removed. Class dump iterates root and hashed child qdiscs, calling each qdisc's class walker.

## State and Persistence
All state is in kernel memory. Global process-wide scheduler state includes `qdisc_base`, `default_qdisc_ops`, `qdisc_rtab_list`, and `qdisc_stab_list`. Per-device state is stored in `net_device`, `netdev_queue`, qdisc hash tables, root qdisc pointers, and optional ingress queue pointers. Per-qdisc state includes handles, parent IDs, refcounts, stats, STAB pointers, rate estimators, optional class operations, and module ownership.

There is no disk persistence. Netlink requests mutate in-memory qdisc trees; dumps reconstruct user-visible state from current kernel structures. RCU is used for qdisc hashes and size tables, RTNL/device operation locks serialize configuration, `sch_tree_lock()` protects qdisc tree changes, and qdisc watchdogs use hrtimers to reschedule roots when packets become eligible.

## Dependencies and Integration Points
This file sits between rtnetlink (`RTM_*QDISC`, `RTM_*TCLASS`) and qdisc modules. It depends on `net/pkt_sched.h`, `net/pkt_cls.h`, gnet stats, BPF module ownership helpers, RCU, hrtimer, netdevice queue management, rate estimators, and optional `CONFIG_PROC_FS`, `CONFIG_NET_CLS`, and retpoline mitigation static keys. Hardware offload integrates through `net_device_ops->ndo_setup_tc()` using `TC_SETUP_ROOT_QDISC`, qdisc-specific setup types, and `TC_QUERY_CAPS`.

## Risks
The highest-risk areas are tree mutation, refcounting, and lock/RCU ordering. Root grafting must not leave device queues pointing at freed qdiscs, ingress/clsact replacement must avoid concurrent miniqdisc access, and module refs must be released on all create/change errors. Handle normalization is subtle: wrong major/minor interpretation can target the wrong class or allow invalid topology. STAB/rate table sharing uses manual refcounts, so error paths must put old references exactly once. Netlink dump paths must preserve cursor state without skipping or duplicating qdiscs under partial skb output.

## Test Signals
Useful tests are `tc qdisc add/change/replace/del/show` across root, ingress, clsact, and classful children; automatic handle allocation; duplicate qdisc registration failure; unknown qdisc module autoload; class create/delete/get/dump with filters bound to classes; STAB and rate estimator configuration; invisible qdisc dump filtering; qdisc tree loop rejection; root graft on multiqueue devices; ingress replacement under active filters returning busy; and offload-capable drivers returning success, `-EOPNOTSUPP`, and hard errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_blackhole.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_blackhole.c

## Purpose
`sch_blackhole.c` implements the minimal `blackhole` qdisc. Every packet accepted by enqueue is dropped immediately, and dequeue/peek always return no packet. It is useful as an explicit traffic sink while keeping qdisc attachment semantics.

## Important APIs, Types, and Functions
The only behavior functions are `blackhole_enqueue()` and `blackhole_dequeue()`. `blackhole_qdisc_ops` advertises id `blackhole`, no private state, enqueue/dequeue/peek callbacks, and module ownership. `blackhole_init()` registers the qdisc through `register_qdisc()` at device initcall time.

## Control Flow
On enqueue, the qdisc calls `qdisc_drop()` for the skb, then returns `NET_XMIT_SUCCESS | __NET_XMIT_BYPASS`, signaling that the packet did not remain queued and callers should not treat it as a congestion backoff event. Dequeue and peek return `NULL`, so the qdisc is always empty from the device transmit scheduler's perspective.

## State and Persistence
There is no qdisc-private state, no queue, no timers, no child qdiscs, and no persistence. Statistics are updated only through the common qdisc drop path.

## Dependencies and Integration Points
The file depends only on core qdisc/skbuff headers and `register_qdisc()` from `sch_api.c`. It integrates with traffic control by registering `Qdisc_ops` with id `blackhole`; there are no netlink options, class operations, hardware offload hooks, or module exit unregister path in this source.

## Risks
The main behavioral risk is operator surprise: enqueue reports success with bypass while discarding all packets. Because there is no `module_exit()` unregister in this file, it behaves like built-in/device-init registered scheduler code rather than a normal unloadable qdisc module.

## Test Signals
Attach `blackhole` to a test interface or class and verify packets are dropped, qdisc backlog and qlen stay at zero, dequeue never emits skbs, and `tc qdisc show` exposes the qdisc id. Drop counters should move through the standard qdisc drop accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_blackhole.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_cake.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_cake.c

## Purpose
`sch_cake.c` implements CAKE, the Common Applications Kept Enhanced qdisc. It combines bandwidth shaping, Diffserv tin scheduling, set-associative flow queueing, host isolation, optional NAT-aware hashing, optional ACK filtering, optional GSO splitting, and Cobalt AQM, which blends CoDel and BLUE. The file also provides a `cake_mq` wrapper that installs CAKE under multiqueue devices while sharing one configuration object.

## Important APIs, Types, and Functions
Core state types are `cobalt_params`, `cobalt_vars`, `cake_flow`, `cake_host`, `cake_heap_entry`, `cake_tin_data`, `cake_sched_config`, and `cake_sched_data`. Packet-private metadata is stored in `struct cobalt_skb_cb` inside `qdisc_skb_cb()`.

The Cobalt AQM helpers are `cobalt_newton_step()`, `cobalt_invsqrt()`, `cobalt_queue_full()`, `cobalt_queue_empty()`, and `cobalt_should_drop()`. Classification and hashing are handled by `cake_select_tin()`, `cake_handle_diffserv()`, `cake_classify()`, `cake_hash()`, `cake_update_flowkeys()`, and host-flow helpers such as `cake_get_flow_quantum()`. Packet manipulation helpers include `flow_queue_add()`, `dequeue_head()`, `cake_ack_filter()`, TCP option helpers, `cake_overhead()`, and `cake_calc_overhead()`.

The qdisc callbacks are `cake_enqueue()`, `cake_dequeue()`, `cake_reset()`, `cake_change()`, `cake_init()`, `cake_destroy()`, `cake_dump()`, and `cake_dump_stats()`. Configuration helpers include `cake_config_change()`, `cake_configure_rates()`, `cake_reconfigure()`, `cake_set_rate()`, and Diffserv layout functions for besteffort, precedence, diffserv8, diffserv4, and diffserv3. Minimal class/stat support is provided by `cake_tcf_block()`, `cake_walk()`, and `cake_dump_class_stats()`. `cake_mq_*()` functions wrap common `mq` helpers for per-TXQ CAKE instances.

## Control Flow
Initialization creates a default config (`diffserv3`, triple isolation, unlimited rate, 100 ms interval, 5 ms target, split GSO enabled), obtains a classifier block, initializes a watchdog, allocates all tins and their 1024 flows, seeds the overflow heap, computes `quantum_div[]`, and calls `cake_reconfigure()`.

On enqueue, CAKE classifies the packet through optional tc filters and then tin selection. Tin selection uses firewall marks, `skb->priority`, or Diffserv DSCP tables; wash mode rewrites DSCP to zero while preserving ECN. Flow selection uses set-associative hashing over flow keys and optional source/destination host keys, with conntrack-based NAT correction when enabled. GSO packets may be segmented into individual skbs, each with Cobalt enqueue time and adjusted length. Non-GSO packets are appended to the selected flow; optional ACK filtering scans the flow for older redundant pure TCP ACKs that can be safely removed. Backlog, tin stats, heap position, bandwidth capacity estimation, sparse/bulk/decaying flow lists, and memory usage are updated. If memory exceeds `buffer_limit`, `cake_drop()` repeatedly drops from the longest flow, updating BLUE state and qdisc tree backlog.

On dequeue, the global shaper first checks `time_next_packet` and `failsafe_next_packet`; if transmission is too early, a qdisc watchdog is armed. In unlimited mode, tins are selected by DRR-style deficits. In shaped mode, the scheduler chooses a tin that is eligible by time, preferring earlier tin schedules. Within a tin, flows rotate among decaying, new, and old lists. Flows with exhausted deficits are moved to the old list and receive quantum adjusted by host bulk-flow counts. Packets are dequeued through Cobalt; marked packets are transmitted, but drop decisions remove packets and retry unless that would drop a flow's last packet. Successful dequeue updates byte stats, delay EWMAs, tin and flow deficits, shaper virtual time, active queue sharing state, and watchdog state.

Configuration changes parse `TCA_CAKE_*` attributes, update rate, Diffserv mode, flow mode, NAT, overhead, ATM/PTM framing, autorate ingress, wash, ingress mode, memory limit, ACK filter, GSO split, and fwmark settings. Reconfiguration recomputes tin rates, Cobalt target/interval, quantum, global shaper timing scale, and buffer limit. `cake_mq` creates one CAKE child per TX queue and replaces each child's config pointer with a shared parent config; child qdiscs cannot be individually reconfigured or grafted.

## State and Persistence
All state is volatile qdisc memory. Per-flow state includes skb linked list, deficit, Cobalt variables, drop count, host indexes, and set membership. Per-tin state includes flows, backlog arrays, set-association tags, host bulk-flow counts, tin shaper state, Cobalt parameters, flow lists, byte/packet/drop/mark counters, delay EWMAs, and hash collision stats. Per-qdisc state includes the config pointer, watchdog, overflow heap, global shaper time, memory usage, active tin/flow indexes, autorate estimator fields, and multiqueue sync fields. No filesystem persistence exists; netlink dumps reconstruct configuration and stats from current memory.

## Dependencies and Integration Points
CAKE depends on qdisc core APIs, classifier blocks, flow dissector, TCP/IP header parsing, GSO segmentation, reciprocal math, netfilter conntrack when NAT mode is enabled, netlink `TCA_CAKE_*` attributes, and common `mq` helpers. It registers `cake` and `cake_mq` with `register_qdisc()`. It exposes a classifier block at class zero so tc filters can override flow/host indexes or perform actions.

## Risks
The implementation is dense and timing-sensitive. Risks include incorrect qdisc tree backlog compensation when splitting GSO or ACK-filtering, stale flow set/host bulk counters after hash collisions or empty-flow transitions, overflow heap corruption causing wrong overlimit drops, unsafe TCP ACK filtering if option/sequence checks miss a state-carrying ACK, and shaper watchdog mistakes that stall or burst traffic. Conntrack NAT mode is conditional; enabling it without kernel support returns `-EOPNOTSUPP`. `cake_mq` shares one config across children, so changes must handle per-child stats reset and rate repartitioning correctly.

## Test Signals
Exercise all Diffserv modes, fwmark and priority overrides, wash behavior for IPv4/IPv6, flow isolation modes, NAT mode with and without conntrack, ACK filter normal/aggressive modes, split-GSO on/off, ingress shaping, autorate ingress, unlimited mode, very low rate shaping, memory-limit drops, and `cake_mq` on multiqueue devices. Inspect tin stats, per-flow class stats, ECN marks, Cobalt drops, hash collision counters, ACK drops, delay EWMAs, buffer usage, qlen/backlog consistency, and watchdog-driven dequeue after shaped sleeps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_cake.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_cbs.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_cbs.c

## Purpose
`sch_cbs.c` implements the IEEE 802.1Q Credit Based Shaper qdisc for time-sensitive networking workloads. It rate-limits a traffic class using credits that accumulate at `idleslope` while packets wait and deplete at `sendslope` while packets transmit. It can operate in software or request hardware offload through the device driver's `ndo_setup_tc()`.

## Important APIs, Types, and Functions
`struct cbs_sched_data` stores offload mode, TX queue index, port rate, last transmission timestamp, current credits, configured high/low credits, slopes, watchdog, child qdisc, and selected enqueue/dequeue function pointers. The software datapath is `cbs_enqueue_soft()` and `cbs_dequeue_soft()`; offloaded mode uses `cbs_enqueue_offload()` and `cbs_dequeue_offload()`. Helpers include `timediff_to_credits()`, `delay_from_credits()`, `credits_from_len()`, `cbs_child_enqueue()`, and `cbs_child_dequeue()`.

Configuration and integration functions are `cbs_change()`, `cbs_init()`, `cbs_reset()`, `cbs_destroy()`, `cbs_dump()`, `cbs_enable_offload()`, `cbs_disable_offload()`, `cbs_set_port_rate()`, and `cbs_dev_notifier()`. Classful wrapper operations expose one child through `cbs_graft()`, `cbs_leaf()`, `cbs_find()`, `cbs_walk()`, and `cbs_dump_class()`.

## Control Flow
Initialization requires `TCA_CBS_PARMS`, creates a default `pfifo` child qdisc, registers the child in the qdisc hash, adds the CBS instance to a global notifier list, computes the TX queue index, initializes software enqueue/dequeue callbacks, sets up the watchdog, and then applies the supplied parameters.

On software enqueue, if the queue was empty and credits are positive, credits are reset to zero and `last` is set to now so an idle class stops accumulating credit. The packet is then enqueued into the child, while parent qlen/backlog are incremented. On software dequeue, CBS waits until any previously transmitted packet's estimated finish time has passed. If credits are negative, it accumulates credits according to elapsed time and `idleslope`; if credits are still negative, it schedules the watchdog for the time credits should reach zero and returns `NULL`. Once eligible, it dequeues from the child, subtracts credits according to packet length and `sendslope / port_rate`, clamps to `locredit`, and estimates the next finish timestamp using the current port rate.

In offload mode, configuration calls `ndo_setup_tc(dev, TC_SETUP_QDISC_CBS, ...)` with queue and credit parameters. The software qdisc still wraps the child queue for accounting, but dequeue no longer enforces credit timing; the hardware is expected to shape. Device up/change notifications update `port_rate` from ethtool link settings for software mode.

## State and Persistence
CBS keeps all state in memory. Persistent-looking configuration such as `idleslope`, `sendslope`, `hicredit`, `locredit`, and offload mode is only qdisc-private state visible through netlink dumps. `port_rate` is an atomic bytes-per-second value updated by notifier events. `last`, `credits`, and watchdog state are runtime scheduling state. A global `cbs_list` protected by `cbs_list_lock` tracks active instances for link speed updates.

## Dependencies and Integration Points
The qdisc depends on `pfifo_qdisc_ops` for its default child, `qdisc_watchdog` from `sch_api.c`, ethtool link settings, netdevice notifiers, `TC_SETUP_QDISC_CBS` hardware offload, and `TCA_CBS_PARMS` netlink configuration. As a one-class qdisc it integrates with tc graft/leaf/dump flows and can have its child replaced.

## Risks
Credit math uses signed 64-bit nanosecond and bytes-per-second products; extreme slopes, long time deltas, or zero port rate paths must avoid overflow and division errors. Software shaping accuracy depends on correct port speed detection; fallback speed is 10 Mbps if ethtool data is unavailable. Offload transition must restore software callbacks on disable and avoid leaving hardware shaping enabled after destroy. The notifier finds a single matching instance and then updates outside the spinlock, so list lifetime is protected by RTNL assumptions.

## Test Signals
Test mandatory-parameter validation, software shaping with positive/negative credit transitions, watchdog wakeups after negative credits, link speed change updates, offload success/failure/disable paths, grafting a replacement child qdisc, reset clearing credits and child queue, dump round-tripping slopes in kbit/s, and qlen/backlog consistency between parent and child.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_cbs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_choke.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_choke.c

## Purpose
`sch_choke.c` implements CHOKe, a stateless active queue management qdisc derived from RED. When average queue size exceeds the low threshold, it samples an already queued packet at random; if the sampled packet belongs to the same flow as the new packet, both are dropped. This approximates fair bandwidth allocation without maintaining per-flow queues.

## Important APIs, Types, and Functions
`struct choke_sched_data` stores RED parameters and variables, CHOKe stats, head/tail indexes, ring mask, and a random-access skb pointer table that may contain holes. `struct choke_skb_cb` caches a flow key digest in qdisc skb private data.

Core helpers include `choke_len()`, `choke_zap_head_holes()`, `choke_zap_tail_holes()`, `choke_drop_by_idx()`, `choke_match_flow()`, `choke_peek_random()`, and `choke_match_random()`. Qdisc callbacks are `choke_enqueue()`, `choke_dequeue()`, `choke_peek_head()`, `choke_reset()`, `choke_change()`, `choke_init()`, `choke_dump()`, `choke_dump_stats()`, and `choke_destroy()`.

## Control Flow
Configuration parses `TCA_CHOKE_PARMS`, `TCA_CHOKE_STAB`, and optional `TCA_CHOKE_MAX_P`, validates RED thresholds/table parameters, caps the configured packet limit, allocates or resizes the ring to the next power-of-two mask, migrates existing packets while dropping overflow, and initializes RED parameters and variables under the qdisc tree lock.

On enqueue, the qdisc invalidates the new skb's cached key, computes RED average queue length, and exits idle state if needed. Below `qth_min`, the packet is admitted if the hard limit allows. Above `qth_min`, CHOKe samples a queued skb and compares flow digests generated by the flow dissector; a match drops the sampled skb and then drops the new skb with congestion notification. If the average exceeds `qth_max`, the packet is forced dropped or ECN-marked depending on flags. Between thresholds, RED probability decides mark/drop. If admitted, the skb is placed at `tail` and qlen/backlog are incremented. Dequeue removes the head skb, skips holes, updates stats, and starts RED idle timing when the ring becomes empty.

## State and Persistence
All state is volatile. The queue is a circular array of skb pointers with holes left by random drops; head and tail adjustment functions compact only from the edges. RED state (`qavg`, `qcount`, idle timer/random state) persists across packets until reset or reconfiguration. Stats distinguish probabilistic drops/marks, forced drops/marks, hard-limit drops, and CHOKe flow matches. No state survives qdisc deletion.

## Dependencies and Integration Points
CHOKe depends on RED helpers from `net/red.h`, ECN marking via `INET_ECN_set_ce()`, flow dissection and digest creation, vmalloc-backed arrays, netlink RED attributes, and qdisc core stats/backlog APIs. It registers as a non-classful qdisc with a minimal classifier-oriented comment but no `Qdisc_class_ops` in this file.

## Risks
The random-access ring can contain holes, so head/tail handling and resize migration must keep qlen/backlog synchronized. `choke_peek_random()` retries only a few times before falling back to head, which can bias sampling under many holes. Flow matching depends on digest correctness and protocol equality; encapsulated or unusual packets may not be grouped as operators expect. Reconfiguration while packets are queued can drop packets when the new limit is smaller, so backlog reduction must match actual bytes dropped.

## Test Signals
Test RED parameter validation, ECN vs harddrop behavior, probabilistic marks/drops between thresholds, forced actions above max threshold, same-flow random match drops, ring resize up/down with queued packets, hole skipping after random drops, idle average decay after empty dequeue, stats dump fields, and qlen/backlog consistency under repeated random deletions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_choke.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_codel.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_codel.c

## Purpose
`sch_codel.c` adapts the generic Controlled Delay AQM implementation to a simple FIFO qdisc. It timestamps packets on enqueue, delegates drop/mark scheduling to `net/codel_impl.h`, and exposes CoDel configuration and stats through traffic-control netlink.

## Important APIs, Types, and Functions
`struct codel_sched_data` contains `codel_params`, `codel_vars`, `codel_stats`, and an overlimit drop counter. CoDel-specific callbacks passed to the generic implementation are `dequeue_func()` and `drop_func()`. Qdisc callbacks are `codel_qdisc_enqueue()`, `codel_qdisc_dequeue()`, `codel_change()`, `codel_init()`, `codel_dump()`, `codel_dump_stats()`, and `codel_reset()`.

## Control Flow
Initialization sets the default packet limit to 1000, initializes CoDel params/vars/stats, captures device MTU, applies optional netlink configuration, enables bypass when the limit is nonzero, and marks the qdisc as having dequeue-side drops. Enqueue succeeds while `qdisc_qlen(sch) < sch->limit`: it records enqueue time and appends to the tail. Over-limit enqueue increments `drop_overlimit` and drops with `QDISC_DROP_OVERLIMIT`.

Dequeue calls `codel_dequeue()` with backlog pointer, parameter/state/stat structures, packet length and enqueue time accessors, and the local drop/dequeue callbacks. The generic CoDel code may drop one or more packets before returning an skb; if so, `codel_qdisc_dequeue()` propagates drop count/bytes to parent qdiscs with `qdisc_tree_reduce_backlog()`, then clears deferred counters. Successful dequeue updates byte stats.

Configuration parses target, limit, interval, ECN enable, and CE threshold. It updates fields under `sch_tree_lock()` and, if the new limit is below current qlen, dequeues and drops excess packets, then reduces parent backlog. Dump serializes current params and only emits CE threshold when enabled.

## State and Persistence
The FIFO queue is the embedded `sch->q`. CoDel runtime state includes count, lastcount, drop_next, dropping flag, latest delay, max packet, ECN/CE stats, and deferred drop counters. This state resets on qdisc reset and is not persisted beyond qdisc lifetime. Netlink dumps expose configuration and current algorithm stats only.

## Dependencies and Integration Points
The file depends on `net/codel.h`, `net/codel_impl.h`, and `net/codel_qdisc.h` for the algorithm. It uses qdisc core queue helpers, gnet stats, netlink `TCA_CODEL_*` attributes, and `qdisc_tree_reduce_backlog()` from the scheduler API. It registers qdisc id `codel`.

## Risks
Most algorithmic risk is in the generic CoDel implementation, but this adapter must maintain backlog correctly because CoDel drops occur during dequeue. Limit changes can drop many packets while locked, so byte counters must match. Time units are shifted CoDel time units; incorrect microsecond-to-CoDel conversion would change control behavior. `drop_func()` updates qdisc drop stats, while parent backlog reduction is deferred, so both paths must remain paired.

## Test Signals
Test default init/dump, target/interval/limit/ECN/CE-threshold changes, enqueue over limit, limit reduction with queued packets, dequeue-side dropping under persistent delay, ECN marking when enabled, reset clearing queue and CoDel vars, and parent backlog consistency after deferred drops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_codel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_drr.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_drr.c

## Purpose
`sch_drr.c` implements a classful Deficit Round Robin scheduler. Each class owns a child qdisc and a quantum; active classes are served round-robin using per-class deficits so variable-sized packets receive approximately fair service.

## Important APIs, Types, and Functions
`struct drr_class` stores class common metadata, byte/queue stats, optional rate estimator, active-list node, child qdisc, quantum, and deficit. `struct drr_sched` stores the active class list, classifier block/list, and class hash table.

Class management functions are `drr_change_class()`, `drr_delete_class()`, `drr_search_class()`, `drr_graft_class()`, `drr_class_leaf()`, `drr_qlen_notify()`, `drr_dump_class()`, `drr_dump_class_stats()`, and `drr_walk()`. Filter integration is through `drr_tcf_block()`, `drr_bind_tcf()`, and `drr_unbind_tcf()`. Datapath callbacks are `drr_enqueue()` and `drr_dequeue()`, with lifecycle handled by `drr_init_qdisc()`, `drr_reset_qdisc()`, and `drr_destroy_qdisc()`.

## Control Flow
Qdisc initialization obtains a tc filter block, initializes the class hash, and initializes the active list. Creating a class requires options, parses optional `TCA_DRR_QUANTUM`, defaults quantum to device MTU, allocates a class, creates a default `pfifo` child (or uses `noop_qdisc`), optionally installs a rate estimator, inserts the class into the hash under the tree lock, and grows the hash if needed. Updating an existing class can replace the estimator and quantum.

On enqueue, classification first honors `skb->priority` when its major matches the qdisc handle, then runs tc filters. Classifier actions can consume/drop packets before class selection. A selected class receives the packet through its child qdisc. If enqueue succeeds and the class was inactive, it is appended to the active list and its deficit is reset to its quantum. Parent qlen/backlog are incremented.

On dequeue, the scheduler repeatedly inspects the first active class and peeks at its child. If the head packet length is within the class deficit, the packet is dequeued, deficit is reduced, an empty class is removed from active list, class and parent stats are updated, and the skb is returned. If the packet is too large, the class gains another quantum and moves to the active-list tail. `drr_qlen_notify()` removes a class from the active list when a child reports it became empty.

## State and Persistence
All state is in memory. Class definitions, child qdiscs, deficits, active-list membership, stats, and rate estimators persist only for the qdisc lifetime. Class hash membership tracks configured classes; active list membership tracks classes with non-empty child queues. There is no disk persistence.

## Dependencies and Integration Points
DRR depends on class hash helpers from `sch_api.c`, tc classifier blocks, gnet stats/rate estimators, default `pfifo` child qdiscs, qdisc grafting, and netlink `TCA_DRR_QUANTUM`. It registers class operations so generic tc class commands can create/delete/graft/dump classes and bind filters.

## Risks
Fairness depends on child `peek()` being reliable; a non-work-conserving child returning `NULL` while queued triggers `qdisc_warn_nonwc()` and can stall dequeue. Active-list state must stay synchronized with child qlen on enqueue, dequeue, reset, delete, and qlen notifications. Deleting a class with bound filters or references is blocked by `qdisc_class_in_use()`, but missing bind/unbind would risk use-after-free. Quantum zero is rejected; very small quantums can cause many list rotations before large packets are sent.

## Test Signals
Test class create/change/delete, zero quantum rejection, default MTU quantum, filter classification by classid and direct class pointer, `skb->priority` classification, classifier shot/stolen actions, child graft replacement, active-list rotation fairness with different packet sizes, class deletion while in use, reset clearing active list and child queues, and stats showing deficit only for non-empty classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_drr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_dualpi2.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_dualpi2.c

## Purpose
`sch_dualpi2.c` implements DualPI2, a dual-queue AQM for L4S and classic traffic. It follows RFC 9332-style coupled dual-queue PI2 behavior: L4S packets use a low-latency queue with scalable ECN marking, classic packets use the main queue with squared probability, and both queues share a PI controller plus weighted starvation protection.

## Important APIs, Types, and Functions
`struct dualpi2_sched_data` stores the L queue, classic qdisc pointer, classifier block, PI2 parameters and hrtimer, step-AQM parameters, classic protection credit/weights, memory and ECN settings, GSO/drop policy flags, and statistics. `struct dualpi2_skb_cb` stores enqueue timestamp, step eligibility, classification result, and ECN codepoint. Classification values are `DUALPI2_C_CLASSIC`, `DUALPI2_C_L4S`, and `DUALPI2_C_LLLL`.

Important helpers include `dualpi2_read_ect()`, `dualpi2_skb_classify()`, `must_drop()`, `dualpi2_classic_marking()`, `dualpi2_scalable_marking()`, `dualpi2_mark()`, `dequeue_packet()`, `do_step_aqm()`, `calculate_probability()`, `dualpi2_timer()`, `dualpi2_calculate_c_protection()`, and alpha/beta scaling helpers. Qdisc callbacks are `dualpi2_qdisc_enqueue()`, `dualpi2_qdisc_dequeue()`, `dualpi2_change()`, `dualpi2_init()`, `dualpi2_reset()`, `dualpi2_destroy()`, `dualpi2_dump()`, and `dualpi2_dump_stats()`. Minimal class ops expose a filter block and two logical classes through `dualpi2_walk()`.

## Control Flow
Initialization marks dequeue-side drops, sets up the PI2 hrtimer, creates a default `pfifo` L queue, obtains a classifier block, installs defaults, applies optional netlink config, and starts the timer. Defaults include limit 10000, target 15 ms, update interval 16 ms, scaled alpha/beta, step threshold 1 ms, C protection weight 10 percent classic / 90 percent L queue, L4S ECN mask, coupling factor 2, dequeue-time dropping, overload dropping, and GSO splitting.

On enqueue, `dualpi2_skb_classify()` reads the packet ECN bits, classifies ECT(1)-matching packets as L4S by mask, allows `skb->priority` to choose one of the logical classes, and otherwise runs tc filters. GSO packets may be segmented; each segment inherits classification and ECN metadata before independent enqueue. `dualpi2_enqueue_skb()` enforces packet and memory limits, optionally performs early PI2 marking/dropping, stamps enqueue time, updates memory/max stats, and enqueues to either the L queue or the main classic queue. L-queue packets are counted both in the child qdisc and in the parent qdisc's aggregate qlen/backlog.

On dequeue, `dequeue_packet()` chooses L or classic queue using the sign of `c_protection_credit`, queue availability, and configured weights. It removes from the selected queue, updates head timestamps, parent/child qlen and backlog, memory usage, and returns a credit delta proportional to packet length. `dualpi2_qdisc_dequeue()` then applies dequeue-time PI2 marking/dropping if configured, applies the L-queue step AQM for eligible L4S packets, updates byte stats and protection credit on success, or defers tree backlog reduction for dropped packets until the loop completes.

The PI2 hrtimer locks the root qdisc and periodically recomputes `pi2_prob` from the max of classic and L queue head delays. The update combines integral (`alpha`) and proportional (`beta`) terms against target and previous delay, clamps probability, and optionally caps L4S probability when overload dropping is disabled.

## State and Persistence
DualPI2 keeps volatile runtime state in its private qdisc data plus the embedded main queue and separate L child queue. Per-packet qdisc control block metadata carries timestamps and classification. PI probability, queue head timestamps, memory usage, packet counters, ECN/step mark counters, deferred drop counters, and C protection credit change continuously. Reset clears queues and runtime stats while preserving configuration. Nothing is persisted outside kernel memory.

## Dependencies and Integration Points
The qdisc depends on ECN helpers, GSO segmentation, hrtimers, tc classifier blocks, default `pfifo` child queue, qdisc queue/backlog helpers, and netlink `TCA_DUALPI2_*` attributes with range validation. It integrates with tc filters through a minimal class API and with qdisc core through dequeue-side drop accounting.

## Risks
The aggregate accounting is subtle because L packets are counted in both the L child and parent aggregate; drops and dequeues must adjust both exactly once. The timer locks the root qdisc while reading queue delay state, so lock ordering must stay compatible with qdisc teardown. Probability scaling uses fixed-point 32-bit values and explicit overflow bounds; incorrect alpha/beta validation could destabilize marking. GSO splitting requires negative backlog compensation when segments replace the original skb. Early-vs-dequeue dropping changes semantics and must keep deferred drop stats paired with parent backlog reduction.

## Test Signals
Test default init/dump, each netlink parameter and validation range, L4S ECN-mask classification, priority/filter classification to all logical classes, GSO splitting on/off, packet and memory limit enforcement, early and dequeue drop modes, overload drop vs mark behavior, step threshold in packets and microseconds, non-ECT L-queue step drops, PI timer probability changes under induced delay, reset clearing both queues, and qlen/backlog consistency after deferred drops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_dualpi2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_etf.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_etf.c

## Purpose
`sch_etf.c` implements the Earliest TxTime First qdisc. It orders packets by `skb->tstamp` transmit time, releases them only when they enter a configured delta window before txtime, optionally treats txtime as a deadline, reports missed/invalid txtime errors back to sockets, and can request hardware ETF offload.

## Important APIs, Types, and Functions
`struct etf_sched_data` stores offload/deadline/skip-socket-check flags, clockid, queue index, delta, last transmitted txtime, an rb-tree ordered by skb tstamp, a qdisc watchdog, and a clock read function pointer. Validation and packet checks are `validate_input_params()` and `is_packet_valid()`. Queue operations are `etf_enqueue_timesortedlist()`, `etf_peek_timesortedlist()`, `etf_dequeue_timesortedlist()`, `timesortedlist_drop()`, `timesortedlist_remove()`, and `timesortedlist_clear()`.

Other integration functions are `reset_watchdog()`, `report_sock_error()`, `etf_enable_offload()`, `etf_disable_offload()`, `etf_init()`, `etf_reset()`, `etf_destroy()`, and `etf_dump()`.

## Control Flow
Initialization requires `TCA_ETF_PARMS`, validates that the clock id is static, currently requires `CLOCK_TAI`, rejects negative delta, records the TX queue index, optionally enables offload through `ndo_setup_tc(dev, TC_SETUP_QDISC_ETF, ...)`, saves flags and parameters, selects the matching `ktime_get*()` function, and initializes a qdisc watchdog with the configured clock.

On enqueue, ETF validates the packet unless `skip_sock_check` is set. Normal validation requires a full socket with `SOCK_TXTIME`, matching socket clockid, matching deadline mode, a txtime not in the past, and a txtime not before the last transmitted txtime. Invalid packets are dropped and may generate a socket extended error with `SO_EE_ORIGIN_TXTIME`. Valid packets are inserted into a cached rb-tree ordered by txtime, qlen/backlog are incremented, and the watchdog is rearmed for the earliest packet's `txtime - delta`.

On dequeue, ETF peeks at the earliest packet. Expired packets with txtime before now are dropped in order and reported as missed. In deadline mode, the earliest valid packet is removed immediately and its timestamp is rewritten to now. In normal mode, the packet is removed only when now is after `txtime - delta`; otherwise dequeue returns `NULL` and the watchdog remains armed. Removal resets skb rbnode-overlaid list fields, restores `skb->dev`, updates backlog and byte stats, records `last`, and decrements qlen.

## State and Persistence
ETF state is in memory only. The rb-tree holds queued skbs ordered by txtime; `last` enforces non-decreasing transmit times; the watchdog schedules the next eligibility time. Offload and mode flags are qdisc-private config visible through dumps. Socket error reporting clones skbs transiently into the owning socket error queue when requested.

## Dependencies and Integration Points
ETF depends on rb-tree skb helpers, qdisc watchdog support, socket txtime fields and error queue APIs, POSIX clock ids, netlink `TCA_ETF_PARMS`, and hardware offload through `TC_SETUP_QDISC_ETF`. It registers qdisc id `etf` and has no class operations or child qdisc.

## Risks
Clock handling is strict: validation currently requires `CLOCK_TAI`, so users with other clocks are rejected even though a switch contains other clock readers. Packets can be dropped for socket mismatch, past txtime, or non-monotonic txtime relative to `last`; this is correct but easy to misconfigure. The rbnode overlays skb list fields, so removal must always reset `next`, `prev`, and `dev`. Offload enable failures abort init, and destroy must disable offload if it was enabled. Watchdog cancellation guards handle partially initialized qdiscs.

## Test Signals
Test missing/invalid parameters, non-TAI clock rejection, negative delta rejection, socket txtime validation, skip-socket-check mode, deadline and non-deadline dequeue timing, expired packet drops and socket errors, rb-tree ordering for equal and increasing txtimes, non-monotonic txtime rejection after `last`, offload success/failure/disable, reset clearing the tree, and watchdog arming for the earliest packet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_etf.c -->
