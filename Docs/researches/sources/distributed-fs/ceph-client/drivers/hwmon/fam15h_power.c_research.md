# sources/distributed-fs/ceph-client/drivers/hwmon/fam15h_power.c

## Purpose
`fam15h_power.c` is a PCI hwmon driver for AMD Family 15h/16h northbridge function 4 devices. It exposes processor power limit, current socket power on supported Family 15h models, and accumulated compute-unit average power when the CPU advertises accumulated power MSR support.

## Important APIs, types, and functions
- `struct fam15h_power_data` stores the PCI device, fixed-point TDP scaling values, dynamically assembled hwmon attribute group, accumulated power MSR state per compute unit, online compute-unit flags, and the averaging interval.
- `power1_input_show()` reads D18F5 `REG_TDP_RUNNING_AVERAGE` and `REG_TDP_LIMIT3`, handles Carrizo-or-later bitfield widths, and reports current power in microwatts.
- `power1_crit_show()` reports processor TDP-derived critical power in microwatts.
- `do_read_registers_on_cu()` reads `MSR_F15H_CU_PWR_ACCUMULATOR` and `MSR_F15H_PTSC` on a representative CPU for a compute unit.
- `read_registers()` builds a cpumask containing one online CPU per compute unit and uses `on_each_cpu_mask()` under `cpus_read_lock()` to sample MSRs.
- `power1_average_show()` takes two MSR snapshots separated by `power_period` milliseconds, handles accumulator wrap, divides by PTSC delta, and sums online compute-unit power.
- `fam15h_power_init_attrs()` conditionally includes attributes based on CPU family/model and `X86_FEATURE_ACC_POWER`.
- `should_load_on_this_node()` avoids duplicate hwmon registration on secondary nodes when northbridge capability bits indicate it should not load.
- `tweak_runavg_range()` applies a BIOS workaround by changing running-average range from `0xe` to `0x9` on affected devices, and resume reapplies it.

## Control flow
The PCI driver matches AMD Family 15h and 16h northbridge function 4 device IDs. Probe first calls `tweak_runavg_range()` for every node because the counters cooperate across MCM nodes. It then filters duplicate nodes with `should_load_on_this_node()`, allocates data, initializes TDP/scaling data and attributes, saves the PCI device pointer, and registers a managed hwmon device with the generated groups.

If accumulated power is supported, initialization reads CPUID `0x80000007` ECX for sample ratio, reads the max CU accumulator MSR, sets a default 10 ms averaging interval, and samples initial registers. `power1_average` reads block for the configured interval using `schedule_timeout_interruptible()` before returning a computed average.

## State and persistence
Most state is derived from PCI config space and CPU MSRs at read time. `power1_average_interval` is mutable driver state in milliseconds, constrained to 1..1000, and affects subsequent `power1_average` reads. `tweak_runavg_range()` writes PCI config space and is re-run on resume. Accumulator snapshots are stored in `fam15h_power_data` only as transient samples.

## Dependencies and integration points
The driver depends on the PCI core, AMD northbridge function layout, x86 CPU topology helpers, CPUID feature bits, MSR access, CPU hotplug read locking, scheduler timeouts, and managed hwmon registration. It exports the standard power hwmon ABI: `power1_crit`, optionally `power1_input`, `power1_average`, and `power1_average_interval`.

## Risks
- `power1_average_show()` can block sysfs reads for up to one second by design; tests and userspace pollers must account for that.
- If CPUs go offline between the two samples, the code skips compute units not online in the second sample; averages can change abruptly around hotplug.
- Division by `tdelta` assumes PTSC advanced; unusual platform behavior could risk divide errors or invalid readings.
- Attribute availability depends on boot CPU family/model and feature bits, while PCI IDs include Family 16h devices. Wrong gating can expose unsupported registers or hide valid ones.
- `tweak_runavg_range()` mutates PCI config space as a firmware workaround; regressions can alter power management behavior.
- `power1_input_show()` uses bitfield widths that differ for Carrizo-or-later; incorrect model detection changes sign extension and scaling.

## Test signals
- Build on x86 with relevant PCI/MSR headers and verify no attribute-array sizing issues in `fam15h_power_init_attrs()`.
- Hardware tests should compare `power1_crit` against expected processor TDP scaling and validate `power1_input` on pre-Carrizo and Carrizo-or-later Family 15h models.
- Accumulated-power tests should read `power1_average` at multiple intervals, around CPU hotplug events, and with interrupted sleeps.
- Resume tests should confirm `REG_TDP_RUNNING_AVERAGE` is retweaked when needed.
- Negative tests should cover non-primary northbridge nodes and CPUs lacking `X86_FEATURE_ACC_POWER`.
