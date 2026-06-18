# subset-b-005830 Research

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/nomadik.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/nomadik.h

## Purpose

`nomadik.h` provides small numeric constants for ST-Ericsson Nomadik pinctrl device-tree properties. It names pull, direction, sleep-mode, GPIO-mode, wakeup, and power-disconnect selections used by Nomadik pin configuration bindings.

## Important APIs, Types, and Functions

The header exports 21 numeric constants. Active-state input constants are `INPUT_NOPULL`, `INPUT_PULLUP`, and `INPUT_PULLDOWN`. Output constants are `OUTPUT_LOW`, `OUTPUT_HIGH`, and `DIR_OUTPUT`. Sleep-mode constants include `SLPM_DISABLED`, `SLPM_ENABLED`, `SLPM_INPUT_*`, `SLPM_DIR_INPUT`, `SLPM_OUTPUT_*`, `SLPM_DIR_OUTPUT`, `SLPM_WAKEUP_*`, and `SLPM_PDIS_*`. `GPIOMODE_DISABLED` and `GPIOMODE_ENABLED` select whether a pin is exposed as GPIO.

## Control Flow

There is no executable flow. DTS source includes the header, the preprocessor substitutes small integers, and the Nomadik pinctrl driver interprets those integers when parsing pin configuration properties.

## State and Persistence Behavior

The header has no mutable state or persistence. Values are persisted only indirectly in compiled device trees. Runtime pin state belongs to the pinctrl driver and hardware registers after the kernel applies active or sleep states.

## Dependencies and Integration Points

There are no C includes or helper macros. Integration is with Nomadik DTS files and the corresponding pinctrl binding parser. Because the values are intentionally small and reused across independent property domains, the meaning depends on the property in which a constant appears.

## Risks and Edge Cases

Several domains reuse the same numeric values with different meanings, for example `0` can mean no pull, output low, sleep disabled, wakeup disabled, GPIO mode disabled, or sleep power-disconnect disabled. This is safe in the correct property but dangerous if constants are moved between properties during DTS edits. The file lacks include guards, so duplicate inclusion is harmless for identical macros but leaves less protection against accidental redefinition by other headers.

## Test Signals

Test signals include DTS compilation for boards that include Nomadik pin states, binding validation for accepted property values, runtime pinctrl debugfs inspection of active and sleep states, suspend/resume tests for `SLPM_*` settings, and wakeup tests for pins using `SLPM_WAKEUP_ENABLE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/nomadik.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/omap.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/omap.h

## Purpose

`omap.h` defines common OMAP pinctrl binding constants and address helper macros. It gives DTS files symbolic mux modes, active/off-state pin configuration bits, SoC-specific padconf offset helpers, and a few common UART RX pad offsets.

## Important APIs, Types, and Functions

The API surface includes `MUX_MODE0` through `MUX_MODE7`, active bit flags such as `PULL_ENA`, `PULL_UP`, `ALTELECTRICALSEL`, and `INPUT_EN`, and off-mode/wakeup flags such as `OFF_EN`, `OFFOUT_EN`, `OFFOUT_VAL`, `OFF_PULL_EN`, `OFF_PULL_UP`, `WAKEUP_EN`, and `WAKEUP_EVENT`. Convenience composites include `PIN_OUTPUT`, `PIN_OUTPUT_PULLUP`, `PIN_OUTPUT_PULLDOWN`, `PIN_INPUT`, `PIN_INPUT_PULLUP`, `PIN_INPUT_PULLDOWN`, and `PIN_OFF_*`.

Address helpers include `OMAP_IOPAD_OFFSET(pa, offset)`, SoC wrappers such as `OMAP2420_CORE_IOPAD`, `OMAP3_CORE1_IOPAD`, `OMAP3_WKUP_IOPAD`, `DM814X_IOPAD`, `AM33XX_IOPAD`, and `AM33XX_PADCONF`, plus `OMAP_PADCONF_OFFSET()`, `OMAP4_IOPAD()`, and `OMAP5_IOPAD()`. `OMAP3_UART*_RX` and `OMAP4_UART*_RX` define commonly used pad offsets.

## Control Flow

No runtime control flow is present. The unusual helper form intentionally expands to multiple device-tree cells, for example an offset expression followed by one or more value cells. DTS compilation resolves the arithmetic before the OMAP pinctrl driver receives the cells.

## State and Persistence Behavior

State exists only in compiled DTS pinctrl states and in hardware padconf registers after the kernel applies them. Off-mode bits influence low-power behavior, but this header does not itself store or restore state.

## Dependencies and Integration Points

The file is standalone. It integrates with OMAP, AM33xx, DM814x/DM816x, OMAP4, and OMAP5 pinctrl bindings whose `pinctrl-single,pins` or related properties accept offset/config pairs. Board DTS files rely on the helper base offsets matching each SoC's padconf register layout.

## Risks and Edge Cases

The address helpers mask physical addresses with `0xffff` and subtract SoC-specific base offsets; using the wrong helper can produce a plausible but incorrect offset. `AM33XX_IOPAD()` expands an extra `(0)` cell while `AM33XX_PADCONF()` expands separate config and mux cells, so property formats must match the binding. Wakeup and off-mode bits can change suspend behavior; wrong use can cause excessive power draw, broken wake sources, or pins driving against external circuitry.

## Test Signals

Validation should include DTS compilation across representative OMAP generations, `dtbs_check` for cell counts, boot-time pinctrl debugfs state, padconf register inspection when available, UART RX smoke tests for the common offsets, and suspend/resume tests for off-mode and wakeup definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/omap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pads-imx8dxl.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pads-imx8dxl.h

## Purpose

`pads-imx8dxl.h` is the NXP i.MX8DXL System Controller firmware pinctrl binding catalog. It assigns stable pad IDs and mux alternatives so DTS files can request pad ownership/function through the i.MX SCU pinctrl interface.

## Important APIs, Types, and Functions

The file exports 626 definitions: 136 numeric pad IDs and 489 pad/function/mux tuples, plus the include guard. The first section maps symbols such as `IMX8DXL_EMMC0_CLK`, `IMX8DXL_ENET0_RGMII_TXC`, `IMX8DXL_SPI3_SCK`, and `IMX8DXL_SCU_BOOT_MODE*` to pad IDs. The second section maps functions using `IMX8DXL_<pad>_<domain>_<signal>  IMX8DXL_<pad>  <mux>`. Domains include HSIO, ADMA, CONN, LSIO, SCU, MIPI, and audio/display-related blocks. A final set of `_PAD` definitions covers companion-control pads such as voltage/compensation controls.

## Control Flow

There is no executable control flow. DTS macros expand to pin ID and mux selector cells. The i.MX SCU pinctrl path passes those values to firmware/hardware to select pad routing, typically when a device's default pinctrl state is applied.

## State and Persistence Behavior

The header is stateless. Selected pin states are stored in device tree and become runtime pad ownership/mux state in the SCU-managed pin controller. The header does not describe drive strength, pull, or persistence policy by itself; those are additional binding cells or firmware-controlled pad settings.

## Dependencies and Integration Points

The header is standalone and is included by i.MX8DXL DTS/DTSI files. It integrates with the NXP SCU pinctrl binding, SCFW resource ownership, and peripheral nodes for eMMC/USDHC, Ethernet, USB, SPI, UART, I2C, MIPI, QSPI, audio clocks, and SCU boot/GPIO pins.

## Risks and Edge Cases

i.MX8DXL uses SCU-managed resources, so a valid macro may still fail if firmware ownership or power-domain setup does not permit the pad/function. Many pads have GPIO alternatives in multiple LSIO banks and mux values 4 or 5; selecting the wrong bank can compile but expose the wrong GPIO number. Companion-control pads ending in `_PAD` are not normal signal muxes and should not be treated like peripheral data pins. Board-level voltage compatibility is important for the `COMP_CTL_GPIO_1V8_3V3_*` pads.

## Test Signals

Good tests are DTS compilation for i.MX8DXL boards, pinctrl binding validation, SCU firmware boot logs for pad ownership errors, debugfs pinmux inspection, and hardware tests for eMMC, USDHC, RGMII, USB, QSPI, SPI, UART/I2C, MIPI, and GPIO fallback paths. Static checks should verify two-cell function macros reference an existing pad ID and use valid mux numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pads-imx8dxl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pads-imx8qm.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pads-imx8qm.h

## Purpose

`pads-imx8qm.h` defines the i.MX8QM pad ID and mux-option binding constants. It is used by device trees to select SCU-managed pad functions for the larger i.MX8QM family.

## Important APIs, Types, and Functions

The header exports 945 definitions: 269 numeric pad IDs and 675 pad/function/mux tuples. Numeric IDs cover SIM, M40/M41 microcontroller pins, GPT, UART, SCU/PMIC/boot pins, LVDS, MIPI DSI/CSI, HDMI/eDP, USB, QSPI, PCIe, SATA, eMMC/USDHC, ENET, ESAI/SPDIF, and many GPIO/companion-control pads. Function macros follow `IMX8QM_<pad>_<domain>_<signal>  IMX8QM_<pad>  <mux>`, with domains such as DMA, LSIO, SCU, MIPI, LVDS, DC, HDMI, HSIO, CONN, VPU, and audio.

## Control Flow

The file has no runtime control flow. The preprocessor expands selected macros into pad and mux cells, which the i.MX SCU pinctrl driver/firmware uses when applying pinctrl states for devices.

## State and Persistence Behavior

No mutable state exists in the header. Device-tree pinctrl states persist the selected constants in the DTB. Runtime state is in SCU-managed pad configuration and may be affected by firmware resource partitioning and low-power transitions.

## Dependencies and Integration Points

The header has no includes. Integration points include i.MX8QM board DTSI files, NXP SCU pinctrl bindings, SCFW resource management, and consumer devices for display, media, storage, network, serial, and control interfaces. The two trailing `_PAD` entries for ENET companion controls expose non-signal pad controls.

## Risks and Edge Cases

The catalog is large and copy/paste-sensitive. Similar pad names exist across M40, M41, LVDS0/1, MIPI DSI0/1, CSI0/1, and ENET instances. A function macro can compile while selecting a different instance or mux mode than the board wiring. The LSIO GPIO alternative often uses mux 3, while other i.MX8 derivatives use different GPIO mux slots; blindly porting pinctrl states from QXP/DXL is risky. SCFW ownership and power domains can reject otherwise valid DTS selections.

## Test Signals

Validation should compile representative i.MX8QM DTBs, run `dtbs_check`, inspect boot logs for SCU pinctrl errors, compare pinctrl debugfs with expected pad names, and smoke test each enabled peripheral. Static consistency checks should verify all function macros reference known pad IDs, mux values match NXP tables, and companion-control `_PAD` definitions are not used as ordinary data lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pads-imx8qm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pads-imx8qxp.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pads-imx8qxp.h

## Purpose

`pads-imx8qxp.h` provides i.MX8QXP pad ID and mux constants for device-tree pinctrl states. It maps physical pads to SCU pin identifiers and names each legal alternate function.

## Important APIs, Types, and Functions

The header exports 736 definitions: 174 numeric pad IDs and 561 function tuples. Pad IDs cover PCIe, USB SS3, eMMC/USDHC, ENET, ESAI/SPDIF, SPI, UART, MIPI DSI/CSI, SCU pins, QSPI, ADC, JTAG, and companion-control pads. Function macros use the form `IMX8QXP_<pad>_<domain>_<signal>  IMX8QXP_<pad>  <mux>`, with domains including HSIO, ADMA, CONN, LSIO, SCU, MIPI, DMA-like audio/display blocks, and QSPI/KPP alternatives.

## Control Flow

There is no executable flow. The header provides constants that are resolved during DTS preprocessing. At runtime, the i.MX SCU pinctrl implementation applies the pad/mux pairs when a device selects a pinctrl state.

## State and Persistence Behavior

The header is stateless. Persistence is limited to compiled DTBs and source DTS files. Runtime pad state is held by the SCU pinctrl/firmware path and hardware registers, not by this file.

## Dependencies and Integration Points

The file is standalone. It integrates with i.MX8QXP DTS files, SCFW-managed pinctrl, and drivers for storage, Ethernet, display/camera, serial buses, USB, QSPI, audio, keypad, and GPIO. It shares many concepts and names with `pads-imx8dxl.h`, but the pad numbering and available functions are not identical.

## Risks and Edge Cases

Porting between QXP, DXL, and QM by name alone can misroute pins because numeric IDs and mux alternatives differ. Some QSPI0B pads expose QSPI1A and keypad alternatives in addition to GPIO, making instance confusion easy. GPIO fallback generally uses LSIO mux 4 in this file, unlike i.MX8QM's common mux 3. Valid macros still depend on firmware resource ownership and board-level voltage/pad constraints.

## Test Signals

Checks include DTS compilation for i.MX8QXP boards, `dtbs_check`, boot-log review for SCU pinctrl failures, pinctrl debugfs inspection, and hardware validation for eMMC/USDHC, ENET, USB, QSPI, MIPI, audio, UART/SPI/I2C, keypad, and GPIO modes. Static tests should ensure every function tuple references a defined pad ID and no board DTS uses a DXL/QM-only macro.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pads-imx8qxp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-cv1800b.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-cv1800b.h

## Purpose

`pinctrl-cv1800b.h` defines Sophgo CV1800B package pin identifiers for device-tree pinmux entries. It is generated from vendor pinout data and is paired with the shared CV18xx `PINMUX()` encoding.

## Important APIs, Types, and Functions

The file includes `dt-bindings/pinctrl/pinctrl-cv18xx.h` and exports 49 pin constants such as `PIN_SD0_*`, `PIN_UART0_*`, `PIN_SPINOR_*`, `PIN_IIC0_*`, `PIN_SD1_*`, `PIN_ETH_*`, `PIN_MIPIRX*`, and audio/ADC/power pins. Values are numeric package pin IDs with gaps, ranging from `PIN_AUD_AOUTR` at 1 to `PIN_AUD_AINL_MIC` at 67.

## Control Flow

No executable flow is present. DTS uses `PINMUX(PIN_*, mux)` or `PINMUX2()` from `pinctrl-cv18xx.h`; this file supplies the first `pin` argument.

## State and Persistence Behavior

The header is stateless. Pin selections are stored in DTS/DTB and are applied by the CV18xx/Sophgo pinctrl driver during boot or state changes.

## Dependencies and Integration Points

The required dependency is `pinctrl-cv18xx.h`, which defines the 32-bit packed encoding. Integration points are CV1800B DTS files, the Sophgo pinctrl binding, and the pinctrl driver's package-specific pin tables.

## Risks and Edge Cases

The numeric IDs are package-specific and sparse. Reusing CV1812H, SG2000, or SG2002 pin names without checking numeric values can select the wrong physical ball. Because the header only names pins, it does not constrain mux values; unsupported mux selections can still compile if written with `PINMUX()`.

## Test Signals

Use DTS compilation, `dtbs_check`, static comparison against vendor pinout tables, and runtime pinctrl debugfs. Hardware smoke tests should cover SD0/SD1, SPI NOR, UART0, I2C0, Ethernet, MIPI RX, ADC, and audio pins present on the target board.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-cv1800b.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-cv1812h.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-cv1812h.h

## Purpose

`pinctrl-cv1812h.h` defines Sophgo CV1812H package pin identifiers for device-tree pinmux entries. It uses package row/column notation so board DTS files can refer to meaningful pin names while still passing compact integer IDs to the pinctrl binding.

## Important APIs, Types, and Functions

The file includes `pinctrl-cv18xx.h`, defines `PINPOS(row, col)` as `((((row) - 'A' + 1) << 8) + ((col) - 1))`, and exports 111 package pin constants. Named pins cover MIPI TX/RX, VIVO camera/display data, USB ID/VBUS, Ethernet pairs, camera clocks/reset/powerdown, ADC, audio, SD0/SD1, UART0/2, I2C/IIC, JTAG, power sequencing, eMMC, clock, reset, GPIO_ZQ, and crystal input.

## Control Flow

There is no runtime control flow. `PINPOS()` is evaluated by the preprocessor/compiler in DTS include processing, then the resulting pin ID is packed by `PINMUX()` or `PINMUX2()` and interpreted by the Sophgo pinctrl driver.

## State and Persistence Behavior

The header holds no state. Compiled DTBs preserve selected row/column-derived pin IDs. Hardware state is maintained by the pinctrl driver and registers after mux application.

## Dependencies and Integration Points

The direct dependency is `pinctrl-cv18xx.h` for shared mux packing. Integration points are CV1812H DTS files and pinctrl driver tables that must use the same row/column encoding. The file is structurally identical in content to `pinctrl-sg2000.h`, reflecting shared package layout.

## Risks and Edge Cases

`PINPOS()` assumes uppercase row letters and one-based columns. Mistyped rows or columns still produce deterministic integers but not valid package pins. Because the file defines package pins, not function enums, invalid mux alternatives remain possible in DTS. Similar names across CV1812H, SG2000, SG2002, and CV1800B hide different encoding schemes, so cross-SoC copy/paste is risky.

## Test Signals

Tests should include DTS compilation, binding validation, static comparison of row/column values against package data, pinctrl debugfs inspection, and hardware checks for SD/eMMC, MIPI, Ethernet, USB, UART/I2C, camera/VIVO, audio, and power-control pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-cv1812h.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-cv18xx.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-cv18xx.h

## Purpose

`pinctrl-cv18xx.h` defines the shared Sophgo CV18xx-family pinmux packing macros used by CV1800B, CV1812H, SG2000, and SG2002 package pin headers.

## Important APIs, Types, and Functions

The key constants are `PIN_MUX_INVALD` with value `0xff`, `PINMUX2(pin, mux, mux2)`, and `PINMUX(pin, mux)`. `PINMUX2()` packs a 16-bit pin ID, an 8-bit primary mux in bits 16-23, and an 8-bit secondary mux in bits 24-31. `PINMUX()` sets the secondary mux byte to `PIN_MUX_INVALD`.

## Control Flow

There is no runtime control flow. Device-tree preprocessing expands these macros into a single 32-bit integer cell. The Sophgo pinctrl driver later unpacks the pin, primary mux, and optional secondary mux fields.

## State and Persistence Behavior

The header is stateless. The packed values persist only as device-tree cells. Runtime state is the hardware mux configuration applied by the pinctrl driver.

## Dependencies and Integration Points

The file is standalone and is included by SoC/package-specific Sophgo pin headers. It must agree with the binding schema and the driver's bit-field decoder. The misspelled exported name `PIN_MUX_INVALD` is part of the binding ABI and should not be silently renamed without compatibility handling.

## Risks and Edge Cases

Arguments are masked, so oversized pin or mux values are truncated rather than rejected by the macro. That can hide DTS mistakes until runtime. The invalid secondary mux sentinel is `0xff`; if hardware ever has a valid secondary mux value of 255, the encoding cannot distinguish it. Consumers must treat the misspelled macro as intentional ABI.

## Test Signals

Static tests should evaluate representative `PINMUX()` and `PINMUX2()` values and verify driver unpacking. DTS compilation should cover each package header using these macros, and `dtbs_check` should catch invalid property shapes even though value-range mistakes may require driver-side validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-cv18xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-sg2000.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-sg2000.h

## Purpose

`pinctrl-sg2000.h` defines Sophgo SG2000 package pin identifiers for use with the shared CV18xx pinmux encoding. It maps named board-visible pins to row/column-derived integer IDs.

## Important APIs, Types, and Functions

The header includes `pinctrl-cv18xx.h`, defines the same `PINPOS(row, col)` helper used by CV1812H, and exports 111 package pin constants. Pins cover MIPI TX/RX, VIVO data, USB, Ethernet, camera controls, audio, SD0/SD1, UART0/2, JTAG, power sequencing, eMMC, IIC/I2C, clock, reset, GPIO_ZQ, and crystal input.

## Control Flow

No executable logic exists. `PINPOS()` produces a package pin ID at preprocessing time, and DTS code usually feeds that value into `PINMUX()` or `PINMUX2()`.

## State and Persistence Behavior

The header is stateless. Selected pinmux entries persist in DTB files and become hardware state when the Sophgo pinctrl driver applies them.

## Dependencies and Integration Points

The direct dependency is `pinctrl-cv18xx.h`. Integration points are SG2000 DTS files, the Sophgo binding, and driver tables that decode row/column pin IDs. The file matches `pinctrl-cv1812h.h` closely, suggesting shared package layout or compatible pin naming.

## Risks and Edge Cases

The row/column formula accepts invalid-looking inputs at preprocessing time if they are syntactically valid character constants and integers. Similar pin names across SG2000 and CV1812H can hide SoC-specific mux availability differences even when package pin IDs match. The header does not validate mux values.

## Test Signals

Run DTS compilation and `dtbs_check`, compare generated pin IDs with SG2000 package documentation, inspect pinctrl debugfs on boot, and test board peripherals using SD/eMMC, MIPI, Ethernet, USB, UART/I2C, camera/VIVO, audio, and power-control pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-sg2000.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-sg2002.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-sg2002.h

## Purpose

`pinctrl-sg2002.h` defines Sophgo SG2002 package pin identifiers for device-tree pinmux entries using the shared CV18xx encoding.

## Important APIs, Types, and Functions

The file includes `pinctrl-cv18xx.h` and exports 65 numeric pin constants. Named pins cover audio input/output, SD0/SD1, speaker enable, UART0, eMMC, JTAG CPU, IIC0, auxiliary and GPIO_ZQ pins, power sequencing/reset/wakeup/button pins, ADC, USB VBUS, Ethernet differential pins, GPIO_RTX, MIPI RX lanes, and MIPI TX lanes. Numeric values range from 2 through 88 with gaps.

## Control Flow

There is no runtime flow. DTS entries use these constants as the `pin` argument to `PINMUX()` or `PINMUX2()`, and the pinctrl driver interprets the packed value when applying states.

## State and Persistence Behavior

The header stores no mutable state. The only persistence is the selected constants in source and compiled device trees. Hardware pin state is owned by the pinctrl subsystem at runtime.

## Dependencies and Integration Points

The direct dependency is the shared CV18xx packing header. Integration points are SG2002 DTS files, binding schemas, and the Sophgo pinctrl driver's SG2002 pin tables.

## Risks and Edge Cases

SG2002 uses simple numeric IDs rather than `PINPOS()` row/column values, so copy/paste from SG2000/CV1812H can be wrong even when signal names match. The file does not restrict mux IDs; an unsupported mux value can be packed and compiled. Sparse numbering means range-only validation is insufficient.

## Test Signals

Tests should include DTS compilation, `dtbs_check`, static comparison against vendor pinout definitions, pinctrl debugfs review, and hardware smoke tests for SD/eMMC, UART0, IIC0, Ethernet, USB VBUS, MIPI, ADC, audio, and power pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-sg2002.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-sg2042.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-sg2042.h

## Purpose

`pinctrl-sg2042.h` defines Sophgo SG2042 pin IDs and a local pinmux packing macro for device-tree pinctrl states. SG2042 uses a simpler two-field packing than the CV18xx shared header.

## Important APIs, Types, and Functions

The file exports `PINMUX(pin, mux)`, which packs a 16-bit pin and an 8-bit mux in bits 16-23. It then defines 182 numeric pin IDs from `PIN_LPC_LCLK` through `PIN_BISR_BYP`. Pin groups cover LPC, PCIe reset/wakeup/clock-request, SPI flash controllers, eMMC/SDIO controls, RGMII0, PWM/fan, IIC0-3, UART0-3, SPI0-1, JTAG0-2, GPIO0-31, mode/boot selects, socket ID, PLL/XTAL clocks, reset, power button, test modes, and BISR bypass.

## Control Flow

There is no executable flow. DTS preprocessing expands `PINMUX()` into one packed cell. The SG2042 pinctrl driver decodes the pin and mux fields when applying pinctrl states.

## State and Persistence Behavior

The header is stateless. Packed pinmux values persist in DTBs and are applied to hardware registers by the pinctrl driver at runtime.

## Dependencies and Integration Points

The file is standalone and intentionally does not include `pinctrl-cv18xx.h`. Integration points are SG2042 DTS files, the SG2042 pinctrl binding, and driver decoding logic that must match the 16-bit pin plus 8-bit mux layout.

## Risks and Edge Cases

`PINMUX()` masks pin and mux arguments, so oversized values truncate silently. Boot-mode, test-mode, reset, and PLL/socket pins are sensitive; accidental muxing can affect boot straps, debug exposure, or platform stability. Dense numeric numbering makes additions easy to misorder, and names like SPI flash, SDIO/eMMC, and boot select may have board-specific electrical constraints.

## Test Signals

Validation should compile SG2042 DTBs, run binding checks, compare pin IDs against SoC documentation, inspect runtime pinctrl state, and smoke test LPC, PCIe sideband pins, SPI flash, eMMC/SDIO, RGMII, PWM/fan, IIC, UART, SPI, JTAG, and GPIO functions. Static tests should evaluate representative `PINMUX()` packing and verify driver decode agreement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-sg2042.h -->
