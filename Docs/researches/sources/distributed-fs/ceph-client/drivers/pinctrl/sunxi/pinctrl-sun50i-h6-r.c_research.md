# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-h6-r.c

## Purpose

This file supplies the H6 R-PIO descriptor for PL0-PL10 and PM0-PM4. It covers GPIO, wake interrupts, sleep-domain serial/I2C/RSB/PWM/CIR/JTAG, and one-wire style functions.

## Important APIs, Types, And Functions

The file defines `sun50i_h6_r_pins[]`, `sun50i_h6_r_pinctrl_data`, `sun50i_h6_r_pinctrl_probe()`, `sun50i_h6_r_pinctrl_match[]`, and `sun50i_h6_r_pinctrl_driver`. The descriptor uses `.pin_base = PL_BASE`, `.irq_banks = 2`, and `.io_bias_cfg_variant = BIAS_VOLTAGE_PIO_POW_MODE_SEL`.

## Control Flow

The built-in driver matches `allwinner,sun50i-h6-r-pinctrl`. Probe calls `sunxi_pinctrl_init()`, and the common core registers the R-PIO pins and handles GPIO, pinmux, pinconf, and IRQ operations.

## State And Persistence

The file is declarative. Runtime state is stored in R-PIO registers and common driver structures. IO bias selection uses the PIO power-mode select variant, which is different from several other SoCs in this subset.

## Dependencies And Integration Points

It depends on `pinctrl-sunxi.h` and OF platform matching. It integrates `s_rsb`, `s_i2c`, `s_uart`, `s_jtag`, `s_pwm`, `s_cir_rx`, `s_w1`, and `1wire` functions with PL/PM external interrupts.

## Risks

The mixed PL/PM R-PIO layout makes `.irq_banks = 2` and `PL_BASE` important. Incorrect IO-bias variant selection could misprogram voltage-domain controls. The table contains both `s_w1` and `1wire` naming, so device-tree users must match the exact function names expected by this driver.

## Test Signals

Validate probe, PL and PM pin visibility, GPIO and EINT operation on both banks, IO-bias register behavior, suspend/wake flows, and functional tests for RSB/I2C, sleep UART, CIR, PWM, and one-wire pins.
