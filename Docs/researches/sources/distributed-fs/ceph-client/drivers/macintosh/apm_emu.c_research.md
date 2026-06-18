# sources/distributed-fs/ceph-client/drivers/macintosh/apm_emu.c

Purpose: bridges PMU battery/AC state into the generic APM emulation layer on PMU-based PowerMac/PowerBook systems. It supplies `apm_get_power_status` so legacy APM userspace can read battery status even though the hardware is managed through the PMU driver.

Important APIs and functions: `pmu_apm_get_power_status()` fills `struct apm_power_info` from exported PMU globals: `pmu_power_flags`, `pmu_battery_count`, and `pmu_batteries[]`. `apm_emu_init()` installs the callback; `apm_emu_exit()` removes it if still installed.

Control flow: the callback initializes all fields to unknown/default values, reports AC online/offline from `PMU_PWR_AC_PRESENT`, aggregates present batteries, averages percentage by present battery count, sums charge and amperage, detects charging state, and computes approximate minutes remaining for discharging batteries. It maps percentage thresholds to critical, low, or high APM battery flags.

State and persistence: the module owns no persistent battery cache; all live state is read from PMU globals maintained by `via-pmu.c`. Its only persistent side effect is assigning the global APM callback pointer while loaded.

Dependencies and integration: depends on `linux/apm-emulation.h`, `linux/pmu.h`, and `linux/adb.h`. It assumes the PMU driver is present and updating battery records.

Risks: battery percentage divides by `max_charge`; malformed or zero PMU battery data would be hazardous. Time remaining uses legacy formulas that differ for smart and non-smart batteries and may be approximate. Concurrent reads of PMU globals are unsynchronized in this file.

Test signals: verify `/proc/apm` or equivalent APM consumers see AC status, charging, low, critical, and multi-battery average changes after PMU battery updates. Unload should clear `apm_get_power_status` only if no other provider replaced it.
