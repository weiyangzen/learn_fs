# subset-b-001099 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/Makefile -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/Makefile

### Purpose
This Makefile maps MediaTek common clock framework Kconfig symbols to the object files that implement shared helpers, PLL/FHCTL support, reset glue, and SoC-specific clock providers. It is the build-time integration table for all MediaTek clock drivers in this directory.

### Important APIs, Types, And Functions
There are no C APIs here, but the important build units are `clk-mtk.o`, `clk-pll.o`, `clk-gate.o`, `clk-apmixed.o`, `clk-cpumux.o`, `reset.o`, `clk-mux.o`, plus optional `clk-fhctl.o` and `clk-pllfh.o`. Per-SoC symbols such as `CONFIG_COMMON_CLK_MT2701`, `CONFIG_COMMON_CLK_MT2712`, `CONFIG_COMMON_CLK_MT6735`, `CONFIG_COMMON_CLK_MT6765`, and `CONFIG_COMMON_CLK_MT6779_*` select the corresponding main or subsystem object files.

### Control Flow, State, And Persistence
The Makefile has no runtime control flow. Its persistent effect is the kernel link composition: common helper objects build under `CONFIG_COMMON_CLK_MEDIATEK`, FHCTL support builds only under `CONFIG_COMMON_CLK_MEDIATEK_FHCTL`, and each SoC/subsystem driver appears only when its matching Kconfig symbol is enabled.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on Kconfig names matching object filenames and on DT bindings selecting compatible drivers at runtime. Risks include missing helper objects causing unresolved symbols, SoC objects omitted from a config, or stale object names after driver renames. Test signals are allmodconfig/allyesconfig builds, per-SoC defconfig builds, and verifying selected objects contain the expected `of_match_table` or platform ID tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-apmixed.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-apmixed.c

### Purpose
`clk-apmixed.c` implements a small common clock provider for the MediaTek `ref2usb_tx` analog clock gate used by APMIXED/USB PHY related hardware. It wraps a raw MMIO control register in a CCF `clk_hw`.

### Important APIs, Types, And Functions
The central type is `struct mtk_ref2usb_tx`, which stores `struct clk_hw` plus a `base_addr`. Exported APIs are `mtk_clk_register_ref2usb_tx()` and `mtk_clk_unregister_ref2usb_tx()`. Clock ops are `mtk_ref2usb_tx_is_prepared()`, `mtk_ref2usb_tx_prepare()`, and `mtk_ref2usb_tx_unprepare()`.

### Control Flow, State, And Persistence
Registration allocates a wrapper, fills `clk_init_data`, and calls `clk_hw_register()`. Prepare sets `REF2USB_TX_EN`, waits 100 microseconds, then sets low-pass-filter and output bits. Unprepare clears the full enable mask. State persists only in the hardware register and the allocated `clk_hw` wrapper until unregister.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on CCF, MMIO `readl/writel`, delay helpers, and the MediaTek clock helpers. Risks are wrong register addresses, missing parent names, and sequencing bugs around the required 100 us delay. Test signals include enable/disable transitions in debugfs clock state, USB PHY bring-up, correct prepared-state reads, and leak-free unregister on probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-apmixed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-cpumux.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-cpumux.c

### Purpose
`clk-cpumux.c` registers MediaTek CPU clock muxes backed by syscon/regmap registers. It gives SoC clock drivers a CCF mux primitive for CPU parent selection while preserving no-reparent rate determination semantics.

### Important APIs, Types, And Functions
`struct mtk_clk_cpumux` stores `clk_hw`, `regmap`, register offset, mask, and shift. Exported APIs are `mtk_clk_register_cpumuxes()` and `mtk_clk_unregister_cpumuxes()`. Internal helpers are `clk_cpumux_get_parent()`, `clk_cpumux_set_parent()`, `mtk_clk_register_cpumux()`, and `mtk_clk_unregister_cpumux()`.

### Control Flow, State, And Persistence
Registration resolves the device node to a regmap, iterates `struct mtk_composite` descriptions, skips duplicate populated IDs, registers each mux, and stores the resulting `clk_hw` in `clk_hw_onecell_data`. On any failure it unregisters already-created muxes in reverse order and marks slots `ERR_PTR(-ENOENT)`. Parent state is read and written through bitfields in persistent SoC registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on syscon/regmap, CCF, `struct mtk_composite`, and DT nodes that expose a regmap. Risks include bad mux widths producing wrong masks, duplicate clock IDs hiding descriptor mistakes, missing syscon setup, and CPU parent switches without voltage/frequency coordination. Test signals are CPU clock parent selection, duplicate-ID warnings, failure unwind coverage, and boot on MT2701/MT2712 CPU mux users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-cpumux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-cpumux.h -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-cpumux.h

### Purpose
This header declares the CPU mux registration interface used by MediaTek SoC clock drivers.

### Important APIs, Types, And Functions
It forward-declares `struct clk_hw_onecell_data`, `struct device_node`, and `struct mtk_composite`, then declares `mtk_clk_register_cpumuxes()` and `mtk_clk_unregister_cpumuxes()`.

### Control Flow, State, And Persistence
The header has no runtime behavior. It defines the compile-time contract: callers provide a device, DT node, composite descriptors, count, and clock data container; unregister receives the same descriptor array and data container.

### Dependencies, Integration Points, Risks, And Test Signals
It integrates `clk-cpumux.c` with SoC drivers such as MT2701. Risks are signature drift between header and implementation or missing includes in users. Test signals are successful compilation of SoC drivers that include it and registration/unregistration coverage through those drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-cpumux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-fhctl.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-fhctl.c

### Purpose
`clk-fhctl.c` implements Frequency Hopping Controller operations for MediaTek PLLFH clocks. It supports spread-spectrum clocking and DDS hopping flows that temporarily hand PLL control to FHCTL hardware.

### Important APIs, Types, And Functions
Public APIs are `fhctl_get_offset_table()`, `fhctl_get_ops()`, and `fhctl_hw_init()`. Important internals include `struct fhctl_offset` tables for V1/V2 register layouts, `fhctl_set_ssc_regs()`, `hopping_hw_flow()`, `fhctl_hopping()`, `fhctl_ssc_enable()`, `__get_postdiv()`, and `__set_postdiv()`.

### Control Flow, State, And Persistence
`fhctl_get_offset_table()` selects register offsets by variant. `fhctl_hopping()` optionally raises postdiv before entering a spinlocked hardware flow, writes current DDS into FHCTL, enables soft-start and hopping control, triggers DVFS DDS, polls monitor DDS for stability, copies the observed DDS back to PLL PCW, and releases FHCTL control. SSC enable programs df/dt/up-down limits and stores `state->ssc_rate`, disabling and restoring SSC around hopping when needed.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `clk-pllfh.h`, `clk-fhctl.h`, `clk-mtk.h`, MMIO, `readl_poll_timeout_atomic()`, PLL postdiv encoding, and caller-provided spinlocks. Risks include timeout during DDS convergence, incorrect offset variant, SSC percentage math errors, postdiv ordering glitches, and lock misuse around MMIO polling. Test signals include successful PLL rate changes, SSC enable/disable persistence, timeout diagnostics from `dump_hw()`, and boot on platforms using `CONFIG_COMMON_CLK_MEDIATEK_FHCTL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-fhctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-fhctl.h -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-fhctl.h

### Purpose
This header exposes the FHCTL variant enum, register-offset layout, and operation accessors for MediaTek PLL frequency hopping support.

### Important APIs, Types, And Functions
It defines `enum fhctl_variant` with `FHCTL_PLLFH_V1` and `FHCTL_PLLFH_V2`, `struct fhctl_offset`, and declarations for `fhctl_get_offset_table()`, `fhctl_get_ops()`, and `fhctl_hw_init()`.

### Control Flow, State, And Persistence
The header has no runtime flow. It provides the data contract used by PLLFH registration code to map logical FH registers to per-variant offsets and to initialize hardware through `struct mtk_fh`.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `clk-pllfh.h` for FH types. Risks are ABI drift with FHCTL implementation or missing fields for future register variants. Test signals are compile coverage under `CONFIG_COMMON_CLK_MEDIATEK_FHCTL` and successful variant table lookup on FH-enabled SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-fhctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-gate.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-gate.c

### Purpose
`clk-gate.c` implements the shared MediaTek gate clock primitive. It supports set/clear/status register layouts, no-setclr read-modify-write layouts, inverted enable polarity, and hardware-voter gate operations.

### Important APIs, Types, And Functions
`struct mtk_clk_gate` stores `clk_hw`, normal and hardware-voter regmaps, and a `struct mtk_gate` descriptor. Exported ops include `mtk_clk_gate_ops_setclr`, `_setclr_inv`, `_no_setclr`, `_no_setclr_inv`, `mtk_clk_gate_hwv_ops_setclr`, and `_hwv_ops_setclr_inv`. Exported registration APIs are `mtk_clk_register_gates()` and `mtk_clk_unregister_gates()`.

### Control Flow, State, And Persistence
Registration resolves a DT node to a regmap and optional hardware-voter regmap, validates duplicate clock IDs, registers each gate with `CLK_SET_RATE_PARENT`, and stores the `clk_hw`. Enable/disable functions either write set/clear registers or update the status register directly, with polarity determined by selected ops. Hardware-voter enable/disable writes HWV set/clear registers and polls done status. Gate state persists in hardware registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on CCF, regmap/syscon, `mtk_clk_get_hwv_regmap()`, `clk-mtk.h`, and `clk-gate.h`. Risks include returning from `mtk_clk_register_gate()` without freeing `cg` if HWV ops lack a regmap, polarity descriptor mistakes, timeout from hardware voters, and partial registration unwinds. Test signals include gate toggles across all ops variants, duplicate-ID warnings, HWV regmap error handling, and `mtk_clk_simple_remove()` unregister paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-gate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-gate.h -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-gate.h

### Purpose
`clk-gate.h` defines the descriptor format and registration API for MediaTek gate clocks.

### Important APIs, Types, And Functions
It declares the exported gate ops, `struct mtk_gate_regs`, `struct mtk_gate`, `GATE_MTK_FLAGS()`, `GATE_MTK()`, `mtk_clk_register_gates()`, and `mtk_clk_unregister_gates()`.

### Control Flow, State, And Persistence
The header has no direct runtime behavior. Its macros produce constant gate descriptors consumed by `clk-gate.c` and by SoC-specific clock tables.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on kernel integer types and CCF declarations. Integration is broad: almost every subsystem clock file in this subset creates `struct mtk_gate` arrays through these macros. Risks are descriptor field omissions, wrong polarity ops, and stale declarations. Test signals are successful compilation and runtime gate registration for each SoC subsystem.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-gate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-aud.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-aud.c

### Purpose
This driver registers MT2701 audio subsystem gates for AFE, I2S, HDMI audio, SPDIF, ASRC, memory interface, and related audio buses.

### Important APIs, Types, And Functions
It defines four `mtk_gate_regs` banks, `GATE_AUDIO0..3` descriptor macros, `audio_clks[]`, and `audio_desc`. `clk_mt2701_aud_probe()` uses `mtk_clk_simple_probe()` then enables selected audio clocks through `clk_prepare_enable()` lookups to satisfy hardware dependencies.

### Control Flow, State, And Persistence
The platform driver matches `mediatek,mt2701-audsys`, registers gates, then explicitly prepares/enables clocks named for audio infrastructure that must stay active. Gate state is held in audsys set/clear/status registers and in CCF prepare counts.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `clk-gate`, `clk-mtk`, MT2701 DT clock IDs, platform devices, and CCF consumer lookups. Risks include failing the post-probe forced-enables, clock-name drift between descriptors and lookups, and audio hangs if critical bus gates are disabled. Test signals include audio playback/capture, HDMI/SPDIF use, probe logs, clock summary prepare counts, and remove/unregister behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-aud.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-bdp.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-bdp.c

### Purpose
This file provides MT2701 BDPSYS gate clocks for video/display processing blocks such as BRZ, BLS, WDMA, and TVD-related paths.

### Important APIs, Types, And Functions
It defines `bdp0_cg_regs`, `bdp1_cg_regs`, `GATE_BDP0/1`, the `bdp_clks[]` descriptor table, `bdp_desc`, and a `module_platform_driver()` using `mtk_clk_simple_probe`.

### Control Flow, State, And Persistence
On a `mediatek,mt2701-bdpsys` platform device, the simple probe registers all gates into the DT onecell provider. Runtime enable/disable uses set/clear/status register banks; no additional persistent software state is kept.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on DT binding IDs, `clk-gate`, `clk-mtk`, and consumers in display/video pipelines. Risks are wrong parent clocks, swapped gate banks, and missing consumers causing display/video failures. Test signals are successful BDPSYS probe, enabling display/video consumers, and clock summary transitions during multimedia use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-bdp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-eth.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-eth.c

### Purpose
This driver registers MT2701 Ethernet subsystem gates and reset controller metadata.

### Important APIs, Types, And Functions
It defines `eth_cg_regs`, `GATE_ETH`, `eth_clks[]`, reset bank offset `rst_ofs[] = { 0x34 }`, `clk_rst_desc`, `eth_desc`, and a simple platform driver for `mediatek,mt2701-ethsys`.

### Control Flow, State, And Persistence
Probe registers Ethernet gates and reset support through `mtk_clk_simple_probe()`. Gate bits persist in the ETHSYS register block; reset state is controlled through the shared MediaTek reset descriptor.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `clk-gate`, `clk-mtk`, reset helpers, DT IDs, and Ethernet/MII consumers. Risks include reset bank offset errors, gate polarity mistakes, and parent mismatch for `ethif_sel`. Test signals include Ethernet MAC probe, link bring-up, reset controller users, and runtime gate toggling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-eth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-g3d.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-g3d.c

### Purpose
This file registers the MT2701 G3D/GPU subsystem gate and reset controller.

### Important APIs, Types, And Functions
It defines `g3d_cg_regs`, `GATE_G3D`, a single-entry `g3d_clks[]`, reset offset `rst_ofs[] = { 0xc }`, `clk_rst_desc`, `g3d_desc`, and a platform driver matching `mediatek,mt2701-g3dsys`.

### Control Flow, State, And Persistence
Simple probe installs the GPU clock provider and reset controller. Runtime CCF calls manipulate the gate register, and reset consumers use the described reset bank.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on GPU DT consumers, the MediaTek gate/reset helpers, and the top-level `mfg_sel` parent. Risks are a wrong reset offset or gate bit preventing GPU power-on. Test signals are GPU driver probe, reset assertion/deassertion, and clock enable state in debugfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-g3d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-hif.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-hif.c

### Purpose
This driver registers MT2701 HIFSYS gates for high-speed interface blocks, including USB and host interface clocks, and exposes a reset bank.

### Important APIs, Types, And Functions
It defines `hif_cg_regs`, `GATE_HIF`, `hif_clks[]`, `rst_ofs[] = { 0x34 }`, `clk_rst_desc`, `hif_desc`, and a simple driver for `mediatek,mt2701-hifsys`.

### Control Flow, State, And Persistence
Probe uses `mtk_clk_simple_probe()` to register the gate table and reset descriptor. Hardware register bits persist gate state; no custom software state exists beyond CCF registrations.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on USB/HIF consumers, DT IDs, and MediaTek common gate/reset code. Risks are reset offset mismatches and disabled HIF clocks blocking USB/host devices. Test signals include USB/HIF enumeration, reset controller use, and clock enable/disable under consumer activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-hif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-img.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-img.c

### Purpose
This file provides MT2701 IMGSYS gates for image-processing paths.

### Important APIs, Types, And Functions
It defines `img_cg_regs`, `GATE_IMG`, `img_clks[]`, `img_desc`, and an OF platform driver matching `mediatek,mt2701-imgsys`.

### Control Flow, State, And Persistence
`mtk_clk_simple_probe()` registers the gate descriptors as a onecell provider. Gate state is persisted by the IMGSYS set/clear/status registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on image pipeline consumers, DT clock IDs, and `clk-gate`. Risks include wrong parent `mm_sel`/multimedia source assumptions and missing gates for imaging blocks. Test signals include camera/image pipeline probe, CCF lookup by DT index, and runtime gate toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-img.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-mm.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-mm.c

### Purpose
This driver registers MT2701 multimedia display/DDP gates.

### Important APIs, Types, And Functions
It defines display gate register banks `disp0_cg_regs` and `disp1_cg_regs`, `GATE_DISP0/1`, `mm_clks[]`, `mm_desc`, a platform ID table carrying `mm_desc`, and a driver using `mtk_clk_pdev_probe()`.

### Control Flow, State, And Persistence
The platform-ID based probe registers the gate table rather than matching an OF table directly in this file. Gate state persists in MMSYS display clock-gate registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on platform device creation by display/MMSYS code, `clk-gate`, and multimedia consumers. Risks include ID-table mismatches, absent platform device instantiation, and wrong gate bank selection. Test signals are DDP/display probe, pdev clock provider registration, and display pipeline clock summary changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-vdec.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-vdec.c

### Purpose
This file registers MT2701 video decoder subsystem gates.

### Important APIs, Types, And Functions
It defines `vdec0_cg_regs`, `vdec1_cg_regs`, `GATE_VDEC0/1`, `vdec_clks[]`, `vdec_desc`, and a platform driver for `mediatek,mt2701-vdecsys`.

### Control Flow, State, And Persistence
Simple probe registers VDEC gates through `mtk_clk_simple_probe()`. Enable/disable state persists in the VDECSYS gate registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on video decoder consumers, DT IDs, and common gate helpers. Risks include wrong active-low polarity or parent `vdec_sel` mismatches causing decoder timeouts. Test signals include vcodec decoder probe, decode workload clocks, and debugfs clock state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-vdec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701.c

### Purpose
`clk-mt2701.c` is the main MT2701 clock provider. It covers topckgen fixed clocks, PLL-derived factors, top muxes/dividers/gates, infra CPU mux and gates, pericfg gates/muxes/resets, and APMIXED PLLs.

### Important APIs, Types, And Functions
Important data includes `top_fixed_clks[]`, `top_fixed_divs[]`, many parent arrays, `cpu_muxes[]`, `top_muxes[]`, `top_adj_divs[]`, `top_clks[]`, `infra_clks[]`, `infra_fixed_divs[]`, `peri_clks[]`, `peri_muxs[]`, `apmixed_plls[]`, and `apmixed_fixed_divs[]`. Probe dispatch functions are `mtk_topckgen_init()`, `mtk_infrasys_init_early()`, `mtk_infrasys_init()`, `mtk_pericfg_init()`, `mtk_apmixedsys_init()`, and `clk_mt2701_probe()`.

### Control Flow, State, And Persistence
The driver registers at `arch_initcall()` so core clocks appear early. `mtk_topckgen_init()` maps topckgen, allocates clock data, registers fixed/factor/composite/divider/gate clocks, and publishes an OF provider. Infrasys has an early `CLK_OF_DECLARE_DRIVER` path to register fixed factors and CPU muxes with placeholder slots, then the platform probe completes gates and reset registration. Pericfg registers peripheral gates, UART muxes, and resets. APMIXED registers PLLs and one HDMI reference factor. Clock state persists in hardware mux, divider, gate, PLL, and reset registers plus the global `infra_clk_data` pointer.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on DT bindings, `clk-mtk`, `clk-pll`, `clk-gate`, `clk-cpumux`, reset helpers, and CCF provider registration. Risks include early/late infrasys ordering, duplicated descriptor lines, unchecked registration helper return values, critical clock flags on AXI/MEM/RTC, PLL parameter mistakes, and reset-bank errors. Test signals are full MT2701 boot, CPU parent switching, peripheral probe coverage, reset controller users, clock debugfs hierarchy, and failure-injection of provider registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-apmixedsys.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-apmixedsys.c

### Purpose
This driver registers MT2712 APMIXED PLL clocks and performs a small amount of PLL control register initialization.

### Important APIs, Types, And Functions
It defines the MT2712 PLL descriptor macro/table `plls[]`, `clk_mt2712_apmixed_probe()`, an OF table for `mediatek,mt2712-apmixedsys`, and a remove path that unregisters PLLs.

### Control Flow, State, And Persistence
Probe maps the APMIXED resource, allocates devm clock data, registers PLLs, publishes the onecell provider, then writes selected AP PLL control bits. Remove unregisters the PLL table. PLL state persists in APMIXED hardware registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `clk-pll`, `clk-mtk`, CCF provider APIs, and MT2712 clock IDs. Risks include wrong PLL PCW/postdiv metadata, control writes that disturb firmware-initialized state, and missing unregister on partial failures. Test signals are PLL rate reads/changes, topckgen factor parents resolving, provider registration, and module unload/reload on modular builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-apmixedsys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-bdp.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-bdp.c

### Purpose
This file provides MT2712 BDPSYS gate clocks for block display/video processing functions.

### Important APIs, Types, And Functions
It defines `bdp_cg_regs`, `GATE_BDP`, `bdp_clks[]`, `bdp_desc`, and a simple platform driver matching `mediatek,mt2712-bdpsys`.

### Control Flow, State, And Persistence
Probe delegates to `mtk_clk_simple_probe()` to register the gate table. Gate state persists in BDPSYS set/clear/status registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on display/video consumers, DT clock bindings, and common MediaTek gate helpers. Risks are bit-shift mismatches and parent clock changes affecting display timing. Test signals include BDPSYS probe, display/video workloads, and CCF gate transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-bdp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-img.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-img.c

### Purpose
This driver registers MT2712 image subsystem gates.

### Important APIs, Types, And Functions
It defines `img_cg_regs`, `GATE_IMG`, `img_clks[]`, `img_desc`, and a simple platform driver for `mediatek,mt2712-imgsys`.

### Control Flow, State, And Persistence
The simple probe registers image gates and publishes the provider. Runtime gate state persists in IMGSYS registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on image/camera consumers and the shared gate framework. Risks include missing or incorrect `mm_sel` parent relationships and wrong gate polarity. Test signals include image pipeline probe, camera use, and clock summary gate state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-img.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-jpgdec.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-jpgdec.c

### Purpose
This file registers the MT2712 JPEG decoder subsystem gate.

### Important APIs, Types, And Functions
It defines `jpgdec_cg_regs`, `GATE_JPGDEC`, `jpgdec_clks[]`, `jpgdec_desc`, and a simple platform driver for `mediatek,mt2712-jpgdecsys`.

### Control Flow, State, And Persistence
Probe registers the JPEG decoder gate provider. The only meaningful runtime state is the gate bit in the JPGDEC register block.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on JPEG decoder consumers, DT bindings, and `clk-gate`. Risks are wrong parent `jpgdec_sel` or bit shift causing decoder access failures. Test signals are JPEG decoder probe/use and CCF enable/disable traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-jpgdec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-mfg.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-mfg.c

### Purpose
This driver registers the MT2712 MFG/GPU gate clock.

### Important APIs, Types, And Functions
It defines `mfg_cg_regs`, `GATE_MFG`, `mfg_clks[]`, `mfg_desc`, and an OF platform driver for `mediatek,mt2712-mfgcfg`.

### Control Flow, State, And Persistence
Simple probe registers the single GPU gate. Gate state persists in the MFGCFG register block.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on GPU consumers and the top-level `mfg_sel` clock. Risks include a wrong gate bit preventing GPU initialization. Test signals include GPU driver probe, runtime GPU clocks, and debugfs gate state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-mfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-mm.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-mm.c

### Purpose
This file registers MT2712 multimedia display/DDP gate clocks.

### Important APIs, Types, And Functions
It defines three gate register banks `mm0_cg_regs`, `mm1_cg_regs`, `mm2_cg_regs`, `GATE_MM0/1/2`, `mm_clks[]`, `mm_desc`, a platform ID table, and a driver using `mtk_clk_pdev_probe()`.

### Control Flow, State, And Persistence
The pdev probe uses the ID table data to register the MMSYS gate provider. Gate state persists across MM register banks with active-low set/clear semantics.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on platform-device creation by MMSYS/display code and downstream DDP consumers. Risks include ID table mismatches, mis-banked gates, and parent `mm_sel`/`dpi` interactions. Test signals include display pipeline probe, MDP/DDP workloads, and clock enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-vdec.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-vdec.c

### Purpose
This driver registers MT2712 video decoder gates split across two register banks.

### Important APIs, Types, And Functions
It defines `vdec0_cg_regs`, `vdec1_cg_regs`, `GATE_VDEC0/1`, `vdec_clks[]`, `vdec_desc`, and an OF driver for `mediatek,mt2712-vdecsys`.

### Control Flow, State, And Persistence
Simple probe publishes VDEC gates. Enable/disable state persists in VDECSYS gate registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on video decoder consumers and `vdec_sel` parent clocks. Risks are incorrect bank selection and disabled LARB/decoder clocks during codec operation. Test signals include decoder probe, decode sessions, and clock debugfs state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-vdec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-venc.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-venc.c

### Purpose
This file registers MT2712 video encoder gates.

### Important APIs, Types, And Functions
It defines `venc_cg_regs`, `GATE_VENC`, `venc_clks[]`, `venc_desc`, and a platform driver matching `mediatek,mt2712-vencsys`.

### Control Flow, State, And Persistence
Probe delegates to `mtk_clk_simple_probe()` to register VENC gates. Gate state persists in the VENC register block.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on video encoder consumers and the top-level `venc_sel` parent. Risks include wrong active-low gate behavior or missing encoder/LARB gating. Test signals include encoder probe, encode workloads, and CCF gate transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-venc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712.c

### Purpose
`clk-mt2712.c` is the main MT2712 top/infrastructure/peripheral/MCU clock provider. It models fixed roots, PLL factors, a large top mux table, MCU CPU/bus muxes, audio dividers/gates, infra gates, peri gates, and reset descriptors.

### Important APIs, Types, And Functions
Important tables include `top_fixed_clks[]`, `top_divs[]`, extensive parent arrays, `top_muxes[]`, `mcu_muxes[]`, `top_adj_divs[]`, `top_clks[]`, `infra_clks[]`, `peri_clks[]`, `clk_rst_desc[]`, and descriptors `topck_desc`, `mcu_desc`, `infra_desc`, `peri_desc`. The driver uses `mtk_clk_simple_probe()` with match data for `mediatek,mt2712-infracfg`, `-mcucfg`, `-pericfg`, and `-topckgen`.

### Control Flow, State, And Persistence
Probe is descriptor-driven: the common simple probe allocates clock data, maps resources, registers fixed/factor/composite/divider/gate groups as listed in the matching descriptor, registers reset controllers for infra/peri, and publishes the onecell provider. Runtime state persists in topckgen mux/divider/gate registers, MCU mux registers, infra/peri gate registers, and reset banks.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on MT2712 DT bindings, `clk-mtk`, `clk-gate`, reset helpers, and consumers across CPU, display, storage, audio, Ethernet, and peripheral subsystems. Risks include descriptor typos, critical-clock flag mistakes, unusual duplicated/extra braces visible in the source, parent names that must match the APMIXED PLL provider, and reset bank map errors. Test signals include full MT2712 boot, CPU cluster mux operation, storage/audio/display/Ethernet probe, reset controller users, and `clk_summary` topology validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-apmixedsys.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-apmixedsys.c

### Purpose
This driver registers MT6735 APMIXED PLLs such as ARMPLL, MAINPLL, UNIVPLL, MMPLL, MSDCPLL, VENCPLL, TVDPLL, and APLL1/2.

### Important APIs, Types, And Functions
It defines PLL register offsets, `PLL()` descriptor macro, `apmixedsys_plls[]`, `clk_mt6735_apmixed_probe()`, `clk_mt6735_apmixed_remove()`, and an OF table for `mediatek,mt6735-apmixedsys`.

### Control Flow, State, And Persistence
Probe maps APMIXED MMIO, allocates devm onecell data sized to the PLL table, registers PLLs, stores clock data in driver data, and registers the provider. Remove unregisters PLLs. PLL configuration persists in AP PLL registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `clk-pll`, DT binding IDs, and topckgen factor/mux parents. Risks include table size not matching binding ID range, wrong PCW/tuner metadata, and missing unwind after provider failure. Test signals include PLL parent resolution by topckgen, rate calculations, remove path execution, and MT6735 boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-apmixedsys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-imgsys.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-imgsys.c

### Purpose
This file registers MT6735 image subsystem gates.

### Important APIs, Types, And Functions
It defines `IMG_CG_*` offsets, `imgsys_cg_regs`, `imgsys_gates[]`, `imgsys_clks`, and a simple driver for `mediatek,mt6735-imgsys`.

### Control Flow, State, And Persistence
Simple probe registers the image gate table and provider; remove uses `mtk_clk_simple_remove()`. Gate state persists in IMGSYS set/clear/status registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on MT6735 image consumers, binding IDs, and the common gate framework. Risks include parent name mismatches and bit-shift mistakes. Test signals include image/camera pipeline clock requests and gate toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-imgsys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-infracfg.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-infracfg.c

### Purpose
This driver registers MT6735 infrastructure gates and a mapped reset controller for infracfg resets.

### Important APIs, Types, And Functions
It defines infra reset/gate offsets, `infracfg_gates[]`, reset bank `infracfg_rst_bank_ofs[]`, logical-to-bank `infracfg_rst_idx_map[]`, `infracfg_resets`, `infracfg_clks`, and a simple platform driver for `mediatek,mt6735-infracfg`.

### Control Flow, State, And Persistence
The simple probe registers gate clocks and reset controller using the descriptor. Gate state persists in infra PDN registers; reset state persists in the INFRA reset bank with logical reset IDs translated by `rst_idx_map`.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on DT clock/reset bindings, reset consumers, and common gate/reset helpers. Risks include incorrect reset ID mapping, critical APXGPT gating, and shared infra clocks being disabled by consumers. Test signals include infracfg provider registration, reset-controller users, timer stability, and peripheral probe coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-infracfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-mfgcfg.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-mfgcfg.c

### Purpose
This file registers MT6735 MFG/GPU configuration gates and reset metadata.

### Important APIs, Types, And Functions
It defines MFG gate offsets, `mfgcfg_cg_regs`, `mfgcfg_gates[]`, `mfgcfg_clks`, and an OF driver for `mediatek,mt6735-mfgcfg`.

### Control Flow, State, And Persistence
Simple probe registers the MFG clock provider and any descriptor reset support. Gate state persists in MFGCFG registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on GPU consumers and MT6735 binding IDs. Risks include wrong parent `mfg_sel` and gate polarity mistakes. Test signals include GPU probe, clock enable during rendering, and simple remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-mfgcfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-pericfg.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-pericfg.c

### Purpose
This driver registers MT6735 peripheral gates and a two-bank peripheral reset controller.

### Important APIs, Types, And Functions
It defines `pericfg_gates[]`, `pericfg_rst_bank_ofs[]`, `pericfg_rst_idx_map[]`, `pericfg_resets`, `pericfg_clks`, and a simple driver for `mediatek,mt6735-pericfg`.

### Control Flow, State, And Persistence
Simple probe registers peripheral gate clocks and reset controller. Gate state persists in PERI PDN registers; resets persist in `PERI_GLOBALCON_RST0/RST1` and are exposed through the index map.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on UART/I2C/SPI/MSDC/USB/PWM consumers, DT reset bindings, and the common reset layer. Risks include reset-map mistakes, disabling active serial/storage clocks, and parent mux name mismatches. Test signals include peripheral enumeration, reset toggles, serial console stability, and simple remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-pericfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-topckgen.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-topckgen.c

### Purpose
This file implements MT6735 topckgen clocks: modeled fixed roots, PLL factors, and top-level muxes for AXI, memory, multimedia, storage, audio, display PWM, and peripheral clock domains.

### Important APIs, Types, And Functions
It defines CLK_CFG register offsets, `mt6735_topckgen_lock`, `topckgen_fixed_clks[]`, `topckgen_factors[]`, many parent arrays, `topckgen_muxes[]`, `topckgen_desc`, and a simple platform driver for `mediatek,mt6735-topckgen`.

### Control Flow, State, And Persistence
The descriptor-driven simple probe registers fixed clocks, fixed factors, and muxes with clear/set/update semantics. Mux state persists in topckgen CLK_CFG registers and is protected by the topckgen spinlock.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on APMIXED PLL parent names, `clk-mux`, `clk-mtk`, and consumers in nearly every MT6735 subsystem. Risks include several modeled fixed clocks with unknown or zero rates, bad update-bit metadata, and parent name drift from PLL providers. Test signals include `clk_summary` topology, rate propagation into pericfg/imgsys/vcodec consumers, storage/display/audio bring-up, and mux parent switching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-topckgen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-vdecsys.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-vdecsys.c

### Purpose
This driver registers MT6735 video decoder gates, including decoder and SMI/LARB related gates.

### Important APIs, Types, And Functions
It defines `vdec_cg_regs`, `smi_larb1_cg_regs`, `vdecsys_gates[]`, `vdecsys_clks`, and a simple driver for `mediatek,mt6735-vdecsys`.

### Control Flow, State, And Persistence
Simple probe registers VDECSYS gates and remove unregisters them. Gate state persists in decoder and SMI LARB register banks.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on video decoder and memory interconnect consumers. Risks include missing LARB gates causing DMA faults and wrong bank offsets. Test signals include decoder probe, media decode workloads, and SMI/larb clock dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-vdecsys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-vencsys.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-vencsys.c

### Purpose
This file registers MT6735 video encoder subsystem gates.

### Important APIs, Types, And Functions
It defines VENC gate offsets, `venc_cg_regs`, `vencsys_gates[]`, `vencsys_clks`, and an OF driver for `mediatek,mt6735-vencsys`.

### Control Flow, State, And Persistence
Simple probe registers VENC gates and the onecell provider; remove unregisters them. Gate state persists in VENC set/clear/status registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on video encoder consumers, topckgen `vencpll` derived parents, and common gate code. Risks include gate bit mistakes and missing clocks during encode. Test signals include encoder probe/workload and clock debugfs transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-vencsys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-audio.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-audio.c

### Purpose
This driver registers MT6765 audio subsystem gates for AFE, I2S, TDM, ASRC, and audio front-end paths.

### Important APIs, Types, And Functions
It defines `audio0_cg_regs`, `audio1_cg_regs`, `GATE_AUDIO0/1`, `audio_clks[]`, `audio_desc`, and a simple platform driver matching `mediatek,mt6765-audsys`.

### Control Flow, State, And Persistence
Simple probe registers audio gates as a DT onecell provider. Gate state persists in audio subsystem set/clear/status registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on audio consumers, MT6765 clock IDs, and top-level audio mux/factor parents. Risks include disabling shared AFE/I2S clocks or parent name mismatches. Test signals include ALSA probe/playback/capture and clock summary enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-cam.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-cam.c

### Purpose
This file registers MT6765 camera subsystem gate clocks.

### Important APIs, Types, And Functions
It defines `cam_cg_regs`, `GATE_CAM`, `cam_clks[]`, `cam_desc`, and a simple driver for `mediatek,mt6765-camsys`.

### Control Flow, State, And Persistence
Simple probe publishes CAMSYS gates; runtime clock enable/disable manipulates the CAM register bank.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on camera sensor/image pipeline consumers and top-level camera muxes. Risks include gate bit mistakes and missing sensor interface clocks. Test signals include camera pipeline probe, streaming, and clock debugfs state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-cam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-img.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-img.c

### Purpose
This driver registers MT6765 image subsystem gates.

### Important APIs, Types, And Functions
It defines `img_cg_regs`, `GATE_IMG`, `img_clks[]`, `img_desc`, and a simple driver for `mediatek,mt6765-imgsys`.

### Control Flow, State, And Persistence
Simple probe registers image gates and provider. Gate state persists in IMGSYS registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on image processing consumers and `mm_ck`/top-level parents. Risks include wrong bit shifts and missing image clocks. Test signals include image pipeline use and CCF gate state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-img.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-mipi0a.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-mipi0a.c

### Purpose
This file registers the MT6765 MIPI0A subsystem gate, used by camera/MIPI PHY related blocks.

### Important APIs, Types, And Functions
It defines `mipi0a_cg_regs`, `GATE_MIPI0A`, `mipi0a_clks[]`, `mipi0a_desc`, and a simple driver for `mediatek,mt6765-mipi0a`.

### Control Flow, State, And Persistence
Probe registers the single gate provider. State persists in the MIPI0A gate register.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on camera/MIPI consumers and the APMIXED 26 MHz gates in the main MT6765 driver. Risks include camera bring-up races if this gate or parent 26 MHz clocks are disabled. Test signals include camera sensor streaming and gate enable state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-mipi0a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-mm.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-mm.c

### Purpose
This driver registers MT6765 multimedia/display subsystem gates.

### Important APIs, Types, And Functions
It defines `mm_cg_regs`, `GATE_MM`, `mm_clks[]`, `mm_desc`, and a simple platform driver for `mediatek,mt6765-mmsys`.

### Control Flow, State, And Persistence
Simple probe registers MMSYS gates. Gate state persists in the multimedia set/clear/status registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on display/MDP consumers, `mm_ck`, and common gate code. Risks include disabling display pipeline clocks and wrong parent propagation. Test signals include display probe, frame updates, MDP workloads, and clock summary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-vcodec.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-vcodec.c

### Purpose
This file registers MT6765 video codec subsystem gates.

### Important APIs, Types, And Functions
It defines `venc_cg_regs`, `GATE_VENC`, `venc_clks[]`, `venc_desc`, and a simple driver for `mediatek,mt6765-vcodecsys`.

### Control Flow, State, And Persistence
Simple probe publishes the video codec clock provider. Gate state persists in VCODECSYS registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on video codec consumers and top-level multimedia/video parents. Risks include bit-shift mismatches and codec DMA failures from disabled clocks. Test signals include encoder/decoder probe and media workload clock activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-vcodec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765.c

### Purpose
`clk-mt6765.c` is the main MT6765 clock driver. It provides APMIXED PLLs and 26 MHz gates, topckgen fixed/factor/mux/gate clocks, and infracfg gates.

### Important APIs, Types, And Functions
Important state includes global `cksys_base` and `apmixed_base`, register macros derived from them, `fixed_clks[]`, `top_divs[]`, parent arrays, `top_muxes[]`, `top_clks[]`, `ifr_clks[]`, `apmixed_clks[]`, `plls[]`, and probe functions `clk_mt6765_apmixed_probe()`, `clk_mt6765_top_probe()`, `clk_mt6765_ifr_probe()`, and dispatcher `clk_mt6765_probe()`.

### Control Flow, State, And Persistence
The driver registers at `arch_initcall()`. Match data dispatches by compatible: APMIXED maps PLL registers, registers PLLs and extra 26 MHz gates, stores `apmixed_base`, and programs AP_PLL/PLLON hardware mode bits; TOP registers fixed/factor/mux/gate clocks, stores `cksys_base`, and sets SCP configuration bits; IFR registers infra gates. Clock state persists in top mux/gate registers, infra gate banks, APMIXED PLL/gate registers, and two global base pointers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `clk-mux`, `clk-gate`, `clk-pll`, DT bindings, and consumers across display, camera, audio, storage, USB, modem, and infra peripherals. Risks include global base pointer ordering, raw register writes with magic masks, no reset descriptors, parent name drift, and source typos/extra braces visible in table regions. Test signals include full MT6765 boot, clock provider registration for all three compatibles, storage/audio/display/camera probe, PLL rate checks, and `clk_summary` verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-aud.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-aud.c

### Purpose
This driver registers MT6779 audio subsystem gates across two audio gate banks.

### Important APIs, Types, And Functions
It defines `audio0_cg_regs`, `audio1_cg_regs`, `GATE_AUDIO0/1`, `audio_clks[]`, `audio_desc`, and a simple platform driver matching `mediatek,mt6779-audio`.

### Control Flow, State, And Persistence
Simple probe registers the audio gate provider. Gate state persists in audio subsystem registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on audio CCF consumers and MT6779 clock bindings. Risks include parent mismatch with the main MT6779 top driver and disabling always-needed audio interface clocks. Test signals include ALSA probe/playback/capture and `clk_summary` enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-aud.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-cam.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-cam.c

### Purpose
This file registers MT6779 camera subsystem gates.

### Important APIs, Types, And Functions
It defines `cam_cg_regs`, `GATE_CAM`, `cam_clks[]`, `cam_desc`, and a simple platform driver for `mediatek,mt6779-camsys`.

### Control Flow, State, And Persistence
Simple probe registers the CAMSYS gate table and publishes the provider. Gate bits persist in camera clock-gate registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on camera/IP blocks and top camera mux parents. Risks include bit-shift mistakes and missing LARB/sensor-interface clocks. Test signals include camera probe/streaming and gate state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-cam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-img.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-img.c

### Purpose
This driver registers MT6779 image subsystem gates.

### Important APIs, Types, And Functions
It defines `img_cg_regs`, `GATE_IMG`, `img_clks[]`, `img_desc`, and a simple OF platform driver for `mediatek,mt6779-imgsys`.

### Control Flow, State, And Persistence
Probe registers IMGSYS gates via `mtk_clk_simple_probe()`. Gate state persists in the IMGSYS register block.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on image processing consumers and common MediaTek gate code. Risks are wrong parent names and gate shift errors. Test signals include image pipeline probe and debugfs clock activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-img.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-ipe.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-ipe.c

### Purpose
This file registers MT6779 Image Processing Engine subsystem gates.

### Important APIs, Types, And Functions
It defines `ipe_cg_regs`, `GATE_IPE`, `ipe_clks[]`, `ipe_desc`, and a simple driver for `mediatek,mt6779-ipesys`.

### Control Flow, State, And Persistence
Simple probe registers IPE gates and the onecell provider. Gate state persists in IPESYS registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on image/camera processing consumers and top-level image parents. Risks include disabled IPE/LARB clocks during camera processing. Test signals include camera/IPE workloads and CCF gate state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-ipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-mfg.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-mfg.c

### Purpose
This driver registers the MT6779 MFG/GPU gate.

### Important APIs, Types, And Functions
It defines `mfg_cg_regs`, `GATE_MFG`, `mfg_clks[]`, `mfg_desc`, and a simple platform driver for `mediatek,mt6779-mfgcfg`.

### Control Flow, State, And Persistence
Simple probe publishes the GPU clock provider. Gate state persists in MFGCFG registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on GPU consumers and top-level MFG parent clocks. Risks are a wrong gate bit or parent name preventing GPU probe. Test signals include GPU initialization and runtime clock activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-mfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-mm.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-mm.c

### Purpose
This file registers MT6779 multimedia MDP/DDP gate clocks.

### Important APIs, Types, And Functions
It defines `mm0_cg_regs`, `mm1_cg_regs`, `GATE_MM0/1`, `mm_clks[]`, `mm_desc`, a platform ID table, and a platform driver using `mtk_clk_pdev_probe()`.

### Control Flow, State, And Persistence
The pdev probe registers the multimedia gate provider from platform ID data. Gate state persists in two MM register banks.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on MMSYS/display platform device creation and display/MDP consumers. Risks include ID-table mismatch, missing pdev instantiation, and wrong bank shifts. Test signals include display/MDP probe, frame update workloads, and clock summary gate states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-vdec.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-vdec.c

### Purpose
This driver registers MT6779 video decoder gates across two decoder gate banks.

### Important APIs, Types, And Functions
It defines `vdec0_cg_regs`, `vdec1_cg_regs`, `GATE_VDEC0_I`, `GATE_VDEC1_I`, `vdec_clks[]`, `vdec_desc`, and a simple driver for `mediatek,mt6779-vdecsys`.

### Control Flow, State, And Persistence
Simple probe registers VDECSYS gates. Gate state persists in VDEC register banks.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on MT6779 video decoder consumers and top-level video parents. Risks include missing decoder/LARB gates and wrong inverted polarity assumptions. Test signals include decoder probe, decode workloads, and CCF gate activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-vdec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-venc.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-venc.c

### Purpose
This file registers MT6779 video encoder gates.

### Important APIs, Types, And Functions
It defines `venc_cg_regs`, `GATE_VENC_I`, `venc_clks[]`, `venc_desc`, and a simple OF platform driver for `mediatek,mt6779-vencsys`.

### Control Flow, State, And Persistence
Probe registers VENC gates through the common simple probe. Gate state persists in VENC register bits.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on video encoder consumers and the top-level video clock tree. Risks include gate shift mistakes and disabled clocks during encode sessions. Test signals include encoder probe/workload and `clk_summary` transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-venc.c -->
