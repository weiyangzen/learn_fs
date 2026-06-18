# subset-b-000670 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx91-pinfunc.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx91-pinfunc.h

### Purpose
`imx91-pinfunc.h` is the i.MX91 device-tree pin-function catalog consumed by i.MX pinctrl nodes. It defines the symbolic `MX91_PAD_*__*` macros that expand to the five-cell pinmux tuple documented by the Freescale i.MX pinctrl bindings: `<mux_reg conf_reg input_reg mux_mode input_val>`. DTS pin groups then append the sixth pad-configuration cell in `fsl,pins`.

### Important APIs, Types, And Functions
There are no C functions or runtime types. The public surface is a preprocessor ABI with 650 `MX91_PAD_` macros over 108 physical pads and 510 unique alternate functions. Major pad groups include DAP/JTAG, GPIO_IO00 through GPIO_IO29, CCM clock outputs, ENET1/ENET2 RGMII pins, USDHC SD1/SD2/SD3 pins, I2C1/I2C2, UART1/UART2, PDM, SAI1, and WDOG. Each macro name encodes both the physical pad and selected signal, while the numeric tuple encodes IOMUXC register offsets, mux mode, and optional daisy-chain input select value.

### Control Flow
This header has no executable control flow. Build-time preprocessing substitutes each macro into DTS `fsl,pins` arrays. At boot, the compiled DTB is interpreted by the i.MX pinctrl driver, which writes the mux register, pad configuration register, and select-input register when `input_reg` is nonzero. The macros with `input_reg` set select one of several candidate pads for receiver paths such as CAN, LPI2C, LPUART, PDM, SAI, SPDIF, USDHC3, or FLEXIO.

### State, Persistence, And Dependencies
The file holds no mutable state. Its values become persistent hardware configuration only after board DTS files instantiate pin groups and the kernel programs the IOMUXC registers. The include guard is `__DTS_IMX91_PINFUNC_H`, and the license is dual GPL-2.0+ or MIT. It is directly included by `imx91.dtsi`, which sets `&iomuxc` compatible to `fsl,imx91-iomuxc`, and is paired with the shared `imx91_93_common.dtsi` SoC description.

### Integration Points
The integration contract is the i.MX9 `fsl,pins` binding: one `MX91_PAD_*` macro plus one pad config value per pin. The macros support i.MX91 board and SoC DTS nodes configuring Ethernet, SD/MMC, serial, I2C/I3C, audio, camera/display media pins, GPIOs, watchdog, debug, and low-power/control functions. The numeric offsets must match the i.MX91 IOMUXC register layout expected by the `fsl,imx91-iomuxc` compatible.

### Risks
This is effectively a hardware ABI. A wrong mux mode or register offset can silently route a signal to the wrong pad, while a wrong `input_val` can leave an input peripheral disconnected even though the mux mode appears correct. The i.MX91 and i.MX93 files are similar but not identical: i.MX91 uses different select-input offsets for several peripherals and names security UART as `ELE_UART`, so copying i.MX93 pin names or values across would be risky. GPIO numbering is also encoded in names and must match the SoC GPIO controllers used by board DTS files.

### Test Signals
Useful checks are `make dtbs`/`dtbs_check` for i.MX91 DTS coverage, preprocessing spot checks that `fsl,pins` entries expand to six cells, and boot tests that exercise every configured peripheral on a target board. Hardware smoke tests should include UART console, I2C/I3C buses, SD/eMMC detection and high-speed modes, Ethernet link and RX/TX traffic, GPIO interrupts, audio/PDM/SAI where used, and alternate input routes with nonzero select-input values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx91-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx93-pinfunc.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx93-pinfunc.h

### Purpose
`imx93-pinfunc.h` is the i.MX93 pin-function definition header for device trees. It supplies the `MX93_PAD_*__*` macro namespace used inside `fsl,pins` properties, with each macro expanding to `<mux_reg conf_reg input_reg mux_mode input_val>` and board DTS files adding the final pad-control value.

### Important APIs, Types, And Functions
There are no functions or structs. The interface consists of 609 `MX93_PAD_` macros spanning 108 pads and 516 unique signal functions. Coverage includes DAP/JTAG, GPIO_IO00 through GPIO_IO29, CCM_CLKO1-4, ENET1/ENET2, SD1/SD2/SD3, I2C1/I2C2, UART1/UART2, PDM, SAI1, and WDOG. Compared with i.MX91, this header uses i.MX93 naming conventions such as zero-padded GPIO/signal names, `S400_UART`, PDM stream names with two digits, and high mux-mode values like `0x10`, `0x11`, and `0x16` for LPI2C routes.

### Control Flow
The header participates only in compile-time DTS preprocessing. DTS files select a macro in a pin group; the resulting DTB stores five routing cells plus one config cell. At runtime the i.MX pinctrl driver consumes the cells and writes mux, config, and select-input registers. Macros with nonzero `input_reg` and `input_val` select daisy inputs for shared receiver functions, especially CAN, LPI2C, LPUART, PDM, SAI, SPDIF, USDHC3, and FLEXIO.

### State, Persistence, And Dependencies
The file has no local state. Its values persist only as programmed IOMUXC hardware state after the pinctrl driver applies a device-tree state. The include guard is `__DTS_IMX93_PINFUNC_H`, and the license is dual GPL-2.0+ or MIT. `imx91_93_common.dtsi` includes this file for the common i.MX91/i.MX93 base, and multiple i.MX93 board overlays include it directly for optional peripherals such as CAN, display, Wi-Fi/Bluetooth, JTAG, I3C, and PWM fan support.

### Integration Points
Primary consumers are `imx91_93_common.dtsi` and board `.dtso` files under the Freescale arm64 DTS tree. The macros integrate with the i.MX9 pinctrl binding and the i.MX pinctrl driver through the standard `fsl,pins` tuple shape. They also cross-reference peripheral nodes that use separate clock/power/interrupt bindings, so a pin macro is only one part of enabling a peripheral; clocks, resets, supplies, and controller status must also be correct.

### Risks
The risk profile is register-accuracy and board-routing accuracy. i.MX91 and i.MX93 share many pad names but differ in input register offsets, mux mode encodings, and function names, so using the wrong SoC header can produce a DTB that compiles but programs incorrect hardware. Nonzero daisy selections are easy to miss during review because the macro name looks sufficient. Some peripheral names in this file refer to SoC-specific internal blocks, such as S400 or CCMSRCGPCMIX, which should not be normalized without checking the reference manual and existing board DTS usage.

### Test Signals
Validation should include `make dtbs` for i.MX93 targets, `dtbs_check` against `fsl,imx9-pinctrl.yaml`, and board-level tests for the overlays that include this file. High-signal hardware checks include UART5 flow control on DAP pins, USDHC3 Wi-Fi/SDIO pin groups, display media pin groups, CAN1 on PDM pads, JTAG on GPIO_IO24-27, I3C on I2C pads, and any route using mux modes `0x10`, `0x11`, or `0x16`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx93-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx94-clock.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx94-clock.h

### Purpose
`imx94-clock.h` defines the i.MX94 clock ID namespace used by device-tree clock specifiers. It maps human-readable `IMX94_CLK_*` names to integer IDs that are passed as the single argument to clock providers such as the SCMI clock protocol in `imx94.dtsi`.

### Important APIs, Types, And Functions
There are no functions or data structures. The public API is 183 integer macros, numbered from `IMX94_CLK_EXT` at 0 through `IMX94_CLK_NPU_CGC` at 182. The list covers fixed/external roots, PLL VCOs and PFD outputs, reserved ABI slots 18-23, bus roots, CPU/M33/M70/M71 clocks, DRAM/display/HSIO roots, network and EtherCAT clocks, LPI2C/LPSPI/LPUART instances, SAI, TPM, USB PHY, USDHC, XSPI, clock-output selectors, and NPU gating.

### Control Flow
This header has no runtime flow. During DTS preprocessing, clock specifiers such as `<&scmi_clk IMX94_CLK_LPUART5>` become numeric IDs in the DTB. At runtime, consumer drivers call the common clock framework with those IDs; the provider, represented in `imx94.dtsi` as SCMI protocol 0x14 with `#clock-cells = <1>`, resolves the ID to firmware-managed clock operations.

### State, Persistence, And Dependencies
The file has no state. Its integer assignments are persistent ABI values between device trees, firmware clock providers, and kernel drivers. The include guard is `__IMX94_CLOCK_H`, and the license is GPL-2.0-only or MIT. `imx94.dtsi` includes this file and uses many IDs for clocks and assigned-clock parents on buses, UARTs, LPI2C/LPSPI, CAN, SAI, USDHC, HSIO, and other SoC nodes.

### Integration Points
The main integration point is `imx94.dtsi`, where `scmi_clk: protocol@14` exposes a one-cell clock provider. Peripheral nodes use `clocks = <&scmi_clk IMX94_CLK_...>` and sometimes `assigned-clocks` and `assigned-clock-parents`, for example CAN nodes selecting `IMX94_CLK_SYSPLL1_PFD1_DIV2` and USDHC nodes selecting `IMX94_CLK_SYSPLL1_PFD1`. The IDs also need to stay consistent with any firmware SCMI clock table and any out-of-tree DTS files that include the same binding.

### Risks
Clock IDs are ABI-sensitive: renumbering, reusing reserved IDs, or inserting a new macro in the middle can make old DTBs request the wrong firmware clock. Reserved entries 18-23 should remain stable unless the firmware/kernel contract explicitly changes. Similar SoCs may have nearby naming but not identical ID maps; replacing this header with another i.MX9 clock binding would compile yet break runtime clock acquisition. Names that distinguish ungated PLL outputs, gated PFD outputs, and divided PFD outputs must remain precise because consumers may depend on rate and gate behavior.

### Test Signals
Useful validation includes building `imx94.dtb`, running `dtbs_check`, booting with clock-provider debug enabled, and checking that every enabled node in `imx94.dtsi` can acquire its clocks. Runtime signals include UART console availability, CAN assigned parent/rate programming, USDHC bus rates, HSIO/USB clocks, network clocks, and absence of SCMI "clock not found" errors. ABI tests should compare generated numeric IDs against firmware documentation or an SCMI clock dump.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx94-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx94-pinfunc.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx94-pinfunc.h

### Purpose
`imx94-pinfunc.h` is the i.MX94 pin-function catalog for arm64 device trees. It defines both pad-control convenience constants and `IMX94_PAD_*__*` pinmux macros that expand to `<mux_reg conf_reg input_reg mux_mode input_val>` for `fsl,pins` properties.

### Important APIs, Types, And Functions
There are no functions or C types. The exported API has two parts. First are pad-control bit constants for drive strength (`IMX94_DSE_X1` through `IMX94_DSE_X6`), slew rate (`IMX94_FSEL_FAST`/`SLOW`), pull-up, pull-down, open-drain, and Schmitt trigger. Second are 1351 `IMX94_PAD_` macros over 192 pads and 965 unique functions. Pad coverage includes DAP, GPIO_IO00-57, CCM_CLKO1-4, ETH0-ETH4/NETC/ECAT groups, SD1/SD2, XSPI1, I2C1/I2C2, UART1/UART2, PDM, SAI1, and WDOG.

### Control Flow
The file has no executable control flow. DTS preprocessing expands pin macros into numeric cells, and the i.MX pinctrl driver later writes IOMUXC mux/config/select-input registers. i.MX94 adds more complex mux encodings than i.MX91/i.MX93: most mux modes are `0x00` through `0x07`, but some entries use extended values such as `0x0100`, `0x0105`, and `0x0200` for alternate paths like XSPI indication, XBAR, or SAI routes. Nearly 500 macros use select-input registers, so receiver daisy routing is a major part of the runtime effect.

### State, Persistence, And Dependencies
The header holds no mutable state. Its macro values persist only once compiled into a DTB and applied to hardware by pinctrl. The include guard is `__DTS_IMX94_PINFUNC_H`, and the license is dual GPL-2.0+ or MIT. `imx94.dtsi` includes this file alongside `imx94-clock.h` and `imx94-power.h`; it defines SCMI-managed firmware services including an `scmi_iomuxc` protocol, while the pin macros provide the numeric pad routes used by board-level pinctrl states.

### Integration Points
The file integrates with i.MX9 pinctrl bindings and i.MX94 DTS files through `fsl,pins`. It is also tied to the i.MX94 clock and power descriptions because pin routing only makes sense when the target peripheral node is enabled and clocked. Important peripheral families represented in the macros include LPI2C1-8, LPSPI1-8, LPUART1-12, CAN1-5, SAI1-4, PDM, TPM/FLEXPWM, LPIT/GPT, USB OTG control pins, NETC Ethernet and 1588 mux inputs, EtherCAT, XSPI, USDHC, XBAR, SINC filters, and GPIO banks 1-7.

### Risks
The main risks are hardware misrouting and ABI drift. i.MX94 has many more pads and several extended mux modes, so tools or reviewers assuming only 3-bit mux values may mishandle valid entries. The pad-control constants are bare bitfields intended to be ORed into the final config cell; mixing them with copied numeric pad configs from older SoCs can set the wrong electrical behavior. Ethernet/NETC/ECAT and SD/XSPI pads are highly multiplexed, so board changes must check both functional muxing and input select values. Because macro names are source-level ABI for DTS files, renaming or removing them can break board overlays even if the numeric tuple remains available under another name.

### Test Signals
Validation should include `make dtbs`, `dtbs_check` against the i.MX9 pinctrl schema, and a scan for `fsl,pins` entries that expand to exactly six cells. Hardware tests should focus on mux-heavy groups: LPUART flow control, LPI2C/LPSPI buses, CAN2-5, USDHC1-3 where board-routed, XSPI1 and XSPI2-related alternate paths, Ethernet/NETC/ECAT links, USB OTG ID/power/overcurrent pins, and XBAR/SINC/GPT routes with nonzero select-input values. Electrical tests should verify drive strength, slew, pull, open-drain, and hysteresis combinations when the provided `IMX94_*` config constants are used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx94-pinfunc.h -->
