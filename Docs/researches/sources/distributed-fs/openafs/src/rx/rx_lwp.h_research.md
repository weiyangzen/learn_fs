# Research: sources/distributed-fs/openafs/src/rx/rx_lwp.h

## sources/distributed-fs/openafs/src/rx/rx_lwp.h

### Purpose
`rx_lwp.h` provides no-op mutex, condition variable, and call refcount macros for RX builds using cooperative LWP rather than preemptive pthread locks.

### Important Definitions
- Typedefs `afs_kmutex_t` and `afs_kcondvar_t` as `int`.
- Defines `MUTEX_*`, `CV_*`, `CALL_HOLD*`, and `CALL_RELE*` macros as no-ops or constant success for try-enter.

### Control Flow and State
There is no runtime state. The header compiles shared RX code without lock objects when LWP scheduling guarantees are expected to provide sufficient serialization.

### Dependencies and Integration Points
Included by `rx.h` when not `KERNEL` and not `AFS_PTHREAD_ENV`. Used indirectly by all RX code compiled under the LWP backend.

### Risks and Edge Cases
- Shared code that relies on actual locking must not run concurrently under LWP in ways that violate cooperative assumptions.
- Refcount macros are no-ops, so lifetime diagnostics differ from pthread/kernel builds.
- Adding new code that assumes condition variables actually block will fail under this backend.

### Test Signals
Build and run RX LWP server/client tests, especially call lifecycle and event interactions, to ensure no code accidentally depends on real mutex/cv behavior.
