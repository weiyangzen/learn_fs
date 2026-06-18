# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imxrt1170-pinfunc.h

Purpose: this binding header enumerates i.MXRT1170 IOMUXC pin alternatives for DTS pinctrl groups. It defines `IMX_PAD_SION` plus 1367 `IOMUXC_*` pin-function macros, each encoded as `<mux_reg conf_reg input_reg mux_mode input_val>`.

Important API surface: the exported macro names are the public contract. The file covers large GPIO pad families such as `GPIO_AD_*`, `GPIO_EMC_B1_*`, `GPIO_EMC_B2_*`, `GPIO_SD_B1_*`, `GPIO_DISP_B1_*`, and `GPIO_DISP_B2_*`. Alternatives span ADC/analog pads, SEMC, FlexSPI, USDHC, LPUART, LPI2C, LPSPI, SAI, SPDIF, ENET and ENET_QOS, CAN, LCDIF/video mux, ARM trace, PIT trigger, XBAR, WDOG, SRC boot config, and GPIO muxes.

Control flow: no executable logic exists. Device-tree source includes this header, the preprocessor emits numeric tuples, and the kernel pinctrl driver consumes those cells during pinctrl state application.

State and persistence: the file has only constants. These constants persist in built DTBs and become part of the board hardware description. Register-offset or selector changes affect boot-time hardware state, not a local software state machine.

Dependencies and integration: it is tied to the NXP i.MXRT1170 IOMUXC hardware map and the common i.MX pinctrl binding grammar. Board DTS files include it for `fsl,pins`; peripheral nodes reference the resulting pinctrl groups during probe and suspend/resume state selection.

Risks and test signals: the high macro volume makes copy/paste drift likely, especially `input_reg` and `input_val` for daisy-chained peripherals and the distinction between normal ENET and ENET_QOS functions. Compile with `make dtbs`, run dt-schema where bindings cover the board, and validate representative boot logs/peripheral operation for display, Ethernet, storage, UART, and I2C.
