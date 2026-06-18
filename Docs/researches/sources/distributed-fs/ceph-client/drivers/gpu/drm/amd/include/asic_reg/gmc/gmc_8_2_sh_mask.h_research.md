# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_8_2_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002743`: lines 1-5194, `Docs/researches/chunks/subset-b-002743_research.md`
- `subset-b-002744`: lines 5195-7850, `Docs/researches/chunks/subset-b-002744_research.md`

## Chunk Research

### subset-b-002743: lines 1-5194

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_8_2_sh_mask.h lines 1-5194

## Scope

This chunk covers the first 5,194 lines of the generated AMD GMC 8.2 register shift/mask header. The source is a C preprocessor header guarded by `GMC_8_2_SH_MASK_H`; it contains no functions, structs, global variables, or executable logic. Its output is a dense collection of `<REGISTER>__<FIELD>_MASK` and `<REGISTER>__<FIELD>__SHIFT` constants used to encode and decode 32-bit memory-controller and GPU-memory-controller MMIO registers.

The covered range starts at the copyright/header guard and ends at `MC_XBAR_ARB_MAX_BURST__WR_PORT1__SHIFT`. It is the first chunk of a larger 7,850-line file, so the merged per-file report must connect this chunk with later `gmc_8_2_sh_mask.h` chunks for the remaining register fields.

## Purpose

`gmc_8_2_sh_mask.h` provides the bitfield ABI for AMDGPU code that targets GMC 8.2 hardware. The sibling `gmc_8_2_d.h` header provides register address macros such as `mmMC_ARB_RAMCFG` and `mmMC_HUB_RDREQ_DMIF_LIMIT`; this header provides the masks and shifts for fields within those registers. Driver code typically consumes these definitions through AMDGPU helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, direct mask/shift arithmetic, `RREG32`, and `WREG32`.

The chunk maps hardware state for memory-controller enablement, arbitration, DRAM timing, client throttling, hub read/write queues, virtual memory apertures, channel mapping, SR-IOV-visible shared state, peer-to-peer routing, XPB routing, and xbar credits. Because the file is generated from hardware register documentation, the constant names are the primary API surface.

## Important Macro Families

### MC and Arbitration Control

The first part of the chunk defines memory-controller configuration and arbitration fields:

- `MC_CONFIG` and `MC_CONFIG_MCD` enable writes to MCD channels (`MCDW` through `MCDV` or numbered `MCD0` through `MCD7`), control MC read enable fields, and provide index-mode enables.
- `MC_CG_CONFIG` and `MC_CG_CONFIG_MCD` repeat the same enable/index pattern for clock-gated/indexed access.
- `MC_ARB_ATOMIC`, `MC_ARB_SNOOP`, `MC_ARB_GRUB`, `MC_ARB_GRUB2`, `MC_ARB_GRUB_PROMOTE`, `MC_ARB_RET_CREDITS*`, and `MC_ARB_MAX_LAT_*` describe atomic/snoop grouping, outstanding limits, return credits, real-time grouping, urgent/promote behavior, and latency measurement.
- `MC_ARB_AGE_CNTL`, `MC_ARB_AGE_RD`, and `MC_ARB_AGE_WR` expose read/write group aging controls, reset bits, enable bits, rates, and divide fields.
- `MC_ARB_PM_CNTL`, `MC_ARB_CG`, `MC_ARB_CAC_CNTL`, `MC_ARB_MISC`, `MC_ARB_MISC2`, and `MC_ARB_MISC3` define power-management override, clock gating request/response, calibration, harshness, GECC/replay status, UVD/DMIF urgent behavior, and miscellaneous arbitration controls.

These macros are used by bring-up, power-management, and debugging paths to select how memory-controller clients are grouped, aged, throttled, and allowed to make forward progress.

### DRAM Geometry, Timing, and ECC

The chunk includes register fields for DRAM topology and timing:

- `MC_ARB_RAMCFG` encodes number of banks, ranks, rows, columns, channel size, groups, and reserved layout fields.
- `MC_ARB_BANKMAP`, `MC_ARB_ADDR_SWIZ0/1`, `MC_ARB_ADDR_HASH`, `MC_SHARED_CHMAP`, `MC_SHARED_CHREMAP`, and `MC_SHARED_CHREMAP2` encode address/channel swizzle and remapping.
- `MC_ARB_DRAM_TIMING`, `MC_ARB_DRAM_TIMING2`, and their `_1` variants encode activate/read/write, RAS-to-RAS, precharge, write-plus-precharge, and bus turn timing.
- `MC_ARB_GECC2`, `MC_ARB_GECC2_STATUS`, `MC_ARB_GECC2_MISC`, `MC_ARB_GECC2_DEBUG`, `MC_ARB_GECC2_DEBUG2`, and `MC_ARB_GECC2_CLI` encode graphics ECC enable/mode, error status/clear bits, replay behavior, injection/debug fields, and client-specific GECC bypass.

`amdgpu/gfx_v8_0.c` includes this header and reads `mmMC_ARB_RAMCFG`, then uses `REG_GET_FIELD(..., MC_ARB_RAMCFG, NOOFBANK/NOOFRANKS/NOOFCOLS)` to derive graphics address configuration. That is a concrete example of these generated masks affecting runtime GPU configuration.

### Training, Refresh, Scheduling, and Weight Tables

Several families define low-level memory scheduler behavior:

- `MC_ARB_RTT_DATA`, `MC_ARB_RTT_CNTL0/1/2`, and `MC_ARB_RTT_DEBUG` cover read-to-write/write-to-read training windows, train periods, thresholds, phase adjustment, filtering, and debug readback.
- `MC_ARB_RFSH_CNTL` and `MC_ARB_RFSH_RATE` cover refresh enablement, urgency, accumulation, single-bank refresh, and pending-rate selection.
- `MC_ARB_WTM_CNTL_RD/WR`, `MC_ARB_WTM_GRPWT_RD/WR`, `MC_CITF_WTM_RD_CNTL/WR_CNTL`, `MC_HUB_RDREQ_WTM_CNTL`, and `MC_HUB_WDP_WTM_CNTL` provide group decrement/weight controls for read and write traffic.
- `MC_ARB_POP`, `MC_ARB_MINCLKS`, `MC_ARB_SQM_CNTL`, `MC_ARB_GDEC_RD_CNTL`, `MC_ARB_GDEC_WR_CNTL`, `MC_ARB_LM_RD`, `MC_ARB_LM_WR`, `MC_ARB_REMREQ`, and `MC_ARB_REPLAY` tune pop queues, minimum clocks, dynamic SQM, group decode, list manager, remote requests, and replay flow.

Most of these fields are hardware-tuning knobs. They are persistent only in hardware register state and must be programmed in sequences owned by the GPU initialization or power-management code, not by this header.

### Client Interface and Client Throttling

The `MC_CITF_*`, `MC_RD_*`, and `MC_WR_*` blocks expose the client-interface side of GMC:

- `MC_CITF_XTRA_ENABLE` enables extra read/write clients and connection controls for CB/DB/TC client paths.
- `MC_CITF_CNTL`, `MC_CITF_CREDITS_VM`, `MC_CITF_CREDITS_ARB_RD/WR/RD2`, `MC_CITF_INT_CREDITS`, `MC_CITF_INT_CREDITS_WR`, `MC_CITF_RET_MODE`, `MC_CITF_DAGB_CNTL`, `MC_CITF_DAGB_DLY`, `MC_CITF_REMREQ`, and `MC_CITF_CREDITS_XBAR` define interface credits, return ordering, priority modes, DAGB behavior, remote-request credits, and crossbar credits.
- `MC_RD_CB`, `MC_RD_DB`, `MC_RD_TC0`, `MC_RD_TC1`, `MC_RD_HUB`, `MC_WR_CB`, `MC_WR_DB`, `MC_WR_TC0`, `MC_WR_TC1`, and `MC_WR_HUB` share a common field layout: enable, prescale, blackout exemption, stall mode/override, max burst, lazy timer, and WTM stall override.
- `MC_RD_GRP_EXT`, `MC_WR_GRP_EXT`, `MC_RD_GRP_LCL`, `MC_WR_GRP_LCL`, `MC_RD_GRP_GFX/SYS/OTH`, and `MC_WR_GRP_GFX/SYS/OTH` assign clients such as CP, SH, IA, RLC, VMC, SDMA, DMIF, MCIF, SMU, VCE, UVD, HDP, SEM, ACP, ISP, VP8, XDMA, and XDMAM into read/write groups.

These definitions are integration points for memory QoS and client fairness policy. Since many clients have nearly identical field layouts, mechanical copy errors or generation drift would be hard to detect by visual inspection alone.

### HUB Read Request and Write Data Path

The largest middle portion of the chunk maps HUB queueing and per-client request controls:

- `MC_HUB_MISC_POWER`, `MC_HUB_MISC_HUB_CG`, `MC_HUB_MISC_VM_CG`, and `MC_HUB_MISC_SIP_CG` cover power blackouts and clock-gating delay/enable fields.
- `MC_HUB_MISC_STATUS`, `MC_HUB_MISC_IDLE_STATUS`, and `MC_HUB_MISC_ATOMIC_IDLE_STATUS` expose outstanding read/write/atomic activity for GFX, RLC, SDMA, display, UVD, SMU, HDP, VMC, VCE, ACP, SAMMSP, XDMA, ISP, VP8, RPB, MCD, and hub paths.
- `MC_HUB_WDP_CNTL`, `MC_HUB_RDREQ_CNTL`, and `MC_HUB_WRRET_CNTL` define global write-data path, read-request, and write-return controls, including jump-ahead, stall override, self-init disable, PwrXpress, MCD stall modes, HDP deadlock break, UVD transcode, DMIF urgent threshold, and fair channel switching.
- `MC_HUB_WDP_STATUS`, `MC_HUB_RDREQ_STATUS`, and `MC_HUB_WRRET_STATUS` expose MCD availability, global storage fullness, power-related error, and write-return availability.
- `MC_HUB_WDP_CREDITS*`, `MC_HUB_RDREQ_CREDITS*`, `MC_HUB_WDP_GBL0/1`, `MC_HUB_RDREQ_GBL0/1`, and MCD credit registers encode VM/storage/read/write/priority credit budgets and stall thresholds.
- Per-client blocks such as `MC_HUB_RDREQ_SMU`, `MC_HUB_RDREQ_SDMA0/1`, `MC_HUB_RDREQ_HDP`, `MC_HUB_RDREQ_RLC`, `MC_HUB_RDREQ_SEM`, `MC_HUB_RDREQ_VCE0/1`, `MC_HUB_RDREQ_UMC`, `MC_HUB_RDREQ_UVD`, `MC_HUB_RDREQ_DMIF`, `MC_HUB_RDREQ_MCIF`, `MC_HUB_RDREQ_VMC`, `MC_HUB_RDREQ_ACPG/ACPO`, `MC_HUB_RDREQ_ISP_*`, and matching `MC_HUB_WDP_*` blocks repeat client-local enable, timing, stall, priority, VM-bypass, and bypass-availability fields.

Display code includes this header and specifically uses `MC_HUB_RDREQ_DMIF_LIMIT__ENABLE__SHIFT` and `MC_HUB_RDREQ_DMIF_LIMIT__ENABLE_MASK` in DCE 10/11 resource definitions. `mxgpu_vi.c` also lists `mmMC_HUB_RDREQ_DMIF_LIMIT` and `mmMC_HUB_WDP_UMC` in virtualization register programming data, showing that these fields are consumed outside plain display bring-up.

### Virtual Memory and Shared Virtualization State

The chunk defines the main GMC 8.2 VM aperture and L1 TLB fields:

- `MC_VM_FB_LOCATION`, `MC_VM_FB_OFFSET`, `MC_VM_AGP_TOP`, `MC_VM_AGP_BOT`, `MC_VM_AGP_BASE`, `MC_VM_SYSTEM_APERTURE_LOW_ADDR`, `MC_VM_SYSTEM_APERTURE_HIGH_ADDR`, and `MC_VM_SYSTEM_APERTURE_DEFAULT_ADDR` encode framebuffer, AGP, and system aperture base/top/default page numbers.
- `MC_VM_DC_WRITE_CNTL` and `MC_VM_DC_WRITE_HIT_REGION_*_LOW_ADDR/HIGH_ADDR` control display-controller write hit-region behavior and local/system memory write handling.
- `MC_VM_MX_L1_TLB_CNTL`, `MC_VM_MB_L1_TLB0..3_DEBUG/STATUS`, and `MC_VM_MD_L1_TLB0..3_DEBUG/STATUS` expose L1 TLB enablement, fragment processing, system access mode, unmapped access behavior, advanced driver model enablement, invalidation, forced misses, effective sizes, queue sizes, and busy status for MB/MD instances.
- `MC_VM_MB_L2ARBITER_L2_CREDITS` and `MC_VM_MD_L2ARBITER_L2_CREDITS` expose L2 interface credits.
- `MC_SHARED_VF_ENABLE`, `MC_SHARED_VIRT_RESET_REQ`, and `MC_SHARED_ACTIVE_FCN_ID` describe SR-IOV/shared function state, reset request bits, active VF ID, and PF/VF indication.
- `MC_SHARED_BLACKOUT_CNTL` controls blackout behavior, MCD blackout count, and dummy SRBM read-return behavior.

These fields are critical during GPU memory initialization, VM setup, reset, suspend/resume, and virtualization. Incorrect masks here can misplace framebuffer apertures, allow unmapped system access incorrectly, fail to invalidate TLBs, or disturb PF/VF isolation.

### RPB, XPB, P2P Routing, and XBAR

The tail of the chunk covers routing between request buffers, peer paths, XPB, and the memory crossbar:

- `MC_RPB_*` blocks cover PCIe ordering, BIF credits, write/read/ATC switch counts, write combining, CID-to-queue mapping, performance counters, TCI control, and extended queue data.
- `MC_XPB_RTR_SRC_APRTR*`, `MC_XPB_XDMA_RTR_SRC_APRTR*`, `MC_XPB_RTR_DEST_MAP*`, and `MC_XPB_XDMA_RTR_DEST_MAP*` define aperture source bases and destination mappings for normal and XDMA routes.
- `MC_XPB_CLG_CFG0..36`, `MC_XPB_CLG_EXTRA`, `MC_XPB_CLG_EXTRA_RD`, `MC_XPB_LB_ADDR`, `MC_XPB_UNC_THRESH_HST/SID`, `MC_XPB_WCB_STS`, and `MC_XPB_WCB_CFG` configure coherency/lookup grouping, write-combine buffers, host/side flush behavior, and uncacheable thresholds.
- `MC_XPB_P2P_BAR_CFG`, `MC_XPB_P2P_BAR0..7`, `MC_XPB_P2P_BAR_SETUP`, `MC_XPB_P2P_BAR_DEBUG`, `MC_XPB_P2P_BAR_DELTA_ABOVE/BELOW`, `MC_XPB_PEER_SYS_BAR0..9`, and `MC_XPB_XDMA_PEER_SYS_BAR0..3` encode peer-to-peer BAR validity, addresses, side-ok state, host/memory system BAR flags, send/compress/update disable fields, snoop, read enable, and ATC-translated state.
- `MC_XPB_CLK_GAT`, `MC_XPB_INTF_CFG`, `MC_XPB_INTF_CFG2`, `MC_XPB_INTF_STS`, `MC_XPB_PIPE_STS`, `MC_XPB_SUB_CTRL`, `MC_XPB_PERF_KNOBS`, `MC_XPB_STICKY`, `MC_XPB_STICKY_W1C`, and `MC_XPB_MISC_CFG` cover XPB clock gating, credits, snoop/ordering overrides, buffer fullness, stalls, sub-block resets, sticky bits, and diagnostics.
- `MC_XBAR_ADDR_DEC`, `MC_XBAR_REMOTE`, `MC_XBAR_*_CREDIT*`, `MC_XBAR_CHTRIREMAP`, `MC_XBAR_TWOCHAN`, `MC_XBAR_ARB`, and `MC_XBAR_ARB_MAX_BURST` control crossbar address decoding, GECC/RB split handling, remote request enablement, per-output credits, channel remap, two-channel behavior, arbitration priority, and read/write max bursts.

These definitions are particularly sensitive because they govern traffic routing between GPU clients, memory channels, PCIe/BIF, XDMA, and peer GPUs/devices.

## Control Flow

There is no runtime control flow in this chunk. The only control-flow-like structure is the include guard. All behavioral effects occur indirectly when compiled driver code uses these masks and shifts to compose MMIO writes or decode MMIO reads.

The runtime control flow is owned by consumers such as `gfx_v8_0.c`, `mxgpu_vi.c`, and DCE display resource/compressor/mem-input files. They include `gmc_8_2_d.h` for addresses and this header for fields, then perform register reads/writes through AMDGPU register access helpers.

## State and Persistence Behavior

The header itself persists no software state. The state described by the macros is hardware register state. Important persistent or latched hardware state represented in this chunk includes:

- MC channel enables, index modes, clock-gating configuration, power blackout state, and low-power memory power timing.
- DRAM geometry, bank/channel remap, timing, address swizzle/hash, GECC status/clear/debug state, and replay state.
- Arbitration weights, return credits, outstanding limits, urgency/promotion state, refresh controls, and scheduler age/list-manager state.
- Client-interface and hub credits, per-client enable/stall/timing/bypass values, global fullness/availability status, and deadlock warning bits.
- VM apertures, framebuffer/AGP/system page ranges, DC write hit regions, L1 TLB invalidation/debug/status, and PF/VF shared state.
- XPB/RPB/P2P routing tables, P2P BAR validity/address state, peer system BAR state, sticky XPB status, sub-block reset/stall controls, and xbar credits/arbitration.

Some fields are ordinary configuration, some are read-only status, some are clear bits, and some are command-like controls such as TLB invalidation, GECC status clear, sticky write-one-to-clear fields, and XPB sub-block resets. The macros do not encode sequencing, polling, side effects, or locking requirements.

## Dependencies and Integration Points

Direct dependencies:

- `gmc_8_2_d.h` supplies the matching register-address macros.
- `gmc_8_2_enum.h` supplies related generated enumeration values for this hardware block.
- AMDGPU register helpers consume the `__SHIFT` and `_MASK` names when setting or extracting register fields.

Observed include sites in this tree:

- `amdgpu/gfx_v8_0.c` includes this header and uses GMC fields such as `MC_ARB_RAMCFG` to derive graphics/memory address configuration.
- `amdgpu/mxgpu_vi.c` includes this header for VI SR-IOV/MxGPU register save/restore or programming tables, including hub/DMIF and WDP-related registers.
- `display/dc/resource/dce100/dce100_resource.c` and `display/dc/resource/dce110/dce110_resource.c` include this header and expose `MC_HUB_RDREQ_DMIF_LIMIT` register/mask/shift metadata to display resource code.
- `display/dc/dce110/dce110_compressor.c` and `display/dc/dce110/dce110_mem_input_v.c` include this header alongside `gmc_8_2_d.h` for display memory/compression programming.

Cross-generation integration is visible through nearby generated headers (`gmc_6_0_sh_mask.h`, `gmc_7_0_sh_mask.h`, `gmc_7_1_sh_mask.h`, and `gmc_8_1_sh_mask.h`) that define similarly named fields with generation-specific layouts. Consumers must include the matching generation header; field names are similar enough that accidental cross-generation substitution could compile in some cases while programming the wrong bit positions.

## Risks

- Bitfield drift is high impact. A wrong mask or shift can corrupt unrelated register bits and cause GPU hangs, memory corruption, display underflow, bad VM aperture setup, incorrect channel routing, or failed virtualization isolation.
- The file is generated and highly repetitive. Families such as per-client HUB RDREQ/WDP, MCD channel controls, XPB CLG config, P2P BARs, and TLB debug/status blocks are prone to copy/generation mistakes that are hard to spot manually.
- Several names look like normal configuration but are status/clear/command fields. GECC clear bits, TLB invalidation bits, XPB sticky W1C bits, and XPB reset/stall controls require hardware-specific sequencing.
- VM and aperture fields are safety-sensitive. Incorrect `MC_VM_*` or P2P BAR programming can route requests to the wrong physical/system memory range.
- Hub/client QoS fields are performance- and correctness-sensitive. Credit, stall, blackout, urgent, and lazy-timer mistakes can produce starvation, deadlock warnings, display underruns, or unstable power transitions.
- SR-IOV fields such as `MC_SHARED_VF_ENABLE`, reset requests, active function IDs, and MxGPU register tables must preserve PF/VF isolation.
- The chunk boundary falls inside the larger header. Later chunks may define related xbar, VM, or additional GMC fields; final per-file synthesis should avoid treating this first chunk as the complete GMC 8.2 surface.

## Test and Validation Signals

Useful validation for this chunk is primarily build and hardware-integration coverage:

- Build AMDGPU and display code that includes `gmc/gmc_8_2_sh_mask.h`; this catches missing or renamed mask/shift symbols.
- Exercise `gfx_v8_0` address-configuration paths that read `MC_ARB_RAMCFG` and derive bank/rank/column geometry.
- Exercise DCE 10/11 display resource paths that use `MC_HUB_RDREQ_DMIF_LIMIT` masks/shifts, especially display memory bandwidth and underflow-sensitive scenarios.
- Run GPU reset, suspend/resume, and power-management tests that touch MC clock gating, blackout, hub idle/status, and channel enable fields.
- Run VM aperture and TLB tests that validate framebuffer/system/AGP ranges, L1 TLB invalidation/busy status, and unmapped-access policy.
- Run SR-IOV/MxGPU validation for shared VF enable/reset/active-function state and hub register programming tables.
- Run peer-to-peer/XDMA tests, if available for the hardware, to validate XPB source/destination maps, P2P BAR validity/address fields, snoop/ATC flags, and xbar credit behavior.
- Use register readback or trace instrumentation to confirm `REG_SET_FIELD` and `REG_GET_FIELD` round-trip values for high-risk fields such as `MC_VM_FB_LOCATION`, `MC_HUB_RDREQ_CNTL`, `MC_XPB_P2P_BAR_CFG`, and `MC_XBAR_*_CREDIT*`.

### subset-b-002744: lines 5195-7850

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_8_2_sh_mask.h lines 5195-7850

## Scope

This chunk is the final 2,656 lines of the generated-style AMDGPU GMC 8.2 shift/mask header. It contains only preprocessor `#define` symbols for register-field masks and shifts, followed by the `GMC_8_2_SH_MASK_H` include-guard close at line 7850.

There are no functions, structs, enums, global variables, allocations, locks, loops, branches, callbacks, or runtime side effects in this range. The exported surface is compile-time metadata used by AMDGPU code to pack values into, and unpack values from, GMC 8.2 memory-controller, virtual-memory, translation-cache, arbitration, power, and writeback registers.

Although the path is under a `ceph-client` source mirror, this file is AMD GPU DRM hardware metadata. It is not Ceph filesystem code.

## Purpose

`gmc_8_2_sh_mask.h` pairs with the GMC 8.2 register-offset header (`gmc_8_2_d.h`) and AMDGPU MMIO/register helpers. This tail chunk defines the bit layouts for register families that control or observe:

- MC crossbar arbitration and FIFO monitoring.
- MC, ATC, CHUB ATC, and GRUB performance counters.
- Address Translation Cache (ATC), ATS/PRI/PASID behavior, ATC L1/L2 TLB/cache debug state, fault reporting, and VMID-to-PASID mapping.
- GMCON power, clock-gating, stutter, PGFSM, and performance-monitor controls.
- VM L2 cache controls, VM contexts 0 and 1, context fault controls/status, dummy/default fault pages, invalidation requests/responses, PRT aperture/fault policy, page-table base/start/end registers, and identity apertures.
- SR-IOV/virtualization-related frame-buffer sizing and offset registers for virtual functions, plus MARC relocation/length windows.
- MC arbiter "HARSH" scheduling, GRUB priorities, GRUB probe/credit/feature controls, and transaction-control-buffer access.
- Fused DRAM address mapping, controller base/limit/high-offset fields, DRAM aperture/default/lock controls, and Garlic arbitration priorities.
- MCIF writeback buffer-manager state, buffer addresses, pitch, per-buffer status/error bits, software/VCE locking, interrupts, VMID filtering, arbitration, urgency watermarks, and debug access.

The file lets C code refer to field boundaries symbolically rather than hard-coding masks such as `0x10000000` or shifts such as `0x1c`. That is important because most consumers use read-modify-write sequences where one wrong mask can corrupt adjacent hardware fields.

## Important APIs, Types, And Constants

The "API" in this chunk is the naming convention:

- `<REGISTER>__<FIELD>_MASK` identifies the bit mask for a field.
- `<REGISTER>__<FIELD>__SHIFT` identifies the least-significant-bit position for that field.
- Full-width data/count fields use masks such as `0xffffffff`; smaller fields use byte, nibble, VMID, page-number, or client-id-sized masks.

Major exported register-field groups include:

- Lines 5195-5242: `MC_XBAR_ARB_MAX_BURST`, `MC_XBAR_FIFO_MON_CNTL*`, `MC_XBAR_FIFO_MON_RSLT*`, `MC_XBAR_FIFO_MON_MAX_THSH`, and spare crossbar words. These describe write-port burst limits, FIFO monitor start/stop thresholds and trigger IDs, four monitor result counters, maximum thresholds, and spare bits.
- Lines 5243-5762: performance-counter layouts for `MC_CITF`, `MC_HUB`, `MC_RPB`, `MC_MCBVM`, `MC_MCDVM`, `MC_VM_L2`, `MC_ARB`, `ATC`, `CHUB_ATC`, and `MC_GRUB`. Repeated patterns define low 32-bit count words, high 16-bit count/compare words, counter configuration fields (`PERF_SEL`, `PERF_SEL_END`, `PERF_MODE`, `ENABLE`, `CLEAR`), and result control (`PERF_COUNTER_SELECT`, start/stop triggers, enable-any, clear-all, stop-on-saturate).
- Lines 5763-6221: ATC/ATS address apertures, ATS control/debug/fault/status/default-page fields, ATC L2/L1 cache and TLB debug fields, read/write TLB status and parity-injection fields, all 16 VMID-to-PASID mapping registers, remap-complete status bits, outstanding VMID status bits, and SMU power/status bits.
- Lines 6222-6388: `GMCON_*` fields for client stall/urgency masks, stutter watermarks, debug, miscellaneous power/clock-gating/soft-reset controls, memory power low-power masks, MGCG override masks, perfmon controls/results, PGFSM indexed access, and STCTRL busy/handshake masks.
- Lines 6389-6834: VM L2 cache and VM context fields. These cover L2 cache enable/fragment/endian/PDE/PTE/default-page/identity modes, invalidation controls, cache sizing and force-miss debug, context enable/page-table-depth/fault-action bits for contexts 0 and 1, context fault address/status/default address fields, invalidation request/response domains 0-15, PRT apertures and fault-disabling policy, context-disable bits 0-15, page-table bases for contexts 0-15, and identity-aperture/physical-offset controls.
- Lines 6835-6984: SR-IOV and relocation fields: `MC_VM_FB_SIZE_OFFSET_VF0` through `VF15` for per-virtual-function frame-buffer size/offset pairs, `MC_VM_SYSTEM_APERTURE_*`, `MC_VM_LOCAL_FB_*`, `MC_VM_FB_LOCATION*`, AGP top/bot/base and default address fields, `MC_VM_MARC_RELOC_*`, `MC_VM_MARC_LEN_*`, and `MC_VM_MARC_CNTL`.
- Lines 6985-7320: MC arbiter and GRUB priority fields. `MC_ARB_HARSH_*` describes read/write priority groups, bandwidth periods/counts/saturation, force-highest/stall controls, and perf monitor selection. `MC_ARB_GRUB_PRIORITY*` maps memory clients such as CB, DB, TC, ACP, DMIF, MCIF, RLC, VMC, SDMA, HDP, UVD, VCE, SMU, SEM, ISP, VP8, and VIN to read/write GRUB priority fields.
- Lines 7321-7536: fused DRAM and Garlic arbitration fields. These include per-channel/chip-select base address and enable fields, DRAM bank address mapping, DCT base/limit/high-offset/mode fields, DRAM aperture/default/lock fields, isochronous and urgency priority enables/overrides, request credits, response FIFO limits, Garlic write priority fields, and the `MC_CG_DATAPORT` data word.
- Lines 7537-7624: GRUB probe map, post-probe delay, probe credits, feature toggles, TX credits, and indexed TCB data access.
- Lines 7625-7848: MCIF writeback buffer-manager fields for software and VCE control, current line and status readback, pitch, four buffer status/status2 blocks, arbitration/watermarks/test debug, Y/C base addresses and offsets for buffers 1-4, and writeback VMID access control.

## Control Flow

This chunk has no direct control flow. The implied runtime flow in AMDGPU code is:

1. Include `gmc_8_2_d.h` for the register address and this header for the register field layout.
2. Build a register value by shifting a field value with `__SHIFT` and masking it with `__MASK`, or isolate a hardware readback with the mask and shift.
3. Perform a register write, read-modify-write, poll, interrupt acknowledgement, fault decode, performance-counter readout, or debug dump in the surrounding driver.
4. Hardware consumes or produces the corresponding GMC/ATC/VM/MCIF/arbiter state.

The ordering requirements are external to this header. Examples include flushing or waiting for VM invalidations before reusing page tables, clearing fault status only after logging it, programming performance counters before enabling them, and respecting buffer locks/interrupt acks for MCIF writeback.

## State And Persistence Behavior

The header itself is stateless. The constants describe state that persists in hardware registers after driver writes, or transient state that software observes through readback registers.

Persistent control state includes VM L2 enable/configuration, VM context control, page-table base/start/end registers, context-disable bits, PRT policy, ATC/ATS mode bits, VMID/PASID mappings, per-VF frame-buffer windows, MARC relocation windows, DRAM/fused aperture mapping, arbiter/GRUB priorities, GMCON clock/power/stutter controls, and MCIF writeback buffer configuration.

Transient or event-like state includes performance counter low/high words, FIFO monitor result counters, ATC/VM busy/deadlock/fault/parity status, VM invalidation responses, protection-fault status/address/client fields, MCIF current-buffer/current-line/error/status bits, and interrupt ack/status bits.

Several fields have special persistence hazards:

- `CLEAR`, `CLEAR_ALL`, `CLEAR_*`, `INVALIDATE_*`, `POWER_DOWN`, `POWER_UP`, interrupt `ACK`, parity-injection, and indexed-read/write-enable fields are command-like bits. They may be write-one-to-trigger or otherwise edge-sensitive in hardware even though this header only exposes their positions.
- Fault status address fields and "allow subsequent updates" controls affect whether later faults overwrite earlier diagnostic state.
- VMID/PASID mappings and VM context page-table state are security-sensitive because stale mappings can expose one process or virtual function's memory to another.
- MCIF buffer lock and active/error bits coordinate software and VCE/writeback ownership. Wrong lock or ack handling can lose frames or hide overflow/line-length errors.

## Dependencies And Integration Points

This header depends on the generated GMC 8.2 register database staying synchronized with the hardware and with `gmc_8_2_d.h`. The direct include point found in this tree is VI-era AMDGPU code such as `amdgpu/mxgpu_vi.c`, which includes both `gmc/gmc_8_2_d.h` and `gmc/gmc_8_2_sh_mask.h` alongside other VI register headers.

Important integration surfaces include:

- AMDGPU MMIO helpers and read-modify-write helpers that combine register offsets with these masks/shifts.
- GMC v8 memory-management initialization and GPUVM programming paths, especially VM L2 cache setup, context setup, page-table base programming, dummy/default-page policy, and TLB/cache invalidation.
- Fault reporting, interrupt handling, and hang/debug dump paths that decode VM and ATC fault/status fields.
- SR-IOV and MxGPU paths that configure per-VF frame-buffer windows, VMID restrictions, and virtualization-related ATC/VM state.
- Performance-monitor/debugfs or profiling paths that program GMC/ATC/GRUB performance counters and read counter results.
- Power-management and clock-gating paths that use GMCON and ATC/VM clock-gating/memory-light-sleep fields.
- Display/video/writeback paths that program MCIF writeback buffers, pitches, addresses, locks, VMID access, and interrupt behavior.
- Memory-controller arbitration/tuning paths that use HARSH, GRUB, Garlic, and DRAM aperture/mapping fields.

Because the symbols are preprocessor macros, they are globally visible after inclusion. They must stay name-compatible with the rest of the AMDGPU register headers and cannot be scoped like C enums or typed constants.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong mask or shift compiles cleanly but programs the wrong hardware bits, potentially corrupting VM state, disabling faults, breaking address translation, or producing misleading diagnostics.
- Many register names are repeated with numeric suffixes (`0-15` VMIDs/domains/contexts/VFs, four perf counters, four MCIF buffers). Off-by-one edits or copy/paste drift can silently target the wrong VMID, invalidation domain, virtual function, or buffer.
- Full-width fields such as counters, data ports, fault-client names, and buffer base addresses need correct register width assumptions. Treating a page-number field as a byte address, or vice versa, would misprogram memory windows.
- VM fault controls include separate interrupt/default/save bits for multiple fault classes. Enabling default-page behavior where interrupt/save was expected can mask real page-table bugs.
- `VM_INVALIDATE_REQUEST` and `VM_INVALIDATE_RESPONSE` fields are per-domain bitmaps. Callers must not assume a request completed until the matching response bit is observed according to the surrounding driver protocol.
- ATC/ATS/PASID fields interact with IOMMU/PCIe ATS semantics. Incorrect disable, invalidation, or VMID/PASID mapping can cause stale translations, incorrect fault attribution, or isolation problems.
- Fault status update controls can overwrite the first fault if subsequent updates are allowed too early, making root-cause analysis harder after GPU hangs.
- Performance-counter selectors and result controls are repetitive across blocks but not interchangeable. A counter configured for one block's event mux may read plausible but meaningless values if used with another block.
- Debug and parity-injection fields (`INJECT_SOFT_PARITY_ERROR`, `INJECT_HARD_PARITY_ERROR`, cache/TLB read selectors) are dangerous outside controlled validation because they can deliberately create error conditions.
- Arbitration and priority fields can create QoS regressions. Misprogramming HARSH, GRUB, or Garlic priorities may starve display/video/SDMA clients or reduce GPU throughput without an obvious kernel failure.
- MCIF writeback status includes overflow, long-line, short-line, frame-length, lock, active, field, next-buffer, and current-line bits. Clearing or ignoring them incorrectly can hide dropped/corrupt writeback frames.
- Some symbols contain doubled wording such as `*_MASK_MASK`, reflecting generated names for fields that themselves are called "mask". Consumers should not "clean up" these names without updating all generated users.

## Test Signals

Useful validation signals for this chunk are mostly build, generated-data, and hardware/runtime checks:

- Kernel build coverage for AMDGPU VI/GMC 8.2 files that include `gmc_8_2_sh_mask.h`.
- Mechanical comparison against AMD's authoritative GMC 8.2 register database for every mask and shift in lines 5195-7850.
- Static checks that every field mask is compatible with its shift and width, and that repeated numeric families have the expected sequence of bits or register suffixes.
- Cross-checks that every register field here has a matching register offset in `gmc_8_2_d.h` and, where applicable, matching enum/value definitions in companion headers.
- GPUVM tests that create/destroy contexts, program page tables, invalidate VM domains, exercise dummy/default-page behavior, and verify no stale translations or unexpected VM faults.
- Fault-injection or negative tests that trigger read/write/execute/PDE/dummy/range faults and verify decoded VMID, client ID, address, protection bits, and interrupt/save/default behavior.
- SR-IOV/MxGPU tests that validate per-VF framebuffer size/offset isolation, allowed VMID masks, PASID mappings, and virtualization entry/exit invalidation behavior.
- Performance-counter tests selecting representative MC, ATC, CHUB_ATC, VM_L2, ARB, and GRUB events and checking that counters clear, enable, saturate/stop, and increment under targeted workloads.
- Power-management tests for GMCON/ATC/VM clock-gating and memory-light-sleep settings, with resume/reset paths verifying register reprogramming.
- Display/video writeback tests that cycle MCIF buffers 1-4, exercise software and VCE locks, verify interrupt ack/status behavior, and detect overflow/line/frame-length error reporting.
- Memory-bandwidth and display-stability workloads to catch arbitration regressions from HARSH, GRUB, Garlic, or DRAM mapping fields.
- Runtime warning signals include GPU VM faults with wrong client/VMID decode, invalidation timeouts, hangs after context teardown, impossible performance counter values, SR-IOV memory isolation failures, dropped writeback frames, or display underflow/stutter after arbitration changes.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002744`. It covers lines 5195-7850, the tail of `gmc_8_2_sh_mask.h`. The final per-file research should merge this with earlier chunks for the complete GMC 8.2 register-field map, including register families whose definitions begin before line 5195.
