# sources/distributed-fs/ceph-client/drivers/mfd/rohm-bd718x7.c

### Purpose
`rohm-bd718x7.c` is the MFD parent driver for ROHM BD71837, BD71847, and BD71850-compatible PMICs. It creates chip-specific clock and regulator children plus a `gpio-keys` power-button child, and it centralizes one-byte regmap and IRQ setup for the BD718xx PMIC interrupt register.

### Important APIs, Types, And Functions
The main entry point is `bd718xx_i2c_probe()`, registered early through `subsys_initcall()` so power rails and clocks are available during boot. `bd718xx_init_press_duration()` parses optional `rohm,short-press-ms` and `rohm,long-press-ms` DT properties and programs `BD718XX_REG_PWRONCONFIG0/1`. Static data includes `bd71837_mfd_cells[]`, `bd71847_mfd_cells[]`, `bd718xx_irqs[]`, `bd718xx_irq_chip`, and `bd718xx_regmap_config`.

### Control Flow
Probe rejects devices without an IRQ, selects the BD71837 or BD71847 cell table from OF match data, initializes an 8-bit maple-cached I2C regmap, registers a one-register regmap IRQ chip over `BD718XX_REG_IRQ`, applies optional power-button duration configuration, maps `BD718XX_INT_PWRBTN_S` to a Linux virtual IRQ, stores it into the static `gpio_keys_button`, and adds MFD children using the regmap IRQ domain.

### State, Persistence, And Dependencies
Runtime state is device-managed regmap, regmap IRQ chip data, and child devices. Hardware persistence includes programmed power-button short/long press thresholds and interrupt mask/ack state. The regmap treats IRQ through power-state registers as volatile and caches the rest with `REGCACHE_MAPLE`. Dependencies include I2C, OF match data, regmap, regmap-irq, MFD core, gpio-keys/input, and `linux/mfd/rohm-bd718x7.h`.

### Integration Points
The clock and PMIC child names are chip-specific (`bd71837-clk`, `bd71847-clk`, `bd71837-pmic`, `bd71847-pmic`), while the power-key child is the generic `gpio-keys` device with platform data. Downstream regulator and clock drivers expect the parent regmap and IRQ domain to exist before they probe.

### Risks
The static mutable power-key button can be overwritten if multiple PMIC instances probe. Press-duration rounding is simple: short presses are rounded by `(ms + 250) / 500` and long presses by `(ms + 500) / 1000`, then capped at 15; DT values outside hardware expectations may be accepted but rounded. Missing IRQ aborts the whole driver. BD71850 is treated as BD71847-compatible, so any register or child difference must be handled elsewhere or added here.

### Test Signals
Probe tests should cover BD71837, BD71847, and BD71850 compatibles, IRQ chip registration, short and long power-button events through `gpio-keys`, and DT press-duration programming. Regmap tests should verify volatile handling for IRQ/status registers and cached reads elsewhere. Boot-order tests are valuable because the driver is registered with `subsys_initcall()`.
