# Research Group: subset-b-006271

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_ets.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_ets.c

## Purpose
`sch_ets.c` implements the Enhanced Transmission Selection qdisc. It is classful, but classes are controlled as a fixed band set rather than as freely addable/removable children. The scheduler combines strict-priority service for the first `nstrict` bands with DRR-like bandwidth sharing for the remaining ETS bands, matching the 802.1Qaz traffic-selection model.

## Important APIs, Types, And Functions
The qdisc state is `struct ets_sched`: active DRR list, classifier block/list, band counts, priority map, and fixed `classes[TCQ_ETS_MAX_BANDS]`. Each `struct ets_class` owns a child qdisc, DRR `quantum`/`deficit`, active-list node, and stats storage. `ets_qdisc_ops` registers qdisc id `ets`; `ets_class_ops` exposes class change/graft/leaf/find/walk/filter binding/stat dump callbacks. Key packet-path functions are `ets_classify()`, `ets_qdisc_enqueue()`, and `ets_qdisc_dequeue()`. Configuration is parsed by `ets_qdisc_change()`, `ets_qdisc_priomap_parse()`, `ets_qdisc_quanta_parse()`, and `ets_class_change()`.

## Control Flow
Initialization requires netlink options, creates the classifier block with `tcf_block_get()`, initializes all active-list nodes, then delegates to `ets_qdisc_change()`. Change validates `nbands`, `nstrict`, priomap, and quanta, preallocates new child `pfifo` qdiscs before taking the tree lock, then commits band counts, strict/shared transitions, maps, quanta, and child qdiscs. Enqueue classifies by major handle, external filters, or `skb->priority` through `prio2band`; successful child enqueue activates non-strict classes with deficit initialized to quantum. Dequeue first scans strict bands in order. Only when strict queues are empty does it serve the `active` list by DRR: peek head, compare packet length to deficit, dequeue if affordable, otherwise add quantum and rotate the class.

## State And Persistence
State is in-memory qdisc/class state only. Persistent user-visible configuration is dumped over netlink: band count, strict count, shared-band quanta, and full priority map. Backlog and queue length are mirrored at the parent qdisc while each child maintains packet storage. Shared classes persist on `q->active` only while their child has packets. `READ_ONCE()`/`WRITE_ONCE()` protect values reported concurrently with dumps.

## Dependencies And Integration Points
ETS depends on the generic qdisc core, child `pfifo`, classifier actions (`tcf_classify`, `tcf_block`), netlink policy parsing, generic stats, and optional device offload through `ndo_setup_tc(TC_SETUP_QDISC_ETS)`. Grafting uses `qdisc_replace()` and `qdisc_offload_graft_helper()`. The classifier block is rooted at the qdisc rather than individual classes.

## Risks
The strict-band scan can starve shared bands if strict traffic is persistent. DRR correctness depends on child `peek()` behavior; non-work-conserving children can trigger `qdisc_warn_nonwc()`. Changing `nstrict` must correctly move classes into or out of the active list. Hardware offload weight conversion uses integer percentages derived from quanta, so small quanta combinations can lose precision. Fine-grained class addition is intentionally rejected; callers expecting generic classful behavior must use qdisc change.

## Test Signals
Exercise netlink rejection for missing/invalid `nbands`, `nstrict > nbands`, zero quantum, too many priomap/quanta entries, and strict-class quantum changes. Packet tests should verify strict priority precedence, DRR rotation and deficit refill, active-list removal on empty children, classification by priority/classid/filter, default band fallback, and behavior when shrinking bands with queued packets. Offload-capable device tests should observe replace/graft/destroy/stats commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_ets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_fifo.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_fifo.c

## Purpose
`sch_fifo.c` provides the simple packet-count FIFO (`pfifo`), byte-count FIFO (`bfifo`), and packet FIFO with head-drop-on-full (`pfifo_head_drop`) qdiscs. It also exports helpers used by other schedulers to create or resize embedded FIFO children.

## Important APIs, Types, And Functions
The qdisc ops are `pfifo_qdisc_ops`, `bfifo_qdisc_ops`, and `pfifo_head_drop_qdisc_ops`. Packet paths are `pfifo_enqueue()`, `bfifo_enqueue()`, and `pfifo_tail_enqueue()`, all paired with generic head dequeue/peek. Configuration/lifecycle functions include `__fifo_init()`, `fifo_init()`, `fifo_hd_init()`, `fifo_dump()`, and `fifo_destroy()`. Exported helpers `fifo_set_limit()` and `fifo_create_dflt()` are used by classful qdiscs that embed FIFO leaves.

## Control Flow
`__fifo_init()` sets `sch->limit` from user `tc_fifo_qopt` or defaults to device `tx_queue_len` for packets and `tx_queue_len * mtu` for bytes. It toggles `TCQ_F_CAN_BYPASS` when the limit can hold at least one packet/MTU. `pfifo_enqueue()` accepts while `q.qlen < limit`; `bfifo_enqueue()` accepts while `backlog + packet_len <= limit`; otherwise both drop the incoming skb. `pfifo_tail_enqueue()` drops immediately for limit zero, appends when not full, and on a full queue drops the current head then appends the new packet, returning `NET_XMIT_CN`.

## State And Persistence
There is no private qdisc state. The limit lives in `sch->limit`, packets live in the generic qdisc queue, and stats live in generic qdisc stats. Dump emits the `tc_fifo_qopt` limit. Head-drop adjusts parent backlog with `qdisc_tree_reduce_backlog()` after replacing the head.

## Dependencies And Integration Points
The file uses generic qdisc queue helpers, netlink attributes, `psched_mtu()`, and optional hardware offload through `ndo_setup_tc(TC_SETUP_QDISC_FIFO)` for `pfifo` and `bfifo`. `pfifo_qdisc_ops` and `bfifo_qdisc_ops` are exported for other schedulers to instantiate default children. `fifo_set_limit()` deliberately detects FIFO qdiscs by ops id string shape.

## Risks
`fifo_set_limit()` uses a historical id-string heuristic and should not be generalized without care. Byte FIFO default limit depends on MTU and can surprise callers expecting packet semantics. Head-drop returns congestion notification even though the new packet is queued, so parent accounting must remain precise. Offload init/destroy/stats are absent for `pfifo_head_drop`.

## Test Signals
Test packet and byte limits at exactly full and one byte/packet over. Validate zero-limit behavior, head-drop replacement ordering, `NET_XMIT_CN` return from head drop, bypass flag toggling for small limits, dump/change round trips, `fifo_create_dflt()` failure cleanup, and offload replace/destroy/stats calls for supported FIFO variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_fifo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_fq.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_fq.c

## Purpose
`sch_fq.c` implements the Fair Queue qdisc with per-flow pacing. It is optimized for locally generated traffic where `skb->sk` identifies flows, and it enforces socket/qdisc pacing rates, EDT timestamps, per-flow packet limits, priority bands, and watchdog-based delayed transmission.

## Important APIs, Types, And Functions
`struct fq_sched_data` holds read-mostly configuration, per-band new/old flow queues, the internal fast path flow, flow hash-tree roots, delayed-flow RB tree, watchdog, counters, and statistics. `struct fq_flow` stores per-flow skb queues, timestamp RB tree, socket identity, credit, band, and delayed-tree state. Key functions are `fq_classify()`, `fq_enqueue()`, `fq_dequeue()`, `fq_check_throttled()`, `fq_flow_set_throttled()`, `fq_resize()`, `fq_change()`, `fq_dump()`, and `fq_dump_stats()`.

## Control Flow
Enqueue maps `skb->priority` through a compressed 2-bit priomap to a band, enforces per-band qdisc packet limit, computes `time_to_send` from `skb->tstamp` or current time, and drops or caps packets beyond the configured horizon. `fq_classify()` uses socket pointer identity when possible, hashes orphan/listener/TIME_WAIT-like traffic, may select the internal fast path flow, and otherwise looks up/allocates a `fq_flow` in an RB tree bucket with garbage collection of old detached flows. Dequeue serves the internal fast path first, unthrottles delayed flows whose pacing time has arrived, then iterates weighted bands and each band’s new/old flow lists by deficit. Packets not yet sendable are moved into the delayed RB tree and a qdisc watchdog is scheduled for the earliest delayed time.

## State And Persistence
All operational state is volatile: dynamically allocated `fq_flow` objects in hash buckets, detached flow ages for GC, per-band credits and packet counts, delayed RB-tree nodes, and watchdog state. User-visible configuration is retained in `sch->limit` and fields such as `flow_plimit`, `quantum`, `initial_quantum`, `flow_max_rate`, `horizon`, `offload_horizon`, and priomap/weights, then dumped over netlink. A module-level kmem cache `fq_flow_cachep` persists for the module lifetime.

## Dependencies And Integration Points
FQ integrates with socket pacing (`sk_pacing_rate`, `sk_max_pacing_rate`, `sk_pacing_status`), skb hashes/timestamps, qdisc watchdogs, generic stats and backlog accounting, netlink policies, TCP state helpers, and device `max_pacing_offload_horizon`. It uses `qdisc_peek_dequeued` for qdisc ops peek and `qdisc_dequeue_internal()` when shrinking limits.

## Risks
Flow identity relies on socket pointer lifetime plus `sk_hash` checks; reuse must refill credits and unthrottle stale state. Timestamp ordering is split between a FIFO list and RB tree, so incorrect `time_to_send` handling can reorder packets. Fast path must preserve ordering when delayed flows become eligible. Rate calculations clamp long delays and update `time_next_packet`; low rates force credit exhaustion. Reconfiguration unlocks around `fq_resize()`, so fields changed before resize must tolerate partial `-ENOMEM`. Horizon/offload horizon misconfiguration affects drops versus caps.

## Test Signals
Cover socket and orphan classification, flow allocation failure fallback to internal queue, flow packet limits, band packet limits and weighted band service, delayed-flow watchdog scheduling, offload horizon validation, horizon drop versus cap, CE marking after threshold, low-rate pacing behavior, `fq_resize()` rehash/GC, qdisc limit shrink drops, priomap and weight validation, and stats counters for throttled, GC, fastpath, band drops, horizon drops/caps, allocation errors, and packet-too-long clamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_fq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_fq_codel.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_fq_codel.c

## Purpose
`sch_fq_codel.c` implements Fair Queue CoDel: a stochastic fixed-flow-table fair queue whose per-flow queues are managed by CoDel active queue management. It prioritizes newly active flows over old flows and bounds both packet count and memory usage.

## Important APIs, Types, And Functions
`struct fq_codel_sched_data` owns classifier state, fixed flow array, per-flow backlog array, quantum, packet/memory/drop limits, CoDel params/stats, memory counters, and new/old flow lists. `struct fq_codel_flow` stores an skb FIFO, DRR deficit, list node, and CoDel variables. Main functions are `fq_codel_classify()`, `fq_codel_enqueue()`, `fq_codel_drop()`, `fq_codel_dequeue()`, `dequeue_func()`, `drop_func()`, `fq_codel_change()`, `fq_codel_init()`, and class stat dump/walk functions.

## Control Flow
Classification accepts explicit classids under the qdisc handle, otherwise uses an external filter if present, then falls back to `skb_get_hash()` scaled to `flows_cnt`. Enqueue records CoDel enqueue time, appends to the selected flow, activates new flows with initial deficit, updates per-flow backlog and memory usage, then checks `sch->limit` and `memory_limit`. If over limit, `fq_codel_drop()` linearly finds the fattest flow and drops up to `drop_batch_size` packets or half that flow’s backlog. Dequeue selects `new_flows` before `old_flows`, replenishes deficit by quantum, calls `codel_dequeue()` with qdisc-specific callbacks, moves empty flows off the list, and propagates CoDel drop accounting to parents.

## State And Persistence
The flow table and backlog array are allocated once during init; flow count cannot change after allocation. Runtime state includes per-flow skb lists, CoDel variables, memory usage, drop counters, and new/old flow chains. Netlink dump exposes CoDel target/interval/ECN/CE threshold, qdisc limit, flows, quantum, batch size, and memory limit. Per-class stats expose individual flow backlog, CoDel delay/drop state, and deficit.

## Dependencies And Integration Points
The qdisc depends on `net/codel*.h`, classifier blocks, generic qdisc class ops, netlink policy parsing, `kvzalloc_objs()`, and generic queue/stat helpers. It exposes a class-like view over hash slots for `tc` stats and filters but has no child qdiscs.

## Risks
Hash collisions combine unrelated flows. `fq_codel_drop()` is intentionally linear over all flows; large `flows_cnt` raises CPU cost in overload. Flow count is immutable after allocation and change rejects late flow-count changes. Memory accounting uses `skb->truesize` saved in CoDel skb CB, so all dequeue/drop paths must subtract it exactly. Classifier actions that steal/drop packets must keep qdisc drop stats consistent.

## Test Signals
Test hash and explicit classid classification, external filter steal/shot paths, new-flow priority over old flows, deficit rollover, CoDel ECN/drop behavior, memory-limit drops, packet-limit drops, fattest-flow batch drop selection, limit shrink by `fq_codel_change()`, immutable flow count, class walk/stat dumps, reset clearing all flows and memory, and destroy freeing arrays and classifier block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_fq_codel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_fq_pie.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_fq_pie.c

## Purpose
`sch_fq_pie.c` implements Flow Queue PIE: a stochastic fixed-flow-table fair queue where each flow uses PIE active queue management. Drops or ECN marks occur on enqueue, while dequeues use new/old flow DRR scheduling.

## Important APIs, Types, And Functions
`struct fq_pie_sched_data` stores classifier block, fixed flow table, PIE params/stats, adaptive timer, memory/flow counters, quantum, and new/old flow lists. `struct fq_pie_flow` stores per-flow PIE vars, deficit, backlog, qlen, list node, and skb FIFO. Main functions are `fq_pie_classify()`, `fq_pie_qdisc_enqueue()`, `fq_pie_qdisc_dequeue()`, `fq_pie_change()`, `fq_pie_timer()`, `fq_pie_init()`, `fq_pie_dump()`, and `fq_pie_dump_stats()`.

## Control Flow
Classification mirrors FQ-CoDel: explicit classid, optional external classifier, or hash fallback. Enqueue checks qdisc packet limit and memory limit, invokes `pie_drop_early()` with the selected flow’s PIE vars and backlog, optionally ECN-marks if PIE probability is below `ecn_prob`, then enqueues and activates the flow if accepted. Dequeue serves new flows before old flows, replenishes deficit by quantum, removes a head packet, updates qdisc and flow backlog/qlen/memory, and calls `pie_process_dequeue()`. The adaptive timer locks the root qdisc and updates PIE probability for up to 2048 flows per tick, rescheduling after a full pass.

## State And Persistence
The fixed flow table is allocated at init. PIE variables are per flow and reset with the qdisc. Runtime counters include memory usage, overmemory, packets in, drops, ECN marks, and new flow count. Configuration persists in memory via `pie_params`, `sch->limit`, `flows_cnt`, `quantum`, `memory_limit`, and `ecn_prob`, and is emitted by netlink dump.

## Dependencies And Integration Points
FQ-PIE depends on `net/pie.h`, classifier blocks, netlink validation, qdisc timers, qdisc root locking, `kvzalloc_objs()`, and generic queue/stat helpers. Unlike FQ-CoDel, it has no class ops for per-flow tc class stats.

## Risks
`flows_cnt` cannot change after allocation. The memory-limit check compares current usage against `memory_limit + skb->truesize`, which should be tested because it is easy to misread as post-enqueue accounting. The timer’s bounded 2048-flow loop spreads CPU work but means probability updates for large flow tables occur over multiple invocations. Timer teardown must set `tupdate` to zero and delete synchronously to avoid use-after-free. Reset clears flow queues/vars but does not explicitly zero all qdisc counters.

## Test Signals
Validate flow classification, classifier action paths, packet-limit and memory-limit drops, PIE early drop versus ECN mark paths, ECN probability threshold, new/old flow service and deficit movement, timer probability update cursor wrap, flow-count immutability, limit shrink drops in change, reset/destroy timer behavior, dump round trips, and stats for packets, overlimit, overmemory, drops, ECN marks, memory usage, and flow-list lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_fq_pie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_frag.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_frag.c

## Purpose
`sch_frag.c` provides `sch_frag_xmit_hook()`, a helper for qdisc/action transmit paths that need to fragment packets when `tc_skb_cb(skb)->mru` is set and the skb exceeds that MRU plus link header length.

## Important APIs, Types, And Functions
The exported API is `sch_frag_xmit_hook(struct sk_buff *skb, int (*xmit)(struct sk_buff *skb))`. Per-CPU scratch state is `struct sch_frag_data`, storing original dst ref, qdisc skb cb, VLAN state, inner protocol, L2 header copy, and the original xmit callback. Internal helpers are `sch_fragment()`, `sch_frag_prepare_frag()`, `sch_frag_xmit()`, and `sch_frag_dst_get_mtu()`.

## Control Flow
The hook sends directly through `xmit` unless MRU is nonzero and packet length exceeds MRU plus hard header length. Fragmentation rejects unexpectedly long L2 headers, then handles IPv4 with a temporary `rtable` and `ip_do_fragment()` or IPv6 with a temporary `rt6_info` and `ip6_fragment()`. Before fragmenting it copies L2/qdisc/VLAN/protocol state into per-CPU storage, pulls the L2 header, resets IP control block fields, installs a temporary dst whose MTU callback returns device MTU, and sets `frag_max_size` to MRU. Each produced fragment enters `sch_frag_xmit()`, which restores dst, qdisc cb, VLAN tag state, inner protocol, and MAC header before calling the original xmit callback.

## State And Persistence
State is per-CPU and protected by `local_lock_nested_bh()`. It lives only during the fragmentation call chain. The original dst reference is restored/dropped after fragmentation via `refdst_drop(orig_dst)`. There is no netlink state or qdisc registration in this file.

## Dependencies And Integration Points
The file integrates with IPv4/IPv6 fragmentation APIs, dst ops, VLAN acceleration helpers, qdisc skb control blocks, tc MRU metadata, and the caller’s transmit callback. It is exported GPL-only for scheduler/action users.

## Risks
The per-CPU scratch area assumes fragmentation callbacks occur under the local lock; nested misuse could corrupt state. Non-IP packets over MRU are dropped with a rate-limited warning. L2 headers longer than `VLAN_ETH_HLEN` cannot be reconstructed and are dropped. Correct restoration of qdisc cb and VLAN metadata is critical because fragments re-enter downstream transmit paths. Temporary dst use and `refdst_drop()` must remain balanced.

## Test Signals
Test direct transmit when MRU is zero or packet fits, IPv4 and IPv6 fragmentation when over MRU, non-IP drop path, long-L2-header drop path, VLAN-tag preservation, qdisc skb cb preservation, MAC header reconstruction, checksum adjustment after `skb_push()`, and callback error propagation from fragment xmit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_frag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_generic.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_generic.c

## Purpose
`sch_generic.c` is the generic qdisc and device scheduler core. It provides the default qdisc selection, qdisc allocation/destruction, transmit run loop, requeue handling, carrier/watchdog integration, default `noop`, `noqueue`, and `pfifo_fast` qdiscs, device activation/deactivation, rate precompute helpers, and mini-qdisc RCU swap helpers.

## Important APIs, Types, And Functions
Exported symbols include `default_qdisc_ops`, `noop_qdisc`, `pfifo_fast_ops`, `qdisc_alloc()`, `qdisc_create_dflt()`, `qdisc_reset()`, `qdisc_put()`, `qdisc_put_unlocked()`, `dev_graft_qdisc()`, `dev_activate()`, `dev_deactivate()`, `mq_change_real_num_tx()`, `dev_qdisc_change_tx_queue_len()`, `dev_init_scheduler()`, `dev_shutdown()`, `psched_ratecfg_precompute()`, `psched_ppscfg_precompute()`, and `mini_qdisc_pair_*()`. The central transmit path is `__qdisc_run()` -> `qdisc_restart()` -> `dequeue_skb()` -> `sch_direct_xmit()`.

## Control Flow
`dequeue_skb()` first handles requeued GSO packets, stopped single-TX queues, and bad-TXQ requeues, then calls the qdisc’s dequeue function and may bulk-dequeue compatible packets. `sch_direct_xmit()` drops the qdisc lock, validates skb lists, takes the driver TX lock, calls `dev_hard_start_xmit()`, and requeues on busy/incomplete transmit. `__qdisc_run()` repeats until queue empty/throttled or `dev_tx_weight` quota is exhausted, then reschedules as needed. Device activation attaches default qdiscs if still noop, transitions sleeping qdiscs to active qdiscs, and starts the watchdog. Deactivation swaps active qdiscs to noop, waits for in-flight enqueue/run activity, and optionally resets.

## State And Persistence
Core state is in `struct Qdisc`, `struct netdev_queue`, and `struct net_device`: qdisc pointers under RCU, qdisc refcounts, busy state bits, `gso_skb`, `skb_bad_txq`, qstats/bstats, watchdog timer, and carrier counters. `pfifo_fast` private state is three `skb_array` rings sized to `tx_queue_len`. There is no disk persistence; all state is kernel runtime state exposed through netlink/stat APIs elsewhere.

## Dependencies And Integration Points
This file is the integration point between qdiscs and netdevice drivers. It uses RCU, rtnl locking, qdisc locks, hard TX locks, skb validation, XFRM offload, BPF module refs, tracepoints, linkwatch, qdisc hash support, per-CPU stats, and qdisc watchdogs. It initializes default qdiscs for normal, noqueue, CAN, and multiqueue devices.

## Risks
The transmit path relies on strict lock ordering: qdisc root lock and driver TX lock must not be held in the wrong combination. Requeue accounting for `gso_skb` and `skb_bad_txq` must keep qlen/backlog correct for both normal and per-CPU stats qdiscs. `qdisc_maybe_clear_missed()` uses memory barriers to avoid missed wakeups. Device deactivation waits by polling busy qdiscs, so state-bit bugs can hang shutdown. `pfifo_fast` is lockless/per-CPU-stat capable and its ring allocation/destruction must tolerate partial init failure.

## Test Signals
Exercise qdisc allocation failure paths, default qdisc fallback to noqueue, multiqueue default attach, `pfifo_fast` priority ordering and ring resize, GSO and bad-TXQ requeue accounting, driver busy requeue, bulk dequeue queue-mapping constraints, watchdog timeout and carrier on/off paths, device deactivate/reactivate with reset, qdisc refcount destruction via RCU, rate precompute edge cases, and mini-qdisc RCU swap under concurrent readers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_gred.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_gred.c

## Purpose
`sch_gred.c` implements the Generic Random Early Detection qdisc. It multiplexes packets into virtual queues selected by `skb->tc_index`, each with RED parameters, and supports RIO and WRED modes plus optional hardware offload.

## Important APIs, Types, And Functions
`struct gred_sched` stores the virtual queue table, global flags, default DP, global RED flags, shared WRED variables, and offload scratch. `struct gred_sched_data` stores per-VQ limit, DP, RED flags, byte/packet counters, backlog, priority, RED params/vars/stats. Packet functions are `gred_enqueue()`, `gred_dequeue()`, and `gred_reset()`. Configuration functions include `gred_change_table_def()`, `gred_change_vq()`, `gred_change()`, VQ-list validation/apply helpers, `gred_init()`, `gred_dump()`, and `gred_destroy()`.

## Control Flow
Initialization accepts only table-level options, sets qdisc limit, allocates offload scratch if possible, then configures DP count/default and mode. VQ configuration validates RED parameters and either creates or updates one `gred_sched_data`. Enqueue chooses DP from low bits of `skb->tc_index`, falls back to default DP, or passes through unconfigured traffic if no default VQ exists and the qdisc limit permits. It computes RED average using either per-VQ backlog or shared WRED backlog, includes lower-priority qavg in RIO mode, then applies RED action: no mark, probabilistic ECN/drop, or forced ECN/drop. Accepted packets are queued in the parent FIFO queue and per-VQ backlog is updated. Dequeue removes from the shared FIFO and adjusts the selected VQ backlog/idle state.

## State And Persistence
State is volatile per-qdisc VQ state plus shared WRED RED vars. Netlink dump emits table-level options, legacy all-in-one VQ parameter records, structured VQ list entries, RED flags, and counters. Hardware stats dump may add driver-provided bstats/qstats/xstats into software state under the tree lock.

## Dependencies And Integration Points
GRED depends on `net/red.h`, netlink nested attributes, tc index classification, generic qdisc FIFO storage, ECN helpers, optional `ndo_setup_tc(TC_SETUP_QDISC_GRED)`, and qdisc offload stats helpers. It uses qdisc-level `sch->limit` as the hard global queue length/default pass-through bound.

## Risks
Misconfigured or absent default VQs can intentionally pass traffic through, which differs from strict classifier failure dropping. WRED mode shares qavg/idle state across VQs with equal priorities, while RIO adds lower-priority qavgs; mode transitions must keep flags coherent. Per-qdisc RED flags and per-VQ flags are mutually constrained. Offload stats are additive even if driver stat dump returns failure, which can surprise tests. Backlog correction depends on `tc_index` surviving requeue/dequeue.

## Test Signals
Cover table validation for zero/too many DPs and invalid default DP, VQ RED parameter validation, per-qdisc versus per-VQ RED flag conflicts, unconfigured DP fallback/pass-through, RIO/WRED mode selection, probabilistic and forced ECN/drop paths, per-VQ limit drops, dequeue backlog/idle updates, shrinking DPs destroying shadowed VQs, legacy and structured dump content, offload replace/destroy/stats commands, and hardware stat merge behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_gred.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_hfsc.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_hfsc.c

## Purpose
`sch_hfsc.c` implements the Hierarchical Fair Service Curve scheduler. It supports class hierarchies with real-time service curves, fair link-sharing curves, and optional upper-limit curves, selecting packets by deadline eligibility first and link-sharing virtual time otherwise.

## Important APIs, Types, And Functions
`struct hfsc_sched` stores default class id, root class, class hash, global eligible tree, and watchdog. `struct hfsc_class` stores class stats, filter block/list, hierarchy links, child qdisc, eligible/vt/cf tree nodes, cumulative work, service-curve runtime state, flags, and activity counters. Core math helpers include `sc2isc()`, `rtsc_init()`, `rtsc_x2y()`, `rtsc_y2x()`, and `rtsc_min()`. Scheduling helpers include eligible-tree, virtual-time-tree, and fit-time-tree operations, `init_ed()`, `update_ed()`, `init_vf()`, and `update_vf()`. Packet and class ops are `hfsc_enqueue()`, `hfsc_dequeue()`, `hfsc_change_class()`, `hfsc_delete_class()`, `hfsc_graft_class()`, and filter binding/dump helpers.

## Control Flow
Qdisc init creates a class hash, classifier block on root, root class, and a default root `pfifo`. Class change creates or updates classes from netlink service curves, upgrades misconfigured realtime-only parents to fair service when needed, attaches child qdiscs, and maintains hierarchy levels. Enqueue classifies by skb priority, nested class filters, or default class, enqueues into a leaf child qdisc, updates parent backlog, and if the class was inactive initializes real-time eligible/deadline state and/or virtual/fit state. Dequeue first chooses the eligible class with minimum deadline at current time. If no realtime class is eligible, it chooses the leaf with minimum virtual time whose fit time permits service; otherwise it schedules the watchdog for the next eligible/fit time and returns NULL.

## State And Persistence
Runtime state includes class hierarchy, child qdiscs, class hash refs, eligible RB tree, per-parent virtual-time and fit-time RB trees, watchdog, service curve runtime positions, cumulative realtime/fair work, and per-class stats/estimators. Netlink persistence is the qdisc default class and each class’s service curves. Reset clears work counters, trees, qdiscs, and runtime curves while preserving configured curves/classes.

## Dependencies And Integration Points
HFSC integrates with the generic classful qdisc API, classifier blocks per class/root, child qdisc grafting, generic estimators, qdisc watchdogs, netlink service-curve attributes, class hash utilities, and `pfifo` defaults. It relies on `psched_get_time()` and scaled service-curve math to avoid expensive divides on the fast path.

## Risks
The service-curve math is delicate: overflow avoidance, convex versus concave curve handling, and inverse slope infinity must remain correct. Tree membership must match queue activity; missed `eltree_remove()`, `vttree_remove()`, or fit-time updates can stall or misorder service. `peek()` is used to compute next packet length, so non-work-conserving child qdiscs can perturb deadline updates. Class deletion must reject active/in-use/root classes. Realtime service can dominate link-sharing if configured aggressively.

## Test Signals
Validate service-curve conversion and dump round trips, class creation/update/delete errors, parent/child level maintenance, nested classifier downward-only selection, default class fallback and failure drop, realtime deadline selection, link-sharing selection with upper-limit fit times, watchdog scheduling when nothing fits, qlen notify removing inactive class state, grafting leaf children, reset preserving configuration while clearing runtime state, and class stats for work/rtwork/period/level.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_hfsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_hhf.c -->
# sources/distributed-fs/ceph-client/net/sched/sch_hhf.c

## Purpose
`sch_hhf.c` implements the Heavy-Hitter Filter qdisc. It separates traffic into heavy-hitter and non-heavy-hitter buckets using a multi-stage approximate counter filter plus an exact heavy-hitter table, then serves the buckets with weighted deficit round robin that favors non-heavy-hitter traffic.

## Important APIs, Types, And Functions
`struct hhf_sched_data` owns two WDRR buckets, hash perturbation key, quantum, heavy-hitter flow table, approximate filter arrays/valid bits, counters, bucket lists, and configurable thresholds/timeouts. `struct hh_flow_state` stores exact heavy-hitter hash and last-hit timestamp. Key functions are `hhf_classify()`, `seek_list()`, `alloc_new_hh()`, `hhf_enqueue()`, `hhf_drop()`, `hhf_dequeue()`, `hhf_change()`, `hhf_init()`, `hhf_dump()`, and `hhf_dump_stats()`.

## Control Flow
Classification periodically resets approximate filter valid bits, hashes the packet with a random perturbation, checks the exact heavy-hitter table, and if absent indexes four counter arrays using three 10-bit hash chunks plus an XOR-derived fourth. If all counters exceed `hhf_admit_bytes`, it allocates or reuses exact heavy-hitter state and classifies into the heavy-hitter bucket without incrementing filter counters. Otherwise it conservatively updates counters to the minimum candidate value and classifies as non-heavy-hitter. Enqueue appends to the selected bucket, activates heavy hitters on old bucket list with weight 1 and non-heavy hitters on new bucket list with configurable higher weight, and drops from heavy hitters first when qdisc limit is exceeded. Dequeue serves new buckets before old buckets by WDRR deficit.

## State And Persistence
Runtime state includes the fixed exact table of list heads, dynamically allocated heavy-hitter flow entries, four counter arrays, four valid-bit arrays, two skb buckets, activity lists, and stats counters. Configuration persists in qdisc memory: backlog limit, quantum, max HH flows, reset/admit/evict parameters, and non-HH weight. Dump emits these parameters and xstats emit HH/drop counters.

## Dependencies And Integration Points
HHF uses skb flow hashing with `siphash_key_t`, generic qdisc queue/stat helpers, netlink policies, jiffies-based timing, `kvcalloc`/`kvzalloc` allocation, and qdisc internal dequeue when shrinking limits. It has no classifier block and no child qdiscs.

## Risks
The approximate filter has false positives by design, though not false negatives for sustained heavy hitters under the algorithm assumptions. Resetting valid bits rather than counters reduces cost but makes valid-bit correctness essential. Heavy-hitter table allocation is capped; when full, new heavy hitters fall back to non-HH classification and increment overlimit stats. Limit drops always target heavy-hitter bucket first if possible, so accounting must handle cases where the enqueued packet’s bucket differs from the dropped bucket. `hhf_reset()` drains through dequeue, so stats/backlog side effects should be expected.

## Test Signals
Test filter admission threshold, conservative counter update, periodic valid-bit reset, exact table hit and eviction, HH flow cap behavior, WDRR weight preference for non-HH bucket, heavy-first overlimit drops, return code difference when dropping from same versus other bucket, netlink validation for zero/overflow non-HH quantum product, limit shrink drops, dump/xstats counters, allocation failure cleanup in init, and destroy freeing flow table/filter arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/sch_hhf.c -->
