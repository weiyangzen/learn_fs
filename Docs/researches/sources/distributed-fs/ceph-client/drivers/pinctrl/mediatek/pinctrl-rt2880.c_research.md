# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-rt2880.c

## Purpose
This file is the RT2880-specific MTMIPS pinmux driver. It declares RT2880 sysc GPIO mode bits, maps each mux group to a contiguous pin range, and registers a platform driver that calls `mtmips_pinctrl_init()`.

## Important APIs, Types, And Data
The SoC data is `rt2880_pinmux_data_act[]`, a sentinel-terminated `struct mtmips_pmx_group` array. Groups are `i2c`, `spi`, `uartlite`, `jtag`, `mdio`, `sdram`, and `pci`. The function arrays are simple one-function groups built with `FUNC()`: I2C pins 1-2, SPI pins 3-6, UART lite pins 7-14, JTAG pins 17-21, MDIO pins 22-23, SDRAM pins 24-39, and PCI pins 40-71.

## Control Flow
`rt2880_pinctrl_probe()` delegates directly to `mtmips_pinctrl_init()`. The platform driver matches `ralink,rt2880-pinctrl` and legacy `ralink,rt2880-pinmux`. Registration uses `core_initcall_sync()`, making it available early for board initialization.

## State And Persistence
The file itself has static mutable function/group arrays because the shared MTMIPS core fills runtime backpointers and enabled flags into the structs. Hardware mux state is stored in Ralink sysc GPIO mode registers.

## Dependencies
It depends on `pinctrl-mtmips.h`, Linux platform/of/module headers, and the shared MTMIPS core. The bit definitions must match RT2880 `SYSC_REG_GPIO_MODE` layout.

## Risks
The PCI group spans 32 pins and can move a large external bus at once. Since every group has a single non-GPIO function with mux value zero, the shared core relies entirely on the group mask/shift to distinguish GPIO from active peripheral mode. Incorrect shifts or masks would directly corrupt sysc mode bits.

## Test Signals
Boot an RT2880 DT with this compatible, verify early driver registration, inspect generated groups/functions, apply each mux state, and compare sysc GPIO mode register bits against expected values. GPIO request tests should fail when a pin is muxed away from GPIO.
