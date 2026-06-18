# sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/governor.sh

## Purpose

`governor.sh` provides governor discovery, switching, file inspection, and restore helpers for cpufreq tests.

## Important APIs, Types, and Functions

It defines `find_gov_directory()`, `find_current_governor()`, `backup_governor()`, `restore_governor()`, `__switch_governor()`, `__switch_governor_for_cpu()`, `switch_governor()`, `switch_show_governor()`, `call_for_each_governor()`, and `shuffle_governors_for_all_cpus()`. Global `CUR_GOV` and `CUR_FREQ` store backup state.

## Control Flow

For each policy, callers back up the current governor and, if it is `userspace`, the current frequency. The script reads `scaling_available_governors`, switches to each governor, optionally dumps governor-specific tunables, and restores the original governor/frequency after the loop.

## State and Persistence Behavior

It mutates `scaling_governor` and sometimes `scaling_setspeed`. Backup state is held in global shell variables, so concurrent policy operations can overwrite backups if not used carefully.

## Dependencies and Integration Points

It depends on `$CPUFREQROOT`, `$CPUROOT`, cpufreq sysfs files, and helper functions from `cpufreq.sh`. It is used by basic tests, module tests, and special lockdep/race reproducers.

## Risks and Edge Cases

The backup variables are global rather than per-policy. `switch_show_governor()` assigns `cur_gov=find_current_governor` without command substitution, but this local value is not used for restore. Missing governor directories are reported as `INVALID` but still passed to recursive readers if callers do not guard.

## Test Signals

Pass signals are successful governor writes, readable governor tunables for dynamic governors, and restored original governor/frequency. Failures show unsupported governors or cpufreq policy state corruption.
