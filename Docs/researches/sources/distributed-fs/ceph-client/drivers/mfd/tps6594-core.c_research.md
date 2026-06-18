# sources/distributed-fs/ceph-client/drivers/mfd/tps6594-core.c

## Purpose
`tps6594-core.c` is the bus-independent MFD core for LP8764, TPS65224, TPS652G1, TPS6593, and TPS6594 PMICs. It defines variant-specific child cells, IRQ resources, regmap IRQ chips, volatile access tables, CRC enable/synchronization policy, ACTIVE-state setup, optional power-button and RTC child registration, and system power-off integration.

## Important APIs, Types, And Functions
The exported API is `tps6594_device_init(struct tps6594 *tps, bool enable_crc)`, plus exported volatile tables `tps6594_volatile_table` and `tps65224_volatile_table`. IRQ resources are grouped for regulators, pinctrl, PFSM, ESM, RTC, ADC, and power button. Variant IRQ tables include `tps6594_irqs[]`, `tps65224_irqs[]`, and `tps652g1_irqs[]`. `tps6594_handle_post_irq()` clears communication-address/error fallout after regmap IRQ ack when CRC is enabled. CRC helpers are `tps6594_check_crc_mode()`, `tps6594_set_crc_feature()`, and `tps6594_enable_crc()`.

## Control Flow
Bus drivers initialize `struct tps6594` and call `tps6594_device_init()`. If requested, CRC enablement either triggers PFSM/I2C CRC on a primary PMIC and completes a global completion, or waits for a primary PMIC before checking secondary CRC mode. The core sets `NSLEEP1B` and `NSLEEP2B` to keep the PMIC active, chooses the correct IRQ chip and child-cell array for TPS65224/TPS652G1 versus TPS6594-class devices, assigns a dynamic IRQ chip name and driver data, registers the regmap IRQ chip, adds common children, optionally adds a TPS65224/TPS652G1 power-button child based on pin configuration, optionally adds RTC for supported chips, and registers a power-off handler when the node is a system power controller.

## State, Persistence, And Dependencies
State includes `tps->chip_id`, `reg`, `irq`, `regmap`, `irq_data`, and `use_crc`. Persistent hardware effects include CRC enablement, active-state trigger bits, interrupt acks, optional power-off trigger writes, and child-visible register state. Dependencies include regmap-irq with custom register lookup, completions, OF properties, bitfield helpers, sys-off, MFD core, and `linux/mfd/tps6594.h`.

## Integration Points
I2C and SPI bus wrappers supply regmap implementations and CRC framing. Children include `tps6594-regulator`, `tps6594-pinctrl`, `tps6594-pfsm`, `tps6594-esm`, `tps6594-rtc`, `tps65224-adc`, and `tps6594-pwrbutton` depending on variant and configuration. The IRQ domain carries named fault, GPIO, PFSM, ESM, RTC, ADC, and power-button interrupts to children.

## Risks
The static regmap IRQ chip objects are mutated per probe (`irq_drv_data` and `name`), which would be unsafe for multiple concurrently probed devices using the same chip object. CRC synchronization uses a single global completion, so multi-primary or reprobe scenarios need scrutiny. CRC post-IRQ cleanup writes error bits after each regmap IRQ pass; wrong chip ID selection could clear the wrong register. Variant IRQ/resource tables are large and hand-maintained, increasing drift risk. The MODULE_AUTHOR line for Bhargav is missing a closing angle bracket in the source string.

## Test Signals
Test all supported chip IDs over both bus wrappers, CRC disabled/enabled primary/secondary flows and timeout, ACTIVE-state write failure, IRQ chip naming, regmap IRQ dispatch for regulator/GPIO/PFSM/ESM/RTC/ADC groups, TPS65224/TPS652G1 power-button pin-detection paths, RTC omission for LP8764/TPS65224/TPS652G1, system-power-controller power-off trigger, and multiple-device probe behavior.
