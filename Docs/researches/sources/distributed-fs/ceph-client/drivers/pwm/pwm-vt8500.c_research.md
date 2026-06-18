# sources/distributed-fs/ceph-client/drivers/pwm/pwm-vt8500.c

Purpose: implements a Linux PWM provider for VIA/WonderMedia VT8500-compatible PWM hardware. The controller exposes register blocks for four logical channels, but this driver registers only `VT8500_NR_PWMS` equal to two implemented channels. It binds through the platform bus and device tree compatible `via,vt8500-pwm`.

Important APIs, types, and functions: `struct vt8500_chip` carries the MMIO base and prepared clock. `vt8500_pwm_apply()` is the only `pwm_ops` entry and orchestrates polarity, configuration, enable, and disable. `vt8500_pwm_config()` converts nanosecond period and duty into hardware prescaler, period, and duty registers. `vt8500_pwm_enable()`, `vt8500_pwm_disable()`, and `vt8500_pwm_set_polarity()` update the control register. `vt8500_pwm_busy_wait()` polls `REG_STATUS` update bits after every register write. `vt8500_pwm_probe()` allocates the chip with devres, gets a prepared clock, maps the IO resource, and registers the PWM chip.

Control flow: probe validates an OF node, allocates a two-channel chip, records private data, prepares the clock, maps registers, and calls `devm_pwmchip_add()`. Runtime requests enter `apply`: polarity changes on an enabled channel first disable output, disabled target state exits after optionally disabling, and enabled state always calls config before enabling. Config enables the clock temporarily, computes `period_cycles = clk_rate * period_ns / 1e9`, derives a 10-bit prescaler and 12-bit period value, writes scalar/period/duty/autoload in order, waits for each update bit to clear, and disables the clock. Enabling leaves the clock enabled until disable.

State and persistence: persistent state is hardware register state plus the clock enable count. No software cache is kept beyond PWM core state. Busy-wait timeout only logs a warning and does not abort, so hardware that fails to clear update bits can leave partially programmed state.

Dependencies and integration: depends on Linux platform, clock, MMIO, OF matching, and PWM core APIs. It uses `devm_` lifetime for allocation and mapping. The driver relies on the PWM core to serialize consumer state transitions.

Risks: `msecs_to_loops(10)` is a crude polling budget and can be CPU-frequency sensitive. Duty calculation uses the reduced period register value, so rounding can be visible. If `state->period` is zero, the division path in duty computation would be invalid unless the PWM core prevents it. Polarity writes do not enable the clock explicitly, unlike config and enable.

Test signals: boot with a matching device tree node, verify `pwmchip` registration, exercise both channels through sysfs/debug consumers, check period/duty rounding at minimum and maximum rates, test polarity changes while active, and watch for status timeout warnings.
