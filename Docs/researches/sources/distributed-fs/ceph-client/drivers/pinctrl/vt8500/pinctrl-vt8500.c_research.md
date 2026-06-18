# sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/pinctrl-vt8500.c

## Purpose

This file supplies VIA VT8500 SoC-specific data to the shared WonderMedia/VIA `pinctrl-wmt` driver. It defines GPIO bank register offsets, symbolic pin IDs, pin descriptors, one-pin group names, and the platform driver for `via,vt8500-pinctrl`.

## Important APIs, Types, And Data

- `vt8500_banks[]` describes seven WMT GPIO banks with enable, direction, data-out, data-in, pull-enable, and pull-config register offsets. Pull registers are `NO_REG` for all banks.
- `WMT_PIN_*` macros map bank/bit pairs to packed pin IDs with `WMT_PIN(bank, bit)`.
- `vt8500_pins[]` enumerates external GPIOs, UARTs, SPI, SD/MMC/MS, I2C, MII Ethernet, serial EEPROM, IDE, video in/out, NAND control, transport stream, and LCD pins.
- `vt8500_groups[]` is a name array matching `vt8500_pins[]` order; each group is effectively one pin for the common WMT model.
- `vt8500_pinctrl_probe()` allocates `struct wmt_pinctrl_data`, fills bank/pin/group counts and pointers, and calls `wmt_pinctrl_probe()`.

## Control Flow

The builtin platform driver binds to `via,vt8500-pinctrl`. Probe allocates devm-managed `wmt_pinctrl_data`, assigns static arrays, and delegates to the common WMT probe. Runtime pinctrl operations are implemented by `pinctrl-wmt.c`, which uses bank offsets to manipulate GPIO enable, direction, input, output, and pinconf registers.

## State And Persistence

This file has no mutable state after probe allocation. The `wmt_pinctrl_data` instance is devm-managed by the platform device. Hardware register state is persisted in the GPIO/pinctrl register block until changed or reset.

## Dependencies And Integration Points

The source depends on `pinctrl-wmt.h`, Linux platform driver APIs, and the common WMT implementation. It integrates with OF through `via,vt8500-pinctrl` and with Kconfig through `CONFIG_PINCTRL_VT8500`.

The comment warns not to reorder banks because bank ordering defines stable Linux pin numbering, especially dedicated external GPIOs in bank 0.

## Risks And Edge Cases

- Reordering bank descriptors or pin arrays changes ABI-visible pin numbers.
- Bank 0 has `NO_REG` for enable, marking dedicated GPIO behavior in the common core; incorrect `NO_REG` usage changes mux/GPIO semantics.
- Pull registers are unavailable for all VT8500 banks, so generic pull configuration should be unsupported or ignored by the common driver.
- The group array must remain in exactly the same order as `vt8500_pins[]`.

## Test Signals

Probe should succeed for `via,vt8500-pinctrl`. GPIO tests should cover dedicated external GPIO bank 0 and non-dedicated banks. Pinctrl debugfs should list the same number of pins and groups. Board tests should exercise UART, SPI, SD/MMC, I2C, MII, LCD, video, IDE, and NAND pins where available.
