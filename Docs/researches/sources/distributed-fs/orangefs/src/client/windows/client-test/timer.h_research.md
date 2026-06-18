# sources/distributed-fs/orangefs/src/client/windows/client-test/timer.h

Purpose: Declares platform-specific timer helper signatures.

Important APIs/types: Windows exports `unsigned __int64 timer_start()` and `double timer_elapsed(unsigned __int64 start)`. POSIX includes `<sys/time.h>` and exports `void timer_start(struct timeval *start)` plus `double timer_elapsed(struct timeval *start)`.

Control flow/state: Header-only declarations; the API shape changes by platform instead of hiding timestamp storage behind one type.

Dependencies/integration: Included by client-test timing code and `test-support.c`.

Risks: The header has no include guard, so repeated inclusion is tolerated only because it contains declarations but is still non-ideal. Cross-platform call sites need conditional code because function signatures differ.

Test signals: Build on Windows and POSIX with `-Wmissing-prototypes`/similar warnings to catch signature mismatches.
