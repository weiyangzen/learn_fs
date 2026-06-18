# sources/distributed-fs/ceph-client/drivers/cpufreq/amd_freq_sensitivity.c

## Purpose

This module adds AMD/Hygon processor feedback support to the ondemand governor's powersave-bias hook. It reads hardware frequency-sensitivity MSRs and biases non-CPU-bound workloads toward lower frequencies.

## Important APIs, types, and functions

`struct cpu_data_t` caches previous actual/reference counters and the previous frequency decision per CPU. `amd_powersave_bias_target()` is the registered ondemand hook. `amd_freq_sensitivity_init()` validates vendor, optional chipset/feature presence, MSR readability, and class code before registering the handler through `od_register_powersave_bias_handler()`. Exit unregisters it.

## Control flow, state, and persistence

On each governor decision, the hook reads `MSR_AMD64_FREQ_SENSITIVITY_ACTUAL` and `REFERENCE`, masks the class bits, handles wrap or zero-delta cases by keeping current frequency, computes sensitivity from counter deltas, compares it with `od_tuners->powersave_bias`, and may clamp the next target down to current, minimum, or the next lower table entry. Per-CPU state is only the prior counter snapshot and previous frequency choice; nothing persists across module unload or reboot.

## Dependencies and integration points

The module depends on x86 MSR access, AMD/Hygon CPU feature detection, PCI probing for older platforms, and internal ondemand governor interfaces in `cpufreq_ondemand.h`. It integrates only with the ondemand governor; other governors do not use this hook.

## Risks and test signals

Risks include reliance on internal governor data structures, counter wrap handling, integer sensitivity calculation, and platform detection that may exclude valid hardware or include broken firmware. Test by loading on supported AMD/Hygon systems, verifying the handler registers, observing powersave-bias behavior under memory-bound versus CPU-bound workloads, and checking no divide-by-zero or invalid frequency-table index occurs.
