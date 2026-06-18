# sources/distributed-fs/ceph-client/drivers/hwmon/nct6775-core.c

## Purpose

`nct6775-core.c` is the shared hwmon implementation for the NCT6106/NCT6116/NCT6775/NCT6776/NCT6779/NCT679x family. It contains the chip-specific register tables, conversion helpers, cache refresh logic, sysfs attribute implementations, automatic fan-control handling, temperature source discovery, and the exported `nct6775_probe()` entry point used by both the platform/LPC frontend and the BMC-oriented I2C frontend.

## Important APIs, Types, and Functions

- `DEFAULT_SYMBOL_NAMESPACE "HWMON_NCT6775"` namespaces exported helpers for frontends.
- Per-chip register arrays and label tables define voltage, fan, PWM, alarm, beep, temperature, TSI, and Smart Fan register layouts for all supported variants.
- Conversion helpers include `fan_from_reg8/13/16/rpm()`, `fan_to_reg()`, `in_from_reg()`, `in_to_reg()`, `tsi_temp_from_reg()`, and PWM step-time conversion.
- Dynamic sysfs generation is handled by `sensor_device_template`, `sensor_device_attr_u`, `sensor_template_group`, and `nct6775_add_template_attr_group()`.
- `nct6775_reg_is_word_sized()` tells regmap frontends which logical registers require two byte accesses.
- `nct6775_update_device()` refreshes cached voltage, fan, PWM, temperature, TSI, alarm, and beep state with a 1.5-second cache window.
- `nct6775_update_pwm()` and `nct6775_update_pwm_limits()` collect fan-control mode, duty, target, tolerance, weight, and automatic curve data.
- Store callbacks such as `store_fan_min()`, `store_pwm_enable()`, `store_pwm_temp_sel()`, `store_auto_pwm()`, and `store_temp_type()` perform validated read-modify-write updates through `nct6775_write_value()`.
- `add_temp_sensors()` and the discovery loops in `nct6775_probe()` map hardware temperature source IDs into fixed and dynamic hwmon temp channels.
- `nct6775_probe()` initializes the regmap, selects the per-kind register map, discovers sensors, runs hardware and frontend initialization, creates attribute groups, and registers the hwmon device.

## Control Flow

Frontend drivers allocate and partially initialize `struct nct6775_data`, including `kind`, `driver_data`, optional `read_only`, and optional `driver_init`, then call `nct6775_probe()`. The core creates a regmap with frontend-supplied bus callbacks and initializes generic state such as `update_lock`, the chip name, bank cache, and default voltage scaling.

The large `switch (data->kind)` fills `struct nct6775_data` with chip-specific register pointers, feature counts, conversion functions, masks, labels, and limits. After that, the probe path determines all available voltage inputs by count, discovers temperature sources by reading `REG_TEMP_SOURCE`, opportunistically assigns unmonitored fan-control sources to available temperature monitor registers, adds alternate temperature registers, detects nonzero TSI temperature channels, starts monitoring/VBAT/temp inputs in `nct6775_init_device()`, then calls the frontend's `driver_init()` to detect bus-specific fan/PWM/VID/other state.

Once initialized, the core seeds fan divider/minimum state, creates repeated PWM, voltage, fan, temp, and optional TSI temp sysfs groups, and registers hwmon. Normal sysfs reads go through `nct6775_update_device()`, which refreshes all cache groups under `update_lock` when stale. Store paths validate input, update the cache, and write hardware through regmap. In read-only I2C mode, visibility is reduced by `nct6775_attr_mode()` but many store functions still exist behind permissions stripped by the mode.

## State and Persistence Behavior

`struct nct6775_data` is the core state object and is intentionally large: it stores constant per-kind register pointers, per-device feature masks, current register bank, cached readings, cached limits, fan divider state, temperature mappings, alarm/beep bitfields, and automatic fan-control tables. Cache validity is based on `last_updated` plus `valid`; failures during refresh return `ERR_PTR(err)` without updating the valid timestamp.

Writes change device registers and cached state but are not persisted outside hardware/firmware behavior. Some stores intentionally preserve related settings, such as fan min values when changing dividers and PWM floor enable bits in `REG_TEMP_SEL`. The core has no PM callbacks; platform PM support lives in `nct6775-platform.c`, while I2C mode is read-only and has no suspend/resume restoration.

## Dependencies and Integration Points

The core depends on `nct6775.h` for `struct nct6775_data`, shared constants, and inline regmap helpers. It integrates Linux hwmon sysfs conventions, regmap, mutex locking, `LM75_TEMP_FROM_REG/TO_REG`, `sysfs_emit`, nospec array indexing for user-selected temperature sources, and exported symbols consumed by `nct6775-platform.c` and `nct6775-i2c.c`.

## Risks and Edge Cases

- The per-kind switch is dense and pointer-heavy; a missing register pointer can hide attributes at best or dereference null in a path not guarded by visibility at worst.
- Many visibility callbacks depend on exact template ordering and hard-coded modulo arithmetic.
- Temperature source discovery changes hardware source registers for unmonitored fan-control sensors, which is helpful but can surprise firmware assumptions.
- `nct6775_update_device()` performs a large number of regmap operations under one mutex; slow or failing transports can block all sysfs access.
- Fan divider auto-selection changes hardware and fan-min encoding based on observed readings; tests need to cover boundary values and preservation of alarms.
- Several Smart Fan modes have chip-specific semantics, especially critical point enable/disable, `sf3` limited to NCT6775, and `sf4` requiring monotonic trip points.
- Alarm and beep bit mapping is indirect for temperatures because source registers, not fixed channel indexes, determine the bits.
- Frontends must provide correct word-size behavior and bank selection; otherwise the core's 16-bit temperature/fan handling breaks.

## Test Signals

High-value tests include per-kind probe table sanity, no-null register coverage for visible attributes, temperature source mapping with duplicates/invalid sources/alternate registers, TSI detection, cache refresh success and error propagation, read-only permission stripping, fan min/divider edge cases, all PWM enable modes and trip-point validation, temperature type writes, alarm/beep bit mapping, auto point read/write including critical points, and frontend integration tests through both direct platform and I2C regmap callbacks.
