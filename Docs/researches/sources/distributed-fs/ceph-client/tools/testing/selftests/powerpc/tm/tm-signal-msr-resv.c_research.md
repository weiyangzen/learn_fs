# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-msr-resv.c

Purpose: verifies sigreturn rejects reserved TM MSR transaction-state bit combinations by delivering SIGSEGV instead of crashing.

Important APIs/types/functions: `signal_usr1()` sets `uc_link` and ORs invalid TM bits into saved MSR; `signal_segv()` exits success only when `segv_expected` is set; `tm_signal_msr_resv()` installs both handlers.

Control flow: after HTM skip, the test raises SIGUSR1. The handler mutates the signal context to invalid TM state and marks SIGSEGV expected. Returning from the handler should trigger kernel validation and SIGSEGV, which exits 0.

State and persistence behavior: global `segv_expected` synchronizes expected failure path.

Dependencies and integration points: handles different 64-bit vs 32-bit mcontext MSR access paths and uses `tm.h`.

Risks and test signals: reaching normal control flow after `raise()` is failure. Success is an expected SIGSEGV caught by the handler.
