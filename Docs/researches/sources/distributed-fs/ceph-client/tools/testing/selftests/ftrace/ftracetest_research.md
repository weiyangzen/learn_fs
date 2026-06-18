<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/ftracetest -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/ftracetest

## Purpose
This shell harness discovers, filters, runs, logs, and summarizes ftrace and RV selftests from `test.d`.

## Important APIs, Types, And Functions
Important functions include `usage()`, `setup()`, `cleanup()`, `errexit()`, `absdir()`, `abspath()`, `find_testcases()`, `parse_opts()`, `strip_esc()`, `prlog()`, `catlog()`, `testcase()`, `checkreq()`, `test_on_instance()`, `ktaptest()`, `eval_result()`, `exit_pass()`, `exit_fail()`, `exit_unresolved()`, `exit_untested()`, `exit_unsupported()`, `exit_xfail()`, `__run_test()`, and `run_test()`. It sources `test.d/functions`.

## Control Flow
The script requires root, disables RT runtime throttling, locates or mounts tracefs/debugfs, parses options, prepares logs, discovers `.tc` files, then runs each test in tracefs with `set -e` and helper functions loaded. Signal traps map special exit helpers to Dejagnu-style result codes. Tests marked for instance mode are run again in a temporary trace instance. KTAP mode emits TAP version, plan, per-test lines, and totals.

## State And Persistence
It changes `/proc/sys/kernel/sched_rt_runtime_us`, may mount tracefs/debugfs, creates logs and `latest` symlink under `logs/`, exports temporary directories, creates/removes trace instances, and relies on `initialize_system`/`finish_system` from `test.d/functions` to reset tracing state.

## Dependencies And Integration Points
It integrates with tracefs/debugfs, ftrace test metadata (`# description`, `# requires`, `# flags`), kselftest skip code, KTAP output, and RV tests under tracefs `rv`.

## Risks
Global scheduler RT runtime is modified for the duration and must be restored. Test scripts run sourced in a shell with `set -e`, so cleanup in individual cases must be robust. Mount discovery and user-provided log paths can affect host state.

## Test Signals
Signals include correct root/tracefs skip behavior, per-test PASS/FAIL/UNSUPPORTED/UNRESOLVED accounting, cleanup of temporary trace instances, restored RT runtime, and valid KTAP totals in `-K` mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/ftracetest -->
