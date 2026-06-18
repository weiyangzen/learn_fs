# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-mips-bits.h

Purpose: `rseq-mips-bits.h` implements the MIPS generated rseq operations used by the generic wrappers. It supports the common compare/store, pop/load, add, double-compare, speculative-store, and memcpy/final-store primitives.

Important APIs, types, and functions: it generates `rseq_cmpeqv_storev`, `rseq_cmpnev_storeoffp_load`, `rseq_addv`, `rseq_cmpeqv_cmpeqv_storev`, `rseq_cmpeqv_trystorev_storev`, and `rseq_cmpeqv_trymemcpy_storev` variants. It does not advertise `RSEQ_ARCH_HAS_OFFSET_DEREF_ADDV`.

Control flow: generated helpers use MIPS branch-and-label assembly inside `asm goto`. Each critical section stores the active descriptor, validates the ABI CPU/mm-cid field, performs data comparisons, commits through a final store, or exits through abort/cmpfail labels.

State and persistence: runtime writes are limited to caller memory and the thread-local `rseq_cs` field. Comparison failure versus abort return values are used by higher-level retry loops in `param_test.c`.

Dependencies and integration points: this file depends on `rseq-mips.h` for register-size selection, RSEQ signature emission, table layout, compare/load/store macros, and memory barriers. It is selected only through `rseq.h` on `__mips__`.

Risks and test signals: MIPS mode differences, delay slots, endian/word-size table encoding, and inline-assembly constraints are the main risks. Test signals are architecture build success and passing `run_param_test.sh` variants on MIPS.
