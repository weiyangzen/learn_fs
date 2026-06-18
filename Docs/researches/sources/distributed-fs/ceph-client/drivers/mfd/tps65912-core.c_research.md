# sources/distributed-fs/ceph-client/drivers/mfd/tps65912-core.c

## Purpose
`tps65912-core.c` provides bus-independent MFD initialization for TPS65912 PMICs. It defines child devices, IRQ mappings, volatile regmap policy, exports the shared regmap config, and exports `tps65912_device_init()` for I2C and SPI transport drivers.

## Important APIs, Types, And Functions
Key exported symbols are `tps65912_regmap_config` and `tps65912_device_init()`. Static data includes `tps65912_cells[]` for regulator and GPIO children, `tps65912_irqs[]` covering power/thermal/GPIO/power-good IRQs across four status registers, `tps65912_irq_chip`, and `tps65912_volatile_table`.

## Control Flow
Bus drivers allocate `struct tps65912`, initialize `tps->regmap`, set `tps->dev` and `tps->irq`, then call `tps65912_device_init()`. The core adds a devm regmap IRQ chip with `IRQF_ONESHOT`, then registers regulator and GPIO children with the resulting IRQ domain.

## State, Persistence, And Dependencies
The core persists `irq_data` in parent state and the regmap cache policy. Volatile registers span `TPS65912_INT_STS` through `TPS65912_GPIO5`. Dependencies include regmap, regmap-irq, MFD core, module exports, and `linux/mfd/tps65912.h`.

## Integration Points
`tps65912-i2c.c` and `tps65912-spi.c` consume the exported regmap config and device init function. Child drivers consume the parent regmap and IRQ domain for regulator and GPIO functionality.

## Risks
`tps65912_device_init()` always attempts IRQ-chip registration; probe on systems without a usable IRQ may fail unless regmap-irq tolerates the supplied value. The volatile range is broad and includes GPIO registers, which preserves correctness but limits caching. There is no chip revision detection or variant-specific behavior here.

## Test Signals
Test I2C and SPI callers, regmap IRQ registration failure, child creation failure, each mapped IRQ register offset, volatile-table behavior for INT/GPIO ranges, and child IRQ domain requests.
