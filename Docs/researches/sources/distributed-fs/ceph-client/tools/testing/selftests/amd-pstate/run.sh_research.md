# sources/distributed-fs/ceph-client/tools/testing/selftests/amd-pstate/run.sh

Purpose: main AMD P-state kselftest driver that validates prerequisites, parses options, dispatches basic/tbench/gitsource/all tests, and manages shared environment.

Important APIs/types/functions: inclusion guard `FILE_MAIN`; sources `basic.sh`, `tbench.sh`, `gitsource.sh`; globals for tracer/perf/sysfs/output/loop/timing; helpers `scaling_name()`, `count_cpus()`, governor backup/restore/switch, `amd_pstate_all()`, `help()`, `parse_arguments()`, prerequisite command checks, `prerequisite()`, `do_test()`, cleanup helpers.

Control flow: parse CLI, verify x86 AMD CPU, verify current scaling driver or comparative driver, require root-like `/dev` write access, check perf/tbench as needed, locate sysfs/cpufreq, clear dumps, run selected function through `tee`, then remove transient logs.

State and persistence: reads `/proc/cpuinfo` and sysfs, modifies cpufreq governors, writes output CSV/log/PNG files through sourced scripts, and removes some logs at end.

Dependencies/integration: kselftest invokes this script; depends on shell utilities, cpufreq sysfs, perf, tbench/dbench, tracer scripts, and root privileges.

Risks and test signals: message uses `COMPARISON_TEST` typo instead of `COMPARATIVE_TEST`; `cat /proc/cpuinfo | grep` is inefficient but harmless. Governor mutation is invasive; failed exits can leave governors changed if restoration is bypassed.
