# sources/distributed-fs/ceph-client/drivers/mfd/hi655x-pmic.c

## Purpose
`hi655x-pmic.c` is the MMIO MFD parent for HiSilicon HI655X PMICs. It validates the PMU version, clears local IRQ state, installs a regmap IRQ chip sourced from a GPIO line, and registers power-key, regulator, and clock children.

## Important APIs, Types, and Functions
`hi655x_irqs[]` maps one status register worth of over-temperature, voltage, power-button, and reserved interrupt bits. `hi655x_irq_chip` defines status, ack, and mask bases. `hi655x_regmap_config` describes 32-bit strided MMIO with 8-bit values. `pwrkey_resources[]` maps down/up/hold power-key IRQ resources. `hi655x_local_irq_clear()` clears analog and PMIC IRQ status registers. `hi655x_pmic_probe()` and `hi655x_pmic_remove()` manage lifecycle.

## Control Flow
Probe allocates `struct hi655x_pmic`, maps MMIO, initializes the regmap, reads and validates the version register, clears all local IRQ status/mask state, obtains the optional `pmic` GPIO as input, converts it to an IRQ, installs the regmap IRQ chip with low-triggered no-suspend flags, stores driver data, and registers child devices using the regmap IRQ domain. On child registration failure or remove, it deletes the IRQ chip and removes children.

## State and Persistence
State includes PMIC version, device pointer, regmap, optional GPIO descriptor, and regmap IRQ data. Hardware state includes cleared IRQ status, IRQ masks, and child-controlled regulator/clock registers. No filesystem persistence exists.

## Dependencies and Integration Points
It depends on platform MMIO, regmap-mmio, GPIO descriptors, regmap-irq, MFD core, and Hi655X register macros. Child power-key resources are resolved through the regmap IRQ domain passed to `mfd_add_devices()`.

## Risks and Edge Cases
`devm_gpiod_get_optional()` can return NULL, but `gpiod_to_irq(pmic->gpio)` is called unconditionally; a missing GPIO can fail or crash depending on helper behavior. `regmap_read()` of the version register ignores its return value before validating `pmic->ver`. IRQ clearing writes all ones to multiple status registers, which can drop pending boot events.

## Test Signals
Test supported and unsupported PMU versions, missing/invalid `pmic` GPIO handling, regmap IRQ domain creation, power-key down/up/hold events, local IRQ clear writes, child registration failure cleanup, and no-suspend IRQ behavior during suspend.
