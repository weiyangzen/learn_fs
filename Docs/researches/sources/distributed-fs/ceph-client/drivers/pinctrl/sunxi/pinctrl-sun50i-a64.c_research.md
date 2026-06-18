# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-a64.c

## Purpose

This file provides the main Allwinner A64 PIO table for banks PB through PH. It enumerates GPIO, mux, and external interrupt capabilities for storage, display, camera, audio, serial, and network-related pins.

## Important APIs, Types, And Functions

The main definitions are `a64_pins[]`, `a64_pinctrl_data`, `a64_pinctrl_probe()`, `a64_pinctrl_match[]`, and `a64_pinctrl_driver`. The descriptor sets `.irq_banks = 3` and relies on the common sunxi core for all runtime operations.

## Control Flow

The built-in driver matches `allwinner,sun50i-a64-pinctrl` and calls `sunxi_pinctrl_init()` from probe. The core then builds pin groups/functions from `a64_pins[]` and programs PIO mux, pull, drive, data, and IRQ registers on demand.

## State And Persistence

Only static table data is local. Hardware state persists in PIO registers until reset or reconfiguration. The three IRQ banks correspond to the banks with EINT annotations in the table and are interpreted by the common IRQ support.

## Dependencies And Integration Points

The file integrates functions including UART, JTAG, SIM, audio interfaces, NAND, MMC, SPI, LCD, LVDS, CSI/CCIR, TS, I2C, PWM, EMAC, SPDIF, and microphone pins. It depends on Linux OF platform binding and `pinctrl-sunxi.h`.

## Risks

The table mixes banks with and without IRQ support and has many overlapping storage/display/audio functions. Wrong function names or mux values break device-tree consumers silently. Since `.irq_banks = 3` is positional rather than an explicit map, changes to the table must preserve the core's expected bank ordering.

## Test Signals

Validation should include A64 probe, debugfs pin/function review, GPIO tests on PB-PH, EINT tests on all IRQ-capable banks, and board tests for UART, MMC, NAND/SPI, display, camera, I2C, audio, PWM, and Ethernet-related pins.
