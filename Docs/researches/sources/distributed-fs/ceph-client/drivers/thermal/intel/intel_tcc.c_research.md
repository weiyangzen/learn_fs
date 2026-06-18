# sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_tcc.c

## Purpose

`intel_tcc.c` is a library for Intel Thermal Control Circuitry MSR access. It provides model-specific masks for TCC offset and temperature readouts, TjMax lookup, TCC offset get/set, and current core/package temperature reads.

## Important APIs, Types, and Functions

`struct temp_masks` stores per-model bitmasks. `intel_tcc_init()` selects masks during `subsys_initcall`. Exports are `intel_tcc_get_offset_mask()`, `intel_tcc_get_tjmax()`, `intel_tcc_get_offset()`, `intel_tcc_set_offset()`, and `intel_tcc_get_temp()`. `get_temp_mask()` chooses core or package digital readout mask.

## Control Flow

Early init matches a long CPU model table and copies matching masks, otherwise defaults are used. Getters read MSRs on any CPU or a specified CPU. Setting offset validates support/range, checks the MSR lock bit, updates bits 24+ with the model mask, and writes back. Temperature reads require valid status bit and return `TjMax - digital_readout` in Celsius.

## State and Persistence Behavior

The selected `intel_tcc_temp_masks` is `__ro_after_init`. Hardware TCC offset persists in `MSR_IA32_TEMPERATURE_TARGET` until changed/reset. No dynamic allocation occurs.

## Dependencies and Integration Points

It depends on x86 CPU matching, MSR helpers, Intel family IDs, and exports namespace `INTEL_TCC`. Processor thermal, DTS, TCC cooling, and package temperature drivers use it.

## Risks and Test Signals

Risks include model mask table drift, MSR access failures on offline CPUs, lock-bit denial, invalid status bit returning `-ENODATA`, and unit expectations by callers. Test signals include model-specific mask selection, TjMax zero handling, offset set range/lock checks, core/package temp reads, and builds for namespace imports.
