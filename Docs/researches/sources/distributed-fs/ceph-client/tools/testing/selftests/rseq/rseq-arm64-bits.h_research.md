# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-arm64-bits.h

Purpose: `rseq-arm64-bits.h` provides AArch64 generated rseq primitive implementations. It is a template body included by `rseq-arm64.h` for each CPU-id/mm-cid and relaxed/release combination.

Important APIs, types, and functions: generated helpers include `rseq_cmpeqv_storev`, `rseq_cmpnev_storeoffp_load`, `rseq_addv`, `rseq_cmpeqv_cmpeqv_storev`, `rseq_cmpeqv_trystorev_storev`, and `rseq_cmpeqv_trymemcpy_storev`. Unlike x86, RISC-V, and OR1K, this file does not define `RSEQ_ARCH_HAS_OFFSET_DEREF_ADDV`.

Control flow: each helper emits an AArch64 `asm goto` critical section using macros such as `RSEQ_ASM_STORE_RSEQ_CS`, `RSEQ_ASM_CMP_CPU_ID`, compare/load/store operations, and the final post-commit label. Compare failures and aborts are separated to let callers distinguish expected data contention from kernel-triggered restart.

State and persistence: the generated code writes the active `rseq_cs` pointer, reads the ABI CPU/mm-cid field, and updates caller memory atomically relative to migration/preemption semantics. Release forms use store-release/fence-style final stores supplied by `rseq-arm64.h`.

Dependencies and integration points: it depends on AArch64 temporary registers and operation macros from `rseq-arm64.h`, and template suffixing from `rseq-bits-template.h`. `param_test.c` uses these helpers for AArch64 per-cpu structures.

Risks and test signals: risks include clobber list accuracy, register allocation conflicts, and copy-loop correctness in `trymemcpy`. Since rseq correctness relies on exact instruction ranges, label placement around final stores is critical. Test signals are passing buffer, memcpy, and compare-twice variants on AArch64.
