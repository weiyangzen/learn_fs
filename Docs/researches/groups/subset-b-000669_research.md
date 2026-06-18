# subset-b-000669 Research

Grouped research for the listed Ceph-client Linux device-tree pin function headers. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8mp-pinfunc.h -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8mp-pinfunc.h

## Purpose
Defines the i.MX8M Plus (`MX8MP`) pin function constants consumed by Freescale/NXP ARM64 device-tree sources. The file is not executable C logic; it is a Device Tree Source include that maps symbolic pad/function names to the numeric IOMUXC tuple format expected by the `fsl,imx-pinctrl` binding. It lets board DTS files write readable pin groups such as `MX8MP_IOMUXC_SD1_CLK__USDHC1_CLK` plus a pad-control value instead of embedding register offsets and mux selector values directly.

This header also carries reusable pad-control bit helpers for i.MX8MP electrical configuration. Those helpers cover drive strength (`MX8MP_DSE_X1`, `MX8MP_DSE_X2`, `MX8MP_DSE_X4`, `MX8MP_DSE_X6`), slew rate (`MX8MP_FSEL_FAST`/`SLOW`), open drain, pull direction, hysteresis, pull enable, and the `MX8MP_SION` force-input bit. `MX8MP_USDHC_DATA_DEFAULT` and `MX8MP_I2C_DEFAULT` are compound defaults for common USDHC data and I2C pin states.

## Important APIs, Types, And Functions
- Include guard: `__DTS_IMX8MP_PINFUNC_H`.
- Pin macro namespace: `MX8MP_IOMUXC_<PAD>__<FUNCTION>`.
- Pin tuple layout: `<mux_reg conf_reg input_reg mux_mode input_val>`, matching the comment above the macro table.
- Pad-control helpers: named bit values and compound default expressions intended for the final config cell in `fsl,pins` entries.
- Source coverage: 785 `MX8MP_IOMUXC_` pin-function macros across about 143 distinct pads, plus the electrical helper macros at the top.

Representative pad/function families include GPIO1_IO00-15 for GPIO, clocks, watchdog, USB, PWM, ISP triggers, PMIC ready, and SDMA events; ENET_QOS and ENET1/RGMII pads with audio/PDM/USDHC3 alternates; USDHC1/2/3 storage pads; NAND/FLEXSPI pads with coresight, SAI, UART, I2C, ISP, and USDHC3 alternates; SAI1/2/3/5 audio banks with PDM, CAN, GPT, Ethernet, and UART alternates; ECSPI1/2, I2C1-4, UART1-4, SPDIF, HDMI DDC/CEC/HPD, PCIe clock request, and CAN alternates.

## Control Flow
The only "flow" is preprocessing and device-tree compilation:

1. A board or SoC `.dts`/`.dtsi` includes this header.
2. Pin-control nodes reference one or more `MX8MP_IOMUXC_*` macros inside `fsl,pins` arrays.
3. The C preprocessor expands each symbolic macro to five numeric cells.
4. The device-tree compiler stores the cells in the DTB.
5. At boot, the i.MX pinctrl driver interprets the mux register offset, config register offset, optional input-select register offset, mux mode, and daisy-chain input value, then applies the trailing pad-control config cell supplied by the DTS author.

There are no functions, loops, conditionals, runtime branches, or callbacks in this file. Ordering is nevertheless meaningful for maintainability: macros are grouped by physical pad order, and repeated `input_reg` values with different `input_val` selectors describe daisy-chain alternatives for peripherals that can be routed through multiple pads.

## State And Persistence
The header stores no runtime state. Its values become persistent only after being compiled into a DTB and shipped in firmware, boot partitions, or kernel image artifacts. A wrong tuple is therefore a static hardware-description bug: it can persist across boots until the DTB or source is corrected. The pad-control helper macros do not program hardware by themselves; they are constants used by downstream DTS files.

## Dependencies And Integration Points
- Integrated with Linux ARM64 Freescale/NXP DTS files under the same tree.
- Consumed by the device-tree preprocessor and compiler, not by normal C object compilation.
- Interpreted at runtime by the i.MX pinctrl driver and the generic pinctrl framework through `fsl,pins`.
- Depends on the SoC reference manual/register layout staying consistent with mux/config/input register offsets and daisy-chain values.
- Integrates indirectly with many peripheral drivers: USDHC, EQoS/ENET, FLEXSPI/NAND, SAI/PDM/SPDIF/HDMI audio/display blocks, I2C, ECSPI, UART, USB OTG, CAN, GPT, PWM, PCIe, watchdog, PMIC, and GPIO.

## Risks And Edge Cases
- Tuple-cell mistakes are silent at compile time because the macros are just numbers; the failure appears as nonfunctional hardware, wrong peripheral routing, or pin contention.
- The i.MX8MP tuple includes both mux and config register offsets. Copying an i.MX8MQ or i.MX8ULP macro shape into this file would corrupt downstream `fsl,pins` layout.
- `input_reg` values of `0x000` mean no daisy-chain input select is needed, while nonzero input registers require the correct `input_val`; mismatches can break only RX/input paths while TX still appears functional.
- `MX8MP_SION` forces input mode and is appropriate for I2C-style bidirectional use, but overuse can change signal behavior or power characteristics.
- Shared pads expose mutually exclusive functions. Board files must ensure that pin groups do not route the same pad to multiple active peripherals.
- Helper defaults are convenience macros, not universal electrical guarantees; high-speed USDHC, open-drain I2C, voltage-select, and board-specific pull requirements still need schematic review.

## Test Signals
- `dtc`/kernel build success verifies that macros expand syntactically and that include guards do not collide.
- Device-tree binding checks can catch malformed pinctrl properties but generally cannot validate every SoC register offset.
- Boot logs from the i.MX pinctrl driver and peripheral probes reveal missing/invalid pinctrl states.
- Hardware smoke tests are the strongest signal: USDHC card/eMMC detection and tuning, Ethernet link/MDIO, I2C bus scan, UART console, SPI transfers, audio clock/data capture, HDMI DDC/CEC/HPD behavior, USB ID/OC/PWR handling, CAN RX/TX, and GPIO toggling.
- Regression review should diff macro tuples against NXP/Linux upstream or the reference manual when changing offsets, mux modes, or daisy-chain values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8mp-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8mq-pinfunc.h -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8mq-pinfunc.h

## Purpose
Defines symbolic pin-function constants for the i.MX8M Quad (`MX8MQ`) device-tree pinctrl binding. Board and SoC DTS files use these constants to configure physical pads for GPIO, storage, networking, audio, serial, boot, debug, and control functions without hard-coding IOMUXC register offsets or mux selector values.

Unlike the i.MX8MP header in the same directory, this file is a pure pin tuple catalog. It does not define electrical pad-control helper bit macros. The DTS author supplies pad-control config values separately after each expanded pin tuple.

## Important APIs, Types, And Functions
- Include guard: `__DTS_IMX8MQ_PINFUNC_H`.
- Pin macro namespace: `MX8MQ_IOMUXC_<PAD>_<FUNCTION>`. This older naming style uses a single underscore between pad and function rather than the double-underscore separator used in newer i.MX8MP/ULP headers.
- Pin tuple layout: `<mux_reg conf_reg input_reg mux_mode input_val>`.
- Source coverage: 607 `MX8MQ_IOMUXC_` macros.

The table begins with always-on/control-style pads such as `PMIC_STBY_REQ`, `PMIC_ON_REQ`, `ONOFF`, `POR_B`, and `RTC_RESET_B`, then covers GPIO1_IO00-15, ENET RGMII/MDIO/MDC, USDHC1/2, NAND/QSPI, SAI1/2/3/5/6, SPDIF, ECSPI1/2, I2C1-4, UART1-4, PCIe clock request, coresight trace, boot configuration, test/observe outputs, SIM/TPSMP debug-style signals, JTAG pins, boot mode pins, and RTC.

The final entries such as `MX8MQ_IOMUXC_TEST_MODE`, `BOOT_MODE0`, `BOOT_MODE1`, JTAG pins, and `RTC` have `mux_reg` set to `0x000` and only provide config-register positions. They still use the same five-cell shape so they can fit the binding's expected cell layout.

## Control Flow
The file has no executable control flow. Its data path is:

1. DTS sources include this header.
2. `fsl,pins` arrays reference `MX8MQ_IOMUXC_*` symbols and append board-specific pad-control values.
3. Preprocessing expands each symbol into the five cells required by the i.MX pinctrl binding.
4. The DTB embeds those cells.
5. The kernel's i.MX pinctrl driver programs mux/config/input-select registers when the relevant pinctrl state is selected by a peripheral driver.

Macro order follows the hardware register/pad order, which makes diff review against reference material practical. Multiple macros can share one `input_reg` with different `input_val` selectors when the same peripheral input can be daisy-chained through multiple pads.

## State And Persistence
The header itself is immutable source data and stores no runtime state. Once compiled into a board DTB, its expanded values persist as part of the board hardware description. Runtime pinctrl state transitions, such as default/sleep states selected by drivers, are driven by DTS users of these macros rather than by this header.

## Dependencies And Integration Points
- Depends on the i.MX8MQ IOMUXC register map and input daisy-chain selector definitions.
- Integrated with ARM64 Freescale/NXP DTS and DTSI files for i.MX8MQ boards.
- Consumed by the Linux device-tree C preprocessor and `dtc`.
- Interpreted by the i.MX pinctrl driver through the standard `fsl,pins` cell contract.
- Affects peripheral integration for PMIC/power controls, USB OTG ID/PWR/OC, USDHC, ENET/RGMII, RAWNAND/QSPI, SAI/SPDIF, ECSPI, I2C, UART, PWM, SDMA events, PCIe clock request, GPIO, JTAG/debug, and boot-mode handling.

## Risks And Edge Cases
- The macro separator convention differs from i.MX8MP and i.MX8ULP. Mechanical searches or generated conversions that assume `PAD__FUNCTION` names can miss or corrupt this file.
- The tuple shape matches i.MX8MP but not i.MX8ULP. Reusing ULP four-cell macros in i.MX8MQ pinctrl states would shift the pad-control cell into the wrong position.
- Some control and JTAG/boot macros use `mux_reg` `0x000`; tooling that treats zero mux offset as invalid would report false positives.
- Many alternate functions are test, observe, SIM/TPSMP, boot-config, or coresight signals that should not be enabled accidentally on production boards.
- `input_reg`/`input_val` errors are hard to catch without hardware because transmit-only signals can still work while receive/input selection is wrong.
- This header does not provide pad-control presets. Board files must choose pull, drive, hysteresis, open-drain, and speed settings explicitly and appropriately.

## Test Signals
- Device-tree compilation catches missing macro names and gross syntax errors.
- Binding validation can verify pinctrl property shape, while tuple correctness needs register-map review or hardware tests.
- Boot and probe logs should show successful pinctrl state application and peripheral initialization.
- Hardware tests should cover Ethernet MDIO/link, USDHC card/eMMC operation, USB OTG role/power/overcurrent signals, UART console/flow control, I2C/SPI transactions, audio clocks/data lines, NAND/QSPI access, GPIO direction/value, and PMIC/power button behavior.
- For edits, compare macro offsets and daisy values against upstream Linux/NXP data and inspect affected board DTS files for tuple-shape assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8mq-pinfunc.h -->

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
