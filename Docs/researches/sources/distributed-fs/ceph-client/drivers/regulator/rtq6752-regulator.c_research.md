<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rtq6752-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/rtq6752-regulator.c

Purpose: implements the Richtek RTQ6752 I2C TFT LCD bias regulator driver. It exposes two voltage regulators, `rtq6752-pavdd` and `rtq6752-navdd`, with linear 5.0 V to 7.3 V selector programming, active discharge control, shared chip-enable GPIO handling, and fault reporting through the regulator framework.

Important APIs/types/functions: `struct rtq6752_priv` stores the regmap, optional `enable` GPIO, mutex, and bitmask of enabled rails. `rtq6752_set_vdd_enable()` and `rtq6752_set_vdd_disable()` coordinate the shared chip enable, regcache-only transitions, and per-rail `regulator_enable_regmap()`/`regulator_disable_regmap()`. `rtq6752_get_error_flags()` maps PAVDD/NAVDD fault bits to `REGULATOR_ERROR_REGULATION_OUT`. `rtq6752_init_device_properties()` programs minimum on-delay and soft-start values. The static `rtq6752_regulator_descs[]` defines voltage, enable, active-discharge, OF child names, and enable time for both rails.

Control flow: probe allocates state, obtains the optional GPIO as initially high, waits for I2C readiness, marks both rails logically enabled, initializes the I2C regmap with maple cache defaults, writes minimum delay/soft-start settings, then registers both regulator descriptors. When the first rail is enabled after the chip was fully off, the driver raises the GPIO, exits cache-only mode, syncs cached registers, marks the rail enabled, and writes the regulator enable bit. When the last rail is disabled, it switches regmap to cache-only, marks it dirty, and drops the GPIO.

State and persistence: runtime state is only the `enable_flag` bitmask, GPIO level, regmap cache, and hardware registers. Voltage settings and active discharge live in chip registers while powered; when the optional GPIO disables the chip, the dirty regcache is later restored on re-enable. No settings are persisted outside the chip.

Dependencies and integration: depends on I2C, regmap, optional GPIO descriptors, OF nodes under `regulators`, and regulator core helpers. It binds `richtek,rtq6752` and uses asynchronous I2C probe. Board DT must provide `pavdd`/`navdd` regulator child constraints and optionally an `enable` GPIO.

Risks and test signals: the shared GPIO/regcache path is concurrency-sensitive, so enable/disable interleavings across both rails should be tested. Probe assumes both rails are on after requesting `GPIOD_OUT_HIGH`, which can affect boot sequencing if constraints later disable one rail. Error-flag reporting depends on fault register availability while the chip is powered. Test with both rails enabled/disabled independently, regcache sync after full power-down, active-discharge writes, fault bit injection, missing GPIO, and probe failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/rtq6752-regulator.c -->
