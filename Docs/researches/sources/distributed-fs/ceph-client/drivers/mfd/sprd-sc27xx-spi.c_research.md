# sources/distributed-fs/ceph-client/drivers/mfd/sprd-sc27xx-spi.c

## Purpose
`sprd-sc27xx-spi.c` is the SPI MFD parent for Spreadtrum SC2730/SC2731 PMICs. It exposes PMIC registers through regmap, creates a regmap IRQ chip, populates child devices, supports wakeup, and exports charger-type detection.

## Important APIs, Types, and Functions
`struct sprd_pmic` stores regmap, IRQ chip data, PMIC data, and parent IRQ. `struct sprd_pmic_data` supplies interrupt base/count and charger-detection register. `sprd_pmic_detect_charger_type()` polls charger detection and returns a USB charger type. SPI regmap bus callbacks are `sprd_pmic_spi_write()` and `sprd_pmic_spi_read()`. `sprd_pmic_probe()` sets up the regmap IRQ chip and child devices. PM callbacks are `sprd_pmic_suspend()` and `sprd_pmic_resume()`.

## Control Flow
Probe loads match data for SC2730 or SC2731, allocates state, initializes a 32-bit native-endian SPI regmap, builds one `regmap_irq` mask per PMIC interrupt, registers the IRQ chip on the SPI IRQ line, populates OF child nodes, and initializes wakeup support. Suspend enables IRQ wake when allowed; resume disables it.

## State and Persistence
Runtime state is devm-managed. Hardware interrupt enable/status registers and charger-detection bits are volatile. Wake capability is stored in the device PM state.

## Dependencies and Integration Points
It depends on SPI, regmap, regmap-irq, OF platform population, `linux/mfd/sc27xx-pmic.h`, and USB charger type definitions. Child PMIC function drivers bind under the parent DT node.

## Risks and Edge Cases
The SPI read path supports only one 32-bit register and one 32-bit value at a time. Charger detection can time out after polling. IRQ chip `ack_base = 0` relies on this PMIC's interrupt semantics and regmap-irq behavior. Match data is mandatory even though SPI IDs exist.

## Test Signals
Exercise both PMIC variants, regmap 32-bit read/write, PMIC IRQ delivery, wakeup suspend/resume, OF child population, and charger detection returning SDP/CDP/DCP/UNKNOWN.
