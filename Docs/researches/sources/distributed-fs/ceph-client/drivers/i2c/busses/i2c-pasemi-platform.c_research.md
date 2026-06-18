
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pasemi-platform.c

Purpose: this is the platform-bus wrapper for the PA Semi/Apple SMBus controller shared core in `i2c-pasemi-core.h`. It binds Apple DT compatibles such as `apple,t8103-i2c` and `apple,i2c`, maps the MMIO resource, enables the reference clock, derives the SMBus clock divider, and delegates adapter setup to `pasemi_i2c_common_probe()`.

Important APIs, types, and functions: `struct pasemi_platform_i2c_data` embeds `struct pasemi_smbus` plus a reference clock. `pasemi_platform_i2c_calc_clk_div()` uses `clk_get_rate()` and `DIV_ROUND_UP()` to compute `smbus.clk_div` as source clock divided by `16 * frequency`, rejecting dividers outside the hardware byte range. `pasemi_platform_i2c_probe()` uses devm allocation, `devm_platform_ioremap_resource()`, `of_property_read_u32("clock-frequency")`, `devm_clk_get_enabled()`, `pasemi_i2c_common_probe()`, `platform_get_irq()`, and `devm_request_irq()` with `pasemi_irq_handler`. The remove callback is intentionally empty because resources are devm-managed and common teardown is apparently handled by managed adapter registration in the core.

Control flow: probe allocates state, initializes `smbus->dev`, maps registers, reads or defaults the bus frequency to standard mode, enables the clock, calculates the divider, assigns the adapter OF node, calls the common core probe, then tries to attach an IRQ. IRQ request failure is not fatal; it simply leaves `smbus->use_irq` unset so the common core can operate without interrupts. Driver registration is via `module_platform_driver()`.

State and persistence: all runtime state is in the device-managed `pasemi_platform_i2c_data`. Persistent hardware state consists of the clock divider and interrupt mode in the shared `pasemi_smbus` structure. There is no disk persistence, global mutable state, or explicit remove teardown in this wrapper.

Dependencies and integration points: it depends on Linux clock, OF, platform, MMIO, and I2C subsystems plus the local PASemi common core. DT supplies MMIO, optional `clock-frequency`, clock, IRQ, and compatible strings. The core provides actual SMBus transaction behavior and interrupt handling.

Risks: invalid clock rates can make frequencies too fast or too slow and probe fails. IRQ acquisition is best-effort, so latency and timeout behavior depend on the common core polling path when no IRQ is usable. The empty remove path is safe only if common adapter/resources are devm-managed by `pasemi_i2c_common_probe()`.

Test signals: boot/probe on Apple hardware should show adapter registration and working standard-mode transfers. Negative tests include zero clock rate, out-of-range `clock-frequency`, missing MMIO, missing clock, no IRQ fallback, and client SMBus reads/writes through the resulting adapter.
