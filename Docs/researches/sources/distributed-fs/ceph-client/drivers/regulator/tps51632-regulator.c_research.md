# sources/distributed-fs/ceph-client/drivers/regulator/tps51632-regulator.c

Purpose: I2C regulator driver for the TI TPS51632 D-CAP step-down controller with serial VID and optional PWM DVFS operation.

Important APIs/types/functions: `struct tps51632_chip` owns the regulator descriptor, regmap, and registered rdev. `tps51632_dcdc_ops` uses generic regmap selector helpers plus `tps51632_dcdc_set_ramp_delay`. `tps51632_init_dcdc` programs base voltage, optional 20 mV DVFS step mode, VMAX, and DVFS control. Regmap access rules mark offset/fault/current-monitor registers volatile and restrict writes to supported control registers.

Control flow: probe builds a single voltage descriptor, obtains platform data or OF-derived init data, validates PWM DVFS base/max voltages, chooses either `VOLTAGE_BASE_REG` or `VOLTAGE_SELECT_REG` as the selector register, initializes regmap, initializes chip DVFS configuration, and registers one regulator. If VMAX is requested, the driver reads the VMAX lock bit and writes only if the register has not already been locked by prior boot firmware or a previous write.

State and persistence: register state persists in the controller. The driver does not maintain runtime selector state beyond regmap cache and descriptor fields. VMAX is hardware one-time writable until power reset, so boot order matters.

Dependencies and integration points: I2C, regmap, regulator core, OF regulator init data, legacy `tps51632_regulator_platform_data`, and `subsys_initcall` registration.

Risks: ramp delay maps directly to a bit position via `DIV_ROUND_UP(ramp_delay, 6000) - 1`; unusually high values may select undefined bits unless constrained by callers. VMAX lock behavior can surprise tests or repeated probes. OF data is required when platform data is absent.

Test signals: probe from DT and platform data, PWM DVFS enabled/disabled, invalid voltage constraints, VMAX locked/unlocked behavior, ramp delay writes, and regmap read/write error propagation.
