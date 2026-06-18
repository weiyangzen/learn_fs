# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-generic-thread-pointer.h

Purpose: `rseq-generic-thread-pointer.h` supplies the fallback implementation of `rseq_thread_pointer()` using the compiler builtin thread-pointer intrinsic.

Important APIs, types, and functions: it exposes `static inline void *rseq_thread_pointer(void)`, wrapped for C++ compatibility.

Control flow: the function simply returns `__builtin_thread_pointer()`. There are no branches besides header guards and C++ extern handling.

State and persistence: no state is stored. Its return value is used by `rseq.c` to compute the offset between the architecture thread pointer and the selftest-owned TLS rseq area, and by `rseq_get_abi()` to recover the current thread's ABI area.

Dependencies and integration points: included by `rseq-thread-pointer.h` on architectures without a dedicated implementation. It depends on compiler support for `__builtin_thread_pointer()`.

Risks and test signals: the risk is compiler or architecture support mismatch. If the builtin returns a pointer using semantics different from libc TLS layout, rseq ABI lookup fails. Test signals are successful registration and current CPU reads on generic-path architectures.
