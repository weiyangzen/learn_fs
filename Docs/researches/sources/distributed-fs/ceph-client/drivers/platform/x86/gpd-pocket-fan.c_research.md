## sources/distributed-fs/ceph-client/drivers/platform/x86/gpd-pocket-fan.c

Purpose: controls the GPD Pocket fan through two GPIO lines, using CPU thermal zones and AC-power status to choose a fan speed from 0 to 3.

Important APIs/types/functions: `struct gpd_pocket_fan_data` stores device, two thermal zones (`soc_dts0`, `soc_dts1`), two GPIO descriptors, delayed work, and last speed. Module parameters `temp_limits`, `hysteresis`, and `speed_on_ac` tune thresholds. `gpd_pocket_fan_worker()` reads both thermal zones, uses the maximum temperature, enforces minimum speed on AC power, applies hysteresis before lowering speed, kick-starts from off by briefly selecting max speed, sets GPIO outputs, and reschedules itself with a speed-dependent interval. PM callbacks stop work and set minimum speed on suspend, then force update on resume.

Control flow: ACPI platform probe validates module parameters, allocates state, creates autocancel delayed work, obtains thermal zones by name, gets two GPIOs, forces an immediate update, and stores driver data. The worker then runs continuously on `system_percpu_wq`.

State and persistence: fan speed is tracked only in `last_speed`; hardware GPIO state reflects the last selected speed. Module parameters are read-only at runtime. No firmware settings are persisted.

Dependencies and integration: ACPI platform matching for `FAN02501`, thermal zone API, GPIO descriptor API, power-supply `power_supply_is_system_supplied()`, delayed work, and PM sleep callbacks.

Risks: missing thermal zones defer probe; temperature read failures force max speed for safety. Threshold arrays are validated for range but not monotonic order. GPIO direction is set on every speed change. Test signals include invalid parameter normalization, AC vs battery minimum speed, hysteresis lowering, kick-start from off, thermal read failure, suspend/resume behavior, GPIO bit patterns for speeds 0..3, and probe deferral until thermal zones exist.
