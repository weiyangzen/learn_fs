# sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest/ksft.py

`ksft.py` is a Python helper for kselftest-style TAP output and exit codes. It mirrors a small subset of the C helper for Python tests.

Important state is `ksft_cnt`, `ksft_num_tests`, and `ksft_test_number`. Constants are `KSFT_PASS`, `KSFT_FAIL`, and `KSFT_SKIP`. Public functions include `print_header()`, `set_plan()`, `print_cnts()`, `print_msg()`, result helpers for pass/fail/skip, `test_result()`, `finished()`, `exit_fail()`, and `exit_pass()`.

Control flow is direct: tests call header/plan, emit result lines through `_test_print()`, then call `finished()` or an exit helper. `finished()` exits success only when pass plus skip equals the plan. The helper prints totals with xfail/xpass/error fixed at zero.

Dependencies are only Python `sys`. Integration is with Python selftests and the common runner's TAP/exit-code expectations. Risks are the lack of xfail/xpass/error support and no detailed plan mismatch reporting. Pass signals are well-formed TAP lines and correct exit code 0 when planned tests pass or skip.
