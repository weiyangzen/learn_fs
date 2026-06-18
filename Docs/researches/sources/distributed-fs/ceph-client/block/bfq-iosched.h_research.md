# sources/distributed-fs/ceph-client/block/bfq-iosched.h

## Purpose

`bfq-iosched.h` is the private interface and state model for the BFQ block I/O scheduler. It defines BFQ's hierarchical B-WF2Q+ entities, per-process queues, per-device scheduler state, cgroup group state, accounting structures, state flags, and cross-file function prototypes used by BFQ dispatch, merge, cgroup, and fair-queueing implementation files.

## Important APIs, Types, And Functions

Key constants include `BFQ_IOPRIO_CLASSES`, `BFQ_MIN_WEIGHT`, `BFQ_MAX_WEIGHT`, `BFQ_WEIGHT_CONVERSION_COEFF`, `BFQ_SOFTRT_WEIGHT_FACTOR`, and `BFQ_MAX_ACTUATORS`.

Important types are `struct bfq_service_tree`, `struct bfq_sched_data`, `struct bfq_entity`, `struct bfq_queue`, `struct bfq_io_cq`, `struct bfq_data`, `struct bfq_group`, `struct bfq_group_data`, `struct bfqg_stats`, and `struct bfq_stat`. They model per-class rbtrees, cached next-service decisions, leaf and group schedulable entities, process queues, per-device scheduling state, blkcg integration, and policy statistics.

The header declares the internal B-WF2Q+ API implemented by `bfq-wf2q.c`, including `bfq_entity_to_bfqq()`, `bfq_entity_service_tree()`, `bfq_ioprio_to_weight()`, `__bfq_entity_update_weight_prio()`, `bfq_bfqq_served()`, `bfq_bfqq_charge_time()`, `bfq_get_next_queue()`, `bfq_activate_bfqq()`, `bfq_deactivate_bfqq()`, `bfq_requeue_bfqq()`, `bfq_add_bfqq_busy()`, and `bfq_del_bfqq_busy()`.

## Control Flow, State, And Persistence

BFQ is represented as a hierarchy of `bfq_entity` objects. Leaf entities are `bfq_queue` instances; non-leaf entities are `bfq_group` instances. `for_each_entity()` and `for_each_entity_safe()` traverse this hierarchy or collapse to one level without group scheduling. Active service trees are ordered by virtual finish time and cache `min_start` for eligibility lookup; idle trees preserve entities with future finish timestamps so short idle periods do not destroy service guarantees.

`bfq_queue` persists request trees/lists, budget state, dispatch count, request position, think-time data, burst membership, soft-real-time/weight-raising data, cooperative merge state, waker relationships, and actuator index. `bfq_iocq_bfqq_data` stores queue state across cooperative merges so split/recycle paths can restore weights, classification, timing, and injection limits.

## Dependencies And Integration Points

The header depends on block tracing, hrtimers, blkcg rwstat helpers, cgroup policy data, rbtrees, lists, request/bio types, and BFQ implementation files. Logging integrates with cgroup-aware or plain block trace paths depending on `CONFIG_BFQ_GROUP_IOSCHED`.

## Risks And Test Signals

Risk is concentrated in cached tree state and queue lifetime. `next_in_service`, `on_st_or_in_serv`, weight-change fields, group pending counters, merge/split saved state, and multi-actuator indexes must stay coherent. Build and runtime testing should cover BFQ with and without group scheduling/debug stats, cgroup migration, queue merge/split, multi-actuator dispatch, blktrace output, and fairness checks for weight ratios, idle-class timeout behavior, and soft-real-time boosting.
