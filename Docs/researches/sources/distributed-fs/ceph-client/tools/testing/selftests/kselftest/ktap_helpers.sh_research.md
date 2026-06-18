# sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest/ktap_helpers.sh

`ktap_helpers.sh` provides shell functions for KTAP/TAP output and kselftest exit statuses. Shell tests and runners source it to get consistent result formatting.

Important globals are `KTAP_TESTNO`, pass/fail/xfail/skip counters, `KSFT_PASS`, `KSFT_FAIL`, `KSFT_XFAIL`, `KSFT_XPASS`, `KSFT_SKIP`, and `KSFT_NUM_TESTS`. Public functions print headers/messages/plans, skip all tests, emit pass/fail/xfail/xpass/skip results, print counters, finish, and exit with pass/fail/skip.

State is global in the sourcing shell. Each result helper prints an `ok` or `not ok` line with the current test number, increments a counter, and advances the number. Finish helpers compare counters to the plan, print totals, and exit. Subshell users must reconcile counters manually.

Dependencies are shell builtins and kselftest runner conventions. Integration points include `runner.sh`, `kho/vmtest.sh`, and other shell selftests. Risks are global state collisions and direct echoing of message text. Pass signals are monotonic test numbering, correct totals, and standard exit codes.
