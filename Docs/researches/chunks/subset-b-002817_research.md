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
