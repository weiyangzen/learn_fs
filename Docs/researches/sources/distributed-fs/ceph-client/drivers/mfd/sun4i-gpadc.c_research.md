# sources/distributed-fs/ceph-client/drivers/mfd/sun4i-gpadc.c

## Purpose
`sun4i-gpadc.c` is the MFD parent for Allwinner sunxi GPADC/touchscreen blocks. It creates an MMIO regmap, exposes FIFO/temp interrupts through regmap-irq, and registers GPADC IIO and hwmon children for supported SoC variants.

## Important APIs, Types, and Functions
`sun4i_gpadc_regmap_irq` maps FIFO data and temperature data interrupts. `sun4i_gpadc_regmap_irq_chip` defines status, ACK, and unmask registers. Variant-specific MFD cell arrays name the IIO child for sun4i, sun5i, or sun6i. `sun4i_gpadc_probe()` selects the cell array, maps registers, initializes regmap and IRQ chip, and registers children.

## Control Flow
Probe matches the DT compatible to an architecture ID, selects child cells, allocates `struct sun4i_gpadc_dev`, maps the MMIO resource, initializes a 32-bit regmap, disables all interrupts, obtains the platform IRQ, adds the regmap IRQ chip, and registers child MFD devices.

## State and Persistence
State is per-device: mapped base, regmap, regmap IRQ data, and device pointer. Interrupt and ADC registers are volatile. No suspend or persistent state is handled in this parent.

## Dependencies and Integration Points
It depends on platform MMIO resources, regmap-irq, Allwinner GPADC register definitions, and child IIO/hwmon drivers named by the selected cells.

## Risks and Edge Cases
Interrupts are disabled before regmap-irq setup, so child drivers must enable what they need. Variant selection is DT-compatible driven; unsupported data values fail probe. The parent assumes one IRQ resource exists.

## Test Signals
Validate all three compatibles, FIFO and temperature interrupt delivery, disabled-interrupt startup state, IIO child naming, hwmon child creation, and cleanup on regmap-irq or MFD-add failure.
