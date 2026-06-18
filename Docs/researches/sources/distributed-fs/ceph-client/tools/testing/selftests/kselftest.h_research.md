# sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest.h

`kselftest.h` is the low-level C reporting API for Linux selftests that do not use `kselftest_harness.h`. It emits TAP output, tracks result counters, and exits with standard kselftest status codes.

Important definitions are `KSFT_PASS`, `KSFT_FAIL`, `KSFT_XFAIL`, `KSFT_XPASS`, `KSFT_SKIP`, `ARRAY_SIZE`, optional x86 `__cpuid_count`, and `struct ksft_count`. Important functions/macros include `ksft_print_header()`, `ksft_set_plan()`, `ksft_print_cnts()`, `ksft_print_msg()`, `ksft_perror()`, `ksft_test_result_*()`, `ksft_test_result_code()`, `ksft_exit_*()`, `ksft_finished()`, `ksft_min_kernel_version()`, and `ksft_reset_state()`.

State is static and process-local: counters for pass/fail/xfail/xpass/skip/error, a plan count, and a debug flag. Tests print a TAP header and plan, emit result lines, and finish through an exit helper. Result helpers increment counters before deriving the visible test number. `ksft_exit_skip()` prints either `1..0 # SKIP` or a skip result depending on whether a plan/results already exist.

Dependencies are libc unless `NOLIBC` is defined, and runner scripts that interpret TAP and exit codes. Risks include the debug-message helper passing `va_list` through varargs incorrectly and xpass counting as acceptable in `ksft_finished()`. Pass signals are correct TAP version, plan, ordered results, totals, and exit code.
