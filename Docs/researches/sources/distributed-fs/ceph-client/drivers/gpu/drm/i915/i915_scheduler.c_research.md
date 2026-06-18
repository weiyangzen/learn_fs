<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scheduler.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scheduler.c

## Purpose
Implements i915 scheduler DAG and priority-queue support shared by submission backends.

## Important APIs, types, and functions
- `i915_sched_lookup_priolist()` finds or allocates a priority list in an RB tree.
- `i915_schedule()` and `__i915_schedule()` propagate priority changes through dependency chains.
- `i915_sched_node_init()`, `i915_sched_node_reinit()`, `i915_sched_node_add_dependency()`, `__i915_sched_node_add_dependency()`, and `i915_sched_node_fini()` manage scheduler node dependency lists.
- `i915_request_show_with_schedule()` prints a request and unsatisfied cross-timeline dependencies.
- `i915_sched_engine_create()`, get/put helpers, and module init/exit manage scheduler-engine and slab state.

## Control flow
Priority scheduling starts with a request node and builds a flat DFS list of unsignaled dependencies instead of recursing on the kernel stack. It then walks dependencies in reverse order under the appropriate scheduler-engine lock, updates priorities, moves ready requests between priolists, invokes backend priority bump hooks, and kicks backend submission. Virtual engines are handled by repeatedly checking that the locked scheduler engine still matches the request's current engine.

Dependency addition publishes RCU-visible signaler/waiter links under a global schedule lock and propagates scheduler flags. Finalization removes both incoming and outgoing dependency links and frees allocated dependency records.

## State and persistence
Persistent scheduler state lives in each `i915_sched_node`, allocated `i915_dependency` records, `i915_priolist` RB-tree nodes, and `i915_sched_engine` queues/locks/hooks. Slab caches persist for dependency and priolist allocations.

## Dependencies and integration points
Depends on `i915_request` state predicates, DRM/i915 priorities, submission backend hooks, Linux RB trees, RCU list walking, tasklets, and lockdep. Integrated with request queueing, engine backends, priority inheritance, and debug request printers.

## Risks
The dependency graph must remain acyclic and lock ordering between global schedule lock and per-engine locks is delicate. Allocation failure in a non-normal priolist disables priority lists and falls back to FIFO behavior, which is intentional but can alter scheduling fairness. Virtual-engine `rq->engine` instability requires the relock loop.

## Test signals
Scheduler selftests, priority inheritance tests, virtual engine migration tests, stress with dependency chains, allocation-failure injection for priolist fallback, lockdep, and request debug output showing expected dependency ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scheduler.c -->
