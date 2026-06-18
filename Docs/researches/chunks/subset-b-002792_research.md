# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_3_0_sh_mask.h lines 1-2339

## Scope

This chunk covers the beginning of the generated AMDGPU MMHUB 2.3.0 shift/mask header. The range starts with the license and include guard, then enters `addressBlock: mmhub_dagbdec` and defines the first large `DAGB0` address-generation/buffer decoder register-field map through the beginning of `DAGB0_WR_TLB_CREDIT`.

The covered register families are:

- `DAGB0_RDCLI0` through `DAGB0_RDCLI30`, each exposing the same read-client fields for virtual-channel selection, TLB-credit checking, urgency thresholds, max/min bandwidth, and outstanding-request limiting.
- `DAGB0_RD_CNTL`, `DAGB0_RD_GMI_CNTL`, `DAGB0_RD_ADDR_DAGB`, output burst/timer registers, and read-path CGTT clock-control registers.
- `DAGB0_RD_ADDR_DAGB_MAX_BURST*` and `DAGB0_RD_ADDR_DAGB_LAZY_TIMER*`, which pack four-bit settings for clients 0 through 31.
- `DAGB0_RD_VC0_CNTL` through `DAGB0_RD_VC7_CNTL`, read-path pool/EA credits and per-VC bandwidth/outstanding controls.
- `DAGB0_RD_CNTL_MISC`, `DAGB0_RD_TLB_CREDIT`, read-return credit controls, and read-client pending status registers.
- `DAGB0_WRCLI0` through `DAGB0_WRCLI30`, matching write-client field layouts.
- `DAGB0_WR_CNTL`, `DAGB0_WR_GMI_CNTL`, `DAGB0_WR_ADDR_DAGB`, write output burst/timer registers, write clock-control registers, write address/data DAGB max-burst and lazy-timer registers, `DAGB0_WR_VC0_CNTL` through `DAGB0_WR_VC7_CNTL`, `DAGB0_WR_CNTL_MISC`, and the first three `DAGB0_WR_TLB_CREDIT` shift definitions at the chunk boundary.

The file is declarative hardware metadata. It contains no normal C functions, structs, variables, allocations, locks, or executable branches. Its public surface is the set of preprocessor macros named as `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`.

## Purpose

`mmhub_2_3_0_sh_mask.h` provides bit-accurate symbolic field locations for MMHUB 2.3.0 registers. This chunk specifically describes the `DAGB0` read and write client arbitration, bandwidth, credit, outstanding request, TLB-credit, clock-gating, and pending-status fields in the MMHUB DAGB decoder block.

The paired generated headers supply the rest of the register contract: `mmhub_2_3_0_offset.h` names register addresses, this `_sh_mask.h` file names fields inside each 32-bit register, and `mmhub_2_3_0_default.h` supplies reset/default values. AMDGPU code then composes register writes with helpers such as `REG_SET_FIELD` and decodes register values with field masks/shifts.

Although this repository path is under a local `ceph-client` source import, the content is Linux AMDGPU DRM hardware register metadata, not Ceph filesystem logic.

## Important APIs, Types, And Macros

There are no C APIs or types in this range. The effective API is the macro namespace consumed by AMDGPU MMHUB and display code.

Important macro groups include:

- `DAGB0_RDCLI*` and `DAGB0_WRCLI*`: per-client policy fields. Each client register packs `VIRT_CHAN`, `CHECK_TLB_CREDIT`, `URG_HIGH`, `URG_LOW`, `MAX_BW_ENABLE`, `MAX_BW`, `MIN_BW_ENABLE`, `MIN_BW`, `OSD_LIMITER_ENABLE`, and `MAX_OSD`. The masks show a common 32-bit layout: low three bits for VC, single-bit enables, four-bit urgency values, bandwidth fields, and high bits for outstanding-depth limits.
- `DAGB0_RD_CNTL` and `DAGB0_WR_CNTL`: global read/write controls for `SCLK_FREQ`, client and VC max-bandwidth windows, IO-level override/selection, IO-level VC compliance, and shared VC count.
- `DAGB0_RD_GMI_CNTL` and `DAGB0_WR_GMI_CNTL`: GMI-facing credit and burst controls, with `EA_CREDIT`, `LEVEL`, `MAX_BURST`, and `LAZY_TIMER`.
- `DAGB0_RD_ADDR_DAGB`, `DAGB0_WR_ADDR_DAGB`, and `DAGB0_WR_DATA_DAGB`: DAGB enable, jump-ahead enable, optional self-init disable, instance identity (`WHOAMI`), and jump mode controls.
- `DAGB0_*_OUTPUT_DAGB_MAX_BURST` and `DAGB0_*_OUTPUT_DAGB_LAZY_TIMER`: eight packed virtual-channel fields (`VC0` through `VC7`) for output burst and lazy timer behavior.
- `DAGB0_*_ADDR_DAGB_MAX_BURST0..3`, `DAGB0_*_ADDR_DAGB_LAZY_TIMER0..3`, and `DAGB0_WR_DATA_DAGB_MAX_BURST0..3` / `DAGB0_WR_DATA_DAGB_LAZY_TIMER0..3`: client-indexed packed controls. Each register packs eight four-bit client fields, so the four registers cover clients 0-31.
- `DAGB0_RD_VC0_CNTL` through `DAGB0_RD_VC7_CNTL` and `DAGB0_WR_VC0_CNTL` through `DAGB0_WR_VC7_CNTL`: per-virtual-channel storage and EA credit fields plus max/min bandwidth and outstanding request limits.
- `DAGB0_RD_CNTL_MISC` and `DAGB0_WR_CNTL_MISC`: pool credits, IO EA credit, cache-coherency legacy mode flags, and client IDs for UTCL2 and HDP.
- `DAGB0_RD_TLB_CREDIT` and the start of `DAGB0_WR_TLB_CREDIT`: packed TLB credit fields (`TLB0`, `TLB1`, `TLB2`, etc.). The write block continues in the next chunk.
- `DAGB0_RD_RDRET_CREDIT_CNTL` and `DAGB0_RD_RDRET_CREDIT_CNTL2`: read-return VC and pool credit controls with `VC_MODE` and `FIX_EQ`.
- `DAGB0_RDCLI_*_PENDING`: pending/busy status words for read clients waiting in ask, go, global-send, TLB, output-arbiter, and outstanding-request paths. Each uses a full 32-bit `BUSY` mask.
- `DAGB0_RD_CGTT_CLK_CTRL`, `DAGB0_L1TLB_RD_CGTT_CLK_CTRL`, `DAGB0_ATCVM_RD_CGTT_CLK_CTRL`, `DAGB0_WR_CGTT_CLK_CTRL`, `DAGB0_L1TLB_WR_CGTT_CLK_CTRL`, and `DAGB0_ATCVM_WR_CGTT_CLK_CTRL`: clock-gating timing and override fields (`ON_DELAY`, `OFF_HYSTERESIS`, soft stall override, light-sleep override, and per-direction/register override bits).

## Control Flow

This chunk has no runtime control flow. It is a compile-time bitfield table.

Runtime sequencing is owned by consumer code:

1. Include the MMHUB 2.3.0 offset, mask, and default headers.
2. Select an MMHUB register offset from `mmhub_2_3_0_offset.h`.
3. Use the `__SHIFT` and `_MASK` macros from this file to compose or decode field values.
4. Read or write the hardware register with AMDGPU/SOC15 MMIO helpers during device initialization, GART setup, VM invalidation setup, clock-gating setup, display resource programming, debug, or error handling.

The direct include sites observed in this tree are `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v2_3.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`. `gmc_v10_0.c` selects `mmhub_v2_3_funcs`, so the mask header participates in MMHUB programming for that GPU memory-controller generation.

## State And Persistence Behavior

The header stores no software state and performs no I/O. It describes MMIO-backed hardware state. When these macros are used by a consumer, the programmed values persist in the GPU's MMHUB registers until reset, power-management transition, firmware/hardware reinitialization, or another driver write changes them.

State represented by this chunk includes:

- Per-client routing and QoS state: virtual-channel mapping, urgency thresholds, max/min bandwidth limits, bandwidth-enable bits, outstanding request limiter enables, and maximum outstanding depth.
- Global read/write policy state: SCLK-related windows, bandwidth-window sizing, IO level override, IO compliance VC, and shared VC count.
- Credit and flow-control state: GMI EA credits, storage/EA pool credits, per-VC storage and EA credits, IO EA credits, TLB credits, read-return VC/pool credits, and fixed/equalization mode.
- DAGB behavior state: DAGB enable masks, jump-ahead behavior, self-init suppression, instance identity, jump mode, output burst limits, client burst limits, and lazy timers.
- Pending/status state: read-client busy bitmaps for ask, go, global send, TLB, output arbitration, and outstanding-request queues.
- Power/clock state: clock-gating on-delay/off-hysteresis, soft-stall override, light-sleep override, and read/write/register/return override bits for read, write, L1TLB, and ATCVM subpaths.
- Cache-coherency/client-ID state: legacy CC mode flags and UTCL2/HDP client identifiers in read/write miscellaneous controls.

The masks do not encode access semantics. A field may be read-only, write-only, sticky, self-clearing, reset-sensitive, or sequencing-sensitive according to the hardware specification. Consumers must treat status-like `PENDING` fields differently from policy fields such as bandwidth limits, credits, and clock overrides.

## Dependencies And Integration Points

This chunk depends on the generated AMDGPU register-header family for MMHUB 2.3.0:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_3_0_offset.h` for register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_3_0_default.h` for reset/default register values.
- AMDGPU field helpers and SOC15 MMIO helpers that combine offsets, masks, shifts, and register base information.

Visible integration points in this tree include:

- `amdgpu/mmhub_v2_3.c`, which includes this header and implements MMHUB 2.3 setup, GART aperture programming, system aperture programming, TLB/cache setup, VMID configuration, invalidation programming, GART enable/disable, fault-default configuration, and clock-gating controls.
- `amdgpu/gmc_v10_0.c`, which selects `mmhub_v2_3_funcs` for matching devices and therefore routes memory-controller initialization through code compiled with these definitions.
- `display/dc/resource/dcn31/dcn31_resource.c`, which includes the same offset and mask headers for DCN 3.1 resource programming that needs MMHUB register definitions.
- Cross-version generated headers such as `mmhub_2_0_0_sh_mask.h` and `mmhub_3_0_1_sh_mask.h`, which expose similar DAGB families but are not interchangeable. Field presence and bit positions must remain matched to the ASIC version.

## Risks And Edge Cases

- Bitfield drift is high impact. A wrong mask or shift can update a neighboring field in the same 32-bit register, changing routing, bandwidth, credits, clock behavior, or status interpretation without a compiler error.
- The file is heavily generated and repetitive. `DAGB0_RDCLI*` and `DAGB0_WRCLI*` are almost identical across 31 clients, as are the eight VC controls and the client-packed burst/timer registers. Copy/generation mistakes may affect a single client, traffic direction, or VC and appear only under a narrow workload.
- Packed client registers are easy to mis-index. The `*_MAX_BURST0..3` and `*_LAZY_TIMER0..3` families each pack eight four-bit clients; consumers or reviewers must distinguish clients 0-7, 8-15, 16-23, and 24-31.
- Read and write blocks look symmetric but should not be blindly treated as equivalent. The write side adds address/data DAGB controls, and the chunk ends before the full `DAGB0_WR_TLB_CREDIT` mask set is visible.
- Clock-control fields can have side effects on power and liveness. Incorrect `SOFT_STALL_OVERRIDE`, light-sleep override, or per-operation override programming can block clock gating, stall traffic, or mask idle behavior.
- Status-like fields such as `DAGB0_RDCLI_*_PENDING__BUSY` are full-width bitmaps. They should be decoded as hardware-reported state, not programmed like normal configuration fields.
- Bandwidth, urgency, credit, and outstanding-depth fields interact. Misprogramming one class of fields can cause starvation, excessive latency, invalid TLB-credit behavior, or memory-hub backpressure.
- This chunk is not the complete file. It starts at the file beginning but stops mid-register at `DAGB0_WR_TLB_CREDIT__TLB2__SHIFT`; later chunks must cover the remaining write TLB-credit masks and all subsequent MMHUB 2.3.0 register families before final file-level conclusions are drawn.

## Test Signals

Useful validation is mostly build-time, generated-header consistency, and hardware behavior:

- Build AMDGPU code paths that include `mmhub_2_3_0_sh_mask.h`, especially `amdgpu/mmhub_v2_3.c` and `display/dc/resource/dcn31/dcn31_resource.c`, to catch missing or renamed generated macros.
- Mechanically compare `mmhub_2_3_0_sh_mask.h` against the authoritative AMD MMHUB 2.3.0 register database and the matching offset/default headers. The important checks in this chunk are packed client fields, per-client RD/WR layouts, per-VC control fields, pending status masks, and TLB/read-return credit fields.
- Use representative `REG_SET_FIELD` / `REG_GET_FIELD` checks for fields such as `DAGB0_RDCLI0__VIRT_CHAN`, `DAGB0_RDCLI0__MAX_BW`, `DAGB0_RD_VC0_CNTL__EA_CREDIT`, `DAGB0_RD_ADDR_DAGB_MAX_BURST3__CLIENT31`, and `DAGB0_WR_CNTL_MISC__HDP_CID`.
- On hardware or simulator, read back MMHUB DAGB registers after initialization and confirm that only intended bits change when programming virtual channels, bandwidth windows, credits, burst limits, lazy timers, and clock-gating controls.
- Exercise mixed read/write GPU memory traffic while watching for hangs, MMHUB backpressure, unexpected latency, or starvation that would suggest bad urgency, bandwidth, credit, or outstanding-depth programming.
- During low-power and clock-gating tests, verify that CGTT delay/override fields do not prevent expected idle transitions or cause traffic stalls.
- For debug/status paths, poll `DAGB0_RDCLI_*_PENDING` registers under load and idle conditions to confirm busy bitmaps match expected queue activity and clear after traffic drains.

## Cross-Chunk Notes

The requested range is the first chunk of a much larger generated header. The next chunk must continue from `DAGB0_WR_TLB_CREDIT` and should reconcile the incomplete write TLB-credit family before describing full write-path credit behavior. The merge lane should also combine this document with later chunks for the complete `mmhub_2_3_0_sh_mask.h` file-level report.
