# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-or1k.h

Purpose: `rseq-or1k.h` defines the OpenRISC architecture layer for rseq helper generation.

Important APIs, types, and functions: it defines `RSEQ_SIG`, `rseq_smp_mb()`, `rseq_smp_rmb()`, `rseq_smp_wmb()`, acquire/release helpers, temporary registers, table/exit/abort macros, compare/load/store/add macros, final-store variants, a byte-copy loop, and offset-deref-add support.

Control flow: the header defines instruction snippets and includes `rseq-or1k-bits.h` for CPU-id relaxed/release, mm-cid relaxed/release, and CPU-id-none relaxed variants.

State and persistence: it contributes linker-visible critical-section descriptors and runtime TLS `rseq_cs` stores through generated helpers. Memory-order macros influence higher-level lock release behavior in `param_test.c`.

Dependencies and integration points: selected by `rseq.h` for `__or1k__`. It depends on OpenRISC instruction syntax and integrates with `rseq-or1k-thread-pointer.h`.

Risks and test signals: delay-slot handling is visible in several snippets and is a key correctness risk. The architecture also supports membarrier-related offset-deref-add, so `test_membarrier()` is a relevant signal in addition to the common parameter tests.
