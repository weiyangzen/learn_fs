# subset-b-005368 Research

Grouped research for MediaTek SoC support files under `sources/distributed-fs/ceph-client/drivers/soc/mediatek`. Each section preserves its source path and is delimited for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/mediatek/Kconfig

## Purpose
This Kconfig menu exposes build-time selections for MediaTek SoC support drivers. It gates the helper, bus, multimedia, power-management, PMIC wrapper, regulator coupling, smart-voltage-scaling, and SoC identification modules under `ARCH_MEDIATEK` or `COMPILE_TEST` where appropriate.

## Important APIs, Types, and Functions
The file defines configuration symbols rather than C APIs. Important symbols are `MTK_CMDQ`, `MTK_DEVAPC`, `MTK_DVFSRC`, `MTK_INFRACFG`, `MTK_PMIC_WRAP`, `MTK_REGULATOR_COUPLER`, `MTK_MMSYS`, `MTK_SVS`, and `MTK_SOCINFO`. The dependency graph is meaningful: `MTK_CMDQ` selects mailbox and infracfg support, `MTK_PMIC_WRAP` depends on reset controller and OF, `MTK_MMSYS` tolerates `MTK_CMDQ=n` but depends on `HAS_IOMEM`, and `MTK_SOCINFO` selects `SOC_BUS`.

## Control Flow and State
There is no runtime control flow. Its persistent effect is the kernel build configuration that determines which objects in the sibling Makefile are compiled and whether code paths using mailbox, regmap, reset, nvmem, regulator, or SoC bus APIs are reachable.

## Dependencies and Integration Points
The menu integrates with the Linux Kconfig system and downstream Makefile object selection. Several options are tristate modules, while `MTK_INFRACFG` and `MTK_REGULATOR_COUPLER` are bools because they provide low-level helper behavior used by other drivers.

## Risks and Test Signals
Risk is mostly dependency drift: missing `select` or `depends on` clauses can allow compile failures in non-MediaTek builds. Test signals are `allyesconfig`, `allmodconfig`, `COMPILE_TEST`, and targeted builds with each symbol enabled as module or built-in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/mediatek/Makefile

## Purpose
This Makefile maps the Kconfig symbols in the same directory to concrete driver objects. It is the build bridge between configuration selections and the MediaTek SoC support code.

## Important APIs, Types, and Functions
There are no runtime APIs. The important entries are one-object mappings such as `obj-$(CONFIG_MTK_CMDQ) += mtk-cmdq-helper.o`, plus two objects under `CONFIG_MTK_MMSYS`: `mtk-mmsys.o` and `mtk-mutex.o`.

## Control Flow and State
The only control flow is kbuild object inclusion. It creates no persistent state, but determines whether exported symbols from drivers such as CMDQ, MMSYS, infracfg, and DVFSRC are present for other kernel subsystems.

## Dependencies and Integration Points
The file relies on Kconfig to enforce prerequisites. It integrates with the kernel module build and may produce separate modules for tristate selections or built-in objects for bool selections.

## Risks and Test Signals
The main risk is Kconfig/Makefile skew, such as a new Kconfig symbol lacking an object or an object compiled without its dependencies. Test signals are successful kernel builds across `m`, `y`, and disabled symbol combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8167-mmsys.h -->
# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8167-mmsys.h

## Purpose
This header supplies MT8167-specific MMSYS display routing register offsets and route table entries. It is consumed by `mtk-mmsys.c` to program display data paths between DDP components.

## Important APIs, Types, and Functions
It defines register offsets for OVL, DITHER, COLOR, DSI, and RDMA selection registers, plus route values such as `MT8167_DITHER_MOUT_EN_RDMA0`. The exported data is `mt8167_mmsys_routing_table[]`, an array of `struct mtk_mmsys_routes` generated with `MMSYS_ROUTE`.

## Control Flow and State
There is no executable control flow. At runtime, `mtk_mmsys_ddp_connect()` and `mtk_mmsys_ddp_disconnect()` iterate this table and write matching register masks/values. The header therefore describes transient hardware mux state, not software-persistent state.

## Dependencies and Integration Points
The table depends on `struct mtk_mmsys_routes`, `MMSYS_ROUTE`, and DDP component identifiers from shared MMSYS/display headers. `mtk-mmsys.c` binds it to the `mediatek,mt8167-mmsys` compatible.

## Risks and Test Signals
Bad route masks or values would silently wire the display pipeline incorrectly. Strong test signals are panel bring-up, DSI output validation, display pipeline mode changes, and register tracing during DDP connect/disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8167-mmsys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8173-mmsys.h -->
# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8173-mmsys.h

## Purpose
This header describes MT8173 MMSYS routing for two display paths, including OVL, OD, UFOE, COLOR, AAL, GAMMA, RDMA, DSI, and DPI connections.

## Important APIs, Types, and Functions
The key artifact is `mt8173_mmsys_routing_table[]`. It uses `MMSYS_ROUTE` entries to describe both MOUT/SOUT and SEL_IN registers. Several entries intentionally use a zero selection value for routes where selecting a path means clearing a field.

## Control Flow and State
Runtime control is table-driven in `mtk-mmsys.c`. When a display driver connects a component pair, matching entries cause masked register updates. Disconnecting clears matching masks.

## Dependencies and Integration Points
The table is bound to MT8173 and reused by MT6795 in `mtk-mmsys.c`. It integrates with DRM DDP topology setup and with shared bit helpers such as `BIT()` and `GENMASK()`.

## Risks and Test Signals
The main risk is that shared reuse with MT6795 may hide SoC differences. Test signals include dual pipeline display output, DPI/DSI routing, UFOE path selection, and checking that zero-valued selections are not mistaken for missing data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8173-mmsys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8183-mmsys.h -->
# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8183-mmsys.h

## Purpose
This header provides MT8183 display routing constants and reset offset data for MMSYS.

## Important APIs, Types, and Functions
It defines `mmsys_mt8183_routing_table[]`, route constants for OVL to 2L overlays, RDMA, DITHER, DPI, DSI, and `MT8183_MMSYS_SW0_RST_B` for reset control. Routes cover the primary path and some secondary output selections.

## Control Flow and State
There is no local control flow. Runtime state is hardware register state set by `mtk_mmsys_ddp_connect()` and reset controller callbacks in `mtk-mmsys.c` using the reset offset.

## Dependencies and Integration Points
This header integrates with the MT8183 driver-data entry in `mtk-mmsys.c`, which sets `num_resets = 32`. It depends on the shared MMSYS route machinery and DDP component IDs.

## Risks and Test Signals
Route omissions are visible as broken display pipelines, especially OVL_2L and RDMA path failures. Reset offset mistakes can affect display block recovery. Test signals are DSI/DPI display bring-up, display reset testing, and DDP topology validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8183-mmsys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8186-mmsys.h -->
# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8186-mmsys.h

## Purpose
This header provides MT8186 MMSYS route definitions, OVL blend/background control bits, DPI output format constants, and software reset offset.

## Important APIs, Types, and Functions
The central artifact is `mmsys_mt8186_routing_table[]`. It maps OVL0 and OVL_2L0 to RDMA0/RDMA1, RDMA0 to COLOR0, DITHER0 to DSI0, and RDMA1 to DPI0. It also defines `MT8186_MMSYS_DPI_OUTPUT_FORMAT`, used by `mtk_mmsys_ddp_dpi_fmt_config()`.

## Control Flow and State
The header has no local execution. Its values drive masked register writes in MMSYS connect/disconnect and DPI format configuration. Hardware state includes output muxes, overlay blend path selections, and `SW0_RST_B` reset bits.

## Dependencies and Integration Points
`mtk-mmsys.c` binds this table to `mediatek,mt8186-mmsys` and exposes DPI format configuration to display drivers. The reset controller uses `MT8186_MMSYS_SW0_RST_B` with 32 resets.

## Risks and Test Signals
The overlap between MOUT, SEL_IN, and OVL_CON fields makes mask accuracy important. Test signals include RDMA0 DSI/COLOR output, RDMA1 DPI output, DPI RGB format changes, and reset controller exercise.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8186-mmsys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8188-mmsys.h -->
# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8188-mmsys.h

## Purpose
This header supplies MT8188 VDOSYS0 and VDOSYS1 MMSYS route tables, reset tables, and video pipeline register constants. It covers complex display/video routing through OVL, RDMA, DITHER, DSC, VPP MERGE, DSI, DP, DPI, MDP RDMA, and ETHDR mixer components.

## Important APIs, Types, and Functions
Important exported data includes `mmsys_mt8188_vdo0_rst_tb[]`, `mmsys_mt8188_vdo1_rst_tb[]`, `mmsys_mt8188_routing_table[]`, and `mmsys_mt8188_vdo1_routing_table[]`. Reset tables translate dt-binding reset IDs into MMSYS bank/bit numbers via `MMSYS_RST_NR`. The route tables encode both source-output and destination-input register fields.

## Control Flow and State
No code executes in the header. Runtime control is table-driven by the MMSYS driver: matching component pairs cause writes to VDO0/VDO1 selector registers, while reset controller operations translate external reset IDs through the tables.

## Dependencies and Integration Points
The file includes public MMSYS and MT8188 reset binding headers. It is bound in `mtk-mmsys.c` to `mediatek,mt8188-vdosys0` and `mediatek,mt8188-vdosys1`; VPP system compatibles are separate clock-only MMSYS instances.

## Risks and Test Signals
Risks include mismatched reset binding indices, selector-mask mistakes, and cross-subsystem routing errors between VDO0 and VDO1. Test signals are DP/DSI/DPI output, DSC and VPP merge paths, ETHDR mixer composition, reset controller consumers, and command queue register updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8188-mmsys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8192-mmsys.h -->
# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8192-mmsys.h

## Purpose
This header defines MT8192 MMSYS routing registers and table entries for display pipelines involving OVL, OVL_2L, RDMA, COLOR, CCORR, AAL, DITHER, DSI, and RDMA4.

## Important APIs, Types, and Functions
The exported data is `mmsys_mt8192_routing_table[]`. It includes OVL_2L0 to RDMA0, OVL_2L2 to RDMA4, DITHER0 to DSI0, CCORR to AAL0, RDMA0 to COLOR0, and OVL/OVL_2L blend selection entries.

## Control Flow and State
The file is declarative. The runtime driver applies matching route entries as masked register writes and uses `MT8186_MMSYS_SW0_RST_B` as the reset offset for MT8192 in the C file.

## Dependencies and Integration Points
It depends on shared DDP component IDs and route infrastructure. The MT8192 driver-data entry in `mtk-mmsys.c` uses this table and exposes 32 reset lines.

## Risks and Test Signals
Route correctness is critical for the multi-overlay display path and RDMA4 support. Test signals include main display bring-up, external display paths using RDMA4, DSI output, CCORR/AAL processing, and reset-controller smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8192-mmsys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8195-mmsys.h -->
# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8195-mmsys.h

## Purpose
This header provides MT8195 VDOSYS0, VDOSYS1, and VPPSYS-related routing constants. It represents a complex video/display fabric with OVL, WDMA, DITHER, DSC, MERGE, DSI, DPI, DP, MDP RDMA, and ETHDR mixer paths.

## Important APIs, Types, and Functions
The key exported arrays are `mmsys_mt8195_routing_table[]` and `mmsys_mt8195_vdo1_routing_table[]`. The header also defines VPP DCM and resize-merge registers used by exported MMSYS helper functions in `mtk-mmsys.c`, such as `mtk_mmsys_vpp_rsz_merge_config()` and `mtk_mmsys_vpp_rsz_dcm_config()`.

## Control Flow and State
All behavior is declarative here. Runtime state consists of selector fields and MOUT/SOUT bits programmed by `mtk_mmsys_update_bits()` from the C driver. VPP DCM and resize-merge bits are toggled by exported helper functions.

## Dependencies and Integration Points
This header is included by `mtk-mmsys.c` for MT8195 VDO0/VDO1 and VPP systems. It integrates with DRM display topology, MDP/video processing, and optional CMDQ-backed register programming.

## Risks and Test Signals
The route matrix contains many paths sharing the same registers with different masks, so small mask or shift errors can affect unrelated outputs. Comments marked `NEED CONFIRM` are not in this file but adjacent PMIC data shows similar SoC bring-up risk. Test signals include DSI0/DSI1, DP0/DP1, DPI0/DPI1, DSC, VPP merge, WDMA, ETHDR mixer, and MDP pipeline validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8195-mmsys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8365-mmsys.h -->
# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8365-mmsys.h

## Purpose
This header describes MT8365 MMSYS route registers for a display pipeline involving OVL0, RDMA0/RDMA1, COLOR0, CCORR, DITHER0, DSI0, DPI0, and LVDS clock selection.

## Important APIs, Types, and Functions
The important data is `mt8365_mmsys_routing_table[]`. It includes MOUT, SOUT, SEL_IN, RDMA0_RSZ0, and LVDS system configuration routes. `MT8365_DISP_MS_IN_OUT_MASK` is used broadly for four-bit selector fields.

## Control Flow and State
The header has no local execution. The MMSYS driver writes the described route values when display components are connected or disconnected. LVDS/DPI selection is captured as route state as well.

## Dependencies and Integration Points
It depends on the shared MMSYS route type and DDP component constants and is bound to `mediatek,mt8365-mmsys` in `mtk-mmsys.c`.

## Risks and Test Signals
There is a duplicate definition of `MT8365_DPI0_SEL_IN_RDMA1`, which is harmless but a maintenance signal. Test signals include DSI0 and DPI0 output, LVDS pixel clock route, RDMA0 resize path, and display component chain validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8365-mmsys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-cmdq-helper.c -->
# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-cmdq-helper.c

## Purpose
This file implements helper routines for MediaTek Command Queue packets. It creates mailbox clients, allocates DMA-backed command buffers, appends encoded GCE instructions, and exposes register write/read/poll/event/logic/jump helpers used by display and SoC drivers.

## Important APIs, Types, and Functions
Important exported APIs include `cmdq_dev_get_client_reg()`, `cmdq_mbox_create()`, `cmdq_mbox_destroy()`, `cmdq_pkt_create()`, `cmdq_pkt_destroy()`, `cmdq_pkt_write*()`, `cmdq_pkt_read_s()`, `cmdq_pkt_mem_move()`, `cmdq_pkt_wfe()`, `cmdq_pkt_acquire_event()`, `cmdq_pkt_clear_event()`, `cmdq_pkt_set_event()`, `cmdq_pkt_poll*()`, `cmdq_pkt_logic_command()`, `cmdq_pkt_assign()`, `cmdq_pkt_jump_abs()`, `cmdq_pkt_jump_rel()`, and `cmdq_pkt_eoc()`. `struct cmdq_instruction` is the local packed instruction representation.

## Control Flow and State
`cmdq_pkt_create()` allocates and DMA maps a zeroed buffer, stores virtual/physical base and mailbox private data, and callers then append commands through `cmdq_pkt_append_command()`. If the buffer is too small, the helper still advances `cmd_buf_size` to report required size and returns `-ENOMEM`. Packet destruction unmaps DMA and frees memory. Register access helpers encode either subsystem-relative or physical-address-based sequences.

## Dependencies and Integration Points
The code depends on mailbox framework channels, DMA mapping, device tree `mediatek,gce-client-reg`, and public CMDQ types from `linux/soc/mediatek/mtk-cmdq.h`. MMSYS and mutex drivers use these helpers for optional CMDQ-backed register programming.

## Risks and Test Signals
Risks include instruction encoding mistakes, DMA lifetime misuse, invalid event IDs, and buffer-size underestimation by callers. A notable issue is `cmdq_pkt_jump_abs()` ignores its `shift_pa` argument and uses `pkt->priv.shift_pa`, which may be intentional but is easy to misread. Test signals include CMDQ packet submission through mailbox, masked writes, polling physical addresses, event wait/set/clear behavior, buffer-too-small warnings, and DMA debug checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-cmdq-helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-devapc.c -->
# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-devapc.c

## Purpose
This driver handles MediaTek Device APC access violations. It enables violation interrupts, synchronizes hardware violation debug information through the shift mechanism, logs violation metadata, clears status, and masks/unmasks module interrupts.

## Important APIs, Types, and Functions
Key local types are `struct mtk_devapc_vio_dbgs`, `struct mtk_devapc_regs_ofs`, `struct mtk_devapc_data`, and `struct mtk_devapc_context`. Important functions are `clear_vio_status()`, `mask_module_irq()`, `devapc_sync_vio_dbg()`, `devapc_extract_vio_dbg()`, `devapc_violation_irq()`, `start_devapc()`, `stop_devapc()`, `mtk_devapc_probe()`, and `mtk_devapc_remove()`.

## Control Flow and State
Probe maps registers with `of_iomap()`, parses IRQ, enables the infraclock, registers the IRQ handler, stores context, and unmasks violation interrupts. The IRQ handler loops while shift status reports pending groups, extracts debug registers, clears violation status, and returns handled. Remove masks interrupts and unmaps MMIO.

## Dependencies and Integration Points
The driver integrates with device tree compatibles `mediatek,mt6779-devapc` and `mediatek,mt8186-devapc`, the clock framework, IRQ framework, and MMIO polling. Per-SoC data supplies violation count and register offsets.

## Risks and Test Signals
Risks include off-by-one handling in violation register loops, incomplete IRQ masking for the final partial register, and using `IS_ERR()` on an OF node pointer in probe. Test signals are synthetic access violations, IRQ logs showing bus/domain/address, clock enable failures, poll timeout behavior, and remove/reprobe cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-devapc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-dvfsrc.c -->
# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-dvfsrc.c

## Purpose
This file implements the MediaTek Dynamic Voltage and Frequency Scaling Resource Collector driver. It converts bandwidth and OPP requests into SoC-specific DVFSRC register writes, initializes firmware through SMC calls, discovers or selects OPP tables, and populates child devices.

## Important APIs, Types, and Functions
Important exported APIs are `mtk_dvfsrc_send_request()` and `mtk_dvfsrc_query_info()`. Core data types include `struct dvfsrc_opp`, `struct dvfsrc_opp_desc`, `struct mtk_dvfsrc`, and `struct dvfsrc_soc_data`. Function pointers in `dvfsrc_soc_data` abstract register layout, bandwidth conversion, level getters/setters, wait behavior, and OPP discovery.

## Control Flow and State
Probe maps registers, enables the clock, calls secure monitor init, records DRAM type, selects static OPP tables or reads hardware gear tables, stores drvdata, populates children, and starts DVFSRC via SMC. Requests either write bandwidth registers and return immediately or set OPP/vcore/vscp levels, delay briefly, poll for idle, then poll for requested level. Persistent driver state is the selected SoC data, current OPP descriptor, mapped registers, clock, and DRAM type.

## Dependencies and Integration Points
The driver depends on ARM SMCCC, MediaTek SIP service IDs, clocks, OF platform population, `linux/soc/mediatek/dvfsrc.h`, bitfield helpers, and MMIO polling. It supports MT6893, MT8183, MT8195, and MT8196-compatible data.

## Risks and Test Signals
Risks include table index bounds for DRAM type, timeout sensitivity, incorrect OPP ordering, and v4 hardware gear parsing. Some request paths assume function pointers exist for supported commands. Test signals include interconnect and regulator child drivers issuing bandwidth/OPP requests, timeout logs, firmware init/start return codes, and observed vcore/DRAM gear transitions under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-dvfsrc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-infracfg.c -->
# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-infracfg.c

## Purpose
This file provides exported helpers to set and clear MediaTek infrastructure bus protection bits, plus an early MT8192 workaround disabling an unsupported GPU-to-ACP path.

## Important APIs, Types, and Functions
Exported functions are `mtk_infracfg_set_bus_protection()` and `mtk_infracfg_clear_bus_protection()`. `mtk_infracfg_init()` is a `postcore_initcall` that finds the MT8192 infracfg syscon and sets `MT8192_INFRA_CTRL_DISABLE_MFG2ACP`.

## Control Flow and State
The set/clear helpers write either update-style or set/clear-style protection registers, then poll `INFRA_TOPAXI_PROTECTSTA1` until bits are reflected. The initcall writes persistent hardware register state early in boot for MT8192 if the syscon exists.

## Dependencies and Integration Points
The code depends on regmap, syscon lookup, MediaTek infracfg public register definitions, and jiffies-derived timeout constants. Power domain and SoC drivers call the exported protection helpers when gating domains or buses.

## Risks and Test Signals
Risks include polling the wrong status register for SoCs with different ack locations and timeout behavior when a bus client is active. Test signals include power-domain on/off cycles, regmap poll timeouts, and MT8192 GPU stability without spurious ACP faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-infracfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-mmsys.c -->
# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-mmsys.c

## Purpose
This is the core MediaTek MMSYS platform driver. It binds SoC-specific route tables and reset data, exports helpers for display/video path configuration, registers an optional reset controller, creates child clock and DRM platform devices, and supports optional CMDQ register writes.

## Important APIs, Types, and Functions
Exported APIs include `mtk_mmsys_ddp_connect()`, `mtk_mmsys_ddp_disconnect()`, `mtk_mmsys_merge_async_config()`, `mtk_mmsys_hdr_config()`, `mtk_mmsys_mixer_in_config()`, `mtk_mmsys_mixer_in_channel_swap()`, `mtk_mmsys_ddp_dpi_fmt_config()`, `mtk_mmsys_vpp_rsz_merge_config()`, and `mtk_mmsys_vpp_rsz_dcm_config()`. Local core data is `struct mtk_mmsys`, containing register base, driver data, child platform devices, reset controller, spinlock, and CMDQ base.

## Control Flow and State
Probe allocates state, maps MMIO, picks match data, registers resets when available, reads optional GCE client register metadata, registers a clock platform device, and registers `mediatek-drm` unless the instance is VPPSYS. Route connect/disconnect iterates SoC route arrays and writes matching masks. Reset operations assert by clearing bits and deassert by setting bits under a spinlock; reset pulses sleep for about 1 ms. Remove unregisters child devices.

## Dependencies and Integration Points
The driver integrates with device tree compatibles for many MediaTek MMSYS/VDOSYS/VPPSYS instances, reset framework, platform device model, DRM display drivers, MediaTek clock drivers, and CMDQ helpers. SoC-specific headers provide route/reset constants.

## Risks and Test Signals
Risks include child device lifetime ordering, optional CMDQ fallback behavior, reset table translation errors, route table omissions, and `platform_device_unregister(NULL)` assumptions for VPPSYS instances. Test signals include DRM probe, clock child probe, display route switching, reset controller consumers, CMDQ and CPU write paths, and suspend/resume display recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-mmsys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-mmsys.h -->
# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-mmsys.h

## Purpose
This shared private header defines common MMSYS route constants, the `MMSYS_ROUTE` helper, `struct mtk_mmsys_routes`, `struct mtk_mmsys_driver_data`, and the default routing table used by older SoCs.

## Important APIs, Types, and Functions
`MMSYS_ROUTE()` is the most important macro: it fills route records while compile-time checking that masks are nonzero and selection values fit masks. `struct mtk_mmsys_driver_data` carries clock driver names, route arrays, reset offsets/tables, VPPSYS marker, and mixer vsync length. `mmsys_default_routing_table[]` describes legacy BLS/OVL/COLOR/RDMA/GAMMA/OD/UFOE routes.

## Control Flow and State
There is no executable control flow. The data here drives runtime route iteration, reset registration, and clock/DRM child device creation in `mtk-mmsys.c`.

## Dependencies and Integration Points
The header depends on DDP component IDs and bit macros. It is included by all per-SoC MMSYS route headers and the core driver, making it the local contract for route data shape.

## Risks and Test Signals
The compile-time route checks reduce mask/value mistakes, but default route reuse for incomplete SoC route information is explicitly provisional. Test signals include build-time validation failures, legacy display path tests on MT2701/MT2712-like SoCs, and route-specific register traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-mmsys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-mutex.c -->
# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-mutex.c

## Purpose
This driver provides MediaTek display and MDP hardware mutex support. It allocates mutex handles, maps display components to mutex module bits, configures SOF/EOF timing sources, enables/disables/acquires/releases hardware mutexes, and exposes command-queue enable support.

## Important APIs, Types, and Functions
Exported APIs include `mtk_mutex_get()`, `mtk_mutex_put()`, `mtk_mutex_prepare()`, `mtk_mutex_unprepare()`, `mtk_mutex_add_comp()`, `mtk_mutex_remove_comp()`, `mtk_mutex_enable()`, `mtk_mutex_enable_by_cmdq()`, `mtk_mutex_disable()`, `mtk_mutex_acquire()`, `mtk_mutex_release()`, `mtk_mutex_write_mod()`, and `mtk_mutex_write_sof()`. Key types are `struct mtk_mutex`, `struct mtk_mutex_data`, and `struct mtk_mutex_ctx`.

## Control Flow and State
Probe initializes ten mutex handles, obtains match data, optionally gets a clock, maps registers, stores the physical register base, reads optional CMDQ register metadata, and stores drvdata. `mtk_mutex_get()` marks an in-memory handle claimed; `put()` clears it. Component add/remove either sets module bits in one of two MOD registers or writes SOF selection for output components. Acquire writes enable and request bits, then polls `INT_MUTEX`; release clears the request bit.

## Dependencies and Integration Points
The driver integrates with DRM/DDP and MDP components through public MediaTek mutex APIs, with CMDQ through `cmdq_dev_get_client_reg()` and `cmdq_pkt_write()`, with clocks, and with OF compatibles for many SoCs and VPP/MDP variants.

## Risks and Test Signals
Risks include lack of locking around the `claimed` array, unchecked component IDs indexing SoC tables, SoC-specific module bit drift, and CMDQ address/subsys mismatch in `mtk_mutex_enable_by_cmdq()`. Test signals include concurrent display pipeline allocation, command queue enable, video mode EOF timing, MDP table-based module writes, clock enable/disable cycles, and acquisition timeout logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-mutex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-pmic-wrap.c -->
# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-pmic-wrap.c

## Purpose
This driver implements the MediaTek PMIC wrapper bus controller. It initializes AP-side wrapper hardware and PMIC-side device-wrapper settings, exposes PMIC access through regmap, handles wrapper interrupts, supports multiple SoC/PMIC register layouts, and populates child devices under the PMIC node.

## Important APIs, Types, and Functions
Key types include `struct pmic_wrapper`, `struct pmic_wrapper_type`, `struct pwrap_slv_type`, and `struct pwrap_slv_regops`. Important functions include `pwrap_read16()`, `pwrap_read32()`, `pwrap_write16()`, `pwrap_write32()`, regmap callbacks, `pwrap_reset_spislave()`, `pwrap_init_sidly()`, `pwrap_init_dual_io()`, `pwrap_init_cipher()`, `pwrap_init_security()`, SoC-specific init helpers, `pwrap_init()`, `pwrap_interrupt()`, and `pwrap_probe()`.

## Control Flow and State
Probe matches the child PMIC node, allocates wrapper state, maps `pwrap` and optional bridge MMIO, obtains resets and clocks, enables DCM where supported, runs `pwrap_init()` unless `INIT_DONE2` indicates bootloader initialization, validates init-done status, configures watchdog/timer/interrupt masks, requests IRQ, registers regmap, and populates child devices. WACS read/write helpers poll FSM state, issue commands, wait for valid data, clear valid state, and recover stale `WFVLDCLR` state on timeout.

## Dependencies and Integration Points
The driver integrates with device tree master and slave compatibles, reset framework, clock framework, MMIO, IRQs, regmap, and OF platform population. PMIC child drivers access registers through the regmap backed by PMIC wrapper transactions. SoC descriptors define register offsets, arbiter masks, interrupt masks, SPI command format, watchdog masks, capabilities, and init callbacks.

## Risks and Test Signals
Risks are high because initialization ordering touches reset, SPI slave mode, SIDLY tuning, dual I/O, cipher/CRC security, arbiter enablement, watchdogs, and interrupts. Descriptor mistakes can break all PMIC communication; MT8195 has `NEED CONFIRM` comments for arbiter and interrupt masks. Test signals include PMIC regmap reads/writes, write-test values, SIDLY pass range, dual-IO read tests, cipher readiness, bootloader-initialized skip path, interrupt logs, child regulator/RTC/MFD probes, and suspend/resume PMIC access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-pmic-wrap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-regulator-coupler.c -->
# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-regulator-coupler.c

## Purpose
This file registers a MediaTek-specific regulator coupler for GPU and SRAM voltage relationships on selected SoCs. It ensures the SRAM regulator is moved to a safe voltage window before balancing the target GPU regulator voltage.

## Important APIs, Types, and Functions
The central type is `struct mediatek_regulator_coupler`, embedding `struct regulator_coupler` and tracking `vsram_rdev`. Important callbacks are `mediatek_regulator_attach()`, `mediatek_regulator_detach()`, and `mediatek_regulator_balance_voltage()`. Initialization is `mediatek_regulator_coupler_init()` via `arch_initcall`.

## Control Flow and State
Attach accepts only two-regulator GPU/SRAM-style couples and remembers the SRAM regulator. Balance rejects direct SRAM voltage changes after SRAM is already in use, computes a target SRAM min/max window from GPU voltage and `max_spread`, sets SRAM voltage, then delegates to regulator core balancing for the target regulator. Detach clears the SRAM pointer when removed.

## Dependencies and Integration Points
The code integrates with regulator core coupling APIs, regulator constraints, suspend state handling, and OF machine compatibility checks for MT8183, MT8186, MT8188, and MT8192.

## Risks and Test Signals
Risks include name-based matching (`sram`, `vgpu`, `Vgpu`), assumptions about exactly two coupled regulators, and constraint misconfiguration producing unsafe voltage windows. Test signals include GPU DVFS transitions, regulator core coupling traces, failed direct SRAM set attempts returning `-EPERM`, suspend/resume voltage balancing, and constraint boundary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-regulator-coupler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-socinfo.c -->
# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-socinfo.c

## Purpose
This driver reads MediaTek efuse/nvmem cells to identify SoC variant and marketing name, then registers a Linux `soc_device` for userspace-visible SoC metadata.

## Important APIs, Types, and Functions
Key types are `struct mtk_socinfo` and `struct socinfo_data`. The lookup table `socinfo_data_table[]` maps up to two cell values to SoC name, segment name, and marketing name. Important functions are `mtk_socinfo_read_cell()`, `mtk_socinfo_get_socinfo_data()`, `mtk_socinfo_create_socinfo_node()`, `mtk_socinfo_probe()`, and `mtk_socinfo_remove()`.

## Control Flow and State
Probe allocates state, reads `socinfo-data1` and optional `socinfo-data2` from the parent nvmem device, matches the values against the static table, registers a `soc_device_attribute`, stores drvdata, and unregisters the soc device on remove. Persistent state is the registered soc device and pointer to static table data.

## Dependencies and Integration Points
The driver depends on being created as an nvmem child device, `nvmem_device_find()`, OF child cell nodes with `reg` offsets, the SoC bus API, and platform driver registration. Userspace consumes the result through the standard SoC device sysfs hierarchy.

## Risks and Test Signals
Risks include incomplete table coverage, partial-cell matching when fewer cells are present, ignoring `nvmem_device_read()` return status, and unused `segment_name` in registered attributes. Test signals include known efuse values on supported chips, unknown-ID warnings, soc bus sysfs content, nvmem read failure injection, and remove/reprobe cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-socinfo.c -->
