# sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-ld20.c

## Purpose

This file provides the UniPhier LD20 pin controller description. It lists LD20 pins, pin groups, mux values, functions, GPIO-only ranges, capability flags, and the platform-driver binding consumed by the shared UniPhier core.

## Important APIs, Types, And Functions

`uniphier_ld20_pins` contains 176 packed pin descriptors. The file defines 58 mux groups plus 3 GPIO-only groups and 38 pinmux functions. Compared with LD11, LD20 has broader audio coverage, both RGMII and RMII Ethernet groups, more HSC input variants, SD, four SPI controllers, and USB0-USB3 groups.

`uniphier_ld20_get_gpio_muxval()` matches the LD11 GPIO policy: XIRQ12 and XIRQ15 use mux value 13, XIRQ offsets 120-143 use mux value 14, and all other GPIOs use mux value 15. `uniphier_ld20_pindata` sets `UNIPHIER_PINCTRL_CAPS_PERPIN_IECTRL`, so input-enable is interpreted per pin. The OF compatible is `socionext,uniphier-ld20-pinctrl`.

## Control Flow

Probe is a thin wrapper around `uniphier_pinctrl_probe(pdev, &uniphier_ld20_pindata)`. The shared core validates and registers the LD20 arrays, then all runtime operations are table-driven: function selection applies a group's mux values pin by pin; GPIO requests compute a GPIO mux value through LD20's callback; bias, drive, and input-enable operations decode the packed metadata in `uniphier_ld20_pins`.

## State And Persistence

The LD20 source is immutable static data and has no local state machine. Hardware pin state is mutable through the shared regmap. Per-pin input-enable capability affects both runtime config and the set of input-enable registers saved by the shared PM code.

## Dependencies And Integration Points

The file integrates with the platform bus, OF compatible matching, Linux pinctrl via the shared core, and board pinctrl states that refer to the group/function names. It depends on `pinctrl-uniphier.h` for metadata packing and array macros.

## Risks

LD20 contains many overlapping media/audio and serial alternatives with high mux values such as 26 and 27 for some audio input groups. Any group/mux mismatch can be difficult to diagnose because the shared core trusts the arrays and only validates array lengths through macros. The SD group comment notes no `SDVOLC`, which is a board-integration risk if device trees assume voltage-control routing. GPIO XIRQ handling shares the same offset-sensitive risks as LD11. Per-pin input-enable must match the hardware register model.

## Test Signals

Test signals include successful DT probe, pinmux activation for RGMII and RMII Ethernet, eMMC plus `emmc_dat8`, SD without voltage-control expectations, all SPI and UART groups, USB0-USB3, audio groups with alternate `aout1b` and high mux values, GPIO tests over the three GPIO ranges, XIRQ-specific GPIO request tests, pinconf get/set on representative pull and drive classes, and suspend/resume retention of mux and input-enable registers.
