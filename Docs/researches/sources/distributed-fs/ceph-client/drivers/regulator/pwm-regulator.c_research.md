# sources/distributed-fs/ceph-client/drivers/regulator/pwm-regulator.c

Purpose: implements a generic platform regulator whose output voltage is controlled by a PWM duty cycle, optionally gated by an enable GPIO. It supports discrete voltage-table mode and continuous voltage-range mode.

Important APIs/types/functions: `struct pwm_regulator_data` stores the PWM, optional voltage table, continuous-mode mapping, descriptor, cached table selector, and enable GPIO. `pwm_regulator_init_table()` parses `voltage-table` entries of `{uV, dutycycle}`. `pwm_regulator_init_continuous()` parses optional `pwm-dutycycle-range` and `pwm-dutycycle-unit`. Table ops implement selector get/set/list/map. Continuous ops implement voltage get/set by linear interpolation between regulator constraints and dutycycle bounds.

Control flow: probe requires a DT node, allocates state, copies a base descriptor, chooses table or continuous mode, obtains regulator init data, gets the PWM, configures optional enable GPIO according to `boot_on`/`always_on`, adjusts PWM config, preserves boot-on output state if needed, and registers the regulator.

State and persistence: `drvdata->state` caches the selected table row and starts as `-ENOTRECOVERABLE`. Continuous mode has no selector cache. PWM hardware state and enable GPIO state are runtime state; no persistent storage is used.

Dependencies and integration: depends on platform bus, OF regulator data, PWM framework, GPIO descriptors, and regulator core. Compatible is `pwm-regulator`.

Risks and test signals: table parsing casts a property into `struct pwm_voltages`, relying on two 32-bit cells and native layout. Continuous `set_voltage()` uses `req_min_uV` and does not explicitly verify `req_max_uV` after interpolation. Test both DT modes, inverted duty ranges, boot-on preservation, GPIO present/absent cases, PWM apply failures, invalid table lengths, and disabled-PWM get-voltage behavior.
