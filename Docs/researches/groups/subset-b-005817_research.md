# subset-b-005817 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt7988-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt7988-clk.h

Purpose: Defines the Device Tree clock IDs for the MediaTek MT7988 clock controllers. It is an ABI header consumed by DTS files and the MT7988 clock drivers, not an implementation unit.

Important APIs, types, and functions: Exports preprocessor constants for APMIXEDSYS PLLs, TOPCKGEN roots and muxes, MCUSYS selectors, infrastructure clocks, ETHDMA, SGMII instances, ETHWARP, and XFIPLL. There are no C types or callable functions.

Control flow: No runtime control flow exists here. Runtime clock lookup is driven by numeric IDs passed through `clocks` phandles; provider drivers index their clock descriptor tables with these values.

State and persistence: The constants are persistent DT ABI. Reordering or renumbering changes the meaning of compiled device trees.

Dependencies and integration points: Integrates with `mediatek,mt7988-*` clock-controller bindings, MediaTek common clock drivers, and Ethernet, PCIe, USB, audio, PWM, and SGMII consumers.

Risks and test signals: Main risks are duplicate IDs, mismatched `*_NR_CLK` sentinel values, and clock names that do not match provider table order. Test with `dtbs_check`, MT7988 boot logs, clk summary inspection, and peripheral probe coverage for PCIe, USB, Ethernet/WED, SGMII, PWM, and audio.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt7988-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt8188-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt8188-clk.h

Purpose: Provides the public clock-ID namespace for MediaTek MT8188, covering the top clock generator and many multimedia, peripheral, image, display, and video clock domains.

Important APIs, types, and functions: Defines `CLK_TOP_*`, `CLK_INFRA_AO_*`, `CLK_APMIXED_*`, `CLK_AUDIODSP_*`, `CLK_PERI_AO_*`, I2C wrapper, MFG, VPP, WPE, image, DIP, VDEC, VENC, CAM, CCI, IPE, MDP, VDO0, and VDO1 IDs. No structs or functions are declared.

Control flow: The header only assigns integer IDs. Clock providers use those IDs as array indexes or lookup keys when processing DT clock specifiers.

State and persistence: Values form a stable DT/kernel ABI and persist in built DTBs. The file stores no runtime state.

Dependencies and integration points: Used by MT8188 DTS/DTSI files, clock-controller YAML schemas, MediaTek clock drivers, and consumers such as display, camera, video codec, IOMMU/SMI, I2C, audio DSP, and GPU drivers.

Risks and test signals: Risks include domain-crossing ID mistakes, stale sentinels, and broken display/video pipelines from swapped VPP/VDO clocks. Test with DT binding validation, boot-time clock registration warnings, `debugfs` clk tree checks, display bring-up, camera capture, codec encode/decode, audio DSP, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt8188-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt8196-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt8196-clock.h

Purpose: Defines the MT8196 Device Tree clock IDs for the main CKSYS/APMIXED domains plus low-power, peripheral, storage, PCIe/USB, display, overlay, MDP, image, video, and CPU PLL domains.

Important APIs, types, and functions: Exports many `CLK_TOP_*`, `CLK_APMIXED_*`, `CLK_TOP2_*`, `CLK_VLP_*`, `CLK_MM*`, `CLK_OVL*`, `CLK_MDP*`, `CLK_IMG*`, `CLK_VDEC*`, `CLK_VENC*`, and CPU PLL constants. It has no functions or data structures.

Control flow: No executable flow is present. Clock provider drivers interpret these numeric IDs when `of_clk_get()` resolves DT clock specifiers.

State and persistence: The definitions are ABI state for DTBs and must remain stable after publication. There is no memory or hardware state in the header.

Dependencies and integration points: Couples MT8196 DTS files to MediaTek CCF provider tables and to display, overlay, media, storage, PCIe, USB, I2C, and CPU frequency consumers.

Risks and test signals: MT8196 has many domains, so risks are sentinel drift, duplicate local numbering, and provider-table mismatches in new SoC support. Test with full `dtbs_check`, clock registration count checks, display/overlay pipelines, storage and PCIe enumeration, camera/video workloads, and CPU frequency or PLL-rate validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt8196-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt8365-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt8365-clk.h

Purpose: Supplies DT clock IDs for the MediaTek MT8365 SoC across top, infrastructure, peripheral, PLL, multimedia, camera, audio, MIPI CSI, MCU, MFG, VDEC, and APU domains.

Important APIs, types, and functions: Defines `CLK_TOP_*`, `CLK_IFR_*`, `CLK_PERI_*`, `CLK_APMIXED_*`, `CLK_GCE_*`, `CLK_AUD_*`, `CLK_MIPI_CSI*`, `CLK_MCU_*`, `CLK_MFG_*`, `CLK_MM_*`, `CLK_VDEC_*`, and `CLK_APU_*` constants. No callable APIs exist.

Control flow: No logic runs in this file. Its IDs are consumed as integer cells in DT `clocks` properties and resolved by MT8365 clock provider drivers.

State and persistence: Constant values are persistent DT ABI. Runtime enable, prepare, and rate state is stored by the common clock framework and provider drivers, not by the header.

Dependencies and integration points: Integrated with MT8365 DTS, MediaTek common clock infrastructure, and consumers for display, GPU, camera, audio, video decode, DMA/GCE, and APU hardware.

Risks and test signals: Risks include mixing similarly named MIPI CSI instances, APU/MFG clock mismatches, and incorrect `*_NR_CLK` limits. Test by validating DTBs, checking clk registration logs, and exercising display, CSI camera, audio playback/capture, GPU, video decode, and APU/accelerator probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mt8365-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mtmips-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mtmips-sysc.h

Purpose: Defines clock IDs for older Ralink/MediaTek MIPS system controllers: RT2880, RT305X, RT3352, RT3883, RT5350, MT7620, and MT76X8 families.

Important APIs, types, and functions: Exports SoC-prefixed IDs such as `RT2880_CLK_*`, `RT305X_CLK_*`, `RT3352_CLK_*`, `RT3883_CLK_*`, `RT5350_CLK_*`, `MT7620_CLK_*`, and `MT76X8_CLK_*`. There are no structures or functions.

Control flow: No code executes. The compatible-specific sysc/clock driver selects the appropriate ID table and maps DT clock specifiers to fixed, gate, or derived clocks.

State and persistence: Numeric IDs are stable binding ABI for MIPS router/access-point DTBs. Runtime clock state lives in the sysc driver and hardware registers.

Dependencies and integration points: Used by Ralink/MTMIPS DTS files and drivers for UART, I2C, SPI, Ethernet, PCI, USB, watchdog, timers, MMC, PCM/I2S, and Wi-Fi MAC blocks.

Risks and test signals: Main risks are cross-family ID confusion and missing peripherals on board variants. Test by compiling affected DTBs, booting representative SoCs, checking sysc clock provider registration, and validating serial console, Ethernet, USB, PCI, Wi-Fi, and timer/watchdog operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mtmips-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/meson8-ddr-clkc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/meson8-ddr-clkc.h

Purpose: Provides the minimal DT clock IDs for the Amlogic Meson8 DDR clock controller.

Important APIs, types, and functions: Defines `DDR_CLKID_DDR_PLL_DCO` and `DDR_CLKID_DDR_PLL`. No functions, structs, or macros with behavior are present.

Control flow: No control flow exists. Consumers and the DDR clock provider use the two IDs to identify the PLL DCO and PLL output.

State and persistence: These constants are the stable DT ABI for the DDR clock provider. Hardware state, rate programming, and parent selection are implemented in the Meson clock driver.

Dependencies and integration points: Included by Meson8 DT sources or bindings that reference DDR PLL clock specifiers. Integrates with the common clock framework and Amlogic Meson clock drivers.

Risks and test signals: Risks are small but ABI-sensitive: changing either value would silently point DT consumers at the wrong DDR clock. Test with DT compilation, Meson8 clock provider probe, DDR PLL rate reporting, memory stability tests, and absence of `of_clk_get()` failures for DDR-related nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/meson8-ddr-clkc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/meson8b-clkc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/meson8b-clkc.h

Purpose: Defines public clock IDs for the Amlogic Meson8b clock tree, including PLLs, fixed-factor clocks, muxes, gates, display/video clocks, audio clocks, and HDMI-related clocks.

Important APIs, types, and functions: Exports `CLKID_*` constants from core PLL outputs through peripheral gates and video paths, ending with HDMI PLL and VCLK enable identifiers. No functions or types are declared.

Control flow: The header is declarative. Meson clock drivers map these IDs to descriptors; DT consumers pass the IDs in clock specifiers.

State and persistence: The integer assignments are stable binding ABI. Runtime clock state is maintained by CCF clock objects and hardware registers.

Dependencies and integration points: Used by Meson8b DTS files, Amlogic clock-controller bindings, and consumers such as Ethernet, USB, MMC, HDMI, VPU, audio, Mali GPU, UART, I2C, and reset-related blocks.

Risks and test signals: Risks include gaps at low IDs, off-by-one provider table entries, and video/audio clock regressions from swapped IDs. Test with `dtbs_check`, clock summary ordering, HDMI/display bring-up, audio playback, MMC/USB/Ethernet probes, and rate checks for PLL-derived clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/meson8b-clkc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/microchip,lan966x.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/microchip,lan966x.h

Purpose: Defines DT clock IDs for the Microchip LAN966x clock controller, separating generated clock IDs and gate clocks.

Important APIs, types, and functions: Exports `GCK_ID_*` constants for QSPI, SDMMC, PI, MCAN, FLEXCOM, timer, and USB reference clocks, gate IDs such as `GCK_GATE_UHPHS`, `GCK_GATE_UDPHS`, `GCK_GATE_MCRAMC`, `GCK_GATE_HMATRIX`, and the `N_CLOCKS` count. No functions or types exist.

Control flow: No runtime flow is in the header. LAN966x provider code uses the IDs to register and look up generated/gated clocks.

State and persistence: IDs are persistent DT ABI. Gate state is in hardware registers and provider driver data.

Dependencies and integration points: Used by LAN966x DTS files and consumers for QSPI, SDMMC, CAN, FLEXCOM serial blocks, timers, USB, matrix, and RAM controller clocks.

Risks and test signals: Risks include mixing gate IDs with generator IDs and an incorrect `N_CLOCKS` bound. Test with `dtbs_check`, clock provider probe, and peripheral validation for QSPI, SDMMC, CAN, FLEXCOM UART/SPI/I2C modes, USB, and timer operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/microchip,lan966x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/microchip,mpfs-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/microchip,mpfs-clock.h

Purpose: Provides DT clock IDs for Microchip PolarFire SoC (MPFS), covering fabric-visible base clocks, peripheral gates, and Clock Conditioning Circuitry outputs.

Important APIs, types, and functions: Defines `CLK_CPU`, `CLK_AXI`, `CLK_AHB`, peripheral IDs for eNVM, MACs, MMC, timers, MMUART, SPI, I2C, CAN, USB, RTC, QSPI, GPIO, DDRC, FICs, ATHENA, CFM, a reserved MSS PLL hole, and `CLK_CCC_*` PLL/DLL outputs. No C functions are declared.

Control flow: Declarative only. The MPFS clock driver interprets DT IDs to expose common-clock-framework handles.

State and persistence: Numeric values are stable DT ABI. Runtime enable/rate state belongs to the clock provider and hardware.

Dependencies and integration points: Coupled to MPFS DTS, clock binding YAML, and consumers for networking, storage, serial, SPI/I2C, CAN, USB, RTC, FPGA fabric interfaces, and CCC-generated clocks.

Risks and test signals: Risks include the reserved ID 38 being accidentally reused and CCC output index mistakes. Test with DT validation, clock count checks, peripheral probe coverage, CCC output rate checks, and boot on boards using FPGA fabric and MSS peripherals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/microchip,mpfs-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/microchip,pic32-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/microchip,pic32-clock.h

Purpose: Defines clock output indices for Microchip PIC32 clock bindings.

Important APIs, types, and functions: Exports flat constants for oscillator, FRC, PLL, system, peripheral bus, reference, and USB PLL clocks, ending with `MAXCLKS`. There are no functions, structs, or stateful macros.

Control flow: No logic executes here. The PIC32 clock provider and DT consumers agree on clock index meanings through these defines.

State and persistence: The constants are binding ABI. Actual oscillator selection, divisors, and enable state are maintained by the PIC32 clock hardware and driver.

Dependencies and integration points: Used by PIC32 DTS files, clock-controller bindings, and consumers requiring system, peripheral bus, reference, or USB PLL clocks.

Risks and test signals: Risks are off-by-one `MAXCLKS`, renamed outputs that do not match provider arrays, and confusion between reference clocks and PB clocks. Test with DT compilation, provider registration, serial console, timers, USB, and peripheral bus consumers, plus clk debug output for expected oscillator parents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/microchip,pic32-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/microchip,sparx5.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/microchip,sparx5.h

Purpose: Supplies the DT clock IDs for Microchip Sparx5.

Important APIs, types, and functions: Defines `CLK_ID_CORE`, `CLK_ID_DDR`, `CLK_ID_CPU2`, `CLK_ID_ARM2`, `CLK_ID_AUX1` through `CLK_ID_AUX4`, `CLK_ID_SYNCE`, and `N_CLOCKS`. No functions or types are declared.

Control flow: There is no runtime control flow. Sparx5 clock provider code registers clocks corresponding to these IDs for DT consumers.

State and persistence: IDs are persistent ABI. Runtime rate and enable state is owned by the Sparx5 clock controller driver and hardware registers.

Dependencies and integration points: Used by Sparx5 DTS files and by consumers needing core, DDR, CPU/ARM auxiliary, and SyncE clocks.

Risks and test signals: Risks are simple but binding-visible: changing order or count breaks existing DTBs. Test with `dtbs_check`, clock provider probe, `N_CLOCKS` array bounds, and platform checks for networking, CPU auxiliary clocks, DDR clock reporting, and SyncE consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/microchip,sparx5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mobileye,eyeq5-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mobileye,eyeq5-clk.h

Purpose: Defines clock IDs for Mobileye EyeQ5 and related EyeQ6H/EyeQ6L-compatible clock domains represented in the binding header.

Important APIs, types, and functions: Exports `EQ5C_PLL_*`, derived CPU and peripheral child clocks, and additional `EQ6LC_*` and `EQ6HC_*` PLL/peripheral IDs. No structs or functions are present.

Control flow: The header has no logic. Clock providers use the constants when translating DT specifiers to PLL, divider, or gate clock objects.

State and persistence: Constants are DT ABI. PLL lock, divisor, and gate state are represented by hardware and common-clock-framework objects elsewhere.

Dependencies and integration points: Used by Mobileye EyeQ DTS files and drivers for CPU, DDR, PCI, PMA, VDI, VMP, MPC, OSPI, UART, I2C, timer, GPIO, and accelerator domains.

Risks and test signals: Risks include mixing EyeQ5 and EyeQ6 subdomain IDs and broken PLL child mapping. Test with DT schema validation, provider registration, CPU/peripheral rate checks, OSPI and serial probes, accelerator clock requests, and boot logs for unresolved clock specifiers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mobileye,eyeq5-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mobileye,eyeq6lplus-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mobileye,eyeq6lplus-clk.h

Purpose: Provides DT clock IDs for Mobileye EyeQ6L Plus clock domains.

Important APIs, types, and functions: Defines `EQ6LPC_PLL_*` roots, CPU, accelerator, DDR, peripheral, and VDI output clocks such as OSPI, I2C, UART, SPI, and PERIPH. No callable functions or data structures are included.

Control flow: No execution occurs. The EyeQ6L Plus clock provider maps these IDs from DT clock specifiers to registered clock objects.

State and persistence: Numeric IDs are stable DT ABI; runtime PLL/divider/gate state is external to the header.

Dependencies and integration points: Integrates Mobileye EyeQ6L Plus DTS files with the common clock framework and consumers in CPU, DDR, VDI, accelerator, OSPI, UART, I2C, SPI, and peripheral subsystems.

Risks and test signals: Risks include parent/child confusion among PLL and OCC outputs and off-by-one provider tables. Test with `dtbs_check`, provider probe logs, clk tree inspection, serial and SPI/I2C bring-up, OSPI storage access, accelerator/VDI consumers, and suspend/resume clock enable validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mobileye,eyeq6lplus-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mpc512x-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mpc512x-clock.h

Purpose: Defines DT clock specifier constants for Freescale/NXP MPC512x SoCs.

Important APIs, types, and functions: Exports `MPC512x_CLK_*` IDs for dummy/reference/system clocks, DIU/VIU, CSB, e300, IPS, FEC, SATA/PATA, NFC, LPC, MBX, USB, PSC, SPDIF, NAND, PCI, SDHC, CAN, OUT clocks, and `MPC512x_CLK_LAST_PUBLIC`. There are no functions or types.

Control flow: No runtime control flow exists. MPC512x clock providers use the IDs to return clock handles for DT consumers.

State and persistence: IDs persist as DT ABI. Runtime state is stored by platform clock code and hardware.

Dependencies and integration points: Used by PowerPC MPC512x DTS files and drivers for Ethernet, storage, display, USB, PSC serial/audio, CAN, PCI, SDHC, and peripheral buses.

Risks and test signals: Risks include public/private boundary drift around `MPC512x_CLK_LAST_PUBLIC`, legacy DTS compatibility breaks, and wrong PSC/SPDIF output mapping. Test with DT compilation, legacy board boot, clk lookup logs, Ethernet, storage, serial, display, PCI, USB, CAN, and audio-related PSC/SPDIF checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mpc512x-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mstar-msc313-mpll.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mstar-msc313-mpll.h

Purpose: Defines output indices for the MStar/SigmaStar MSC313 MPLL divider outputs.

Important APIs, types, and functions: Exports `MSTAR_MSC313_MPLL_DIV2`, `_DIV3`, `_DIV4`, `_DIV5`, `_DIV6`, `_DIV7`, and `_DIV10`. No functions, structs, or runtime macros exist.

Control flow: The header is declarative. The MPLL clock provider maps DT clock specifiers to the corresponding fixed-factor divider output.

State and persistence: Constants are stable DT ABI. PLL rate and divider behavior are implemented in provider code and hardware.

Dependencies and integration points: Used by MStar/SigmaStar DTS files and consumers that need a divided MPLL clock source.

Risks and test signals: Risks are limited but ABI-critical: the IDs begin at 1, so provider arrays must either reserve index 0 or translate explicitly. Test with DT binding checks, MPLL provider probe, clk summary rates for each divider, and peripheral consumers whose rates depend on divided MPLL outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mstar-msc313-mpll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt2701-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt2701-clk.h

Purpose: Provides MediaTek MT2701 DT clock IDs across top, PLL, DDRPHY, infrastructure, peripheral, audio, multimedia, image, video decode, high-speed interface, Ethernet, 3D, and BDP domains.

Important APIs, types, and functions: Defines `CLK_TOP_*`, `CLK_APMIXED_*`, `CLK_DDRPHY_*`, `CLK_INFRA_*`, `CLK_PERI_*`, `CLK_AUD_*`, `CLK_MM_*`, `CLK_IMG_*`, `CLK_VDEC_*`, `CLK_HIFSYS_*`, `CLK_ETHSYS_*`, `CLK_G3DSYS_*`, and `CLK_BDP_*` IDs. No functions or types are declared.

Control flow: No logic is present. The constants are used by MT2701 clock providers to resolve DT clock specifiers.

State and persistence: Numeric values are stable ABI and persist in DTBs. Runtime clock state is maintained by CCF and MediaTek drivers.

Dependencies and integration points: Used by MT2701 DTS, MediaTek clock drivers, and audio, display, image, codec, Ethernet, high-speed interface, and bus consumers.

Risks and test signals: Risks include older one-based top IDs, sentinel mismatch, and swapped media/audio clocks. Test with DT validation, clk registration counts, audio playback, display, Ethernet, high-speed I/O, image/video decode, and clock tree inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt2701-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt2712-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt2712-clk.h

Purpose: Defines MT2712 Device Tree clock IDs for PLL, top clock, infrastructure, peripheral, MCU, GPU, display, image, BDP, VDEC, VENC, and JPEG decode domains.

Important APIs, types, and functions: Exports `CLK_APMIXED_*`, `CLK_TOP_*`, `CLK_INFRA_*`, `CLK_PERI_*`, `CLK_MCU_*`, `CLK_MFG_*`, `CLK_MM_*`, `CLK_IMG_*`, `CLK_BDP_*`, `CLK_VDEC_*`, `CLK_VENC_*`, and `CLK_JPGDEC_*` constants. There are no functions or structs.

Control flow: The file has no executable behavior. Driver probe paths register clock tables whose indexes must match these IDs.

State and persistence: Values are DT ABI and remain meaningful in compiled DTBs. Runtime enable/rate state is elsewhere.

Dependencies and integration points: Integrated with MT2712 DTS and MediaTek CCF providers for display, multimedia, codecs, JPEG, GPU, peripheral buses, and MCU clocks.

Risks and test signals: Risks are provider table ordering errors, missing `*_NR_CLK` updates, and media-domain miswiring. Test with `dtbs_check`, boot registration warnings, display output, JPEG decode, video encode/decode, image pipeline, GPU probe, and peripheral bus consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt2712-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt6765-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt6765-clk.h

Purpose: Provides clock IDs for MediaTek MT6765, including fixed 26 MHz, PLL, top, infrastructure, audio, MIPI CSI analog, multimedia, image, video encode, and camera domains.

Important APIs, types, and functions: Defines `CLK_TOP_CLK26M`, `CLK_APMIXED_*`, `CLK_TOP_*`, `CLK_IFR_*`, `CLK_AUDIO_*`, `CLK_MIPI0A_*`, `CLK_MM_*`, `CLK_IMG_*`, `CLK_VENC_*`, and `CLK_CAM_*`. No functions or types are provided.

Control flow: No code executes. DT consumers use these integer IDs; clock providers map them to registered CCF clocks.

State and persistence: IDs are persistent DT ABI. Runtime state is in CCF/provider structures and hardware registers.

Dependencies and integration points: Used by MT6765 DTS files and consumers for UART/SPI/MSDC, audio, display, camera, image processing, MIPI CSI, and video encode.

Risks and test signals: Risks include overlapping local domains being passed to the wrong provider, top/fixed clock confusion, and camera CSI clock mismatches. Test with DT validation, clock provider registration, serial/storage probes, camera capture, display, audio, image processing, and video encode scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt6765-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt6779-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt6779-clk.h

Purpose: Defines MediaTek MT6779 clock IDs for TOPCKGEN, APMIXED PLLs, camera, infrastructure, GPU, image, IPE, multimedia, video decode/encode, and audio domains.

Important APIs, types, and functions: Exports `CLK_TOP_*`, `CLK_APMIXED_*`, `CLK_CAM_*`, `CLK_INFRA_*`, `CLK_MFG_*`, `CLK_IMG_*`, `CLK_IPE_*`, `CLK_MM_*`, `CLK_VDEC_*`, `CLK_VENC_*`, and `CLK_AUD_*` constants. It declares no functions or data types.

Control flow: The header is declarative. Runtime control is in MT6779 clock drivers and CCF operations.

State and persistence: Numeric values persist in DT ABI. No runtime state exists in this file.

Dependencies and integration points: Used by MT6779 DTS and consumers for camera, display, audio, video codec, GPU, image/IPE accelerators, buses, UART/SPI/MSDC, and SCP/SSPM-related clocks.

Risks and test signals: Risks include one-based TOP IDs, large INFRA domain ordering errors, and multimedia subsystem clock swaps. Test with `dtbs_check`, clk registration count checks, display and camera bring-up, audio paths, video encode/decode, GPU probe, and suspend/resume clock gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt6779-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt6797-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt6797-clk.h

Purpose: Provides clock IDs for the MediaTek MT6797 SoC across top muxes, PLLs, infrastructure, image, multimedia, video decode, and video encode domains.

Important APIs, types, and functions: Defines `CLK_TOP_MUX_*`, `CLK_APMIXED_*`, `CLK_INFRA_*`, `CLK_IMG_*`, `CLK_MM_*`, `CLK_VDEC_*`, and `CLK_VENC_*` constants. No structs, enums, or functions are declared.

Control flow: No executable flow exists. Clock providers use these IDs as DT ABI inputs to select CCF clock descriptors.

State and persistence: The definitions are stable DT ABI. Runtime enable/rate/parent state is kept by provider drivers.

Dependencies and integration points: Integrated with MT6797 DTS and drivers for UART/SPI/MSDC, USB, display, MDP, image, video codecs, GPU/MFG, camera timing, and infrastructure bus clocks.

Risks and test signals: Risks include top mux numbering starting at 1, domain-local ID reuse with the wrong provider phandle, and missing sentinel updates. Test with DT binding validation, boot-time clk registration, display and codec workloads, image path tests, USB/storage/serial probes, and clk debugfs comparisons to expected parents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt6797-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt7621-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt7621-clk.h

Purpose: Defines the MT7621 clock IDs for the SoC root clocks and peripheral gates used by router-class MIPS platforms.

Important APIs, types, and functions: Exports `MT7621_CLK_*` constants for XTAL, CPU, bus, fixed-frequency clocks, HSDMA, Ethernet, timer, PCM, PIO, GDMA, NAND, I2C, I2S, SPI, UART, watchdog, PCIe ports, crypto, SHXC, and `MT7621_CLK_MAX`. No functions or types are present.

Control flow: The file is declarative. MT7621 clock drivers map DT specifier IDs to fixed clocks or gates.

State and persistence: IDs are stable DT ABI. Runtime enable state and rates are in the driver/hardware.

Dependencies and integration points: Used by MT7621 DTS files and consumers for Ethernet, PCIe, crypto, NAND, SDHCI/SHXC, serial, SPI, I2C, I2S/PCM, timers, watchdog, and DMA.

Risks and test signals: Risks include wrong fixed-rate selection and off-by-one `MT7621_CLK_MAX`. Test with DT compilation, boot logs, Ethernet/PCIe/storage/serial probes, timer/watchdog function, and clk summary rate checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt7621-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt7622-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt7622-clk.h

Purpose: Provides MediaTek MT7622 clock IDs for top, infrastructure, peripheral, PLL, audio, USB, PCIe, Ethernet, and SGMII clock domains.

Important APIs, types, and functions: Defines `CLK_TOP_*`, `CLK_INFRA_*`, `CLK_PERI_*`, `CLK_APMIXED_*`, `CLK_AUDIO_*`, `CLK_SSUSB_*`, `CLK_PCIE_*`, `CLK_ETH_*`, and `CLK_SGMII_*` constants. No functions or C types are declared.

Control flow: No runtime flow exists. The IDs are consumed by DT clock specifiers and resolved by MT7622 clock-controller drivers.

State and persistence: Values form stable DT ABI. Runtime state is maintained in common-clock-framework objects and hardware registers.

Dependencies and integration points: Used by MT7622 DTS, networking drivers, PCIe, USB, SATA/SGMII, audio, serial, SPI/I2C, PWM, and peripheral bus consumers.

Risks and test signals: Risks include confusing similar MT7622/MT7629 names, SGMII instance mismatch, and audio domain count errors. Test with `dtbs_check`, clk provider registration, Ethernet/SGMII links, PCIe, USB, SATA where present, audio playback, and peripheral probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt7622-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt7629-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt7629-clk.h

Purpose: Defines MediaTek MT7629 DT clock IDs for top, infrastructure, peripheral, PLL, USB, PCIe, Ethernet, and SGMII domains.

Important APIs, types, and functions: Exports `CLK_TOP_*`, `CLK_INFRA_*`, `CLK_PERI_*`, `CLK_APMIXED_*`, `CLK_SSUSB_*`, `CLK_PCIE_*`, `CLK_ETH_*`, and `CLK_SGMII_*` constants. No functions or structs exist.

Control flow: Declarative only. Provider drivers use the numeric IDs to locate clock descriptors for DT consumers.

State and persistence: The numeric assignments are persistent binding ABI; runtime state is external.

Dependencies and integration points: Used by MT7629 DTS and consumers for Ethernet switch/MAC, SGMII, PCIe, USB, SPI/I2C/UART, PWM, MSDC, and system buses.

Risks and test signals: Risks include accidental reuse of MT7622 IDs that differ on MT7629, incorrect SGMII/ETH provider mapping, and sentinel mismatches. Test with DT validation, clk registration counts, Ethernet and SGMII link tests, PCIe/USB enumeration, storage/serial probes, and clk tree parent/rate checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt7629-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt7986-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt7986-clk.h

Purpose: Provides MT7986 clock IDs for the PLL, top, infrastructure, SGMII, and Ethernet domains of MediaTek networking SoCs.

Important APIs, types, and functions: Defines `CLK_APMIXED_*`, `CLK_TOP_*`, `CLK_INFRA_*`, `CLK_SGMII0_*`, `CLK_SGMII1_*`, and `CLK_ETH_*` constants. It has no callable functions or C data types.

Control flow: No logic is in the header. MT7986 clock drivers translate DT clock IDs into fixed, mux, divider, gate, or PLL clock objects.

State and persistence: IDs are stable DT ABI. Runtime clock state belongs to the provider and hardware.

Dependencies and integration points: Used by MT7986 DTS files and networking/storage/peripheral consumers, especially Ethernet, WED/WOCPU, SGMII, PCIe/USB-related top clocks, UART, SPI, PWM, and I2C.

Risks and test signals: Risks include SGMII0/1 swaps, Ethernet gate misnumbering, and mismatched `*_NR_CLK` entries. Test with DT binding validation, Ethernet throughput/link tests, SGMII link training, WOCPU/WED bring-up, PCIe/USB if present, and clk summary checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt7986-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8135-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8135-clk.h

Purpose: Defines MediaTek MT8135 clock IDs for top clock generation, PLLs, infrastructure, and peripheral systems.

Important APIs, types, and functions: Exports `CLK_TOP_*`, `CLK_APMIXED_*`, `CLK_INFRA_*`, and `CLK_PERI_*` constants for PLL-derived clocks, TV/HDMI/LVDS paths, USB, MSDC, PWM, I2C, UART, SPI, NAND, and bus clocks. No functions or structs are declared.

Control flow: No executable control flow. The IDs are interpreted by MT8135 clock provider arrays and used by DT clock consumers.

State and persistence: Values are ABI-stable and persist in DTBs. Runtime clock state is stored outside the header.

Dependencies and integration points: Used by MT8135 DTS and consumers for display/HDMI/LVDS, USB, storage, serial, SPI/I2C, PWM, and core bus clocks.

Risks and test signals: Risks include one-based top IDs, missing index 2 behavior, and confusion between similarly named PLL divisions. Test with DT validation, provider probe logs, display/HDMI/LVDS clocks, storage, USB, serial, and clk rate checks against expected PLL divisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8135-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8167-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8167-clk.h

Purpose: Extends the MT8516 clock ID namespace for MT8167-specific PLL, top, GPU, multimedia, image, and video decode clocks.

Important APIs, types, and functions: Includes `<dt-bindings/clock/mt8516-clk.h>` and defines MT8167 additions such as `CLK_APMIXED_TVDPLL`, `CLK_APMIXED_LVDSPLL`, `MT8167_CLK_APMIXED_NR_CLK`, extra `CLK_TOP_*` display/video clocks, `CLK_MFG_*`, `CLK_MM_*`, `CLK_IMG_*`, and `CLK_VDEC_*`. No functions or structs exist.

Control flow: No code executes. IDs are computed by offsetting the inherited MT8516 sentinels, so provider drivers must share the same base namespace.

State and persistence: Constants are DT ABI. Runtime clock state is in MT8167/MT8516 provider drivers.

Dependencies and integration points: Tightly coupled to `mt8516-clk.h`, MT8167 DTS, and consumers for HDMI/LVDS/DSI/DPI, MFG/GPU, display, image, and VDEC.

Risks and test signals: Risks include inherited sentinel drift and broken ABI if MT8516 IDs change. Test by building both MT8516 and MT8167 DTBs, verifying provider counts, and exercising display outputs, GPU, image, VDEC, and inherited peripheral clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8167-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8173-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8173-clk.h

Purpose: Provides MT8173 clock IDs for top clocks, PLLs, infrastructure, peripheral, image, multimedia/display, video decode, video encode, and VENCLT domains.

Important APIs, types, and functions: Defines `CLK_TOP_*`, `CLK_APMIXED_*`, `CLK_INFRA_*`, `CLK_PERI_*`, `CLK_IMG_*`, `CLK_MM_*`, `CLK_VDEC_*`, `CLK_VENC_*`, and `CLK_VENCLT_*`. There are no functions or types.

Control flow: The header is declarative. Clock controller drivers use these numeric IDs during DT clock resolution.

State and persistence: The constants are stable DT ABI and carry no runtime state.

Dependencies and integration points: Used by MT8173 DTS and consumers for display/HDMI, multimedia, image, video codecs, USB, storage, serial, I2C/SPI, PWM, and infrastructure buses.

Risks and test signals: Risks include sparse top numbering, provider array holes, and codec/display ID swaps. Test with DT binding validation, clk provider warnings, HDMI/display output, video encode/decode, image pipeline, storage/USB/serial probes, and suspend/resume clock gating checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8173-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8183-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8183-clk.h

Purpose: Defines MediaTek MT8183 clock IDs across APMIXED PLLs, TOPCKGEN muxes, camera, infrastructure, peripheral, GPU, image, multimedia, video, audio, IPU, and MCU domains.

Important APIs, types, and functions: Exports `CLK_APMIXED_*`, `CLK_TOP_MUX_*`, `CLK_CAM_*`, `CLK_INFRA_*`, `CLK_PERI_*`, `CLK_MFG_*`, `CLK_IMG_*`, `CLK_MM_*`, `CLK_VDEC_*`, `CLK_VENC_*`, `CLK_AUDIO_*`, `CLK_IPU_*`, and `CLK_MCU_*`. No functions or structs exist.

Control flow: No runtime behavior. Provider drivers map these IDs to CCF clocks used by DT consumers.

State and persistence: IDs are DT ABI. Runtime parent/rate/enable state is external.

Dependencies and integration points: Used by MT8183 DTS, MediaTek CCF providers, and consumers for Chromebook-class display, camera, IPU, audio, video, GPU, I2C/SPI/UART, storage, and SCP/MCU clocks.

Risks and test signals: Risks include IPU domain mismatches, large infra table ordering errors, and top mux ID drift. Test with `dtbs_check`, boot logs, display, camera, IPU, audio, video codecs, GPU probe, and peripheral suspend/resume coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8183-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8186-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8186-clk.h

Purpose: Provides MT8186 Device Tree clock IDs for MCU, top, infrastructure, PLL, I2C wrapper, GPU, multimedia, WPE, image, video, camera, camera raw, and IPE domains.

Important APIs, types, and functions: Defines `CLK_MCU_*`, `CLK_TOP_*`, `CLK_INFRA_AO_*`, `CLK_APMIXED_*`, `CLK_IMP_IIC_WRAP_*`, `CLK_MFG_*`, `CLK_MM_*`, `CLK_WPE_*`, `CLK_IMG*`, `CLK_VDEC_*`, `CLK_VENC_*`, `CLK_CAM*`, and `CLK_IPE_*` constants. No functions or structs are present.

Control flow: Declarative only. Clock providers use the IDs when resolving DT phandle arguments.

State and persistence: Values are stable DT ABI; runtime clock state is maintained elsewhere.

Dependencies and integration points: Used by MT8186 DTS and consumers for display, camera/raw pipelines, WPE, image/IPE, video codecs, GPU, I2C, storage, serial, and infrastructure clocks.

Risks and test signals: Risks include camera raw domain confusion, I2C wrapper instance mismatches, and sentinel drift. Test with DT validation, clk provider counts, display, camera/raw capture, WPE/image processing, video encode/decode, GPU, and I2C bus enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8186-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8192-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8192-clk.h

Purpose: Defines MediaTek MT8192 clock IDs for top, infrastructure, peripheral, PLL, SCP/ADSP, audio, I2C wrappers, MSDC, GPU, multimedia, image, camera, video, IPE, display pipe, and MDP domains.

Important APIs, types, and functions: Exports `CLK_TOP_*`, `CLK_INFRA_*`, `CLK_PERI_*`, `CLK_APMIXED_*`, `CLK_SCP_ADSP_*`, `CLK_AUD_*`, `CLK_IMP_IIC_WRAP_*`, `CLK_MSDC*`, `CLK_MFG_*`, `CLK_MM_*`, `CLK_IMG*`, `CLK_CAM_*`, `CLK_VDEC_*`, `CLK_VENC_*`, `CLK_IPE_*`, `CLK_DPE_*`, and `CLK_MDP_*`. No functions or types.

Control flow: No logic is present. DT specifiers feed provider lookup tables indexed by these IDs.

State and persistence: IDs are binding ABI; runtime state is external.

Dependencies and integration points: Used by MT8192 DTS and consumers for display, camera, MDP, image/IPE/DPE, audio DSP, SCP/ADSP, codecs, GPU, storage, and buses.

Risks and test signals: Risks include large-table ordering mistakes and split image/camera domain mismatch. Test with DT schema checks, clk registration, display/camera/media workloads, ADSP/SCP/audio boot, GPU probe, storage, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8192-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8195-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8195-clk.h

Purpose: Provides the public DT clock-ID namespace for MediaTek MT8195 across top, infra, PLL, SCP/ADSP, peripheral, I2C wrapper, GPU, VPP/WPE, image, DIP, IPE, camera, video decode/encode, audio, impedance, MDP, and VDO domains.

Important APIs, types, and functions: Defines hundreds of `CLK_*` constants including `CLK_TOP_*`, `CLK_INFRA_AO_*`, `CLK_APMIXED_*`, `CLK_SCP_ADSP_*`, `CLK_PERI_AO_*`, `CLK_IMP_IIC_WRAP_*`, `CLK_MFG_*`, `CLK_VPP*`, `CLK_WPE*`, `CLK_IMG*`, `CLK_IPE_*`, `CLK_CAM*`, `CLK_VDEC*`, `CLK_VENC*`, `CLK_AUD_*`, `CLK_MDP_*`, `CLK_VDO0_*`, and `CLK_VDO1_*`. No functions or types.

Control flow: Declarative only. Provider drivers and DTBs must agree exactly on the numeric IDs.

State and persistence: Persistent DT ABI; runtime state belongs to CCF/provider drivers.

Dependencies and integration points: Used by MT8195 DTS and high-end media/display/camera/audio/GPU/peripheral consumers.

Risks and test signals: Risks include cross-domain swaps in very large tables, stale count constants, and display/video pipeline breakage. Test with DT validation, provider count checks, dual-display/VDO pipelines, camera, codecs, audio DSP, GPU, MDP/VPP/WPE, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8195-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8516-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8516-clk.h

Purpose: Defines MediaTek MT8516 clock IDs for PLL, infrastructure, top, and audio system clock domains.

Important APIs, types, and functions: Exports `CLK_APMIXED_*`, `CLK_IFR_*`, `CLK_TOP_*`, and `CLK_AUD_*` constants, including sentinel values used by MT8167 extension headers. No functions or structs are declared.

Control flow: The file contains no executable behavior. Clock providers use the constants to map DT specifiers to CCF clocks.

State and persistence: IDs are stable binding ABI. Runtime rate and enable state is owned by the common clock framework and MediaTek provider drivers.

Dependencies and integration points: Used by MT8516 DTS, MT8167 derived headers, and consumers for infrastructure buses, Ethernet, I2C, audio interfaces, USB, NAND/flash, PWM, PMIC wrapper, and top PLL-derived clocks.

Risks and test signals: Risks include breaking MT8167 offset-based IDs, stale sentinels, and audio/top clock parent mistakes. Test by building MT8516 and MT8167 DTBs, checking provider counts, audio playback, Ethernet, I2C, USB, flash, and clk summary rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8516-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/nuvoton,ma35d1-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/nuvoton,ma35d1-clk.h

Purpose: Provides DT clock IDs for the Nuvoton MA35D1 clock controller, spanning oscillators, PLLs, divisors, gates, system buses, AXI/AHB peripherals, and APB peripherals.

Important APIs, types, and functions: Defines flat constants for HXT/LXT/HIRC/LIRC gates, CAPLL/SYSPLL/DDRPLL/APLL/EPLL/VPLL, EPLL dividers, CPU/system/HCLK/PCLK divisors, GPIO/PDMA/USB/SDH/NAND/EMAC/LCD/DCU/GFX/CAP gates, timers, UARTs, I2C, QSPI, SPI, CAN, I2S, EPWM, ADC/EADC, and `CLK_MAX_IDX`. No functions or structs exist.

Control flow: No runtime logic. Provider code maps these numeric IDs to clock objects.

State and persistence: IDs are DT ABI; hardware and provider code store runtime state.

Dependencies and integration points: Used by MA35D1 DTS and consumers for buses, display, graphics, storage, networking, USB, serial, SPI/I2C/CAN/I2S, timers/PWM, ADC, and DMA.

Risks and test signals: Risks include very large flat namespace ordering errors and gate/divider pair confusion. Test with DT validation, clock count bounds, boot logs, serial/storage/network/display/USB probes, timer/PWM, ADC, and rate checks for PLL-derived clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/nuvoton,ma35d1-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/nuvoton,npcm7xx-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/nuvoton,npcm7xx-clock.h

Purpose: Defines clock binding numbers for the Nuvoton NPCM7xx clock generator.

Important APIs, types, and functions: Exports `NPCM7XX_CLK_*` constants for CPU, graphics pixel, memory controller, ADC, AHB, timer, UART, MMC, SPI, PCI, AXI, APB, RNG, SDHC, GPIO, watchdog, USB bridge/host/device, GFX, SPIX, reference, bypass clocks, and `NPCM7XX_NUM_CLOCKS`. No functions or types are included.

Control flow: The header has no logic. The NPCM7xx clock driver uses IDs to look up clock descriptors for DT consumers.

State and persistence: Numeric IDs are stable DT ABI. Runtime clock state is in the provider driver/hardware.

Dependencies and integration points: Used by NPCM7xx BMC DTS files and consumers for serial, timers, MMC/SDHC, SPI, PCI, USB, graphics, RNG, watchdog, GPIO, and buses.

Risks and test signals: Risks include expression-based `NPCM7XX_NUM_CLOCKS` mismatches and graphics clock naming drift. Test with DT validation, provider probe, BMC boot, UART console, storage, SPI, USB, watchdog, graphics if enabled, and clk lookup warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/nuvoton,npcm7xx-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/nuvoton,npcm845-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/nuvoton,npcm845-clk.h

Purpose: Provides DT clock IDs for the Nuvoton NPCM8XX/NPCM845 clock controller.

Important APIs, types, and functions: Defines `NPCM8XX_CLK_*` constants for CPU, graphics pixel, memory controller, ADC, AHB, timer, UART/UART2, MMC, SPI3, PCI, AXI, APB, RNG, SDHC, GPIO, watchdog, USB bridge/host/device, graphics, SU, DDR PHY, pre-clock outputs, thermal sensor, reference, bypass clocks, and `NPCM8XX_NUM_CLOCKS`. No functions or data types exist.

Control flow: No runtime flow is present. Provider drivers translate these DT IDs to registered clocks.

State and persistence: IDs are stable binding ABI. Runtime rates, parents, and gates are maintained by the NPCM8XX clock driver and hardware.

Dependencies and integration points: Used by NPCM845/NPCM8XX DTS files and consumers for BMC serial, storage, SPI, PCI, USB, GPIO, watchdog, RNG, graphics, DDR, thermal, and bus clocks.

Risks and test signals: Risks include `NPCM8XX_NUM_CLOCKS` expression drift, new pre-clock IDs not represented in provider arrays, and NPCM7xx/NPCM8xx namespace confusion. Test with `dtbs_check`, provider count checks, BMC boot, UART, MMC/SDHC, SPI, USB, watchdog, thermal, and clk debugfs lookup coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/nuvoton,npcm845-clk.h -->
