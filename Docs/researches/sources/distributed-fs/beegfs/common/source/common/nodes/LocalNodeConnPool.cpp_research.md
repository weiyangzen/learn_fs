<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/LocalNodeConnPool.cpp -->
## sources/distributed-fs/beegfs/common/source/common/nodes/LocalNodeConnPool.cpp

### Purpose
`LocalNodeConnPool.cpp` implements an internal connection pool for messages sent from a service to itself, using `LocalConnWorker` instances instead of TCP.

### Important APIs, Types, And Functions
The constructor copies NICs, initializes connection counters, and reads max internal connections from config. `acquireStreamSocketEx()` returns an available worker endpoint, waits when allowed and maxed out, or starts a new `LocalConnWorker`. `releaseStreamSocket()` marks a worker available. `invalidateStreamSocket()` removes a worker, gracefully shuts down the endpoint, joins the worker, and deletes it. `updateInterfaces()` updates the copied NIC list and ignores the stream port.

### Control Flow
Acquire is synchronized by `mutex`: wait for availability, reuse a worker, or increment established count before creating a new worker. Invalidation removes the worker under lock, then performs shutdown/join outside the lock. The destructor copies the worker list and invalidates every endpoint.

### State, Persistence, And Dependencies
State is in-memory worker list, connection counters, max connection limit, condition variable, and NIC list. Dependencies include `LocalConnWorker`, `PThread` app config, `NodeConnPool`, logging, and socket exceptions.

### Integration Points
`LocalNode` installs this pool so normal messaging code can talk to the local service through the same `Socket` abstraction.

### Risks
Several searches dereference `*iter` before checking `iter != end`, which is unsafe if the socket is absent. Worker creation increments `establishedConns` before allocation/start and must decrement on failure. Tests should cover acquire/release reuse, max-connection waiting, no-wait acquire, invalidation of missing sockets, worker start failure, destructor cleanup, and interface-change detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/LocalNodeConnPool.cpp -->
