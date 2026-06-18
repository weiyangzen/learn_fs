# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun50i-h616-r.c

## Purpose

This small file describes the H616 R-PIO controller for PL0 and PL1. It exposes the sleep-domain pins used for `s_rsb` or `s_i2c` SCK/SDA plus GPIO input/output.

## Important APIs, Types, And Functions

The definitions are `sun50i_h616_r_pins[]`, `sun50i_h616_r_pinctrl_data`, `sun50i_h616_r_pinctrl_probe()`, `sun50i_h616_r_pinctrl_match[]`, and `sun50i_h616_r_pinctrl_driver`. The descriptor sets `.pin_base = PL_BASE` and does not declare IRQ banks.

## Control Flow

The built-in driver matches `allwinner,sun50i-h616-r-pinctrl`. Probe calls `sunxi_pinctrl_init()` and the common core registers two PL pins for GPIO and mux use.

## State And Persistence

All local data is static. Runtime state is the shared core's device data and R-PIO register contents. No local suspend, resume, or IRQ behavior is defined.

## Dependencies And Integration Points

This file depends on OF platform binding and the sunxi common core. It integrates the low-power serial bus pins used by PMIC/control paths through `s_rsb` and `s_i2c` function names.

## Risks

Because only two pins are described, wrong `PL_BASE` or function ordering would break the entire controller. Lack of IRQ bank data means consumers must not expect wake interrupts from this descriptor. Copying richer R-PIO descriptors from other SoCs would add unsupported behavior.

## Test Signals

Validation includes probe, debugfs visibility for PL0 and PL1, GPIO direction/value tests, and functional RSB/I2C communication on the sleep-domain bus.
