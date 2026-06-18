# Research: subset-b-000638

Grouped source-tree-aligned research for the requested ARM DTS NXP, Qualcomm, Realtek, Renesas, Rockchip, Samsung, SigmaStar, and Socionext files.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imxrt1050-pinfunc.h -->
## sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imxrt1050-pinfunc.h

Purpose: this dt-bindings header defines the complete i.MXRT1050 IOMUXC pin-function constants consumed by device-tree `fsl,pins` properties. It exposes `IMX_PAD_SION` and 852 `MXRT1050_IOMUXC_*` macros. Each pin macro is a five-cell tuple documented in the file as `<mux_reg conf_reg input_reg mux_mode input_val>`.

Important API surface: the macro namespace is the API. Banks covered are `GPIO_EMC` (261 macro alternatives), `GPIO_AD` (255), `GPIO_B0` (112), `GPIO_B1` (107), and `GPIO_SD` (117). Functions include SEMC memory pins, FlexPWM, LPSPI, LPI2C, LPUART, SAI, ENET, CSI, USDHC, FlexSPI, XBAR, watchdog, CCM, SNVS, and GPIO alternatives. `IMX_PAD_SION` is an OR-able software-input-on bit used by the common i.MX pinctrl binding.

Control flow: there is no runtime control flow. The C preprocessor substitutes constants into compiled DTS files; the dtc output carries numeric cells that the i.MX pinctrl driver interprets when probing pinctrl nodes.

State and persistence: the header stores no mutable state. Its numeric register offsets and mux/input selector values are persistent ABI-like data for board DTS files; changing them can silently alter boot-time pad routing.

Dependencies and integration: included by i.MXRT1050 DTS/DTSI files under the ARM device-tree build. It depends on Linux dt-bindings conventions and the NXP i.MX pinctrl driver tuple parser. The values integrate with SoC reference-manual IOMUXC register layout and with board `pinctrl-*` groups.

Risks and test signals: risks are off-by-one register offsets, wrong daisy-chain `input_val`, missing GPIO alternative, or changing a macro name used by a DTS. Useful tests are `make dtbs` for affected i.MXRT1050 boards, dtc preprocessing checks for all referenced macros, and runtime validation that critical peripherals such as USDHC, ENET, LPUART, and FlexSPI probe with expected pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imxrt1050-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imxrt1170-pinfunc.h -->
## sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imxrt1170-pinfunc.h

Purpose: this binding header enumerates i.MXRT1170 IOMUXC pin alternatives for DTS pinctrl groups. It defines `IMX_PAD_SION` plus 1367 `IOMUXC_*` pin-function macros, each encoded as `<mux_reg conf_reg input_reg mux_mode input_val>`.

Important API surface: the exported macro names are the public contract. The file covers large GPIO pad families such as `GPIO_AD_*`, `GPIO_EMC_B1_*`, `GPIO_EMC_B2_*`, `GPIO_SD_B1_*`, `GPIO_DISP_B1_*`, and `GPIO_DISP_B2_*`. Alternatives span ADC/analog pads, SEMC, FlexSPI, USDHC, LPUART, LPI2C, LPSPI, SAI, SPDIF, ENET and ENET_QOS, CAN, LCDIF/video mux, ARM trace, PIT trigger, XBAR, WDOG, SRC boot config, and GPIO muxes.

Control flow: no executable logic exists. Device-tree source includes this header, the preprocessor emits numeric tuples, and the kernel pinctrl driver consumes those cells during pinctrl state application.

State and persistence: the file has only constants. These constants persist in built DTBs and become part of the board hardware description. Register-offset or selector changes affect boot-time hardware state, not a local software state machine.

Dependencies and integration: it is tied to the NXP i.MXRT1170 IOMUXC hardware map and the common i.MX pinctrl binding grammar. Board DTS files include it for `fsl,pins`; peripheral nodes reference the resulting pinctrl groups during probe and suspend/resume state selection.

Risks and test signals: the high macro volume makes copy/paste drift likely, especially `input_reg` and `input_val` for daisy-chained peripherals and the distinction between normal ENET and ENET_QOS functions. Compile with `make dtbs`, run dt-schema where bindings cover the board, and validate representative boot logs/peripheral operation for display, Ethernet, storage, UART, and I2C.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imxrt1170-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/lpc/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/lpc/Makefile

Purpose: this Kbuild fragment selects NXP LPC ARM device-tree blobs for the kernel DTB build. It maps six DTBs to two architecture configuration symbols.

Important API surface: `dtb-$(CONFIG_ARCH_LPC18XX)` adds `lpc4337-ciaa.dtb`, `lpc4350-hitex-eval.dtb`, `lpc4357-ea4357-devkit.dtb`, and `lpc4357-myd-lpc4357.dtb`. `dtb-$(CONFIG_ARCH_LPC32XX)` adds `lpc3250-ea3250.dtb` and `lpc3250-phy3250.dtb`. The Kbuild variable names are consumed by the ARM `dtbs` target.

Control flow: Kbuild evaluates the `CONFIG_ARCH_*` symbols and appends matching DTB targets. There is no shell logic or custom rule.

State and persistence: no runtime state is held. The persistent effect is the build manifest: enabled configs determine which DTBs are generated and shipped.

Dependencies and integration: depends on matching `.dts` files in the same directory and on the parent ARM DTS Makefile descending into `nxp/lpc`. It integrates with kernel configuration and packaging flows that collect generated DTBs.

Risks and test signals: stale names break `make dtbs`; missing entries leave boards without installable DTBs. Test with configs enabling LPC18xx and LPC32xx, and verify every listed `.dts` target exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/lpc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/ls/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/ls/Makefile

Purpose: this Kbuild fragment lists Layerscape LS1021A DTB outputs and composed overlay DTB targets.

Important API surface: under `CONFIG_SOC_LS1021A`, it builds base boards such as `ls1021a-iot.dtb`, `ls1021a-moxa-uc-8410a.dtb`, `ls1021a-qds.dtb`, `ls1021a-tqmls1021a-mbls1021a.dtb`, `ls1021a-tsn.dtb`, and `ls1021a-twr.dtb`. It also defines four `*-dtbs` composition variables pairing the TQMLS1021A base DTB with HDMI, LVDS, and RGB display overlay `.dtbo` files, then exposes the resulting composed `.dtb` targets.

Control flow: Kbuild expands conditional `dtb-y` style variables and recognizes `<target>-dtbs` lists to build composite DTBs from a base plus overlays.

State and persistence: no mutable state. The file persists board support in the build graph, including display-panel variants that become separate generated artifacts.

Dependencies and integration: depends on LS1021A `.dts` and `.dtso` files, the kernel overlay composition machinery, and `CONFIG_SOC_LS1021A`. Bootloader or distribution packaging may depend on the exact composed target names.

Risks and test signals: overlay ordering and target naming are fragile. A wrong base/overlay pairing can compile but describe the wrong display hardware. Test `make dtbs` with LS1021A enabled and inspect that all four composed display DTBs are emitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/ls/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/mxs/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/mxs/Makefile

Purpose: this Makefile is the DTB build manifest for NXP/Freescale MXS i.MX23 and i.MX28 boards.

Important API surface: `dtb-$(CONFIG_ARCH_MXS)` appends 33 board DTBs. The list includes i.MX23 boards such as `imx23-evk`, `imx23-olinuxino`, `imx23-sansa`, `imx23-stmp378x_devb`, and `imx23-xfi3`; and many i.MX28 boards such as `imx28-apf28`, `imx28-apx4devkit`, `imx28-duckbill*`, `imx28-evk`, `imx28-m28evk`, `imx28-ts4600`, `imx28-tx28`, and `imx28-xea`.

Control flow: Kbuild conditionally includes the full list when `CONFIG_ARCH_MXS` is enabled. No custom commands are present.

State and persistence: the file stores the persistent build inventory for MXS DTBs. It does not affect kernel runtime state directly.

Dependencies and integration: depends on matching DTS files, `imx23-pinfunc.h`, `imx28-pinfunc.h`, and common MXS DTSI files. Parent ARM DTS Kbuild uses this fragment to produce board DTBs for packaging.

Risks and test signals: board support can disappear if a target is removed or misspelled. Test with `make ARCH=arm dtbs` for `CONFIG_ARCH_MXS`; check that each listed `.dtb` has a corresponding source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/mxs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/mxs/imx23-pinfunc.h -->
## sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/mxs/imx23-pinfunc.h

Purpose: this MXS pinctrl binding header defines i.MX23 pad/function constants for DTS pin groups. It includes `mxs-pinfunc.h` for shared electrical configuration constants.

Important API surface: it exports 313 `MX23_PAD_*__*` macros. The packed numeric values use the MXS pad encoding where the high nibbles identify bank/pin position and the low bits encode mux function. Banks/functions include GPMI NAND, LCD, SSP1/SSP2, EMI, AUART, I2C, PWM, rotary, ETM/JTAG, SAIF, SPDIF, and GPIO aliases. GPIO alternatives cover GPIO banks 0 through 2.

Control flow: no runtime logic exists. DTS preprocessing replaces readable pad names with packed constants that the MXS pinctrl driver decodes.

State and persistence: constants are immutable source data. Once built into DTBs, they persist as the hardware pad selection for board pinctrl states.

Dependencies and integration: depends on `mxs-pinfunc.h` for `MXS_DRIVE_*`, `MXS_VOLTAGE_*`, and `MXS_PULL_*` values used alongside the function IDs. Board DTS files combine these function constants with electrical properties in MXS pinctrl nodes.

Risks and test signals: errors in the packed low mux value can select a valid but wrong alternate function. The dense GPIO alias section also risks bank/pin mismatch. Test by compiling all i.MX23 DTBs and validating boot-time pinctrl, especially NAND, LCD, UART, I2C, and MMC-style SSP pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/mxs/imx23-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/mxs/imx28-pinfunc.h -->
## sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/mxs/imx28-pinfunc.h

Purpose: this header provides i.MX28 pad/function IDs for MXS device-tree pinctrl bindings and includes the shared `mxs-pinfunc.h` electrical constants.

Important API surface: it exports 486 `MX28_PAD_*__*` macros. Covered pad groups include GPMI, LCD, SSP0 through SSP3, AUART0 through AUART3, PWM, SAIF, I2C0, SPDIF, ENET0/ENET clock, JTAG, and EMI address/data/control pins. GPIO alternatives cover GPIO banks 0 through 4. The values are compact MXS encodings such as `0x0000`, `0x0001`, and `0x0003`, with low bits indicating mux selection.

Control flow: no executable control flow. The header participates in C-preprocessed DTS compilation; the pinctrl driver later decodes the numeric values.

State and persistence: no mutable state. The constants form a stable DT binding contract for generated DTBs and board hardware routing.

Dependencies and integration: depends on the MXS pinctrl binding, the shared MXS electrical property constants, and the i.MX28 board DTS files selected by the `nxp/mxs/Makefile`.

Risks and test signals: risks include wrong mux value for Ethernet/SAIF/SSP alternatives, confusing similarly named `ENET0` and `ENET1` timestamp functions, and GPIO bank numbering mistakes. Test all i.MX28 DTBs and run hardware smoke tests for Ethernet, LCD, NAND, UART, and storage on representative boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/mxs/imx28-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/mxs/mxs-pinfunc.h -->
## sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/mxs/mxs-pinfunc.h

Purpose: this small shared binding header defines electrical configuration constants for MXS pinctrl nodes.

Important API surface: it exports eight macros: `MXS_DRIVE_4mA`, `MXS_DRIVE_8mA`, `MXS_DRIVE_12mA`, `MXS_DRIVE_16mA`, `MXS_VOLTAGE_LOW`, `MXS_VOLTAGE_HIGH`, `MXS_PULL_DISABLE`, and `MXS_PULL_ENABLE`. These map directly to `fsl,drive-strength`, `fsl,voltage`, and `fsl,pull-up` property values.

Control flow: none. DTS files include this header for symbolic constants, and dtc emits the numeric property values.

State and persistence: no state is held. Numeric values persist in DTBs as pin electrical settings that the MXS pinctrl driver applies at boot.

Dependencies and integration: included by `imx23-pinfunc.h`, `imx28-pinfunc.h`, and board DTS/DTSI files using MXS pinctrl properties.

Risks and test signals: changing numeric values would alter drive strength, voltage selection, or pull-up behavior across many boards. Test with `make dtbs`, schema checks for MXS pinctrl properties, and hardware validation for buses sensitive to drive/pull settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/mxs/mxs-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/vf/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/vf/Makefile

Purpose: this Kbuild fragment lists Vybrid VF500/VF610 board DTBs.

Important API surface: `dtb-$(CONFIG_SOC_VF610)` appends 14 outputs, including Colibri VF500/VF610 variants, `vf610-bk4`, `vf610-cosmic` and `vf610m4-cosmic`, `vf610-twr`, and multiple ZII boards such as `vf610-zii-dev-rev-b`, `vf610-zii-dev-rev-c`, `vf610-zii-scu4-aib`, `vf610-zii-spb4`, and SSMB variants.

Control flow: Kbuild conditionally emits the list for `CONFIG_SOC_VF610`. There are no composite overlay rules.

State and persistence: no runtime state. It persists the board DTB inventory for the VF610 SoC family.

Dependencies and integration: depends on matching `.dts` files and shared VF610 DTSI/pin binding data such as `vf610-pinfunc.h`. Parent ARM DTS Kbuild includes this fragment.

Risks and test signals: stale entries fail `make dtbs`; missing entries break board packaging. Test with a VF610-enabled config and ensure all listed DTBs build cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/vf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/vf/vf610-pinfunc.h -->
## sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/vf/vf610-pinfunc.h

Purpose: this binding header defines Vybrid VF610 pin-function IDs for device-tree pinctrl groups.

Important API surface: it defines `ALT0` through `ALT7` and 831 `VF610_PAD_*` macros. The documented tuple shape is `<mux_reg input_reg mux_mode input_val>`. Pad banks include PTA, PTB, PTC, PTD, PTE, and DDR pads. Function coverage includes GPIO, RMII/ENET, DCU display, LCD, VIU, UART, I2C, DSPI, QSPI, SAI/ESAI, FTM timers, CAN, USB control pins, NAND/FB, SRC boot straps, debug outputs, watchdog/NMI, and DDR signals.

Control flow: no runtime code. DTS preprocessing converts symbolic pin names into tuples; the VF610/NXP pinctrl implementation programs mux and input-select registers while applying pinctrl states.

State and persistence: constants only. The generated DTB stores mux tuples that persist as board hardware configuration at boot and during pinctrl state switches.

Dependencies and integration: integrated with VF610 board DTS files, `CONFIG_SOC_VF610` DTB builds, and the pinctrl driver parser that recognizes `ALT*` mux modes and input daisy values.

Risks and test signals: risks include inconsistent macro naming, wrong input register for shared signals, and DDR pad changes that may affect early hardware assumptions. Test `make dtbs` for VF610 boards, then hardware smoke-test UART console, Ethernet, display, storage, and I2C/SPI pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/vf/vf610-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/qcom/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm/boot/dts/qcom/Makefile

Purpose: this Kbuild fragment enumerates 32-bit Qualcomm ARM DTBs under `CONFIG_ARCH_QCOM`.

Important API surface: a single `dtb-$(CONFIG_ARCH_QCOM)` list contains 60 DTBs spanning MSM8226/MSM8926 phones, APQ8016/APQ806x/APQ8074 boards, IPQ4018/IPQ4019/IPQ8064 networking platforms, MSM8916 devices, MSM8960/MSM8974 phones/tablets, MDM9615, and SDX55/SDX65 modem platforms.

Control flow: Kbuild appends the full list when the architecture config is enabled. No custom commands or overlay composition are present.

State and persistence: the file holds build inventory only. Generated DTBs become persistent artifacts consumed by bootloaders and distro packages.

Dependencies and integration: depends on same-directory Qualcomm DTS/DTSI files and the parent ARM DTS build. It is also coupled to naming conventions used by firmware loaders and packaging scripts.

Risks and test signals: with many product DTBs, risks are misspellings, removed DTS files still listed, or new boards omitted from the build. Test with `CONFIG_ARCH_QCOM=y` and `make ARCH=arm dtbs`; verify every listed board source exists and schema warnings are reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/qcom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/realtek/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm/boot/dts/realtek/Makefile

Purpose: this Makefile lists Realtek ARM DTBs for the kernel device-tree build.

Important API surface: `dtb-$(CONFIG_ARCH_REALTEK)` includes `rtd1195-horseradish.dtb` and `rtd1195-mele-x1000.dtb`.

Control flow: Kbuild conditionally appends two DTB targets based on `CONFIG_ARCH_REALTEK`.

State and persistence: no runtime state. The file persists the buildable RTD1195 board inventory.

Dependencies and integration: depends on matching Realtek DTS files and parent ARM DTS Makefile inclusion. Generated DTBs integrate with bootloader board selection for RTD1195 systems.

Risks and test signals: low complexity, but target/source drift still breaks `make dtbs`. Test with Realtek arch enabled and ensure both DTBs compile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/realtek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/renesas/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm/boot/dts/renesas/Makefile

Purpose: this Kbuild fragment selects Renesas ARM DTBs for multiple legacy and RZ/R-Car families.

Important API surface: `dtb-$(CONFIG_ARCH_RENESAS)` appends 32 DTBs. The list spans EMEV2, RZ/A1 and RZ/A2 boards, RZ/G1 and R-Car Gen2-style `r8a77xx/r8a779x` boards, RZ/N1 `r9a06g032` DB/EB boards, and `sh73a0-kzm9g`.

Control flow: Kbuild conditionally includes the list when Renesas ARM support is enabled. There are no overlay or custom build rules.

State and persistence: no mutable state. It persists the set of Renesas board DTBs generated by the build.

Dependencies and integration: depends on same-directory DTS files and SoC `.dtsi` includes. It integrates with distribution DTB packaging and bootloader board-specific DTB naming.

Risks and test signals: board names with daughter-card suffixes are easy to omit or mistype. Test `make dtbs` under `CONFIG_ARCH_RENESAS` and check dt-schema output for changed SoC/board bindings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/renesas/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/rockchip/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm/boot/dts/rockchip/Makefile

Purpose: this Kbuild fragment enumerates 32-bit Rockchip DTBs.

Important API surface: `dtb-$(CONFIG_ARCH_ROCKCHIP)` lists 45 targets covering RV1103/RV1108/RV1109/RV1126 boards, RK3036, RK3066a, RK3128, RK3188, RK3228/RK3229, and many RK3288 boards including Firefly, MiQi, Popmetal, Rock2, Rock Pi N8, Tinker, and Veyron Chromebook variants.

Control flow: Kbuild includes the list when `CONFIG_ARCH_ROCKCHIP` is enabled. No composite targets are defined.

State and persistence: no runtime state. The persistent artifact is the build graph for Rockchip board DTBs.

Dependencies and integration: depends on matching DTS files, shared Rockchip DTSI files, pinctrl/GPIO bindings, and parent ARM DTS Makefile recursion.

Risks and test signals: high board count means stale target risk and incomplete board coverage. Test `make ARCH=arm dtbs` for Rockchip, and validate that Veyron and RK3288 variants remain separately built because they often differ in regulators, panels, and peripherals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/rockchip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/Makefile

Purpose: this Makefile is the ARM Samsung DTB build manifest for Exynos3/4/5, S3C64xx, and S5PV210 families.

Important API surface: it declares conditional `dtb-*` lists for `CONFIG_ARCH_EXYNOS3` (3 DTBs), `CONFIG_ARCH_EXYNOS4` (18), `CONFIG_ARCH_EXYNOS5` (22), `CONFIG_ARCH_S3C64XX` (2), and `CONFIG_ARCH_S5PV210` (7), totaling 52 DTB targets. It covers phones, tablets, Chromebook boards, Odroid boards, Samsung reference boards, and legacy S3C/S5PV210 boards.

Control flow: Kbuild evaluates each architecture symbol independently, so multi-platform configs may build several Samsung families in one `dtbs` run.

State and persistence: no runtime state. The file persists which board descriptions are generated and packaged.

Dependencies and integration: depends on same-directory DTS files and Samsung pinctrl binding headers such as `exynos-pinctrl.h`, `s3c64xx-pinctrl.h`, and `s5pv210-pinctrl.h`. It integrates with the parent ARM DTS build.

Risks and test signals: risks are stale board targets and accidental movement between config groups. Test with Samsung architecture configs enabled and review schema output for Exynos pinctrl and board bindings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/exynos-pinctrl.h -->
## sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/exynos-pinctrl.h

Purpose: this Samsung binding header defines symbolic pinctrl constants for Exynos DTS files.

Important API surface: it exports pull mode constants (`EXYNOS_PIN_PULL_NONE`, DOWN, UP), power-down function constants (`EXYNOS_PIN_PDN_*`), drive strength encodings for Exynos4/3250/5250, Exynos5260, and Exynos5420/542x/5800/850-style blocks, and pin function constants from input/output through function 6 plus external interrupt function `0xf` (`EXYNOS_PIN_FUNC_EINT`/`F`).

Control flow: none. DTS files include the header to express pin configuration values symbolically; dtc emits the numbers that Samsung pinctrl drivers apply.

State and persistence: constants only. The values persist in DTBs as pull, drive, power-down, and mux settings.

Dependencies and integration: integrated with Exynos pinctrl binding properties and Exynos board DTS files selected by the Samsung Makefile. The different drive-strength macro families reflect SoC-specific register encodings.

Risks and test signals: changing a value can misconfigure every board using that SoC family. A key risk is using the wrong drive-strength family for a DTS node. Test with dt-schema for Samsung pinctrl nodes and boot/peripheral checks for GPIO, eMMC, SDIO, I2C, and sleep/resume pin states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/exynos-pinctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/s3c64xx-pinctrl.h -->
## sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/s3c64xx-pinctrl.h

Purpose: this header provides Samsung S3C64xx DTS pinctrl symbolic constants.

Important API surface: it defines pull modes `S3C64XX_PIN_PULL_NONE`, DOWN, and UP; and pin functions `INPUT`, `OUTPUT`, `FUNC_2` through `FUNC_6`, plus external interrupt function `S3C64XX_PIN_FUNC_EINT` with value 7.

Control flow: there is no executable logic. DTS preprocessing substitutes these names into pinctrl property cells.

State and persistence: no mutable state. Numeric constants persist in generated DTBs and are applied by the S3C64xx pinctrl driver.

Dependencies and integration: used by S3C64xx board DTS files such as mini6410 and smdk6410 builds. It follows Samsung pinctrl binding conventions but with the S3C64xx-specific EINT encoding.

Risks and test signals: a mismatch between function value and hardware register encoding breaks GPIO/peripheral muxing. Test S3C64xx DTB compilation and validate external interrupt and pull-up/down behavior on supported boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/s3c64xx-pinctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/s5pv210-pinctrl.h -->
## sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/s5pv210-pinctrl.h

Purpose: this binding header defines S5PV210 pinctrl constants for DTS files.

Important API surface: it exports pull constants, power-down mode constants, drive-strength levels `S5PV210_PIN_DRV_LV1` through `LV4`, mux function constants input/output/function 2 through 6, and external interrupt alias `S5PV210_PIN_FUNC_F` equal to `S5PV210_PIN_FUNC_EINT` (`0xf`).

Control flow: none. The preprocessor turns symbolic pinctrl values into numeric cells in generated DTBs.

State and persistence: constants only. Values persist in board DTBs and are applied during pinctrl state configuration, including power-down modes.

Dependencies and integration: used by S5PV210 board DTS files listed in the Samsung Makefile and by the Samsung pinctrl binding/parser for that SoC family.

Risks and test signals: drive-strength encodings are not monotonic in source order (`LV2` is 2 and `LV3` is 1), so casual edits can invert electrical behavior. Test DTB builds, schema validation, and board checks for external interrupts, sleep pin states, and bus signal integrity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/s5pv210-pinctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/sigmastar/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm/boot/dts/sigmastar/Makefile

Purpose: this Kbuild fragment lists SigmaStar/MStar ARMv7 DTBs.

Important API surface: `dtb-$(CONFIG_ARCH_MSTARV7)` adds eight board DTBs, including infinity/infinity2m/infinity3 and mercury5 targets such as BreadBee, 100ask DongshanPi One, Miyoo Mini, WirelessTag IDO SBC, SSD201HTV2, UnitV2, and Midrive D08.

Control flow: Kbuild conditionally appends targets for `CONFIG_ARCH_MSTARV7`.

State and persistence: no runtime state. The file persists the list of buildable SigmaStar/MStar device trees.

Dependencies and integration: depends on matching DTS files and the parent ARM DTS build. Generated artifacts integrate with board-specific bootloader DTB selection.

Risks and test signals: target names are long and product-specific, so spelling drift is the primary risk. Test with MStarV7 enabled and verify all eight DTBs compile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/sigmastar/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/socionext/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm/boot/dts/socionext/Makefile

Purpose: this Makefile lists Socionext Milbeaut and UniPhier ARM DTBs.

Important API surface: `dtb-$(CONFIG_ARCH_MILBEAUT)` adds `milbeaut-m10v-evb.dtb`. `dtb-$(CONFIG_ARCH_UNIPHIER)` adds 10 UniPhier boards: LD4, LD6b, Pro4, Pro5, PXs2, and SLD8 reference/evaluation variants.

Control flow: Kbuild appends targets based on the two architecture config symbols. There are no overlay composition rules.

State and persistence: no mutable state. The persistent behavior is build inclusion of the listed DTBs.

Dependencies and integration: depends on same-directory DTS files and shared Socionext DTSI includes. Parent ARM DTS Kbuild consumes the fragment.

Risks and test signals: risk is limited to missing or stale target names and incorrect config gating. Test `make dtbs` for Milbeaut and UniPhier configs and ensure all listed sources exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/socionext/Makefile -->
