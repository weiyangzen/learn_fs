# sources/compression/xz/tests/tuktest.h

Purpose: standalone C99/C11 test framework for small XZ test programs. It provides test registration, pass/fail/skip/error accounting, optional TAP output, optional coloring, allocation cleanup, file-loading helpers, and assertion macros.

Important APIs/types/functions: public macros include `tuktest_start`, `tuktest_run`, `tuktest_end`, `tuktest_early_skip`, `tuktest_error`, `tuktest_malloc`, `tuktest_free`, `tuktest_file_from_srcdir`, `tuktest_file_from_builddir`, `assert_fail`, `assert_skip`, `assert_error`, `assert_true`, `assert_false`, integer, enum, bit, string, and array assertions. Internal state includes `enum tuktest_result`, `tuktest_stats`, `tuktest_argc`, `tuktest_argv`, `tuktest_name`, `tuktest_jmpenv`, and allocation-record lists.

Control flow: `tuktest_start` records `argc/argv` and prints a header. `tuktest_run_test` optionally filters by test name, sets a `setjmp` target, calls the test, and uses `longjmp` results from assertions to count fail/skip/error. Hard errors exit through `tuktest_end`. `tuktest_end` frees tracked allocations, prints TAP or summary output, checks stdout errors, and returns Automake-compatible exit status. File helpers validate names, size, emptiness, and read completeness before returning managed buffers.

State and persistence: state is process-global in static variables. `tuktest_malloc` tracks allocations separately for per-test and global lifetimes and frees them at test end or program end. File helpers read from `srcdir` or the build directory but do not write.

Dependencies and integration: depends on standard C headers and optional `PRIu64` availability. Integrated by XZ test programs through `tests.h` or direct inclusion. Exit codes are designed for Automake, Meson, and CMake with `SKIP_RETURN_CODE 77`.

Risks: assertions are only valid under `tuktest_run`; using them elsewhere is undefined by design. The framework uses global state, `setjmp`/`longjmp`, and process exit for hard errors, so it is not thread-safe and not suitable for embedding in long-lived processes. TAP mode always exits success, relying on TAP consumers for interpretation.

Test signals: produces concise per-test result lines and final totals, supports command-line selection by test function name, and reports mistyped test names as hard errors when fewer tests run than requested.
