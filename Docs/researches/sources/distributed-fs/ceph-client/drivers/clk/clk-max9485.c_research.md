# sources/distributed-fs/ceph-client/drivers/clk/clk-max9485.c

Purpose: I2C driver for the Maxim MAX9485 programmable audio clock generator. It exposes MCLK output, programmable CLKOUT, and two gated child outputs.

Important APIs, types, and functions: `max9485_rate` maps exact output rates to one-byte hardware register values. `max9485_driver_data` stores input clock, I2C client, shadow register value, regulator, reset GPIO, and four clock hw entries. `max9485_clk_hw` links each clock to an enable bit and driver data. `max9485_clkout_*` implements rate selection; `max9485_clk_prepare/unprepare()` toggles output enable bits.

Control flow: probe gets `xclk`, enables `vdd`, gets optional reset GPIO, reads the current device register into `reg_value`, registers four clocks with parent relationships, and adds an OF provider. `max9485_update_bits()` updates the shadow byte then sends it over I2C. Suspend deasserts reset; resume reasserts reset and writes the shadow register back.

State and persistence: the single hardware register is mirrored in `drvdata->reg_value`; this shadow is the source for rate recalc and resume restore. The supply regulator is enabled at probe and not disabled by a local remove path because devm/resource teardown owns it.

Dependencies and integration points: depends on I2C, regulator, GPIO, parent input clock, DT clock-output names, common clock framework, and PM sleep ops.

Risks and test signals: `max9485_update_bits()` mutates the shadow before knowing whether I2C send succeeded, so failed writes can desynchronize software and hardware. `max9485_of_clk_get()` lacks bounds checking. Parent selection uses `parent_index > 0`, so index 0 is treated as external xclk rather than an internal parent. Test signals are exact/rounded rate selection, suspend/resume restore, I2C failure behavior, and phandle index validation.
