# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun20i-d1.c

## Purpose

This file provides the Allwinner D1 PIO pin description for the shared sunxi pinctrl driver. It lists pins on banks PB through PG and maps each pin to GPIO input/output, peripheral mux values, and external interrupt positions.

## Important APIs, Types, And Functions

The main table is `d1_pins[]`, an array of `struct sunxi_desc_pin` built with `SUNXI_PIN()`, `SUNXI_PINCTRL_PIN()`, `SUNXI_FUNCTION()`, and `SUNXI_FUNCTION_IRQ_BANK()`. The file defines `d1_irq_bank_map[]`, `d1_pinctrl_data`, `d1_pinctrl_probe()`, `d1_pinctrl_match[]`, and `d1_pinctrl_driver`.

## Control Flow

The built-in platform driver binds to `allwinner,sun20i-d1-pinctrl`. Probe calls `sunxi_pinctrl_init_with_flags()` with `SUNXI_PINCTRL_NEW_REG_LAYOUT`. The common sunxi core registers the listed pins, groups functions by name, exposes GPIO and pinconf operations, and uses the new register layout when programming mux, pull, drive, data, and IRQ registers.

## State And Persistence

Local state is immutable table data. Runtime state is held by the common sunxi driver and by hardware registers. `d1_irq_bank_map` maps logical IRQ banks to hardware banks PB-PG, and `io_bias_cfg_variant = BIAS_VOLTAGE_PIO_POW_MODE_CTL` tells the core how to persist or update IO voltage bias register selections.

## Dependencies And Integration Points

The file depends on `pinctrl-sunxi.h`, OF platform binding, and Linux pinctrl descriptors. It integrates D1 peripherals including LCD, LVDS, DSI, TCON, DMIC, I2S, I2C, SPI, UART, CAN, IR, SPDIF, PWM, LEDC, MMC, EMAC, NCSI, JTAG, clock fanout, and boot/pll signals.

## Risks

The mux table is dense and shares names across alternative pins. Any wrong mux value or IRQ bank index can route a peripheral or interrupt to the wrong pad. Because this file opts into the new register layout and PIO power-mode bias control, using the wrong init flags would corrupt register offsets. Banks start at PB, so off-by-one errors in bank maps are plausible.

## Test Signals

Useful tests include D1 boot with the compatible node, debugfs pin/function listing for PB-PG, GPIO direction/value tests per bank, external interrupt tests on each mapped bank, IO bias tests for voltage-sensitive pins, and functional mux tests for UART console, MMC, I2C, SPI, audio, display, and EMAC.
