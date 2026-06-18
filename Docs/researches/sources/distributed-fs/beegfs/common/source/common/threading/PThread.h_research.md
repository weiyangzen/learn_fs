<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/PThread.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/PThread.h

Purpose: Declares the BeeGFS base class for pthread-backed worker threads.

Important APIs/types: `PThread` exposes `start`, `startOnNumaNode`, `startInCurrentThread`, `join`, `timedjoin`, `terminate`, `kill`, `selfTerminate`, self-terminate waits, sleep/yield helpers, TLS accessors for current thread/app/name, and a pure virtual `run`.

Control flow/state/persistence: `runStatic` installs TLS name/app, kernel thread name, applies priority shift, then calls `run`. Self-termination uses both an atomic fast flag and a mutex/condition pair for waiters. No persistent state.

Dependencies/integration: Foundation for long-running BeeGFS components and worker queues. Uses `Condition`, `Mutex`, `Atomics`, `System`, signal APIs, and pthread attributes.

Risks/test signals: `join` does not reset `threadID`; repeated joins are unsafe. Tests should cover timeout math, self-terminate wakeups, `startInCurrentThread`, name truncation/prefixing, and exception behavior on invalid operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/PThread.h -->
