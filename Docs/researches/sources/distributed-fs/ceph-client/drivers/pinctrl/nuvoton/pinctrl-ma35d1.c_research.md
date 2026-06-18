# sources/distributed-fs/ceph-client/drivers/pinctrl/nuvoton/pinctrl-ma35d1.c

## Purpose
This file is the MA35D1 SoC-specific pin table and platform-driver wrapper for the common MA35 pinctrl implementation. It enumerates 224 pin descriptors from PA0 through PN15-style ports, records each pin's MFP register offset and bit shift, documents available mux values, supplies the MA35D1 MFP-to-pin-number decoder, and registers the `nuvoton,ma35d1-pinctrl` platform driver.

## Important APIs, types, and functions
The central data is `ma35d1_pins[]`, built with `MA35_PIN()` and `MA35_MUX()` entries. `ma35d1_get_pin_num()` converts an MFP register offset and shift to a linear pin number using `(offset - 0x80) * 2 + shift / 4`. `ma35d1_pinctrl_info` packages the pin table and decoder for the common driver. `ma35d1_pinctrl_probe()` calls `ma35_pinctrl_probe()`. The platform driver uses `ma35d1_pinctrl_of_match`, `DEFINE_NOIRQ_DEV_PM_OPS()`, and `arch_initcall()`.

## Control flow
At architecture init time, `ma35d1_pinctrl_init()` registers the platform driver. OF matching on `nuvoton,ma35d1-pinctrl` calls `ma35d1_pinctrl_probe()`, which delegates all real setup to the common MA35 driver with `ma35d1_pinctrl_info`. Runtime muxing and GPIO handling are then controlled by `pinctrl-ma35.c`; this file only supplies descriptor data and PM callback wiring.

## State and persistence behavior
The SoC pin table and mux descriptors are immutable. The platform driver's runtime state is allocated by the common probe. Hardware persistence happens when common code writes MFP and GPIO registers. The file's initcall choice makes the driver built-in and registered early, consistent with `PINCTRL_MA35D1` being a bool symbol.

## Dependencies and integration points
The file depends on platform-driver, module metadata, PM, pinctrl descriptors, and the local MA35 header. It integrates with device-tree binding data and the common MA35 parser: `nuvoton,pins` triples must use offsets and shifts compatible with `ma35d1_get_pin_num()`. The descriptors cover GPIO, UART, I2C, CAN, SPI/QSPI, SD/eMMC, EBI, LCM, RGMII/RMII, CCAP, PWM, timers, smartcard, JTAG, tamper, USB host, trace, and interrupt functions.

## Risks
The table is large and hardware-sensitive. Wrong offsets, shifts, mux values, or duplicate/conflicting pin numbers can silently mux the wrong pad. The PN entries include repeated names and offsets across linear pin numbers, reflecting package or function variants; that area deserves datasheet cross-checking. Because device-tree mux values are not validated against the `MA35_MUX()` list in common code, an invalid but in-range value could still be written. The decoder formula assumes the MA35D1 MFP block remains a simple 8-byte-per-bank, 4-bit-per-pin layout from base `0x80`.

## Test signals
Build and link with `CONFIG_PINCTRL_MA35D1`, confirm `arch_initcall` registration and OF probe, inspect pinctrl debugfs for all expected pin names, validate representative mux groups across every port bank, test GPIO fallback on each bank, exercise high-value peripherals such as UART0, SD/eMMC, Ethernet RGMII/RMII, LCM, and QSPI, and compare register writes against the MA35D1 datasheet for selected pins.
