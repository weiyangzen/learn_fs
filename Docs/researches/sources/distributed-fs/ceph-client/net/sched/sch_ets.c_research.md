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
