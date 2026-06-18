<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt8365-pinfunc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt8365-pinfunc.h

## Purpose

`mt8365-pinfunc.h` is the device-tree binding macro catalog for MediaTek MT8365 pin multiplexing. It lets DTS authors select a physical pad and one of that pad's hardware mux functions using symbolic names instead of raw integer cells.

## Important APIs, Types, and Functions

The file exports 704 preprocessor definitions and depends on `dt-bindings/pinctrl/mt65xx.h` for `MTK_PIN_NO()`. Each exported symbol follows `MT8365_PIN_<pin>_<pad>__FUNC_<function>` and expands to `MTK_PIN_NO(pin) | mux`. The covered pin range is GPIO/pad numbers 0 through 144, with mux values generally 0 through 7. Function groups include GPIO, DPI display, PWM, I2S/TDM audio, SPI, UART, keypad, JTAG/DFD/UDI debug, Ethernet MAC sideband, SD/eMMC, I2C, USB ID/drive-vbus, antenna selection, connectivity top/WiFi/Bluetooth, and debug monitor outputs.

## Control Flow

There is no runtime control flow in this header. The C preprocessor expands a chosen macro in a DTS include context into the integer encoding consumed by the MediaTek pinctrl binding. At boot, the device-tree blob carries those constants to the MTK pinctrl driver, which decodes the pin number and mux selector and programs SoC pinmux registers.

## State and Persistence Behavior

The header stores no state and persists nothing. Its definitions become part of compiled device trees. The effective state is the board's `pinctrl-*` configuration, which the kernel applies during device probe, suspend/resume state changes, or pinctrl state selection.

## Dependencies and Integration Points

The direct dependency is `mt65xx.h`; without the correct `MTK_PIN_NO()` packing convention these values are wrong. Integration points are MT8365 board DTS files, bindings for consumers that reference pinctrl states, and the MediaTek pinctrl driver tables that must agree on pin numbering and mux indices.

## Risks and Edge Cases

The definitions are compile-time valid even when a board chooses an electrically unsafe or conflicting mux. Debug and manufacturing functions such as DFD, UDI, APU/JTAG, `DBG_MON_*`, and test clocks can expose internal signals if selected accidentally. Reused peripheral names appear on multiple pins and mux slots, so DTS review must verify the intended physical pad, not just the function suffix. Any mismatch between this generated catalog and the SoC pinctrl driver's pin table can silently route a device to the wrong pad.

## Test Signals

Useful checks are `dtbs_check` for binding shape, `make dt_binding_check` where applicable, successful DTS compilation using representative MT8365 pin states, boot-time pinctrl debugfs inspection, and hardware smoke tests for display, audio, UART, SPI, SD/eMMC, Ethernet, USB role pins, and connectivity pins. Static checks should confirm all macros use `MTK_PIN_NO(n) | mux`, cover the expected 0-144 pin range, and avoid duplicate symbolic names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt8365-pinfunc.h -->
