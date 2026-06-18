# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/ksft.py

## Purpose
This module implements a Python kselftest/KTAP runner and assertion library for networking tests.

## Important APIs and Types
Exception types `KsftFailEx`, `KsftSkipEx`, `KsftXfailEx`, and `KsftTerminate` encode test outcomes. Assertion helpers include `ksft_eq`, `ksft_ne`, `ksft_true`, `ksft_not_none`, `ksft_in`, `ksft_not_in`, `ksft_is`, `ksft_ge`, `ksft_gt`, `ksft_lt`, and context manager `ksft_raises`. `ksft_busy_wait` polls a condition. `ktap_result` emits one KTAP result line. `ksft_disruptive` skips tests when `DISRUPTIVE` disables disruptive cases. `ksft_variants` and `KsftNamedVariant` generate parameterized cases. `ksft_setup`, `ksft_run`, `ksft_flush_defer`, and `ksft_exit` manage execution.

## Control Flow and State
`ksft_run` parses `-h`, `-l`, `-t`, and `-T`, generates case tuples from explicit cases or globals/prefix discovery, emits `TAP version 13` and the plan, then runs each case with deferred cleanup armed. Failures set global `KSFT_RESULT`; aggregate status is held in `KSFT_RESULT_ALL`. `SIGTERM` is trapped to allow cleanup on runner timeouts. Deferred cleanup uses `utils.GLOBAL_DEFER_QUEUE`, flushed after every case.

## Dependencies and Integration
It depends on standard Python modules plus sibling `utils`. Tests such as `link_netns.py` call `ksft_run([...])` and `ksft_exit()`. The command-line filters mirror common kselftest needs for listing and selecting cases.

## Risks and Test Signals
`KSFT_RESULT` prevents multiple `ksft_run()` invocations in one process. Assertions mark failure but do not raise, so tests continue unless they raise explicitly. Deferred cleanup exceptions convert a test to failure. Pass/fail signals are KTAP lines and the final totals line; process exit is controlled by `ksft_exit`.
