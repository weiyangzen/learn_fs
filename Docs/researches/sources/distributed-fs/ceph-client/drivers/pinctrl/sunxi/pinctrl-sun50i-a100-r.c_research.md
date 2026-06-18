# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-a100-r.c

## Purpose

This file describes the A100 R-PIO controller, the reduced always-on pin controller for PL pins. It maps PL0-PL11 to sleep-domain GPIO, serial, I2C, PWM, CIR, and JTAG functions.

## Important APIs, Types, And Functions

The core data is `a100_r_pins[]`, `a100_r_pinctrl_data`, `a100_r_pinctrl_probe()`, `a100_r_pinctrl_match[]`, and `a100_r_pinctrl_driver`. The descriptor sets `.pin_base = PL_BASE`, `.irq_banks = 1`, and `.io_bias_cfg_variant = BIAS_VOLTAGE_PIO_POW_MODE_CTL`.

## Control Flow

The platform driver matches `allwinner,sun50i-a100-r-pinctrl`. Probe calls `sunxi_pinctrl_init()`, and the common sunxi driver registers the PL-range pins with R-PIO numbering. Unlike many older sunxi files, this one uses `MODULE_DEVICE_TABLE()` and `module_platform_driver()`.

## State And Persistence

The source owns only static descriptors. Runtime mux, GPIO, IRQ, and bias state live in R-PIO hardware registers and common driver data. R-PIO pin numbering is offset by `PL_BASE`, so persistence and lookup must remain aligned with Linux global pin IDs.

## Dependencies And Integration Points

It depends on the sunxi pinctrl core and OF platform matching. It integrates sleep-domain functions `s_uart0`, `s_i2c0`, `s_i2c1`, `s_jtag`, `s_pwm`, and `s_cir`, with IRQ mappings through mux value `0x6`.

## Risks

The main risks are incorrect `PL_BASE` handling and IO-bias variant selection. A wrong pin base makes all consumers request the wrong global pins, while a wrong bias mode can affect low-power domain voltage handling. Because this controller is small and sleep-domain oriented, missing it can break wake, PMIC, or low-power serial paths even when the main PIO works.

## Test Signals

Validate probe from the R-PIO compatible, debugfs names PL0-PL11, GPIO and IRQ operation on PL pins, wake-capable interrupt behavior, and mux tests for sleep UART, I2C, PWM, CIR, and JTAG.
