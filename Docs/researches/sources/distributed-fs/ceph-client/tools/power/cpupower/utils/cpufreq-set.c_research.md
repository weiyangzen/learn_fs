# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/cpufreq-set.c

## Purpose
Implements `cpupower frequency-set`, changing cpufreq minimum, maximum, governor, or fixed userspace frequency for selected CPUs.

## Important APIs, Types, and Functions
Key pieces are option table `set_opts`, `string_to_frequency` for parsing units from Hz through THz into kHz, `do_new_policy`, `do_one_cpu`, and `cmd_freq_set`. The command uses `cpufreq_set_frequency`, `cpufreq_modify_policy_min/max/governor`, `cpufreq_get_policy`, `cpufreq_set_policy`, and related-CPU discovery APIs.

## Control Flow, State, and Persistence
Parsing rejects duplicate options, invalid units, and mixing fixed `--freq` with policy options. With no global `--cpu` mask it sets all CPUs. With `--related`, it expands the selected bitmask to CPUs returned by `cpufreq_get_related_cpus`. It snapshots online/offline state with `get_cpustate`, applies each change only to online selected CPUs, and reports skipped offline CPUs. All state changes are kernel/sysfs cpufreq policy writes; no repository files are persisted.

## Dependencies and Integration Points
Depends on libcpupower cpufreq and cpuidle headers, global bitmasks from `cpupower.c`, and helper output routines. It is root-gated by the main dispatcher.

## Risks and Test Signals
Frequency parsing is hand-rolled and sensitive to rounding, leading zeros, multiple decimal points, and buffer length. Related-CPU list iteration may lose the original head before freeing depending on lib API expectations. Setting all CPUs can partially succeed before a later CPU fails. Test with unit-suffixed frequencies, duplicate options, offline CPUs, related policy domains, unavailable userspace governor, and invalid governor names.
