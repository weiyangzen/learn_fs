
# sources/distributed-fs/ceph-client/tools/perf/util/mutex.h

Purpose: defines perf synchronization wrapper types and optional Clang/GCC thread-safety annotation macros.

Important APIs/types/functions: feature-detects attributes such as `guarded_by`, `lockable`, `exclusive_lock_function`, `unlock_function`, and `no_thread_safety_analysis`, falling back to empty macros when unavailable. `struct mutex` wraps `pthread_mutex_t` and is marked `LOCKABLE` when supported. `struct cond` wraps `pthread_cond_t`. Function declarations cover normal, process-shared, and recursive mutex initialization; destroy/lock/unlock/trylock; normal and process-shared condition initialization; destroy/wait/signal/broadcast.

Control flow: no executable flow. The annotations document lock requirements to static analyzers while leaving compiled behavior to `mutex.c`.

State and persistence: caller-owned pthread objects only. No persistent state.

Dependencies: pthreads and booleans. It intentionally keeps the wrapper thin so existing pthread semantics remain recognizable.

Integration points: included by shared perf utilities needing annotated locking contracts. `cond_wait` is annotated as requiring the associated mutex.

Risks: annotation support differs by compiler; code must compile correctly when all macros are empty. Passing uninitialized wrappers or mixing raw pthread operations with wrapper annotations can defeat diagnostics. Test signals are compilation on GCC/Clang versions and runtime synchronization smoke tests.
