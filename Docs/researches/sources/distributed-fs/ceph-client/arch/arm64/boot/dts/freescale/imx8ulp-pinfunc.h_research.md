<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8ulp-pinfunc.h -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8ulp-pinfunc.h

## Purpose
Defines the i.MX8ULP (`MX8ULP`) pad/function constants used by device-tree pinctrl nodes. It provides a symbolic mapping from package pad names (`PTD*`, `PTE*`, `PTF*`, and boot-mode pads) to mux mode and input-select values for the UltraLite Plus IOMUXC layout.

This header is a data catalog, not an implementation file. It allows DTS files to name pad functions such as `MX8ULP_PAD_PTE14__ENET0_MDIO` or `MX8ULP_PAD_PTD1__SDHC0_CMD` while emitting the numeric cells expected by the i.MX8ULP pinctrl binding.

## Important APIs, Types, And Functions
- Include guard: `__DTS_IMX8ULP_PINFUNC_H`.
- Pin macro namespace: `MX8ULP_PAD_<PAD>__<FUNCTION>`.
- Pin tuple layout: `<mux_reg input_reg mux_mode input_val>`. This is a four-cell layout and intentionally omits the separate config-register cell used by i.MX8MP/i.MX8MQ.
- Source coverage: 964 `MX8ULP_PAD_` macros across 82 distinct pads.

The table is organized by pad banks: `PTD0`-`PTD23`, `PTE0`-`PTE23`, `PTF0`-`PTF31`, and `BOOT_MODE0/1`. Alternate functions include GPIO-like port functions, FXIO1, LPSPI4/5, LPUART4-7, LPI2C4-7, I3C2, TPM4-8, I2S4-7, SPDIF, SDHC0-2, FLEXSPI2 A/B, USB0/1 ID/PWR/OC, ENET0 RMII/RGMII-style signals and IEEE1588 timers, EPDC0, DBI0, DPI0, TRACE0, watchdog resets, WUU wakeup inputs, MQS audio, clock outputs, and low-power/high-voltage debug muxes.

## Control Flow
The file contributes static data to the device-tree build:

1. A DTS/DTSI source includes this header.
2. A pinctrl group references one or more `MX8ULP_PAD_*` macros.
3. The preprocessor expands each macro to four cells.
4. The device-tree compiler stores those cells with any additional pad config values required by the binding.
5. The i.MX8ULP pinctrl driver programs the mux register and, when `input_reg` is nonzero, the peripheral input-select/daisy register with `input_val`.

No functions execute from this header. Register offsets increase in physical pad order, and the many repeated peripheral names with different `input_val` values encode selectable input routes from alternative pads.

## State And Persistence
There is no mutable state. The constants become part of the compiled DTB and remain persistent board description data until the DTB is replaced. Runtime pin ownership, sleep/default switching, and electrical configuration are controlled by consuming DTS pinctrl nodes and the kernel pinctrl subsystem, not by this header itself.

## Dependencies And Integration Points
- Depends on the i.MX8ULP IOMUXC register map, mux mode assignments, and input-select register definitions.
- Integrated with Freescale/NXP ARM64 device-tree files for i.MX8ULP boards.
- Consumed by the device-tree preprocessor and `dtc`.
- Interpreted by the i.MX pinctrl driver using the i.MX8ULP-specific four-cell pin-function format.
- Integrates indirectly with many subsystem drivers: SDHC, USB, ENET, LPUART, LPI2C/I3C, LPSPI, I2S/SAI-style audio, SPDIF, TPM/PWM, FLEXSPI, display/EPDC/DBI/DPI, watchdog, wakeup unit, trace/debug, GPIO/port, and clock output users.

## Risks And Edge Cases
- The four-cell tuple shape is the major compatibility hazard. Copying five-cell i.MX8MP/i.MX8MQ macros or parsers into this context will misalign all following pad configuration cells.
- Some pads define mux mode `0x0` for debug mux variants while most normal port functions use mode `0x1`; validation should not assume mode zero is always invalid.
- Many macros share peripheral input registers with different `input_val` selectors. Wrong daisy values can create subtle receive-only failures.
- Several pads expose debug, trace, watchdog reset, boot-mode, WUU wake, and low-power/high-voltage debug mux functions. Accidental selection can affect boot, power, reset, wake, or debug visibility.
- Display, storage, Ethernet, and FLEXSPI functions are spread across wide pad groups. Board files must avoid overlapping pin groups and must match the schematic's lane ordering.
- This file has no electrical helper definitions. Downstream pinctrl nodes must still provide correct pull/drive/open-drain/speed settings for board wiring and signal rate.

## Test Signals
- Successful device-tree preprocessing/build verifies macro names and tuple arity in consumers.
- Binding checks should be run for board DTS files that use these macros, especially to catch incorrect cell counts.
- Boot logs should show successful pinctrl state selection for enabled peripherals.
- Hardware validation should exercise SDHC0/1/2, FLEXSPI2, ENET0 link and MDIO/1588 paths, USB0/1 ID/PWR/OC behavior, LPUART RX/TX/flow control, LPI2C/I3C bus scans, LPSPI transfers, TPM outputs/capture inputs, I2S/SPDIF audio clocks and data, display/EPDC paths, watchdog reset lines, WUU wake pins, and GPIO direction/value changes.
- For changes, compare the affected macros against upstream Linux/NXP headers and inspect all DTS users for four-cell tuple expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8ulp-pinfunc.h -->
