# subset-b-001102 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-cam.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-cam.c

## Purpose
`clk-mt8188-cam.c` provides the MT8188 camera clock-controller drivers for the main CAMSYS block and its RAW/YUV sub-blocks. It maps multiple device-tree compatibles to gate-only clock descriptors used by the camera pipeline.

## Important APIs, Types, And Functions
The file defines `cam_cg_regs`, per-domain `struct mtk_gate` arrays for main, raw A/B, and yuv A/B clocks, and `struct mtk_clk_desc` instances. `cam_sys_rst_desc` exposes CAM reset lines from `mt8188-resets.h`. The platform driver binds `mediatek,mt8188-camsys`, `camsys-rawa`, `camsys-rawb`, `camsys-yuva`, and `camsys-yuvb` through `mtk_clk_simple_probe()`/`mtk_clk_simple_remove()`.

## Control Flow, State, And Persistence
Probe is data-driven: OF match selects one descriptor, the common MediaTek helper maps registers, allocates onecell clock storage, registers gates, optional reset support for the main descriptor, and publishes clocks to OF consumers. Persistent kernel state is the registered clock hardware, gate register offsets, and reset-controller metadata until driver remove unregisters it.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include `clk-gate`, `clk-mtk`, `clk-mt8188` IDs, CAM reset bindings, and camera DT nodes. Risks are incorrect parent names such as top camera clocks, wrong gate bit positions, or reset maps that break camera sensor/ISP bring-up. Test signals include DT binding probe for all five compatibles, `clk_summary` CAM gate visibility, reset-controller use by camera drivers, and camera stream start/stop power gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-cam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-ccu.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-ccu.c

## Purpose
`clk-mt8188-ccu.c` registers the MT8188 camera control unit clock gate. It is a small gate-only provider for the CCU subsystem.

## Important APIs, Types, And Functions
The driver defines `ccu_cg_regs`, `ccu_clks`, and `ccu_desc`, then exposes them through a platform driver matching `mediatek,mt8188-ccusys`. The only runtime entry points are `mtk_clk_simple_probe()` and `mtk_clk_simple_remove()`.

## Control Flow, State, And Persistence
At probe, the generic MediaTek simple clock helper maps the CCU register resource, registers the gate clock with parent `top_ccu`, and installs an OF clock provider. The state is limited to clock hardware registration and the gate bit stored in the CCU register block.

## Dependencies, Integration Points, Risks, And Test Signals
It depends on `clk-mtk.h`, `clk-gate.h`, and MT8188 clock IDs. Integration is through CCU device-tree consumers in camera firmware/control paths. Risks are mostly DT compatible mismatches or a wrong parent/gate bit causing CCU firmware timeouts. Tests should confirm provider probe, CCU clock lookup, and camera control-unit enable/disable paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-ccu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-img.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-img.c

## Purpose
`clk-mt8188-img.c` supplies MT8188 image subsystem clocks for the main IMGSYS block, three WPE islands, and DIP top/NR blocks. These gates feed image processing engines used by camera and post-processing pipelines.

## Important APIs, Types, And Functions
Important definitions are `imgsys_cg_regs`, gate arrays for `imgsys_main`, `wpe1`, `wpe2`, `wpe3`, `imgsys1_dip_top`, and `imgsys1_dip_nr`, plus matching `mtk_clk_desc` objects. `img_sys_rst_desc` provides reset-controller metadata for image subsystem reset IDs. The OF table maps six MT8188 image compatibles to those descriptors.

## Control Flow, State, And Persistence
The platform driver delegates to `mtk_clk_simple_probe()`, so descriptor data controls register mapping, gate registration, optional reset registration, and OF clock publication. The registered clocks persist as common-clock-framework providers until remove unwinds them.

## Dependencies, Integration Points, Risks, And Test Signals
The file integrates with image, WPE, and DIP device-tree nodes and common MediaTek gate operations. Risks include missing sub-block compatibles, wrong WPE/DIP gate bank offsets, and reset index drift against bindings. Test signals include successful probe of all IMGSYS nodes, WPE/DIP driver clock acquisition, reset line behavior, and image workload suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-img.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-imp_iic_wrap.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-imp_iic_wrap.c

## Purpose
`clk-mt8188-imp_iic_wrap.c` registers MT8188 infrastructure I2C wrapper clocks for central, west, and east/north wrapper regions. These gates enable the SoC's distributed I2C controller wrappers.

## Important APIs, Types, And Functions
The file defines one register layout `imp_iic_wrap_cg_regs`, three gate arrays, and descriptors `imp_iic_wrap_c_desc`, `imp_iic_wrap_w_desc`, and `imp_iic_wrap_en_desc`. The OF table binds `mediatek,mt8188-imp-iic-wrap-c`, `-w`, and `-en` to the common simple clock probe/remove helpers.

## Control Flow, State, And Persistence
Probe is table-driven. The selected descriptor tells the common helper which gates exist under the matched wrapper node; the helper registers them and publishes a onecell provider. No persistent software state beyond registered clocks is maintained.

## Dependencies, Integration Points, Risks, And Test Signals
It depends on MT8188 clock IDs and I2C wrapper DT nodes. Integration consumers are I2C controllers that need wrapper bus clocks before transfer. Risks include regional compatible naming differences and parent clock mistakes that produce silent I2C probe or transfer failures. Tests should cover I2C adapters in each wrapper region, clock lookup, and runtime suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-imp_iic_wrap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-infra_ao.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-infra_ao.c

## Purpose
`clk-mt8188-infra_ao.c` implements the MT8188 always-on infrastructure clock provider. It exposes a large set of infra gates for security, DMA, UART, SPI, PWM, I2C, thermal, debug, and bus fabric functions that must often remain available early or during low-power transitions.

## Important APIs, Types, And Functions
The driver defines five `mtk_gate_regs` banks, an `infra_ao_clks` array with critical flags on essential clocks, `infra_ao_rst_desc` for reset-controller integration, and `infra_ao_desc`. It matches `mediatek,mt8188-infracfg-ao` and uses `mtk_clk_simple_probe()`/`remove()`.

## Control Flow, State, And Persistence
The simple probe registers gate clocks from all infra AO banks and the reset controller described by `infra_ao_rst_desc`. `CLK_IS_CRITICAL` entries are retained by the CCF and should not be disabled by unused-clock cleanup. State persists in hardware gate bits and reset-controller registration until remove.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include `mt8188-resets.h`, infra clock IDs, and many peripheral consumers. Risks are high because disabling a critical infra clock can break interrupt, security, bus, or debug access; reset-map mismatches can reset the wrong block. Test signals include boot with unused-clock cleanup, peripheral probe across UART/SPI/I2C/PWM, reset-controller consumers, suspend/resume, and `clk_summary` showing critical infra clocks protected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-infra_ao.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-ipe.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-ipe.c

## Purpose
`clk-mt8188-ipe.c` registers MT8188 Image Processing Engine clocks for FD, FE, RSC, DPE, and IPE top paths.

## Important APIs, Types, And Functions
The file defines `ipe_cg_regs`, `ipe_clks`, `ipe_sys_rst_desc`, and `ipe_desc`. It matches `mediatek,mt8188-ipesys` and delegates probe/remove to the generic MediaTek simple clock helpers.

## Control Flow, State, And Persistence
Probe maps the IPE register region, registers each gate clock, publishes the OF provider, and registers reset lines from the descriptor. Runtime state is limited to the clock provider, gate bits, and reset metadata.

## Dependencies, Integration Points, Risks, And Test Signals
Integration points are IPE imaging drivers and reset-controller consumers. Risks include incorrect `top_ipe` parentage, reset ID drift, and gate coverage omissions that only appear under specific camera/vision workloads. Test signals include IPE device probe, reset assertions, clock enable counts during image processing, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-ipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-mfg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-mfg.c

## Purpose
`clk-mt8188-mfg.c` provides the MT8188 GPU manufacturing/MFG clock gate provider.

## Important APIs, Types, And Functions
It defines `mfgcfg_cg_regs`, one `mfgcfg_clks` gate using `CLK_SET_RATE_PARENT`, and `mfgcfg_desc`. The platform driver matches `mediatek,mt8188-mfgcfg` and uses `mtk_clk_simple_probe()`/`remove()`.

## Control Flow, State, And Persistence
The common probe registers the MFG gate and publishes it as an OF clock provider. `CLK_SET_RATE_PARENT` lets GPU clock changes propagate to the selected parent path. There is no custom state beyond the registered clock.

## Dependencies, Integration Points, Risks, And Test Signals
The file integrates with GPU/devfreq consumers and topckgen MFG mux handling. Risks include rate propagation bugs, wrong gate polarity, or topckgen notifier mismatch leading to GPU hangs during PLL changes. Test signals include GPU driver clock acquisition, rate changes, devfreq transitions, and clean disable on GPU idle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-mfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-peri_ao.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-peri_ao.c

## Purpose
`clk-mt8188-peri_ao.c` registers MT8188 always-on peripheral gates for Ethernet MAC/PHY, flash, and PCIe-related paths.

## Important APIs, Types, And Functions
The file defines `peri_ao_cg_regs`, `peri_ao_clks`, and `peri_ao_desc`, binding `mediatek,mt8188-pericfg-ao` through `mtk_clk_simple_probe()` and `mtk_clk_simple_remove()`.

## Control Flow, State, And Persistence
Probe registers the gate table against the pericfg AO register block and publishes clocks for peripheral consumers. State persists only as common-clock-framework registrations and hardware gate bits.

## Dependencies, Integration Points, Risks, And Test Signals
Consumers include Ethernet, flash, and PCIe controller nodes. Risks are incorrect gate bits or parent names that break device probe only when those peripherals are enabled in DT. Tests should include peripheral probe, link bring-up where applicable, unused-clock cleanup, and suspend/resume retention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-peri_ao.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-topckgen.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-topckgen.c

## Purpose
`clk-mt8188-topckgen.c` implements the MT8188 top clock generator. It owns fixed clocks, fixed factors, muxes, adjustable dividers, top-level gates, and the special GPU fast-reference mux path used by many downstream subsystem clock providers.

## Important APIs, Types, And Functions
Key data includes `mt8188_clk_lock`, `top_fixed_clks`, `top_divs`, many parent arrays, `top_mtk_muxes`, `top_adj_divs`, and `top_clks`. `clk_mt8188_reg_mfg_mux_notifier()` installs a mux notifier that bypasses MFG fast reference changes to `TOP_MFG_CORE_TMP`. `clk_mt8188_topck_probe()` manually calls `mtk_clk_register_fixed_clks()`, `mtk_clk_register_factors()`, `mtk_clk_register_muxes()`, `devm_clk_hw_register_mux()`, `mtk_clk_register_composites()`, `mtk_clk_register_gates()`, and `of_clk_add_hw_provider()`.

## Control Flow, State, And Persistence
Probe allocates `CLK_TOP_NR_CLK` onecell storage, ioremaps the topckgen resource, registers clock classes in dependency order, adds the special `mfg_ck_fast_ref` mux at offset `0x250`, registers the MFG mux notifier, then publishes the OF provider. Error paths unwind gates, composites, muxes, factors, fixed clocks, and clock data in reverse order. Remove deletes the OF provider and performs the same reverse unregistration.

## Dependencies, Integration Points, Risks, And Test Signals
This is a root integration point for nearly every MT8188 clock consumer: camera, display, image, video, audio, USB, I2C, storage, Ethernet, and GPU. Risks include parent-array index mistakes, critical clock flags on bus/display paths, non-linear parent index arrays for DP/eDP, and incomplete unwind after a mid-probe failure. Test signals include boot clock provider registration, `clk_summary` parent/rate sanity, GPU frequency changes exercising the notifier, display/audio/storage peripheral probes, and unused-clock cleanup preserving critical gates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-topckgen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-vdec.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-vdec.c

## Purpose
`clk-mt8188-vdec.c` provides MT8188 video decoder clocks for SoC and decoder-core domains.

## Important APIs, Types, And Functions
The driver defines three gate register banks, `vdec1_clks`, `vdec2_clks`, and descriptors `vdec1_desc` and `vdec2_desc`. The OF table maps `mediatek,mt8188-vdecsys-soc` and `mediatek,mt8188-vdecsys` to those descriptors.

## Control Flow, State, And Persistence
The simple MediaTek probe registers the matched decoder gate set and publishes it to OF. There is no software persistence beyond clock registrations and hardware gate state.

## Dependencies, Integration Points, Risks, And Test Signals
Consumers are V4L2/media decoder drivers. Risks include split-domain ordering, wrong lat/active gate selection, and parent clock mismatches causing decode hangs. Test signals include decoder probe, stream decode start/stop, power-domain transitions, and clock gating during suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-vdec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-vdo0.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-vdo0.c

## Purpose
`clk-mt8188-vdo0.c` registers MT8188 VDO0 display output clocks for overlay, RDMA, WDMA, color, DSC, DSI, DPI, DP/eDP, and related mutex paths.

## Important APIs, Types, And Functions
It defines three VDO0 gate banks, `vdo0_clks`, and `vdo0_desc`. The driver uses `mtk_clk_pdev_probe()`/`mtk_clk_pdev_remove()` rather than the simpler helper, matching `mediatek,mt8188-vdosys0`.

## Control Flow, State, And Persistence
The platform-device clock helper registers the descriptor's gates and stores provider state for removal. Some gates use `CLK_SET_RATE_PARENT`, such as eDP-related paths, allowing display rate requests to propagate upward.

## Dependencies, Integration Points, Risks, And Test Signals
Integration points are DRM display pipelines, DSI/eDP/DPI output nodes, and multimedia power domains. Risks include display blanking from wrong gate bits, rate-parent propagation mistakes, and missing gates for rarely used output paths. Test signals include DRM modeset, multiple output combinations, suspend/resume, and clock enable counts during display pipeline enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-vdo0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-vdo1.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-vdo1.c

## Purpose
`clk-mt8188-vdo1.c` provides MT8188 VDO1 clocks for the second display/video-output fabric, including merge, padding, DSC, DP interface, HDMI/eDP/HDCP, and related split paths.

## Important APIs, Types, And Functions
The file defines six VDO1 gate register banks, a large `vdo1_clks` table, `vdo1_desc`, and the platform driver for `mediatek,mt8188-vdosys1`. It uses `mtk_clk_pdev_probe()` and `mtk_clk_pdev_remove()`. `CLK_SET_RATE_PARENT` appears on the DP interface gate.

## Control Flow, State, And Persistence
Probe registers all VDO1 gates through the MediaTek platform-device helper and publishes the provider. State is the onecell clock data and hardware gate bits; remove unregisters the provider and gates.

## Dependencies, Integration Points, Risks, And Test Signals
Consumers are DRM display and external display paths, especially DP/HDMI/eDP/HDCP blocks. Risks are high for multi-output display because gate-bank offsets and parent names must match the hardware data sheet. Test signals include DP/HDMI/eDP modesets, HDCP paths if enabled, unused-clock cleanup, and display suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-vdo1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-venc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-venc.c

## Purpose
`clk-mt8188-venc.c` registers MT8188 video encoder clock gates.

## Important APIs, Types, And Functions
The driver defines `venc1_cg_regs`, `venc1_clks`, `venc1_desc`, and an OF match for `mediatek,mt8188-vencsys`. Probe/remove are delegated to `mtk_clk_simple_probe()` and `mtk_clk_simple_remove()`.

## Control Flow, State, And Persistence
The common helper registers encoder gates and publishes them as a onecell provider. There is no custom persistence or runtime policy in this file.

## Dependencies, Integration Points, Risks, And Test Signals
Consumers are encoder/media drivers and the parent top VENC clock muxes. Risks include gate bit mistakes that appear only when encoding starts. Test signals include video encode workloads, encoder device probe, power-domain transitions, and idle gate disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-venc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-vpp0.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-vpp0.c

## Purpose
`clk-mt8188-vpp0.c` registers MT8188 Video Post Processing 0 clocks for display/video composition, scaler, RDMA/WROT, padding, mutex, and related pipeline functions.

## Important APIs, Types, And Functions
The file defines three VPP0 gate banks, `vpp0_clks`, and `vpp0_desc`, then binds `mediatek,mt8188-vppsys0` through `mtk_clk_pdev_probe()`/`remove()`.

## Control Flow, State, And Persistence
Probe registers the VPP0 gate table and OF provider through the pdev helper. Runtime state is only the registered clocks and gate bits, with no policy beyond CCF enable/disable requests from consumers.

## Dependencies, Integration Points, Risks, And Test Signals
Integration includes DRM/display and video post-processing consumers. Risks include gate coverage gaps in complex display pipelines and bad parent names that break rate propagation. Tests should exercise display composition, rotation/writeback, video post-processing, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-vpp0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-vpp1.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-vpp1.c

## Purpose
`clk-mt8188-vpp1.c` provides MT8188 Video Post Processing 1 clocks for the second post-processing/display fabric, including split, merge, scaler, VPP padding, and WPE/VPP links.

## Important APIs, Types, And Functions
It defines two VPP1 gate banks, `vpp1_clks`, `vpp1_desc`, and the `mediatek,mt8188-vppsys1` platform driver using `mtk_clk_pdev_probe()`/`mtk_clk_pdev_remove()`.

## Control Flow, State, And Persistence
The pdev helper registers the gate table and publishes the OF clock provider. Gate state is persisted only in hardware registers and the CCF while the driver is bound.

## Dependencies, Integration Points, Risks, And Test Signals
Consumers are display/video post-processing and WPE-linked paths. Risks include multi-bank gate offset errors and integration mismatches with VDO/VPP parent clocks. Test signals include VPP1 pipeline enablement, WPE/VPP workloads, display suspend/resume, and `clk_summary` gate toggling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-vpp1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-wpe.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-wpe.c

## Purpose
`clk-mt8188-wpe.c` registers MT8188 Warp Engine clocks for top and VPP0-connected WPE domains.

## Important APIs, Types, And Functions
The driver defines top and VPP0 gate register layouts, `wpe_top_clks`, `wpe_vpp0_clks`, descriptors `wpe_top_desc` and `wpe_vpp0_desc`, and OF matches `mediatek,mt8188-wpesys` plus `mediatek,mt8188-wpesys-vpp0`.

## Control Flow, State, And Persistence
`mtk_clk_simple_probe()` registers the gates associated with the matched WPE node and publishes a onecell provider. State is the gate registration and hardware gate bits; remove unwinds through the simple helper.

## Dependencies, Integration Points, Risks, And Test Signals
Integration is with image/WPE drivers and VPP-connected processing paths. Risks include split-domain confusion between top and VPP0 clock sets and wrong parent linkage to top WPE/VPP muxes. Test signals include WPE workload start/stop, image pipeline probe, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-wpe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-apmixedsys.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-apmixedsys.c

## Purpose
`clk-mt8192-apmixedsys.c` registers MT8192 analog mixed-signal PLL clocks and AP mixed gates. It is the PLL/root-frequency provider for the rest of the MT8192 clock tree.

## Important APIs, Types, And Functions
The file defines `apmixed_cg_regs`, `apmixed_clks`, `plls`, and frequency-hopping metadata `pllfhs`. `clk_mt8192_apmixed_probe()` allocates `CLK_APMIXED_NR_CLK` storage, registers PLLFH-backed PLLs with `mtk_clk_register_pllfhs()`, registers gates, and publishes an OF provider for `mediatek,mt8192-apmixedsys`.

## Control Flow, State, And Persistence
Probe creates clock data, registers PLLFH PLLs before gates, adds the OF provider, and stores driver data. Failures unwind gates, PLLFH registrations, and clock data. Remove deletes the provider and unregisters gates and PLLFH clocks.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include `clk-pllfh`, `clk-mtk`, MT8192 PLL IDs, and topckgen consumers. Risks are significant because PLL table errors affect all derived rates; missing unwind can leave published root clocks inconsistent. Test signals include boot rate summaries, frequency-hopping behavior if enabled, parent rates for topckgen, and module remove/reprobe in test kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-apmixedsys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-aud.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-aud.c

## Purpose
`clk-mt8192-aud.c` provides MT8192 audio subsystem clocks for AFE, I2S, memory interface, DAC/ADC, TDM, and related audio paths.

## Important APIs, Types, And Functions
The driver defines three audio gate banks, `aud_clks`, `aud_desc`, and custom `clk_mt8192_aud_probe()`/`remove()`. Probe wraps `mtk_clk_simple_probe()` and calls `mt8192_mmsys_clk_register()` for cross-subsystem audio/display clock integration; remove calls `mt8192_mmsys_clk_unregister()` before simple removal.

## Control Flow, State, And Persistence
Audio gate registration is handled by the simple helper. Additional MMSYS clock registration is layered after successful simple probe and explicitly unwound on failure or remove. State includes audio clock provider data and the auxiliary MMSYS registration.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include `clk-mtk`, audio DT consumers, and the MT8192 MMSYS clock hook. Risks include asymmetry between audio and mmsys registration and audio paths failing only under display/audio shared-clock scenarios. Test signals include ALSA probe/playback/capture, I2S/TDM paths, MMSYS registration failure injection, and remove/reprobe cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-aud.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-cam.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-cam.c

## Purpose
`clk-mt8192-cam.c` registers MT8192 camera clocks for the main CAMSYS block and RAW A/B/C sub-blocks.

## Important APIs, Types, And Functions
Definitions include `cam_cg_regs`, gate arrays for main and raw blocks, descriptors `cam_desc`, `cam_rawa_desc`, `cam_rawb_desc`, `cam_rawc_desc`, and OF compatibles `mediatek,mt8192-camsys`, `camsys_rawa`, `camsys_rawb`, and `camsys_rawc`.

## Control Flow, State, And Persistence
`mtk_clk_simple_probe()` selects the descriptor from the OF match data, registers the gates, and publishes an OF provider. No custom state or reset handling is present in this file.

## Dependencies, Integration Points, Risks, And Test Signals
It integrates with camera sensor/ISP nodes and MT8192 top camera parents. Risks are compatible-string underscore differences, raw-domain gate omissions, and parent name mismatches. Test signals include camera probe, raw pipeline capture, runtime PM gate toggling, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-cam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-img.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-img.c

## Purpose
`clk-mt8192-img.c` registers MT8192 image subsystem clocks for two image-system nodes.

## Important APIs, Types, And Functions
The file defines `img_cg_regs`, `img_clks`, `img2_clks`, and descriptors `img_desc` and `img2_desc`. It binds `mediatek,mt8192-imgsys` and `mediatek,mt8192-imgsys2` through the simple MediaTek clock helpers.

## Control Flow, State, And Persistence
Probe registers the matched image gate table and publishes a onecell provider. The driver maintains no extra state beyond CCF registrations.

## Dependencies, Integration Points, Risks, And Test Signals
Consumers are image processing and camera pipeline drivers. Risks include choosing the wrong descriptor for the second image node or top image parent drift. Tests include image pipeline probe, clock lookup for both nodes, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-img.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-imp_iic_wrap.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-imp_iic_wrap.c

## Purpose
`clk-mt8192-imp_iic_wrap.c` provides MT8192 I2C wrapper clock gates across central, east, north, south, west, and west-south wrapper regions.

## Important APIs, Types, And Functions
It defines a shared `imp_iic_wrap_cg_regs`, per-region gate arrays, and descriptors for C/E/N/S/W/WS. The OF table maps six `mediatek,mt8192-imp_iic_wrap_*` compatibles to those descriptors.

## Control Flow, State, And Persistence
The generic simple probe registers the region-specific gate set for the matched wrapper node and installs the OF provider. State is limited to CCF clock registrations and hardware gate bits.

## Dependencies, Integration Points, Risks, And Test Signals
Integration consumers are I2C adapter nodes spread across the SoC. Risks include region-compatible mismatches and missing wrapper gates causing only some I2C buses to fail. Test signals include probing every enabled I2C bus, transfer tests in each region, runtime PM, and unused-clock cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-imp_iic_wrap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-ipe.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-ipe.c

## Purpose
`clk-mt8192-ipe.c` registers MT8192 Image Processing Engine clocks.

## Important APIs, Types, And Functions
The file defines `ipe_cg_regs`, `ipe_clks`, `ipe_desc`, and the `mediatek,mt8192-ipesys` OF match. Runtime operations are `mtk_clk_simple_probe()` and `mtk_clk_simple_remove()`.

## Control Flow, State, And Persistence
The selected descriptor is registered by the simple helper, creating gate clocks and an OF provider. The file has no reset controller or custom persistence.

## Dependencies, Integration Points, Risks, And Test Signals
It depends on IPE clock IDs and top IPE parent clocks. Risks include gate-bit drift and missing clocks for DPE/FD/FE workloads. Test signals include IPE device probe, image workload execution, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-ipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-mdp.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-mdp.c

## Purpose
`clk-mt8192-mdp.c` registers MT8192 Media Data Path clocks for MDP RDMA, Rsz, WROT, TDSHP, mutex, and related processing blocks.

## Important APIs, Types, And Functions
The driver defines two MDP gate banks, `mdp_clks`, `mdp_desc`, and an OF match for `mediatek,mt8192-mdpsys`. It uses `mtk_clk_simple_probe()` and `mtk_clk_simple_remove()`.

## Control Flow, State, And Persistence
Probe registers the MDP gate table and publishes the provider. No additional software state is kept.

## Dependencies, Integration Points, Risks, And Test Signals
Consumers include MDP and multimedia pipeline drivers. Risks include wrong gate-bank offsets affecting only specific processing units and parent mismatch with top MDP muxes. Test signals include MDP transform workloads, probe of all MDP blocks, and runtime PM transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-mdp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-mfg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-mfg.c

## Purpose
`clk-mt8192-mfg.c` provides the MT8192 GPU MFG clock gate.

## Important APIs, Types, And Functions
The file defines `mfg_cg_regs`, one `mfg_clks` gate with `CLK_SET_RATE_PARENT`, `mfg_desc`, and the `mediatek,mt8192-mfgcfg` OF match.

## Control Flow, State, And Persistence
The simple helper registers the MFG gate and publishes it to OF. Rate changes may propagate to the parent because of the gate flag. State is limited to the registered clock and gate bit.

## Dependencies, Integration Points, Risks, And Test Signals
Integration is with GPU drivers and the MT8192 topckgen MFG mux notifier. Risks include GPU hangs during rate switch if parent bypass/notifier behavior is wrong. Test signals include GPU probe, devfreq rate changes, and idle clock gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-mfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-mm.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-mm.c

## Purpose
`clk-mt8192-mm.c` registers MT8192 multimedia/display subsystem clocks.

## Important APIs, Types, And Functions
It defines three MM gate banks, `mm_clks`, and `mm_desc`. The driver uses `mtk_clk_pdev_probe()`/`mtk_clk_pdev_remove()` for the `mediatek,mt8192-mmsys` platform device.

## Control Flow, State, And Persistence
The pdev helper registers display/multimedia gates and the OF provider from descriptor data. State is the clock provider and hardware gate bits until remove.

## Dependencies, Integration Points, Risks, And Test Signals
Consumers are DRM and multimedia blocks, including display pipeline components. Risks include gate ordering and bank offsets causing blank display or failed component binding. Test signals include DRM modeset, display pipeline enable/disable, suspend/resume, and clock summary inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-msdc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-msdc.c

## Purpose
`clk-mt8192-msdc.c` registers MT8192 MSDC top clocks for eMMC/SD storage controller support.

## Important APIs, Types, And Functions
The file defines `msdc_top_cg_regs`, `msdc_top_clks`, `msdc_top_desc`, and the OF compatible `mediatek,mt8192-msdc_top`. It uses the simple MediaTek clock helper pair.

## Control Flow, State, And Persistence
Probe registers storage-related gates and publishes the provider. Persistent state is only the registered CCF clocks and hardware gate state.

## Dependencies, Integration Points, Risks, And Test Signals
Consumers are MMC/SD/eMMC host controller nodes and top storage clock parents. Risks include storage boot failures if critical bus/storage gates are wrong. Test signals include rootfs-on-eMMC boot, SD card probe, high-speed mode negotiation, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-msdc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-scp_adsp.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-scp_adsp.c

## Purpose
`clk-mt8192-scp_adsp.c` registers the MT8192 SCP/ADSP clock gate.

## Important APIs, Types, And Functions
The driver defines `scp_adsp_cg_regs`, a one-entry `scp_adsp_clks` table, `scp_adsp_desc`, and OF compatible `mediatek,mt8192-scp_adsp`.

## Control Flow, State, And Persistence
`mtk_clk_simple_probe()` registers the gate clock and OF provider. There is no custom state or reset handling.

## Dependencies, Integration Points, Risks, And Test Signals
Integration consumers are SCP and ADSP firmware/remoteproc paths. Risks include firmware boot failure if the gate parent or bit is wrong. Test signals include SCP/ADSP remoteproc boot, audio DSP use, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-scp_adsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-vdec.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-vdec.c

## Purpose
`clk-mt8192-vdec.c` provides MT8192 video decoder clocks for core and SoC decoder domains.

## Important APIs, Types, And Functions
The file defines three decoder gate banks, `vdec_clks`, `vdec_soc_clks`, descriptors `vdec_desc` and `vdec_soc_desc`, and OF matches `mediatek,mt8192-vdecsys` and `mediatek,mt8192-vdecsys_soc`.

## Control Flow, State, And Persistence
The simple probe registers the matched decoder-domain gates and publishes an OF provider. State is limited to the common clock registrations and hardware gate bits.

## Dependencies, Integration Points, Risks, And Test Signals
Consumers are media decoder drivers and power-domain code. Risks include split core/SOC domain gate mistakes causing decode hangs. Test signals include V4L2 decode, power-domain cycling, and clock disable on decoder idle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-vdec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-venc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-venc.c

## Purpose
`clk-mt8192-venc.c` registers MT8192 video encoder clocks.

## Important APIs, Types, And Functions
It defines `venc_cg_regs`, `venc_clks`, `venc_desc`, and OF compatible `mediatek,mt8192-vencsys`. Probe/remove are the common simple helper functions.

## Control Flow, State, And Persistence
The helper registers encoder gates and publishes them to OF; remove unregisters them. No additional state is kept.

## Dependencies, Integration Points, Risks, And Test Signals
Integration is with V4L2/media encoder drivers and top VENC parent muxes. Risks include gate bit drift and missing clocks for encoder sub-blocks. Test signals include encode workloads, probe/remove, runtime PM, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-venc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192.c

## Purpose
`clk-mt8192.c` is the aggregate MT8192 main clock driver for topckgen, infracfg, and pericfg nodes. It defines root fixed clocks, top-level fixed factors, muxes, composites, gates, infra/peri gates, reset metadata, and GPU mux-notifier behavior.

## Important APIs, Types, And Functions
Major data includes `mt8192_clk_lock`, `top_fixed_clks`, `top_divs`, many parent arrays, `top_mtk_muxes`, `top_muxes`, infra/peri/top gate tables, `clk_rst_desc`, and three `mtk_clk_desc` objects. `clk_mt8192_reg_mfg_mux_notifier()` locates `CLK_TOP_MFG_PLL_SEL` in the mux table and registers a notifier with bypass index 0 to switch to the 26 MHz crystal during MFG parent changes.

## Control Flow, State, And Persistence
OF match data selects between `mediatek,mt8192-infracfg`, `mediatek,mt8192-pericfg`, and `mediatek,mt8192-topckgen`. `mtk_clk_simple_probe()` uses the selected descriptor to register fixed clocks, factors, muxes, composites, gates, reset controllers, and the optional notifier. Registered clocks persist as OF providers until simple remove unwinds them.

## Dependencies, Integration Points, Risks, And Test Signals
This file is a central MT8192 integration point for bus, storage, display, image, camera, audio, USB, UFS, SPI/I2C, video, ADSP, and GPU clocks. Risks include parent order mismatches, critical infra gate flags, reset-controller map errors, and the MFG notifier failing to protect GPU PLL switching. Test signals include full boot with unused-clock cleanup, peripheral probe matrix, reset-controller consumers, GPU devfreq transitions, `clk_summary` topology checks, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-apmixedsys.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-apmixedsys.c

## Purpose
`clk-mt8195-apmixedsys.c` registers MT8195 AP mixed-signal PLL clocks and AP mixed gates. It supplies root PLLs and frequency-hopping-capable clock hardware to the rest of the MT8195 tree.

## Important APIs, Types, And Functions
The file defines AP mixed gate registers, `apmixed_clks`, `plls`, and `pllfhs`. `clk_mt8195_apmixed_probe()` allocates `CLK_APMIXED_NR_CLK` storage, calls `fhctl_parse_dt()` for `mediatek,mt8195-fhctl`, registers PLLFH clocks and gates, and publishes an OF provider for `mediatek,mt8195-apmixedsys`.

## Control Flow, State, And Persistence
Probe parses FHCTL metadata before registering PLLFH clocks, then registers gates and the provider. Error handling and remove unwind gates, PLLFH registrations, and clock data in reverse order. State consists of PLL hardware registrations, frequency hopping metadata, gates, and OF provider data.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include `clk-pllfh`, FHCTL DT, MT8195 clock IDs, and topckgen consumers. Risks include root PLL rate errors, FHCTL mismatch, and provider publication failures leaving downstream clocks unavailable. Test signals include topckgen parent rates, PLL rate changes, FHCTL-enabled boot, clock summary checks, and remove/reprobe cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-apmixedsys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-apusys_pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-apusys_pll.c

## Purpose
`clk-mt8195-apusys_pll.c` provides MT8195 AI Processing Unit PLL clocks.

## Important APIs, Types, And Functions
It defines `apusys_plls`, `clk_mt8195_apusys_pll_probe()`, `clk_mt8195_apusys_pll_remove()`, and the OF match `mediatek,mt8195-apusys_pll`. Probe uses `mtk_clk_register_plls()` rather than PLLFH registration.

## Control Flow, State, And Persistence
Probe allocates `CLK_APUSYS_PLL_NR_CLK` onecell data, registers APUSYS PLL hardware, publishes the OF provider, and stores driver data. Failure and remove paths unregister PLLs and free clock data after deleting the provider.

## Dependencies, Integration Points, Risks, And Test Signals
Consumers are APUSYS/NPU drivers and their power/clock domains. Risks include PLL rate table errors, provider absence causing AI accelerator probe deferral, and missing remove cleanup. Test signals include APUSYS probe, PLL rate requests, clock summary validation, and module remove/reprobe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-apusys_pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-cam.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-cam.c

## Purpose
`clk-mt8195-cam.c` registers MT8195 camera clocks for main, MRAW, RAW A/B, and YUV A/B camera domains.

## Important APIs, Types, And Functions
The file defines `cam_cg_regs`, six gate arrays, six descriptors, and OF matches for `mediatek,mt8195-camsys`, `camsys_mraw`, `camsys_rawa`, `camsys_rawb`, `camsys_yuva`, and `camsys_yuvb`. It uses the common simple probe/remove helpers.

## Control Flow, State, And Persistence
The selected descriptor drives gate registration and OF provider creation. There is no reset-controller descriptor in this file; state is limited to the registered clocks and gate bits.

## Dependencies, Integration Points, Risks, And Test Signals
Integration is with MT8195 camera/ISP drivers and top camera parent muxes. Risks include compatible underscore naming, split raw/yuv domain mistakes, and missing MRAW gates. Test signals include camera capture over raw/yuv paths, MRAW use, runtime PM, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-cam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-ccu.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-ccu.c

## Purpose
`clk-mt8195-ccu.c` registers MT8195 camera control unit clocks.

## Important APIs, Types, And Functions
It defines `ccu_cg_regs`, `ccu_clks`, `ccu_desc`, and OF compatible `mediatek,mt8195-ccusys`. Runtime operations are `mtk_clk_simple_probe()` and `mtk_clk_simple_remove()`.

## Control Flow, State, And Persistence
Probe registers CCU gates and publishes the OF provider for camera-control consumers. No extra state is stored beyond the common clock provider.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies are CCU DT nodes, MT8195 clock IDs, and top CCU parents. Risks include camera firmware/control failures if the CCU clock gate is wrong. Test signals include CCU consumer clock lookup, camera pipeline startup, and runtime suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-ccu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-img.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-img.c

## Purpose
`clk-mt8195-img.c` registers MT8195 image subsystem clocks for main image, DIP top, DIP NR, and WPE image blocks.

## Important APIs, Types, And Functions
The driver defines `img_cg_regs`, gate arrays for `img`, `img1_dip_top`, `img1_dip_nr`, and `img1_wpe`, plus descriptors for each. OF matches include `mediatek,mt8195-imgsys`, `imgsys1_dip_top`, `imgsys1_dip_nr`, and `imgsys1_wpe`.

## Control Flow, State, And Persistence
`mtk_clk_simple_probe()` registers gates for the matched image-domain node and publishes the clock provider. State is the CCF provider and hardware gate bits.

## Dependencies, Integration Points, Risks, And Test Signals
Consumers are image, DIP, and WPE drivers. Risks include compatible-string mismatch and gate omissions in image subdomains. Test signals include image processing workloads, WPE/DIP probe, runtime PM, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-img.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-imp_iic_wrap.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-imp_iic_wrap.c

## Purpose
`clk-mt8195-imp_iic_wrap.c` registers MT8195 I2C wrapper clocks for south and west wrapper regions.

## Important APIs, Types, And Functions
It defines `imp_iic_wrap_cg_regs`, `imp_iic_wrap_s_clks`, `imp_iic_wrap_w_clks`, descriptors for south and west wrappers, and OF matches `mediatek,mt8195-imp_iic_wrap_s` and `mediatek,mt8195-imp_iic_wrap_w`.

## Control Flow, State, And Persistence
The simple probe registers region-specific I2C wrapper gates and publishes a onecell provider. No custom state is maintained.

## Dependencies, Integration Points, Risks, And Test Signals
Integration consumers are I2C controllers in the south and west infrastructure regions. Risks include region mismatch and wrong wrapper parent clocks producing adapter probe failures. Test signals include I2C bus probe/transfer in both regions, runtime PM, and unused-clock cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-imp_iic_wrap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-infra_ao.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-infra_ao.c

## Purpose
`clk-mt8195-infra_ao.c` implements the MT8195 always-on infrastructure clock provider. It covers bus, security, DMA, UART/SPI/I2C, thermal, PMIC, debug, and other infra clocks that support early and low-power operation.

## Important APIs, Types, And Functions
The file defines five infra AO gate banks, a large `infra_ao_clks` table with multiple `CLK_IS_CRITICAL` entries, and `infra_ao_desc` for `mediatek,mt8195-infracfg_ao`. It includes MT8195 reset bindings but does not attach a reset descriptor in the visible descriptor.

## Control Flow, State, And Persistence
`mtk_clk_simple_probe()` registers all infra AO gates and publishes an OF provider. Critical clocks are protected from automatic disable. State persists as hardware gate state and CCF registration until simple remove.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include MT8195 infra clock IDs and many SoC peripheral consumers. Risks are system-wide: a wrong critical flag, parent, or gate bit can break boot, interrupt/security paths, serial console, or PMIC access. Test signals include boot with unused-clock cleanup, serial/I2C/SPI/PWM/thermal probe, suspend/resume, and `clk_summary` critical gate status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-infra_ao.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-ipe.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-ipe.c

## Purpose
`clk-mt8195-ipe.c` registers MT8195 Image Processing Engine clocks.

## Important APIs, Types, And Functions
The file defines `ipe_cg_regs`, `ipe_clks`, `ipe_desc`, and OF compatible `mediatek,mt8195-ipesys`. It uses the common simple probe/remove helpers.

## Control Flow, State, And Persistence
The matched descriptor is registered by `mtk_clk_simple_probe()`, creating gate clocks and an OF provider. There is no custom reset or policy state.

## Dependencies, Integration Points, Risks, And Test Signals
Integration consumers are MT8195 IPE imaging blocks. Risks include gate bit errors and missing parent clocks that only surface under imaging workloads. Test signals include IPE probe, image-processing execution, runtime PM, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-ipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-mfg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-mfg.c

## Purpose
`clk-mt8195-mfg.c` provides the MT8195 GPU MFG clock gate.

## Important APIs, Types, And Functions
It defines `mfg_cg_regs`, one `mfg_clks` entry using `CLK_SET_RATE_PARENT`, `mfg_desc`, and an OF match for `mediatek,mt8195-mfgcfg`.

## Control Flow, State, And Persistence
The simple MediaTek probe registers the MFG gate and publishes it to OF. Rate requests can propagate to the parent clock. No custom state is present.

## Dependencies, Integration Points, Risks, And Test Signals
Integration is with GPU drivers and MT8195 topckgen MFG mux notifier behavior. Risks include GPU hangs during clock-rate changes or wrong gate polarity. Test signals include GPU probe, devfreq transitions, idle gating, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-mfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-peri_ao.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-peri_ao.c

## Purpose
`clk-mt8195-peri_ao.c` registers MT8195 always-on peripheral clocks for Ethernet, flash/NFI/ECC, and PCIe-related functions.

## Important APIs, Types, And Functions
The driver defines `peri_ao_cg_regs`, `peri_ao_clks`, `peri_ao_desc`, and OF compatible `mediatek,mt8195-pericfg_ao`, using `mtk_clk_simple_probe()` and `mtk_clk_simple_remove()`.

## Control Flow, State, And Persistence
Probe registers the peripheral AO gate table and exposes the clocks to OF consumers. State is limited to CCF registration and hardware gate bits.

## Dependencies, Integration Points, Risks, And Test Signals
Consumers include Ethernet, flash, NAND/ECC, and PCIe devices. Risks include rarely tested peripheral gates drifting from DT bindings. Test signals include enabled peripheral probe, link/storage tests, unused-clock cleanup, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-peri_ao.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-scp_adsp.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-scp_adsp.c

## Purpose
`clk-mt8195-scp_adsp.c` registers the MT8195 SCP/ADSP clock gate.

## Important APIs, Types, And Functions
It defines `scp_adsp_cg_regs`, one `scp_adsp_clks` entry, `scp_adsp_desc`, and the OF compatible `mediatek,mt8195-scp_adsp`.

## Control Flow, State, And Persistence
The simple helper registers the gate and publishes the provider. No custom state, reset support, or policy is implemented.

## Dependencies, Integration Points, Risks, And Test Signals
Consumers are SCP/ADSP firmware and remoteproc/audio DSP paths. Risks include firmware boot failure if the gate bit or parent clock is wrong. Test signals include SCP/ADSP boot, DSP workload execution, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-scp_adsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-topckgen.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-topckgen.c

## Purpose
`clk-mt8195-topckgen.c` implements the MT8195 top clock generator. It registers root fixed clocks, fixed factors, muxes, adjustable dividers, top gates, and a special GPU fast-reference mux with notifier protection.

## Important APIs, Types, And Functions
Important state includes `mt8195_clk_lock`, `top_fixed_clks`, `top_divs`, numerous parent arrays, `top_mtk_muxes`, `top_adj_divs`, and `top_clks`. `clk_mt8195_reg_mfg_mux_notifier()` creates an `mtk_mux_nb` with bypass index 0. `clk_mt8195_topck_probe()` manually registers fixed clocks, factors, muxes, the `mfg_ck_fast_ref` mux at offset `0x250`, the notifier, composites, gates, and the OF provider.

## Control Flow, State, And Persistence
Probe allocates `CLK_TOP_NR_CLK` onecell storage, ioremaps registers, registers each clock class in dependency order, then publishes the provider. Errors unwind in reverse order; remove deletes the provider and unregisters gates, composites, muxes, factors, fixed clocks, and clock data.

## Dependencies, Integration Points, Risks, And Test Signals
This root clock provider feeds MT8195 display, camera, image, video, audio, storage, USB, UFS, Ethernet, APUSYS, ADSP, and GPU domains. Risks include parent-table ordering, critical top gate flags, special index arrays, and the MFG fast-reference notifier failing during GPU rate changes. Test signals include full boot clock topology, GPU devfreq, display/audio/storage peripheral probes, unused-clock cleanup, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-topckgen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-vdec.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-vdec.c

## Purpose
`clk-mt8195-vdec.c` registers MT8195 video decoder clocks for primary decoder, core1, and decoder SoC domains.

## Important APIs, Types, And Functions
The file defines three decoder gate register banks, gate arrays `vdec_clks`, `vdec_core1_clks`, and `vdec_soc_clks`, descriptors for each, and OF matches `mediatek,mt8195-vdecsys`, `vdecsys_core1`, and `vdecsys_soc`.

## Control Flow, State, And Persistence
The simple helper registers the matched decoder-domain gates and publishes an OF provider. State persists as CCF clock registrations and gate bits until remove.

## Dependencies, Integration Points, Risks, And Test Signals
Consumers are MT8195 media decoder drivers and power-domain code. Risks include split-domain gate mistakes, decode hangs under core1 workloads, and parent mismatch with top VDEC muxes. Test signals include V4L2 decode on each core/domain, power-domain cycling, idle gating, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-vdec.c -->
