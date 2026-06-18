# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-resched-dscr.c

Purpose: verifies DSCR SPR preservation when a suspended transaction is doomed by rescheduling/context switch.

Important APIs/types/functions: `test_body()` sets DSCR, begins/suspends TM, loops on `tcheck` until doomed, records DSCR and TEXASR; `tm_resched_dscr()` wraps it in `eat_cpu()`.

Control flow: the loop repeats until the transaction abort cause is reschedule. For that cause, it compares DSCR after reclaim with the pre-transaction value and reports OK/FAIL.

State and persistence behavior: DSCR is thread SPR state; no external state. The transaction may repeat many times until a suitable reschedule abort occurs.

Dependencies and integration points: depends on HTM, `../pmu/lib.h` `eat_cpu()`, SPR constants, and TM failure-code encodings.

Risks and test signals: could spin for a long time on systems that do not reschedule the thread as expected. Failure is explicit DSCR mismatch.
