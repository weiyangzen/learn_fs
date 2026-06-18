# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-x86.h

Purpose: `rseq-x86.h` supplies the x86 architecture layer for rseq selftest helpers.

Important APIs, types, and functions: it defines `RSEQ_SIG`, CPU/rseq/mm-cid offsets, `RSEQ_ASM_TP_SEGMENT`, memory barriers, acquire/release helpers, x86-64 and i386 descriptor table encodings, exit-point macros, `RSEQ_ASM_STORE_RSEQ_CS()`, `RSEQ_ASM_CMP_CPU_ID()`, abort and cmpfail section macros, and the include-time expansion of `rseq-x86-bits.h`.

Control flow: separate compile-time branches define x86-64 versus i386 assembly forms. The file then generates CPU-id relaxed/release, mm-cid relaxed/release, and CPU-id-none relaxed helpers.

State and persistence: no standalone state. Its macros store descriptor addresses into TLS and emit `__rseq_cs`, `__rseq_cs_ptr_array`, `__rseq_exit_point_array`, and failure sections. The barriers are also used by higher-level lock/unlock helpers.

Dependencies and integration points: selected by `rseq.h` for x86 targets. It integrates with `rseq-x86-thread-pointer.h`, `rseq.c`, and the param test runner.

Risks and test signals: the code works around GCC asm-goto/TLS operand issues, so compiler behavior is a risk. i386 has stronger barrier macros than x86-64. Test signals include passing optimized, legacy, compare-twice, mm-cid, and injection tests on x86.
