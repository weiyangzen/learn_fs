# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-or1k-bits.h

Purpose: `rseq-or1k-bits.h` provides OpenRISC generated rseq primitive implementations for the selftest helper stack.

Important APIs, types, and functions: it generates `rseq_cmpeqv_storev`, `rseq_cmpnev_storeoffp_load`, `rseq_addv`, `rseq_cmpeqv_cmpeqv_storev`, `rseq_offset_deref_addv`, `rseq_cmpeqv_trystorev_storev`, and `rseq_cmpeqv_trymemcpy_storev`. The presence of `RSEQ_ARCH_HAS_OFFSET_DEREF_ADDV` enables the membarrier test path in `param_test.c`.

Control flow: each helper emits OpenRISC `asm goto` using the parent header's compare/load/store, final-store, abort, and memcpy snippets. Success reaches a post-commit label; logical comparison failures and kernel aborts return distinct statuses.

State and persistence: the code updates the TLS active critical-section pointer and caller-supplied data. Offset-deref-add follows a pointer plus offset, loads the target value, adds an increment, and commits within the rseq range.

Dependencies and integration points: it depends on `rseq-or1k.h` temporary-register choices and memory-order macros, plus the common template header. It is included multiple times to build CPU-id and mm-cid variants.

Risks and test signals: OR1K branch delay slots and scratch register choices are sensitive. The manual byte-copy helper and offset-deref-add operation need architecture-specific test coverage. Test signals include successful OR1K builds, `-T r` membarrier coverage, and injection-heavy `param_test` runs.
