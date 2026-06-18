<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/PThread.cpp -->
## sources/distributed-fs/beegfs/common/source/common/threading/PThread.cpp

Purpose: Implements BeeGFS thread lifecycle helpers, signal handling, priority shifting, and NUMA-aware start.

Important APIs/functions: Static TLS keys/destructors store thread name and app. `blockInterruptSignals`/`unblockInterruptSignals` manage signal masks. `registerSignalHandler` installs crash/termination handlers. `signalHandler` turns fatal signals into `SignalException` or exits. `setPriorityShift`, `applyPriorityShift`, `resetSelfTerminate`, and `startOnNumaNode` implement runtime controls.

Control flow/state/persistence: `startOnNumaNode` configures pthread affinity attributes before `pthread_create`. Priority shift maps to `nice`. Signal handling is process-global; app/name state is thread-local.

Dependencies/integration: Integrates with `AbstractApp`, `System`, logging/string helpers, Linux signals, sched affinity, and pthread APIs. Many BeeGFS worker classes derive from `PThread`.

Risks/test signals: Signal handlers throwing exceptions is delicate and context-sensitive. Tests should cover start/join, TLS app/name propagation, self-terminate reset, NUMA fallback, priority errors, and fake-thread initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/PThread.cpp -->
