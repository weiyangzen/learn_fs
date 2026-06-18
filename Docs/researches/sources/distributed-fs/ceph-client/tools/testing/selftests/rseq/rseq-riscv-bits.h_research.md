# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-riscv-bits.h

Purpose: `rseq-riscv-bits.h` implements RISC-V generated rseq primitives.

Important APIs, types, and functions: it generates `rseq_cmpeqv_storev`, `rseq_cmpnev_storeoffp_load`, `rseq_addv`, `rseq_cmpeqv_cmpeqv_storev`, `rseq_offset_deref_addv`, `rseq_cmpeqv_trystorev_storev`, and `rseq_cmpeqv_trymemcpy_storev`. The offset-deref-add implementation enables membarrier testing on RISC-V.

Control flow: helpers are `asm goto` sections that store the active descriptor, validate current CPU/mm-cid, execute RISC-V load/compare/store or byte-copy sequences, and return through success, abort, or comparison-failure labels.

State and persistence: state changes are limited to TLS `rseq_cs` and caller memory. The helpers rely on fences from `rseq-riscv.h` for release-mode final stores and higher-level synchronization.

Dependencies and integration points: it depends on register-width macros, temporary register names, and operation snippets from `rseq-riscv.h`, plus the template header. `param_test.c` exercises it through all generic wrappers.

Risks and test signals: little-endian-only support is enforced in the parent header. Risks include fence placement, scratch register clobbers, byte-copy correctness, and offset-deref-add commit semantics. Passing `run_param_test.sh`, including `-T r`, is the main test signal.
