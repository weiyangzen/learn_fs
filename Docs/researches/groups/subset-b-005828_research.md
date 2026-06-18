# subset-b-005828 Research

Grouped source research for four MediaTek device-tree pin function binding headers. Each source file has a marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt6795-pinfunc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt6795-pinfunc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt6795-pinfunc.h` defines the device-tree pinmux constants for the MediaTek MT6795 pin controller. The file was read as a complete 908-line header. It is a data/ABI header rather than executable code: DTS and DTSI files include it so `pinmux = <...>` properties can name pins and alternate functions symbolically instead of hard-coding packed integers.

The header exports 698 `#define` macros covering GPIO pins 0 through 196 with no gaps in the pin number range. Each macro expands to `(MTK_PIN_NO(pin) | mux_function)`, where `MTK_PIN_NO()` is supplied by `dt-bindings/pinctrl/mt65xx.h` and shifts the pin number into the upper bits. GPIO mode is consistently mux function 0; alternate function selectors in this file use values 1 through 6.

## Important APIs, Types, and Functions

There are no C functions, structs, or enums. The public API is the macro namespace `PINMUX_GPIO<n>__FUNC_<name>`. Important examples include `PINMUX_GPIO0__FUNC_GPIO0`, `PINMUX_GPIO0__FUNC_IRDA_PDN`, `PINMUX_GPIO1__FUNC_SDA4`, `PINMUX_GPIO2__FUNC_SCL4`, `PINMUX_GPIO5__FUNC_PCM1_CLK`, `PINMUX_GPIO9__FUNC_USB_DRVVBUS`, and the final audio-oriented pins `PINMUX_GPIO195__FUNC_I2S0_DO` and `PINMUX_GPIO196__FUNC_I2S0_DI`.

The macro values are part of the kernel device-tree binding contract. MediaTek pinctrl code decodes the packed value through the common helpers `MTK_GET_PIN_NO(x)` and `MTK_GET_PIN_FUNC(x)`, so the exact numeric pin and mux selector must match the SoC pin table and register layout.

## Control Flow

The header has no runtime control flow. At preprocessing time, DTS sources include the header and substitute the symbolic names into numeric pinmux cells. At boot, the device-tree blob already contains those encoded integers; the pinctrl driver reads a pin number and mux selector from each cell and programs the corresponding SoC mode register.

The implicit flow is: board DTS selects one or more `PINMUX_GPIO...` macros, the preprocessor encodes them using `MTK_PIN_NO(pin) | function`, the flattened tree stores the values, and the MediaTek pinctrl driver applies those values while probing pin groups or configuring a device state.

## State and Persistence Behavior

The file holds no mutable state and persists nothing at runtime. Its definitions affect persistent ABI in a different sense: once DTS files and external device trees use these macro names and numeric encodings, changing a pin number or function selector would alter hardware configuration for existing boards. The include guard `__DTS_MT6795_PINFUNC_H` prevents duplicate preprocessing definitions.

## Dependencies and Integration Points

The only direct include is `dt-bindings/pinctrl/mt65xx.h`, which defines `MTK_PIN_NO(x) ((x) << 8)`, `MTK_GET_PIN_NO(x)`, and `MTK_GET_PIN_FUNC(x)`. This header integrates with MT6795 device-tree sources, the generic MediaTek pinctrl binding parser, and the MT6795 pin controller driver selected by `CONFIG_PINCTRL_MT6795`.

The function names expose the major SoC mux domains visible in this header: IRDA, I2S0-I2S3, PCM1, SPI, TDD and LTE modem/JTAG signals, AP/MD debug JTAG, USB VBUS drive, SIM1/SIM2, MSDC0-MSDC3, DPI/display, PWRAP, UART, I2C `SDA`/`SCL`, and baseband `BPI` signals. Those names must stay aligned with the SoC datasheet and with any driver pin descriptors that validate pin/function combinations.

## Risks and Edge Cases

The main risk is ABI drift. A wrong mux selector can still compile cleanly but configure a different electrical function at runtime, causing silent board failures such as dead UART, broken storage, wrong I2C bus ownership, or exposed debug/JTAG pins. Because function selectors are sparse for many pins, adding a missing alternate function requires preserving existing selector numbers rather than renumbering a pin block.

The namespace differs from some older MediaTek headers by using `PINMUX_GPIO...` rather than a SoC-prefixed macro name. That is valid for this generation but increases collision risk if multiple pinfunc headers are included in a single preprocessed DTS translation unit. Another review point is license compatibility: this file uses dual `(GPL-2.0-only OR BSD-2-Clause)` SPDX text, unlike several neighboring MediaTek pinfunc headers that are GPL-only.

## Test Signals

Useful validation is mostly compile-time and board-level. `dtbs_check`/DTC preprocessing should catch missing macro names and include guard problems. Grep or script checks can confirm every macro uses `MTK_PIN_NO(n)` matching the GPIO number in its name, that GPIO mode uses selector 0, and that selectors remain within the 4-bit function field decoded by `MTK_GET_PIN_FUNC(x)`. Runtime signals are successful probe and operation of MT6795 boards using UART, storage, I2C, display/audio, modem, and USB pin states without pinctrl warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt6795-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt6797-pinfunc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt6797-pinfunc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt6797-pinfunc.h` defines MediaTek MT6797 pin function constants for device-tree pinmux properties. The file was read as a complete 1368-line header. It supplies symbolic names for the SoC's GPIO and alternate-function matrix so board DTS files do not encode raw pin/function integers by hand.

The header exports 1091 `#define` macros for GPIO pins 0 through 261, with all pin numbers present. Every macro expands to `(MTK_PIN_NO(pin) | function)`. GPIO mode is function 0 on each pin, and alternate selectors use the full range 1 through 7.

## Important APIs, Types, and Functions

There are no executable functions or declared types. The exported API is the macro namespace `MT6797_GPIO<n>__FUNC_<name>`. The early pins map CSI camera lanes, for example `MT6797_GPIO0__FUNC_CSI0A_L0P_T0A` through CSI0/CSI1/CSI2 lane macros. Later pins cover SPI, PWM, SCP/CONN/C2K debug signals, MIPI, I2S, PCM, DPI, MSDC, UART, I2C, modem, LTE JTAG, antenna, and diagnostic functions.

Several pins expose the maximum eight alternatives: for example GPIO28 has GPIO, `SPI5_CLK_A`, two MIPI functions, SCP/CONN JTAG, PWM, and C2K debug output selectors. The high-numbered pins 260 and 261 end with LTE/DFD/ANC/SCP/C2K JTAG and trace-related functions.

## Control Flow

The header has no runtime branches or call graph. Its practical flow is preprocessing and consumption by pinctrl: a DTS pin state references `MT6797_GPIO...` macros, the preprocessor emits packed integers, and the MediaTek pinctrl driver decodes those integers into pin number and mux selector when applying a pin state.

Because this is a binding header, correctness depends on the names and numeric selectors matching the separate MT6797 driver pin descriptor/register tables. The file itself does not validate combinations or enforce group membership.

## State and Persistence Behavior

No runtime state is stored. The only state-like behavior is the public ABI represented by macro names and values. Device trees built from this header carry the encoded values into the DTB, so any macro value change can alter boot-time hardware muxing for existing device trees. The include guard `__DTS_MT6797_PINFUNC_H` prevents duplicate definitions.

## Dependencies and Integration Points

The direct dependency is `dt-bindings/pinctrl/mt65xx.h` for `MTK_PIN_NO()` and decode helpers. The integration points are MT6797 board DTS/DTSI files, the MediaTek pinctrl binding, and the `CONFIG_PINCTRL_MT6797` driver path, including `drivers/pinctrl/mediatek/pinctrl-mt6797.c` and the associated pin descriptor header.

The function matrix is especially broad for camera and modem/debug use. Top-level function families visible in the macro names include CSI, C2K, DBG, CONN, MD/MD1, PWM, BPI, I2S0-I2S2, MIPI, PCM0/PCM1, DPI, SPI1/SPI2/SPI4/SPI5, SCP, LTE, UDI, TP, IRTX, MSDC0/MSDC1, UART, I2C, SIM, and antenna selectors. These names are an integration contract with both board authors and subsystem maintainers.

## Risks and Edge Cases

The major risk is a selector mismatch that compiles and boots but routes pins to the wrong peripheral. MT6797 has many debug, modem, connectivity, and camera lane alternatives; confusing similarly named signals such as SCP versus CONN JTAG or C2K debug can break low-level diagnostics or expose unintended hardware functions. Because selectors reach 7, any shared decoder must preserve at least the lower four function bits, as `MTK_GET_PIN_FUNC(x)` does.

The header uses a SoC-prefixed namespace (`MT6797_GPIO...`) rather than the newer generic `PINMUX_GPIO...` pattern. That helps avoid cross-SoC macro collisions but means board files cannot mechanically swap names between MT6797 and newer MediaTek pinfunc headers without translation. The GPL-2.0-only SPDX line also matters when comparing with dual-licensed binding headers.

## Test Signals

Compile-time tests should include all MT6797 DTS targets that include this header and should fail on missing or duplicate macro names. A simple static check can verify that each macro's numeric `MTK_PIN_NO()` argument matches the GPIO number embedded in the macro name and that every function selector stays in the expected 0-7 range. Runtime board signals include pinctrl probe without invalid function warnings, working CSI camera lanes, SPI/I2C/UART, MSDC storage, display/audio pins, modem/connectivity pins, and debug mux states on hardware that exposes them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt6797-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt7623-pinfunc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt7623-pinfunc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt7623-pinfunc.h` defines pinmux constants for the MediaTek MT7623 pin controller. The file was read as a complete 651-line header. It gives DTS authors symbolic constants for pin/function selections across the MT7623 router/networking SoC package.

The header exports 491 `#define` macros. Unlike the contiguous MT6795/MT6797/MT8135 headers in this group, MT7623 is sparse: the macros cover 153 unique pin numbers between 0 and 278, leaving 126 numeric gaps in that range. This reflects the SoC/package pin numbering used by the corresponding driver rather than an error in this header. Each value is encoded as `(MTK_PIN_NO(pin) | function)`, with GPIO selector 0 and alternate selector values 1 through 6.

## Important APIs, Types, and Functions

There are no C functions or types. The exported API is the macro namespace `MT7623_PIN_<n>_<ball_or_signal>_FUNC_<function>`, for example `MT7623_PIN_0_PWRAP_SPI0_MI_FUNC_PWRAP_SPIDO`, `MT7623_PIN_7_SPI1_CSN_FUNC_SPI1_CS`, `MT7623_PIN_18_PCM_CLK_FUNC_PCM_CLK0`, `MT7623_PIN_75_SDA0_FUNC_SDA0`, `MT7623_PIN_111_MSDC0_DAT7_FUNC_MSDC0_DAT7`, `MT7623_PIN_262_G2_TXD0_FUNC_G2_TXD0`, `MT7623_PIN_275_G2_MDC_FUNC_MDC`, and `MT7623_PIN_278_JTAG_RESET_FUNC_JTAG_RESET`.

The naming carries both a pin number and a primary pad/signal label before `_FUNC_`, which is useful for a sparse SoC map. The most common families in the file are connectivity/debug, PCM/audio, AP/MD debug, Ethernet G1/G2, MSDC, PWRAP, SPI, I2C, UART, USB OTG, PCIe, HDMI, NAND, MIPI, and JTAG.

## Control Flow

The header has no executable flow. DTS preprocessing turns each selected macro into a packed pinmux integer. The MT7623 pinctrl driver then decodes the integer and programs mode registers based on its `mt7623_pins`, function, and group tables.

The MT7623 driver has explicit pin/function group arrays for many peripherals, including Ethernet switch, EPHY, external SDIO, HDMI, I2C alternatives, I2S alternatives, MDC/MDIO, multiple MSDC ports, NAND, USB OTG ID/VBUS, PCIe reset/wake/clock request, and UART/SPI paths. This header's macro values must match those group function selectors.

## State and Persistence Behavior

No mutable kernel state is declared here. The file is a stable binding input: once a DTS references a macro, the resulting DTB persists the encoded pin/function selection. The include guard `__DTS_MT7623_PINFUNC_H` protects the macro definitions during preprocessing.

The sparse numbering is a state-contract detail. Consumers must not assume `pin_max + 1` macros or contiguous GPIO coverage from this header; they must rely on the pinctrl driver's advertised pin descriptors and groups.

## Dependencies and Integration Points

The direct include is `dt-bindings/pinctrl/mt65xx.h`, which provides the common MediaTek encoding and decode helpers. The main integration point is `drivers/pinctrl/mediatek/pinctrl-mt7623.c`, which defines the MT7623 register ranges, `mt7623_pins` descriptors, group pins, group functions, and `mt7623_reg_cals`.

Hardware integration surfaces are broad but skew toward networking and board I/O: PWRAP, SPI0-SPI2, keypad columns, UARTs, PCM/I2S/MRG audio, connectivity DSP/JTAG, external frame sync, I2C, MSDC0-MSDC3, NAND, HDMI and MIPI display, USB OTG ID/VBUS, PCIe, Ethernet G1/G2, MDC/MDIO, EPHY/ESW reset and interrupt, and JTAG reset.

## Risks and Edge Cases

The sparse pin map is the most important edge case. A mechanical checker that expects all numbers 0 through 278 to exist would report false positives; a better checker validates only macro-to-`MTK_PIN_NO()` consistency and cross-references the driver's descriptor table. Conversely, adding a missing-looking pin without matching driver support could create an unusable binding name.

Another risk is mismatch between this dt-binding header and the MT7623 driver's group arrays. For example, some driver group arrays use higher function values for alternate/reversed PCIe functions that are not represented by this header's 0-6 selectors, so board authors should use only published binding macros unless the driver binding is extended deliberately. Selector mistakes can disable boot-critical storage, Ethernet, or serial console pins while still passing compilation.

## Test Signals

Static tests should confirm that each macro's numeric `MTK_PIN_NO()` matches the pin number in `MT7623_PIN_<n>_...`, that GPIO alternatives use selector 0, and that no selector exceeds the shared 4-bit function field. DTS/DTC builds for MT7623 boards should catch missing names. Runtime signals include working serial console, PWRAP, MMC/SD, NAND where used, Ethernet G1/G2 and MDIO/MDC, USB/PCIe, I2C/SPI, HDMI/display, and absence of MediaTek pinctrl warnings while applying board pin states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt7623-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt8135-pinfunc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt8135-pinfunc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt8135-pinfunc.h` defines MediaTek MT8135 pin function constants for device-tree pinmux properties. The file was read as a complete 1294-line header. It maps every SoC GPIO pad to the numeric mux values accepted by the MT8135 pinctrl driver.

The header exports 1079 `#define` macros for GPIO pins 0 through 202, with no gaps in the pin number range. Values are encoded as `(MTK_PIN_NO(pin) | function)`. GPIO mode is selector 0 where present, and alternate selectors use 1 through 7. A few pins have only GPIO definitions, while many early and midrange pins expose six to eight total mux choices.

## Important APIs, Types, and Functions

There are no functions, structs, or enums. The public interface is the macro namespace `MT8135_PIN_<n>_<pad>__FUNC_<function>`. Examples include `MT8135_PIN_0_MSDC0_DAT7__FUNC_MSDC0_DAT7`, `MT8135_PIN_0_MSDC0_DAT7__FUNC_EINT49`, `MT8135_PIN_4_MSDC0_CMD__FUNC_USB_TEST_IO_0`, `MT8135_PIN_5_MSDC0_CLK__FUNC_MSDC0_CLK`, and high-numbered MSDC3/I2C/PWM/clock macros such as `MT8135_PIN_202_MSDC3_DAT0__FUNC_SCL3`.

The file's function families include MSDC0-MSDC4, EINT lines, I2S input/output, DAC, PCM1, SPI1, NAND-style signals, USB test/drive signals, display/DPI, PWM, clock monitor/output, DSP/test bus signals, touch/keypad, I2C, UART, HDMI/CEC-adjacent signals, and multimedia debug/test functions.

## Control Flow

There is no runtime control flow inside the header. Device-tree preprocessing substitutes macro names with encoded pin/function integers. The MT8135 pinctrl driver decodes those values and uses its descriptor/register data to set the hardware mux mode for each pin in a selected state.

The compile-time flow is strict: macros must be visible before DTS pin state definitions are preprocessed, and the packed values must stay compatible with the common MediaTek decode helpers. The runtime flow is delegated entirely to the pinctrl subsystem.

## State and Persistence Behavior

The header declares no mutable state and performs no persistence. It contributes to the persistent board hardware description because generated DTBs contain the encoded pinmux values. Renaming macros breaks source-level DTS compatibility; changing numeric encodings can silently break existing DTBs rebuilt from the same source.

The include guard `__DTS_MT8135_PINFUNC_H` prevents repeated definition. The header carries GPL-2.0-only licensing and MediaTek copyright/authorship metadata from 2014.

## Dependencies and Integration Points

The direct dependency is `dt-bindings/pinctrl/mt65xx.h`, especially `MTK_PIN_NO()`, `MTK_GET_PIN_NO()`, and `MTK_GET_PIN_FUNC()`. The runtime integration is through the MT8135 pinctrl driver selected by `CONFIG_PINCTRL_MT8135`, including `drivers/pinctrl/mediatek/pinctrl-mt8135.c` and `pinctrl-mtk-mt8135.h`, where the driver maintains pin descriptors and register fields.

The header also integrates with ARM MediaTek board DTS files that describe MT8135 pin states. Its macro names include both pad identity and mux function, which lets DTS reviewers see whether a pin state selects a primary peripheral path, an interrupt line, or a test/debug function.

## Risks and Edge Cases

The largest risk is silent hardware misconfiguration from a wrong selector. MT8135 pins often have dense 0-7 mux sets; shifting a selector by one can change storage, external interrupt, audio, display, or test-bus behavior without a compiler error. Test and USB diagnostic functions are interleaved with normal peripheral functions, so board pin states should avoid accidentally selecting factory/test modes.

A small number of pins have only one macro in this header, which is expected for pads with only GPIO exposure in this binding. Reviewers should avoid "filling in" apparent gaps unless the SoC datasheet and driver register tables are updated together. The header's SoC-prefixed namespace reduces cross-header collision risk but differs from newer generic `PINMUX_GPIO...` style headers.

## Test Signals

Compile-time coverage should include MT8135 DTS/DTSI builds and DTC preprocessing with this header. Static checks can verify macro name pin numbers against `MTK_PIN_NO()` arguments, selector bounds within the low nibble decoded by `MTK_GET_PIN_FUNC()`, and stable include guards. Hardware or integration signals include successful pinctrl probe, working MSDC storage, I2C/SPI/UART, EINT wake/interrupt lines, audio I2S/PCM/DAC, display/DPI, USB-related pins, and lack of unexpected test/debug muxing in board pin states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt8135-pinfunc.h -->
