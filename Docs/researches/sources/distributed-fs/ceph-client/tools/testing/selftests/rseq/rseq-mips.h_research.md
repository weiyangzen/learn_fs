# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-mips.h

Purpose: `rseq-mips.h` is the architecture glue for MIPS rseq selftest helpers. It chooses the signature encoding for MIPS, microMIPS, and nanoMIPS, defines barriers and word-size-dependent instruction macros, and generates concrete helper variants.

Important APIs, types, and functions: it defines `RSEQ_SIG`, `rseq_smp_mb()`, `rseq_smp_rmb()`, `rseq_smp_wmb()`, acquire/release helpers, load/store operation macros, `RSEQ_ASM_DEFINE_TABLE()`, `RSEQ_ASM_DEFINE_EXIT_POINT()`, `RSEQ_ASM_STORE_RSEQ_CS()`, `RSEQ_ASM_CMP_CPU_ID()`, abort/cmpfail macros, and repeated inclusion of `rseq-mips-bits.h`.

Control flow: after architecture macro setup, the file includes the bits header for CPU-id relaxed/release, mm-cid relaxed/release, and CPU-id-none relaxed helpers. The generated code then supplies the symbols called by `rseq.h` wrappers.

State and persistence: it does not hold runtime data but defines ELF section records and TLS `rseq_cs` update sequences used at runtime. Memory-order macros are used by both generated critical sections and higher-level locking helpers.

Dependencies and integration points: selected by `rseq.h` on `__mips__`. It depends on MIPS assembler syntax and `_MIPS_SZLONG` for register-width selection. It integrates with `param_test.c` for MIPS correctness coverage.

Risks and test signals: signature handling across MIPS ISA modes is fragile. Incorrect word-size selection or branch delay behavior can invalidate critical-section ranges. Test signals are successful MIPS builds and passing injected rseq tests.
