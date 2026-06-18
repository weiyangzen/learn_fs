# subset-b-001103 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-vdo0.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-vdo0.c

### Purpose
`clk-mt8195-vdo0.c` provides the MT8195 VDO0 video-output clock controller. It exposes gates for display overlay, color, correction, AAL, gamma, dither, WDMA/RDMA, DSI, DSC, merge, DP interface, SMI, monitor, and async-link blocks.

### Important APIs, Types, And Functions
The file is table driven around `struct mtk_gate_regs`, `GATE_VDO0_*` macros, `vdo0_clks`, and `vdo0_desc`. It uses `mtk_clk_gate_ops_setclr`, plus `GATE_MTK_FLAGS` for the DP interface clock with `CLK_SET_RATE_PARENT`. Registration is through a platform ID table whose `driver_data` points at `vdo0_desc`, and the driver uses `mtk_clk_pdev_probe()` and `mtk_clk_pdev_remove()`.

### Control Flow, State, And Persistence
Probe is delegated to the common MediaTek platform-clock helper, which maps the platform resource, allocates onecell clock data, registers every gate in `vdo0_clks`, and publishes the provider to consumers. Runtime state is the hardware gate bits in three set/clear/status banks at 0x100, 0x110, and 0x120 ranges; the driver has no persistent storage beyond registered clock objects.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies are `dt-bindings/clock/mt8195-clk.h`, the common MediaTek gate framework, and parent clocks such as `top_vpp`, `top_dsi_occ`, and `top_edp`. Risks are wrong bit shifts, missing parent names, and DP rate propagation failures. Test signals include boot-time provider registration, display pipeline probe success, clk summary showing VDO0 gates, DP/DSI enable sequences, and suspend/resume gate status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-vdo0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-vdo1.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-vdo1.c

### Purpose
`clk-mt8195-vdo1.c` describes the second MT8195 video-output clock domain. It gates VDO1 SMI/LARB, MDP RDMA, merge, HDR front/back-end, DPI, DP, monitor, HDMI-DPI, slow 26 MHz, and cross-domain async clocks.

### Important APIs, Types, And Functions
The core objects are five `mtk_gate_regs` banks, `GATE_VDO1_*` macros, `vdo1_clks`, and `vdo1_desc`. Most gates use `mtk_clk_gate_ops_setclr`; the HDMI DPI gate uses `mtk_clk_gate_ops_no_setclr_inv` against the 0x400 register; the DP interface gate carries `CLK_SET_RATE_PARENT`. The platform driver uses `mtk_clk_pdev_probe()` with a platform ID table.

### Control Flow, State, And Persistence
The driver is passive after module registration. Common probe reads `driver_data`, registers the fixed gate table, and makes a onecell provider. Clock enable state is stored only in the SoC gate registers; no software cache or nonvolatile state is maintained.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on MT8195 clock IDs, parent names `top_vpp`, `top_dp`, `clk26m`, and `hdmi_txpll`, and display/HDMI/DP consumers. Risks include the inverted no-setclr HDMI gate being modeled incorrectly, rate-parent behavior for DP, and fragile long clock names used by consumers. Test signals include HDMI/DPI and DP output bring-up, VDO1 SMI clock availability, debugfs clock parent/rate checks, and module remove/unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-vdo1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-venc.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-venc.c

### Purpose
`clk-mt8195-venc.c` registers MT8195 video encoder clocks for the main VENC system and the second VENC core. It covers LARB, VENC, JPEG encode/decode, secondary JPEG decode, and GALS clocks.

### Important APIs, Types, And Functions
The file defines one inverted set/clear gate bank, `GATE_VENC`, two gate arrays (`venc_clks` and `venc_core1_clks`), and two descriptors selected by OF compatible strings. The platform driver uses `mtk_clk_simple_probe()` and `mtk_clk_simple_remove()` instead of a platform ID table.

### Control Flow, State, And Persistence
At probe, the common simple helper selects the descriptor from `of_match_clk_mt8195_venc`, registers the selected gate set, and publishes the OF clock provider. Hardware state is held in the VENC gate register at offsets 0x0/0x4/0x8; the two compatibilities instantiate independent providers for separate register blocks.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parent `top_venc`, OF nodes `mediatek,mt8195-vencsys` and `mediatek,mt8195-vencsys_core1`, and V4L2/media encoder consumers. Risks are inverted gate semantics, core0/core1 binding mismatches, and missing LARB/GALS clocks causing DMA failures. Test signals are encoder/JPEG runtime PM paths, clk summary for both providers, media pipeline encode/decode tests, and clean unregistration on driver unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-venc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-vpp0.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-vpp0.c

### Purpose
`clk-mt8195-vpp0.c` implements the first MT8195 video processing pipe clock provider. It gates MDP, warp async, mutex, VPP relay, SMI, GALS bridge, HDR/TDSHP/color/OVL, and warp relay clocks.

### Important APIs, Types, And Functions
Important objects are three gate-register banks, the `GATE_VPP0_*` macros, `vpp0_clks`, `vpp0_desc`, and a platform driver wired to `mtk_clk_pdev_probe()`. All gates use non-inverted set/clear operations through `mtk_clk_gate_ops_setclr`.

### Control Flow, State, And Persistence
The probe path is the common MediaTek platform descriptor path: match platform ID, map registers, register gate clocks, and expose the provider. Runtime state is only hardware clock-gate bits across VPP0_0, VPP0_1, and VPP0_2 banks. No persistent data is written.

### Dependencies, Integration Points, Risks, And Test Signals
The provider depends on parent clocks `top_vpp` and `top_wpe_vpp`, MT8195 binding IDs, and display/MDP/warp consumers. Risks include incorrect cross-pipe relay gating, SMI/IOMMU clock omissions leading to bus faults, and parent dependency changes in topckgen. Test signals include MDP and display processing tests, warp-engine workflows, SMI/LARB activity, clock debugfs enables, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-vpp0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-vpp1.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-vpp1.c

### Purpose
`clk-mt8195-vpp1.c` supplies gates for MT8195 VPPSYS1. It covers SVPP1/2/3 MDP blocks, VPP split/merge, VDO relay links, LARB fake engines, HDMI/DGI paths, display mutex, and 26 MHz split support.

### Important APIs, Types, And Functions
The file defines `vpp1_0_cg_regs`, `vpp1_1_cg_regs`, `GATE_VPP1_0`, `GATE_VPP1_1`, `vpp1_clks`, and `vpp1_desc`. Registration is through a platform ID table and common `mtk_clk_pdev_probe()`/`mtk_clk_pdev_remove()` helpers.

### Control Flow, State, And Persistence
After platform matching, the common helper registers all gate descriptors against the resource-backed register map and adds a onecell provider. Hardware gate bits in the two VPP1 banks are the only retained state. The driver has no custom sequencing, runtime PM logic, or persistent configuration.

### Dependencies, Integration Points, Risks, And Test Signals
It integrates with MT8195 video/display processing, HDMI receiver paths, DGI paths, and parents `top_vpp`, `hdmirx_p`, `in_dgi`, `top_dgi_out`, and `clk26m`. Risks include accidental gating of relay paths shared with VDO0/VDO1, wrong non-top parent names, and incomplete test coverage for HDMI/DGI-only clocks. Test signals include multi-pipe MDP jobs, display split/merge use, HDMI/DGI input paths, and clk enable-count tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-vpp1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-wpe.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-wpe.c

### Purpose
`clk-mt8195-wpe.c` registers MT8195 warp engine clocks for the root WPE system and two WPE-VPP subdomains. It gates WPE VPP links, SMI LARBs, event TX, cache/top/DMA/vector/output/mask blocks, and crop/sync units.

### Important APIs, Types, And Functions
The file defines three no-setclr inverted register banks, `GATE_WPE`, `GATE_WPE_VPP0`, `GATE_WPE_VPP1`, three gate arrays, and three descriptors. OF matching maps `mediatek,mt8195-wpesys`, `_vpp0`, and `_vpp1` to the correct descriptor. Probe/remove use `mtk_clk_simple_probe()` and `mtk_clk_simple_remove()`.

### Control Flow, State, And Persistence
Probe selects the OF descriptor, registers the gate array against the device resource, and exposes a onecell provider. WPE root and VPP subdomain clocks are modeled as separate providers for separate register blocks. State lives in hardware gate bits, including no-setclr inverted gates at offsets 0x0, 0x58, and 0x5c.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parents `top_wpe_vpp` and `top_img`, image/MDP consumers, and MT8195 clock IDs. Risks are inverted gate interpretation, duplicated VPP0/VPP1 table structure, and SMI LARB clock ordering. Test signals include WPE image-processing jobs, VPP0/VPP1 subdomain probes, SMI access without bus faults, and clock debugfs gate toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-wpe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-apmixedsys.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-apmixedsys.c

### Purpose
`clk-mt8196-apmixedsys.c` implements MT8196 APMIXEDSYS PLL providers for two PLL groups: main APMIXEDSYS and APMIXEDSYS_GP2. It provides root PLLs used by topckgen, multimedia, storage, network, display, image, and audio/video clock trees.

### Important APIs, Types, And Functions
Key definitions are `PLL_FENC`, `struct mtk_pll_desc`, `apmixed_plls`, `apmixed2_plls`, `clk_mt8196_apmixed_probe()`, and `clk_mt8196_apmixed_remove()`. PLLs use `mtk_pll_fenc_clr_set_ops`, shared enable/set/clear registers `PLLEN_ALL*`, `FENC_STATUS_CON0`, 22 PCW bits, and 8 integer bits. OF match data selects the descriptor.

### Control Flow, State, And Persistence
Probe obtains match data, allocates `clk_hw_onecell_data`, registers all PLLs, adds an OF clock provider, and stores clk data in platform driver data. Error paths unregister PLLs and free data. Remove deletes the provider, unregisters PLLs, and frees data. Persistent state is hardware PLL configuration and enable bits only.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include `clk-pll.h`, MT8196 clock bindings, OF matching, and topckgen consumers expecting names such as `mainpll`, `univpll`, `emipll`, `mainpll2`, and `tvdpll*`. Risks include fencing status bit mismatches, always-on PLL flag mistakes for EMI/main PLLs, and failure to unwind providers. Test signals include boot clock tree registration, PLL rate changes, topckgen parent resolution, OF provider failure injection, and suspend/resume PLL state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-apmixedsys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-disp0.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-disp0.c

### Purpose
`clk-mt8196-disp0.c` describes the MT8196 primary display clock gate domain. It covers display configuration, mutex, AAL, C3D, color/correction, CHIST, dither, DLI/DLO async, gamma, MDP, postmask, RSZ, SPR, WDMA, Y2R, SMI, and fake-engine clocks.

### Important APIs, Types, And Functions
The file uses normal gate macros (`GATE_MM0`, `GATE_MM1`) and hardware-voter macros (`GATE_HWV_MM0`, `GATE_HWV_MM1`). HWV gates carry `hwv_regs` pointing to done/set/clear registers and use `mtk_clk_gate_hwv_ops_setclr`; non-HWV gates use `mtk_clk_gate_ops_setclr`. `mm_mcd` is registered through `mtk_clk_pdev_probe()`.

### Control Flow, State, And Persistence
The platform probe registers the table as a provider. Gate operations may either write local CG registers or request hardware-voter operations depending on each descriptor. Runtime state is split between display CG registers and HWV status registers; no software state is persisted.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parent `disp`, MT8196 IDs, MediaTek HWV gate support, and display/MDP consumers. Risks are wrong HWV register offsets, parent-enable semantics not matching hardware power dependencies, and display path hangs if async or SMI clocks are gated unexpectedly. Test signals include display pipeline boot, HWV gate enable/disable completion, clk summary parent enables, DRM modeset, and runtime suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-disp0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-disp1.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-disp1.c

### Purpose
`clk-mt8196-disp1.c` registers the MT8196 secondary display clock domain. It gates dispsys1 config, display mutex, DLI/DLO async paths, relay, DP/DSI/DVO, DSC, GDMA, merge, ODDMR, postalign, dither, splitters, WDMA, SMI LARB, module clocks, and 26 MHz support.

### Important APIs, Types, And Functions
Two clock-gate banks are modeled by `mm10_cg_regs` and `mm11_cg_regs`, with corresponding HWV register banks. `GATE_HWV_MM10` and `GATE_HWV_MM11` use `mtk_clk_gate_hwv_ops_setclr`; normal macros use `mtk_clk_gate_ops_setclr`. The platform ID table passes `mm1_mcd` into `mtk_clk_pdev_probe()`.

### Control Flow, State, And Persistence
The common platform probe creates the clock provider from the descriptor. Runtime clock changes are table-driven and write either HWV or direct CG registers, with `CLK_OPS_PARENT_ENABLE` on all gates. State persists only as hardware register state across the display power domain.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parents `disp`, `clk26m`, `dp0`, and `dp1`, plus DRM display consumers. Risks include unusual clock names such as `mm1_CLK0` and `mm1_DP_CLK`, HWV completion timeouts, and display-output-specific clocks being untested. Test signals include secondary display/DSI/DP paths, clock provider binding by platform name, HWV status observation, and suspend/resume display tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-disp1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-imp_iic_wrap.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-imp_iic_wrap.c

### Purpose
`clk-mt8196-imp_iic_wrap.c` supplies MT8196 I2C wrapper clocks for central, east, north, and west I2C domains. It exposes gates for I2C0 through I2C14 using regional parent clocks.

### Important APIs, Types, And Functions
The file defines shared direct gate registers `imp_cg_regs`, one north HWV register block, `GATE_IMP`, `GATE_HWV_IMPN`, four clock arrays, and four descriptors. `of_match_clk_mt8196_imp_iic_wrap` maps each regional compatible to the correct descriptor. Probe/remove are `mtk_clk_simple_probe()` and `mtk_clk_simple_remove()`.

### Control Flow, State, And Persistence
OF matching chooses central/east/north/west tables. The common helper registers the selected gate clocks and provider. Most gates directly write set/clear/status offsets around 0xe00; `impn_i2c7` uses hardware voter registers. The driver keeps no persistent state outside clock registration data.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parents `i2c_p`, `i2c_east`, `i2c_north`, and `i2c_west`, I2C controller consumers, and HWV support. Risks include regional compatible mismatches, one HWV-only north clock path, and I2C probe failures when parent topckgen clocks are absent. Test signals include all I2C bus probes, runtime clock gating during transfers, north I2C7 HWV completion, and DT binding coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-imp_iic_wrap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-mcu.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-mcu.c

### Purpose
`clk-mt8196-mcu.c` registers per-control-block MT8196 CPU and interconnect PLLs: ARMPLL for big, little, and low-power clusters, plus CCI and PTP PLLs.

### Important APIs, Types, And Functions
The file defines one-PLL arrays (`cpu_bl_plls`, `cpu_b_plls`, `cpu_ll_plls`, `cci_plls`, `ptp_plls`), a `PLL` macro using 22 PCW bits and 8 integer bits, `clk_mt8196_mcu_probe()`, and `clk_mt8196_mcu_remove()`. OF match data directly points to the single-entry PLL array for each compatible.

### Control Flow, State, And Persistence
Probe fetches the match-data PLL array, allocates one clock slot, registers that PLL, adds the OF clock provider, and records driver data. Remove deletes the provider, unregisters exactly one PLL, and frees data. The hardware PLL registers hold rate and enable state; no software persistence is used.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include CPUfreq/OPP consumers, CCI interconnect users, PTP calibration, `clk-pll.h`, and MT8196 DT compatibles. Risks include using identical offsets across distinct register resources, always-on PLL semantics, and cluster PLL parent/rate changes destabilizing CPUfreq. Test signals include CPUfreq transitions, clock provider registration for each PLL node, rate readback, remove unwind, and suspend/resume on CPU clusters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-mcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-mdpsys.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-mdpsys.c

### Purpose
`clk-mt8196-mdpsys.c` registers MT8196 MDP system clocks for mdpsys0 and mdpsys1. It covers MDP mutex, SMI, APB, RDMA, BIRSZ, HDR, AAL, RSZ, TDSHP, color, WROT, RROT, async links, image links, VPP RSZ, and 26 MHz gates.

### Important APIs, Types, And Functions
The file defines three gate banks, `GATE_MDP0/1/2`, two nearly parallel gate arrays (`mdp_clks` and `mdp1_clks`), and descriptors `mdp_mcd` and `mdp1_mcd`. Both descriptors set `.need_runtime_pm = true`, so the common helper integrates provider registration with runtime PM. Probe/remove use `mtk_clk_simple_probe()`.

### Control Flow, State, And Persistence
OF matching selects mdpsys0 or mdpsys1. The helper enables runtime PM as requested, registers gates, and publishes a provider. Gate state resides in the three hardware CG banks; runtime PM state is managed by the common MediaTek helper and device core, not by custom logic here.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parent `mdp`, parent `clk26m`, runtime PM, MDP/DRM/media consumers, and SMI. Risks include duplicated table drift between mdpsys0 and mdpsys1, runtime PM ordering around clock registration, and bus faults if SMI clocks are gated. Test signals include MDP jobs on both systems, runtime PM get/put cycles, clk debugfs state, and image/display pipeline tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-mdpsys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-mfg.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-mfg.c

### Purpose
`clk-mt8196-mfg.c` registers MT8196 GPU manufacturing PLLs: the main MFG PLL and two shader-core PLL controls.

### Important APIs, Types, And Functions
Important objects are `mfg_ao_plls`, `mfgsc0_ao_plls`, `mfgsc1_ao_plls`, the local `PLL` macro, `clk_mt8196_mfg_probe()`, and `clk_mt8196_mfg_remove()`. PLL descriptors set parent `"mfg_eb"` and `PLL_PARENT_EN`, with 22 PCW bits and 8 integer bits.

### Control Flow, State, And Persistence
The OF compatible selects a single PLL array. Probe allocates one clock slot, registers the PLL, exposes the provider, and records driver data. Remove deletes the provider and unregisters the PLL. Hardware PLL control registers persist actual enable/rate state.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include topckgen parent `mfg_eb`, GPU devfreq/OPP consumers, `clk-pll.h`, and MT8196 bindings. Risks include missing parent enable during PLL operations, identical register offsets requiring separate resources, and bad GPU rate transitions. Test signals include GPU probe and devfreq changes, PLL parent enable count, rate readback, and clean provider removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-mfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-ovl0.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-ovl0.c

### Purpose
`clk-mt8196-ovl0.c` registers the first MT8196 overlay clock provider. It gates OVLSYS config, fake engines, mutex, EXDMA, blenders, output processors, MDP RSZ, WDMA, UFBC WDMA, MDP RDMA, BWM, DLI/DLO async links, relay, inline rotation, and SMI.

### Important APIs, Types, And Functions
All gates are HWV-aware through `GATE_HWV_OVL0` and `GATE_HWV_OVL1`, each carrying direct CG registers and HWV set/clear/done registers. The provider descriptor is `ovl_mcd`, selected through the platform ID table and registered by `mtk_clk_pdev_probe()`.

### Control Flow, State, And Persistence
The platform probe registers a single descriptor containing two hardware banks. Clock enable and disable operations go through `mtk_clk_gate_hwv_ops_setclr`, which coordinates with the hardware voter. No local state is persisted beyond clock framework registration.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parent `disp`, display overlay consumers, HWV gate support, and MT8196 clock IDs. Risks include HWV offset/bit mistakes, display pipeline stalls from overlay async gates, and SMI gating errors. Test signals include overlay composition, DRM page flips, HWV completion status, clock debugfs gate toggles, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-ovl0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-ovl1.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-ovl1.c

### Purpose
`clk-mt8196-ovl1.c` mirrors the first overlay provider for MT8196 overlay system 1. It gates the ovl1 config, fake engines, mutex, EXDMA, blenders, output processors, MDP RSZ, WDMA, UFBC, MDP RDMA, BWM, DLI/DLO links, relay, inline rotation, and SMI clocks.

### Important APIs, Types, And Functions
The key objects are `ovl10_cg_regs`, `ovl11_cg_regs`, HWV registers, `GATE_HWV_OVL10`, `GATE_HWV_OVL11`, `ovl1_clks`, and `ovl1_mcd`. The platform driver uses `mtk_clk_pdev_probe()` and `mtk_clk_pdev_remove()`.

### Control Flow, State, And Persistence
Common probe registers all HWV gates and exposes the clock provider. All enable/disable operations are table-driven through hardware-voter set/clear ops. The only durable state is hardware gate status; no runtime PM or custom software state appears in this file.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parent `disp`, overlay pipeline consumers, and the HWV gate implementation. Risks are table drift from ovl0, incorrect duplicate clock naming, and missed SMI/relay dependencies for secondary display paths. Test signals include ovl1 display composition, multi-display overlay use, HWV done-register checks, and provider unbind/rebind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-ovl1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-peri_ao.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-peri_ao.c

### Purpose
`clk-mt8196-peri_ao.c` implements the MT8196 always-on peripheral clock controller. It gates UART, PWM, SPI, flash interface, AP DMA, and MSDC1/MSDC2 clocks.

### Important APIs, Types, And Functions
The file defines three direct gate banks plus one HWV bank for SPI gates. `GATE_PERI_AO0`, `GATE_PERI_AO1`, `GATE_HWV_PERI_AO1`, and `GATE_PERI_AO2` fill `peri_ao_clks`, described by `peri_ao_mcd`. OF matching uses `mediatek,mt8196-pericfg-ao`, and probe/remove use `mtk_clk_simple_probe()`.

### Control Flow, State, And Persistence
The common simple probe registers the descriptor and publishes the provider. UART/PWM/flash/MSDC gates use direct set/clear operations; SPI clocks use HWV set/clear operations. State is hardware gate bits only.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include top parents `uart`, `p_axi`, `pwm`, `spi*_b`, `sflash`, `msdc30_1`, and `msdc30_2`. Risks include early-console or storage clocks being gated unexpectedly, HWV SPI failures, and incorrect parent chains for flash/MSDC wrappers. Test signals include UART console, SPI transfer tests, PWM use, flash boot/storage access, MSDC probes, and clock debugfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-peri_ao.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-pextp.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-pextp.c

### Purpose
`clk-mt8196-pextp.c` registers MT8196 PCIe transmit PHY clock and reset providers for PEXTP0 and PEXTP1. It covers PCIe MAC/PHY TL, REF, MCU bus, AXI, AHB/APB, PL, and VLP low-power clocks.

### Important APIs, Types, And Functions
The file defines `GATE_PEXT`, two gate arrays, two reset index maps, `pext_rst_desc`, `pext1_rst_desc`, and descriptors with `.rst_desc`. It uses `MTK_RST_SET_CLR` reset semantics and reset IDs from `mediatek,mt8196-resets.h`.

### Control Flow, State, And Persistence
OF matching selects either PEXTP0 or PEXTP1. `mtk_clk_simple_probe()` registers both clocks and reset controller data from the descriptor. Gate state is stored in PEXTP CG registers, while reset state is controlled through set/clear reset banks.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include PCIe PHY/MAC consumers, parent clocks `tl`, `tl_p1`, `tl_p2`, `ufs_pexpt0_mem_sub`, `ufs_pextp0_axi`, `pextp1_usb_axi`, and reset framework integration. Risks include reset index map off-by-one errors, mismatched PEXTP0/PEXTP1 compatible usage, and incorrect memory-subsystem parents. Test signals include PCIe port probe/reset, reset-controller lookup, link training, clk summary, and unbind/rebind of both providers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-pextp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-topckgen.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-topckgen.c

### Purpose
`clk-mt8196-topckgen.c` is the primary MT8196 top clock generator. It defines fixed factors, muxes, mux gates, fenced muxes, hardware-voter mux gates, and audio divider/composite clocks for CPU/peripheral/storage/audio/security/interconnect clock roots.

### Important APIs, Types, And Functions
Important tables are `top_divs`, many parent arrays, `top_muxes`, `top_aud_divs`, and `topck_desc`. It uses macros from `clk-mux.h` including `MUX_CLR_SET_UPD`, `MUX_GATE_CLR_SET_UPD`, `MUX_GATE_FENC_CLR_SET_UPD`, `MUX_GATE_HWV_FENC_CLR_SET_UPD`, `MUX_DIV_GATE`, and `DIV_GATE`. The descriptor is registered via `mtk_clk_simple_probe()`.

### Control Flow, State, And Persistence
Probe is fully table driven: the common helper registers factors, muxes, and composites, then exposes the OF provider for `mediatek,mt8196-topckgen`. Mux state is persisted in hardware `CLK_CFG_*` registers with set/clear/update writes. Fenced muxes check `CLK_FENC_STATUS_MON_*`; HWV muxes use HW voter set/clear/done registers. Audio dividers store divider fields in `CLK_AUDDIV_*`.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include APMIXED PLL names, VLP audio PLLs, ULP oscillator parents, HWV support, and nearly every MT8196 peripheral driver. Risks are parent-list ordering, update-bit mapping, fencing status bits, missing separators in parent strings, and critical clocks accidentally gated. Test signals include full boot provider resolution, clk tree dumps, peripheral probes, mux rate switching, audio I2S divider tests, and HWV/fence timeout instrumentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-topckgen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-topckgen2.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-topckgen2.c

### Purpose
`clk-mt8196-topckgen2.c` implements the MT8196 GP2 top clock generator for multimedia-heavy roots: sensor interfaces, image/IPE/camera/DPE, VDEC/VENC, CCU, DVO/DP, display, MDP, MMINFRA, MMUP, and MMINFRA_AO.

### Important APIs, Types, And Functions
The main data is `top_divs`, multimedia parent arrays, `top_muxes`, and `topck_desc`. It uses GP2 register offsets (`CKSYS2_CLK_CFG_*`), fenced mux macros, and HWV mux-gate macros using `MM_HWV_CG_*` and `MM_HWV_MUX_UPDATE_31_0` infrastructure. Registration is through `mtk_clk_simple_probe()`.

### Control Flow, State, And Persistence
The common probe registers fixed factors and muxes for `mediatek,mt8196-topckgen-gp2`. Hardware state lives in CKSYS2 mux registers, set/clear registers, update bits, fence status, and multimedia HWV done registers. No custom state is held in the driver.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include APMIXED2 PLLs (`mainpll2`, `univpll2`, `mmpll2`, `imgpll`, `tvdpll*`), display/media consumers, and HWV support. Risks include multimedia parent-order mistakes, fractional TVDPLL factors, fence bit mapping, and display/camera paths failing only under high-rate configurations. Test signals include camera/video/display probes, DP/DVO output rates, VDEC/VENC throughput tests, clk summary parent selection, and fence timeout logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-topckgen2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-ufs_ao.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-ufs_ao.c

### Purpose
`clk-mt8196-ufs_ao.c` registers the MT8196 UFS always-on clock and reset controller. It gates UFSHCI UFS/AES, UniPro TX/RX/SYS/SAP, and PHY SAP clocks, and exposes UFS-related reset lines.

### Important APIs, Types, And Functions
Key objects are `ufsao0_cg_regs`, `ufsao1_cg_regs`, `GATE_UFSAO0`, `GATE_UFSAO1`, `ufsao_clks`, `ufsao_rst_ofs`, `ufsao_rst_idx_map`, `ufsao_rst_desc`, and `ufsao_mcd`. The reset descriptor uses `MTK_RST_SET_CLR` and `RST_NR_PER_BANK`.

### Control Flow, State, And Persistence
`mtk_clk_simple_probe()` registers the clock gates and reset controller for `mediatek,mt8196-ufscfg-ao`. Gate state is stored in UFS AO CG banks, and reset state is controlled through reset set/clear banks at 0x48 and 0x148. The driver has no custom runtime state.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include UFS host/PHY consumers, parent clocks `ufs`, `aes_ufsfde`, and `clk26m`, and reset framework clients. Risks include reset bank indexing errors, storage boot failures if parent clocks are missing, and improper AES clock gating. Test signals include UFS host probe, reset-controller lookups, UFS link training, crypto path operation, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-ufs_ao.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-vdec.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-vdec.c

### Purpose
`clk-mt8196-vdec.c` provides MT8196 video decoder clock gates for the main VDEC system and VDEC SOC companion block. It covers VDEC core, active, engine, LAT, LARB, SOC IPS/APTV, and APTV top clocks.

### Important APIs, Types, And Functions
The file defines multiple CG and HWV register blocks and gate macros `GATE_HWV_VDE20/21/22` and `GATE_HWV_VDE10/11/12/13/14`. Descriptors `vde2_mcd` and `vde1_mcd` set `.need_runtime_pm = true`. Gates use inverted HWV set/clear ops, and LARB clocks carry `CLK_IGNORE_UNUSED`.

### Control Flow, State, And Persistence
OF matching selects `mediatek,mt8196-vdecsys` or `mediatek,mt8196-vdecsys-soc`. The simple helper registers the selected runtime-PM-aware descriptor. Clock state is controlled through hardware voter registers and underlying VDEC CG banks; no custom storage exists.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parent `vdec`, `ck_tck_26m_mx9_ck`, runtime PM, video decoder drivers, and SMI/LARB. Risks include inverted HWV semantics, `CLK_IGNORE_UNUSED` masking missing consumers, and runtime PM ordering around decoder power domains. Test signals include V4L2 decode, LAT/core dual-path operation, runtime PM transitions, HWV completion, and suspend/resume decode recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-vdec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-vdisp_ao.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-vdisp_ao.c

### Purpose
`clk-mt8196-vdisp_ao.c` registers a small MT8196 always-on display clock provider for VDISP AO configuration, DPC, and SMI sub-SOMM0 clocks.

### Important APIs, Types, And Functions
It defines one direct gate bank, one HWV bank, `GATE_MM_AO_V`, `GATE_HWV_MM_V`, `mm_v_clks`, and `mm_v_mcd`. The SMI sub-SOMM0 clock is marked `CLK_IS_CRITICAL`; HWV clocks use `mtk_clk_gate_hwv_ops_setclr`. The platform driver uses `mtk_clk_pdev_probe()`.

### Control Flow, State, And Persistence
The platform provider registers three clocks from the descriptor. DPC and config gates use hardware-voter operations, while the SMI sub-clock uses direct set/clear and is kept critical. State resides in CG/HWV registers only.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parent `disp`, display power management, and SMI/display consumers. Risks include critical-clock misuse, HWV offset errors, and provider matching through OF data with a platform-probe helper. Test signals include display boot with unused-clock cleanup enabled, DPC activity, clk critical flag visibility, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-vdisp_ao.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-venc.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-venc.c

### Purpose
`clk-mt8196-venc.c` registers MT8196 video encoder clocks for three encoder domains: main VENC, VENC C1, and VENC C2. It gates LARB, VENC, JPEG encode/decode, GALS, ADAB/XPC controls, GALS SRAM, and RES_FLAT clocks.

### Important APIs, Types, And Functions
The file defines direct and HWV gate macros for VEN1, VEN2, and VEN_C2 banks. Descriptors `ven1_mcd`, `ven2_mcd`, and `ven_c2_mcd` set `.need_runtime_pm = true`. Some gates use direct inverted set/clear operations; most core gates use HWV inverted operations. `ven1_venc_xpc_ctrl` is marked `CLK_IGNORE_UNUSED`.

### Control Flow, State, And Persistence
OF matching selects one descriptor and the simple helper registers a runtime-PM-aware provider. Gate state is controlled through VENC CG registers and HWV done/set/clear registers. The driver contains no custom sequencing beyond table selection.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parent `venc`, encoder/JPEG drivers, runtime PM, and MT8196 OF bindings. Risks include mixed direct/HWV semantics, inverted set/clear mistakes, unused XPC control handling, and multi-core descriptor mismatches. Test signals include VENC and JPEG encode/decode on all domains, runtime PM cycles, HWV completion, GALS clock behavior, and unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-venc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-vlpckgen.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-vlpckgen.c

### Purpose
`clk-mt8196-vlpckgen.c` implements the MT8196 very-low-power clock generator. It provides VLP fixed factors, many VLP muxes, two VLP audio PLLs, and tuner initialization for always-on and low-power subsystems.

### Important APIs, Types, And Functions
Important pieces are `vlp_divs`, `vlp_muxes`, `vlp_plls`, `vlpckgen_regmap_config`, `clk_mt8196_vlp_probe()`, and `clk_mt8196_vlp_remove()`. It uses a local spinlock for mux registration, `mtk_pll_fenc_clr_set_ops` for `vlp_apll1/2`, regmap writes for tuner defaults, and indexed mux parents for audio clocks.

### Control Flow, State, And Persistence
Probe allocates onecell data for divs, muxes, and PLLs; ioremaps registers; creates a regmap; registers factors, muxes, and PLLs in order; adds the OF provider; then writes APLL tuner defaults. Error paths unwind in reverse. Remove deletes the provider and unregisters PLLs, muxes, and factors.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include `clk-mux.h`, `clk-pll.h`, regmap MMIO, parents from topckgen/APMIXED, and low-power/audio/camera timer consumers. Risks include tuner default mistakes, parent array string issues, HWV/fence bit mismatches, and probe leaks on early ioremap/regmap failures. Test signals include low-power subsystem boot, audio APLL rates, camera TG clocks, regmap tuner values, mux rate changes, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-vlpckgen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-apmixedsys.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-apmixedsys.c

### Purpose
`clk-mt8365-apmixedsys.c` registers MT8365 APMIXED PLLs and two USB/universal gates. It provides root PLLs for CPU, system, multimedia, audio, DSP, APU, storage, and USB clock trees.

### Important APIs, Types, And Functions
The file defines `PLL_B`, `PLL`, PLL divider tables for ARM/MFG/DSP, the `plls` array, and `clk_mt8365_apmixed_probe()`. Probe uses `devm_platform_ioremap_resource()`, `mtk_devm_alloc_clk_data()`, `devm_clk_hw_register_gate()` for `univ_en` and `usb20_en`, `mtk_clk_register_plls()`, and `of_clk_add_hw_provider()`. It is registered with `builtin_platform_driver()`.

### Control Flow, State, And Persistence
As a built-in platform driver, it is available early. Probe maps registers, allocates clock data for all APMIXED IDs, registers two gates, registers PLLs, and adds the provider. Failure after PLL registration unregisters PLLs. Hardware PLL/gate registers persist clock state; devm handles mapped resources and gate objects.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include MT8365 clock bindings, topckgen factors expecting `univ_en`/`usb20_en`, CPUfreq/audio/DSP/APU consumers, and OF. Risks include early boot ordering, no custom remove path, PLL divider table accuracy, and USB parent naming. Test signals include boot provider availability, USB clock operation, PLL rate changes, topckgen parent resolution, and forced provider registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-apmixedsys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-apu.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-apu.c

### Purpose
`clk-mt8365-apu.c` provides MT8365 AI Processing Unit gate clocks for AHB, EDMA, interface, JTAG, AXI, and IPU/APU core clocks.

### Important APIs, Types, And Functions
It defines one set/clear gate bank, `GATE_APU`, `apu_clks`, `apu_desc`, and an OF match table for `mediatek,mt8365-apu`. The driver uses `mtk_clk_simple_probe()` and `mtk_clk_simple_remove()`.

### Control Flow, State, And Persistence
The simple probe registers the APU gate descriptors and exposes them as an OF clock provider. Gate state is stored in the APU CG register block at offsets 0x0/0x4/0x8. There is no custom runtime state or persistence.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parents `ifr_apu_axi`, `apu_sel`, `apu_if_sel`, and `clk26m`, plus APU/IPU consumers. Risks include missing infra parent clocks, incorrect bit positions for core versus bus gates, and APU probe ordering. Test signals include APU driver probe, EDMA/interface clock enables, clk summary parent links, and module unbind/rebind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-apu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-cam.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-cam.c

### Purpose
`clk-mt8365-cam.c` registers MT8365 image/camera system gates for LARB2, camera core, CAMTG, SENIF, CAMSV0/1, FDVT, and WPE.

### Important APIs, Types, And Functions
The file defines `cam_cg_regs`, `GATE_CAM`, `cam_clks`, `cam_desc`, and an OF match table for `mediatek,mt8365-imgsys`. All gates use `mtk_clk_gate_ops_setclr`; probe/remove are delegated to `mtk_clk_simple_probe()` and `mtk_clk_simple_remove()`.

### Control Flow, State, And Persistence
OF matching supplies `cam_desc` to the common helper, which registers the gate clocks and provider. Clock state lives in set/clear/status registers at 0x4/0x8/0x0. No persistent state is maintained.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parent `mm_sel`, camera sensor and image processing drivers, and MT8365 DT bindings. Risks include camera pipeline failures if LARB or SENIF gates are wrong, parent-rate mismatches for CAMTG, and incomplete coverage of WPE/FDVT use. Test signals include camera capture, CAMSV paths, FDVT/WPE activity, SMI/LARB access, and clock debugfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-cam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-mfg.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-mfg.c

### Purpose
`clk-mt8365-mfg.c` registers MT8365 GPU manufacturing clock gates for the BG3D core and MBIST diagnostic clock.

### Important APIs, Types, And Functions
The file defines two gate register banks, `GATE_MFG0` using set/clear ops, `GATE_MFG1` using no-setclr ops, `mfg_clks`, and `mfg_desc`. OF matching uses `mediatek,mt8365-mfgcfg`, and common simple probe/remove do the registration.

### Control Flow, State, And Persistence
Probe registers the two gate descriptors and adds the provider. BG3D uses the normal 0x0/0x4/0x8 gate block, while MBIST uses a direct 0x280 register without set/clear sideband. State is hardware-only.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parents `mfg_sel` and `mbist_diag_sel`, GPU consumers, and MT8365 clock IDs. Risks include no-setclr semantics for MBIST, GPU availability if `mfg_sel` is absent, and diagnostic clocks being rarely tested. Test signals include GPU probe/render, MBIST clock lookup, clk debugfs toggles, and provider unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-mfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-mm.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-mm.c

### Purpose
`clk-mt8365-mm.c` provides MT8365 multimedia gates for MDP, display, DSI/DPI/LVDS, SMI, image relay/async, and 26 MHz HRTWT clocks.

### Important APIs, Types, And Functions
Two gate banks are defined by `mm0_cg_regs` and `mm1_cg_regs`; `GATE_MM0` and `GATE_MM1` fill `mm_clks`. The descriptor `mm_desc` is selected by a platform device ID table and registered via `mtk_clk_pdev_probe()`.

### Control Flow, State, And Persistence
The platform helper registers all multimedia gates and publishes the provider. Gate state is in MM0/MM1 hardware set/clear/status registers. The driver contains no custom runtime PM or persistent software state.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parents `mm_sel`, `dpi0_sel`, `dsi0_lntc_dsick`, `vpll_dpix`, and `lvdstx_dig_cts`, plus DRM/MDP/camera consumers. Risks include display output parent naming, SMI/LARB gating errors, and platform-device creation from the SoC clock controller. Test signals include display modeset, MDP operations, DSI/DPI/LVDS outputs, SMI access, and clk debugfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-vdec.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-vdec.c

### Purpose
`clk-mt8365-vdec.c` registers MT8365 video decoder gates for the decoder core and LARB1.

### Important APIs, Types, And Functions
It defines two inverted set/clear gate banks, `GATE_VDEC0`, `GATE_VDEC1`, `vdec_clks`, and `vdec_desc`. OF matching selects the descriptor for `mediatek,mt8365-vdecsys`; probe/remove use the common simple helpers.

### Control Flow, State, And Persistence
The simple probe registers two gates and exposes the OF clock provider. Both gates use `mtk_clk_gate_ops_setclr_inv`, so enable/disable interpretation is inverted relative to normal gates. State is stored in the VDEC hardware registers only.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parent `mm_sel`, video decoder consumers, and SMI/LARB. Risks include inverted gate semantics, minimal table size masking missing decoder clocks, and LARB gating leading to DMA faults. Test signals include V4L2 decode, LARB access during decode, clock enable-count checks, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-vdec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-venc.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-venc.c

### Purpose
`clk-mt8365-venc.c` registers MT8365 video encoder gates for the VENC core and JPEG encoder.

### Important APIs, Types, And Functions
The file defines `venc_cg_regs`, `GATE_VENC`, `venc_clks`, and `venc_desc`. Gates use `mtk_clk_gate_ops_setclr_inv`. OF matching uses `mediatek,mt8365-vencsys`, and registration is via `mtk_clk_simple_probe()`.

### Control Flow, State, And Persistence
Probe registers the two inverted gates and publishes them as an OF provider. Clock state persists only in the VENC CG register block; the driver has no custom state or runtime PM logic.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parent `mm_sel`, VENC/JPEG consumers, and MT8365 clock bindings. Risks include inverted gate modeling, missing auxiliary encoder bus clocks, and JPEG-only paths not being exercised. Test signals include video encode, JPEG encode, clk summary state, runtime open/close cycles, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-venc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365.c

### Purpose
`clk-mt8365.c` is the main MT8365 clock controller driver. It describes topckgen, infracfg, pericfg, and mcucfg clocks including fixed clocks, PLL-derived factors, top muxes, composite audio/misc muxes, dividers, top gates, infra gates, pericfg gate, and MCU bus mux.

### Important APIs, Types, And Functions
Key tables are `top_fixed_clks`, `top_divs`, many parent arrays, `top_misc_muxes`, `top_muxes`, `mcu_muxes`, `top_adj_divs`, `top_clk_gates`, `ifr_clks`, `peri_clks`, and descriptors `topck_desc`, `infra_desc`, `peri_desc`, `mcu_desc`. It uses `mtk_mux`, `mtk_composite`, `mtk_gate`, `mtk_clk_divider`, and a shared spinlock.

### Control Flow, State, And Persistence
`mtk_clk_simple_probe()` selects a descriptor from OF compatibles `mt8365-topckgen`, `mt8365-infracfg`, `mt8365-pericfg`, or `mt8365-mcucfg`, then registers the relevant tables. Hardware mux, divider, and gate registers retain current clock configuration; the driver stores no nonvolatile data.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include APMIXED PLL names (`mainpll`, `univ_en`, `apll*`, etc.), syscon/regmap-ready clock infrastructure, peripheral drivers, and MT8365 bindings. Risks include large parent-order tables, critical flags on AXI/DXCC/SPM/MCU clocks, duplicate-looking divider lines, and cross-provider parent resolution. Test signals include complete boot without unresolved parents, UART/storage/USB/audio/display/camera/APU probes, CPU bus rate behavior, and clk tree validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8516-apmixedsys.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8516-apmixedsys.c

### Purpose
`clk-mt8516-apmixedsys.c` registers MT8516 APMIXED PLLs: ARMPLL, MAINPLL, UNIVPLL, MMPLL, APLL1, and APLL2. These are root inputs for the MT8516 top clock tree and audio/multimedia subsystems.

### Important APIs, Types, And Functions
The file defines `PLL_B`, `PLL`, `mmpll_div_table`, `plls`, and `clk_mt8516_apmixed_probe()`. Probe uses `devm_platform_ioremap_resource()`, `mtk_devm_alloc_clk_data()`, `mtk_clk_register_plls()`, and `of_clk_add_hw_provider()`. The driver is registered using `builtin_platform_driver()`.

### Control Flow, State, And Persistence
As a built-in driver, probe maps registers early, allocates clock data, registers PLLs, and publishes the provider. On provider registration failure, it unregisters PLLs. PLL control, power, post-divider, tuner, and PCW fields are stored in hardware registers; no software persistence is kept.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include MT8516 clock bindings, topckgen consumers, `clk-pll.h`, OF, and early platform probing. Risks include PLL max frequency limits, reset-bar bit modeling, MMPLL divider table accuracy, and lack of explicit remove cleanup. Test signals include topckgen parent resolution, audio PLL rate generation, CPU/main PLL rates, boot ordering, and forced error-path tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8516-apmixedsys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8516-aud.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8516-aud.c

### Purpose
`clk-mt8516-aud.c` registers MT8516 audio subsystem gates for AFE, I2S, 22 MHz, 24 MHz, internal direction/SPDIF, APLL tuners, HDMI, ADC, DAC, DAC pre-distortion, and TML clocks.

### Important APIs, Types, And Functions
The file defines a no-setclr audio gate bank, `GATE_AUD`, `aud_clks`, `aud_desc`, and an OF match for `mediatek,mt8516-audsys`. It uses `mtk_clk_gate_ops_no_setclr` and common `mtk_clk_simple_probe()`/`remove()`.

### Control Flow, State, And Persistence
Probe registers the audio gates and publishes the provider. Gates are controlled through a direct register at offset 0x0 with no set/clear sideband. State is hardware-only and no runtime PM logic is implemented locally.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parents from MT8516 topckgen such as `clk26m_ck`, `i2s_infra_bck`, `rg_aud_engen1/2`, `rg_aud_spdif_in`, and APLL dividers. Risks include no-setclr races, parent naming mismatches, and tuner clocks being required before audio stream start. Test signals include ALSA playback/capture, SPDIF/HDMI audio, APLL tuner enables, clk summary, and suspend/resume audio.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8516-aud.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8516.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8516.c

### Purpose
`clk-mt8516.c` is the main MT8516 top and infra clock controller. It defines fixed clocks, PLL-derived factors, top muxes, infra muxes, audio dividers, top gates, and descriptors for topckgen and infracfg.

### Important APIs, Types, And Functions
Important data includes `fixed_clks`, `top_divs`, large parent arrays, `top_muxes`, `ifr_muxes`, `top_adj_divs`, `top_clks`, `topck_desc`, and `infra_desc`. It uses `mtk_composite`, `mtk_clk_divider`, `mtk_gate`, a shared `mt8516_clk_lock`, and the common MediaTek simple clock probe.

### Control Flow, State, And Persistence
OF matching selects `mediatek,mt8516-topckgen` or `mediatek,mt8516-infracfg`. The common helper registers the selected table sets and exposes the provider. Top muxes and gates are init-data heavy but registered into the clock framework; hardware registers hold mux/divider/gate state. No nonvolatile state is stored.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include APMIXED PLL names, `clk26m`, many peripheral consumers, and MT8516 binding IDs. Risks include very sparse parent arrays with `clk_null`, no-setclr/inverted gate variations, audio divider chains, and parent name compatibility with old DTs. Test signals include boot provider resolution, UART/I2C/MSDC/USB/Ethernet/audio probes, audio divider rate checks, NAND/NFI paths, and clk tree dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8516.c -->
