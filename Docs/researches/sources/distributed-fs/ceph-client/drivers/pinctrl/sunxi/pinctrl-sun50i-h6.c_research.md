# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-h6.c

## Purpose

This file describes the main Allwinner H6 PIO controller for banks PA, PB, PC, PD, PF, PG, and PH. It supplies mux and interrupt data for Ethernet, camera/display, storage, audio, serial, SIM, HDMI, and related functions.

## Important APIs, Types, And Functions

Important definitions are `h6_pins[]`, `h6_irq_bank_map[]`, `h6_pinctrl_data`, `h6_pinctrl_probe()`, `h6_pinctrl_match[]`, and `h6_pinctrl_driver`. The descriptor sets `.irq_banks = 4`, maps IRQ banks through `{ 1, 5, 6, 7 }`, enables `irq_read_needs_mux`, and uses `BIAS_VOLTAGE_PIO_POW_MODE_SEL`.

## Control Flow

The built-in driver matches `allwinner,sun50i-h6-pinctrl`. Probe calls `sunxi_pinctrl_init()`. The common core uses the explicit IRQ bank map to translate logical IRQ bank positions to hardware banks PB, PF, PG, and PH while servicing mux, GPIO, pinconf, and IRQ operations.

## State And Persistence

Local data is static. Runtime state is common-core bookkeeping plus PIO register contents. IRQ readback depends on mux state, and IO bias uses the power-mode select register variant.

## Dependencies And Integration Points

The table integrates EMAC, CCIR/CSI, I2S and H-I2S variants, I2C, PWM, NAND, SPI, MMC, UART, SIM, SPDIF, TS, LCD, HDMI, JTAG, IR transmit, and DMIC functions. It depends on the common sunxi pinctrl and GPIO/IRQ infrastructure.

## Risks

The explicit IRQ bank map is a key correctness point because the hardware IRQ-capable banks are not contiguous. Several early PA pins list only peripheral functions and lack normal GPIO entries, so assumptions that every descriptor has gpio-in/out are unsafe. IO-bias variant and mux-aware IRQ reads are SoC-specific and should not be generalized without hardware tests.

## Test Signals

Test H6 probe, debugfs pin and IRQ map output, GPIO behavior on banks with GPIO entries, IRQ tests on PB/PF/PG/PH, IO-bias readback, and peripheral mux tests for Ethernet, camera, MMC, NAND/SPI, UART, I2C, audio, HDMI, and display pins.
