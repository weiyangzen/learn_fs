# sources/distributed-fs/ceph-client/drivers/power/supply/apm_power.c

## Purpose
`apm_power.c` bridges the power-supply subsystem to legacy APM emulation. It selects a main battery, converts power-supply status/capacity/time properties into `struct apm_power_info`, and installs itself as the global `apm_get_power_status` callback.

## Important APIs, Types, And Functions
- `main_battery` caches the selected power supply during a status query; `apm_mutex` serializes selection and reporting.
- `struct find_bat_param` tracks explicit `use_for_apm`, maximum charge battery, maximum energy battery, and fallback battery candidates.
- `find_main_battery()` and `__find_main_battery()` select the reporting battery, preferring `desc->use_for_apm`, then largest charge/energy capacity, then a fallback last battery.
- `do_calculate_time()` computes minutes to full/empty from energy, charge, or voltage quantities and current.
- `calculate_time()` tries energy, charge, then voltage sources.
- `calculate_capacity()` computes percent from energy, charge, or voltage full/empty/current values.
- `apm_battery_apm_get_power_status()` fills APM AC line status, battery status/flag/life, time units, and time remaining.

## Control Flow
Module init assigns `apm_get_power_status`. Each APM query locks the mutex, scans registered power supplies for a main battery, reads status, derives AC line state, gets or computes capacity, maps capacity/status to APM battery status, and obtains time from native time-to-full/empty properties or calculated fallbacks. Module exit clears the global callback if it is still installed.

## State And Persistence
There is no persistent state. `main_battery` is recalculated on each query under `apm_mutex`, so hotplugged batteries can be reflected. The global callback pointer is process-wide kernel state changed at module load/unload.

## Dependencies And Integration Points
The file depends on `linux/apm-emulation.h`, the power-supply class, and power-supply drivers exposing standard battery properties. It is a compatibility layer rather than a hardware driver.

## Risks
- Selection heuristics can choose an arbitrary battery when several batteries expose incomplete or incomparable energy/charge data.
- Calculations assume compatible units and signs across current, energy, charge, and voltage properties. Incorrect current sign can invert time estimates.
- `do_calculate_time()` uses `POWER_SUPPLY_PROP_CHARGE_EMPTY` as the fallback design property in the energy path, which looks suspicious and may reduce fallback accuracy.
- Capacity/time fallbacks may return `-1`; downstream APM consumers must tolerate unknown values.
- The global `apm_get_power_status` hook can conflict with another provider if load ordering changes, though exit only clears if it still owns the hook.

## Test Signals
- Use fake power supplies to cover explicit `use_for_apm`, largest charge, largest energy, mixed charge/energy with voltage comparison, and no battery.
- Verify APM mappings for charging, not charging, full, discharging, unknown status, high/low/critical thresholds, and AC line state.
- Exercise native time-to-full/empty paths and calculated energy/charge/voltage fallback paths, including zero current and missing properties.
- Module unload should leave `apm_get_power_status` untouched if another provider replaced it.
