# sources/distributed-fs/ceph-client/drivers/cpufreq/amd-pstate-ut.c

## Purpose

This module is an in-kernel unit-test harness for the AMD P-State driver. It validates platform prerequisites, driver enablement, CPPC performance/frequency data, EPP sysfs behavior, mode transitions, and the dynamic frequency-attribute set exposed by `amd-pstate.c`.

## Important APIs, types, and functions

`struct amd_pstate_ut_struct` maps test names to callbacks, with `test_list` allowing a comma-delimited module parameter filter. Test cases include `amd_pstate_ut_acpi_cpc_valid()`, `amd_pstate_ut_check_enabled()`, `amd_pstate_ut_check_perf()`, `amd_pstate_ut_check_freq()`, `amd_pstate_ut_epp()`, `amd_pstate_ut_check_driver()`, and `amd_pstate_ut_check_freq_attrs()`. It calls exported AMD pstate helpers such as `amd_pstate_get_status()`, `amd_pstate_update_status()`, `amd_pstate_get_mode_string()`, `store_energy_performance_preference()`, `show_energy_performance_preference()`, `amd_pstate_clear_dynamic_epp()`, and `amd_pstate_get_current_attrs()`.

## Control flow, state, and persistence

`amd_pstate_ut_init()` iterates the static test table at module load and skips tests not present in `test_list`. Most tests walk online CPUs via cpufreq policies and inspect per-policy `struct amd_cpudata`. The EPP test temporarily disables dynamic EPP, switches to active mode, writes all raw EPP values from 0 through 255, checks readback, then checks string preferences before restoring the original mode. The driver-transition test walks all mode pairs. The module stores no persistent state except transient mode/EPP changes that it tries to restore before returning.

## Dependencies and integration points

The test depends on ACPI CPPC, x86 CPPC MSRs, cpufreq policy access, AMD pstate private data from `amd-pstate.h`, and CPU feature detection. It integrates tightly with AMD pstate global mode switching and sysfs preference helpers, so failures are direct regression signals for the production driver.

## Risks and test signals

The test mutates global AMD pstate mode and per-policy EPP, so early exits can leave altered driver state if restore paths fail. It assumes policy driver data is `struct amd_cpudata` and that CPU0 is representative for EPP testing. Strong signals are successful module load logs for every case, valid CPPC perf ordering, frequency invariants matching policy limits, EPP roundtrips, and exact expected visibility of prefcore/EPP/floor-frequency attributes in passive, active, and guided modes.
