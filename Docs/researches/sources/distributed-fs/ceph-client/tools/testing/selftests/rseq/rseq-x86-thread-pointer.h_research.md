# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-x86-thread-pointer.h

Purpose: `rseq-x86-thread-pointer.h` implements `rseq_thread_pointer()` for x86 targets.

Important APIs, types, and functions: it exposes `static inline void *rseq_thread_pointer(void)`. GCC 11.1 and newer use `__builtin_thread_pointer()`. Older compiler paths read `%fs:0` on x86-64 or `%gs:0` on i386.

Control flow: compile-time branches select builtin versus inline assembly and 64-bit versus 32-bit segment register. Runtime behavior is a simple thread-pointer load.

State and persistence: no state is stored. The return value anchors all TLS rseq ABI access.

Dependencies and integration points: selected by `rseq-thread-pointer.h` for `__x86_64__` or `__i386__`. It depends on glibc feature macros for `__GNUC_PREREQ`.

Risks and test signals: wrong segment selection or compiler-version detection breaks `rseq_get_abi()`. Test signals are successful registration and current CPU access on old and new GCC builds.
