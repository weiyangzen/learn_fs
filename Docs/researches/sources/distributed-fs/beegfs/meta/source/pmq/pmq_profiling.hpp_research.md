## sources/distributed-fs/beegfs/meta/source/pmq/pmq_profiling.hpp

Purpose: provides build-time profiling abstraction macros for PMQ scopes, functions, mutexes, condition variables, and locks, optionally integrating with Tracy.

Important APIs: when `PMQ_WITH_PROFILING` is enabled, `PMQ_PROFILING_CTX`, `PMQ_PROFILED_SCOPE`, `PMQ_PROFILED_FUNCTION`, `PMQ_PROFILED_MUTEX`, `PMQ_PROFILED_CONDVAR`, `PMQ_PROFILED_LOCK`, and `PMQ_PROFILED_UNIQUE_LOCK` expand to Tracy-aware constructs. Otherwise they expand to standard `std::mutex`, `std::condition_variable`, `std::lock_guard`, and `std::unique_lock` wrappers.

Control flow: PMQ code writes profiling-neutral lock and scope declarations. The macros choose whether instrumentation exists at compile time.

State and persistence behavior: no persistence. The selected mutex/condition types affect synchronization behavior and type compatibility across PMQ implementation files.

Dependencies and integration points: includes `<mutex>` and `<condition_variable>` always, and `<Tracy.hpp>` only under profiling. Comments identify a BeeGFS/flex-docs build setup requirement for Tracy headers.

Risks: profiling mode uses `std::condition_variable_any` and Tracy lock wrappers, which can differ in overhead and behavior from the non-profiling build. The macro-generated temporary names require careful use to avoid collisions.

Test signals: compile both profiling and non-profiling variants, run lock/condition wait tests in both modes, and check that PMQ hot paths still build when Tracy headers are absent and profiling is disabled.
