<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rds/run.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/rds/run.sh

## Purpose

`run.sh` is the RDS selftest runner. It validates environment and kernel configuration, runs the Python RDS traffic test under `strace`, captures logs and dmesg, and optionally collects RDS-specific GCOV coverage.

## Important APIs, Types, and Functions

Important helpers are `check_gcov_env`, `check_gcov_conf`, `check_conf_enabled`, `check_conf_disabled`, `check_conf`, and `check_env`. It sources `include.sh` when available to find `mk_build_dir`, sources `settings` for timeout, derives `ksrc_dir`, `.config`, and `net/rds`, and runs `strace -T -tt -o <trace> python3 test.py --timeout ... -d ... -l ... -c ... -u ...`. Coverage collection reads `*.gcda` from `/sys/kernel/debug/gcov` and invokes `gcovr`.

## Control Flow

The script parses log directory and netem percentages, validates required tools and Python version, checks kernel config and optional GCOV config, recreates the log and coverage directories, runs `test.py` with `set +e`, saves `dmesg`, conditionally exports coverage data and produces an HTML report, prints PASS/FAIL, and exits with the Python test's return code.

## State and Persistence Behavior

It writes logs under the selected log directory, defaulting to a directory beside the script, including `rds-strace.txt`, `dmesg.out`, pcaps produced by `test.py`, and optional `coverage/gcovr*` output. It may copy GCOV data from debugfs into the source/object tree paths expected by gcov tooling. It does not itself clean network namespaces; `test.py` owns test topology lifecycle poorly if interrupted.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies include a configured kernel source tree, `strace`, `tcpdump`, Python 3.9 or newer, RDS/RDS_TCP, netem, veth, namespaces, disabled modules, optional `gcov`/`gcovr`, and debugfs GCOV for coverage. Integration points are RDS kernel config, RDS TCP transport, sysctl reset coverage, and kselftest skip code 4. Risks are version mismatch between gcc and gcov, absent source tree in installed environments, stale `include.sh`, missing `gcovr`, destructive log directory removal, and coverage collection requiring privileges. Signals are `PASS: Test completed successfully`, nonzero Python return generating `FAIL`, strace/dmesg artifacts, and optional coverage HTML.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rds/run.sh -->
