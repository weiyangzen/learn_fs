# sources/distributed-fs/ceph-client/block/bfq-wf2q.c

## Purpose

`bfq-wf2q.c` implements BFQ's hierarchical Budget Worst-case Fair Weighted Fair Queueing scheduler. It manages virtual timestamps, active and idle service trees, entity activation/requeue/deactivation, group hierarchy propagation, queue selection, service accounting, and busy queue insertion/removal.

## Important APIs, Types, And Functions

Important functions include `bfq_entity_to_bfqq()`, `bfq_tot_busy_queues()`, `bfq_entity_of()`, `bfq_entity_service_tree()`, `bfq_ioprio_to_weight()`, `__bfq_entity_update_weight_prio()`, `bfq_bfqq_served()`, `bfq_bfqq_charge_time()`, `__bfq_deactivate_entity()`, `next_queue_may_preempt()`, `bfq_get_next_queue()`, `__bfq_bfqd_reset_in_service()`, `bfq_activate_bfqq()`, `bfq_deactivate_bfqq()`, `bfq_requeue_bfqq()`, `bfq_add_bfqq_busy()`, and `bfq_del_bfqq_busy()`.

Static helpers handle wrap-safe timestamp comparison (`bfq_gt()`), virtual-time deltas (`bfq_delta()`), finish timestamps (`bfq_calc_finish()`), active/idle rbtree insert/extract, `min_start` maintenance, eligible entity lookup, parent budget updates, and `next_in_service` refresh.

## Control Flow, State, And Persistence

Activation inserts a queue entity into the active service tree, taking a service reference and calculating `start`/`finish`. If an entity was idle, it is extracted from the idle tree and possibly backshifted. Requeueing recalculates timestamps after service or budget changes and repositions entities in active trees. Both activation and requeue operations propagate up the entity hierarchy until no parent scheduling change is needed.

`bfq_get_next_queue()` walks from the root scheduler down to a leaf using cached `next_in_service`, sets `in_service_entity` at every level, extracts entities that no longer qualify as next-service candidates, then refreshes next-service caches on the way back up. Deactivation calculates final finish time, removes active/idle membership, optionally keeps the entity idle for service guarantees, or forgets it and drops service references.

Service accounting via `bfq_bfqq_served()` advances queue and ancestor service, virtual time, and weight-raising counters. `bfq_bfqq_charge_time()` converts elapsed time into synthetic service for slow queues to preserve latency/throughput behavior.

## Dependencies And Integration Points

The file consumes `bfq-iosched.h` structures and calls external BFQ helpers for queue lifetime, weights-tree maintenance, cgroup stats, tracing, and group lookup. It integrates with dispatch through busy transitions: `bfq_add_bfqq_busy()` marks queues busy and activates them, while `bfq_del_bfqq_busy()` deactivates and may free queue-related state.

## Risks And Test Signals

The main risks are stale rb-tree derived fields, incorrect wraparound comparisons, and queue reference mistakes. `bfq_weights_tree_remove()` can free a queue and must remain last in removal paths. Hierarchical builds add risk through parent budgets, active entity counts, and approximated pending-group counters. Test with lockdep/KASAN under activation/deactivation storms, cgroup churn, expiration, soft-real-time workloads, multi-actuator dispatch, and fairness/latency benchmarks.
