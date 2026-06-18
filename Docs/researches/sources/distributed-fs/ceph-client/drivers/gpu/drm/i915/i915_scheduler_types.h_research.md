<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scheduler_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scheduler_types.h

## Purpose
Defines scheduler data structures shared between i915 request objects and submission engines.

## Important APIs, types, and functions
- `struct i915_sched_attr` carries execution priority.
- `struct i915_sched_node` tracks signalers, waiters, queue membership, current attributes, scheduler flags, and semaphore engine mask.
- `struct i915_dependency` links waiter and signaler nodes and carries allocation/external/weak flags.
- `for_each_waiter()` and `for_each_signaler()` provide lockless/RCU dependency iteration.
- `struct i915_sched_engine` holds backend queue state, priolists, locks, tasklet, private data, lifecycle hooks, and priority/preemption hooks.

## Control flow
The file is declarative, but its comments define scheduler semantics: the scheduler is primarily passive DAG tracking plus priority-ordered ready queues, with backend active elements handling timeslicing/preemption decisions.

## State and persistence
Scheduler nodes are embedded in requests and live until request retirement. Dependencies live until removed by node finalization or dependency completion. Scheduler engines persist with backend lifetime and own the RB-tree priority queue and request/hold lists.

## Dependencies and integration points
Depends on Intel engine masks and priolist types. Integrated with `i915_request`, scheduler implementation, execlists/GuC backends, and debug traversals.

## Risks
Dependency list comments describe fundamental invariants: signalers precede waiters, dependencies form a DAG, and list walkers may be lockless/RCU. Adding fields or changing flags requires updates in scheduler propagation, request dependency setup, and backend priority handling.

## Test signals
Priority propagation tests, DAG traversal/debug output, backend preemption behavior, RCU list walking under stress, and lockdep/KCSAN coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scheduler_types.h -->
