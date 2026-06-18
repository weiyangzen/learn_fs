<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/Barrier.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/Barrier.h

Purpose: RAII wrapper around `pthread_barrier_t`.

Important APIs/types: `Barrier` initializes a pthread barrier for a fixed count, destroys it in the destructor, and exposes `wait()`.

Control flow/state/persistence: Constructor throws `PThreadException` on initialization failure. `wait` delegates to `pthread_barrier_wait`; no state is persisted.

Dependencies/integration: Depends on `PThreadException` and `System::getErrString`. Used by thread coordination tests or components needing phase synchronization.

Risks/test signals: Destructor does not report destroy errors. Tests should cover successful multi-thread waits, invalid count behavior, and exception propagation on init failure where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/Barrier.h -->
