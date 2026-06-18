# sources/distributed-fs/openafs/src/opr/softsig.c

Purpose: pthread-compatible signal handling system that routes allowed signals to normal handler functions in a dedicated thread, avoiding async-signal-safety constraints.

Important APIs/types/functions: public `opr_softsig_Init` and `opr_softsig_Register`. Internal `softsigSignalSet` builds the managed signal set, `signalHandler` loops on `sigwait`, `ExitHandler` restores default-style termination by unblocking and raising the signal, and `StopHandler` sends `SIGSTOP`.

Control flow: initialization blocks managed signals in the calling thread before other threads are created, registers default handlers for INT/TERM/QUIT/TSTP/FPE, starts and detaches the handler thread. Registration validates that the signal is in the managed set and stores the handler. The handler thread waits synchronously for signals and invokes registered callbacks.

State and persistence: process-local static `handlers[NSIG]`. No persistence.

Dependencies/integration: requires pthreads, signal APIs, and `opr_Verify`. Exposed by `softsig.h`.

Risks and test signals: must be called before creating other threads so signal masks are inherited. Handler table updates are not locked. Fatal synchronous signals such as SEGV and BUS are deliberately excluded. Tests should send handled signals and verify callback/default behavior.
