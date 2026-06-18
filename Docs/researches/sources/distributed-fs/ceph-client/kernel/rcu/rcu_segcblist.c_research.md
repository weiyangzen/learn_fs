# sources/distributed-fs/ceph-client/kernel/rcu/rcu_segcblist.c

## Purpose
`rcu_segcblist.c` implements simple and segmented RCU callback lists. Segmented lists divide callbacks into done, waiting, next-ready, and next segments so RCU can advance callbacks as grace periods start and finish without relinking each callback individually.

## Important APIs, types, and functions
Simple-list APIs are `rcu_cblist_init()`, `rcu_cblist_enqueue()`, `rcu_cblist_flush_enqueue()`, and `rcu_cblist_dequeue()`. Segmented-list APIs include length helpers, `rcu_segcblist_init()`, `rcu_segcblist_disable()`, `rcu_segcblist_ready_cbs()`, `rcu_segcblist_pend_cbs()`, `rcu_segcblist_first_cb()`, `rcu_segcblist_first_pend_cb()`, `rcu_segcblist_nextgp()`, `rcu_segcblist_enqueue()`, `rcu_segcblist_entrain()`, extract/insert helpers, `rcu_segcblist_advance()`, `rcu_segcblist_accelerate()`, and `rcu_segcblist_merge()`.

## Control flow
Normal callback enqueue increments total and next-segment lengths, appends the callback at `RCU_NEXT_TAIL`, and updates tail pointers. When a grace period advances, `rcu_segcblist_advance()` moves segments whose `gp_seq[]` is complete into `RCU_DONE_TAIL`, compacts remaining segment pointers, and preserves pending sequence labels. `rcu_segcblist_accelerate()` merges later segments into an earlier GP sequence when better GP information is available. Extract/insert helpers move done or pending callbacks to temporary `rcu_cblist`s for invocation, migration, or CPU hotplug merging.

## State and persistence behavior
State is stored in `struct rcu_segcblist`: callback head, segment tail pointers, per-segment lengths, total length, flags, and GP sequence labels. Total length may temporarily disagree with actual linked callbacks while invocation batches are extracted; comments explicitly direct callers to use count-based checks when needed.

## Dependencies and integration points
The code depends on callback-list definitions from public/internal RCU headers, `CONFIG_RCU_NOCB_CPU` atomic length handling, CPU hotplug locking for merge, memory barriers required by `rcu_barrier()`, and RCU implementations that post, accelerate, invoke, and migrate callbacks.

## Risks and invariants
Length transitions between zero and nonzero are barrier-sensitive because `rcu_barrier()` samples lengths locklessly and must not miss callbacks before module unload. Tail pointers must preserve segment ordering and emptiness semantics. `rcu_segcblist_entrain()` is only for barrier-like callbacks and waits for prior callbacks, not necessarily a grace period. Merging pending callbacks makes them restart GP waiting, so callers should advance/accelerate first.

## Test signals
Signals include RCU torture callback flooding, `rcu_barrier()` under module unload races, NOCB offload tests, CPU hotplug callback migration, segment length consistency checks, and KCSAN/lockdep around lockless length sampling.
