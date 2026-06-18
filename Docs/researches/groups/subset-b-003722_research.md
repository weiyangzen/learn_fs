# subset-b-003722 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/nid.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/nid.h

### Purpose
`nid.h` is the Northern Islands/Cayman-era register and packet-definition header for the Radeon DRM driver. It does not implement behavior directly; it names memory-mapped register offsets, bit fields, packet builders, command opcodes, async-DMA packet formats, and ASIC limits used by the NI, Cayman, Trinity/Aruba, UVD, display AUX, VM, memory-controller, power-management, and command-processor code.

### Important APIs, Types, And Functions
The file exports preprocessor constants rather than C functions or structs. Important groups are Cayman resource caps (`CAYMAN_MAX_*`), golden address configurations, SRBM/GRBM status and soft-reset bits, VM L1/L2/context/protection-fault registers, MC aperture and DRAM timing registers, HDP flush/coherency registers, shader/texture/color/depth backend disable masks, SCLK/MCLK/SMC power-management registers, CAC weight and throttle fields, PCIe link fields, UVD ring/status registers, PM4 `PACKET0`, `PACKET2`, `PACKET3` helpers and PACKET3 opcodes, and async DMA ring/IB/fence/trap/copy/write packet helpers.

### Control Flow
There is no runtime control flow in the header. Its macros encode control flow for other modules by making hardware state machines addressable: reset code polls `SRBM_STATUS`/`GRBM_STATUS` bits, VM code invalidates TLB/L2 through `VM_L2_CNTL2`, ring emitters build PM4 packets with `PACKET*`, DMA emitters build DMA words with `DMA_PACKET`/`DMA_IB_PACKET`, and DPM code programs PLL, voltage, CAC, and memory-timing fields.

### State, Persistence, And Dependencies
The persistent state controlled through this header lives in GPU registers and command streams, not in the header itself. Register writes alter hardware-visible state such as VM contexts, ring pointers, memory timing, clocks, PCIe link configuration, UVD state, and reset bits. The header depends on shared Radeon packet constants such as `RADEON_PACKET_TYPE0`, `RADEON_PACKET_TYPE3`, and `REG_SET`, plus the driver convention that register offsets are byte offsets.

### Integration Points
The definitions are consumed throughout the Radeon ASIC files for Northern Islands and related hardware, including interrupt/reset paths, ring setup, VM fault handling, power management, UVD setup, DisplayPort AUX transactions, and DMA command emission. The PM4/DMA packet helpers are an ABI boundary with GPU firmware and hardware parsers: callers must pass exactly the field widths expected by the command processor.

### Risks
Because this is a raw hardware contract, wrong masks, shifts, or offsets can cause hangs, memory corruption, failed reset, incorrect VM fault handling, or broken power management. Several macro names are generic (`ENABLE`, `RESET`, `BYPASS`, `INDEX`) and depend on include ordering and local context. Field builders generally do not mask every input, so callers must range-check values. Duplicate concepts such as soft reset bits in SRBM and GRBM need careful selection for the target block. The header is also architecture-sensitive because packet words and register offsets must match the hardware documentation exactly.

### Test Signals
Useful signals are successful NI/Cayman bring-up, ring tests, IB tests, DMA copy/fill tests, VM fault decode and TLB invalidate tests, UVD ring tests, DisplayPort AUX reads/writes, suspend/resume reset tests, and DPM clock/voltage transitions. Static checks should watch for macro redefinition warnings and ensure packet-builder users mask or bound user-derived fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/nid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/nislands_smc.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/nislands_smc.h

### Purpose
`nislands_smc.h` defines the packed host-side data layout used to communicate Northern Islands dynamic power-management state to the SMC firmware. It describes performance levels, software states, voltage masks, CAC tables, memory-controller register tables, DRAM timing tables, SPLL divider tables, and SMC firmware-header offsets.

### Important APIs, Types, And Functions
The header exports packed structs, not functions. Key types are `PP_NIslands_Dpm2PerfLevel` and `PP_NIslands_DPM2Parameters` for DPM2/TDP tuning; `NISLANDS_SMC_SCLK_VALUE`, `NISLANDS_SMC_MCLK_VALUE`, and `NISLANDS_SMC_VOLTAGE_VALUE` for PLL and voltage programming; `NISLANDS_SMC_HW_PERFORMANCE_LEVEL` for one hardware level; `NISLANDS_SMC_SWSTATE`, `NISLANDS_SMC_SWSTATE_SINGLE`, and `NISLANDS_SMC_STATETABLE` for firmware state tables; `PP_NIslands_CACTABLES` and `SMC_NISLANDS_MC_TPP_CAC_TABLE` for power estimation; `SMC_NIslands_MCRegisters` and `SMC_NIslands_MCArbDramTimingRegisters` for memory-controller programming; and `SMC_NISLANDS_SPLL_DIV_TABLE` for firmware clock lookup.

### Control Flow
There is no executable control flow. Runtime DPM code fills these structures from BIOS PowerPlay tables, calculated PLL values, voltage dependencies, and memory timing, writes them to SMC SRAM at offsets advertised by the firmware header, and then sends SMC messages to switch or enable states. The flexible `NISLANDS_SMC_SWSTATE.levels[]` and the fixed `driverState` plus `dpmLevels[]` arrangement allow the host to present a driver-selected sequence of levels to firmware.

### State, Persistence, And Dependencies
The file uses `#pragma pack(push, 1)` because the structures are firmware ABI, not normal kernel-only data. State persists in SMC SRAM and is interpreted by microcode after host upload. It depends on fixed-width integer types and on common SMC/PowerPlay flags from `ppsmc.h` and BIOS parsing code. The firmware-header offset constants such as `NISLANDS_SMC_FIRMWARE_HEADER_stateTable`, `cacTable`, `mcRegisterTable`, and `spllTable` define where the driver discovers SMC SRAM destinations.

### Integration Points
Northern Islands DPM code uses these layouts when constructing SCLK/MCLK, voltage, CAC, memory timing, and state tables. The register field names mirror hardware registers from `nid.h`, letting code copy calculated register values directly into firmware-facing tables. The structures are also tied to AtomBIOS PowerPlay data from `pptable.h`, which supplies clock, voltage, platform, and classification inputs.

### Risks
The dominant risk is ABI drift: padding, type-size, endian, or layout changes would corrupt SMC SRAM interpretation. Flexible arrays and fixed maximums (`NISLANDS_MAX_SMC_PERFORMANCE_LEVELS_PER_SWSTATE`, `SMC_NISLANDS_MC_REGISTER_ARRAY_SIZE`, `SMC_NISLANDS_MC_REGISTER_ARRAY_SET_COUNT`) require strict bounds in producers. Many fields are raw precomputed register values, so validation must happen before upload. CAC and voltage-mask tables can affect thermal and power limits, making unit or scaling mistakes hardware-visible. Because this is shared with firmware, comments and names are not enough; byte offsets must remain stable.

### Test Signals
High-value tests include DPM enable/disable on NI cards, SMC state-table upload verification, SCLK/MCLK switching, voltage-mask transitions, UVD/display watermark changes, memory-clock transition tests using MC register tables, suspend/resume DPM restoration, thermal/CAC throttling behavior, and compile-time or runtime size/offset checks against firmware expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/nislands_smc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ppsmc.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ppsmc.h

### Purpose
`ppsmc.h` is the shared PowerPlay-to-SMC message and flag vocabulary for Radeon DPM code. It defines firmware result codes, state/system/extra flags, fan-control modes, display watermark values, thermal-protection modes, and SMC message IDs used across multiple ASIC families.

### Important APIs, Types, And Functions
The file exports constants and two typedefs: `PPSMC_Result` as an 8-bit firmware response and `PPSMC_Msg` as a 16-bit message type. Important constants include `PPSMC_Result_OK`/`PPSMC_Result_Failed`, state flags such as `PPSMC_SWSTATE_FLAG_DC`, `UVD`, `VCE`, and `PCIE_X1`, system flags such as `GPIO_DC`, `STEPVDDC`, and `GDDR5`, state behavior flags such as `POWERBOOST` and deep-sleep controls, `enum FAN_CONTROL`, legacy 8-bit messages for RV7xx/NI-era firmware, CI/KV/KB 16-bit DPM messages, and TN 32-bit-valued message macros.

### Control Flow
There is no local execution. Runtime control flow occurs in SMC client code that writes one of these message IDs to an SMC mailbox, waits for a response, and branches on `PPSMC_Result_OK`. Common flows include halt/resume, switching to driver or initial states, forcing high/medium/no levels, enabling or disabling CAC/DTE/ULV/Thermal DPM, powering UVD/VCE/SAMU/ACP blocks, setting enabled masks, forcing PCIe or MCLK/SCLK levels, and querying clocks.

### State, Persistence, And Dependencies
The constants represent protocol state in firmware mailboxes and SMC-managed state machines. They do not store kernel state themselves. The header uses packed pragmas for consistency with adjacent firmware ABI headers, although it contains only scalar constants and an enum. It depends on fixed-width integer types and is consumed by ASIC-specific DPM and SMC mailbox implementations.

### Integration Points
`rv770_dpm.c`, NI/SI/CI/KV DPM code, and SMC transport files use these definitions to build state tables and send mailbox commands. `nislands_smc.h` relies on the flag meanings for state-table fields, and `pptable.h` supplies BIOS-derived classifications that are translated into these SMC flags and messages.

### Risks
Message IDs are firmware ABI. Reusing an ID for the wrong ASIC family can cause silent no-ops, failed responses, or incorrect power-state transitions. Some macros intentionally overlap by family and width, and `PPSMC_MSG_PCIeDPM_Disable` is defined twice with the same value, so consumers must not assume a unique list. The typedef `PPSMC_Msg` is 16-bit even though TN macros are declared with 32-bit casts, so code passing TN-only IDs through `PPSMC_Msg` should be checked for truncation assumptions. Feature flags must match the SMC firmware version loaded for the device.

### Test Signals
Test signals include successful SMC halt/resume handshakes, mailbox timeout/error handling, DPM enable/disable, forced-level changes, AC/DC transitions, thermal interrupt enablement, UVD/VCE/SAMU/ACP power toggles, clock query responses, and negative tests that unsupported messages return failure without corrupting state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ppsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/pptable.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/pptable.h

### Purpose
`pptable.h` defines packed AtomBIOS PowerPlay table layouts and constants used by Radeon power-management code. It describes thermal controllers, fan tables, platform capabilities, PowerPlay table revisions, state arrays, non-clock metadata, ASIC-specific clock-info records, clock/voltage dependency tables, leakage and phase-shedding tables, multimedia clock tables, PowerTune tables, and platform power-management data.

### Important APIs, Types, And Functions
The file is a data ABI header. Core types include `ATOM_PPLIB_POWERPLAYTABLE` through `ATOM_PPLIB_POWERPLAYTABLE5`, `ATOM_PPLIB_THERMALCONTROLLER`, `ATOM_PPLIB_FANTABLE*`, `ATOM_PPLIB_EXTENDEDHEADER`, `ATOM_PPLIB_STATE` and `ATOM_PPLIB_STATE_V2`, `StateArray`, `ClockInfoArray`, `NonClockInfoArray`, `ATOM_PPLIB_NONCLOCK_INFO`, clock info records for R600/RS780/Evergreen/SI/CI/Sumo, dependency and limit tables for clock/voltage, `ATOM_PPLIB_CAC_Leakage_Table`, `ATOM_PPLIB_PhaseSheddingLimits_Table`, VCE/UVD/SAMU/ACP tables, `ATOM_PPLIB_POWERTUNE_Table*`, and `ATOM_PPLIB_PPM_Table`.

### Control Flow
There is no direct control flow. Power-management code reads the BIOS PowerPlay table header, follows offsets to variable-length arrays, converts non-clock classifications into driver power-state classes, converts clock-info records into SCLK/MCLK/VDDC/VDDCI/PCIe settings, applies platform capability bits, and uses extended-header offsets to discover optional tables for fan, VCE, UVD, SAMU, ACP, PowerTune, leakage, and dependency data. Later DPM code translates those parsed records into SMC state tables and mailbox commands.

### State, Persistence, And Dependencies
The persistent source of truth is the AtomBIOS image. This header must match that firmware binary layout, so it uses `#pragma pack(1)`, BIOS integer typedefs (`UCHAR`, `USHORT`, `ULONG`), flexible arrays, and one-element trailing-array patterns. It depends on AtomBIOS common table headers and on consumers that validate revision, table size, entry size, offsets, and entry counts before dereferencing.

### Integration Points
`rv770_dpm.c`, `radeon_pm.c`, KV/CI-era DPM files, and other ASIC-specific PowerPlay parsers use these layouts to populate `struct radeon_power_state` and SMC tables. The classification and caps bits drive sysfs/profile selection, display/video state selection, AC/DC restrictions, dynamic refresh, PCIe lane/speed choices, and thermal/fan behavior. Optional multimedia tables integrate with UVD, VCE, SAMU, and ACP power management.

### Risks
This is BIOS ABI parsing, so malformed or unexpected offsets can lead to out-of-bounds reads if callers do not verify size. Many tables are variable-length and represented by flexible arrays or `entries[1]`, requiring careful bounds math. Revisions add fields by embedding previous table versions; code must use the actual table size and revision before reading newer offsets. `ATOM_PPLIB_SWSTATE_MEMORY_DLL_OFF` has an extra hex digit compared with nearby 32-bit flags, so consumers should confirm intended bit position. Packed BIOS structs can produce unaligned accesses if copied or cast carelessly on strict-alignment architectures. Comments show some partially modeled tables, such as VCE/UVD tables where nested arrays are commented out and consumers must manually walk the layout.

### Test Signals
Useful tests include parsing real BIOS PowerPlay tables across R600, RS780, Evergreen, SI, CI, Sumo, KV, and mobile/desktop variants; fuzzing table offsets/counts/revisions; validating derived power states and UI classes; fan table and thermal-controller detection; dependency-table voltage lookup; multimedia clock table lookup; PowerTune limit extraction; and suspend/resume transitions using parsed states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/pptable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r100.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r100.c

### Purpose
`r100.c` implements Radeon DRM support for the R100 through R500-family legacy command processor and memory/display blocks, with special focus on R100/R200/R300-era behavior. It contains display vblank/page-flip helpers, legacy power-management hooks, hotplug handling, PCI GART setup, IRQ handling, fence/ring/IB emission, CP firmware loading and ring initialization, command-stream parsing and validation, render/texture/vertex tracking, reset and idle waits, VRAM and memory-controller setup, PLL/MMIO accessors, debugfs dumps, tiling surface programming, bandwidth calculation, and init/resume/suspend/fini paths.

### Important APIs, Types, And Functions
Display and PM entry points include `r100_wait_for_vblank`, `r100_page_flip`, `r100_page_flip_pending`, `r100_pm_get_dynpm_state`, `r100_pm_init_profile`, `r100_pm_misc`, `r100_pm_prepare`, and `r100_pm_finish`. Hotplug and IRQ code includes `r100_hpd_sense`, `r100_hpd_set_polarity`, `r100_hpd_init`, `r100_hpd_fini`, `r100_irq_set`, `r100_irq_disable`, `r100_irq_process`, and `r100_get_vblank_counter`.

GART/ring/CP helpers include `r100_pci_gart_init`, `r100_pci_gart_enable`, `r100_pci_gart_disable`, `r100_pci_gart_set_page`, `r100_copy_blit`, `r100_fence_ring_emit`, `r100_ring_start`, `r100_cp_init_microcode`, `r100_cp_load_microcode`, `r100_cp_init`, `r100_cp_fini`, `r100_cp_disable`, `r100_gfx_get_rptr`, `r100_gfx_get_wptr`, `r100_gfx_set_wptr`, `r100_ring_test`, `r100_ring_ib_execute`, and `r100_ib_test`.

Command-submission validation is centered on `r100_cs_parse`, `r100_cs_parse_packet0`, `r100_packet0_check`, `r100_packet3_check`, `r100_reloc_pitch_offset`, `r100_packet3_load_vbpntr`, `r100_cs_packet_parse_vline`, `r100_get_vtx_size`, `r100_cs_track_check_pkt3_indx_buffer`, `r100_cs_track_check`, `r100_cs_track_texture_check`, `r100_cs_track_cube`, and `r100_cs_track_clear`.

Lifecycle and hardware support include `r100_errata`, `r100_gui_wait_for_idle`, `r100_mc_wait_for_idle`, `r100_gpu_is_lockup`, `r100_asic_reset`, `r100_set_common_regs`, `r100_vram_init_sizes`, `r100_mc_init`, PLL accessors, `r100_set_safe_registers`, `r100_set_surface_reg`, `r100_clear_surface_reg`, `r100_bandwidth_update`, `r100_mc_stop`, `r100_mc_resume`, `r100_mc_program`, `r100_clock_startup`, `r100_startup`, `r100_resume`, `r100_suspend`, `r100_fini`, `r100_restore_sanity`, `r100_init`, `r100_mm_rreg_slow`, `r100_mm_wreg_slow`, `r100_io_rreg`, and `r100_io_wreg`.

### Control Flow
Initialization through `r100_init` disables VGA rendering, initializes scratch and surface tracking, restores sane CP register state after kexec-like handoff, obtains and initializes COMBIOS, resets and verifies the posted card, records PLL errata, initializes clocks, AGP/VRAM/GART, fence and BO managers, safe-register bitmaps, power management, and then calls `r100_startup`. `r100_startup` programs common registers and MC apertures, starts clocks, enables bus mastering and PCI GART when needed, initializes writeback, fences, IRQs, CP/ring, and the IB pool. Resume disables stale PCI GART, starts clocks, resets/posts the ASIC, reinitializes surfaces, and reruns startup. Suspend and fini unwind CP, writeback, IRQ, GART, AGP, fences, BOs, AtomBIOS/COMBIOS, and BIOS memory.

The CP path loads family-specific firmware (`R100_cp.bin`, `R200_cp.bin`, `R300_cp.bin`, `R420_cp.bin`, `RS690_cp.bin`, `RS600_cp.bin`, or `R520_cp.bin`), writes it into CP ME RAM, sizes and initializes the ring, sets read/write pointers and writeback scratch addresses, starts command processing, enables PCI bus mastering, starts the ring, and validates it with a scratch-register ring test. IB execution writes optional saved-rptr state, then emits `CP_IB_BASE` and length. Fence emission flushes color/depth/HDP caches, waits for idle/clean, writes the fence sequence to a scratch register, and fires a software interrupt.

The CS parser loops over user IB packets. PACKET0 writes are accepted only if they fall in the ASIC safe-register bitmap, then delegated to `r100_packet0_check` or `r200_packet0_check`. The R100 checker relocates color/depth/texture/vertex/index buffers, updates tiling bits unless `RADEON_CS_KEEP_TILING_FLAGS` is set, tracks render target, z buffer, texture format/size/mips/cube faces, vertex format, VLINE waits, and draw state. PACKET3 validation supports known draw, vertex-buffer, index-buffer, clear, and NOP opcodes, rejects unknown opcodes, and calls `r100_cs_track_check` before draw packets. The tracker computes required buffer sizes for color, depth, AA resolve, textures including mip and compressed formats, cube faces, indexed and non-indexed vertex arrays, and immediate draws, rejecting unbound or undersized buffers before the IB reaches hardware.

IRQ processing acknowledges software, vblank, page-flip, and HPD status bits, loops until no more status remains, handles fences, DRM vblank accounting, page-flip completion, hotplug work scheduling, and MSI rearm. Power-management hooks choose dynpm target states, program GPIO voltage and reduced/dynamic SCLK behavior, change PCIe lanes, and temporarily suppress display requests across clock changes. Bandwidth update computes memory/display latency from current modes, clocks, VRAM width/type, memory timings, and display priority, then programs graphics buffer stop/start/critical points.

### State, Persistence, And Dependencies
Persistent driver state lives in `struct radeon_device`: rings, fences, IRQ counters, mode info, PM state, GART table, MC aperture/VRAM data, firmware pointer, writeback buffer, scratch registers, safe-register bitmap, and cached HDP control. Hardware-persistent state includes CP ring registers, MC FB/AGP locations, AIC PCI GART registers, display CRTC offsets/pitches, PLL registers, surface registers, interrupt masks/status, and GPU reset/bus-mastering state. CS parser state is temporary in `struct r100_cs_track`, allocated per parse and attached to `p->track`; it records enough state to prove draw commands cannot read or write outside referenced BOs.

Dependencies include Linux firmware loading, PCI config and bus-master APIs, DRM vblank/framebuffer/CRTC helpers, Radeon core subsystems for rings, fences, IBs, BO/TTM, GART, AGP, PM, BIOS/COMBIOS, scratch registers, IRQ KMS, surface management, and fixed-point math. Register definitions come from `r100d.h`, `radeon_reg.h`, `rs100d.h`, `rv200d.h`, `rv250d.h`, and related safe-register bitmap headers. `r100_track.h` supplies the CS tracking structures and prototypes used by this file and R200/R300 parser code.

### Integration Points
The ASIC function table calls these routines for legacy Radeon devices. Display code uses the vblank, page-flip, HPD, and bandwidth hooks. Memory management uses PCI GART, surface-register, copy-blit, and VRAM sizing helpers. The scheduler and fence code use CP ring/IB/fence operations. Userspace command submission relies on the CS parser and safe-register bitmap as the main isolation boundary. Debugfs exposes RBBM, CP ring/CSQ FIFO, and MC state for diagnosis. Power-management code invokes dynpm/profile/misc/prepare/finish hooks.

### Risks
The CS validator is security-sensitive: any missed register, relocation, tiling bit, texture size, vertex size, or draw-count case can allow GPU memory access outside authorized BOs. Size calculations use mixed `unsigned`, `unsigned long`, and hardware-derived values, so overflow and off-by-one behavior need care, especially for compressed/cube textures and immediate draw dword counts. `r100_cs_parse` returns early on errors without freeing the allocated `track` in this file, so ownership/freeing by the caller should be verified. Ring and reset code relies on polling timeouts; hangs or stale writeback pointers can cascade into GPU lockups. Firmware loading accepts any length divisible by eight but does not appear to validate family-specific expected microcode size. PCI GART TLB flush is a TODO, and stale one-entry hardware cache behavior is acknowledged. Power and bandwidth programming use many family-specific heuristics and hard-coded workarounds, so regressions may be board-specific. Suspend/fini paths must avoid disabling resources out of order while interrupts or rings are still active.

### Test Signals
High-value tests are legacy ASIC boot, COMBIOS init, ring and IB tests, fence interrupt tests, page flips on both CRTCs, vblank waits/counters, HPD plug/unplug, PCI and AGP GART memory moves, copy blits across large page counts, CS parser negative tests for forbidden registers, missing relocs, undersized color/depth/texture/vertex/index buffers, invalid draw modes, and HyperZ authorization. Hardware tests should cover reset after lockup, kexec sanity restoration, suspend/resume, DPM transitions, PCIe lane changes, bandwidth-heavy dual-display modes, debugfs reads, and operation with/without writeback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r100_track.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r100_track.h

### Purpose
`r100_track.h` declares the command-stream tracking structures and helper prototypes used by the R100/R200/R300 Radeon CS validators. It is the shared data model for proving that render targets, depth buffers, textures, cube faces, vertex arrays, AA resolve buffers, and draw parameters are valid before user command buffers are submitted to legacy GPUs.

### Important APIs, Types, And Functions
The core type is `struct r100_cs_track`, which stores hardware-family limits (`num_cb`, `num_texture`), current render height, vertex and draw metadata, color-channel mask, arrays for up to sixteen vertex buffers, color buffers up to `R300_MAX_CB`, depth and AA buffers, textures up to `R300_TRACK_MAX_TEXTURE`, and dirty/enable flags. Supporting types are `r100_cs_track_cb` for color/depth-like buffers, `r100_cs_track_array` for vertex buffers, `r100_cs_cube_info` for non-primary cube faces, and `r100_cs_track_texture` for texture dimensions, pitch, mip count, bytes per pixel, coordinate type, depth, compression, and flags. The header declares `r100_cs_track_check`, `r100_cs_track_clear`, `r100_cs_packet_parse_vline`, `r200_packet0_check`, `r100_reloc_pitch_offset`, and `r100_packet3_load_vbpntr`.

### Control Flow
The header has no local control flow. At runtime, `r100_cs_parse` allocates a `r100_cs_track`, `r100_cs_track_clear` initializes conservative defaults, PACKET0/PACKET3 checkers update fields as registers and draw packets are parsed, and `r100_cs_track_check` validates dirty state before draw packets. R200 and later parser code can reuse the same declarations while adding family-specific packet0 validation.

### State, Persistence, And Dependencies
Tracker state is per-command-submission and temporary. It persists only for the lifetime of the parser invocation and points to BOs from the parser relocation list; it does not own those BOs. The header depends on `radeon.h` for `struct radeon_bo`, `struct radeon_device`, `struct radeon_cs_parser`, and packet types, and on family constants that determine array sizes. Dirty flags allow incremental validation when command streams modify only some state.

### Integration Points
`r100.c` includes this header directly and implements the declared R100 functions. R200/R300 command-stream code uses the common structures and prototypes to share validation state. This header is part of the userspace command-submission trust boundary because its fields represent the driver's model of what hardware will read or write after a draw.

### Risks
The arrays are fixed-size and rely on parser code bounding texture units, color buffers, and vertex arrays correctly. Conservative defaults are intentionally huge or invalid, so forgetting to clear or update a field can cause false rejects or, worse, stale validation if dirty flags are mishandled. The tracker stores BO pointers without ownership, so lifetime must be tied to the parser relocation list. Several fields encode hardware units rather than bytes (`pitch`, `cpp`, mip dimensions), making unit consistency critical. Cube texture tracking has separate handling for older ASICs and can be easy to desynchronize from texture-format parsing.

### Test Signals
Useful tests include parser coverage for all texture units and cube faces, color/depth/AA resolve bounds, indexed and non-indexed vertex buffers, immediate draws, compressed DXT textures, non-power-of-two textures using pitch, R100/R200/R300 family limit differences, missing relocations, dirty-flag transitions, and shared R200 packet0 paths that call into the R100 tracking helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r100_track.h -->
