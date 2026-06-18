# sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/pinctrl-wm8650.c

## Purpose

This file supplies WonderMedia WM8650 pinctrl data to the common WMT driver. It describes eight GPIO banks with pull support, pin IDs, pin descriptors, one-pin groups, and the platform driver for `wm,wm8650-pinctrl`.

## Important APIs, Types, And Data

- `wm8650_banks[]` defines eight banks with enable, direction, data-out, data-in, pull-enable, and pull-config registers.
- `wm8650_pins[]` includes external GPIOs, wake/suspend GPIOs, SD card-detect pins, 24-bit video output, video input, I2C, SPI0, SD0/SD1 buses, UART0-UART3, keypad rows/columns, and SD1 control pins.
- `wm8650_groups[]` mirrors the pin descriptor names in order.
- `wm8650_pinctrl_probe()` allocates and populates `wmt_pinctrl_data` before calling the shared WMT probe.

## Control Flow

The builtin platform driver binds to `wm,wm8650-pinctrl` and delegates to `wmt_pinctrl_probe()`. The common driver interprets bank offsets and one-pin groups for GPIO, pinmux, and generic pinconf operations.

Because pull-enable and pull-config registers are present for all banks, generic pull configuration has real hardware-backed state on this SoC.

## State And Persistence

The source’s static arrays are immutable. Probe-created `wmt_pinctrl_data` is devm-managed. Hardware state persists in bank registers, including pull-enable and pull-config state.

## Dependencies And Integration Points

It depends on `pinctrl-wmt.h`, the common WMT driver, platform/OF APIs, and `CONFIG_PINCTRL_WM8650`. The OF compatible is `wm,wm8650-pinctrl`.

## Risks And Edge Cases

- Bank order and pin order are ABI-sensitive.
- Pull register support means incorrect pull offsets affect electrical behavior directly, unlike older no-pull variants.
- The pin set has multiple SD buses and SD card-detect/write-protect pins; board device trees must select the intended bus and avoid conflicts.
- Group names must remain aligned with pin descriptor order.

## Test Signals

Probe and pin/group count should match. GPIO tests should exercise several banks and pull configuration. Board-level smoke tests should cover video, I2C, SPI0, SD0/SD1, UARTs, keypad, and card-detect/write-protect pins.
