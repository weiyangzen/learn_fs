# sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/pinctrl-wm8750.c

## Purpose

This file provides WonderMedia WM8750-specific descriptor data for the shared WMT pinctrl driver. It defines eleven banks, pin descriptors, group names, and the builtin platform driver for `wm,wm8750-pinctrl`.

## Important APIs, Types, And Data

- `wm8750_banks[]` describes eleven banks with enable, direction, data-out, data-in, pull-enable, and pull-config register offsets.
- `wm8750_pins[]` covers external GPIOs, wake pins, SD0 card detect, 24-bit video output, video input, SPI0 with multiple chip-selects, SD0/SD1/SD2 buses and control pins, I2C0-I2C2, UART0-UART3, PWM outputs, and SD power/write-protect/card-detect pins.
- `wm8750_groups[]` mirrors pin names in descriptor order.
- `wm8750_pinctrl_probe()` allocates `wmt_pinctrl_data`, assigns static descriptors, and calls the common WMT probe.

## Control Flow

The platform driver binds to `wm,wm8750-pinctrl`. Probe delegates to the common driver, which uses bank offsets and pin/group arrays to implement pinctrl, pinmux, GPIO, and pinconf operations.

## State And Persistence

Static arrays are immutable. Runtime state is held by the common driver through a devm-managed `wmt_pinctrl_data`. Hardware state persists in GPIO/pinctrl registers, including pull registers.

## Dependencies And Integration Points

The file depends on `pinctrl-wmt.h`, the common WMT implementation, Linux platform APIs, and OF. It is built by `CONFIG_PINCTRL_WM8750` and matches `wm,wm8750-pinctrl`.

## Risks And Edge Cases

- Bank and pin ordering must not change because it changes Linux pin numbering.
- WM8750 has three SD interfaces plus SPI chip-select alternatives and PWM outputs; pin conflicts are likely if device-tree states are not carefully composed.
- The group list must remain order-aligned with `wm8750_pins[]`.
- Pull support makes register offset accuracy important for board-level signal integrity.

## Test Signals

Probe should expose matching pin/group counts. GPIO and pinconf tests should cover pull-enabled banks. Board smoke tests should exercise SPI0, SD0/SD1/SD2 including power and card-detect lines, I2C, UART, PWM, and video pins.
