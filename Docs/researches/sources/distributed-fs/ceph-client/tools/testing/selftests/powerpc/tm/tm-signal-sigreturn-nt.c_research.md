# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-sigreturn-nt.c

Purpose: tests returning from a signal handler while CPU is suspended in a transaction but the user context does not explicitly set MSR transaction-state bits.

Important APIs/types/functions: `trap_signal_handler()` executes `tbegin.; tsuspend.;` and advances saved NIP; `tm_signal_sigreturn_nt()` installs it for SIGTRAP and raises SIGTRAP.

Control flow: after HTM skips, SIGTRAP enters the handler, which creates a suspended transaction and adjusts NIP to skip the trap on return. The test succeeds if sigreturn handles this state without crashing.

State and persistence behavior: no external state; CPU TM state is intentionally altered inside the handler.

Dependencies and integration points: real HTM and powerpc ucontext register access are required.

Risks and test signals: this is a robustness test with success as normal return. Synthetic TM is skipped.
