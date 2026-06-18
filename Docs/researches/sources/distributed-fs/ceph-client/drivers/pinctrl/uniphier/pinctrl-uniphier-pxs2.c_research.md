# sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-pxs2.c

## Purpose

This file provides Socionext UniPhier PXs2-specific pinctrl data. It describes the PXs2 pin universe, peripheral groups, pinmux functions, GPIO ranges, SoC GPIO mux callback, and platform driver for `socionext,uniphier-pxs2-pinctrl`.

The file is a hardware-description companion to the common UniPhier pinctrl core. It does not implement generic pinctrl algorithms; it supplies the static data consumed by those algorithms.

## Important APIs, Types, And Data

- `uniphier_pxs2_pins[]` is the PXs2 `struct pinctrl_pin_desc` table, with each pin carrying packed input-enable, drive, pull, and pull-direction metadata through `UNIPHIER_PINCTRL_PIN`.
- Peripheral pin groups include audio input/output groups (`ain1`, `ain2`, `ain3`, `aout1`, `aout2`, `aout3`, IEC pins, and data-width extensions), `emmc`, Ethernet in `ether_mii`, `ether_rgmii`, and `ether_rmii` modes, I2C, NAND with `nand_cs1`, SD, SPI, system bus, UART alternatives, and USB host/device groups.
- `gpio_range0_pins[]` and `gpio_range1_pins[]` describe GPIO exposure ranges for the common driver.
- `uniphier_pxs2_groups[]` binds named groups to pin lists and mux-value arrays.
- `uniphier_pxs2_functions[]` maps functions to one or more groups. Several functions expose alternative groups, such as UART and USB device variants.
- `uniphier_pxs2_get_gpio_muxval()` handles the GPIO mux selection rule for ordinary pins and XIRQ aliases.
- `uniphier_pxs2_pindata` exports all SoC data to `uniphier_pinctrl_probe()`.

## Control Flow

The builtin platform driver matches `socionext,uniphier-pxs2-pinctrl`, then `uniphier_pxs2_pinctrl_probe()` delegates to the common UniPhier probe with `uniphier_pxs2_pindata`.

During normal pinctrl operation, device-tree pinctrl states resolve function names to groups in `uniphier_pxs2_functions[]`, then the common core writes group mux values for the listed pins. GPIO requests flow through `uniphier_pxs2_get_gpio_muxval()`: offsets `120..143`, used for XIRQ aliases, return mux value `14`; all other offsets return `15`.

## State And Persistence

All SoC data in this file is `static const` and immutable. The only persistent state affected by this file is hardware register state written by the common driver using this metadata. There are no file-local locks, allocations, caches, or suspend state.

## Dependencies And Integration Points

This file depends on `pinctrl-uniphier.h` and the common UniPhier driver. It integrates with OF through `socionext,uniphier-pxs2-pinctrl`, with the platform driver core via `builtin_platform_driver`, and with the pinctrl subsystem through the shared `uniphier_pinctrl_probe()` implementation.

Unlike Pro5 and PXs3, `uniphier_pxs2_pindata.caps` is `0`, so the common driver should use baseline UniPhier behavior without separate debug mux or per-pin input-enable capability flags.

## Risks And Edge Cases

- PXs2 includes many alternative and overlapping groups, especially audio, UART, Ethernet, and USB device functions. Incorrect group membership or mux values can break only one alternate mode while leaving others functional.
- The XIRQ GPIO rule relies on GPIO offsets rather than only physical pin numbers; device-tree GPIO ranges must match the callback’s offset assumptions.
- Some groups extend base functions with data-width variants, such as `ain*_dat2`, `ain*_dat4`, `aout*_dat2`, and `aout*_dat4`; missing these in device-tree states can produce partial bus wiring.
- Static compile-time checks catch only pin-array versus mux-array length mismatches, not whether register indices or mux values are electrically valid.

## Test Signals

Validation should include probe against a PXs2-compatible node, device-tree pinmux states for audio, Ethernet MII/RGMII/RMII, eMMC, NAND, SD, UART, USB host/device, and SPI, plus GPIO request tests for ordinary offsets and XIRQ alias offsets. Functional tests should verify wide bus variants such as eMMC DAT8 and audio data-extension groups.
