# subset-b-000635

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx6dl-pinfunc.h -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx6dl-pinfunc.h

## Purpose
`imx6dl-pinfunc.h` is the device-tree pin-function binding table for the NXP/Freescale i.MX6 DualLite/Solo IOMUX controller. It gives DTS authors symbolic names for pad mux alternatives so board files can populate `fsl,pins` arrays with readable tokens instead of raw register offsets.

Each macro expands to the five-cell tuple documented at the top of the file: `<mux_reg conf_reg input_reg mux_mode input_val>`. The Linux i.MX pinctrl binding consumes those cells, while each board DTS appends the sixth pad-control word that encodes electrical configuration such as pull, keeper, drive strength, hysteresis, and open-drain behavior.

## Important APIs, Types, And Functions
There are no C functions, structs, enums, or runtime APIs. The exported interface is a preprocessor namespace of 1,074 `#define` macros across 197 physical pad names.

The macro naming convention is the important contract: `MX6QDL_PAD_<PAD_NAME>__<FUNCTION_NAME>`. The `MX6QDL` prefix is shared with i.MX6Q family DTS content, but this file carries the i.MX6DL/Solo register map. The pad name identifies the external ball or pad group, and the function name identifies the mux target selected by `mux_mode` plus optional daisy-chain `input_reg/input_val`.

Major covered signal families include IPU1 display and CSI, EIM, EPDC, ENET/RGMII, NAND, SD1 through SD4, ECSPI1 through ECSPI4, I2C1 through I2C4, UART1 through UART5, ESAI/AUD, KEY matrix, PWM/GPT/EPIT, USB, HDMI DDC/CEC, SPDIF, FLEXCAN, SDMA events, GPIO banks 1 through 7, boot strap `SRC_BOOT_CFG*`, trace/JTAG, and watchdog outputs. GPIO alternatives are consistently present on most pads, which makes the header the authoritative map from named pads to GPIO controller/line numbers.

## Control Flow
The file has no executable control flow. Its compile-time flow is inclusion guarded by `__DTS_IMX6DL_PINFUNC_H`, followed by a flat list of macro definitions and a closing `#endif`.

At DTS preprocessing time, a pinctrl group such as `MX6QDL_PAD_EIM_D21__I2C1_SCL 0x40010878` expands to the five cells from this header plus the board-supplied pad-control value. The device-tree compiler emits those cells into the DTB, and the kernel `pinctrl-imx` driver later interprets the tuple by programming IOMUXC mux, pad-control, and select-input registers.

## State, Persistence, And Dependencies
The header itself stores no mutable state and persists no data. Its values describe SoC hardware state that will be programmed at boot or when pinctrl states are selected.

It depends on the i.MX pinctrl device-tree binding contract and the SoC-specific IOMUXC register layout. Nonzero `input_reg` values describe daisy-chain select-input registers for shared peripheral inputs, while `input_reg` equal to `0x000` means no select-input programming is needed for that function. The file must remain synchronized with the i.MX6DL/Solo reference manual and the Linux `pinctrl-imx` tuple parser.

## Integration Points
`imx6dl.dtsi` includes this header, and i.MX6DL/Solo board DTS files consume the exported macros inside pinctrl groups. Examples in this source tree include `imx6dl-alti6p.dts`, which uses the definitions for audio clocks/data, CAN, SPI, ENET, HDMI, I2C, UART, USB, and SD pin groups.

The file is also coupled to the sibling `imx6q-pinfunc.h` because both expose the `MX6QDL_PAD_*` namespace. The names intentionally let common `imx6qdl-*.dtsi` board fragments refer to the same logical pads across Quad/DualLite variants, while the included SoC dtsi chooses the correct register offsets and select-input values.

## Risks
Because each entry is raw hardware data, a single wrong cell can silently route a signal to the wrong mux mode, write an invalid IOMUXC offset, or select the wrong daisy-chain input. These faults often show up as board-specific peripheral failures rather than compile errors.

The shared `MX6QDL` namespace is useful but risky: copying values between the i.MX6Q and i.MX6DL headers is unsafe because many equivalent names have different register offsets and select-input values. DTS include ordering must ensure the SoC-appropriate header is visible.

Several pads expose boot strap, watchdog reset, USB ID/over-current/power, and clock-output alternatives. Misusing those macros in board pinctrl can affect boot mode sampling, reset behavior, clocking, or external power switching. GPIO alternatives also require matching GPIO controller/line references in board nodes; mismatches can compile but behave incorrectly.

## Test Signals
Build all i.MX6DL/Solo DTBs that include `imx6dl.dtsi` with `make dtbs` and run `dtbs_check` for pinctrl binding validation. Useful source-level checks include verifying every macro has exactly five numeric cells, no duplicate macro names, legal mux modes for the SoC, and register offsets/select-input values matching the reference manual.

Runtime signals are board-specific: boot logs should show successful pinctrl state application, affected peripherals should probe, and hardware smoke tests should cover ENET/RGMII link, I2C scans, SPI transfers, UART console/flow control, SD/eMMC enumeration, USB ID/OC behavior, GPIO interrupts, display/camera pins, and wake/reset lines that use these macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx6dl-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx6q-pinfunc.h -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx6q-pinfunc.h

## Purpose
`imx6q-pinfunc.h` is the device-tree pin-function binding table for the NXP/Freescale i.MX6 Quad/Dual IOMUX controller. It maps human-readable pad/function names to the five register-selector cells consumed by the Linux i.MX pinctrl binding.

The file allows board DTS sources to express pinmux choices as symbols such as `MX6QDL_PAD_EIM_D21__I2C1_SCL` rather than raw IOMUXC offsets. Board files then append the pad-control word to complete each `fsl,pins` entry.

## Important APIs, Types, And Functions
There are no runtime functions or types. The public API is 1,030 `#define` macros for 197 physical pads, using the tuple format `<mux_reg conf_reg input_reg mux_mode input_val>`.

The macro namespace is `MX6QDL_PAD_<PAD_NAME>__<FUNCTION_NAME>`. Although the prefix is shared with i.MX6DL/Solo, this header represents the i.MX6Q/D register layout. Function families include SD1 through SD4, RGMII/ENET, EIM, dual IPU display and CSI routing, CSI0, NAND, GPIO banks 1 through 7, ECSPI1 through ECSPI5, I2C1 through I2C3, UART1 through UART5, ESAI/AUD, KEY matrix, HDMI DDC/CEC, SPDIF, FLEXCAN, SDMA, USB, boot strap `SRC_BOOT_CFG*`, watchdog, PWM/GPT/EPIT, MLB, HSI, and ARM trace/JTAG.

The Quad/Dual file differs from the DualLite file in meaningful ways. It includes IPU2 alternatives, ECSPI5 alternatives on SD pads, and Quad-specific select-input offsets, while i.MX6DL includes some EPDC-oriented alternatives absent here. For shared macro names, the symbolic name may match but the numeric tuple can differ.

## Control Flow
The file has no executable control flow. It is protected by `__DTS_IMX6Q_PINFUNC_H`, defines the tuple-format comment, lists the pad-function macros, and ends with the include guard close.

During DTS preprocessing, every macro expands inline into five cells. The device-tree compiler treats the expansion as integer data. Later, when a pinctrl state is selected by the kernel, the i.MX pinctrl driver writes the mux register at `mux_reg`, the pad-control register at `conf_reg`, and, when nonzero, the select-input register at `input_reg` with `input_val`.

## State, Persistence, And Dependencies
This header contains static hardware-description constants only. It has no mutable state, allocation, persistence, or side effects.

Its correctness depends on the i.MX6Q/D IOMUXC register map and on the Linux `fsl,imx-pinctrl` binding. The numbers are not self-validating: `mux_mode` must correspond to the named alternate function for that pad, and `input_val` must select the same physical pad in daisy-chain registers used by UART, I2C, ECSPI, ENET, IPU, USB, and similar peripherals.

## Integration Points
`imx6q.dtsi` includes this header, making the macros available to i.MX6Q/D board files and common `imx6qdl-*.dtsi` fragments. In-tree consumers use it in pinctrl groups for Ethernet, HDMI, I2C, SPI, UART, SD/eMMC, USB power/over-current, GPIO keys, displays, audio, CAN, and board-specific control signals.

The primary integration boundary is with the sibling i.MX6DL header: common board fragments rely on shared `MX6QDL_PAD_*` names, while the SoC root dtsi chooses either the Quad/Dual or DualLite/Solo numeric mapping. The kernel pinctrl driver and device-tree binding form the runtime consumer.

## Risks
The highest risk is silent hardware misconfiguration. A wrong register offset, mux mode, or select-input value can leave a peripheral unresponsive even when the DTB builds cleanly. This is especially likely around functions with many daisy-chain alternatives such as UART RX/RTS, I2C SCL/SDA, ECSPI chip selects, ENET clocks/data, IPU CSI inputs, USB ID/OC, and HDMI DDC/CEC.

The shared macro namespace can hide SoC-family differences. A board fragment that is valid for i.MX6Q may not have equivalent electrical routing or select-input values on i.MX6DL, despite using the same macro spelling. Conversely, adding new names here without considering common `imx6qdl` include files can break portability.

Special-case entries such as USB ID values and `GPIO_6__ENET_IRQ` carry non-obvious select-input or mux information. Boot-strap and reset-related pads also need care because changing them can affect early boot behavior or external reset lines.

## Test Signals
Build affected i.MX6Q/D DTBs with `make dtbs` and run `dtbs_check` to catch binding-shape regressions. Static checks should confirm exactly five cells per macro, no duplicate names, legal numeric tokens, and tuple values aligned with the i.MX6Q/D reference manual.

Runtime validation should focus on peripherals touched by changed macros: RGMII/ENET link and interrupts, I2C bus detection, SPI loopback or device probes, UART TX/RX and flow control, SD/eMMC card modes, HDMI DDC/CEC, USB host/OTG ID and over-current handling, display/camera paths, GPIO interrupts, and wake/reset pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx6q-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx6sl-pinfunc.h -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx6sl-pinfunc.h

## Purpose
`imx6sl-pinfunc.h` is the device-tree pin-function binding table for the NXP/Freescale i.MX6 SoloLite IOMUX controller. It defines symbolic pinmux constants for the SoC's pad set, including its display, e-paper, SD, FEC, audio, serial, USB, keypad, and GPIO routing options.

Like the other i.MX pin-function headers, each macro expands to `<mux_reg conf_reg input_reg mux_mode input_val>`. Board DTS files use these macros in `fsl,pins` arrays and append the pad-control word that configures electrical behavior.

## Important APIs, Types, And Functions
There are no C functions or data types. The interface is 1,059 `#define` macros covering 150 physical pads, all using the `MX6SL_PAD_<PAD_NAME>__<FUNCTION_NAME>` naming convention.

The covered pad families reflect the SoloLite feature mix: AUD, ECSPI1 through ECSPI4, EPDC/SPDC e-paper signals, FEC Ethernet, HSIC USB, I2C1 through I2C3, keypad rows/columns, LCD data and control, PWM, reference clocks, SD1 through SD3 plus SD4 alternatives, UART1 through UART5, watchdog, GPIO banks 1 through 5, CSI, EIM, GPT/EPIT, SPDIF, USB ID/power/over-current, boot strap `SRC_BOOT_CFG*`, and ARM trace/JTAG.

The `input_reg/input_val` cells are heavily used for shared input signals. Examples include I2C, UART RX/RTS, ECSPI, FEC, CSI, keypad, LCD, SD card detect/write-protect, USB ID/OC, GPT capture, EPDC power status/IRQ, and CCM PMIC ready.

## Control Flow
There is no executable control flow. The header uses the `__DTS_IMX6SL_PINFUNC_H` include guard, defines the tuple-format comment, emits a flat macro table, and closes the guard.

At build time, DTS preprocessing expands the macros into integer cells. At runtime, the pinctrl state selected by the kernel causes the i.MX pinctrl driver to program IOMUXC registers according to those cells. Whether and when a group is applied depends on the consuming device node's pinctrl state, not on this header.

## State, Persistence, And Dependencies
The file is pure static hardware description. It creates no persistent state and has no side effects by itself.

It depends on the i.MX6SL IOMUXC register map and the Linux i.MX pinctrl binding. The macro values must stay synchronized with the SoC reference manual, especially because SoloLite has a different pad inventory and display/e-paper-oriented mux map from i.MX6QDL. Board-level correctness also depends on matching the symbolic pinmux to the external schematic and supplying an appropriate pad-control value.

## Integration Points
`imx6sl.dtsi` includes this header, and i.MX6SL board files consume the macros in their pinctrl groups. In this source tree, `imx6sl-tolino-shine3.dts` uses the header extensively for touch, power key, hall sensor, LCD/EPDC-related GPIOs, I2C buses, UARTs, USB OTG ID, SD card pin states, charger/PMIC interrupts, and e-paper power control signals.

The runtime integration point is the same i.MX pinctrl driver family used by other i.MX SoCs, but the macro namespace is distinct (`MX6SL_PAD_*`) and not interchangeable with `MX6QDL_PAD_*`.

## Risks
The key risk is silent board failure from incorrect tuple data. A valid-looking macro with an incorrect mux register, mode, or select-input value can cause one peripheral input to listen to the wrong pad. This is particularly risky for SoloLite because many pads offer dense alternatives among EPDC, LCD, CSI, SD, FEC, UART, I2C, ECSPI, and GPIO functions.

Display and e-paper pads are high-impact: mistakes can disable panels, power sequencing, VCOM, or EPDC status/IRQ lines. USB ID/OC/power macros, watchdog/reset alternatives, boot strap signals, and PMIC-ready routes can affect boot, reset, power, or wake behavior.

Another risk is using a `MX6SL_PAD_*` macro spelling in common DTS content meant for other i.MX6 families, or copying numeric tuples from Q/DL headers. The pad inventory, offsets, and daisy-chain values are SoC-specific.

## Test Signals
Build all i.MX6SL DTBs with `make dtbs` and run `dtbs_check`. Static validation should check exactly five cells per macro, no duplicate definitions, valid hexadecimal numeric tokens, and reference-manual alignment for mux modes and select-input registers.

Hardware validation should cover panel or EPDC operation, e-paper power sequencing and IRQ/status signals, SD card detection and bus modes, FEC link and traffic, I2C scans, SPI devices, UART consoles, USB OTG ID/host behavior, GPIO interrupts, keypad signals where used, watchdog/reset routing, and suspend/resume wake lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx6sl-pinfunc.h -->
