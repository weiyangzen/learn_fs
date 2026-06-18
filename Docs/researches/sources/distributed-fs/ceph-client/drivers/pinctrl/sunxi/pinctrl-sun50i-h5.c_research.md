# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-h5.c

## Purpose

This file describes the Allwinner H5 main PIO controller for banks PA, PC, PD, PE, PF, and PG. It supports GPIO, mux, and interrupt routing for common H5 board peripherals.

## Important APIs, Types, And Functions

Important objects are `sun50i_h5_pins[]`, `sun50i_h5_pinctrl_data_broken`, `sun50i_h5_pinctrl_data`, `sun50i_h5_pinctrl_probe()`, `sun50i_h5_pinctrl_match[]`, and `sun50i_h5_pinctrl_driver`. The probe path is unusual because it calls `platform_irq_count()` and selects between two descriptors.

## Control Flow

The built-in platform driver matches `allwinner,sun50i-h5-pinctrl`. Probe counts platform IRQ resources. With two IRQs it warns that the device tree lacks the PG bank IRQ and initializes a reduced descriptor; with three IRQs it initializes the full descriptor; any other count fails with `-EINVAL`. The common core then handles the pinctrl/GPIO/IRQ operations.

## State And Persistence

All local state is immutable. Runtime state is common-core data plus hardware registers. The descriptor sets `irq_read_needs_mux = true` and `disable_strict_mode = true`. The selected descriptor controls whether the PG interrupt bank is available for the lifetime of the device.

## Dependencies And Integration Points

The table integrates UART, JTAG, SIM, I2C, display interface, SPI, SPDIF, I2S, TS, MMC, NAND, EMAC, CSI, PWM, and GPIO interrupt functions. It depends on platform IRQ resources being described correctly in device tree.

## Risks

The probe compatibility path intentionally tolerates broken device trees, but systems with only two IRQs lose PG bank interrupt support. Device-tree resource counts are therefore part of functional behavior. `disable_strict_mode` keeps legacy mux/GPIO overlap permissive and should not be removed without board testing. Table risks are typical dense mux errors.

## Test Signals

Test with both two-IRQ and three-IRQ device trees, confirm warning behavior for the broken case, verify debugfs pin and IRQ bank exposure, exercise PG EINTs on corrected device trees, and run peripheral tests for UART, MMC, Ethernet, I2C, SPI, audio, display, and camera pins.
