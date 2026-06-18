# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/signal_tm.c

Purpose: verifies self-signalling from a suspended transaction and checks that the signal handler is not invoked while still in active transactional state.

Important APIs/types/functions: external `tm_signal_self()`, `signal_handler()`, `test_signal_tm()`, and TM helpers `have_htm()`, `htm_is_synthetic()`, `tcheck_active()`, and `tcheck_transactional()`.

Control flow: after installing handlers and skipping unsupported HTM, the loop calls `tm_signal_self()` repeatedly. A special untouched return sentinel means the transaction aborted too early and the iteration is retried. Otherwise the test expects a successful syscall result and eventual `SIGUSR1` delivery.

State and persistence behavior: global signal flags coordinate handler and main loop; per-iteration local sentinels distinguish abort timing from syscall failure.

Dependencies and integration points: built with `-mhtm`, `signal.S`, and `../tm/tm.h`.

Risks and test signals: HTM temporary aborts are expected. Persistent failures print TEXASR/TFIAR plus iteration context; alarms prevent indefinite waits.
