# sources/distributed-fs/ceph-client/drivers/mfd/rk8xx-core.c

## Purpose
`rk8xx-core.c` is the shared MFD core for Rockchip RK801/RK805/RK806/RK808/RK809/RK816/RK817/RK818 PMICs. Bus-specific drivers supply a regmap and variant ID; the core selects IRQ chip, pre-initialization registers, child cells, poweroff/restart behavior, and suspend/resume pin policy.

## Important APIs, Types, And Functions
`struct rk808_reg_data` describes masked register writes. Variant arrays define child `mfd_cell`s, pre-init register scripts, and regmap IRQ tables. `rk808_power_off()`, `rk808_restart()`, `rk8xx_shutdown()`, `rk8xx_probe()`, `rk8xx_suspend()`, and `rk8xx_resume()` are the exported/shared entry points. Regmap IRQ chips exist for each variant family.

## Control Flow
`rk8xx_probe()` allocates `struct rk808`, selects variant-specific IRQ chip/pre-init/cells, optionally configures RK806 reset mode from `rockchip,reset-mode`, requires a core IRQ, registers a regmap IRQ chip, applies all pre-init masked writes, adds children with the IRQ domain, and if marked as a system power controller registers sys-off poweroff and sometimes restart handlers. Shutdown and PM callbacks adjust sleep/powerdown pin functions for supported variants.

## State And Persistence
Driver state includes variant ID, regmap, regmap IRQ chip data, and sys-off callbacks. Pre-init writes persist in PMIC runtime registers and include thermal thresholds, reset behavior, voltage monitor actions, codec defaults, interrupt polarity, and current limits.

## Dependencies And Integration Points
It depends on bus wrappers (`rk8xx-i2c.c`, `rk8xx-spi.c`), `linux/mfd/rk808.h`, regmap-irq, MFD core, sys-off/reboot APIs, device properties `system-power-controller`, `rockchip,system-power-controller`, and `rockchip,reset-mode`, plus regulator, RTC, pwrkey, pinctrl, clkout, codec, charger, and ADC child drivers.

## Risks
Pre-init scripts are large hardware policy tables; wrong values can affect rails, reset, thermal shutdown, audio, and charging. Core probe refuses missing IRQs, so boards without wired PMIC IRQ fail. RK817 codec registers include vendor-derived undocumented values. Poweroff/restart register choices are variant-specific and must remain aligned with PMIC IDs.

## Test Signals
Probe every variant through I2C/SPI as applicable, verify IRQ-domain child resources, pre-init register diffs, system poweroff/restart, shutdown pin-mode writes, suspend/resume pin behavior, RK806 reset-mode property, and child driver operation.
