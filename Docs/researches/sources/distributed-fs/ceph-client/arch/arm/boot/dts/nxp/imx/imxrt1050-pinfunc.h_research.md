# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imxrt1050-pinfunc.h

Purpose: this dt-bindings header defines the complete i.MXRT1050 IOMUXC pin-function constants consumed by device-tree `fsl,pins` properties. It exposes `IMX_PAD_SION` and 852 `MXRT1050_IOMUXC_*` macros. Each pin macro is a five-cell tuple documented in the file as `<mux_reg conf_reg input_reg mux_mode input_val>`.

Important API surface: the macro namespace is the API. Banks covered are `GPIO_EMC` (261 macro alternatives), `GPIO_AD` (255), `GPIO_B0` (112), `GPIO_B1` (107), and `GPIO_SD` (117). Functions include SEMC memory pins, FlexPWM, LPSPI, LPI2C, LPUART, SAI, ENET, CSI, USDHC, FlexSPI, XBAR, watchdog, CCM, SNVS, and GPIO alternatives. `IMX_PAD_SION` is an OR-able software-input-on bit used by the common i.MX pinctrl binding.

Control flow: there is no runtime control flow. The C preprocessor substitutes constants into compiled DTS files; the dtc output carries numeric cells that the i.MX pinctrl driver interprets when probing pinctrl nodes.

State and persistence: the header stores no mutable state. Its numeric register offsets and mux/input selector values are persistent ABI-like data for board DTS files; changing them can silently alter boot-time pad routing.

Dependencies and integration: included by i.MXRT1050 DTS/DTSI files under the ARM device-tree build. It depends on Linux dt-bindings conventions and the NXP i.MX pinctrl driver tuple parser. The values integrate with SoC reference-manual IOMUXC register layout and with board `pinctrl-*` groups.

Risks and test signals: risks are off-by-one register offsets, wrong daisy-chain `input_val`, missing GPIO alternative, or changing a macro name used by a DTS. Useful tests are `make dtbs` for affected i.MXRT1050 boards, dtc preprocessing checks for all referenced macros, and runtime validation that critical peripherals such as USDHC, ENET, LPUART, and FlexSPI probe with expected pins.
