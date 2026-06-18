# sources/distributed-fs/ceph-client/drivers/thermal/khadas_mcu_fan.c

Purpose: cooling-device driver for Khadas boards where an MCU controls fan speed. It exposes four cooling states, 0 through `MAX_LEVEL` 3, and writes the selected level to the parent Khadas MCU regmap.

Important APIs/types/functions: `struct khadas_mcu_fan_ctx` stores the parent `struct khadas_mcu`, cached fan level, and registered cooling device. `khadas_mcu_fan_set_level()` writes `KHADAS_MCU_CMD_FAN_STATUS_CTRL_REG` through regmap and updates the cache only on success. `khadas_mcu_fan_get_max_state()`, `get_cur_state()`, and `set_cur_state()` implement `thermal_cooling_device_ops`. Probe gets parent driver data, allocates context, and registers a named cooling device with `devm_thermal_of_cooling_device_register()`.

Control flow: thermal governors call `set_cur_state()`, which bounds-checks the state, avoids duplicate writes, and forwards changes to the MCU. Shutdown unconditionally requests level 0. Suspend saves the current level, stops the fan, then restores the cached level so resume can reapply it. Resume writes the cached level.

State/persistence: the only software state is `ctx->level`; actual persistence is in MCU state after regmap writes. Suspend deliberately leaves the cached level unchanged while forcing hardware off. Dependencies/integration: parent MFD `khadas-mcu`, regmap, thermal cooling-device framework, platform ID `khadas-mcu-fan-ctrl`, and the parent OF node for cooling maps.

Risks: if regmap writes fail during shutdown the error is ignored; the cached level can diverge if firmware changes fan state out-of-band; there is no locking around `level`, relying on thermal framework serialization and simple word writes. Test signals include registration under the parent OF node, state bounds, duplicate-state no-op, suspend/resume restore, shutdown level 0 write, and regmap error propagation for governor requests.
