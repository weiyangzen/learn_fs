# sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/pinctrl-wm8505.c

## Purpose

This file provides WonderMedia WM8505-specific pinctrl data for the shared `pinctrl-wmt` driver. It defines bank register layouts, pin IDs, pin descriptors, matching group names, and the platform driver for `wm,wm8505-pinctrl`.

## Important APIs, Types, And Data

- `wm8505_banks[]` describes eleven banks. All banks have enable, direction, data-out, and data-in registers; pull-enable and pull-config are `NO_REG`.
- Pin macros and `wm8505_pins[]` enumerate external GPIOs, wake/suspend GPIOs, SD/MMC, video input/output and syncs, NOR data/address bus, AC97, serial flash, SPI0-SPI2, UART0-UART3, and I2C0-I2C2.
- `wm8505_groups[]` mirrors `wm8505_pins[]` by name and order, preserving the common WMT one-pin group model.
- `wm8505_pinctrl_probe()` allocates `wmt_pinctrl_data`, fills static descriptors, and calls `wmt_pinctrl_probe()`.

## Control Flow

The builtin platform driver matches `wm,wm8505-pinctrl`. Probe initializes the common driver data from static arrays and delegates all real pinctrl/GPIO/pinconf behavior to `pinctrl-wmt.c`.

Runtime operations use the bank register offsets to switch mux/GPIO enable, direction, and data bits. Since pull registers are absent, pull configuration support depends on the common driver returning unsupported behavior for those banks.

## State And Persistence

All SoC descriptions are static. The only runtime allocation is the devm-managed `wmt_pinctrl_data` created in probe. Persistent hardware state is register state in the GPIO memory space.

## Dependencies And Integration Points

The file depends on `pinctrl-wmt.h`, `wmt_pinctrl_probe()`, Linux platform APIs, and OF matching through `wm,wm8505-pinctrl`. Kconfig symbol `CONFIG_PINCTRL_WM8505` controls build inclusion.

## Risks And Edge Cases

- The code explicitly says dedicated external GPIOs should remain in bank 0 and banks must not be reordered; this is a Linux pin-numbering ABI risk.
- `wm8505_groups[]` must stay aligned with `wm8505_pins[]`.
- Pull configuration registers are not present, so device-tree states requiring pulls may fail or have no effect.
- The bank 9 data-in offset duplicates bank 0's `0xDC` value in the descriptor table, which may be intentional hardware mapping but is a high-value item to verify against the manual.

## Test Signals

Expected signals include successful probe, matching pin/group counts, GPIO operations on external GPIO and higher banks, and board-level pin use for SD/MMC, NOR, AC97, serial flash, SPI, UART, I2C, and video outputs. Negative pinconf tests should cover pull settings on `NO_REG` pull banks.
