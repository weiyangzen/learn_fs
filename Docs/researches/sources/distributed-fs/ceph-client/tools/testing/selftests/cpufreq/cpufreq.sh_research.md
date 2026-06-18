# sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/cpufreq.sh

## Purpose

`cpufreq.sh` implements cpufreq policy enumeration, sysfs read/write sanity tests, frequency shuffling, suspend/resume validation, and the default basic cpufreq test sequence.

## Important APIs, Types, and Functions

Key functions include `cpu_should_have_cpufreq_directory()`, `for_each_policy()`, `for_each_policy_concurrent()`, `read_cpufreq_files_in_dir()`, `update_cpufreq_files_in_dir()`, `find_current_freq()`, `set_cpu_frequency()`, `test_all_frequencies()`, `shuffle_frequency_for_all_cpus()`, `cpufreq_basic_tests()`, and `do_suspend()`. It reads/writes `$CPUFREQROOT/policy*/scaling_*` and `$SYSFS/power/state`.

## Control Flow

Basic tests count cpufreq-managed CPUs, warn about unmanaged CPUs, recursively read all cpufreq files, rewrite writable files with their current values except `scaling_setspeed`, hotplug non-boot CPUs five times, cycle all available frequencies under the userspace governor, and shuffle all governors. Suspend modes validate sysfs power state, optionally use `rtcwake`, and run basic tests after resume.

## State and Persistence Behavior

It mutates cpufreq governor, frequency, writable policy attributes, CPU online state, and optionally system sleep state. Governor backup/restore is delegated to `governor.sh`; logs are printed to stdout and captured by `main.sh`.

## Dependencies and Integration Points

It requires `CPUROOT`, `CPUFREQROOT`, and `SYSFS` set by `main.sh`, plus helpers from `cpu.sh` and `governor.sh`. It exercises cpufreq core sysfs ABI, governors, hotplug interactions, and suspend/resume integration.

## Risks and Edge Cases

Recursive file rewriting can trigger side effects in writable cpufreq knobs. Frequency tests require `scaling_available_frequencies` and userspace governor support. Suspend/hibernate paths are intrusive and platform-dependent. Shell tests compare numeric strings with `=` and assume common sysfs file availability.

## Test Signals

Success is a complete basic run without `ktap_exit_fail_msg` and with printed cpufreq/dmesg dumps. Failures indicate missing cpufreq management, write rejection, hotplug regressions, unavailable governors/frequencies, or suspend resume cpufreq breakage.
