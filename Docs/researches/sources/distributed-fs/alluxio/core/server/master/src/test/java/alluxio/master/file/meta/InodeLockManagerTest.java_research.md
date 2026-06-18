# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/InodeLockManagerTest.java

## Purpose
Concurrency tests for `InodeLockManager` node and edge locks. It verifies read/write compatibility and blocking semantics for inode locks and edge locks.

## Important APIs/types/functions
- Tests `lockInode` and `lockEdge` with combinations of `LockMode.READ` and `LockMode.WRITE`.
- Uses `LockResource` to hold/release locks.
- Uses a second thread plus `AtomicBoolean` to observe whether a competing lock acquisition finishes.

## Control flow
- `lockInode` runs four combinations: WRITE/READ, READ/WRITE, WRITE/WRITE should block; READ/READ should not.
- `lockEdge` runs the same combinations for `Edge(10, "name")`.
- Helpers acquire first lock, start a thread that tries to acquire a logically equivalent copied inode or new edge instance, sleep briefly if blocking is expected, then release and wait for completion.

## State and persistence behavior
- Lock state only; no inode store or filesystem persistence.
- Inode copy via journal entry proves locks are keyed by inode identity/id rather than Java object reference.
- Edge test proves locks are keyed by edge value rather than object reference.

## Dependencies and integration points
- Integrates `InodeLockManager`, `MutableInodeFile`, `CreateFileContext`, `Edge`, and `CommonUtils.waitFor`.

## Risks and edge cases
- Uses a 20 ms sleep to detect blocking, which is pragmatic but timing-sensitive.
- Does not test reentrancy, fairness, or lock cleanup after exceptions.

## Test signals
- Clear signal for core lock compatibility matrix and key equality semantics.
