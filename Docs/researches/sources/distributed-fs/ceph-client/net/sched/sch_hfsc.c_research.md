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
