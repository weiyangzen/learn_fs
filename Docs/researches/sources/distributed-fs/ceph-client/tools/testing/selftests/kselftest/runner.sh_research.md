# sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest/runner.sh

`runner.sh` is the common shell runner for selftests in a directory. It applies settings, timeouts, per-test arguments, output prefixing, exit-code mapping, optional per-test logs, and optional network namespace execution.

It requires `BASE_DIR` before sourcing and imports `kselftest/ktap_helpers.sh`. Important variables are `timeout_rc=124`, `logfile`, `per_test_logging`, `per_test_log_dir`, `RUN_IN_NETNS`, and `kselftest_default_timeout=45`. Important functions are `tap_prefix()`, `tap_timeout()`, `run_one()`, `in_netns()`, `run_in_netns()`, and `run_many()`.

`run_one()` resets timeout, derives a sanitized `KSELFTEST_<TEST>_ARGS` variable name, reads optional `settings`, applies timeout override, selects an executable, `ksft_runner.sh`, or shebang interpreter, runs the test from its directory under `timeout` when available, prefixes output into the log, captures exit status, and emits KTAP pass/skip/xfail/timeout/fail. `run_many()` runs tests sequentially or dispatches them into temporary network namespaces and reconciles counters from child exit codes.

Dependencies are KTAP helpers, `timeout`, `stdbuf`, Perl or sed for prefixing, `tr`, `ip netns` for namespace mode, and per-test settings conventions. Risks include simple settings parsing with `eval`, command construction through `eval`, and subshell counter handling. Pass signals are prefixed logs, timeout reporting, and KTAP results matching child exit codes.
