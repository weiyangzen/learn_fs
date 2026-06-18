# sources/distributed-fs/ceph-client/drivers/mfd/stmpe.c

## Purpose
`stmpe.c` is the common core for STMicroelectronics STMPE multifunction expanders. It abstracts I2C/SPI register access, models multiple chip variants, controls functional blocks, manages nested interrupts, parses DT children, and registers GPIO, keypad, touchscreen, ADC, and PWM child devices as supported.

## Important APIs, Types, and Functions
Exported register and block APIs include `stmpe_enable()`, `stmpe_disable()`, `stmpe_reg_read()`, `stmpe_reg_write()`, `stmpe_set_bits()`, `stmpe_block_read()`, `stmpe_block_write()`, `stmpe_set_altfunc()`, `stmpe811_adc_common_init()`, `stmpe_probe()`, and `stmpe_remove()`. Variant descriptors are `struct stmpe_variant_info` and `struct stmpe_variant_block` instances for STMPE610/801/811/1600/1601/1801/2401/2403. IRQ handling uses `stmpe_irq()`, `stmpe_irq_mask()`, `stmpe_irq_unmask()`, `stmpe_irq_sync_unlock()`, and an irqdomain.

## Control Flow
Transport wrappers call `stmpe_probe()` with callbacks and a part number. Probe parses DT for requested child blocks and ADC settings, handles optional VCC/VIO regulators, resolves parent IRQ or IRQ GPIO, selects no-IRQ variant data when supported, initializes the chip, creates an IRQ domain and threaded parent IRQ when present, then registers requested child cells. Chip init reads and validates the chip ID, disables all modules, resets the chip, configures interrupt control from trigger type, optionally enables autosleep, and writes the interrupt-control register. Nested IRQ handling reads ISR banks, masks by cached IER state, dispatches mapped child IRQs, and clears serviced bits.

## State and Persistence
`struct stmpe` stores transport callbacks, variant info, register index table, locks, child block requests, regulator handles, IRQ domain, IER/old IER caches, ADC configuration, and optional IRQ line. Hardware state is reset during probe; block enable bits, interrupt masks, alternate functions, autosleep, and ADC setup live in volatile chip registers. Suspend/resume only toggles IRQ wake for wake-capable devices.

## Dependencies and Integration Points
The file depends on transport wrappers, regulators, gpio descriptors for optional IRQ GPIO, irqdomain/nested IRQ handling, and MFD children named `stmpe-gpio`, `stmpe-keypad`, `stmpe-ts`, `stmpe-adc`, and `stmpe-pwm`. Child drivers use exported register/block APIs and `stmpe_set_altfunc()`.

## Risks and Edge Cases
Variant tables encode register ordering and interrupt counts; mistakes map child drivers to wrong registers. Only STMPE801 supports no-IRQ mode here. Some variants do not support edge-trigger configuration. `stmpe_devices_init()` mutates static resource arrays to fill IRQ numbers, which can be risky with multiple instances. Regulator enable failures are warnings, not fatal, after optional supplies are found.

## Test Signals
Test each variant ID and requested child combination, no-IRQ STMPE801, parent IRQ trigger polarity, IRQ mask/unmask synchronization, reset completion timeout, autosleep timeout rounding, ADC common init, alternate-function programming, and remove path regulator disable plus child removal.
