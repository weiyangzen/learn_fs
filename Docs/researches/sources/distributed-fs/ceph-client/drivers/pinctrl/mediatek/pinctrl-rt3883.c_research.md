# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-rt3883.c

## Purpose
This file is the RT3883-specific MTMIPS pinmux driver. It describes RT3883 GPIO mode fields and group/function pin ranges, then registers a platform driver that delegates to the shared MTMIPS pinctrl core.

## Important APIs, Types, And Data
The file defines multi-bit mode constants for UART0, PCI, LNA_A, and LNA_G plus single-bit positions for I2C, SPI, UART1, JTAG, MDIO, GE1, and GE2. Function groups include I2C, SPI, multi-option UARTF, UART lite, JTAG, MDIO, LNA A/G, PCI with four mux values (`pci-dev`, `pci-host2`, `pci-host1`, `pci-fnc`), GE1, and GE2. `rt3883_pinmux_data[]` is the sentinel-terminated table passed to `mtmips_pinctrl_init()`.

## Control Flow
`rt3883_pinctrl_probe()` directly calls `mtmips_pinctrl_init()`. The platform driver matches `ralink,rt3883-pinctrl` and legacy `ralink,rt2880-pinmux`, and registers during `core_initcall_sync()`.

## State And Persistence
State is shared-core mutable table data plus hardware sysc GPIO mode registers. PCI, UARTF, and LNA selections are encoded as multi-bit fields in the register state.

## Dependencies
The driver depends on `pinctrl-mtmips.h`, Linux platform/of/module infrastructure, and the shared MTMIPS implementation. The mode constants must match RT3883 sysc register layout, including fields whose shifts already encode high bit positions.

## Risks
Multi-bit groups are the high-risk paths: UARTF has partial GPIO options, PCI has four function values over a 32-pin range, and LNA fields use shifted masks. The `GRP()` macro expects an unshifted mask plus shift, so passing a pre-shifted value would be dangerous; this file uses unshifted masks for PCI and LNA group masks via explicit mask constants.

## Test Signals
Boot with RT3883 compatible, verify groups and functions, exercise PCI mode values, UARTF mode values, LNA A/G, and GE1/GE2. Check sysc register field values after mux application and GPIO request behavior for pins returned to GPIO mode.
