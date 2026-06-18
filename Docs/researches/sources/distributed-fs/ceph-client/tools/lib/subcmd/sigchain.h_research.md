# sources/distributed-fs/ceph-client/tools/lib/subcmd/sigchain.h

Purpose: Public declarations for libsubcmd signal handler chaining.

Important APIs/types/functions: Defines `typedef void (*sigchain_fun)(int)` and declares `sigchain_pop()` and `sigchain_push_common()`.

Control flow: Callers push one handler across common termination signals and pop individual handlers when re-raising or restoring.

State and persistence: Implementation stores signal stacks statically.

Dependencies/integration: Used by pager cleanup and any libsubcmd user needing stacked signal handlers.

Risks: The header exposes no push for arbitrary signals; only common push plus single-signal pop. Callers must not assume thread safety.

Test signals: Compile and behavioral tests in `sigchain.c`.
