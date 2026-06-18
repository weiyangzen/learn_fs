# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-a64-r.c

## Purpose

This file describes the Allwinner A64 R-PIO controller, covering sleep-domain PL0-PL12 pins. It supplies the reduced R-bank pin table used for low-power serial, RSB/I2C, PWM, CIR, JTAG, GPIO, and wake interrupt use cases.

## Important APIs, Types, And Functions

The file defines `sun50i_a64_r_pins[]`, `sun50i_a64_r_pinctrl_data`, `sun50i_a64_r_pinctrl_probe()`, `sun50i_a64_r_pinctrl_match[]`, and `sun50i_a64_r_pinctrl_driver`. The descriptor sets `.pin_base = PL_BASE` and `.irq_banks = 1`.

## Control Flow

The built-in platform driver binds to `allwinner,sun50i-a64-r-pinctrl`. Probe calls `sunxi_pinctrl_init()` with the R-PIO descriptor. The shared core uses `PL_BASE` to expose the pins under the global PL numbering and handles mux, GPIO, and IRQ requests.

## State And Persistence

This source contains immutable data only. Runtime state is in common sunxi objects and R-PIO registers. The wake/sleep domain nature means register state may be relevant across low-power transitions, but no local suspend/resume logic is implemented here.

## Dependencies And Integration Points

The table integrates `s_rsb`, `s_i2c`, `s_uart`, `s_jtag`, `s_pwm`, and `s_cir_rx` functions, plus PL external interrupts through mux value `0x6`. It depends on the shared sunxi core and OF platform matching.

## Risks

`PL_BASE` must match the core's global pin numbering or every consumer is shifted. R-PIO pins often back PMIC or wake functions, so missing IRQ entries or wrong mux values can produce power-management failures rather than obvious boot failures. A64 lacks the explicit IO-bias variant used by newer R-PIO files, so copying descriptors between SoCs would be unsafe.

## Test Signals

Validate binding, debugfs PL0-PL12 visibility, GPIO and PL_EINT tests, suspend/wake tests, and functional checks for RSB/I2C to PMIC, sleep UART, PWM, CIR receive, and JTAG pins.
