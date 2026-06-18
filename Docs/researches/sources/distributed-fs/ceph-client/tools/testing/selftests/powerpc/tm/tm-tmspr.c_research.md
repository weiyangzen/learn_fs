# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-tmspr.c

Purpose: stress-tests preservation of TM SPRs (`TFIAR`, `TFHAR`, and `TEXASR`) across many threads and transactions.

Important APIs/types/functions: `tfiar_tfhar()` writes unique thread values and repeatedly reads them back; `texasr()` repeatedly aborts transactions and checks `TEXASR_FS`; `test_tmspr()` launches many pthreads.

Control flow: thread count is 10 times online CPUs. Even-indexed threads validate TFIAR/TFHAR stability; odd-indexed threads validate TEXASR failure summary after `tabort`. Main joins all and returns based on global `passed`.

State and persistence behavior: global `num_loops` and `passed`; per-thread SPR state; no external persistence.

Dependencies and integration points: requires pthreads and real HTM.

Risks and test signals: `passed` is unsynchronized but only transitions from 1 to 0, sufficient for this stress test. Failures are reported through final nonzero status without detailed offending values.
