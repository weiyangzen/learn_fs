# Research: subset-b-005818

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/nvidia,tegra264.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/nvidia,tegra264.h

Purpose: declares the device-tree clock IDs for NVIDIA Tegra264 BPMP-managed clocks. It exports 458 macro constants, mainly `TEGRA264_CLK_*`, spanning numeric IDs 1..467; the set covers PLLs, CPU/cluster roots, memory/display/video/audio blocks, PCIe/UPHY, GPU, MGBE, and DPAUX identifiers.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 458 exported defines, numeric range 1..467, first numeric symbols `TEGRA264_CLK_OSC`=1, `TEGRA264_CLK_CLK_S`=2, `TEGRA264_CLK_JTAG_REG`=3, `TEGRA264_CLK_SPLL`=4, `TEGRA264_CLK_SPLL_OUT0`=5, and last numeric symbols `TEGRA264_CLK_MGBE0_RX_SER`=463, `TEGRA264_CLK_MGBE1_RX_SER`=464, `TEGRA264_CLK_MGBE2_RX_SER`=465, `TEGRA264_CLK_MGBE3_RX_SER`=466, `TEGRA264_CLK_DPAUX`=467. Dominant macro prefixes are `TEGRA264`(458); common suffix categories are `M`(62), `IN`(23), `DIV`(19), `REF`(15), `CORE`(12), `SYNC`(10), `TX`(9), `SER`(8). Source section markers include `Copyright (c) 2022-2025, NVIDIA CORPORATION. All rights reserved.`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs are consumed by Tegra device trees and the Tegra BPMP clock provider path under `drivers/clk/tegra/clk-bpmp.c`, where firmware-facing clock numbers must match BPMP firmware and binding documentation.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `DT_BINDINGS_CLOCK_NVIDIA_TEGRA264_H` should remain unique enough to avoid accidental include suppression. Since the file has no executable validation, errors usually appear as boot-time probe failures, missing clocks, or devices stuck in reset.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include BPMP firmware accepting all requested IDs, Tegra264 platform devices acquiring clock handles, and no firmware `invalid clock id` errors during PCIe, display, GPU, audio, and networking bring-up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/nvidia,tegra264.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/nxp,imx94-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/nxp,imx94-clock.h

Purpose: declares i.MX9 block-controller clock selector/gate IDs for `nxp,imx94-clock.h`. It is intentionally compact, exporting 2 macros in local block namespaces such as VPUBLK, CAMBLK, DISPMIX, or NETCMIX; values span 0..0 and are reused per block because each provider interprets the index in its own clock domain.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 2 exported defines, numeric range 0..0, first numeric symbols `IMX94_CLK_DISPMIX_CLK_SEL`=0, `IMX94_CLK_DISPMIX_LVDS_CLK_GATE`=0, and last numeric symbols `IMX94_CLK_DISPMIX_CLK_SEL`=0, `IMX94_CLK_DISPMIX_LVDS_CLK_GATE`=0. Dominant macro prefixes are `IMX94`(2); common suffix categories are `GATE`(1), `SEL`(1). Source section markers include no named comment sections.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs integrate with i.MX block-control clock drivers, especially `drivers/clk/imx/clk-imx95-blk-ctl.c`, and with NETC/display/camera block-controller device-tree bindings.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `__DT_BINDINGS_CLOCK_IMX94_H` should remain unique enough to avoid accidental include suppression. Repeated numeric values are intentional across separate block-local namespaces, so tests and reviews must validate provider domain selection rather than global uniqueness.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include i.MX9 block-control provider probe, display/camera/NETC clock consumers resolving block-local indexes, and no accidental reliance on global uniqueness of small integer IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/nxp,imx94-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/nxp,imx95-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/nxp,imx95-clock.h

Purpose: declares i.MX9 block-controller clock selector/gate IDs for `nxp,imx95-clock.h`. It is intentionally compact, exporting 17 macros in local block namespaces such as VPUBLK, CAMBLK, DISPMIX, or NETCMIX; values span 0..4 and are reused per block because each provider interprets the index in its own clock domain.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 17 exported defines, numeric range 0..4, first numeric symbols `IMX95_CLK_VPUBLK_WAVE`=0, `IMX95_CLK_VPUBLK_JPEG_ENC`=1, `IMX95_CLK_VPUBLK_JPEG_DEC`=2, `IMX95_CLK_CAMBLK_CSI2_FOR0`=0, `IMX95_CLK_CAMBLK_CSI2_FOR1`=1, and last numeric symbols `IMX95_CLK_DISPMIX_PIX_DI1_GATE`=4, `IMX95_CLK_DISPMIX_ENG0_SEL`=0, `IMX95_CLK_DISPMIX_ENG1_SEL`=1, `IMX95_CLK_NETCMIX_ENETC0_RMII`=0, `IMX95_CLK_NETCMIX_ENETC1_RMII`=1. Dominant macro prefixes are `IMX95`(17); common suffix categories are `GATE`(4), `RMII`(2), `SEL`(2), `AXI`(1), `DEC`(1), `DIV`(1), `ENC`(1), `FOR0`(1). Source section markers include no named comment sections.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs integrate with i.MX block-control clock drivers, especially `drivers/clk/imx/clk-imx95-blk-ctl.c`, and with NETC/display/camera block-controller device-tree bindings.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `__DT_BINDINGS_CLOCK_IMX95_H` should remain unique enough to avoid accidental include suppression. Repeated numeric values are intentional across separate block-local namespaces, so tests and reviews must validate provider domain selection rather than global uniqueness.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include i.MX9 block-control provider probe, display/camera/NETC clock consumers resolving block-local indexes, and no accidental reliance on global uniqueness of small integer IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/nxp,imx95-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/omap4.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/omap4.h

Purpose: maps OMAP clock-control register offsets into DT clock specifier indexes. It defines 96 macros plus register-index helpers; most exported `*_CLKCTRL` values are computed by subtracting the clock-control base offset, not by assigning opaque clock IDs.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 96 exported defines, numeric range 0..440, first numeric symbols `OMAP4_CLKCTRL_OFFSET`=32, `OMAP4_MPU_CLKCTRL`=0, `OMAP4_DSP_CLKCTRL`=0, `OMAP4_L4_ABE_CLKCTRL`=0, `OMAP4_AESS_CLKCTRL`=8, and last numeric symbols `OMAP4_GPIO1_CLKCTRL`=24, `OMAP4_TIMER1_CLKCTRL`=32, `OMAP4_COUNTER_32K_CLKCTRL`=48, `OMAP4_KBD_CLKCTRL`=88, `OMAP4_DEBUGSS_CLKCTRL`=0. Dominant macro prefixes are `OMAP4`(96); common suffix categories are `CLKCTRL`(94), `OFFSET`(2). Source section markers include `mpuss clocks`, `tesla clocks`, `abe clocks`, `l4_ao clocks`, `l3_1 clocks`, `l3_2 clocks`, `ducati clocks`, `l3_dma clocks`, `l3_emif clocks`, `d2d clocks`, `l4_cfg clocks`, `l3_instr clocks`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The constants integrate with TI OMAP clock-control providers and OMAP DTS nodes that specify module clockctrl offsets. The `CLKCTRL_INDEX()` convention must match PRCM register maps and OMAP clock data.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `__DT_BINDINGS_CLK_OMAP4_H` should remain unique enough to avoid accidental include suppression. The computed offset macros are especially sensitive to base-offset changes; a wrong `CLKCTRL_OFFSET` or secure-clock base shifts every derived index.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include OMAP PRCM clockctrl providers registering each module clock, remoteproc/display/DMA/MMC/USB devices probing, and no shifted offset lookups in clock debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/omap4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/omap5.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/omap5.h

Purpose: maps OMAP clock-control register offsets into DT clock specifier indexes. It defines 86 macros plus register-index helpers; most exported `*_CLKCTRL` values are computed by subtracting the clock-control base offset, not by assigning opaque clock IDs.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 86 exported defines, numeric range 0..440, first numeric symbols `OMAP5_CLKCTRL_OFFSET`=32, `OMAP5_MPU_CLKCTRL`=0, `OMAP5_MMU_DSP_CLKCTRL`=0, `OMAP5_L4_ABE_CLKCTRL`=0, `OMAP5_AESS_CLKCTRL`=8, and last numeric symbols `OMAP5_WD_TIMER2_CLKCTRL`=16, `OMAP5_GPIO1_CLKCTRL`=24, `OMAP5_TIMER1_CLKCTRL`=32, `OMAP5_COUNTER_32K_CLKCTRL`=48, `OMAP5_KBD_CLKCTRL`=88. Dominant macro prefixes are `OMAP5`(86); common suffix categories are `CLKCTRL`(84), `OFFSET`(2). Source section markers include `mpu clocks`, `dsp clocks`, `abe clocks`, `l3main1 clocks`, `l3main2 clocks`, `ipu clocks`, `dma clocks`, `emif clocks`, `l4cfg clocks`, `l3instr clocks`, `l4per clocks`, `l4_secure clocks`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The constants integrate with TI OMAP clock-control providers and OMAP DTS nodes that specify module clockctrl offsets. The `CLKCTRL_INDEX()` convention must match PRCM register maps and OMAP clock data.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `__DT_BINDINGS_CLK_OMAP5_H` should remain unique enough to avoid accidental include suppression. The computed offset macros are especially sensitive to base-offset changes; a wrong `CLKCTRL_OFFSET` or secure-clock base shifts every derived index.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include OMAP PRCM clockctrl providers registering each module clock, remoteproc/display/DMA/MMC/USB devices probing, and no shifted offset lookups in clock debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/omap5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/pistachio-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/pistachio-clk.h

Purpose: publishes the Imagination Pistachio clock-controller IDs for PLLs, fixed-factor clocks, gates, dividers, muxes, peripheral clocks, system clocks, and external input gates. It exports 149 macros with several independent ID spaces and `*_NR_CLKS` sentinels.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 149 exported defines, numeric range 0..113, first numeric symbols `CLK_MIPS_PLL`=0, `CLK_AUDIO_PLL`=1, `CLK_RPU_V_PLL`=2, `CLK_RPU_L_PLL`=3, `CLK_SYS_PLL`=4, and last numeric symbols `SYS_CLK_HASH`=27, `SYS_CLK_NR_CLKS`=28, `EXT_CLK_AUDIO_IN`=0, `EXT_CLK_ENET_IN`=1, `EXT_CLK_NR_CLKS`=2. Dominant macro prefixes are `CLK`(87), `PERIPH`(35), `SYS`(24), `EXT`(3); common suffix categories are `DIV`(51), `MUX`(17), `PLL`(7), `IN`(6), `CLKS`(4), `OUT`(3), `TIMER`(3), `ADC`(2). Source section markers include `PLLs`, `Fixed-factor clocks`, `Gate clocks`, `Divider clocks`, `Mux clocks`, `Peripheral gate clocks`, `Peripheral divider clocks`, `System gate clocks`, `Gates for external input clocks`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The header is included by `arch/mips/boot/dts/img/pistachio.dtsi` and matches the providers under `drivers/clk/pistachio/`, including the core, peripheral, system, and external clock domains.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLOCK_PISTACHIO_H` should remain unique enough to avoid accidental include suppression. Since the file has no executable validation, errors usually appear as boot-time probe failures, missing clocks, or devices stuck in reset.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include Pistachio MIPS DTS boot, provider registration for core/peripheral/system/external domains, audio/network/USB/MMC clock consumers probing, and `*_NR_CLKS` matching provider array sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/pistachio-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/px30-cru.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/px30-cru.h

Purpose: defines Rockchip PX30 CRU clock and soft-reset specifier IDs. It exports 350 macros across PLL/core clocks, SCLK/HCLK/PCLK/ACLK gates, power-domain clocks, and `SRST_*` reset IDs; numeric values span 0..353 with gaps matching hardware/reset bank layout.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 350 exported defines, numeric range 0..353, first numeric symbols `PLL_APLL`=1, `PLL_DPLL`=2, `PLL_CPLL`=3, `PLL_NPLL`=4, `APLL_BOOST_H`=5, and last numeric symbols `SRST_GPIO2_P`=183, `SRST_GPIO3_P`=184, `SRST_SGRF_P`=185, `SRST_GRF_P`=186, `SRST_I2S0_RX`=191. Dominant macro prefixes are `SRST`(178), `SCLK`(80), `PCLK`(37), `HCLK`(25), `ACLK`(18), `PLL`(5), `APLL`(2), `DCLK`(2); common suffix categories are `P`(48), `H`(31), `A`(22), `PRE`(11), `PMU`(8), `OUT`(6), `DIV`(5), `ISP`(5). Source section markers include `core clocks`, `sclk gates (special clocks)`, `dclk gates`, `aclk gates`, `hclk gates`, `pclk gates`, `pmu-clocks indices`, `soft-reset indices`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The constants map to `drivers/clk/rockchip/clk-px30.c`, Rockchip CRU DTS clock/reset specifiers, and reset-controller consumers using the shared CRU provider.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_ROCKCHIP_PX30_H` should remain unique enough to avoid accidental include suppression. Clock and reset IDs coexist in one header, so edits must avoid colliding semantic domains while preserving bank gaps used by the CRU provider.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include PX30 CRU probe, clock/reset consumers resolving their phandles, stable peripheral boot for UART/I2C/MMC/GMAC/GPU/VOP, and reset IDs operating through the CRU reset controller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/px30-cru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/pxa-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/pxa-clock.h

Purpose: defines legacy PXA2xx/PXA3xx clock IDs consumed by PXA clock providers and device-tree users. It exports 63 contiguous `CLK_*` IDs from `CLK_NONE` through `CLK_MAX`, covering UARTs, SSP/I2C/I2S, LCD, memory, GPIO, USB, MMC, camera, timers, and board-specific functional clocks.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 63 exported defines, numeric range 0..62, first numeric symbols `CLK_NONE`=0, `CLK_1WIRE`=1, `CLK_AC97`=2, `CLK_AC97CONF`=3, `CLK_ASSP`=4, and last numeric symbols `CLK_USIM`=58, `CLK_USIM1`=59, `CLK_USMI0`=60, `CLK_OSC32k768`=61, `CLK_MAX`=62. Dominant macro prefixes are `CLK`(63); common suffix categories are `GCU`(2), `IM`(2), `LCD`(2), `1WIRE`(1), `AC97`(1), `AC97CONF`(1), `ASSP`(1), `BOOT`(1). Source section markers include no named comment sections.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs are shared by PXA DTS users and the PXA clock drivers in `drivers/clk/pxa/`, preserving compatibility with older board and SoC clock naming.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `__DT_BINDINGS_CLOCK_PXA2XX_H__` should remain unique enough to avoid accidental include suppression. Since the file has no executable validation, errors usually appear as boot-time probe failures, missing clocks, or devices stuck in reset.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include provider probe success and expected entries in common-clock debugfs output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/pxa-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,apss-ipq.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,apss-ipq.h

Purpose: declares Qualcomm IPQ APSS/L3 clock IDs for CPU alias/core and L3 clock providers. It exports 8 contiguous constants used by `apss-ipq6018` style providers and CPU/NOC consumers.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 8 exported defines, numeric range 0..7, first numeric symbols `APCS_ALIAS0_CLK_SRC`=0, `APCS_ALIAS0_CORE_CLK`=1, `APSS_PLL_EARLY`=2, `APSS_SILVER_CLK_SRC`=3, `APSS_SILVER_CORE_CLK`=4, and last numeric symbols `APSS_SILVER_CLK_SRC`=3, `APSS_SILVER_CORE_CLK`=4, `L3_PLL`=5, `L3_CLK_SRC`=6, `L3_CORE_CLK`=7. Dominant macro prefixes are `APSS`(3), `L3`(3), `APCS`(2); common suffix categories are `CLK`(3), `SRC`(3), `EARLY`(1), `PLL`(1). Source section markers include no named comment sections.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs match Qualcomm APSS clock providers such as `drivers/clk/qcom/apss-ipq6018.c` and CPU/L3 consumers in IPQ DTS files.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLOCK_QCA_APSS_IPQ6018_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,apss-ipq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,camcc-sc7180.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,camcc-sc7180.h

Purpose: declares Qualcomm camera clock-controller binding IDs for `qcom,camcc-sc7180.h`. It exports 106 generated-style macros for PLL outputs, camera NOC/CCI/ICP/IPE/BPS/TFE/IFE/LRME/JPEG/MCLK clocks, reset lines, and camera power domains where present.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 106 exported defines, numeric range 0..78, first numeric symbols `CAM_CC_PLL2_OUT_EARLY`=0, `CAM_CC_PLL0`=1, `CAM_CC_PLL1`=2, `CAM_CC_PLL2`=3, `CAM_CC_PLL2_OUT_AUX`=4, and last numeric symbols `CAM_CC_MCLK1_BCR`=17, `CAM_CC_MCLK2_BCR`=18, `CAM_CC_MCLK3_BCR`=19, `CAM_CC_MCLK4_BCR`=20, `CAM_CC_TITAN_TOP_BCR`=21. Dominant macro prefixes are `CAM`(101), `IFE`(2), `BPS`(1), `IPE`(1), `TITAN`(1); common suffix categories are `CLK`(48), `SRC`(25), `BCR`(22), `GDSC`(5), `AUX`(1), `EARLY`(1), `PLL0`(1), `PLL1`(1). Source section markers include `CAM_CC clocks`, `CAM_CC power domains`, `CAM_CC resets`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/camcc-sc7180.c` or the nearest SoC-specific camera clock provider, and with camera DT nodes that use `clocks`/`resets`/`power-domains` specifiers.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_QCOM_CAM_CC_SC7180_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,camcc-sc7180.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,camcc-sc7280.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,camcc-sc7280.h

Purpose: declares Qualcomm camera clock-controller binding IDs for `qcom,camcc-sc7280.h`. It exports 114 generated-style macros for PLL outputs, camera NOC/CCI/ICP/IPE/BPS/TFE/IFE/LRME/JPEG/MCLK clocks, reset lines, and camera power domains where present.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 114 exported defines, numeric range 0..107, first numeric symbols `CAM_CC_PLL0`=0, `CAM_CC_PLL0_OUT_EVEN`=1, `CAM_CC_PLL0_OUT_ODD`=2, `CAM_CC_PLL1`=3, `CAM_CC_PLL1_OUT_EVEN`=4, and last numeric symbols `CAM_CC_IFE_0_GDSC`=1, `CAM_CC_IFE_1_GDSC`=2, `CAM_CC_IFE_2_GDSC`=3, `CAM_CC_IPE_0_GDSC`=4, `CAM_CC_TITAN_TOP_GDSC`=5. Dominant macro prefixes are `CAM`(114); common suffix categories are `CLK`(57), `SRC`(34), `EVEN`(6), `GDSC`(6), `ODD`(2), `AUX`(1), `AUX2`(1), `PLL0`(1). Source section markers include `CAM_CC clocks`, `CAM_CC power domains`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/camcc-sc7280.c` or the nearest SoC-specific camera clock provider, and with camera DT nodes that use `clocks`/`resets`/`power-domains` specifiers.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_QCOM_CAM_CC_SC7280_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,camcc-sc7280.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,camcc-sdm845.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,camcc-sdm845.h

Purpose: declares Qualcomm camera clock-controller binding IDs for `qcom,camcc-sdm845.h`. It exports 101 generated-style macros for PLL outputs, camera NOC/CCI/ICP/IPE/BPS/TFE/IFE/LRME/JPEG/MCLK clocks, reset lines, and camera power domains where present.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 101 exported defines, numeric range 0..84, first numeric symbols `CAM_CC_BPS_AHB_CLK`=0, `CAM_CC_BPS_AREG_CLK`=1, `CAM_CC_BPS_AXI_CLK`=2, `CAM_CC_BPS_CLK`=3, `CAM_CC_BPS_CLK_SRC`=4, and last numeric symbols `IPE_0_GDSC`=1, `IPE_1_GDSC`=2, `IFE_0_GDSC`=3, `IFE_1_GDSC`=4, `TITAN_TOP_GDSC`=5. Dominant macro prefixes are `CAM`(85), `TITAN`(11), `IFE`(2), `IPE`(2), `BPS`(1); common suffix categories are `CLK`(52), `SRC`(25), `BCR`(10), `GDSC`(6), `EVEN`(4), `PLL0`(1), `PLL1`(1), `PLL2`(1). Source section markers include `CAM_CC clock registers`, `CAM_CC Resets`, `CAM_CC GDSCRs`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/camcc-sdm845.c` or the nearest SoC-specific camera clock provider, and with camera DT nodes that use `clocks`/`resets`/`power-domains` specifiers.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_SDM_CAM_CC_SDM845_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,camcc-sdm845.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,camcc-sm8250.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,camcc-sm8250.h

Purpose: declares Qualcomm camera clock-controller binding IDs for `qcom,camcc-sm8250.h`. It exports 123 generated-style macros for PLL outputs, camera NOC/CCI/ICP/IPE/BPS/TFE/IFE/LRME/JPEG/MCLK clocks, reset lines, and camera power domains where present.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 123 exported defines, numeric range 0..110, first numeric symbols `CAM_CC_BPS_AHB_CLK`=0, `CAM_CC_BPS_AREG_CLK`=1, `CAM_CC_BPS_AXI_CLK`=2, `CAM_CC_BPS_CLK`=3, `CAM_CC_BPS_CLK_SRC`=4, and last numeric symbols `IPE_0_GDSC`=1, `SBI_GDSC`=2, `IFE_0_GDSC`=3, `IFE_1_GDSC`=4, `TITAN_TOP_GDSC`=5. Dominant macro prefixes are `CAM`(117), `IFE`(2), `BPS`(1), `IPE`(1), `SBI`(1), `TITAN`(1); common suffix categories are `CLK`(66), `SRC`(34), `BCR`(6), `GDSC`(6), `EVEN`(4), `MAIN`(1), `ODD`(1), `PLL0`(1). Source section markers include `CAM_CC clocks`, `CAM_CC resets`, `CAM_CC GDSCRs`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/camcc-sm8250.c` or the nearest SoC-specific camera clock provider, and with camera DT nodes that use `clocks`/`resets`/`power-domains` specifiers.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_QCOM_CAM_CC_SM8250_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,camcc-sm8250.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-qcm2290.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-qcm2290.h

Purpose: declares Qualcomm display clock-controller binding IDs for `qcom,dispcc-qcm2290.h`. It exports 23 macros for MDSS AHB/AXI/core/byte/ESC/DP/pixel/VSYNC clocks, display resets, and MDSS GDSC domains where present.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 23 exported defines, numeric range 0..20, first numeric symbols `DISP_CC_PLL0`=0, `DISP_CC_MDSS_AHB_CLK`=1, `DISP_CC_MDSS_AHB_CLK_SRC`=2, `DISP_CC_MDSS_BYTE0_CLK`=3, `DISP_CC_MDSS_BYTE0_CLK_SRC`=4, and last numeric symbols `DISP_CC_SLEEP_CLK_SRC`=18, `DISP_CC_XO_CLK`=19, `DISP_CC_XO_CLK_SRC`=20, `MDSS_GDSC`=0, `DISP_CC_MDSS_CORE_BCR`=0. Dominant macro prefixes are `DISP`(22), `MDSS`(1); common suffix categories are `CLK`(11), `SRC`(9), `BCR`(1), `GDSC`(1), `PLL0`(1). Source section markers include `DISP_CC clocks`, `GDSCs`, `Resets`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/dispcc-qcm2290.c` or the matching display clock provider, plus MDSS/DSI/DP/display-controller DTS and YAML binding examples.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_QCOM_DISP_CC_QCM2290_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-qcm2290.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-sc7180.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-sc7180.h

Purpose: declares Qualcomm display clock-controller binding IDs for `qcom,dispcc-sc7180.h`. It exports 36 macros for MDSS AHB/AXI/core/byte/ESC/DP/pixel/VSYNC clocks, display resets, and MDSS GDSC domains where present.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 36 exported defines, numeric range 0..32, first numeric symbols `DISP_CC_PLL0`=0, `DISP_CC_PLL0_OUT_EVEN`=1, `DISP_CC_MDSS_AHB_CLK`=2, `DISP_CC_MDSS_AHB_CLK_SRC`=3, `DISP_CC_MDSS_BYTE0_CLK`=4, and last numeric symbols `DISP_CC_MDSS_VSYNC_CLK_SRC`=31, `DISP_CC_XO_CLK`=32, `DISP_CC_MDSS_CORE_BCR`=0, `DISP_CC_MDSS_RSCC_BCR`=1, `MDSS_GDSC`=0. Dominant macro prefixes are `DISP`(35), `MDSS`(1); common suffix categories are `CLK`(18), `SRC`(13), `BCR`(2), `EVEN`(1), `GDSC`(1), `PLL0`(1). Source section markers include `Clocks`, `Resets`, `GDSCs`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/dispcc-sc7180.c` or the matching display clock provider, plus MDSS/DSI/DP/display-controller DTS and YAML binding examples.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_QCOM_DISP_CC_SC7180_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-sc7180.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-sc7280.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-sc7280.h

Purpose: declares Qualcomm display clock-controller binding IDs for `qcom,dispcc-sc7280.h`. It exports 44 macros for MDSS AHB/AXI/core/byte/ESC/DP/pixel/VSYNC clocks, display resets, and MDSS GDSC domains where present.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 44 exported defines, numeric range 0..40, first numeric symbols `DISP_CC_PLL0`=0, `DISP_CC_MDSS_AHB_CLK`=1, `DISP_CC_MDSS_AHB_CLK_SRC`=2, `DISP_CC_MDSS_BYTE0_CLK`=3, `DISP_CC_MDSS_BYTE0_CLK_SRC`=4, and last numeric symbols `DISP_CC_SLEEP_CLK`=39, `DISP_CC_XO_CLK`=40, `DISP_CC_MDSS_CORE_GDSC`=0, `DISP_CC_MDSS_CORE_BCR`=0, `DISP_CC_MDSS_RSCC_BCR`=1. Dominant macro prefixes are `DISP`(44); common suffix categories are `CLK`(23), `SRC`(17), `BCR`(2), `GDSC`(1), `PLL0`(1). Source section markers include `DISP_CC clocks`, `DISP_CC power domains`, `DISPCC resets`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/dispcc-sc7280.c` or the matching display clock provider, plus MDSS/DSI/DP/display-controller DTS and YAML binding examples.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_QCOM_DISP_CC_SC7280_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-sc7280.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-sc8280xp.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-sc8280xp.h

Purpose: declares Qualcomm display clock-controller binding IDs for `qcom,dispcc-sc8280xp.h`. It exports 85 macros for MDSS AHB/AXI/core/byte/ESC/DP/pixel/VSYNC clocks, display resets, and MDSS GDSC domains where present.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 85 exported defines, numeric range 0..80, first numeric symbols `DISP_CC_PLL0`=0, `DISP_CC_PLL1`=1, `DISP_CC_PLL1_OUT_EVEN`=2, `DISP_CC_PLL2`=3, `DISP_CC_MDSS_AHB1_CLK`=4, and last numeric symbols `DISP_CC_XO_CLK_SRC`=80, `DISP_CC_MDSS_CORE_BCR`=0, `DISP_CC_MDSS_RSCC_BCR`=1, `MDSS_GDSC`=0, `MDSS_INT2_GDSC`=1. Dominant macro prefixes are `DISP`(83), `MDSS`(2); common suffix categories are `CLK`(44), `SRC`(33), `BCR`(2), `GDSC`(2), `EVEN`(1), `PLL0`(1), `PLL1`(1), `PLL2`(1). Source section markers include `DISPCC clocks`, `DISPCC resets`, `DISPCC GDSCs`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/dispcc-sc8280xp.c` or the matching display clock provider, plus MDSS/DSI/DP/display-controller DTS and YAML binding examples.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_QCOM_DISP_CC_SC8280XP_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-sc8280xp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-sdm845.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-sdm845.h

Purpose: declares Qualcomm display clock-controller binding IDs for `qcom,dispcc-sdm845.h`. It exports 41 macros for MDSS AHB/AXI/core/byte/ESC/DP/pixel/VSYNC clocks, display resets, and MDSS GDSC domains where present.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 41 exported defines, numeric range 0..38, first numeric symbols `DISP_CC_MDSS_AHB_CLK`=0, `DISP_CC_MDSS_AXI_CLK`=1, `DISP_CC_MDSS_BYTE0_CLK`=2, `DISP_CC_MDSS_BYTE0_CLK_SRC`=3, `DISP_CC_MDSS_BYTE0_INTF_CLK`=4, and last numeric symbols `DISP_CC_MDSS_DP_PIXEL1_CLK_SRC`=36, `DISP_CC_MDSS_DP_PIXEL_CLK`=37, `DISP_CC_MDSS_DP_PIXEL_CLK_SRC`=38, `DISP_CC_MDSS_RSCC_BCR`=0, `MDSS_GDSC`=0. Dominant macro prefixes are `DISP`(40), `MDSS`(1); common suffix categories are `CLK`(22), `SRC`(16), `BCR`(1), `GDSC`(1), `PLL0`(1). Source section markers include `DISP_CC clock registers`, `DISP_CC Reset`, `DISP_CC GDSCR`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/dispcc-sdm845.c` or the matching display clock provider, plus MDSS/DSI/DP/display-controller DTS and YAML binding examples.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_SDM_DISP_CC_SDM845_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-sdm845.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-sm6125.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-sm6125.h

Purpose: declares Qualcomm display clock-controller binding IDs for `qcom,dispcc-sm6125.h`. It exports 30 macros for MDSS AHB/AXI/core/byte/ESC/DP/pixel/VSYNC clocks, display resets, and MDSS GDSC domains where present.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 30 exported defines, numeric range 0..27, first numeric symbols `DISP_CC_PLL0`=0, `DISP_CC_MDSS_AHB_CLK`=1, `DISP_CC_MDSS_AHB_CLK_SRC`=2, `DISP_CC_MDSS_BYTE0_CLK`=3, `DISP_CC_MDSS_BYTE0_CLK_SRC`=4, and last numeric symbols `DISP_CC_MDSS_VSYNC_CLK`=25, `DISP_CC_MDSS_VSYNC_CLK_SRC`=26, `DISP_CC_XO_CLK`=27, `DISP_CC_MDSS_CORE_BCR`=0, `MDSS_GDSC`=0. Dominant macro prefixes are `DISP`(29), `MDSS`(1); common suffix categories are `CLK`(16), `SRC`(11), `BCR`(1), `GDSC`(1), `PLL0`(1). Source section markers include `Clocks`, `Resets`, `GDSCs`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/dispcc-sm6125.c` or the matching display clock provider, plus MDSS/DSI/DP/display-controller DTS and YAML binding examples.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_QCOM_DISP_CC_SM6125_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-sm6125.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-sm6350.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-sm6350.h

Purpose: declares Qualcomm display clock-controller binding IDs for `qcom,dispcc-sm6350.h`. It exports 36 macros for MDSS AHB/AXI/core/byte/ESC/DP/pixel/VSYNC clocks, display resets, and MDSS GDSC domains where present.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 36 exported defines, numeric range 0..32, first numeric symbols `DISP_CC_PLL0`=0, `DISP_CC_MDSS_AHB_CLK`=1, `DISP_CC_MDSS_AHB_CLK_SRC`=2, `DISP_CC_MDSS_BYTE0_CLK`=3, `DISP_CC_MDSS_BYTE0_CLK_SRC`=4, and last numeric symbols `DISP_CC_SLEEP_CLK`=31, `DISP_CC_XO_CLK`=32, `DISP_CC_MDSS_CORE_BCR`=0, `DISP_CC_MDSS_RSCC_BCR`=1, `MDSS_GDSC`=0. Dominant macro prefixes are `DISP`(35), `MDSS`(1); common suffix categories are `CLK`(19), `SRC`(13), `BCR`(2), `GDSC`(1), `PLL0`(1). Source section markers include `DISP_CC clocks`, `Resets`, `GDSCs`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/dispcc-sm6350.c` or the matching display clock provider, plus MDSS/DSI/DP/display-controller DTS and YAML binding examples.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_QCOM_DISP_CC_SM6350_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-sm6350.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-sm8150.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-sm8150.h

Purpose: declares Qualcomm display clock-controller binding IDs for `qcom,dispcc-sm8150.h`. It exports 61 macros for MDSS AHB/AXI/core/byte/ESC/DP/pixel/VSYNC clocks, display resets, and MDSS GDSC domains where present.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 61 exported defines, numeric range 0..57, first numeric symbols `DISP_CC_MDSS_AHB_CLK`=0, `DISP_CC_MDSS_AHB_CLK_SRC`=1, `DISP_CC_MDSS_BYTE0_CLK`=2, `DISP_CC_MDSS_BYTE0_CLK_SRC`=3, `DISP_CC_MDSS_BYTE0_DIV_CLK_SRC`=4, and last numeric symbols `DISP_CC_MDSS_EDP_PIXEL_CLK_SRC`=56, `DISP_CC_MDSS_EDP_LINK_DIV_CLK_SRC`=57, `DISP_CC_MDSS_CORE_BCR`=0, `DISP_CC_MDSS_RSCC_BCR`=1, `MDSS_GDSC`=0. Dominant macro prefixes are `DISP`(60), `MDSS`(1); common suffix categories are `CLK`(30), `SRC`(26), `BCR`(2), `GDSC`(1), `PLL0`(1), `PLL1`(1). Source section markers include `DISP_CC clock registers`, `DISP_CC Reset`, `DISP_CC GDSCR`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/dispcc-sm8150.c` or the matching display clock provider, plus MDSS/DSI/DP/display-controller DTS and YAML binding examples.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_QCOM_DISP_CC_SM8250_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-sm8150.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-sm8250.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-sm8250.h

Purpose: declares Qualcomm display clock-controller binding IDs for `qcom,dispcc-sm8250.h`. It exports 61 macros for MDSS AHB/AXI/core/byte/ESC/DP/pixel/VSYNC clocks, display resets, and MDSS GDSC domains where present.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 61 exported defines, numeric range 0..57, first numeric symbols `DISP_CC_MDSS_AHB_CLK`=0, `DISP_CC_MDSS_AHB_CLK_SRC`=1, `DISP_CC_MDSS_BYTE0_CLK`=2, `DISP_CC_MDSS_BYTE0_CLK_SRC`=3, `DISP_CC_MDSS_BYTE0_DIV_CLK_SRC`=4, and last numeric symbols `DISP_CC_MDSS_EDP_PIXEL_CLK_SRC`=56, `DISP_CC_MDSS_EDP_LINK_DIV_CLK_SRC`=57, `DISP_CC_MDSS_CORE_BCR`=0, `DISP_CC_MDSS_RSCC_BCR`=1, `MDSS_GDSC`=0. Dominant macro prefixes are `DISP`(60), `MDSS`(1); common suffix categories are `CLK`(30), `SRC`(26), `BCR`(2), `GDSC`(1), `PLL0`(1), `PLL1`(1). Source section markers include `DISP_CC clock registers`, `DISP_CC Reset`, `DISP_CC GDSCR`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/dispcc-sm8250.c` or the matching display clock provider, plus MDSS/DSI/DP/display-controller DTS and YAML binding examples.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_QCOM_DISP_CC_SM8250_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-sm8250.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-sm8350.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-sm8350.h

Purpose: declares Qualcomm display clock-controller binding IDs for `qcom,dispcc-sm8350.h`. It exports 61 macros for MDSS AHB/AXI/core/byte/ESC/DP/pixel/VSYNC clocks, display resets, and MDSS GDSC domains where present.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 61 exported defines, numeric range 0..57, first numeric symbols `DISP_CC_MDSS_AHB_CLK`=0, `DISP_CC_MDSS_AHB_CLK_SRC`=1, `DISP_CC_MDSS_BYTE0_CLK`=2, `DISP_CC_MDSS_BYTE0_CLK_SRC`=3, `DISP_CC_MDSS_BYTE0_DIV_CLK_SRC`=4, and last numeric symbols `DISP_CC_MDSS_EDP_PIXEL_CLK_SRC`=56, `DISP_CC_MDSS_EDP_LINK_DIV_CLK_SRC`=57, `DISP_CC_MDSS_CORE_BCR`=0, `DISP_CC_MDSS_RSCC_BCR`=1, `MDSS_GDSC`=0. Dominant macro prefixes are `DISP`(60), `MDSS`(1); common suffix categories are `CLK`(30), `SRC`(26), `BCR`(2), `GDSC`(1), `PLL0`(1), `PLL1`(1). Source section markers include `DISP_CC clock registers`, `DISP_CC Reset`, `DISP_CC GDSCR`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/dispcc-sm8350.c` or the matching display clock provider, plus MDSS/DSI/DP/display-controller DTS and YAML binding examples.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_QCOM_DISP_CC_SM8250_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dispcc-sm8350.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dsi-phy-28nm.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dsi-phy-28nm.h

Purpose: declares the tiny Qualcomm 28 nm DSI PHY PLL clock ID ABI. It exports 2 constants identifying byte and pixel PLL outputs exposed by the DSI PHY clock provider.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 2 exported defines, numeric range 0..1, first numeric symbols `DSI_BYTE_PLL_CLK`=0, `DSI_PIXEL_PLL_CLK`=1, and last numeric symbols `DSI_BYTE_PLL_CLK`=0, `DSI_PIXEL_PLL_CLK`=1. Dominant macro prefixes are `DSI`(2); common suffix categories are `CLK`(2). Source section markers include no named comment sections.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs are used by Qualcomm DSI PHY and display stack bindings to refer to byte and pixel PLL outputs created by the 28 nm PHY provider.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_QCOM_DSI_PHY_28NM_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,dsi-phy-28nm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,eliza-dispcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,eliza-dispcc.h

Purpose: declares Qualcomm Eliza-family clock-controller binding IDs for `qcom,eliza-dispcc.h`. It exports 103 macros for a generated-style provider namespace, including controller clocks plus reset or GDSC IDs where present.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 103 exported defines, numeric range 0..97, first numeric symbols `DISP_CC_PLL0`=0, `DISP_CC_PLL1`=1, `DISP_CC_PLL2`=2, `DISP_CC_ESYNC0_CLK`=3, `DISP_CC_ESYNC0_CLK_SRC`=4, and last numeric symbols `DISP_CC_MDSS_CORE_BCR`=0, `DISP_CC_MDSS_CORE_INT2_BCR`=1, `DISP_CC_MDSS_RSCC_BCR`=2, `MDSS_GDSC`=0, `MDSS_INT2_GDSC`=1. Dominant macro prefixes are `DISP`(101), `MDSS`(2); common suffix categories are `CLK`(56), `SRC`(39), `BCR`(3), `GDSC`(2), `PLL0`(1), `PLL1`(1), `PLL2`(1). Source section markers include `DISP_CC clocks`, `DISP_CC resets`, `DISP_CC GDSCR`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The macros align with Qualcomm display clock provider sources for the Eliza platform and DTS display nodes requesting MDSS/DP/DSI clocks.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_QCOM_ELIZA_DISP_CC_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,eliza-dispcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,eliza-gcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,eliza-gcc.h

Purpose: declares Qualcomm Eliza-family clock-controller binding IDs for `qcom,eliza-gcc.h`. It exports 195 macros for a generated-style provider namespace, including controller clocks plus reset or GDSC IDs where present.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 195 exported defines, numeric range 0..151, first numeric symbols `GCC_AGGRE_NOC_PCIE_AXI_CLK`=0, `GCC_AGGRE_UFS_PHY_AXI_CLK`=1, `GCC_AGGRE_USB3_PRIM_AXI_CLK`=2, `GCC_BOOT_ROM_AHB_CLK`=3, `GCC_CAM_BIST_MCLK_AHB_CLK`=4, and last numeric symbols `GCC_USB3PHY_PHY_PRIM_BCR`=30, `GCC_USB3PHY_PHY_SEC_BCR`=31, `GCC_VIDEO_AXI0_CLK_ARES`=32, `GCC_VIDEO_AXI1_CLK_ARES`=33, `GCC_VIDEO_BCR`=34. Dominant macro prefixes are `GCC`(195); common suffix categories are `CLK`(100), `SRC`(46), `BCR`(33), `GDSC`(8), `ARES`(2), `EVEN`(1), `GPLL0`(1), `GPLL4`(1). Source section markers include `GCC clocks`, `GCC power domains`, `GCC resets`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The macros align with `drivers/clk/qcom/gcc-eliza.c` and platform DTS nodes for global bus, storage, USB, PCIe, camera, display, video, and reset resources.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_QCOM_GCC_ELIZA_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,eliza-gcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,eliza-tcsr.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,eliza-tcsr.h

Purpose: declares Qualcomm Eliza-family clock-controller binding IDs for `qcom,eliza-tcsr.h`. It exports 6 macros for a generated-style provider namespace, including controller clocks plus reset or GDSC IDs where present.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 6 exported defines, numeric range 0..5, first numeric symbols `TCSR_HDMI_CLKREF_EN`=0, `TCSR_PCIE_0_CLKREF_EN`=1, `TCSR_PCIE_1_CLKREF_EN`=2, `TCSR_UFS_CLKREF_EN`=3, `TCSR_USB2_CLKREF_EN`=4, and last numeric symbols `TCSR_PCIE_0_CLKREF_EN`=1, `TCSR_PCIE_1_CLKREF_EN`=2, `TCSR_UFS_CLKREF_EN`=3, `TCSR_USB2_CLKREF_EN`=4, `TCSR_USB3_CLKREF_EN`=5. Dominant macro prefixes are `TCSR`(6); common suffix categories are `EN`(6). Source section markers include `TCSR_CC clocks`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The macros align with Eliza TCSR clock-reference provider data and DTS nodes that gate external clock references.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_QCOM_TCSR_CC_ELIZA_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,eliza-tcsr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-apq8084.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-apq8084.h

Purpose: declares Qualcomm global clock-controller binding IDs for `qcom,gcc-apq8084.h`. It exports 338 macros covering GPLLs and bus/peripheral clocks plus reset lines and GDSC power domains where supported.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 338 exported defines, numeric range 0..333, first numeric symbols `GPLL0`=0, `GPLL0_VOTE`=1, `GPLL1`=2, `GPLL1_VOTE`=3, `GPLL2`=4, and last numeric symbols `GCC_MMSS_GPLL0_CLK_SRC`=333, `USB_HS_HSIC_GDSC`=0, `PCIE0_GDSC`=1, `PCIE1_GDSC`=2, `USB30_GDSC`=3. Dominant macro prefixes are `GCC`(239), `BLSP1`(18), `BLSP2`(18), `USB`(7), `USB30`(5), `PCIE`(4), `QDSS`(4), `SATA`(4); common suffix categories are `CLK`(237), `SRC`(86), `VOTE`(5), `GDSC`(4), `GPLL0`(1), `GPLL1`(1), `GPLL2`(1), `GPLL3`(1). Source section markers include `gdscs`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/gcc-apq8084.c` or the matching GCC provider and with SoC DTS nodes for UART, BLSP/QUP, SDCC, USB, PCIe, UFS, camera/display/video, modem, crypto, and NOC clocks.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_APQ_GCC_8084_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-apq8084.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-ipq4019.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-ipq4019.h

Purpose: declares Qualcomm global clock-controller binding IDs for `qcom,gcc-ipq4019.h`. It exports 154 macros covering GPLLs and bus/peripheral clocks plus reset lines and GDSC power domains where supported.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 154 exported defines, numeric range 0..77, first numeric symbols `GCC_DUMMY_CLK`=0, `AUDIO_CLK_SRC`=1, `BLSP1_QUP1_I2C_APPS_CLK_SRC`=2, `BLSP1_QUP1_SPI_APPS_CLK_SRC`=3, `BLSP1_QUP2_I2C_APPS_CLK_SRC`=4, and last numeric symbols `ESS_MAC2_ARES`=73, `ESS_MAC3_ARES`=74, `ESS_MAC4_ARES`=75, `ESS_MAC5_ARES`=76, `ESS_PSGMII_ARES`=77. Dominant macro prefixes are `GCC`(104), `PCIE`(12), `ESS`(7), `BLSP1`(6), `WIFI0`(6), `WIFI1`(6), `USB3`(3), `USB2`(2); common suffix categories are `CLK`(56), `BCR`(42), `ARES`(23), `SRC`(18), `RESET`(13), `VCO`(2). Source section markers include no named comment sections.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/gcc-ipq4019.c` or the matching GCC provider and with SoC DTS nodes for UART, BLSP/QUP, SDCC, USB, PCIe, UFS, camera/display/video, modem, crypto, and NOC clocks.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `__QCOM_CLK_IPQ4019_H__` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-ipq4019.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-ipq5018.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-ipq5018.h

Purpose: declares Qualcomm global clock-controller binding IDs for `qcom,gcc-ipq5018.h`. It exports 174 macros covering GPLLs and bus/peripheral clocks plus reset lines and GDSC power domains where supported.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 174 exported defines, numeric range 0..173, first numeric symbols `GPLL0_MAIN`=0, `GPLL0`=1, `GPLL2_MAIN`=2, `GPLL2`=3, `GPLL4_MAIN`=4, and last numeric symbols `GCC_USB0_PIPE_CLK`=169, `GMAC0_RX_DIV_CLK_SRC`=170, `GMAC0_TX_DIV_CLK_SRC`=171, `GMAC1_RX_DIV_CLK_SRC`=172, `GMAC1_TX_DIV_CLK_SRC`=173. Dominant macro prefixes are `GCC`(119), `BLSP1`(8), `USB0`(5), `GMAC0`(4), `GMAC1`(4), `QDSS`(4), `PCIE0`(3), `PCIE1`(3); common suffix categories are `CLK`(117), `SRC`(49), `MAIN`(4), `GPLL0`(1), `GPLL2`(1), `GPLL4`(1), `PLL`(1). Source section markers include no named comment sections.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/gcc-ipq5018.c` or the matching GCC provider and with SoC DTS nodes for UART, BLSP/QUP, SDCC, USB, PCIe, UFS, camera/display/video, modem, crypto, and NOC clocks.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLOCK_IPQ_GCC_5018_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-ipq5018.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-ipq6018.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-ipq6018.h

Purpose: declares Qualcomm global clock-controller binding IDs for `qcom,gcc-ipq6018.h`. It exports 253 macros covering GPLLs and bus/peripheral clocks plus reset lines and GDSC power domains where supported.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 253 exported defines, numeric range 0..252, first numeric symbols `GPLL0`=0, `UBI32_PLL`=1, `GPLL6`=2, `GPLL4`=3, `PCNOC_BFDCD_CLK_SRC`=4, and last numeric symbols `GCC_QDSS_STM_CLK`=248, `GCC_QDSS_TRACECLKIN_CLK`=249, `QDSS_STM_CLK_SRC`=250, `QDSS_TRACECLKIN_CLK_SRC`=251, `GCC_NSSNOC_ATB_CLK`=252. Dominant macro prefixes are `GCC`(164), `NSS`(27), `BLSP1`(18), `PCIE0`(5), `QDSS`(4), `USB0`(4), `APSS`(3), `LPASS`(3); common suffix categories are `CLK`(163), `SRC`(78), `MAIN`(6), `PLL`(2), `GPLL0`(1), `GPLL2`(1), `GPLL4`(1), `GPLL6`(1). Source section markers include no named comment sections.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/gcc-ipq6018.c` or the matching GCC provider and with SoC DTS nodes for UART, BLSP/QUP, SDCC, USB, PCIe, UFS, camera/display/video, modem, crypto, and NOC clocks.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLOCK_IPQ_GCC_6018_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-ipq6018.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-ipq806x.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-ipq806x.h

Purpose: declares Qualcomm global clock-controller binding IDs for `qcom,gcc-ipq806x.h`. It exports 280 macros covering GPLLs and bus/peripheral clocks plus reset lines and GDSC power domains where supported.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 280 exported defines, numeric range 0..287, first numeric symbols `AFAB_CLK_SRC`=0, `QDSS_STM_CLK`=1, `SCSS_A_CLK`=2, `SCSS_H_CLK`=3, `AFAB_CORE_CLK`=4, and last numeric symbols `NSSTCM_CLK_SRC`=282, `NSSTCM_CLK`=283, `CE5_A_CLK_SRC`=285, `CE5_H_CLK_SRC`=286, `CE5_CORE_CLK_SRC`=287. Dominant macro prefixes are `SFAB`(29), `PCIE`(18), `USB`(15), `SPDM`(13), `AFAB`(11), `EBI1`(9), `GMAC`(8), `QDSS`(8); common suffix categories are `CLK`(186), `SRC`(60), `FCLK`(20), `VOTE`(5), `PLL0`(1), `PLL10`(1), `PLL11`(1), `PLL12`(1). Source section markers include no named comment sections.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/gcc-ipq806x.c` or the matching GCC provider and with SoC DTS nodes for UART, BLSP/QUP, SDCC, USB, PCIe, UFS, camera/display/video, modem, crypto, and NOC clocks.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_GCC_IPQ806X_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-ipq806x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-ipq8074.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-ipq8074.h

Purpose: declares Qualcomm global clock-controller binding IDs for `qcom,gcc-ipq8074.h`. It exports 376 macros covering GPLLs and bus/peripheral clocks plus reset lines and GDSC power domains where supported.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 376 exported defines, numeric range 0..227, first numeric symbols `GPLL0`=0, `GPLL0_MAIN`=1, `GCC_SLEEP_CLK_SRC`=2, `BLSP1_QUP1_I2C_APPS_CLK_SRC`=3, `BLSP1_QUP1_SPI_APPS_CLK_SRC`=4, and last numeric symbols `GCC_NSSPORT4_RESET`=143, `GCC_NSSPORT5_RESET`=144, `GCC_NSSPORT6_RESET`=145, `USB0_GDSC`=0, `USB1_GDSC`=1. Dominant macro prefixes are `GCC`(287), `NSS`(35), `BLSP1`(18), `USB0`(5), `USB1`(5), `PCIE0`(3), `PCIE1`(3), `GPLL0`(2); common suffix categories are `CLK`(138), `BCR`(89), `SRC`(78), `ARES`(39), `RESET`(14), `MAIN`(6), `ENABLE`(4), `GDSC`(2). Source section markers include no named comment sections.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/gcc-ipq8074.c` or the matching GCC provider and with SoC DTS nodes for UART, BLSP/QUP, SDCC, USB, PCIe, UFS, camera/display/video, modem, crypto, and NOC clocks.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLOCK_IPQ_GCC_8074_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-ipq8074.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-mdm9607.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-mdm9607.h

Purpose: declares Qualcomm global clock-controller binding IDs for `qcom,gcc-mdm9607.h`. It exports 92 macros covering GPLLs and bus/peripheral clocks plus reset lines and GDSC power domains where supported.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 92 exported defines, numeric range 0..86, first numeric symbols `GPLL0`=0, `GPLL0_EARLY`=1, `GPLL1`=2, `GPLL1_VOTE`=3, `GPLL2`=4, and last numeric symbols `USB2_HS_PHY_ONLY_BCR`=0, `QUSB2_PHY_BCR`=1, `GCC_MSS_RESTART`=2, `USB_HS_HSIC_BCR`=3, `USB_HS_BCR`=4. Dominant macro prefixes are `GCC`(49), `BLSP1`(18), `BIMC`(3), `USB`(3), `APSS`(2), `GPLL0`(2), `GPLL1`(2), `GPLL2`(2); common suffix categories are `CLK`(45), `SRC`(34), `BCR`(4), `EARLY`(2), `VOTE`(2), `GPLL0`(1), `GPLL1`(1), `GPLL2`(1). Source section markers include `Resets`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/gcc-mdm9607.c` or the matching GCC provider and with SoC DTS nodes for UART, BLSP/QUP, SDCC, USB, PCIe, UFS, camera/display/video, modem, crypto, and NOC clocks.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_MSM_GCC_9607_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-mdm9607.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-mdm9615.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-mdm9615.h

Purpose: declares Qualcomm global clock-controller binding IDs for `qcom,gcc-mdm9615.h`. It exports 309 macros covering GPLLs and bus/peripheral clocks plus reset lines and GDSC power domains where supported.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 309 exported defines, numeric range 0..309, first numeric symbols `AFAB_CLK_SRC`=0, `AFAB_CORE_CLK`=1, `SFAB_MSS_Q6_SW_A_CLK`=2, `SFAB_MSS_Q6_FW_A_CLK`=3, `QDSS_STM_CLK`=4, and last numeric symbols `CE3_H_CLK`=305, `USB_HS1_SYSTEM_CLK_SRC`=306, `USB_HS1_SYSTEM_CLK`=307, `EBI2_CLK`=308, `EBI2_AON_CLK`=309. Dominant macro prefixes are `SFAB`(32), `USB`(27), `SPDM`(12), `AFAB`(11), `EBI1`(9), `DFAB`(8), `QDSS`(8), `SATA`(7); common suffix categories are `CLK`(209), `SRC`(63), `FCLK`(18), `VOTE`(8), `PLL0`(1), `PLL10`(1), `PLL11`(1), `PLL12`(1). Source section markers include no named comment sections.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/gcc-mdm9615.c` or the matching GCC provider and with SoC DTS nodes for UART, BLSP/QUP, SDCC, USB, PCIe, UFS, camera/display/video, modem, crypto, and NOC clocks.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_MDM_GCC_9615_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-mdm9615.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8660.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8660.h

Purpose: declares Qualcomm global clock-controller binding IDs for `qcom,gcc-msm8660.h`. It exports 258 macros covering GPLLs and bus/peripheral clocks plus reset lines and GDSC power domains where supported.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 258 exported defines, numeric range 0..257, first numeric symbols `AFAB_CLK_SRC`=0, `AFAB_CORE_CLK`=1, `SCSS_A_CLK`=2, `SCSS_H_CLK`=3, `SCSS_XO_SRC_CLK`=4, and last numeric symbols `PLL8_VOTE`=253, `PLL9`=254, `PLL10`=255, `PLL11`=256, `PLL12`=257. Dominant macro prefixes are `SFAB`(28), `USB`(14), `SPDM`(12), `AFAB`(11), `DFAB`(8), `GSBI1`(6), `GSBI10`(6), `GSBI11`(6); common suffix categories are `CLK`(174), `SRC`(55), `FCLK`(17), `VOTE`(3), `HCLK`(1), `PLL0`(1), `PLL10`(1), `PLL11`(1). Source section markers include no named comment sections.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/gcc-msm8660.c` or the matching GCC provider and with SoC DTS nodes for UART, BLSP/QUP, SDCC, USB, PCIe, UFS, camera/display/video, modem, crypto, and NOC clocks.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_MSM_GCC_8660_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8660.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8909.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8909.h

Purpose: declares Qualcomm global clock-controller binding IDs for `qcom,gcc-msm8909.h`. It exports 195 macros covering GPLLs and bus/peripheral clocks plus reset lines and GDSC power domains where supported.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 195 exported defines, numeric range 0..147, first numeric symbols `GPLL0_EARLY`=0, `GPLL0`=1, `GPLL1`=2, `GPLL1_VOTE`=3, `GPLL2_EARLY`=4, and last numeric symbols `MDSS_GDSC`=0, `OXILI_GDSC`=1, `VENUS_GDSC`=2, `VENUS_CORE0_GDSC`=3, `VFE_GDSC`=4. Dominant macro prefixes are `GCC`(133), `BLSP1`(14), `ULTAUDIO`(5), `BIMC`(4), `CAMSS`(3), `GPLL0`(2), `GPLL1`(2), `GPLL2`(2); common suffix categories are `CLK`(91), `SRC`(49), `BCR`(41), `GDSC`(5), `EARLY`(3), `GPLL0`(1), `GPLL1`(1), `GPLL2`(1). Source section markers include `PLLs`, `RCGs`, `Voteable Clocks`, `Branches`, `Resets`, `Subsystem Restart`, `Power Domains`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/gcc-msm8909.c` or the matching GCC provider and with SoC DTS nodes for UART, BLSP/QUP, SDCC, USB, PCIe, UFS, camera/display/video, modem, crypto, and NOC clocks.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_QCOM_GCC_8909_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8909.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8916.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8916.h

Purpose: declares Qualcomm global clock-controller binding IDs for `qcom,gcc-msm8916.h`. It exports 167 macros covering GPLLs and bus/peripheral clocks plus reset lines and GDSC power domains where supported.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 167 exported defines, numeric range 0..160, first numeric symbols `GPLL0`=0, `GPLL0_VOTE`=1, `BIMC_PLL`=2, `BIMC_PLL_VOTE`=3, `GPLL1`=4, and last numeric symbols `VENUS_GDSC`=1, `MDSS_GDSC`=2, `JPEG_GDSC`=3, `VFE_GDSC`=4, `OXILI_GDSC`=5. Dominant macro prefixes are `GCC`(99), `BLSP1`(14), `BIMC`(5), `ULTAUDIO`(5), `CAMSS`(3), `APSS`(2), `GPLL0`(2), `GPLL1`(2); common suffix categories are `CLK`(99), `SRC`(54), `GDSC`(6), `VOTE`(4), `GPLL0`(1), `GPLL1`(1), `GPLL2`(1), `PLL`(1). Source section markers include `Indexes for GDSCs`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/gcc-msm8916.c` or the matching GCC provider and with SoC DTS nodes for UART, BLSP/QUP, SDCC, USB, PCIe, UFS, camera/display/video, modem, crypto, and NOC clocks.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_MSM_GCC_8916_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8916.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8917.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8917.h

Purpose: declares Qualcomm global clock-controller binding IDs for `qcom,gcc-msm8917.h`. It exports 198 macros covering GPLLs and bus/peripheral clocks plus reset lines and GDSC power domains where supported.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 198 exported defines, numeric range 0..182, first numeric symbols `APSS_AHB_CLK_SRC`=0, `BLSP1_QUP2_I2C_APPS_CLK_SRC`=1, `BLSP1_QUP2_SPI_APPS_CLK_SRC`=2, `BLSP1_QUP3_I2C_APPS_CLK_SRC`=3, `BLSP1_QUP3_SPI_APPS_CLK_SRC`=4, and last numeric symbols `VENUS_CORE0_GDSC`=4, `VENUS_GDSC`=5, `VFE0_GDSC`=6, `VFE1_GDSC`=7, `MSM8937_OXILI_CX_GDSC`=8. Dominant macro prefixes are `GCC`(114), `MSM8937`(17), `BLSP1`(8), `BLSP2`(8), `CAMSS`(3), `GPLL0`(3), `CPP`(2), `GPLL3`(2); common suffix categories are `CLK`(118), `SRC`(57), `GDSC`(9), `BCR`(6), `EARLY`(4), `GPLL0`(1), `GPLL3`(1), `GPLL4`(1). Source section markers include `Clocks`, `Addtional MSM8937-specific clocks`, `GCC block resets`, `GDSCs`, `Additional MSM8937-specific GDSCs`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/gcc-msm8917.c` or the matching GCC provider and with SoC DTS nodes for UART, BLSP/QUP, SDCC, USB, PCIe, UFS, camera/display/video, modem, crypto, and NOC clocks.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_MSM_GCC_8917_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8917.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8939.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8939.h

Purpose: declares Qualcomm global clock-controller binding IDs for `qcom,gcc-msm8939.h`. It exports 201 macros covering GPLLs and bus/peripheral clocks plus reset lines and GDSC power domains where supported.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 201 exported defines, numeric range 0..192, first numeric symbols `GPLL0`=0, `GPLL0_VOTE`=1, `BIMC_PLL`=2, `BIMC_PLL_VOTE`=3, `GPLL1`=4, and last numeric symbols `JPEG_GDSC`=3, `VFE_GDSC`=4, `OXILI_GDSC`=5, `VENUS_CORE0_GDSC`=6, `VENUS_CORE1_GDSC`=7. Dominant macro prefixes are `GCC`(116), `BLSP1`(14), `BIMC`(5), `ULTAUDIO`(5), `CAMSS`(3), `USB`(3), `VENUS`(3), `APSS`(2); common suffix categories are `CLK`(116), `SRC`(61), `GDSC`(8), `VOTE`(8), `GPLL0`(1), `GPLL1`(1), `GPLL2`(1), `GPLL3`(1). Source section markers include `Indexes for GDSCs`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/gcc-msm8939.c` or the matching GCC provider and with SoC DTS nodes for UART, BLSP/QUP, SDCC, USB, PCIe, UFS, camera/display/video, modem, crypto, and NOC clocks.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_MSM_GCC_8939_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8939.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8953.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8953.h

Purpose: declares Qualcomm global clock-controller binding IDs for `qcom,gcc-msm8953.h`. It exports 226 macros covering GPLLs and bus/peripheral clocks plus reset lines and GDSC power domains where supported.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 226 exported defines, numeric range 0..205, first numeric symbols `APC0_DROOP_DETECTOR_CLK_SRC`=0, `APC1_DROOP_DETECTOR_CLK_SRC`=1, `APSS_AHB_CLK_SRC`=2, `BLSP1_QUP1_I2C_APPS_CLK_SRC`=3, `BLSP1_QUP1_SPI_APPS_CLK_SRC`=4, and last numeric symbols `USB30_GDSC`=5, `VENUS_CORE0_GDSC`=6, `VENUS_GDSC`=7, `VFE0_GDSC`=8, `VFE1_GDSC`=9. Dominant macro prefixes are `GCC`(140), `BLSP1`(10), `BLSP2`(10), `CAMSS`(3), `USB30`(3), `CPP`(2), `GPLL0`(2), `GPLL2`(2); common suffix categories are `CLK`(130), `SRC`(66), `BCR`(10), `GDSC`(10), `EARLY`(5), `GPLL0`(1), `GPLL2`(1), `GPLL3`(1). Source section markers include `Clocks`, `GCC block resets`, `GDSCs`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/gcc-msm8953.c` or the matching GCC provider and with SoC DTS nodes for UART, BLSP/QUP, SDCC, USB, PCIe, UFS, camera/display/video, modem, crypto, and NOC clocks.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_MSM_GCC_8953_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8953.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8960.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8960.h

Purpose: declares Qualcomm global clock-controller binding IDs for `qcom,gcc-msm8960.h`. It exports 307 macros covering GPLLs and bus/peripheral clocks plus reset lines and GDSC power domains where supported.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 307 exported defines, numeric range 0..307, first numeric symbols `AFAB_CLK_SRC`=0, `AFAB_CORE_CLK`=1, `SFAB_MSS_Q6_SW_A_CLK`=2, `SFAB_MSS_Q6_FW_A_CLK`=3, `QDSS_STM_CLK`=4, and last numeric symbols `CE3_SRC`=303, `CE3_CORE_CLK`=304, `CE3_H_CLK`=305, `PLL16`=306, `PLL17`=307. Dominant macro prefixes are `SFAB`(32), `USB`(25), `SPDM`(12), `AFAB`(11), `EBI1`(9), `DFAB`(8), `QDSS`(8), `SATA`(7); common suffix categories are `CLK`(206), `SRC`(62), `FCLK`(18), `VOTE`(8), `PLL0`(1), `PLL10`(1), `PLL11`(1), `PLL12`(1). Source section markers include no named comment sections.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/gcc-msm8960.c` or the matching GCC provider and with SoC DTS nodes for UART, BLSP/QUP, SDCC, USB, PCIe, UFS, camera/display/video, modem, crypto, and NOC clocks.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_MSM_GCC_8960_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8960.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8974.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8974.h

Purpose: declares Qualcomm global clock-controller binding IDs for `qcom,gcc-msm8974.h`. It exports 307 macros covering GPLLs and bus/peripheral clocks plus reset lines and GDSC power domains where supported.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 307 exported defines, numeric range 0..305, first numeric symbols `GPLL0`=0, `GPLL0_VOTE`=1, `CONFIG_NOC_CLK_SRC`=2, `GPLL2`=3, `GPLL2_VOTE`=4, and last numeric symbols `GPLL4`=302, `GPLL4_VOTE`=303, `GCC_SDCC1_CDCCAL_SLEEP_CLK`=304, `GCC_SDCC1_CDCCAL_FF_CLK`=305, `USB_HS_HSIC_GDSC`=0. Dominant macro prefixes are `GCC`(225), `BLSP1`(18), `BLSP2`(18), `USB`(5), `QDSS`(4), `BIMC`(3), `GPLL0`(2), `GPLL1`(2); common suffix categories are `CLK`(193), `SRC`(74), `ENA`(28), `VOTE`(5), `GDSC`(1), `GPLL0`(1), `GPLL1`(1), `GPLL2`(1). Source section markers include `gdscs`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/gcc-msm8974.c` or the matching GCC provider and with SoC DTS nodes for UART, BLSP/QUP, SDCC, USB, PCIe, UFS, camera/display/video, modem, crypto, and NOC clocks.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_MSM_GCC_8974_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8974.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8976.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8976.h

Purpose: declares Qualcomm global clock-controller binding IDs for `qcom,gcc-msm8976.h`. It exports 225 macros covering GPLLs and bus/peripheral clocks plus reset lines and GDSC power domains where supported.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 225 exported defines, numeric range 0..203, first numeric symbols `GPLL0`=0, `GPLL2`=1, `GPLL3`=2, `GPLL4`=3, `GPLL6`=4, and last numeric symbols `VFE0_GDSC`=5, `VFE1_GDSC`=6, `CPP_GDSC`=7, `OXILI_GX_GDSC`=8, `OXILI_CX_GDSC`=9. Dominant macro prefixes are `GCC`(137), `RST`(11), `BLSP1`(10), `BLSP2`(10), `CAMSS`(3), `USB`(3), `VENUS`(3), `APS`(2); common suffix categories are `CLK`(132), `SRC`(67), `BCR`(11), `GDSC`(10), `GPLL0`(1), `GPLL2`(1), `GPLL3`(1), `GPLL4`(1). Source section markers include `GCC block resets`, `GDSCs`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/gcc-msm8976.c` or the matching GCC provider and with SoC DTS nodes for UART, BLSP/QUP, SDCC, USB, PCIe, UFS, camera/display/video, modem, crypto, and NOC clocks.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_MSM_GCC_8976_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8976.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8994.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8994.h

Purpose: declares Qualcomm global clock-controller binding IDs for `qcom,gcc-msm8994.h`. It exports 164 macros covering GPLLs and bus/peripheral clocks plus reset lines and GDSC power domains where supported.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 164 exported defines, numeric range 0..152, first numeric symbols `GPLL0_EARLY`=0, `GPLL0`=1, `GPLL4_EARLY`=2, `GPLL4`=3, `UFS_AXI_CLK_SRC`=4, and last numeric symbols `USB3PHY_PHY_RESET`=1, `PCIE_PHY_0_RESET`=2, `PCIE_PHY_1_RESET`=3, `QUSB2_PHY_RESET`=4, `MSS_RESET`=5. Dominant macro prefixes are `GCC`(86), `BLSP1`(18), `BLSP2`(18), `PCIE`(11), `GPLL0`(4), `UFS`(3), `USB30`(3), `GPLL4`(2); common suffix categories are `CLK`(86), `SRC`(57), `RESET`(6), `GDSC`(5), `LDO`(4), `EARLY`(2), `GPLL0`(1), `GPLL4`(1). Source section markers include `GDSCs`, `Resets`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/gcc-msm8994.c` or the matching GCC provider and with SoC DTS nodes for UART, BLSP/QUP, SDCC, USB, PCIe, UFS, camera/display/video, modem, crypto, and NOC clocks.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_MSM_GCC_8994_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8994.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8996.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8996.h

Purpose: declares Qualcomm global clock-controller binding IDs for `qcom,gcc-msm8996.h`. It exports 345 macros covering GPLLs and bus/peripheral clocks plus reset lines and GDSC power domains where supported.

Important APIs/types/functions: there are no C functions, structs, or inline helpers beyond preprocessor definitions. The public API is the macro set itself: 345 exported defines, numeric range 0..229, first numeric symbols `GPLL0_EARLY`=0, `GPLL0`=1, `GPLL1_EARLY`=2, `GPLL1`=3, `GPLL2_EARLY`=4, and last numeric symbols `USB30_GDSC`=4, `PCIE0_GDSC`=5, `PCIE1_GDSC`=6, `PCIE2_GDSC`=7, `UFS_GDSC`=8. Dominant macro prefixes are `GCC`(261), `BLSP1`(18), `BLSP2`(18), `HLOS1`(3), `HMSS`(3), `UFS`(3), `USB30`(3), `BIMC`(2); common suffix categories are `CLK`(154), `BCR`(105), `SRC`(66), `GDSC`(9), `EARLY`(5), `GPLL0`(1), `GPLL1`(1), `GPLL2`(1). Source section markers include `Indexes for GDSCs`.

Control flow: this header has no runtime control flow. At build time it is included by DTS/DTSI, binding examples, or matching clock-controller provider code so integer macros replace literal clock specifier cells. At boot, the device-tree core passes those integers to the provider's `of_clk_hw_onecell_get`, reset-controller, or power-domain lookup path; the provider then indexes static tables or firmware calls that live outside this header.

State and persistence: the file owns no mutable state and persists nothing. Its constants are persistent ABI once they are compiled into DTBs, kernel drivers, or out-of-tree device trees. That ABI character is the main state concern: old DTBs can continue to use these IDs against newer kernels, so additions should append or fill documented gaps without changing existing meanings.

Dependencies and integration points: The IDs must stay synchronized with `drivers/clk/qcom/gcc-msm8996.c` or the matching GCC provider and with SoC DTS nodes for UART, BLSP/QUP, SDCC, USB, PCIe, UFS, camera/display/video, modem, crypto, and NOC clocks.

Risks: The primary risk is ABI drift: these integer constants are part of compiled DTB/kernel/provider contracts, so renumbering, reusing a value in the wrong domain, or moving a macro across domains can silently bind a consumer to the wrong clock, reset, or power domain. Header guard `_DT_BINDINGS_CLK_MSM_GCC_8996_H` should remain unique enough to avoid accidental include suppression. Qualcomm generated-style headers often contain multiple domains in one file: clock IDs, reset IDs ending in `BCR`/`RESET`/`ARES`, and GDSC IDs. Provider array order and `num_*` counts are the key review points.

Test signals: Compile checks should include `dt_binding_check`, `dtbs_check`, and an SoC defconfig build that includes both DTS users and the matching clock provider. Runtime signals include successful provider probe, `clk_summary` showing expected names/rates, display/camera/GCC consumers acquiring all clocks, reset-controller operations succeeding, and GDSC domains toggling without `-ENOENT` or probe deferral loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,gcc-msm8996.h -->
