# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq.c

Purpose: `rseq.c` is the runtime registration and discovery implementation behind `rseq.h`. It supports both libc-owned rseq areas and a selftest-owned TLS fallback.

Important APIs, types, and functions: exported state includes `ptrdiff_t rseq_offset`, `unsigned int rseq_size`, and `unsigned int rseq_flags`. Public functions are `rseq_available()`, `__rseq_register_current_thread()`, `rseq_unregister_current_thread()`, `rseq_fallback_current_cpu()`, and `rseq_fallback_current_node()`. Internal helpers are `sys_rseq()`, `sys_getcpu()`, `get_rseq_kernel_feature_size()`, constructor `rseq_init()`, and destructor `rseq_exit()`.

Control flow: the constructor first checks weak libc symbols `__rseq_offset`, `__rseq_size`, and `__rseq_flags`, retrying with `dlsym(RTLD_NEXT, ...)` when weak values are absent. If libc owns rseq, it mirrors libc offset, size, and flags with compatibility handling for 20/32 byte historical sizes. Otherwise it computes the offset to an internal `__thread union rseq_tls` area and marks ownership. Registration uses auxv `AT_RSEQ_FEATURE_SIZE`/`AT_RSEQ_ALIGN` to choose allocation size and invokes `__NR_rseq`. Unregistration calls the same syscall with `RSEQ_ABI_FLAG_UNREGISTER`.

State and persistence: `__rseq` is per-thread TLS and initially has `cpu_id` set to `RSEQ_ABI_CPU_ID_UNINITIALIZED`. Global process state records ownership, active size, allocation size, offset, and flags. Destructor invalidates self-owned global state.

Dependencies and integration points: depends on syscall numbers, auxv constants, dlfcn, scheduler fallback APIs, `kselftest.h`, and `rseq.h`. All selftest programs link this file to use registration and current CPU/node helpers.

Risks and test signals: libc interposition and feature-size compatibility are subtle. A process-wide successful registration followed by a later thread failure aborts as incoherent. Test signals include `basic_test`, `legacy_check`, `syscall_errors_test`, `param_test`, and any test that runs with `GLIBC_TUNABLES=glibc.pthread.rseq=0`.
