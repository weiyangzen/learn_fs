# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-ppc-bits.h

Purpose: `rseq-ppc-bits.h` implements generated PowerPC rseq primitives for the selftest wrapper API.

Important APIs, types, and functions: generated functions are `rseq_cmpeqv_storev`, `rseq_cmpnev_storeoffp_load`, `rseq_addv`, `rseq_cmpeqv_cmpeqv_storev`, `rseq_cmpeqv_trystorev_storev`, and `rseq_cmpeqv_trymemcpy_storev`. It does not define offset-deref-add support.

Control flow: the functions emit PowerPC `asm goto` critical sections using CR7 comparisons and parent-defined load/store macros. Success commits through the final store and returns zero. Data mismatch returns a comparison-failure code, while kernel abort returns a retry/abort code after `RSEQ_INJECT_FAILED`.

State and persistence: it updates the current thread's active rseq descriptor and caller memory. The generated helpers assume the caller passes the CPU/mm-cid value already read from the ABI area.

Dependencies and integration points: depends on `rseq-ppc.h` for 32-bit/64-bit instruction selection, `lwsync`/`sync` barriers, table encoding, and scratch register usage. It feeds the generic wrappers used by `param_test.c`.

Risks and test signals: PowerPC 32-bit big-endian table encoding, register clobbering, and CR7 use are sensitive. Test signals are architecture build success and passing common rseq stress variants, especially compare-twice and release-mode buffer tests.
