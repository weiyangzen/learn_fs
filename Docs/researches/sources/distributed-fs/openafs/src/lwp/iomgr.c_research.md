## sources/distributed-fs/openafs/src/lwp/iomgr.c

Purpose: Implements the LWP I/O manager, allowing cooperative lightweight processes to wait on select file descriptors, timeouts, Unix signals, and software signals.

Important APIs and functions: Public functions include `IOMGR_Initialize`, `IOMGR_Finalize`, `IOMGR_Select`, `IOMGR_Poll`, `IOMGR_Cancel`, `IOMGR_Signal`, `IOMGR_CancelSignal`, `IOMGR_Sleep`, `IOMGR_AllocFDSet`, `IOMGR_FreeFDSet`, and `IOMGR_SoftSig`. Core internal functions include `IOMGR`, `SignalIO`, `SignalTimeout`, `SigHandler`, and `SignalSignals`.

Control flow: `IOMGR_Initialize` initializes LWP support if needed, creates a timer list, and starts an `IO MANAGER` LWP. `IOMGR_Select` either performs immediate polling select or constructs an `IoRequest`, inserts it into the timer queue, records it in the active PCB, and `LWP_QWait`s. The manager loop handles delivered signals, expires timers, builds aggregate fd sets, runs `select`, signals matching requests, and dispatches runnable LWPs. `IOMGR_Cancel` removes a pending request and wakes the waiting process with result `-2`.

State and persistence: Maintains global request timer list, request free list, fd_set pool, signal handler state, soft signal slots, aggregate fd sets, and the IOMGR process id. No disk persistence.

Dependencies and integration: Depends on LWP queues, timer package, fasttime, POSIX select/signal APIs, and platform-specific fd_set representation.

Risks: Global state is not pthread-safe and is intended for cooperative LWP use. `FD_SETSIZE` is forced to 65536 on non-Windows, so fd_set memory is large. Signal handling races are acknowledged in comments. `IOMGR_Poll` logs allocation failure but can still dereference null fd sets. Request lifetime invariants are delicate because the selector frees requests after wakeup.

Test signals: Blocking select wake by fd readiness, timeout wake, cancel, Unix signal delivery, software signal process creation, high fd values, invalid timeval correction, finalize cleanup, and Windows/Linux max-wait behavior.
