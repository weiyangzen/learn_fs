## sources/distributed-fs/openafs/src/lwp/lwp.c

Purpose: Implements the core non-preemptive lightweight process scheduler for OpenAFS, including process creation/destruction, cooperative dispatch, event waiting/signaling, stack management, and per-process rocks.

Important APIs and functions: Public APIs include `LWP_InitializeProcessSupport`, `LWP_CreateProcess`, `LWP_CreateProcess2` on AIX, `LWP_DestroyProcess`, `LWP_DispatchProcess`, `LWP_WaitProcess`, `LWP_MwaitProcess`, `LWP_INTERNALSIGNAL`, `LWP_QWait`, `LWP_QSignal`, `LWP_CurrentProcess`, `LWP_ThreadId`, `LWP_GetProcessPriority`, `LWP_TerminateProcessSupport`, `LWP_StackUsed`, `LWP_NewRock`, and `LWP_GetRock`. Internal helpers manage queues, PCBs, stacks, dispatcher context, and signaling.

Control flow: Initialization creates the main PCB and dispatcher anchor. Process creation allocates a PCB and stack, initializes stack guard/use tracking, inserts it into a priority runnable queue, then uses architecture-specific `savecontext` to build a start context. `Dispatcher` checks stack overflow, rotates the current runnable queue, selects the highest priority non-empty runnable queue, and `returnto`s that context. Wait calls move the active process to blocked or qwaiting queues; signal calls scan blocked processes and move satisfied waiters back to runnable.

State and persistence: Global scheduler state includes runnable queues by priority, blocked and qwaiting queues, current PCB pointer, LWP control anchor, stack sizing knobs, next process index, and overflow behavior. No durable persistence.

Dependencies and integration: Requires `savecontext` and `returnto` from platform process assembly/C code. IOMGR and lock code build on its wait/signal/dispatch APIs.

Risks: Cooperative scheduling means blocking system calls outside IOMGR block all LWPs. Stack setup is architecture-specific and fragile. Stack overflow checks assume downward-growing stacks except special HP handling. `LWP_TerminateProcessSupport` must run from the original process. Event matching is pointer identity based. No pthread safety.

Test signals: Process creation and completion, priority scheduling, wait on one and multiple events, quick wait/signal, destroy self and other process, stack overflow diagnostics, rock set/get behavior, environment-driven minimum stack size, and architecture context-switch tests.
