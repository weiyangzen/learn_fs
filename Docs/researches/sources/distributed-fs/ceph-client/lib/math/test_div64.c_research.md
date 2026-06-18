# sources/distributed-fs/ceph-client/lib/math/test_div64.c

Purpose: Loadable test module for `do_div()` 64-bit dividend / 32-bit divisor quotient and remainder behavior.

Important APIs/types/functions: Contains fixed dividend/divisor vectors, expected quotient/remainder matrix, `test_div64_one()` macro, `test_div64()`, and module init/exit.

Control flow: For each dividend it tests every divisor both as compile-time constants and as variables, so constant-optimized and generic `do_div` paths are exercised. Init repeats the full matrix `TEST_DIV64_N_ITER` times and prints elapsed time.

State and persistence: No persistent state; results are emitted through kernel logging.

Dependencies/integration: Built by `CONFIG_TEST_DIV64`, depends on `asm/div64.h`, timekeeping, module init.

Risks: Stops at first failure and still returns 0 from init, so logs are the main failure signal.

Test signals: The file itself is the test signal, with broad edge vectors including near-maximum dividends and divisors.
