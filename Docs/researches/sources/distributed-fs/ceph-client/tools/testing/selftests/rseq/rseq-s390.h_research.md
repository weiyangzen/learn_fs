# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-s390.h

Purpose: `rseq-s390.h` is the s390 architecture layer for rseq selftest helpers.

Important APIs, types, and functions: it defines `RSEQ_SIG` using `trap4`, `rseq_smp_mb()`, `rseq_smp_rmb()`, `rseq_smp_wmb()`, acquire/release helpers, long-word instruction aliases, table/exit macros, `RSEQ_ASM_STORE_RSEQ_CS()`, `RSEQ_ASM_CMP_CPU_ID()`, `RSEQ_ASM_DEFINE_ABORT()`, and `RSEQ_ASM_DEFINE_CMPFAIL()`.

Control flow: the header prepares s390 assembly snippets and includes `rseq-s390-bits.h` for CPU-id relaxed/release, mm-cid relaxed/release, and CPU-id-none relaxed generated helpers.

State and persistence: no direct runtime state. The macros define how active critical-section pointers are stored in TLS and how critical-section descriptors are emitted for kernel/debugger use.

Dependencies and integration points: selected by `rseq.h` for `__s390__`. It integrates with `param_test.c`, `syscall_errors_test.c`, and the shared registration layer in `rseq.c`.

Risks and test signals: alternate user address-space behavior affects syscall error tests, and this header's trap signature must remain safe and recognizable. Passing s390 builds and parameter tests are key validation signals.
