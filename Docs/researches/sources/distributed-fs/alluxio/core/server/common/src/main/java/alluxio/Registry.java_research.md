## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/Registry.java

### Purpose
`Registry` manages `Server` instances inside an Alluxio process, including lookup, dependency-ordered start, reverse-order stop, and close.

### Important APIs, Types, And Functions
The registry maps server classes to instances under a `ReentrantLock`. Public methods are `get`, `get` with timeout, `add`, `getServers`, `start`, `stop`, and `close`. Private `getTransitiveDeps` computes dependencies, and `DependencyComparator` orders servers.

### Control Flow
`get` waits up to a timeout for a server class to appear, then type-checks and casts it. `getServers` sorts registered servers: if left depends on right, left compares after right; if right depends on left, left compares before right; otherwise names determine order. `start` starts in sorted dependency order and stops already-started servers if a later start throws. `stop` and `close` traverse the reverse order.

### State And Persistence
State is an in-memory registry map and lock. No persistence.

### Dependencies And Integration Points
Used by process implementations to wire master/worker internal servers. Depends on `Server`, `LockResource`, `CommonUtils.waitFor`, `WaitForOptions`, and Guava `Lists.reverse`.

### Risks
`getTransitiveDeps` reads `mRegistry` without holding `mLock` when called during sorting, so concurrent mutation can produce inconsistent ordering. Dependency cycles are detected only when a dependency path reaches the original server, not necessarily all malformed graphs. Failed start stops servers in start order, not reverse start order.

### Test Signals
No direct tests in this subset. Server lifecycle tests should cover dependency ordering and failure cleanup.
