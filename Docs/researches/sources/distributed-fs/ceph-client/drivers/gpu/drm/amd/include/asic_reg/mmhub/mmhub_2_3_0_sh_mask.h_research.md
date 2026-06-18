# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_3_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002792`: lines 1-2339, `Docs/researches/chunks/subset-b-002792_research.md`
- `subset-b-002793`: lines 2340-4718, `Docs/researches/chunks/subset-b-002793_research.md`
- `subset-b-002794`: lines 4719-7196, `Docs/researches/chunks/subset-b-002794_research.md`
- `subset-b-002795`: lines 7197-9714, `Docs/researches/chunks/subset-b-002795_research.md`
- `subset-b-002796`: lines 9715-10331, `Docs/researches/chunks/subset-b-002796_research.md`

## Chunk Research

### subset-b-002792: lines 1-2339

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

### subset-b-002793: lines 2340-4718

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_3_0_sh_mask.h lines 2340-4718

## Scope

This chunk covers the middle of the generated AMD MMHUB 2.3 register shift/mask header. The range starts inside the `DAGB0_WR_TLB_CREDIT` field definitions, completes a large tail of the `mmhub_dagbdec`/`DAGB0_*` register block, then enters `addressBlock: mmhub_mmea_mmeadec0` and defines most of the `MMEA0_*` memory/E/A decoder register fields through the beginning of `MMEA0_LATENCY_SAMPLING`.

The file is declarative hardware ABI data. It contains no C functions, structs, executable branches, storage, or in-header persistence. Its public surface is the generated set of `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros used by AMDGPU code to compose and decode 32-bit MMIO register values.

Because this is a chunk of a larger generated file, the final per-file research pass should reconcile it with earlier lines for the beginning of `DAGB0_WR_TLB_CREDIT` and with later lines for the rest of `MMEA0_LATENCY_SAMPLING`, performance counters, error status, DSM/error-injection, clock-gating, and any later MMEA instances.

## Purpose

`mmhub_2_3_0_sh_mask.h` supplies bit-accurate field layout for the MMHUB 2.3 hardware block. The sibling `mmhub_2_3_0_offset.h` provides register addresses, `mmhub_2_3_0_default.h` provides reset/default values, and this header provides the masks and shifts that let code update a single field without hard-coding bit positions.

In this chunk, the `DAGB0_*` definitions describe write-side credits, outstanding/pending indications, snoop override controls, virtual-channel remapping, clock-gating disables, FIFO status, and performance-counter controls for the DAGB decoder. The `MMEA0_*` definitions describe the first MMEA decoder instance: DRAM and IO client grouping, group-to-virtual-channel mapping, request accumulation, CAM/page-burst and priority policy, address normalization and DRAM address decoding, channel/bank/chip-select hashing, harvested address ranges, SDP arbitration/credits/reservations, request controls, miscellaneous link/priority behavior, and latency-sampler filters.

Although this repository path sits under a Ceph client source import, this file is Linux AMDGPU DRM hardware register interface data. It is not Ceph filesystem logic.

## Important Macro Families

The macro convention is the API:

- `REGISTER__FIELD__SHIFT` is the least-significant bit position for a field.
- `REGISTER__FIELD_MASK` is the already-positioned 32-bit mask for that field.
- Consumers use these directly or through AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15`.

### DAGB0 write credits, status, and counters

The start of the chunk finishes `DAGB0_WR_TLB_CREDIT`, with six 5-bit TLB credit fields (`TLB0` through `TLB5`). It then defines write data and misc credit controls:

- `DAGB0_WR_DATA_CREDIT` packs deadlock-VC, large-burst, middle-burst, and small-burst credit budgets into byte-sized fields.
- `DAGB0_WR_MISC_CREDIT` covers atomic credits, deadlock VC number, OSD credits, and OSD deadlock credits.
- `DAGB0_WR_OSD_CREDIT_CNTL1/2` expose per-VC, IO, GMI, and pool OSD credits plus credit margin and legacy behavior.
- `DAGB0_WR_DATA_FIFO_CREDIT_CNTL1/2` and `DAGB0_WR_ATOMIC_FIFO_CREDIT_CNTL1` define per-VC FIFO credits, pool credits, VC mode, fixed-equation bits, and per-VC maximum packet lengths.

The pending/status block includes `DAGB0_WRCLI_ASK_PENDING`, `GO_PENDING`, `GBLSEND_PENDING`, `TLB_PENDING`, `OARB_PENDING`, `OSD_PENDING`, `DBUS_ASK_PENDING`, and `DBUS_GO_PENDING`, each exposing a full-width `BUSY` mask. `DAGB0_WRCLI_GPU_SNOOP_OVERRIDE` and `_VALUE` are full-width enable/value fields for snoop override policy.

`DAGB0_DAGB_DLY`, `DAGB0_CNTL_MISC`, and `DAGB0_CNTL_MISC2` cover delay/client/position selection, EA VC0-VC7 remapping, bandwidth initialization/gap cycles, urgency boost/halt, clock-gating disable bits for write/read request/return and TLB paths, EA busy disable bits, byte-swap control, parity check enable, and read-return FIFO credit fields.

The chunk also defines status and performance-counter registers:

- `DAGB0_FIFO_EMPTY`, `DAGB0_FIFO_FULL`, `DAGB0_WR_CREDITS_FULL`, and `DAGB0_RD_CREDITS_FULL` expose packed fullness/emptiness state.
- `DAGB0_PERFCOUNTER_LO/HI` provide counter data and compare value bits.
- `DAGB0_PERFCOUNTER0_CFG`, `1_CFG`, `2_CFG`, and `DAGB0_PERFCOUNTER_RSLT_CNTL` provide event select ranges, mode, enable, clear, counter select, start/stop triggers, enable-any, clear-all, and stop-on-saturate.
- `DAGB0_RESERVE0` through `DAGB0_RESERVE9` are full-width reserved fields.

### MMEA0 DRAM grouping, arbitration, and priority

The `mmhub_mmea_mmeadec0` block begins at line 2627. It first defines DRAM client and priority plumbing:

- `MMEA0_DRAM_RD_CLI2GRP_MAP0/1` and `MMEA0_DRAM_WR_CLI2GRP_MAP0/1` map client IDs `CID0` through `CID31` into 2-bit request groups for read and write traffic.
- `MMEA0_DRAM_RD_GRP2VC_MAP` and `MMEA0_DRAM_WR_GRP2VC_MAP` map four request groups to virtual channels.
- `MMEA0_DRAM_RD_LAZY` and `MMEA0_DRAM_WR_LAZY` encode per-group delay plus request accumulation threshold, timeout, and idle maximum.
- `MMEA0_DRAM_RD_CAM_CNTL` and `MMEA0_DRAM_WR_CAM_CNTL` define CAM allocation mode and per-group allocation fields.
- `MMEA0_DRAM_PAGE_BURST` defines read/write page-hit burst limits.
- `MMEA0_DRAM_RD_PRI_AGE`, `WR_PRI_AGE`, `RD_PRI_QUEUING`, `WR_PRI_QUEUING`, `RD_PRI_FIXED`, `WR_PRI_FIXED`, `RD_PRI_URGENCY`, and `WR_PRI_URGENCY` provide age, queueing, fixed priority, urgency coefficient, and urgency mode fields for the four DRAM request groups.
- `MMEA0_DRAM_RD_PRI_QUANT_PRI1/2/3` and `MMEA0_DRAM_WR_PRI_QUANT_PRI1/2/3` define per-group quantum thresholds.

These fields are QoS and forward-progress controls. They determine how MMEA0 classifies MMHUB clients, assigns them to virtual channels, accumulates requests, arbitrates across groups, and switches priority modes.

### MMEA0 address normalization and DRAM decoding

The address block defines how incoming addresses are normalized and decoded into DRAM topology:

- `MMEA0_ADDRNORM_BASE_ADDR0/1`, `LIMIT_ADDR0/1`, and `OFFSET_ADDR1` describe two address ranges with valid bits, legacy MMIO-hole enable, interleave channel/die/socket parameters, address select, base/limit address, destination fabric ID, and high-address offset behavior.
- `MMEA0_ADDRNORMDRAM_HOLE_CNTL` and `MMEA0_ADDRNORMDRAM_NP2_CHANNEL_CFG` describe DRAM hole validity/offset and non-power-of-two channel space sizing.
- `MMEA0_ADDRDEC_BANK_CFG` and `MMEA0_ADDRDEC_MISC_CFG` define bank, bank-group, pseudo-channel, bank swap, row/column/bank remap, stack, 3DS, and chip-select sizing/stacking fields.
- `MMEA0_ADDRDECDRAM_ADDR_HASH_BANK0` through `BANK5`, `PC`, `PC2`, `CS0`, and `CS1` define hash masks for bank, pseudo-channel, and chip-select selection.
- `MMEA0_ADDRDECDRAM_HARVEST_ENABLE`, `HARVNA_ADDR_START0/END0`, and `HARVNA_ADDR_START1/END1` describe harvested or non-addressable address-range enable and boundaries.

The chunk then defines repeated `ADDRDEC0` and `ADDRDEC1` chip-select programming:

- `BASE_ADDR_CS0..CS3` and `BASE_ADDR_SECCS0..SECCS3` give base address fields for primary and secondary chip selects.
- `ADDR_MASK_*`, `ADDR_CFG_*`, `ADDR_SEL_*`, `ADDR_SEL2_*`, `COL_SEL_LO_*`, `COL_SEL_HI_*`, and `RM_SEL_*` define address masks, config bits, row/column/bank/bank-group/chip-select address bit selection, remap, and column bit selection for paired chip selects (`CS01`, `CS23`, `SECCS01`, `SECCS23`) and later single-chip-select variants (`CS1`, `CS3`, `SECCS1`, `SECCS3`).
- `MMEA0_ADDRNORMDRAM_GLOBAL_CNTL`, `MMEA0_ADDRDECDRAM_GECC_HARV_ADJ0..5`, and `MMEA0_ADDRNORMDRAM_MASKING` complete this chunk's address-normalization side with global control, GECC harvest adjustment masks, and DRAM masking.

This is among the riskiest material in the chunk: a wrong mask or shift can misroute physical memory accesses, disturb interleave behavior, or break harvested-memory/topology handling.

### MMEA0 IO grouping and priority

The IO section mirrors the DRAM grouping model for non-DRAM traffic:

- `MMEA0_IO_RD_CLI2GRP_MAP0/1` and `MMEA0_IO_WR_CLI2GRP_MAP0/1` map client IDs to read/write IO groups.
- `MMEA0_IO_RD_COMBINE_FLUSH` and `MMEA0_IO_WR_COMBINE_FLUSH` control group flush timers and enable bits for request combining.
- `MMEA0_IO_GROUP_BURST` sets read/write group burst limits.
- `MMEA0_IO_RD_PRI_AGE`, `WR_PRI_AGE`, `RD_PRI_QUEUING`, `WR_PRI_QUEUING`, `RD_PRI_FIXED`, `WR_PRI_FIXED`, `RD_PRI_URGENCY`, and `WR_PRI_URGENCY` define the same age/queue/fixed/urgency policy fields for IO traffic.
- `MMEA0_IO_RD_PRI_URGENCY_MASKING` and `MMEA0_IO_WR_PRI_URGENCY_MASKING` provide one-bit urgency masks for client IDs `CID0` through `CID31`.
- `MMEA0_IO_RD_PRI_QUANT_PRI1/2/3` and `MMEA0_IO_WR_PRI_QUANT_PRI1/2/3` provide per-group quantum threshold fields.

The IO urgency-masking registers are full, densely packed 32-bit client masks. Callers must preserve all unrelated clients when changing one client bit.

### MMEA0 SDP arbitration, credits, request control, and sampling

The tail of this chunk defines shared data path controls:

- `MMEA0_SDP_ARB_DRAM` controls DRAM read/write burst limit cycles/data, early switch-to-read/write on priority or reservation, end-of-burst-on-expire, and decoupled read/write bank state.
- `MMEA0_SDP_ARB_FINAL` controls final DRAM/GMI/IO burst limits, burst multiplier, read-only flags for VC0-VC7, error-event and halt-request on error, GMI burst stretch, and DRAM/GMI read/write throttles.
- `MMEA0_SDP_DRAM_PRIORITY` and `MMEA0_SDP_IO_PRIORITY` define read/write priority values for groups 0-3.
- `MMEA0_SDP_CREDITS` defines tag, write-response, and read-response credits.
- `MMEA0_SDP_TAG_RESERVE0/1`, `MMEA0_SDP_VCC_RESERVE0/1`, and `MMEA0_SDP_VCD_RESERVE0/1` define per-VC tag and credit reservations plus distribute-pool flags.
- `MMEA0_SDP_REQ_CNTL` defines read/write/atomic pass-password overrides, DRAM/GMI chain override, inner-domain mode, and request block levels for reads, writes, and atomics.
- `MMEA0_MISC` controls relative priority modes in DRAM/GMI/IO arbiters, early write-return enable per VC, early SDP original-data behavior, link-manager dynamic/halt/reconnect/idle parameters, and chip-select switching preferences.
- `MMEA0_LATENCY_SAMPLING` begins at the chunk tail, defining sampler0/sampler1 filters for DRAM, GMI, IO, read, write, atomic-return, atomic-no-return, and virtual-channel selection. The final `SAMPLER1_VC_MASK` appears just after this chunk and must be merged from the next range.

## Control Flow

There is no direct control flow in this header. The only behavior is indirect: compiled driver code includes this generated macro table, reads or writes an MMIO register from the offset header, and uses a mask/shift pair to isolate a field.

Typical runtime flow in consumers is:

1. Read a 32-bit MMHUB register with a helper such as `RREG32_SOC15`.
2. Update one or more fields using `REG_SET_FIELD` or direct mask operations.
3. Write the result back with `WREG32_SOC15`, or decode status with `REG_GET_FIELD` or direct masks.
4. Poll status, collect counters, or rely on hardware behavior after the register programming takes effect.

One concrete integration in this tree is `drivers/gpu/drm/amd/amdgpu/mmhub_v2_3.c`: `mmhub_v2_3_update_medium_grain_clock_gating()` reads `mmDAGB0_CNTL_MISC2` and clears or sets `DAGB0_CNTL_MISC2__DISABLE_WRREQ_CG_MASK`, `DISABLE_WRRET_CG_MASK`, `DISABLE_RDREQ_CG_MASK`, `DISABLE_RDRET_CG_MASK`, `DISABLE_TLBWR_CG_MASK`, and `DISABLE_TLBRD_CG_MASK` depending on `AMD_CG_SUPPORT_MC_MGCG`. `mmhub_v2_3_get_clockgating()` reads the same masks to report whether medium-grain memory-controller clock gating is active.

## State And Persistence Behavior

The header itself has no state. The hardware registers described by these macros are persistent device state until reset, suspend/resume reprogramming, driver reinitialization, or another MMIO write changes them.

Important state classes represented in this chunk include:

- DAGB credit state: write TLB/data/misc/OSD/FIFO/atomic credit limits, pool credits, maximum packet length, and credit-full indications.
- DAGB diagnostic and status state: pending busy vectors, FIFO empty/full bits, performance-counter selection/mode/enable/clear state, and current counter low/high words.
- DAGB power/clock and parity state: clock-gating disable bits, EA busy disable bits, parity check enable, and read-return FIFO credit policy.
- MMEA0 QoS state: client-to-group maps, group-to-virtual-channel maps, lazy accumulation, CAM allocation, burst limits, age/queue/fixed/urgency coefficients, urgency masking, quantum thresholds, and SDP priority values.
- MMEA0 address-routing state: base/limit/offset windows, fabric destination, interleave topology, DRAM holes, non-power-of-two channel sizing, bank/chip-select/pseudo-channel hashing, harvest enable/ranges, chip-select masks/configuration, and GECC harvest adjustment.
- MMEA0 SDP state: burst arbitration, read-only virtual-channel flags, error/halt on error policy, throttles, tag/response credits, per-VC reservations, request blocking levels, chain overrides, and link-manager thresholds.
- MMEA0 observability state: latency-sampling filter selection for traffic class, operation type, atomic type, and virtual channel.

Several fields have side effects or control liveness rather than merely storing configuration. Counter `CLEAR`/`CLEAR_ALL`, request block levels, halt-on-error, throttles, clock-gating disable bits, snoop override, and parity/check/error policy fields should be treated as active hardware controls.

## Dependencies And Integration Points

Direct dependencies:

- `mmhub_2_3_0_offset.h` supplies matching register address macros such as `mmDAGB0_CNTL_MISC2`; this `_sh_mask.h` file only supplies field layout.
- `mmhub_2_3_0_default.h` supplies reset/default values for this generation.
- AMDGPU register helpers and SOC15 MMIO helpers consume the generated mask/shift names.

Observed integration in this tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v2_3.c` includes `mmhub/mmhub_2_3_0_sh_mask.h`, `mmhub_2_3_0_offset.h`, and `mmhub_2_3_0_default.h`.
- The concrete in-chunk use in `mmhub_v2_3.c` is `DAGB0_CNTL_MISC2` clock-gating mask handling for medium-grain memory-controller clock gating and clock-gating status reporting.
- Other fields in this chunk are ABI surface for generated-register consumers, hardware bring-up, debug/perf tooling, RAS/error-policy flows, and firmware or table-driven programming paths even when there is no local textual reference to each macro in this tree snapshot.

Cross-generation integration matters. Similar `DAGB0_*` and `MMEA0_*` macros exist in other MMHUB generated headers, but bit positions and available fields differ by ASIC generation. Consumers must include the matching `mmhub_2_3_0_*` files for MMHUB 2.3 hardware rather than substituting a nearby generation.

## Risks And Edge Cases

Bitfield drift is the primary risk. These constants are generated from hardware register specifications; if a shift or mask is wrong, driver code may silently program the wrong bits in a 32-bit MMIO register.

Packed fields are common and fragile:

- Client-to-group maps pack sixteen 2-bit client fields into one word.
- Urgency masking packs one bit for each of 32 clients.
- Priority, quantum, credit, reservation, and VC-map registers pack multiple independent policy fields into one register.
- Address-decoder registers pack topology selectors, masks, and chip-select controls where a single incorrect field can affect a large address range.

Status, command, and configuration fields share the same naming convention. For example, `BUSY`, `EMPTY`, `FULL`, and counter-value fields are observed status, while `CLEAR`, `CLEAR_ALL`, request-block, throttle, halt-on-error, snoop-override, and clock-gating-disable fields actively change hardware behavior. Code review should verify access direction and side effects against the register specification, not just the macro name.

Power and clock-gating fields are liveness-sensitive. `DAGB0_CNTL_MISC2` clock-gating disables are used by `mmhub_v2_3.c`; accidentally setting or clearing the wrong bit can leave request/return/TLB clock domains ungated, gated at the wrong time, or misreported in clock-gating status.

Address normalization and DRAM decode fields are correctness-sensitive. Misprogramming `MMEA0_ADDRNORM_*`, `ADDRDEC_*`, hash, harvest, or chip-select selection fields can route memory accesses incorrectly, break interleave assumptions, expose harvested regions, or cause data corruption/hangs.

The chunk ends inside `MMEA0_LATENCY_SAMPLING`, so this document must not be treated as a complete description of all MMEA0 observability/performance/error controls. Later chunks continue the register family.

## Test And Validation Signals

Useful validation is mostly build, register-generation, and hardware behavior coverage:

- Build AMDGPU code that includes `mmhub/mmhub_2_3_0_sh_mask.h`; this catches missing, renamed, or syntactically invalid macro definitions.
- Exercise `mmhub_v2_3_set_clockgating()` and `mmhub_v2_3_get_clockgating()` with `AMD_CG_SUPPORT_MC_MGCG` and confirm `DAGB0_CNTL_MISC2` read/modify/write only changes the intended clock-gating disable bits.
- Compare this header against the authoritative AMD MMHUB 2.3 register database, especially `DAGB0_CNTL_MISC2`, packed DAGB credit controls, `MMEA0_ADDRNORM_*`, `MMEA0_ADDRDEC*`, hash/harvest fields, IO urgency masks, and SDP request/credit registers.
- Use representative `REG_SET_FIELD`/`REG_GET_FIELD` checks for packed fields such as `MMEA0_DRAM_RD_CLI2GRP_MAP0__CID15_GROUP`, `MMEA0_IO_RD_PRI_URGENCY_MASKING__CID31`, `MMEA0_SDP_ARB_FINAL__GMI_WR_THROTTLE`, and `DAGB0_WR_DATA_FIFO_CREDIT_CNTL1__FIX2`.
- On hardware or simulator, read back MMHUB 2.3 registers after initialization and clock-gating transitions to verify default values, intended field updates, and preservation of unrelated fields.
- Run GPU reset, suspend/resume, and power-management tests because hardware register state in this chunk is reset/reprogrammed across those flows.
- Run memory stress and MMHUB client traffic tests that exercise DRAM and IO read/write clients; failures may show as hangs, timeout recovery, protection faults, degraded bandwidth, or unfair client service if group/VC/priority/credit fields are wrong.
- Use performance-counter and latency-sampling smoke tests where available to confirm DAGB counter enable/clear/select behavior and MMEA0 sampler filters select expected traffic classes and virtual channels.

### subset-b-002794: lines 4719-7196

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_3_0_sh_mask.h lines 4719-7196

## Scope

This chunk is a middle segment of the generated AMD MMHUB 2.3.0 shift/mask header. It covers line 4719 through line 7196 and defines 1,069 `__SHIFT` macros and 1,054 `_MASK` macros across 334 visible register comments. The range begins at the tail of `MMEA0_LATENCY_SAMPLING`, then covers MMEA0 monitoring and error-control registers, MMHUB power-control (`PCTL`) registers, L1 TLB stream and fault registers, SAW/L2 VM context registers, ATC L2 cache registers, and the beginning of MMVM L2 protection-fault control. It ends inside `MMVM_L2_PROTECTION_FAULT_CNTL`, before that register's remaining `CRASH_ON_RETRY_FAULT` shift and mask definitions.

The content is declarative only. There are no C functions, structs, enums, allocations, branches, loops, locks, or local side effects. The exported surface is a set of preprocessor constants that encode bit positions and masks for memory-mapped MMHUB hardware registers.

## Purpose

`mmhub_2_3_0_sh_mask.h` provides symbolic field definitions for AMDGPU code targeting the MMHUB 2.3.0 register layout. Consumers combine these macros with companion register offsets from `mmhub_2_3_0_offset.h`, defaults from `mmhub_2_3_0_default.h`, and register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15` to update VM translation, cache, fault, clock-gating, power-management, performance, and diagnostic registers without embedding raw bit arithmetic in driver logic.

This chunk covers the MMHUB surfaces that support:

- MMEA0 performance counters, EDC counters, DSM/error injection controls, error status, address-decode selection, SDP priority overrides, and clock-control fields.
- PCTL deep-sleep, power-gating ignore, save/restore ranges, reserved fields, status, and performance-counter registers for UTCL2 and two slices.
- L1 TLB status and stream-local translation windows for `TLS0`, including 38 control registers, start/end address pairs, invalidation bits, protection-fault status/address, and IOMMU fault status/address.
- SAW and MMVM L2 controls for context 0, page-table base/start/end registers, context disable masks, pipe-busy readbacks, and L2 cache/fragment/fault behavior.
- ATC L2 controls for cache policy, cache data readback words, transaction limits, group real-time classes, parity status, clock gating, memory light sleep, and SDP port clock-enable handshakes.

## Exported API Surface

There are no callable APIs or local types. The public interface is the macro namespace generated from the MMHUB 2.3.0 register database:

- `MMEA0_*`: monitoring and error-analysis fields, including latency sampling, performance-counter low/high words, two counter configs, result control, SEC/DED/SED EDC counters, DSM single-write controls, error-injection controls, clock-control overrides, EDC mode, error status, address-decode selectors, SDP priority overrides, and always-on misc bits.
- `PCTL_*`: power-control fields, including deep-sleep input/override masks for many MMHUB sub-blocks, power-gating ignore masks, slice-level busy/allow controls, UTCL2 misc controls, slice misc controls, register-engine execute/index/data surfaces, state-controller register-save ranges and exclusion sets, status bits, performance counters, and reserved registers.
- `MMMC_VM_MX_L1_*`: L1 TLB status and performance-counter fields, plus the `TLS0` stream context controls, start/end logical address windows, invalidation streams, pending invalidation state, protection-fault status/address, and IOMMU fault status/address.
- `MMVM_L2_SAW_*`: system aperture/window style L2 controls, context 0 translation controls, page-table base/start/end registers, context-disable bitmaps, and pipe-busy readbacks.
- `MM_ATC_L2_*`: address-translation-cache L2 controls, cache data readback fields, transaction limits, group real-time-class register, parity/error status, clock-gating controls, memory light-sleep timing, and SDP port clock enables/receivers.
- `MMVM_L2_*`: the start of the MMVM L2 control and fault namespace, including L2 cache enable/fragment/cache-mode fields, invalidation controls, status/parity bits, dummy-page fault matching, invalidate-control throttles, and most `MMVM_L2_PROTECTION_FAULT_CNTL` shifts.

The usual generated pattern is `<REGISTER>__<FIELD>__SHIFT` plus `<REGISTER>__<FIELD>_MASK`. Full-width address and data registers often provide a single field with a `0xFFFFFFFFL` mask; packed control/status registers expose one macro pair per subfield.

## Register Areas Covered

The MMEA0 block exposes performance and reliability instrumentation around MMHUB memory paths. The counter registers provide select ranges, modes, enables, clears, trigger controls, and low/high counter readback words. EDC registers count correctable, deferred, and detected errors across DRAM, GMI, IO, RRET/WRET tag memories, page memories, and MAM memories. DSM and DSM2 families define single-write irritation and error-injection controls per memory path, while `MMEA0_ERR_STATUS` reports SDP read/write response status, read-data status, data parity, busy-on-error, FUE, and clear bits. Address-decoder and SDP priority fields influence arbitration/diagnostic selection.

The PCTL block is a large power-management surface. `PCTL_MMHUB_DEEPSLEEP_*`, `PCTL_PG_IGNORE_DEEPSLEEP*`, and `PCTL_SLICE*_CFG_DS_ALLOW*` define per-sub-block masks for deep-sleep eligibility and overrides. Slice and UTCL2 misc registers expose disable, clock-control, and FUE/DFT-style fields. The RENG and STCTRL groups provide register-engine execute/index/data registers plus register-save ranges and exclusion sets for UTCL2 and both slices. PCTL also has status and performance-counter registers that mirror the generated counter pattern used by MMEA0.

The L1 TLB section starts with eight `MMMC_VM_MX_L1_TLBn_STATUS` registers that expose request and page-table-walk counters. It then defines four L1 performance-counter configs plus result and readback registers. The `MMMC_VM_MX_L1_TLS0_*` block is the largest area in the chunk: `TLS0_CNTL` selects enable/system access/debug-mode behavior and `TLS0_CNTL0` through `TLS0_CNTL37` pack per-stream page-table and protection attributes such as enable context, page-table depth, range/PDE/valid/read/write/execute protection defaults, TLB bypass, retry behavior, VMID selection, and address comparators. The matching start/end address pairs describe 38 logical address windows. Invalidate stream and pending registers expose 64-bit bitmaps, and protection/IOMMU fault registers carry status plus low/high fault addresses.

The SAW/L2 VM area describes L2 controls and a dedicated context 0 page table. `MMVM_L2_SAW_CNTL*` exposes cache enables, default-page behavior, PTE/PDE cache sizing, page-table-walk credit limits, walk-order controls, snoop controls, and context-1 identity/fragment behavior. `MMVM_L2_SAW_CONTEXT0_*` defines context enable, page-table depth, range/protection fault defaults, retry behavior, page-table block size, address mode, and base/start/end registers. Context-disable and pipe-busy low/high registers are 32-bit bitmaps.

The ATC L2 section defines cache behavior and power-management details for the memory-management L2. `MM_ATC_L2_CNTL*` fields cover L2 cache enablement, line direction, address translation modes, update/force-miss/cache-size controls, page-fragment sizes, and FIFO active transaction limits. Cache data registers expose tag, valid, VMID, PTE/PDE, and address components for diagnostics. Status registers expose busy and parity information. Clock-gating and light-sleep registers define delay, hysteresis, override, enable, setup, and hold fields; `MM_ATC_L2_SDPPORT_CTRL` names each SDP request/response clock-enable and receiver bit.

The final MMVM L2 section starts the non-SAW L2 control surface consumed by MMHUB setup code. `MMVM_L2_CNTL`, `CNTL2`, and `CNTL3` describe cache enablement, invalidation, default page behavior, VMID/cache modes, bank selection, cache update modes, effective sizes, big-page fragment sizes, associativity, and force-miss bits. `MMVM_L2_STATUS` reports L2 busy, per-domain busy, and cache parity errors. Dummy-page fault and invalidate-control registers support fault matching and invalidation throttling. `MMVM_L2_PROTECTION_FAULT_CNTL` starts the global fault-default policy fields used when enabling or disabling MMHUB fault handling.

## Control Flow And State Behavior

This header has no local control flow. Runtime behavior appears only through driver code that includes the generated macros and performs MMIO reads/writes.

The field names imply several hardware state machines and persistent hardware states:

- VM translation setup persists in MMHUB registers until reset, power loss, or driver reprogramming. Page-table base/start/end fields, context enables, page-table depth, block size, address mode, and fault-default bits determine how MMHUB translates GPU virtual addresses.
- Cache and TLB invalidation is command/state oriented. `MMVM_L2_CNTL2` invalidation bits, L1/TLS invalidation stream bitmaps, pending invalidation readbacks, and `MMVM_INVALIDATE_CNTL` outstanding/alternating controls coordinate TLB/L2 cache flushes.
- Fault handling is sticky and policy driven. Protection and IOMMU fault status/address registers capture fault metadata; clear and allow-update bits control whether later faults overwrite stored status. Fault default-enable bits decide whether invalid accesses fault, route to dummy/default pages, retry, NACK, or crash.
- Power and clock state is shared hardware state. PCTL deep-sleep allow/override masks, power-gating ignore masks, ATC L2 clock-gating overrides, and memory light-sleep setup/hold values affect whether MMHUB sub-blocks may gate clocks or enter low-power states.
- Performance and error counters accumulate hardware events. Counter low/high registers, compare fields, enable/clear bits, EDC counters, MMEA error status, PCTL status, and ATC parity status are readback or clear/control points rather than software-owned data structures.
- DSM/error-injection fields intentionally perturb hardware memory paths for validation. These must be treated as lab/recovery controls, because enabling injection or forced single writes can change observed reliability behavior.

No software persistence is implemented here. Any persistence belongs to hardware register contents and to higher-level AMDGPU state that rewrites these registers during initialization, suspend/resume, reset recovery, GART enable/disable, clock-gating changes, or RAS/error-handling flows.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. Semantically, the chunk pairs with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_3_0_offset.h` for matching `mm...`/`reg...` offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_3_0_default.h` for reset/default values such as L2 control defaults used by setup code.
- AMD register helper macros, especially `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

Direct include sites in this tree are `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v2_3.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`. `mmhub_v2_3.c` is the main runtime consumer for this ASIC generation: it initializes GART apertures, system aperture registers, L1 TLB controls, MMVM L2 cache controls, VMID context configuration, invalidation ranges, protection-fault behavior, client-ID fault reporting, and MMHUB clock-gating/light-sleep state. The DCN31 resource path includes the same header for display resource table construction on hardware using this MMHUB register set.

Related code in other MMHUB generations uses matching macro names for similar behavior. For example, nearby `mmhub_v2_0.c`, `mmhub_v3_0*.c`, `mmhub_v3_3.c`, `mmhub_v4_2_0.c`, `mmhub_v1_7.c`, and `mmhub_v9_4.c` show how `MM_ATC_L2_*`, `MMVM_L2_PROTECTION_FAULT_CNTL*`, `MMVM_L2_SAW_*`, and `MMEA0_EDC_*` fields are used for cache setup, fault policy, SAW context programming, clock gating, and RAS counter decoding. These cross-generation users are useful comparison points but must not be assumed bit-compatible without the matching generated header.

## Risks

- Generated-header drift is the main risk. A wrong shift or mask can silently update an adjacent hardware field during `REG_SET_FIELD` read-modify-write operations, affecting VM translation, fault policy, power state, or diagnostic controls.
- The chunk mixes control, status, clear, and readback fields in the same macro form. Consumers need the register specification or established driver sequence to know whether a field is writable, read-only, sticky, write-one-to-clear, clear-on-read, or reserved.
- VM context, page-table, and fault-policy fields are safety-critical for GPU memory isolation. Incorrect values can cause invalid DMA, hidden faults routed to dummy/default pages, fault storms, no-retry crashes, or loss of useful fault evidence.
- Cache/TLB invalidation fields are ordering-sensitive. Missing L1/L2 invalidation bits, wrong pending-stream interpretation, or incorrect outstanding limits can leave stale translations active after VM updates.
- PCTL and ATC clock-gating/light-sleep fields affect live hardware availability. Over-aggressive deep-sleep enables or stale override bits can cause hangs, timeouts, or unreliable fault/performance readback.
- MMEA DSM/error-injection controls can deliberately create SEC/DED/FUE-like behavior. Accidentally enabling injection or single-write irritators in production code would look like hardware reliability failures.
- The range starts and ends at chunk boundaries inside register groups. Earlier chunks contain the first `MMEA0_LATENCY_SAMPLING` shifts, and later chunks contain the rest of `MMVM_L2_PROTECTION_FAULT_CNTL`; merge-time validation should avoid treating those boundary groups as locally incomplete defects.

## Test Signals

Useful validation is mostly build-time, generation-time, and hardware-integration oriented:

- Compile or preprocess AMDGPU and DCN31 code that includes `mmhub_2_3_0_offset.h`, `mmhub_2_3_0_sh_mask.h`, and `mmhub_2_3_0_default.h`.
- Static generation checks that every complete register in the full `mmhub_2_3_0_sh_mask.h` file has matching `__SHIFT` and `_MASK` definitions, with explicit chunk-boundary exceptions for `MMEA0_LATENCY_SAMPLING` and `MMVM_L2_PROTECTION_FAULT_CNTL`.
- Cross-check register and field names against `mmhub_2_3_0_offset.h` and the source register database used to generate the header.
- Runtime MMHUB bring-up tests on MMHUB 2.3.0-class ASICs: GART enable/disable, VMID programming, page-table base/start/end programming, L1/L2 TLB/cache invalidation, VM fault reporting, dummy/default page handling, and no-retry/retry fault behavior.
- Suspend/resume and GPU reset tests that verify MMHUB register state is restored correctly, including PCTL save ranges, deep-sleep overrides, ATC L2 clock gating, memory light sleep, and cache/TLB control registers.
- RAS and diagnostics validation that reads MMEA0 EDC counters, `MMEA0_ERR_STATUS`, ATC L2 parity status, L1/TLS protection fault status, and IOMMU fault addresses, including clear/update behavior.
- Performance-counter validation that MMEA0, PCTL, and L1 TLB counters can be configured, cleared, started/stopped, and read without corrupting unrelated fields.

## Chunk Notes For Merge

This document is intentionally source-tree aligned and covers only lines 4719-7196 of `mmhub_2_3_0_sh_mask.h`. Earlier chunks should cover the beginning of MMEA0 and the missing `MMEA0_LATENCY_SAMPLING` shifts. Later chunks should continue `MMVM_L2_PROTECTION_FAULT_CNTL` and the rest of the MMVM L2 protection-fault namespace. The final per-file report should treat the whole file as a generated ASIC register bitfield map for AMDGPU MMHUB programming, not as handwritten runtime logic.

### subset-b-002795: lines 7197-9714

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_3_0_sh_mask.h

Chunk: `subset-b-002795`
Covered source range: lines 7197-9714 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_3_0_sh_mask.h`

## Purpose

This chunk is a generated AMDGPU MMHUB 2.3.0 shift/mask header section. It contains no executable code; it defines C preprocessor constants that describe bit positions and bit masks for fields in MMHUB memory-management registers.

The covered range is the central MMVM/MMUTCL2 portion of the header. It supplies field metadata for:

- L2 protection-fault control, status, fault address, and default fault address registers;
- context identity aperture and physical-offset registers;
- L2 cache control extensions, cache fragment sizing, real-time class assignment, reserved client-ID bank selection, parity/logging, clock-gating, GCR, and PTE cache dump controls;
- VM context control registers for contexts 0-15;
- per-PF/VF and per-context PTE cache fragment-size registers;
- MMVM L2 and MMUTCL2 performance counter configuration/result registers;
- shared virtualization, SR-IOV VF framebuffer size/offset, IOMMU, MARC relocation/window, ATS, PF aperture, cacheable DRAM, local HBM, harvest-bypass, and active-function registers;
- VM page-table base/start/end registers for contexts 0-15;
- invalidation engine semaphore/request/ack/address-range/register-reserve definitions for engines 0 through the beginning of engine 6.

The source range contains 2,518 lines and 2,102 `#define` lines. The range begins after the first `MMVM_L2_PROTECTION_FAULT_CNTL` comment but includes its mask fields, and it ends in the middle of the `MMVM_INVALIDATE_ENG6_REQ` field set. Earlier and later chunks are needed for a complete file-level view.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or exported symbols in this header chunk. The API surface is macro constants used by AMDGPU register helpers.

The naming convention is consistent:

- `<REGISTER>__<FIELD>__SHIFT` gives the right-shift amount for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Register address macros live in the paired `mmhub_2_3_0_offset.h` header, and reset defaults live in `mmhub_2_3_0_default.h`.

Important macro families in this range include:

- `MMVM_L2_PROTECTION_FAULT_CNTL`, `MMVM_L2_PROTECTION_FAULT_CNTL2`, `MMVM_L2_PROTECTION_FAULT_MM_CNTL3`, `MMVM_L2_PROTECTION_FAULT_MM_CNTL4`, `MMVM_L2_PROTECTION_FAULT_STATUS`, and fault-address/default-address registers. These describe which faults redirect to the default page, which client IDs raise interrupts, retry/no-retry handling, active page migration retry behavior, and status decoding fields such as `MORE_FAULTS`, `WALKER_ERROR`, `PERMISSION_FAULTS`, `MAPPING_ERROR`, `CID`, `RW`, `ATOMIC`, `VMID`, `VF`, and `VFID`.
- `MMVM_L2_CONTEXT1_IDENTITY_APERTURE_*` and `MMVM_L2_CONTEXT_IDENTITY_PHYSICAL_OFFSET_*`, which bound and offset identity-mapped context-1 access.
- `MMVM_L2_CNTL4`, `MMVM_L2_CNTL5`, `MMVM_L2_GCR_CNTL`, `MMVM_L2_CGTT_CLK_CTRL`, and `MMVM_L2_CGTT_BUSY_CTRL`, covering cache partitioning, physical request taps, multimedia IFIFO transaction limits, small/large page fragment size, global cache request bits, and L2 clock-gating controls.
- `MMVM_L2_MM_GROUP_RT_CLASSES`, a 32-bit per-group real-time class bitmap.
- `MMVM_L2_BANK_SELECT_RESERVED_CID` and `MMVM_L2_BANK_SELECT_RESERVED_CID2`, which encode reserved read/write client IDs, enable bits, invalidation mode, private invalidation, and fragment size.
- `MMVM_CONTEXT0_CNTL` through `MMVM_CONTEXT15_CNTL`, each with context enable, page-table depth, page-table block size, retry behavior, fault interrupt enables, and default fault behavior for range, dummy-page, PDE0, valid, read, write, execute, and secure faults.
- `MMVM_CONTEXTS_DISABLE`, which provides disable bits for contexts 0-15.
- `MMVM_L2_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` and `MMVM_L2_CONTEXT*_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES`, which configure small-page fragment size, large-page fragment size, and bank select at PF/VF and context granularity.
- `MMMC_VM_L2_PERFCOUNTER*_CFG`, `MMUTCL2_PERFCOUNTER*_CFG`, result-control registers, and low/high result registers. These provide `PERF_SEL`, `PERF_SEL_END`, `PERF_MODE`, `ENABLE`, `CLEAR`, trigger, clear-all, stop-on-saturate, counter, and compare-value fields.
- `MMMC_VM_FB_SIZE_OFFSET_VF0` through `MMMC_VM_FB_SIZE_OFFSET_VF31`, where each VF register exposes `VF_FB_SIZE` and `VF_FB_OFFSET`.
- Shared virtualization/aperture registers such as `MMVM_IOMMU_MMIO_CNTRL_1`, `MMVM_IOMMU_CONTROL_REGISTER`, `MMVM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER`, `MMVM_PCIE_ATS_CNTL`, `MMVM_PCIE_ATS_CNTL_VF_*`, `MMMC_VM_NB_*`, `MMMC_VM_FB_OFFSET`, `MMMC_VM_SYSTEM_APERTURE_*`, `MMMC_VM_CACHEABLE_DRAM_ADDRESS_*`, `MMMC_VM_LOCAL_HBM_ADDRESS_*`, `MMMC_VM_FB_LOCATION_*`, `MMMC_VM_AGP_*`, and `MMMC_VM_MX_L1_TLB_CNTL`.
- `MMVM_CONTEXT0_PAGE_TABLE_*` through `MMVM_CONTEXT15_PAGE_TABLE_*`, which define base address, logical start/end page number, and reserve register fields for every VM context.
- `MMVM_INVALIDATE_ENG0_*` through `MMVM_INVALIDATE_ENG6_REQ`, covering invalidation engine semaphores, VMID request bitmaps, flush type, L2 PTE/PDE and L1 PTE invalidation bits, protection-fault status-address clearing, request logging, 4K-only invalidation, ack state, and address-range bounds.

The chunk boundary cuts off `MMVM_INVALIDATE_ENG6_REQ` after `FLUSH_TYPE_MASK`; the remaining ENG6 request masks and following ENG6 ack/range/reserve fields are outside this work item.

## Control Flow

The chunk has no local runtime control flow. It is compile-time data consumed by register access macros such as `REG_SET_FIELD()` and `REG_GET_FIELD()`.

The concrete runtime path in this source tree is `drivers/gpu/drm/amd/amdgpu/mmhub_v2_3.c`, which includes:

- `mmhub/mmhub_2_3_0_offset.h`
- `mmhub/mmhub_2_3_0_sh_mask.h`
- `mmhub/mmhub_2_3_0_default.h`

`gmc_v10_0_set_mmhub_funcs()` selects `mmhub_v2_3_funcs` for MMHUB IP versions 2.3.0, 2.4.0, and 2.4.1. Once selected, `mmhub_v2_3_gart_enable()` programs the MMHUB in a fixed sequence:

1. Program GART page-table base/start/end registers for context 0.
2. Program system aperture, AGP aperture, default system page, and protection-fault default page registers.
3. Enable and configure the L1 TLB and L2 cache.
4. Enable the system-domain VM context.
5. Disable the context-1 identity aperture by writing an inverted low/high address range and zero physical offset.
6. Configure VMID contexts 1-15 with context-enable, page-table depth/block size, default protection-fault behavior, retry/no-retry behavior, and full page-table address ranges.
7. Program invalidation engine address ranges.

The important control pattern is read-modify-write:

- read a hardware register through `RREG32_SOC15()` or `RREG32_SOC15_OFFSET()`;
- insert fields with `REG_SET_FIELD()` using this header's mask/shift macros;
- write the result with `WREG32_SOC15()` or `WREG32_SOC15_OFFSET()`.

Fault reporting uses the inverse pattern: `mmhub_v2_3_print_l2_protection_fault_status()` decodes `MMVM_L2_PROTECTION_FAULT_STATUS` with `REG_GET_FIELD()` to identify the client ID, read/write bit, walker error, permission-fault class, mapping error, and multiple-fault state.

TLB/cache invalidation uses `mmhub_v2_3_get_invalidate_req()`, which builds a request value from `MMVM_INVALIDATE_ENG0_REQ` fields: VMID bitmap, flush type, L2 PTE invalidation, PDE0/PDE1/PDE2 invalidation, L1 PTE invalidation, and fault-status-address clearing.

## State And Persistence Behavior

The header has no mutable software state. Its constants are compiled into AMDGPU code and used to manipulate persistent hardware register state.

The state represented by this chunk is MMHUB memory-translation state:

- GART and per-VMID page-table base/start/end state persists in MMHUB context registers until overwritten, disabled, reset, or reinitialized during suspend/resume or GPU reset.
- Context control state determines whether a VMID is enabled, how many page-table levels are walked, how faults are classified, and whether faults retry, interrupt, redirect to a dummy/default page, or can become crash-triggering no-retry/retry faults.
- Protection-fault status and address registers retain fault evidence until cleared by driver action or hardware reset. The `CLEAR_PROTECTION_FAULT_STATUS_ADDR` fields are the explicit clearing hooks.
- Default fault address registers point faults to `adev->dummy_page_addr` when default handling is enabled.
- Invalidation engine semaphore/request/ack registers are transient synchronization state, but incorrect values can leave stale translations in L1/L2 TLB/cache state.
- SR-IOV VF framebuffer size/offset and ATS/IOMMU/shared virtualization registers participate in partitioning and address-translation state that must match PF/VF ownership and firmware policy.
- Perf-counter configuration and result registers hold diagnostic state until cleared, reset, or reprogrammed.

The default values referenced by `mmhub_v2_3.c` come from `mmhub_2_3_0_default.h`; this chunk provides the field layout used when those defaults are modified. Reset or power-management transitions can restore hardware defaults, so AMDGPU reprograms these registers during GART enable and clock-gating flows.

## Dependencies And Integration Points

Direct dependencies in the MMHUB 2.3.0 register family are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_3_0_offset.h`, which provides register offsets such as `mmMMVM_L2_PROTECTION_FAULT_CNTL`, `mmMMVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32`, and `mmMMVM_INVALIDATE_ENG0_REQ`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_3_0_default.h`, which provides reset/default values such as `mmMMVM_L2_CNTL4_DEFAULT`, `mmMMVM_L2_CNTL5_DEFAULT`, and protection-fault/invalidation defaults.
- AMDGPU register helper macros and SOC15 accessors, especially `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`.

Primary source-tree consumers and integration points:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v2_3.c`: includes this header and programs protection faults, context controls, page-table registers, cache/TLB controls, identity aperture, invalidation, clock gating, and fault-status reporting.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v2_3.h`: exposes `mmhub_v2_3_funcs`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`: chooses `mmhub_v2_3_funcs` for MMHUB IP 2.3.0/2.4.x and integrates MMHUB with the GMC v10 memory-management path.
- `amdgpu_vmhub` state: `mmhub_v2_3_init()` stores MMHUB register offsets, context distance, context-address distance, invalidation-engine distance, fault-status/control offsets, `vm_cntx_cntl_vm_fault` interrupt masks, and the VM hub callback table.
- `amdgpu_mmhub_client_name()` and `amdgpu_mmhub_init_client_info()`: fault-status `CID`/`RW` decoding is tied to the Vangogh MMHUB client-ID table in `mmhub_v2_3.c`.

This generated header must stay synchronized with the matching offset/default headers and the ASIC register database. Same-named fields exist in other MMHUB generations, but field presence and offsets can differ; for example later MMHUB 4.2 invalidation request fields add `INVALIDATE_L2_PDE3`, while this MMHUB 2.3.0 chunk only defines PDE0-PDE2 in the visible request fields.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. The compiler cannot verify that a mask belongs to the register being accessed, that a shift matches the mask, or that a field exists for this ASIC generation.

Fault handling fields are safety-critical. Incorrect `MMVM_L2_PROTECTION_FAULT_CNTL` or `MMVM_CONTEXT*_CNTL` values can turn recoverable faults into crashes, suppress needed interrupts, create VM fault storms, retry when the driver expects no-retry behavior, or redirect bad accesses to an unintended physical/default page.

Page-table address fields split 64-bit physical/logical page numbers into low and high registers. Wrong masks, shifts, high-bit widths, or context-address distances can point a VMID at the wrong page directory or make a valid address range appear truncated.

Context register families are repetitive. The header defines the same field shape for contexts 0-15, and driver code relies on distances between context 0 and context 1 registers. A regenerated offset/header mismatch can make looped `WREG32_SOC15_OFFSET()` programming hit the wrong VMID.

Invalidation engine fields are translation-coherency critical. Missing `INVALIDATE_L2_PTES`, PDE invalidation, L1 invalidation, or wrong VMID bitmap can leave stale translations active after page-table changes. Incorrect address-range low/high fields can also over-invalidate or under-invalidate.

The assigned chunk ends in the middle of `MMVM_INVALIDATE_ENG6_REQ`. Any analysis of ENG6 is partial here. The final file-level report should merge with the following chunk before claiming full invalidation-engine coverage.

SR-IOV and virtualization fields can affect PF/VF isolation. VF framebuffer offset/size, active function ID, shared reset request, ATS per-VF controls, IOMMU controls, and MARC relocation/window fields should not be changed casually because wrong programming can expose or deny memory ranges across functions.

Clock-gating and cache control fields affect power and liveness. Bad values in `MMVM_L2_CGTT_CLK_CTRL`, `MMUTCL2_CGTT_CLK_CTRL`, cache fragment-size, bank-select, or GCR fields can cause performance regressions, hangs, or incorrect cache/TLB behavior that only appears under load.

Generated constants use `L`-suffixed hexadecimal values intended for 32-bit registers. Callers should keep using the driver's unsigned register types and helper macros to avoid signed arithmetic or shift-width surprises.

## Test Signals

Useful validation is a mix of build coverage, static generated-header checks, and hardware behavior tests:

- Build AMDGPU with GMC v10/MMHUB v2.3 support enabled. Missing or renamed macros should fail in `mmhub_v2_3.c`, `gmc_v10_0.c`, and related VM/GMC paths.
- Static consistency checks that every complete `_MASK` has a matching `__SHIFT`, no duplicate macro names have conflicting values, and field prefixes match registers in `mmhub_2_3_0_offset.h`. This chunk intentionally has an incomplete `MMVM_INVALIDATE_ENG6_REQ` field set because of the line-range boundary.
- Boot an MMHUB 2.3.0/2.4.x ASIC path and verify GART enable succeeds without VM setup errors, GPU reset loops, or early page-fault storms.
- Exercise VM fault handling: trigger controlled invalid, read/write, range, dummy-page, and PDE/valid faults; verify `MMVM_L2_PROTECTION_FAULT_STATUS` decoding logs expected `CID`, `RW`, permission/mapping state, VMID, and VF/VFID bits.
- Toggle `set_fault_enable_default()` behavior and verify faults redirect to the dummy/default page when expected and crash/no-retry bits are set only in the intended mode.
- Run GPUVM workloads that allocate, update, and invalidate page tables across multiple VMIDs; verify TLB flushes complete and no stale translations remain after page migration or unmap.
- Cover SR-IOV VF paths where `mmhub_v2_3_gart_enable()` programs `MMMC_VM_FB_LOCATION_BASE/TOP`, and validate VF framebuffer sizing/offset isolation against PF policy.
- Check suspend/resume and GPU reset recovery: page-table bases, system aperture, default fault address, context controls, invalidation ranges, and cache/TLB controls should be reinitialized correctly.
- Use performance counter smoke tests for `MMMC_VM_L2_PERFCOUNTER*` and `MMUTCL2_PERFCOUNTER*`: configure, clear, enable, read low/high results, and confirm counters change under MMHUB traffic.
- Verify medium-grain clock-gating/light-sleep behavior around MMHUB accesses, especially when cache/TLB invalidation and VM faults happen under clock-gated states.

### subset-b-002796: lines 9715-10331

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_3_0_sh_mask.h lines 9715-10331

## Scope

This chunk is the final section of the generated MMHUB 2.3.0 shift/mask header. It starts in the middle of the `MMVM_INVALIDATE_ENG6_REQ` field definitions and continues through:

- `MMVM_INVALIDATE_ENG6` through `MMVM_INVALIDATE_ENG17` acknowledgement, address-range, and reserved-register field masks.
- Full invalidation request field masks for engines 7 through 17.
- The `mmhub_mmutcl2_mml2tlbpfdec` address block, currently represented here by `MML2TLB_TLB0_STATUS`.
- The `mmhub_mmutcl2_mml2tlbpldec` performance-counter configuration and result-control masks.
- The `mmhub_mmutcl2_mml2tlbprdec` performance-counter result low/high masks.
- The closing `#endif` for `_mmhub_2_3_0_SH_MASK_HEADER`.

The source file is a generated hardware register bitfield map. This chunk defines preprocessor constants only; it contains no C functions, structs, runtime variables, or executable branches.

## Purpose

The header provides the bit-level ABI used by AMDGPU code when it composes or decodes MMHUB 2.3.0 MMIO register values. The conventional macro pairs are:

- `<REGISTER>__<FIELD>__SHIFT`, the field bit offset.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit mask for that field.

The sibling `mmhub_2_3_0_offset.h` file supplies register addresses such as `mmMMVM_INVALIDATE_ENG0_REQ`, `mmMMVM_INVALIDATE_ENG0_ACK`, and `mmMMVM_INVALIDATE_ENG0_ADDR_RANGE_LO32`; this file supplies field layout. The direct runtime consumer for this ASIC generation is `amdgpu/mmhub_v2_3.c`, which includes this header and uses the masks through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`.

## Important Macro Families

### MMVM Invalidate Engine Fields

The `MMVM_INVALIDATE_ENGn` family describes per-engine VM/TLB invalidation register layouts. The covered chunk starts after the shift definitions for `MMVM_INVALIDATE_ENG6_REQ`, so its first visible entries are the remaining request masks for engine 6. Engines 7 through 17 then repeat the full register pattern:

- `MMVM_INVALIDATE_ENGn_SEM` exposes a single `SEMAPHORE` bit.
- `MMVM_INVALIDATE_ENGn_REQ` exposes `PER_VMID_INVALIDATE_REQ`, `FLUSH_TYPE`, `INVALIDATE_L2_PTES`, `INVALIDATE_L2_PDE0`, `INVALIDATE_L2_PDE1`, `INVALIDATE_L2_PDE2`, `INVALIDATE_L1_PTES`, `CLEAR_PROTECTION_FAULT_STATUS_ADDR`, `LOG_REQUEST`, and `INVALIDATE_4K_PAGES_ONLY`.
- `MMVM_INVALIDATE_ENGn_ACK` exposes `PER_VMID_INVALIDATE_ACK` and `SEMAPHORE`.
- `MMVM_INVALIDATE_ENGn_ADDR_RANGE_LO32` exposes `S_BIT` and the low 31 bits of the logical page address range.
- `MMVM_INVALIDATE_ENGn_ADDR_RANGE_HI32` exposes the high 5 bits of the logical page address range.
- `MMVM_INVALIDATE_ENGn_RESERVE0/1/2` expose full-width `DUMMY` fields.

The request layout is stable across the covered engines: VMID request bits occupy the low 16 bits, `FLUSH_TYPE` occupies bits 16-18, invalidation scope bits occupy bits 19-23, and optional fault-status/log/4K-only controls occupy bits 24-26. The acknowledgement layout mirrors the VMID mask in bits 0-15 and puts the semaphore acknowledgement at bit 16.

### Invalidation Address Range Fields

Each engine has a low and high address-range register. The low register encodes `S_BIT` at bit 0 and `LOGI_PAGE_ADDR_RANGE_LO31` in bits 1-31. The high register carries `LOGI_PAGE_ADDR_RANGE_HI5` in bits 0-4. `mmhub_v2_3_program_invalidation()` initializes every invalidation engine's range to `0xffffffff` low and `0x1f` high, effectively programming the full addressable logical page range before invalidation requests are issued.

### L2 TLB Status

`MML2TLB_TLB0_STATUS` belongs to the `mmhub_mmutcl2_mml2tlbpfdec` address block. It provides:

- `BUSY`, a bit indicating active TLB work.
- `FOUND_PARITY_ERRORS`, a bit indicating parity error detection in the L2 TLB path.

No in-tree MMHUB 2.3.0 C code references these specific macros directly in the checked source, but they are part of the generated register surface available to debug, bring-up, or future error-handling code.

### L2 TLB Performance Counters

The `MML2TLB_PERFCOUNTER0_CFG` through `MML2TLB_PERFCOUNTER3_CFG` registers share the same encoding:

- `PERF_SEL` in bits 0-7 selects the first event.
- `PERF_SEL_END` in bits 8-15 selects the end/range companion event.
- `PERF_MODE` in bits 24-27 selects counter mode.
- `ENABLE` at bit 28 enables the counter.
- `CLEAR` at bit 29 clears the counter.

`MML2TLB_PERFCOUNTER_RSLT_CNTL` selects and controls result capture with `PERF_COUNTER_SELECT`, `START_TRIGGER`, `STOP_TRIGGER`, `ENABLE_ANY`, `CLEAR_ALL`, and `STOP_ALL_ON_SATURATE`.

`MML2TLB_PERFCOUNTER_LO` and `MML2TLB_PERFCOUNTER_HI` expose counter result storage. The low register is a full 32-bit low counter word. The high register splits bits 0-15 as `COUNTER_HI` and bits 16-31 as `COMPARE_VALUE`, which means consumers must not treat the high register as an unqualified 32-bit high counter word.

## Control Flow

There is no local control flow in this header. Runtime control flow is in the MMHUB driver code that includes it:

- `mmhub_v2_3_get_invalidate_req()` builds an invalidation request using `REG_SET_FIELD` with the `MMVM_INVALIDATE_ENG0_REQ` layout. Because engines 6-17 in this chunk use the same request field layout, generic VM hub code can use engine offsets rather than separate field encodings per engine.
- `mmhub_v2_3_program_invalidation()` loops over 18 invalidation engines and writes address range low/high registers by adding `i * hub->eng_addr_distance` to engine 0's address-range register.
- `mmhub_v2_3_init()` records `hub->vm_inv_eng0_sem`, `hub->vm_inv_eng0_req`, `hub->vm_inv_eng0_ack`, `hub->eng_distance`, and `hub->eng_addr_distance`. Those distances let common VM invalidation code address engines 0-17 consistently.
- Higher-level VM flush paths then write request registers, wait for acknowledgement bits, and coordinate semaphore state using the register addresses and field masks supplied by the generated headers.

The performance-counter and TLB-status macros in this chunk are passive definitions until a diagnostics or profiling path programs the corresponding MMIO registers.

## State and Persistence Behavior

The header itself persists no software state. The persistent or latched state described by the macros lives in MMHUB hardware registers:

- Invalidation request registers hold command bits until hardware consumes or overwrites them according to the MMHUB protocol.
- Acknowledgement registers report completion per VMID and semaphore state.
- Address-range registers persist the logical-page range used by invalidation engines. For MMHUB 2.3.0, the driver initializes all 18 engines to the maximal range during GART enablement.
- `MML2TLB_TLB0_STATUS` exposes transient busy state and error indication.
- Performance counter configuration registers persist event selection, mode, enable, and clear state until changed or reset.
- Performance counter result registers expose accumulated hardware counter values and compare state.

Several fields are command or strobe style rather than ordinary durable settings: invalidation request bits trigger TLB/cache invalidation work, `CLEAR` clears individual performance counters, and `CLEAR_ALL` clears the selected result-control domain. Consumers need the owning driver's sequencing and timeout policy; the generated masks do not encode ordering guarantees.

## Dependencies and Integration Points

This chunk depends on the AMDGPU register access infrastructure and the paired generated headers:

- `amdgpu/mmhub_v2_3.c` includes `mmhub_2_3_0_offset.h`, `mmhub_2_3_0_sh_mask.h`, and `mmhub_2_3_0_default.h`.
- `mmhub_2_3_0_offset.h` provides MMIO register numbers. The masks in this chunk are only meaningful when paired with those addresses.
- `soc15_common.h` and AMDGPU SOC15 helpers provide the MMHUB instance addressing used by `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`.
- `REG_SET_FIELD` and `REG_GET_FIELD` rely on the exact `__SHIFT` and `_MASK` naming convention used here.
- `struct amdgpu_vmhub` stores engine base addresses and spacing derived from the generated offset header, allowing common VM invalidation logic to walk engines without hard-coding every `ENGn` address.

This file is source-tree-aligned with the Linux AMDGPU ASIC register headers under `drivers/gpu/drm/amd/include/asic_reg/mmhub`. It should be regenerated from AMD register descriptions rather than hand-edited when hardware definitions change.

## Risks and Edge Cases

- The chunk starts mid-register at line 9715. Engine 6 request shift definitions are in the preceding chunk, while the corresponding masks are in this chunk. Any merged per-file report should join these halves before describing engine 6 as a complete register.
- Field layout drift is high risk. `REG_SET_FIELD` will silently compose incorrect MMIO values if a mask or shift is wrong, potentially causing incomplete TLB invalidation, stale translations, missed acknowledgements, or VM fault storms.
- The driver loops over 18 invalidation engines. If future hardware changes the engine count, the register spacing, or the engine layout, both generated headers and the C loop assumptions need review.
- `PER_VMID_INVALIDATE_REQ` and `PER_VMID_INVALIDATE_ACK` are 16-bit fields. Callers must avoid invalid VMID shifts outside the supported range.
- The `MML2TLB_PERFCOUNTER_HI` register is split between `COUNTER_HI` and `COMPARE_VALUE`; interpreting it as a plain 64-bit counter high word would corrupt profiler results.
- Reserved `DUMMY` fields should not be treated as usable ABI without hardware documentation. Writing non-default values to reserved registers can have undefined hardware effects.
- Performance-counter control bits such as `ENABLE`, `CLEAR`, `ENABLE_ANY`, `CLEAR_ALL`, and `STOP_ALL_ON_SATURATE` affect live counters and should be coordinated with any concurrent profiling or diagnostics user.
- TLB status/error bits are hardware-observed state; polling code must account for timeout and reset behavior rather than assuming `BUSY` always clears promptly.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-facing:

- Build coverage for `amdgpu/mmhub_v2_3.c` confirms that `REG_SET_FIELD(..., MMVM_INVALIDATE_ENG0_REQ, ...)` and related masks still compile with the generated header.
- VM/GART enablement on MMHUB 2.3.0 hardware should execute `mmhub_v2_3_program_invalidation()` and successfully program all 18 invalidation address ranges.
- GPUVM stress tests should show successful TLB invalidation completion with matching per-VMID acknowledgement bits and no hangs in invalidation wait paths.
- VM fault tests should still print meaningful MMHUB protection fault status and should not regress into repeated stale-translation faults after page table updates.
- Profiling or debug tests that use MML2TLB performance counters should verify counter clear, enable, saturation/stop behavior, event selection, and 48-bit-style result reconstruction from `LO` plus the 16-bit `COUNTER_HI` field.
- Error-injection or low-level diagnostics, when available, can check that `MML2TLB_TLB0_STATUS__FOUND_PARITY_ERRORS_MASK` is decoded as a single-bit status indicator.
