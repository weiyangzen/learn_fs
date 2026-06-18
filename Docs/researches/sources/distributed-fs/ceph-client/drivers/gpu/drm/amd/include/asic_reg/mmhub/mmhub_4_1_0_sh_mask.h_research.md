# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_4_1_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002817`: lines 1-2373, `Docs/researches/chunks/subset-b-002817_research.md`
- `subset-b-002818`: lines 2374-4752, `Docs/researches/chunks/subset-b-002818_research.md`
- `subset-b-002819`: lines 4753-6943, `Docs/researches/chunks/subset-b-002819_research.md`

## Chunk Research

### subset-b-002817: lines 1-2373

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_4_1_0_sh_mask.h lines 1-2373

## Scope

This chunk covers the opening 2,373 lines of the generated AMD MMHUB 4.1.0 shift/mask header. It starts with the license, include guard, and `mmhub_dagb_dagbdec` address-block marker, then defines the bitfield constants for almost all of the `DAGB0` decoder block. The final covered lines begin `DAGB1_RDCLI0`; the rest of the DAGB1 and later MMHUB register map belongs to later chunks.

The requested range contains 2,176 `#define` lines. Nearly all definitions follow AMD's generated convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit mask used to isolate or compose that field.

This is hardware metadata only. It declares no C functions, structs, enums, variables, storage, includes, locks, or executable logic. Although the path is under a local `ceph-client` source mirror, this file is AMDGPU MMHUB register ABI data, not distributed filesystem behavior.

## Purpose

The purpose of this header section is to provide the field-level ABI for programming MMHUB 4.1.0 DAGB registers from AMDGPU driver code. The companion `mmhub_4_1_0_offset.h` header supplies register addresses, while this file supplies the bit positions and masks used by helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15`.

The covered DAGB0 registers control how MMHUB read and write clients are assigned to virtual channels, how bandwidth and outstanding-request limits are applied, how TLB and FIFO credits are budgeted, how SDP traffic is prioritized and mapped, and how error/performance/status registers are interpreted.

## Important Macro Families

### Read Client Arbitration

Lines 28-531 define `DAGB0_RDCLI0` through `DAGB0_RDCLI23`. Each read client exposes the same packed fields:

- `VIRT_CHAN`, selecting the client virtual channel.
- `CHECK_TLB_CREDIT`, enabling TLB-credit enforcement.
- `URG_HIGH` and `URG_LOW`, priority or urgency thresholds.
- `MAX_BW_ENABLE` and `MAX_BW`, setting maximum bandwidth throttling.
- `MIN_BW_ENABLE` and `MIN_BW`, setting minimum bandwidth reservation.
- `OSD_LIMITER_ENABLE` and `MAX_OSD`, limiting outstanding operations.

This repeated 24-client layout is a major integration surface for memory-client QoS. Consumers must keep the client index, field width, and direction aligned with the offset header.

### Read DAGB Control, Burst, Timer, VC, And Credit Fields

The read-side aggregate controls define:

- `DAGB0_RD_CNTL`: client and VC bandwidth windows, shared VC count, and VC round-robin enable.
- `DAGB0_RD_IO_CNTL` and `DAGB0_RD_GMI_CNTL`: two client-specific priority overrides plus common priority for IO and GMI paths.
- `DAGB0_RD_ADDR_DAGB`: DAGB enable lanes, jump-ahead enable, self-init disable, `WHOAMI`, and jump mode.
- `DAGB0_RD_CGTT_CLK_CTRL` and `DAGB0_L1TLB_RD_CGTT_CLK_CTRL`: clock-gating/light-sleep timing, disable, and busy-override fields.
- `DAGB0_RD_ADDR_DAGB_MAX_BURST0..2` and `DAGB0_RD_ADDR_DAGB_LAZY_TIMER0..2`: 4-bit per-client controls for clients 0-23.
- `DAGB0_RD_VC0_CNTL` through `DAGB0_RD_VC5_CNTL`, plus `DAGB0_RD_IO_VC_CNTL` and `DAGB0_RD_GMI_VC_CNTL`: storage credits, max/min bandwidth, OSD limiters, and max OSD per VC class.
- `DAGB0_RD_CNTL_MISC`: storage-pool credits, `UTCL2_VCI`, read-return compression/legacy behavior, and IO compression bypass shift.
- `DAGB0_RD_TLB_CREDIT`: six packed TLB credit fields.

Read pending/status macros cover `ASK`, `GO`, `GBLSEND`, `TLB`, `OARB`, `ASK2ARB`, `ASK2DF`, `OSD`, and `ASK_OSD` pending state. Most expose a 24-bit client busy mask; `ASK2DF` exposes a `NUM` shift in this slice without a paired mask.

### Write Client Arbitration

Lines 877-1380 mirror the read client layout for `DAGB0_WRCLI0` through `DAGB0_WRCLI23`. Each write client has the same `VIRT_CHAN`, TLB-credit, urgency, bandwidth, and outstanding-operation limiter fields as the read client registers.

Write aggregate controls then define:

- `DAGB0_WR_CNTL`: client/VC bandwidth windows and VC round-robin enable.
- `DAGB0_WR_IO_CNTL` and `DAGB0_WR_GMI_CNTL`: IO and GMI priority override fields.
- `DAGB0_WR_ADDR_DAGB` and `DAGB0_WR_DATA_DAGB`: address and data DAGB enable/jump/self-init/identity controls.
- `DAGB0_WR_CGTT_CLK_CTRL` and `DAGB0_L1TLB_WR_CGTT_CLK_CTRL`: write-side clock-gating controls.
- `DAGB0_WR_ADDR_DAGB_MAX_BURST0..2`, `DAGB0_WR_ADDR_DAGB_LAZY_TIMER0..2`, `DAGB0_WR_DATA_DAGB_MAX_BURST0..2`, and `DAGB0_WR_DATA_DAGB_LAZY_TIMER0..2`: per-client address/data burst and lazy-timer controls.
- `DAGB0_WR_VC0_CNTL` through `DAGB0_WR_VC5_CNTL`, `DAGB0_WR_IO_VC_CNTL`, and `DAGB0_WR_GMI_VC_CNTL`: write VC credit, bandwidth, and OSD limits.
- `DAGB0_WR_CNTL_MISC`: storage pool credit, `HDP_CID`, DCC/compression bypass and mapping-related shifts.
- `DAGB0_WR_TLB_CREDIT`, `DAGB0_WR_DATA_FIFO_CREDIT_CNTL1`, and `DAGB0_WR_ATOMIC_FIFO_CREDIT_CNTL1`: TLB, write-data FIFO, and atomic FIFO credit fields.

Write pending/status macros cover the same read-side pending states plus DBUS ask/go pending state and GPU snoop override masks for all 24 write clients.

### SDP, Error, Performance, And Debug Fields

The second half of the chunk defines DAGB0 SDP and observability controls:

- `DAGB0_SDP_ERR_STATUS` exposes read/write response status, data status, metadata/data parity error shifts, clear-on-error control, busy-on-error, FUE flag, and FUE client fields.
- `DAGB0_DAGB_DLY`, `DAGB0_CNTL_MISC`, and `DAGB0_CNTL_MISC2` expose delay selection, bandwidth initialization timing, fatal-edge mode shift, busy overrides, swap control, read-return FIFO performance mode, and tap-chain clock-gating disables.
- `DAGB0_FIFO_EMPTY`, `DAGB0_FIFO_FULL`, `DAGB0_RD_CREDITS_FULL`, and `DAGB0_WR_CREDITS_FULL` expose packed fullness/emptiness status.
- `DAGB0_PERFCOUNTER_LO`, `DAGB0_PERFCOUNTER_HI`, `DAGB0_PERFCOUNTER0_CFG` through `DAGB0_PERFCOUNTER2_CFG`, and `DAGB0_PERFCOUNTER_RSLT_CNTL` define counter values, compare values, event selections, modes, enable/clear bits, start/stop triggers, and saturation behavior.
- `DAGB0_L1TLB_REG_RW` provides L1 TLB control read/write command bits.
- `DAGB0_RESERVE0` through `DAGB0_RESERVE3` are full-width reserved fields.

The SDP QoS and request groups include `DAGB0_SDP_RD_BW_CNTL`, `DAGB0_SDP_PRIORITY_OVERRIDE`, `DAGB0_SDP_RD_PRIORITY`, `DAGB0_SDP_WR_PRIORITY`, `DAGB0_SDP_RD_CLI2SDP_VC_MAP`, `DAGB0_SDP_WR_CLI2SDP_VC_MAP`, `DAGB0_SDP_ENABLE`, `DAGB0_SDP_CREDITS`, tag reserves, VCC/VCD reserves, `DAGB0_SDP_REQ_CNTL`, `DAGB0_SDP_MISC_AON`, `DAGB0_SDP_MISC`, `DAGB0_SDP_MISC2`, and `DAGB0_SDP_ARB_CNTL0/1`. These fields map traffic classes such as SRT, NRT, DLOCK, HRT, IO, and GMI to SDP VCs; reserve tag/credit pools; tune read/write priority; control request pass/chain/block/align/upsize behavior; and configure link-manager, early write-return, block-request, and read/write arbitration behavior.

Fatal error and sampling fields include:

- `DAGB0_FATAL_ERROR_CLEAR` and `DAGB0_FATAL_ERROR_STATUS0..4`, capturing valid flag, client ID, address low/high, CLI/SDP tags, VF/VFID, unit ID, operation, security level, TMZ, snoop, invalid, NACK, read-only, memory-log, internal/external fatal, priority, chain/full/drop/space/IO/size/reuse-hint shifts.
- `DAGB0_SDP_CGTT_CLK_CTRL`, matching the common clock-gating layout.
- `DAGB0_SDP_LATENCY_SAMPLING`, selecting sampler filters for DRAM, GMI, IO, read, write, atomic-return, atomic-no-return, and VC fields.
- `DAGB0_WRCLI_GPU_SNOOP_OVERRIDE` and `DAGB0_WRCLI_GPU_SNOOP_OVERRIDE_VALUE`, exposing 24-bit write-client snoop override masks.

## Control Flow

This chunk has no runtime control flow. It influences control flow indirectly at compile time: C code names a register field, the preprocessor resolves the matching `__SHIFT` and `_MASK` constants, and AMDGPU register helpers compose or decode the 32-bit MMIO value.

The runtime sequencing is entirely in consuming MMHUB, GMC, VM, reset, clock-gating, debugfs, and diagnostics code. That code is responsible for choosing when to program DAGB traffic limits, when to poll pending/fifo/full/error status, when to clear errors, when to arm or clear performance counters, and how to coordinate these writes with power, reset, and memory-controller state.

## State And Persistence Behavior

The header stores no software state and persists nothing itself. It describes MMIO-backed hardware state in the MMHUB DAGB block. Configuration fields generally persist in hardware until they are reprogrammed, power-gated, reset, or restored after suspend/resume. Status and counter fields are hardware-maintained and may be read-only, sticky, self-clearing, write-one-to-clear, or sequencing-sensitive depending on the register.

Important hardware state represented here includes per-client read/write VC assignment, TLB-credit checking, urgency thresholds, bandwidth windows and reservations, OSD limits, IO/GMI priority overrides, per-client burst and lazy-timer values, read/write VC storage credits, TLB/FIFO/pool credits, pending client masks, SDP enablement and credit reservations, SDP class-to-VC maps, request formatting and alignment behavior, error capture state, fatal error capture state, clock-gating controls, FIFO/credit fullness status, performance counter configuration/results, and latency sampler filters.

Several fields are command-like rather than durable policy, including clear bits, register read/write strobes, performance counter clear/enable controls, fatal error clear, and request-blocking controls. The generated macros do not encode the necessary ordering or polling rules.

## Dependencies And Integration Points

This chunk depends on AMD's generated MMHUB 4.1.0 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_4_1_0_offset.h`, which supplies the `reg...`/`mm...` register offsets for these field names.
- Other generated MMHUB 4.1.0 headers, especially defaults where present, and the SOC15 base-address tables used by AMDGPU register helpers.

Expected consumers are AMDGPU MMHUB/GMC code for ASICs using MMHUB 4.1.0. Integration points include VM hub setup, memory-client QoS setup, clock-gating and light-sleep tuning, reset/suspend/resume restoration, fault/error handling, performance/debug counter access, and SR-IOV or VF-aware diagnostics through fields such as fatal error `VFID` and `VF`.

The immediate naming boundary is important: this chunk covers `DAGB0` almost completely and only begins `DAGB1_RDCLI0`. Code using `DAGB1` fields must rely on later chunks for complete research coverage.

## Risks And Edge Cases

- Bitfield drift is high impact. Wrong masks or shifts can silently write unrelated MMHUB fields, leading to memory-client starvation, bad QoS, VM/TLB credit underflow, hangs, or misleading diagnostics.
- The repeated client families are copy-sensitive. `RDCLI0..23` and `WRCLI0..23` look identical, but a single index, direction, or field-width mismatch can affect only one hardware client and evade broad testing.
- Read and write layouts are similar but not identical. Write-side address/data DAGB and FIFO/atomic credit registers have no exact read-side equivalent.
- Some generated fields in this slice are shift-only or have missing masks in the visible range, such as `ASK2DF` `NUM` fields and selected sparse error/request fields. Consumers should not assume every shift has a local mask pair.
- Status and clear fields are side-effect-sensitive. Pending masks, FIFO fullness, SDP error state, fatal error clear/status, performance counter clear bits, and request blocking must be handled with the hardware-defined read/modify/write and polling semantics.
- Clock-gating overrides can hide real idle/busy state. Misuse of `BUSY_OVERRIDE`, `CGLS_DISABLE`, `LS_DISABLE`, or DAGB busy override fields can break power management, reset quiescing, or low-power entry.
- QoS and credit settings interact. Bandwidth windows, min/max bandwidth, storage credits, TLB credits, tag reserves, VC reserves, and OSD limits need coherent values; isolated changes can throttle traffic or allow queue buildup.
- Fatal error status fields include address, client, VF, operation, security, TMZ, snoop, NACK, and memory-log metadata. Decoding them with stale or mismatched masks can corrupt fault attribution.
- The chunk boundary is artificial. The final `DAGB1_RDCLI0` shifts are incomplete here, so the final merged report must connect this document with the following chunk before making complete file-level claims.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU with MMHUB 4.1.0 support enabled; missing or renamed macros should fail at compile time in MMHUB/GMC users.
- Mechanically compare this header against AMD's authoritative generated register database and verify field widths by checking that each `_MASK` aligns with its matching `__SHIFT`.
- Cross-check `mmhub_4_1_0_sh_mask.h` with `mmhub_4_1_0_offset.h` so every referenced DAGB0 register has both an address and field definitions.
- Exercise GPU VM and memory traffic under graphics, compute, SDMA, display, IO, and peer/GMI load; watch for hangs, VM faults, bandwidth starvation, and unexpected throttling.
- Test suspend/resume, reset, and clock-gating paths that program or restore DAGB, L1TLB, and SDP clock-control fields.
- Validate performance and debug paths by programming DAGB performance counters, reading low/high results, using result-control start/stop triggers, and checking clear/saturation behavior.
- Inject or observe MMHUB fault/error scenarios where possible and verify `DAGB0_SDP_ERR_STATUS`, `DAGB0_FATAL_ERROR_STATUS0..4`, and fatal clear behavior decode to plausible client/address/VF/operation metadata.
- For virtualization-capable configurations, verify that VF/VFID fields in fatal errors and client-specific QoS/status reporting remain correctly attributed.

## Cross-Chunk Notes

Earlier file content does not exist before this chunk. Later chunks continue from `DAGB1_RDCLI0` and should cover the remaining DAGB1 and subsequent MMHUB 4.1.0 shift/mask namespace. The final per-file research document should merge this DAGB0-focused report with later chunks before summarizing the full `mmhub_4_1_0_sh_mask.h` hardware map.

### subset-b-002818: lines 2374-4752

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_4_1_0_sh_mask.h lines 2374-4752

## Scope

This chunk covers a middle section of the generated MMHUB 4.1.0 shift/mask header. It starts inside the `DAGB1_RDCLI0` register definitions, continues through the rest of the `DAGB1` read-side decoder, the `mmhub_pctldec` power-control block, shared MMUTCL2/MMMC aperture registers, and the beginning of the MMVM L2 control/fault block. It ends inside `MMVM_L2_MM_GROUP_RT_CLASSES`, after masks for groups 0 through 26; masks for groups 27 through 31 are outside this chunk.

The file contains preprocessor constants only. There are no C functions, structs, runtime variables, or executable branches in this source range.

## Purpose

`mmhub_4_1_0_sh_mask.h` is a hardware register bitfield contract for AMDGPU's MMHUB 4.1.0 support. Each register field is represented by generated macros of the form:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset of the field.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit field mask.

The paired `mmhub_4_1_0_offset.h` header supplies register offsets such as `regDAGB1_CNTL_MISC2`, `regMMVM_L2_CNTL`, and `regMMVM_L2_PROTECTION_FAULT_STATUS_LO32`; this file supplies field layouts used by `REG_SET_FIELD`, `REG_GET_FIELD`, direct mask checks, and SOC15 MMIO access helpers.

## Important Macro Families

### DAGB1 Read Client and Arbitration Fields

The chunk begins after the first two `DAGB1_RDCLI0` shift macros. The visible part of `DAGB1_RDCLI0`, and the full `DAGB1_RDCLI1` through `DAGB1_RDCLI23` families, define repeated per-read-client policy fields:

- `VIRT_CHAN` selects a virtual channel.
- `CHECK_TLB_CREDIT` gates behavior on TLB credit availability.
- `URG_HIGH` and `URG_LOW` encode urgency thresholds.
- `MAX_BW_ENABLE`/`MAX_BW` and `MIN_BW_ENABLE`/`MIN_BW` encode per-client bandwidth limits or guarantees.
- `OSD_LIMITER_ENABLE` and `MAX_OSD` control outstanding-request limiting.

The `DAGB1_RD_CNTL`, `DAGB1_RD_IO_CNTL`, `DAGB1_RD_GMI_CNTL`, and `DAGB1_RD_ADDR_DAGB` families describe read-side DAGB routing and transaction behavior, including disabled-client bitmaps, IO/GMI virtual-channel enable/map fields, ARB/RETCREDIT forwarding, OSD limiting, address DAGB response behavior, and pipe stall controls.

`DAGB1_RD_ADDR_DAGB_MAX_BURST0/1/2` and `DAGB1_RD_ADDR_DAGB_LAZY_TIMER0/1/2` are packed per-output-DAGB tuning registers. `DAGB1_RD_VC0_CNTL` through `DAGB1_RD_VC5_CNTL`, plus `DAGB1_RD_IO_VC_CNTL` and `DAGB1_RD_GMI_VC_CNTL`, provide virtual-channel enablement and weight fields. `DAGB1_RD_TLB_CREDIT` sets available TLB credit and retry credit values.

`DAGB1_RDCLI_ASK_PENDING`, `GO_PENDING`, `GBLSEND_PENDING`, `TLB_PENDING`, `OARB_PENDING`, `ASK2ARB_PENDING`, `ASK2DF_PENDING`, `OSD_PENDING`, and `ASK_OSD_PENDING` expose read-client pipeline busy state. Several are full-width status bitmaps; `OSD_PENDING` is a single field. `DAGB1_FIFO_EMPTY`, `DAGB1_FIFO_FULL`, and `DAGB1_RD_CREDITS_FULL` expose FIFO and credit saturation signals.

### DAGB1 Error, Clock, Performance, and SDP Fields

`DAGB1_SDP_ERR_STATUS` reports SDMA/SDP error state, including poisoned write, poisoned read-return, bad command, unexpected write-response, and unexpected read-response indicators. It also includes clearing bits for those latched error classes.

`DAGB1_RD_CGTT_CLK_CTRL`, `DAGB1_L1TLB_RD_CGTT_CLK_CTRL`, `DAGB1_SDP_CGTT_CLK_CTRL`, `DAGB1_DAGB_DLY`, `DAGB1_CNTL_MISC`, and `DAGB1_CNTL_MISC2` encode clock-gating, delay, and miscellaneous control. The v4.1.0 driver directly uses `DAGB1_CNTL_MISC2__DISABLE_RDRET_TAP_CHAIN_FGCG_MASK` and `DAGB1_CNTL_MISC2__DISABLE_WRRET_TAP_CHAIN_FGCG_MASK` when toggling medium-grain clock gating.

`DAGB1_PERFCOUNTER0_CFG` through `DAGB1_PERFCOUNTER2_CFG`, `DAGB1_PERFCOUNTER_RSLT_CNTL`, and result low/high fields provide event selection, counter mode, enable/clear strobes, start/stop triggers, any-counter enablement, clear-all, and stop-on-saturate controls.

The SDP-facing families include `DAGB1_SDP_RD_BW_CNTL`, `DAGB1_SDP_PRIORITY_OVERRIDE`, `DAGB1_SDP_RD_PRIORITY`, `DAGB1_SDP_RD_CLI2SDP_VC_MAP`, `DAGB1_SDP_ENABLE`, `DAGB1_SDP_CREDITS`, tag/VCC reserves, `DAGB1_SDP_REQ_CNTL`, `DAGB1_SDP_MISC_AON`, `DAGB1_SDP_MISC`, `DAGB1_SDP_MISC2`, `DAGB1_SDP_ARB_CNTL0/1`, and `DAGB1_SDP_LATENCY_SAMPLING`. These fields govern SDP read bandwidth and priority policy, client-to-VC mapping, enablement, credits, arbitration deadlines, retry/no-OSD handling, and latency sampler configuration.

### PCTL Power-Control Fields

The `mmhub_pctldec` block begins at line 3598. `PCTL_CTRL` packs soft reset, clock mux selection, deep-sleep timers, VDD/GFXOFF qualifiers, XGMI isolation, and service-request controls. `PCTL_MMHUB_DEEPSLEEP_IB`, `PCTL_MMHUB_DEEPSLEEP_OVERRIDE`, `PCTL_MMHUB_DEEPSLEEP_OVERRIDE_IB`, `PCTL_PG_IGNORE_DEEPSLEEP`, and `PCTL_PG_IGNORE_DEEPSLEEP_IB` define per-subblock deep-sleep input, override, and power-gating ignore bitmaps.

`PCTL_UTCL2_MISC`, `PCTL_SLICE0_CFG_DAGB_WRBUSY`, `PCTL_SLICE0_CFG_DAGB_RDBUSY`, `PCTL_SLICE0_CFG_DS_ALLOW`, `PCTL_SLICE0_CFG_DS_ALLOW_IB`, `PCTL_SLICE0_MISC`, and the matching `SLICE1` families describe deep-sleep allow/ignore behavior and slice miscellaneous control. Their repeated packed fields are power-state contracts for UTCL2, DAGB0-4, MMA, MME, MMR, RET, SDP, and VML2-facing logic.

`PCTL_RENG_CTRL` and the `PCTL_*_RENG_*`/`PCTL_*_STCTRL_REGISTER_SAVE_*` families define register-engine execution, RAM index/data access, and register-save ranges/exclusion sets for UTCL2 and slices 0/1. `PCTL_STATUS` reports deep-sleep state and power-controller state for UTCL2 and slices. `PCTL_PERFCOUNTER*` and `PCTL_RESERVED_*` provide power-control performance counter and reserved-register field layouts.

### MMMC and Shared MMUTCL2 Fields

The `mmhub_mmutcl2_mmvmsharedpfdec` block defines address and aperture controls that are programmed during MMHUB GART/system aperture setup:

- `MMMC_VM_NB_MMIOBASE`, `MMMC_VM_NB_MMIOLIMIT`, `MMMC_VM_NB_PCI_CTRL`, `MMMC_VM_NB_PCI_ARB`, `MMMC_VM_NB_TOP_OF_DRAM_SLOT1`, `MMMC_VM_NB_LOWER_TOP_OF_DRAM2`, and `MMMC_VM_NB_UPPER_TOP_OF_DRAM2` describe NB/MMIO/PCI/TOM fields.
- `MMMC_VM_FB_OFFSET`, `MMMC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_LSB/MSB`, and `MMMC_VM_STEERING` define framebuffer offset, default system-aperture page address, and default steering.
- `MMMC_SHARED_VIRT_RESET_REQ` exposes VMC reset request/ack bits.
- `MMMC_VM_CACHEABLE_DRAM_ADDRESS_*`, `MMMC_VM_LOCAL_SYSMEM_ADDRESS_*`, `MMMC_VM_LOCAL_FB_ADDRESS_*`, and `MMMC_VM_LOCAL_FB_ADDRESS_LOCK_CNTL` define cacheable/local address ranges and lock behavior.
- `MMMC_VM_APT_CNTL` encodes aperture translation policy, including direct-system enable, forced uncached memory type, fragment interaction mode, local checks, 2M fragment capping, and local-sysmem aperture policy.
- `MMUTCL2_CGTT_CLK_CTRL`, `MMUTCL2_CGTT_BUSY_CTRL`, `MMUTCL2_HARVEST_BYPASS_GROUPS`, `MMUTCL2_GROUP_RET_FAULT_STATUS`, and `MMMC_SHARED_ACTIVE_FCN_ID` expose shared UTCL2 clock/busy, harvest bypass, group fault, and active function-ID state.

### MMVM L2 Control and Fault Fields

The `mmhub_mmutcl2_mmvml2pfdec` block starts in this chunk and includes:

- `MMVM_L2_CNTL`, with L2 cache enablement, fragment processing, endian swap, default page-out routing, PDE0 tag mode, LRU update, PDE fault classification, identity-access mode, and identity fragment size.
- `MMVM_L2_CNTL2`, with global invalidate controls, per-domain invalidate-disable bits, big-K disable controls, fragment-size disable, VMID passthrough mode, physical address masking, cache invalidation mode, invalidation clock-gating disable, and bank-select reserved CID.
- `MMVM_L2_CNTL3`, with update mode, bank/select, force-miss, cache level, context count, fragment size, cache sharing mode, and cache-size fields.
- `MMVM_L2_CNTL4`, with 4K partition count, physical tap request controls, MM non-real-time and soft-real-time IFIFO active transaction limits, BPM/CG override, foreground clock-gating control, and VFIFO behavior.
- `MMVM_L2_STATUS`, exposing busy flags, context/domain busy flags, and parity-error discovery for PTE and PDE caches.
- `MMVM_DUMMY_PAGE_FAULT_CNTL` and `MMVM_DUMMY_PAGE_FAULT_ADDR_LO32/HI32`, which control and report dummy-page fault behavior.
- `MMVM_INVALIDATE_CNTL`, which provides invalidation mode selection.

The protection-fault families are central to runtime error handling. `MMVM_L2_PROTECTION_FAULT_CNTL` controls clearing/updating the latched fault address, default enables for range/PDE/translation/NACK/dummy/valid/read/write/execute fault classes, per-client no-retry interrupt masks, other-client interrupt behavior, and crash-on-fault bits. `MMVM_L2_PROTECTION_FAULT_CNTL2` adds retry-fault interrupt and active-page-migration PTE behavior. `MMVM_L2_PROTECTION_FAULT_MM_CNTL3/4` expose VML1 read/write no-retry interrupt masks.

`MMVM_L2_PROTECTION_FAULT_STATUS_LO32` decodes latched fault details: more faults, walker error, permission fault bitmap, mapping error, client ID, read/write direction, atomic, VMID, VF flag, VFID, PRT, and uncorrectable-error state. `MMVM_L2_PROTECTION_FAULT_STATUS_HI32` provides `FED`. The fault address/default address and identity aperture families split logical or physical page numbers across low 32-bit and high 4-bit fields.

`MMVM_L2_MM_GROUP_RT_CLASSES` begins at the end of this chunk. It maps groups 0 through 31 to one-bit real-time class fields, but only masks through group 26 are visible here.

## Control Flow

There is no local control flow in the header. Runtime sequencing is in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v4_1_0.c`, which includes both `mmhub_4_1_0_offset.h` and this shift/mask header.

The main v4.1.0 flows using fields from this chunk are:

- `mmhub_v4_1_0_init_system_aperture_regs()` programs system aperture/default-page registers and writes `MMVM_L2_PROTECTION_FAULT_DEFAULT_ADDR_LO32/HI32`; it also enables `MMVM_L2_PROTECTION_FAULT_CNTL2.ACTIVE_PAGE_MIGRATION_PTE_READ_RETRY`.
- `mmhub_v4_1_0_init_cache_regs()` programs `MMVM_L2_CNTL`, `MMVM_L2_CNTL2`, `MMVM_L2_CNTL3`, `MMVM_L2_CNTL4`, and `MMVM_L2_CNTL5` during GART enablement. This chunk supplies the masks for the first four of those registers.
- `mmhub_v4_1_0_disable_identity_aperture()` writes the identity aperture low/high and physical offset registers, using the register offsets paired with the field definitions in this chunk.
- `mmhub_v4_1_0_print_l2_protection_fault_status()` decodes `MMVM_L2_PROTECTION_FAULT_STATUS_LO32` with `REG_GET_FIELD` to print CID, RW, more-faults, walker-error, permission, and mapping-error diagnostics.
- `mmhub_v4_1_0_set_fault_enable_default()` writes `MMVM_L2_PROTECTION_FAULT_CNTL` default fault-enable bits and crash-on-fault bits depending on the requested fault policy.
- `mmhub_v4_1_0_update_medium_grain_clock_gating()` toggles `DAGB1_CNTL_MISC2` tap-chain clock-gating disable masks along with the matching DAGB0 register.

Most other fields in this chunk are passive until used by initialization, debug, clock/power management, profiling, or bring-up code.

## State and Persistence Behavior

The header persists no software state. It names hardware state held in MMIO registers:

- DAGB1 read-client, virtual-channel, bandwidth, SDP, and clock-gating registers persist read fabric policy until reset or reprogramming.
- DAGB1 pending/FIFO/credit/error registers expose transient or latched hardware state; error clear bits are command-style fields.
- Performance-counter registers retain event selection, mode, enable state, and accumulated results until cleared, saturated, reset, or reprogrammed.
- PCTL deep-sleep, override, register-engine, and save-range registers persist low-power policy and save/restore configuration across the relevant power-control flows.
- MMMC aperture and default-page registers persist address-translation windows used by MMHUB memory accesses.
- MMVM L2 control registers persist cache/TLB and invalidation policy; `MMVM_L2_CNTL2` invalidation bits are command-like controls.
- Protection-fault status/address registers latch fault information until cleared or updated according to `MMVM_L2_PROTECTION_FAULT_CNTL`; the default address registers persist fallback page locations.

SR-IOV matters for persistence and ownership. The v4.1.0 driver skips several system-aperture, cache, identity-aperture, and fault-default writes when running as a VF because those registers are host/PF-owned.

## Dependencies and Integration Points

The direct integration point is AMDGPU MMHUB 4.1.0 support:

- `amdgpu/mmhub_v4_1_0.c` includes this header and uses its field names through `REG_SET_FIELD`, `REG_GET_FIELD`, and direct mask operations.
- `mmhub_4_1_0_offset.h` supplies the `reg*` MMIO offsets. These shift/mask macros are not independently sufficient for register access.
- `soc15_common.h` and the SOC15 access helpers provide `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`.
- Common VM hub code consumes fields initialized by `mmhub_v4_1_0_init()`, including protection-fault status/control offsets and invalidation engine spacing.
- Power-management integration reaches this chunk through `mmhub_v4_1_0_set_clockgating()`, which updates DAGB0/DAGB1 clock-gating masks.
- Diagnostic integration reaches the protection-fault status fields through `amdgpu_mmhub_client_name()` and the `mmhub_client_ids_v4_1_0` CID table.

Because this is a generated hardware definition, updates should come from the AMD register-generation source rather than manual edits to individual masks.

## Risks and Edge Cases

- The chunk starts mid-register. `DAGB1_RDCLI0__VIRT_CHAN__SHIFT` and `CHECK_TLB_CREDIT__SHIFT` are in the preceding chunk, while the remaining `DAGB1_RDCLI0` shifts and all masks are here.
- The chunk ends mid-register. `MMVM_L2_MM_GROUP_RT_CLASSES` masks for groups 27 through 31 are outside this range, so a final merged report must join the next chunk before claiming complete coverage of that register.
- Repeated register families are copy-sensitive. A single incorrect client number in `DAGB1_RDCLI[0-23]`, virtual-channel, pending, or SDP macros could affect one client path while leaving most traffic apparently healthy.
- Field drift in `MMVM_L2_CNTL*` can cause severe GPUVM failures: stale translations, missed invalidations, incorrect default-page routing, bad cache sizing, or page-table walker behavior changes.
- Protection-fault field errors affect both fault policy and diagnostics. Incorrect clear/update bits may hide the first faulting address; incorrect CID/RW masks can misattribute a bad client; incorrect crash-on-fault bits can change recovery behavior.
- `CLIENT_ID_NO_RETRY_FAULT_INTERRUPT` is a wide packed mask and `MMVM_L2_PROTECTION_FAULT_STATUS_LO32.CID` spans bits 9-17. Callers must not assume small client IDs or a single-client-only fault source.
- Several fields are strobe or command style (`CLEAR`, error clear, invalidate, register-engine execute). Treating them as durable settings can clear evidence or trigger hardware work unexpectedly.
- PCTL deep-sleep and register-save fields affect low-power transitions. Bad masks can produce suspend/resume instability that may not appear under normal runtime VM tests.
- Reserved fields such as `PCTL_RESERVED_*` dummy fields should not be repurposed without hardware documentation.

## Test Signals

Useful validation signals for this chunk are hardware-facing and integration-oriented:

- Build coverage of `amdgpu/mmhub_v4_1_0.c` verifies that all `REG_SET_FIELD`/`REG_GET_FIELD` references to `MMVM_L2_CNTL*`, `MMVM_L2_PROTECTION_FAULT_*`, and `DAGB1_CNTL_MISC2` still match generated macro names.
- MMHUB v4.1.0 GART enablement should complete `mmhub_v4_1_0_gart_enable()` without VM faults: aperture setup, TLB setup, L2 cache setup, identity aperture disable, VMID configuration, and invalidation range programming should all succeed.
- GPUVM stress tests that allocate, evict, update page tables, and invalidate VMIDs should not show stale translations or hangs in invalidation wait paths.
- Negative-access or fault-injection tests should produce meaningful `MMVM_L2_PROTECTION_FAULT_STATUS_LO32` logs, including CID, RW, walker error, permission, mapping, and more-faults decoding.
- Toggling fault-default policy through AMDGPU fault handling should show the expected change between default-page routing and crash/no-retry behavior.
- Clock-gating tests on supported hardware should exercise `mmhub_v4_1_0_set_clockgating()` and confirm DAGB1 remains functional with `DAGB1_CNTL_MISC2` read/write return tap-chain FGCG masks enabled and disabled.
- Suspend/resume or runtime power-management tests should watch PCTL status and deep-sleep behavior for hangs, register-save failures, or lost MMHUB aperture/cache configuration.
- Debug/profiling coverage can validate DAGB1 and PCTL performance-counter selection, clear, enable, saturation, and result-read behavior.

### subset-b-002819: lines 4753-6943

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_4_1_0_sh_mask.h lines 4753-6943

## Scope

This chunk is the final section of the generated MMHUB 4.1.0 shift/mask header. It starts at the tail of the `MMVM_L2_MM_GROUP_RT_CLASSES` field masks and continues through the closing `#endif` for `_mmhub_4_1_0_SH_MASK_HEADER`.

The covered register families span:

- L2 bank/client selection, cache parity, clock-gating, GCR, PTE-cache dump, bank-select masks, and credit-safety controls.
- MMHUB MC/UTCL2 L2 performance counter result and configuration registers.
- Shared memory aperture and L1 TLB controls for framebuffer, AGP, system aperture, and L1 TLB policy.
- VM context control registers for contexts 0 through 15.
- Context disable masks.
- VM invalidation request, acknowledgement, and logical page address range fields for engines 0 through 17.
- Per-context page-table base, page-table start, and page-table end address fields.
- Per-PF/VF PTE-cache fragment-size registers for the global setting and contexts 0 through 15.
- PSP/IOMMU-facing translation bypass, GPU-host translation, GPUVA VMID assist, IOMMU enable, default translation-fault address, and VSCH power-status fields.

The file is a generated hardware register bitfield map. This chunk defines preprocessor constants only; it has no C functions, structs, enums, runtime variables, or executable branches.

## Purpose

`mmhub_4_1_0_sh_mask.h` supplies the bit-level ABI used by AMDGPU MMHUB 4.1.0 code to compose and decode 32-bit MMIO register values. Each field normally appears as:

- `<REGISTER>__<FIELD>__SHIFT`, the starting bit position.
- `<REGISTER>__<FIELD>_MASK`, the field mask in the register word.

The paired `mmhub_4_1_0_offset.h` header provides register addresses such as `regMMVM_CONTEXT0_CNTL`, `regMMVM_INVALIDATE_ENG0_REQ`, and `regMMMC_VM_FB_LOCATION_BASE`. This header supplies the field layout used by helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()`.

The direct runtime consumer in this source tree is `amdgpu/mmhub_v4_1_0.c`, which includes both the offset and mask headers and uses the fields in MMHUB GART enablement, VMID setup, TLB/cache programming, invalidation request construction, fault handling setup, and framebuffer-base discovery.

## Important Macro Families

### L2 Cache, Bank, Credit, and Diagnostics Controls

The chunk begins with the final `MMVM_L2_MM_GROUP_RT_CLASSES` masks for groups 27 through 31, then defines `MMVM_L2_BANK_SELECT_RESERVED_CID` and `MMVM_L2_BANK_SELECT_RESERVED_CID2`. These reserved-client-ID registers encode read/write client IDs, an enable bit, invalidation mode, private invalidation, and cache fragment-size controls. `mmhub_v4_1_0_init()` records `regMMVM_L2_BANK_SELECT_RESERVED_CID2` in `hub->vm_l2_bank_select_reserved_cid2`, making this register available to common VM/MMHUB code.

`MMVM_L2_CACHE_PARITY_CNTL` exposes parity-check enable bits for 4K PTE, big-page PTE, and PDE caches plus force-parity-mismatch controls. It also selects a target cache bank, cache number, and associativity way for parity injection or diagnostics.

`MMVM_L2_CGTT_CLK_CTRL` and `MMVM_L2_CGTT_BUSY_CTRL` describe clock gating and light-sleep timing controls: on delay, off hysteresis, LS assert hysteresis, minimum MGLS, CGLS/LS disable bits, busy override, read delay, and always-busy. The main v4.1.0 C file currently gates MMHUB through DAGB registers rather than these fields, but the masks remain part of the generated hardware surface.

`MMVM_L2_CNTL5` is actively used by `mmhub_v4_1_0_init_cache_regs()`. The driver starts from `regMMVM_L2_CNTL5_DEFAULT`, then sets `L2_CACHE_SMALLK_FRAGMENT_SIZE` with `REG_SET_FIELD()`. The register also includes walker priority client ID, PDE fetch no-allocate/MTYPE controls, fine-grain clock-gating overrides for MM client return and UTCL2 ATC request paths, and `UTCL2_ONE_OUTSTANDING_ATC_INVREQ`.

`MMVM_L2_GCR_CNTL` exposes GCR enable and GCR client ID. `MMVM_L2_PTE_CACHE_DUMP_CNTL` and `MMVM_L2_PTE_CACHE_DUMP_READ` provide a diagnostic path to select bank/cache/assoc/index and read PTE-cache dump data after a ready indication. `MMVM_L2_BANK_SELECT_MASKS` splits four 4-bit bank-select masks in a single register.

Credit-safety registers (`MMUTCL2_CREDIT_SAFETY_GROUP_RET_CDC`, `MMUTCL2_CREDIT_SAFETY_GROUP_CLIENTS_INVREQ_CDC`, `MMUTCL2_CREDIT_SAFETY_GROUP_CLIENTS_INVREQ_NOCDC`, `MMVML2_CREDIT_SAFETY_IH_FAULT_INTERRUPT`, and `MMVML2_WALKER_CREDIT_SAFETY_FETCH_RDREQ`) share a 10-bit `CREDITS` field and an `UPDATE` bit. These tune or report credit limits for UTCL2/MMVML2 return, invalidation request, interrupt, and walker-fetch paths.

### Performance Counter Registers

The `mmhub_mmutcl2_mmvml2prdec` block defines result registers for MC VM L2 and UTCL2 counters:

- `MMMC_VM_L2_PERFCOUNTER_LO` and `MMUTCL2_PERFCOUNTER_LO` expose full 32-bit low counter words.
- `MMMC_VM_L2_PERFCOUNTER_HI` and `MMUTCL2_PERFCOUNTER_HI` split bits 0-15 as `COUNTER_HI` and bits 16-31 as `COMPARE_VALUE`.

The `mmhub_mmutcl2_mmvml2pldec` block defines configuration for `MMMC_VM_L2_PERFCOUNTER0_CFG` through `MMMC_VM_L2_PERFCOUNTER7_CFG` and `MMUTCL2_PERFCOUNTER0_CFG` through `MMUTCL2_PERFCOUNTER3_CFG`. Each config register uses the same layout: `PERF_SEL` in bits 0-7, `PERF_SEL_END` in bits 8-15, `PERF_MODE` in bits 24-27, `ENABLE` at bit 28, and `CLEAR` at bit 29.

`MMMC_VM_L2_PERFCOUNTER_RSLT_CNTL` and `MMUTCL2_PERFCOUNTER_RSLT_CNTL` select a counter and define start/stop trigger fields, `ENABLE_ANY`, `CLEAR_ALL`, and `STOP_ALL_ON_SATURATE`. These are passive definitions unless a profiling or bring-up path programs the MMIO registers.

### Shared Aperture and L1 TLB Controls

The `mmhub_mmutcl2_mmvmsharedvcdec` block covers address-window and L1 TLB policy fields:

- `MMMC_VM_FB_LOCATION_BASE` and `MMMC_VM_FB_LOCATION_TOP` encode framebuffer base/top values. `mmhub_v4_1_0_get_fb_location()` reads `regMMMC_VM_FB_LOCATION_BASE`, applies `MMMC_VM_FB_LOCATION_BASE__FB_BASE_MASK`, then shifts by 24 bits.
- `MMMC_VM_AGP_TOP`, `MMMC_VM_AGP_BOT`, and `MMMC_VM_AGP_BASE` encode AGP aperture bounds. `mmhub_v4_1_0_init_system_aperture_regs()` writes these from `adev->gmc.agp_*` unless running as an SR-IOV VF.
- `MMMC_VM_SYSTEM_APERTURE_LOW_ADDR` and `MMMC_VM_SYSTEM_APERTURE_HIGH_ADDR` encode logical system aperture bounds. The driver writes these from the min/max of framebuffer and AGP ranges.
- `MMMC_VM_MX_L1_TLB_CNTL` controls L1 TLB enablement, system access mode, unmapped system-aperture behavior, advanced driver model, ECO bits, and memory type. `mmhub_v4_1_0_init_tlb_regs()` enables the L1 TLB, sets system access mode to 3, enables advanced driver model, disables unmapped system-aperture access, clears ECO bits, and sets `MTYPE_UC`. `mmhub_v4_1_0_gart_disable()` later clears `ENABLE_L1_TLB` and `ENABLE_ADVANCED_DRIVER_MODEL`.

### VM Context Controls

The `mmhub_mmutcl2_mmvml2vcdec` block defines `MMVM_CONTEXT0_CNTL` through `MMVM_CONTEXT15_CNTL`. All 16 contexts share the same field layout:

- `ENABLE_CONTEXT`
- `PAGE_TABLE_DEPTH`
- `PAGE_TABLE_BLOCK_SIZE`
- `RETRY_PERMISSION_OR_INVALID_PAGE_FAULT`
- `RETRY_OTHER_FAULT`
- interrupt/default handling bits for range, dummy-page, PDE0, valid, read, write, execute, and secure protection faults

`mmhub_v4_1_0_enable_system_domain()` programs context 0 with context enablement, depth 0, and no retry on permission/invalid-page faults. `mmhub_v4_1_0_setup_vmid_config()` programs contexts 1 through 15 by writing from `regMMVM_CONTEXT1_CNTL` with `hub->ctx_distance`; it enables the contexts, sets page-table depth from `adev->vm_manager.num_level`, sets default fault handling for multiple fault classes, derives `PAGE_TABLE_BLOCK_SIZE` from `adev->vm_manager.block_size - 9`, and sets retry behavior from `amdgpu_noretry`.

`MMVM_CONTEXTS_DISABLE` exposes one disable bit per context. `mmhub_v4_1_0_init()` stores its register address in `hub->vm_contexts_disable` for use by common MMHUB/VM paths.

### Invalidation Engines

The chunk defines invalidation request registers for engines 0 through 17. Every `MMVM_INVALIDATE_ENGn_REQ` register has the same layout:

- `PER_VMID_INVALIDATE_REQ` in bits 0-15.
- `FLUSH_TYPE` in bits 16-18.
- `INVALIDATE_L2_PTES`, `INVALIDATE_L2_PDE0`, `INVALIDATE_L2_PDE1`, `INVALIDATE_L2_PDE2`, and `INVALIDATE_L1_PTES` in bits 19-23.
- `CLEAR_PROTECTION_FAULT_STATUS_ADDR`, `LOG_REQUEST`, and `INVALIDATE_4K_PAGES_ONLY` in bits 24-26.

`mmhub_v4_1_0_get_invalidate_req()` constructs an engine-0 request by setting one VMID bit, forcing legacy flush type 0, invalidating L2 PTEs/PDE0/PDE1/PDE2 and L1 PTEs, and leaving protection-fault-status address clear disabled. The common VM code can apply the resulting layout to other engines because `mmhub_v4_1_0_init()` records `hub->eng_distance` from engine 1 minus engine 0.

Each `MMVM_INVALIDATE_ENGn_ACK` register exposes `PER_VMID_INVALIDATE_ACK` in bits 0-15 and `SEMAPHORE` at bit 16. `mmhub_v4_1_0_init()` records the engine-0 semaphore, request, and acknowledgement addresses in `struct amdgpu_vmhub`.

Each engine also has `ADDR_RANGE_LO32` and `ADDR_RANGE_HI32` field definitions. The low register has `S_BIT` at bit 0 and `LOGI_PAGE_ADDR_RANGE_LO31` in bits 1-31; the high register has `LOGI_PAGE_ADDR_RANGE_HI5` in bits 0-4. `mmhub_v4_1_0_program_invalidation()` initializes all 18 engines to a full logical page range by writing low `0xffffffff` and high `0x1f` using `hub->eng_addr_distance`.

### Page Table Base and Range Registers

The chunk defines per-context page-table base address fields for contexts 0 through 15. Each context has:

- `MMVM_CONTEXTn_PAGE_TABLE_BASE_ADDR_LO32__PAGE_DIRECTORY_ENTRY_LO32`
- `MMVM_CONTEXTn_PAGE_TABLE_BASE_ADDR_HI32__PAGE_DIRECTORY_ENTRY_HI32`

`mmhub_v4_1_0_setup_vm_pt_regs()` writes these for a selected VMID using `hub->ctx_addr_distance`, splitting a 64-bit page-table base into low and high 32-bit words. `mmhub_v4_1_0_init_gart_aperture_regs()` uses it for VMID 0 and the GART page table base.

The chunk also defines per-context page-table start and end registers. Each low register exposes a full 32-bit logical page number low field. Each high register exposes a 4-bit high logical page number field. The driver writes context 0 start/end from `adev->gmc.gart_start` and `adev->gmc.gart_end`; for contexts 1 through 15 it programs start to 0 and end to `adev->vm_manager.max_pfn - 1`.

### Per-PF/VF PTE Cache Fragment Sizes

`MMVM_L2_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` and `MMVM_L2_CONTEXT0_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` through `MMVM_L2_CONTEXT15_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` share three fields: `L2_CACHE_SMALLK_FRAGMENT_SIZE`, `L2_CACHE_BIGK_FRAGMENT_SIZE`, and `BANK_SELECT`. These masks allow global and per-context/PF/VF tuning of L2 PTE cache fragment sizing and bank selection.

The v4.1.0 C file does not directly program these per-PF/VF registers in the checked source, but the global L2 cache code does program related fragment-size and bank-select fields in `MMVM_L2_CNTL3` and `MMVM_L2_CNTL5`.

### PSP/IOMMU and Translation Controls

The `mmhub_mmutcl2_mmvml2pspdec` block exposes security/translation control registers:

- `MMUTCL2_TRANSLATION_BYPASS_BY_VMID` has 16-bit masks for translation-bypass VMIDs and GPA-mode VMIDs.
- `MMVM_IOMMU_GPU_HOST_TRANSLATION_ENABLE` has a single GPU-host translation enable bit.
- `MMUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL` has a single assist enable bit.
- `MMVM_IOMMU_CONTROL_REGISTER` exposes the `IOMMUEN` bit.
- `MMVM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER` exposes `PERFOPTEN`.
- `MMUTC_TRANSLATION_FAULT_CNTL0` and `MMUTC_TRANSLATION_FAULT_CNTL1` define a default physical page address and IO/SPA/snoop attributes used on translation fault handling paths.
- `MMUTCL2_VSCH_POWER_STATUS` exposes a `POWERED_DOWN` status bit.

These definitions are not directly referenced by `mmhub_v4_1_0.c` in the checked source, but they define the MMHUB 4.1.0 register ABI for PSP/IOMMU/translation bring-up or diagnostics.

## Control Flow

There is no local control flow in this header. Runtime sequencing is in `amdgpu/mmhub_v4_1_0.c`:

1. `mmhub_v4_1_0_init()` records key register addresses and register spacing values in `adev->vmhub[AMDGPU_MMHUB0(0)]`, including context base, invalidate engine base, fault status/control, context-disable, and bank-select-reserved-CID2 registers.
2. `mmhub_v4_1_0_gart_enable()` calls setup routines in order: GART aperture, system aperture, L1 TLB, L2 cache, system domain, identity aperture disablement, VMID context configuration, and invalidation engine range programming.
3. `mmhub_v4_1_0_get_invalidate_req()` composes a request word using the `MMVM_INVALIDATE_ENG0_REQ` field definitions. Common VM invalidation code then uses the recorded engine register addresses/distances and acknowledgement masks to drive hardware invalidation.
4. `mmhub_v4_1_0_gart_disable()` disables context registers, clears L1 TLB advanced-driver state, and disables L2 cache.
5. Fault-default behavior is controlled separately by `mmhub_v4_1_0_set_fault_enable_default()`, using protection-fault masks defined earlier in the same header, while this chunk supplies the per-context fault enable/default bits used in VMID setup.

## State and Persistence Behavior

The header itself persists no state. The state described by these macros resides in MMHUB hardware registers:

- Context control, page-table base, start, and end registers persist the active VMID translation configuration until reprogrammed or reset.
- Invalidation request registers are command-style MMIO surfaces. A write triggers invalidation for the selected VMID mask and cache/TLB scope. Acknowledgement registers expose completion state per VMID and semaphore state.
- Invalidation address-range registers persist per-engine logical-page range configuration. The driver initializes all 18 engines to the full range during GART enablement.
- L1 TLB, L2 cache, fragment-size, bank-select, GCR, and clock-gating registers persist hardware policy and performance/power settings.
- Performance counter config and result-control registers persist profiling setup. Counter result registers expose accumulated hardware counter state and compare values.
- Credit-safety registers persist credit limits or update state for UTCL2/MMVML2 paths.
- Translation bypass, IOMMU enable, GPU-host translation, translation fault default, and VSCH power status represent security/translation hardware state outside normal per-VM page-table setup.

Several fields are strobe or command-like rather than durable policy bits: invalidation request bits start hardware work, performance-counter `CLEAR` and `CLEAR_ALL` clear counters, credit-safety `UPDATE` commits credit changes, and cache dump `ENABLE` initiates a diagnostic read sequence.

## Dependencies and Integration Points

This chunk depends on the AMDGPU register access and generated-register infrastructure:

- `amdgpu/mmhub_v4_1_0.c` includes `mmhub/mmhub_4_1_0_offset.h` and `mmhub/mmhub_4_1_0_sh_mask.h`.
- `mmhub_4_1_0_offset.h` supplies register addresses; this file supplies fields. Either header alone is incomplete for MMIO programming.
- `REG_SET_FIELD()` and `REG_GET_FIELD()` depend on the exact `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming convention.
- `RREG32_SOC15()`, `WREG32_SOC15()`, `WREG32_SOC15_OFFSET()`, and `SOC15_REG_OFFSET()` perform the actual MMHUB instance register reads/writes.
- `struct amdgpu_vmhub` stores base addresses and spacing for contexts and invalidation engines so common VM code can operate on repeated register arrays without hard-coding every context or engine register name.
- Higher-level state comes from `struct amdgpu_device`: `adev->gmc` aperture bounds, GART object page directory address, dummy/default pages, `adev->vm_manager` page-table geometry, SR-IOV VF status, and clock-gating feature flags.

The file is source-tree-aligned with the Linux AMDGPU generated ASIC register headers under `drivers/gpu/drm/amd/include/asic_reg/mmhub`. Hardware definition changes should be regenerated from AMD register descriptions rather than hand-edited.

## Risks and Edge Cases

- The chunk starts mid-family at `MMVM_L2_MM_GROUP_RT_CLASSES` masks. The merged per-file report should combine this with earlier chunk content before treating that register as complete.
- Field layout drift is high risk. Incorrect masks or shifts can silently produce wrong MMIO values via `REG_SET_FIELD()`, causing stale translations, missing invalidation acknowledgements, incorrect page-table bounds, or VM fault storms.
- MMHUB 4.1.0 has 18 invalidation engines in the driver loop. If a future ASIC changes engine count, spacing, or field layout, both generated headers and `mmhub_v4_1_0_program_invalidation()` assumptions need review.
- `PER_VMID_INVALIDATE_REQ` and `PER_VMID_INVALIDATE_ACK` are 16-bit fields. Callers must not shift a VMID outside the supported bit range.
- Context control fields are repeated across contexts 0 through 15, but the driver treats context 0 as the system/GART domain and contexts 1 through 15 as VMID contexts. Applying context-1 policy blindly to context 0 would change system-domain behavior.
- Page-table start/end high registers expose only four high bits in this chunk. Address calculations must match the driver shifts (`>> 12`, `>> 44`) and the hardware page-number width.
- `MMMC_VM_L2_PERFCOUNTER_HI` and `MMUTCL2_PERFCOUNTER_HI` are split between `COUNTER_HI` and `COMPARE_VALUE`; treating the high register as an unqualified 32-bit high counter word would corrupt profiling interpretation.
- SR-IOV VF mode intentionally skips several system aperture and cache registers because the PF programs them. New callers should preserve that access boundary.
- Reserved-client-ID, parity-injection, PTE-cache dump, credit-safety, translation bypass, IOMMU, and default translation-fault fields affect low-level memory translation behavior. Misprogramming can produce security isolation issues, data corruption, hangs, or hard-to-debug VM faults.
- Command bits such as invalidation request, performance-counter clear, and credit update require hardware sequencing and timeout handling in the consumer; the generated masks do not encode ordering guarantees.

## Test Signals

Useful validation signals are integration and hardware-facing:

- Build coverage for `amdgpu/mmhub_v4_1_0.c` confirms that `REG_SET_FIELD()` and `REG_GET_FIELD()` references still match generated mask names.
- GART enablement on MMHUB 4.1.0 hardware should successfully program aperture, L1 TLB, L2 cache, context, and invalidation-range registers without register access faults.
- GPUVM stress tests should complete TLB/cache invalidations with matching per-VMID acknowledgement bits and no timeout in VM flush paths.
- VM fault tests should report expected client IDs and fault classes, and toggling fault-default policy should redirect or interrupt faults according to driver settings.
- SR-IOV VF tests should verify that skipped PF-owned system aperture/cache registers are not accessed by the guest path.
- Suspend/resume and GPU reset tests should re-run GART/MMHUB initialization and restore context/page-table/invalidation state.
- Performance-counter diagnostics should validate the split low/high/compare register interpretation and the `ENABLE`, `CLEAR`, `CLEAR_ALL`, and saturation behavior.
- IOMMU/translation-bypass bring-up should verify VMID bypass/GPA bits, GPU-host translation enablement, default translation fault address, and VSCH power status against hardware documentation.
