# sources/distributed-fs/ceph/src/client/barrier.cc

## Purpose
`barrier.cc` implements write/commit barrier bookkeeping for client block synchronization, tracking outstanding write callback intervals and waiting for overlapping commits to finish.

## Important APIs, Types, and Functions
The local `C_Block_Sync` context records `Client*`, inode, interval, state, owning `Barrier*`, result pointer, and intrusive hook. `BarrierContext::write_nobarrier()`, `write_barrier()`, `commit_barrier()`, and `complete()` maintain unclaimed writes and active commit barriers.

## Control Flow
Constructing `C_Block_Sync` lazily creates a per-inode `BarrierContext` in `cl->barriers` and registers the write as unclaimed. `write_barrier()` waits while any active commit span intersects the write interval, then enqueues the write. `commit_barrier()` selects outstanding writes whose intervals intersect the commit interval, moves them to a new `Barrier`, pushes it to `active_commits`, and waits on its condition. `complete()` removes the callback from either the outstanding list or the barrier write list, notifies waiters, deletes empty barriers, and marks completion.

## State and Persistence Behavior
State is in-memory per inode. It persists only for outstanding async callbacks and active commits. No on-disk state is created.

## Dependencies and Integration Points
It depends on `Client`, `Context`, Ceph mutex/condition variables, Boost intrusive lists, and Boost ICL interval sets. It is intended to support CephFS low-level block commit semantics.

## Risks
The implementation comments say current semantics are not commit-ordered. Correct intrusive-list membership is critical; calling `complete()` on an unexpected state aborts. `BarrierContext` destructor does not drain or validate outstanding entries.

## Test Signals
Tests should verify overlapping intervals block, disjoint intervals proceed, unclaimed writes are removed on completion, commit waiters wake after the last matching write, and empty barriers are deleted.
