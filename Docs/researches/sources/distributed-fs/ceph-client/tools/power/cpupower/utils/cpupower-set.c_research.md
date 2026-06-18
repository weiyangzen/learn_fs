# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/cpupower-set.c

## Purpose
Implements the generic `cpupower set` command for performance bias, energy performance preference, AMD pstate mode, and turbo/boost toggles.

## Important APIs, Types, and Functions
Key entry point is `cmd_set`. Options are `--perf-bias`, `--epp`, `--amd-pstate-mode`, `--turbo-boost`, and alias `--boost`. It calls `cpupower_intel_set_perf_bias`, `cpupower_set_epp`, `cpupower_set_amd_pstate_mode`, `cpupower_set_intel_turbo_boost`, and `cpupower_set_generic_turbo_boost`.

## Control Flow, State, and Persistence
After rejecting POWER machines and parsing options, command-level settings such as AMD pstate mode and turbo boost are applied once. Then, with no selected CPU mask, it targets all CPUs and iterates online selected CPUs for per-CPU perf-bias and EPP writes. State changes persist in kernel sysfs/MSR-backed interfaces until changed by the kernel, firmware, or later user commands.

## Dependencies and Integration Points
Depends on global CPU vendor/capability discovery, sysfs helpers, bitmask helpers, and root gating in the main dispatcher. The boost path integrates Intel-specific `intel_pstate/no_turbo` with a generic `/sys/devices/system/cpu/cpufreq/boost` fallback.

## Risks and Test Signals
Partial updates are possible if one CPU write fails after previous CPUs succeeded. AMD mode validation only checks vendor and string length, leaving mode validity to sysfs. The `--boost` alias shares the same short option as `--turbo-boost`. Test range validation, invalid EPP/mode strings, Intel and generic boost paths, offline CPUs, and mixed CPU masks.
