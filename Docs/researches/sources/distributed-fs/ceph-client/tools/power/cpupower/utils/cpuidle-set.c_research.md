# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/cpuidle-set.c

## Purpose
Implements `cpupower idle-set`, enabling or disabling cpuidle states by explicit state index, by maximum latency threshold, or by enabling all disabled states.

## Important APIs, Types, and Functions
Key API is `cmd_idle_set`; options are `--disable`, `--enable`, `--disable-by-latency`, and `--enable-all`. It uses `cpuidle_state_count`, `cpuidle_is_state_disabled`, `cpuidle_state_latency`, and `cpuidle_state_disable` plus global CPU state helpers.

## Control Flow, State, and Persistence
The command parses exactly one action. With no selected CPU mask it targets all CPUs, snapshots online/offline state, skips offline CPUs, and for each online CPU applies the requested state mutation. The latency mode disables enabled states whose latency is at or above the threshold and re-enables disabled states below the threshold. Persistence is entirely through kernel cpuidle sysfs `disable` files.

## Dependencies and Integration Points
Depends on libcpuidle/libcpufreq headers, global bitmask state, and helper routines from `helpers.h`. The main dispatcher requires root for this command.

## Risks and Test Signals
No action defaults to the `default` switch branch and exits as invalid; callers must pass one mutation option. Error handling reports per-state failures but often continues, so partial changes are possible. Test invalid numeric arguments, unsupported disable files, threshold boundary behavior, offline CPUs, and all-state re-enable on kernels with mixed disabled states.
