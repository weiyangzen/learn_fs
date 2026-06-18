# sources/distributed-fs/openafs/src/lwp/test/test.c

Purpose: microbenchmark for LWP wait/signal cost.

Important APIs/types/functions: `OtherProcess` continuously signals a static `semaphore`. `main` initializes LWP, creates `OtherProcess`, waits on the semaphore a requested number of times, and reports elapsed time.

Control flow: the worker LWP loops forever calling `LWP_SignalProcess`. The main process loops `count` times through `LWP_WaitProcess`, relying on cooperative dispatch and event signaling to bounce between LWPs.

State and persistence: static in-memory `semaphore`, LWP PCBs, and timing variables. No persistence.

Dependencies/integration: depends on `lwp.h`, `gettimeofday`, and assertions. It is built by the LWP test makefile.

Risks and test signals: argument validation is absent; `argv[1]` must exist and be a positive count. It is primarily a performance and smoke signal for LWP event dispatch.
