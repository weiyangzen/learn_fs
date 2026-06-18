# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-s390-bits.h

Purpose: `rseq-s390-bits.h` provides s390 generated rseq primitive implementations.

Important APIs, types, and functions: it generates `rseq_cmpeqv_storev`, `rseq_cmpnev_storeoffp_load`, `rseq_addv`, `rseq_cmpeqv_cmpeqv_storev`, `rseq_cmpeqv_trystorev_storev`, and `rseq_cmpeqv_trymemcpy_storev`. It does not provide offset-deref-add support.

Control flow: generated helpers emit s390 `asm goto` critical sections. They publish the descriptor address, compare CPU/mm-cid, execute long-word load/compare/store sequences, and branch to abort or cmpfail labels as needed.

State and persistence: only TLS `rseq_cs` and caller-provided memory are modified. Return values tell higher-level retry loops whether the operation committed, saw a data mismatch, or aborted due to rseq restart.

Dependencies and integration points: it depends on `rseq-s390.h` for `trap4` signature handling, `bcr` barriers, long-word instruction aliases, table macros, and jump syntax. It feeds the generic `rseq.h` wrappers.

Risks and test signals: the main risks are long-word instruction assumptions, clobber lists, and correct s390 jump/label placement. Test signals are successful s390 builds and passing parameter tests, including injection and compare-twice modes.
