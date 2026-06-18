# sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/special-tests.sh

## Purpose

`special-tests.sh` contains targeted cpufreq regression and stress reproducers for governor switching lockdep reports, concurrent governor races, and CPU hotplug mixed with cpufreq file updates.

## Important APIs, Types, and Functions

It defines `__simple_lockdep()`, `simple_lockdep()`, `__concurrent_lockdep()`, `concurrent_lockdep()`, `quick_shuffle()`, `governor_race()`, `hotplug_with_updates_cpu()`, and `hotplug_with_updates()`. It writes `scaling_governor` and `scaling_min_freq`, reads governor tunables, and calls CPU reboot helpers.

## Control Flow

`simple_lockdep` switches each policy to `ondemand`, reads all ondemand files, then switches to `conservative`. `concurrent_lockdep` repeats that flow 101 times per policy in background. `governor_race` starts eight concurrent loops that rapidly tee `ondemand` and `userspace` into all policies. `hotplug_with_updates` reboots non-boot CPUs thousands of times while writing available frequencies into `scaling_min_freq`, then restores the old minimum.

## State and Persistence Behavior

The script heavily mutates governors, CPU online state, and minimum frequency settings. It launches background jobs and uses global sysfs paths set by `main.sh`.

## Dependencies and Integration Points

It depends on cpufreq policies supporting `ondemand`, `conservative`, and `userspace`, sudo availability for `quick_shuffle`, and CPU hotplug support. It integrates with lockdep and race detection via kernel logs rather than explicit assertions.

## Risks and Edge Cases

These tests are intentionally stressful and can destabilize cpufreq policy state or leave background jobs running until loops finish. `quick_shuffle` uses `sudo tee` despite the main script already requiring root. The script does not explicitly wait for all background jobs in every case.

## Test Signals

The primary signals are absence of kernel lockdep splats, warnings, hangs, or sysfs write failures during and after the stress loops. Dmesg captured by `main.sh` is important evidence.
