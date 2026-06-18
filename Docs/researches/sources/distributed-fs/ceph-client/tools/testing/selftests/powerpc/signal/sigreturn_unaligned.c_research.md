# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/sigreturn_unaligned.c

Purpose: validates that returning from a signal to an unaligned NIA does not trigger problematic kernel warnings or crashes.

Important APIs/types/functions: `sigusr1_handler()` ORs the low two bits into `UCONTEXT_NIA()`, and `test_sigreturn_unaligned()` installs it and raises `SIGUSR1`.

Control flow: the test registers a SA_SIGINFO handler, raises SIGUSR1 once, and returns. The handler mutates the saved next instruction address to be unaligned before sigreturn.

State and persistence behavior: no persistent state. The only state change is the signal frame's NIA modification.

Dependencies and integration points: uses `ucontext_t` and powerpc `UCONTEXT_NIA()` helper from `utils.h`.

Risks and test signals: this is mainly a kernel robustness smoke test. A pass is simply returning from `raise()` without fatal signal or harness failure.
