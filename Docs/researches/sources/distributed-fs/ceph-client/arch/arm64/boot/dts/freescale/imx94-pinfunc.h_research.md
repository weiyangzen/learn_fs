# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx94-pinfunc.h

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
