
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/lib_sh_test.sh

Purpose: Unit-style selftest for `lib.sh` result semantics, especially `RET`, `retmsg`, `FAIL_TO_XFAIL`, skip handling, slow-machine xfail behavior, and final `EXIT_STATUS`.

Important APIs/functions: simulated checks `tpass`, `tfail`, `txfail`; simulated tests `pass`, `fail`, `xfail`, `skip`, `slow_xfail`; verifiers `ret_tests_run`, `ret_subtest`, `test_ret`, `exit_status_tests_run`, `exit_status_subtest`, `test_exit_status`.

Control flow: sets `NUM_NETIFS=0`, sources `lib.sh`, then runs two meta-tests. `test_ret` invokes check helpers directly in subshells and asserts resulting return code/message. `test_exit_status` sets `TESTS` and runs `tests_run` in subshells to verify final status precedence.

State/persistence: no network devices are needed. It mutates shell globals `RET`, `EXIT_STATUS`, `retmsg`, `TESTS`, `FAIL_TO_XFAIL`, and `KSFT_MACHINE_SLOW` only within current/subshell contexts.

Dependencies/integration: depends on `lib.sh` being sourceable with zero interfaces and on parent kselftest status constants (`ksft_pass`, `ksft_fail`, `ksft_xfail`, `ksft_skip`).

Risks: because it tests shell-global behavior, accidental leakage between subshell and parent would mask bugs. It traps `pre_cleanup`, not full network cleanup, because no topology is created.

Test signals: logs expected transitions for check return aggregation and final exit status across combinations of pass/fail/xfail/skip and slow-machine flags.
