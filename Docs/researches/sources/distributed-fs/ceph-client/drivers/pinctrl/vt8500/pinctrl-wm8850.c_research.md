# sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/pinctrl-wm8850.c

## Purpose

This file provides WonderMedia WM8850 SoC pinctrl data for the common WMT driver. It defines bank registers, pin descriptors, one-pin group names, and the platform driver for `wm,wm8850-pinctrl`.

## Important APIs, Types, And Data

- `wm8850_banks[]` uses the same eleven-bank register layout pattern as WM8750, including pull-enable and pull-config registers.
- `wm8850_pins[]` describes external GPIOs, wakeup and suspend GPIOs, SD0 card detect, video output/input, SPI0, SD0/SD1/SD2 controls, I2C0-I2C2, UART0-UART2, PWM outputs, and SD power/write-protect/card-detect pins.
- `wm8850_groups[]` mirrors the pin descriptors in order for the one-pin group model.
- `wm8850_pinctrl_probe()` allocates `wmt_pinctrl_data`, fills bank/pin/group fields, and calls `wmt_pinctrl_probe()`.

## Control Flow

The builtin platform driver matches `wm,wm8850-pinctrl`. Probe initializes shared WMT data and delegates all operations to the common driver. The common driver handles GPIO direction/data, muxing, and generic pinconf based on the bank offsets and group names.

## State And Persistence

This file provides immutable descriptors only. Runtime data is devm-managed in the common driver. Hardware pin state persists in MMIO registers.

## Dependencies And Integration Points

It depends on `pinctrl-wmt.h`, common WMT logic, Linux platform/OF APIs, and `CONFIG_PINCTRL_WM8850`. It uses OF compatible `wm,wm8850-pinctrl`.

## Risks And Edge Cases

- WM8850 is similar to WM8750 but has a reduced UART/SD2 pin set; copying assumptions from WM8750 could expose nonexistent pins.
- Bank and group order are ABI-sensitive.
- Pull register offsets must match hardware because generic pinconf can alter electrical behavior.
- Group names must stay aligned with pin descriptors for common WMT lookup.

## Test Signals

Probe should expose the expected number of pins and groups. Runtime tests should exercise GPIO, pull configuration, video pins, SPI0, SD0/SD1/SD2 controls present on WM8850, I2C, UART0-UART2, PWM, and wake/suspend GPIOs.
