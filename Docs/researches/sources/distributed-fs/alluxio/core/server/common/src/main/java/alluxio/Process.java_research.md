## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/Process.java

### Purpose
`Process` is the common lifecycle interface for Alluxio processes.

### Important APIs, Types, And Functions
It declares `start`, `stop`, and `waitForReady(int timeoutMs)`.

### Control Flow
Implementations start and block until stopped, stop synchronously, and report readiness within a timeout. `ProcessUtils.run` and shutdown hooks use this contract.

### State And Persistence
No state in the interface. Implementations hold process services, threads, ports, and persisted state.

### Dependencies And Integration Points
Used by master, worker, and other daemon entry points through `ProcessUtils`.

### Risks
`start` is expected to block; implementations that return early alter process main behavior. `waitForReady` has a TODO to replace it with serving-state semantics.

### Test Signals
No direct test in this subset.
