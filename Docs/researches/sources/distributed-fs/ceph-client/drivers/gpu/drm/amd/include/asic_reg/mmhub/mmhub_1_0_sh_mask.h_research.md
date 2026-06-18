# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002750`: lines 1-2367, `Docs/researches/chunks/subset-b-002750_research.md`
- `subset-b-002751`: lines 2368-4742, `Docs/researches/chunks/subset-b-002751_research.md`
- `subset-b-002752`: lines 4743-7093, `Docs/researches/chunks/subset-b-002752_research.md`
- `subset-b-002753`: lines 7094-9528, `Docs/researches/chunks/subset-b-002753_research.md`
- `subset-b-002754`: lines 9529-10249, `Docs/researches/chunks/subset-b-002754_research.md`

## Chunk Research

### subset-b-002750: lines 1-2367

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_0_sh_mask.h lines 1-2367

## Scope

This chunk covers the beginning of the generated AMDGPU MMHub 1.0 shift/mask header. It starts with the MIT-style AMD copyright/license text, the `_mmhub_1_0_SH_MASK_HEADER` include guard, and the start of the `mmhub_dagbdec` address block. The covered register-field definitions run from `DAGB0_RDCLI0` through the start of `DAGB1_RD_CNTL_MISC`.

The file continues beyond this range. The line boundary is inside one register definition: this chunk includes all `DAGB1_RD_CNTL_MISC` shift fields and only `DAGB1_RD_CNTL_MISC__STOR_POOL_CREDIT_MASK`; the remaining `DAGB1_RD_CNTL_MISC` masks begin on line 2368 and belong to the next chunk.

This is generated hardware register metadata. It contains preprocessor constants only. There are no C functions, structs, enums, runtime variables, storage objects, or executable control flow in this chunk.

## Purpose

The purpose of this section is to define the bit-level ABI for the MMHub DAGB decoder registers on MMHub 1.0 ASICs. Each field is represented by the standard pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset for composing or extracting a field.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit mask for isolating that field.

The companion `mmhub_1_0_offset.h` header defines register addresses such as `mmDAGB0_CNTL_MISC2`, `mmDAGB0_PERFCOUNTER0_CFG`, and `mmDAGB1_RD_VC7_CNTL`; this file defines the field layout at those addresses. Runtime code reads and writes the addresses through AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15_OFFSET`, and field helpers/macros such as `REG_SET_FIELD` or direct bit masking.

The covered DAGB fields describe memory-request arbitration and accounting around two DAGB instances:

- `DAGB0` read and write request/client paths.
- The start of `DAGB1` read request/client paths.

The fields cover virtual-channel routing, TLB credit checks, urgency thresholds, bandwidth caps/floors, outstanding request limits, credit pools, clock-gating controls, busy/pending status, FIFO/credit-full status, and DAGB performance-counter selection/control.

## Important Macro Families

### Read and Write Client Configuration

`DAGB0_RDCLI0` through `DAGB0_RDCLI15` and `DAGB0_WRCLI0` through `DAGB0_WRCLI15` define the repeated per-client fields for DAGB0 read and write clients. `DAGB1_RDCLI0` through `DAGB1_RDCLI15` define the same repeated layout for the DAGB1 read clients in this chunk.

Each client exposes the same logical knobs:

- `VIRT_CHAN` selects a virtual channel.
- `CHECK_TLB_CREDIT` enables credit gating against TLB availability.
- `URG_HIGH` and `URG_LOW` encode urgency thresholds.
- `MAX_BW_ENABLE` and `MAX_BW` control per-client maximum bandwidth limiting.
- `MIN_BW_ENABLE` and `MIN_BW` control minimum bandwidth reservation.
- `OSD_LIMITER_ENABLE` and `MAX_OSD` control outstanding-request limiting.

The repetition is intentional hardware layout, not source duplication that should be refactored. Consumers depend on the register-specific macro names matching the generated offset header and hardware register specification.

### Global Read and Write Control

`DAGB0_RD_CNTL`, `DAGB0_WR_CNTL`, and `DAGB1_RD_CNTL` define global arbitration timing and virtual-channel sharing fields:

- `SCLK_FREQ`
- `CLI_MAX_BW_WINDOW`
- `VC_MAX_BW_WINDOW`
- `IO_LEVEL_OVERRIDE_ENABLE`
- `IO_LEVEL`
- `IO_LEVEL_COMPLY_VC`
- `SHARE_VC_NUM`

`DAGB0_RD_GMI_CNTL`, `DAGB0_WR_GMI_CNTL`, and `DAGB1_RD_GMI_CNTL` define credit, level, burst, and lazy-timer fields for the GMI-facing path.

### DAGB Address/Data Path Tuning

The `*_ADDR_DAGB`, `*_DATA_DAGB`, `*_OUTPUT_DAGB_MAX_BURST`, `*_OUTPUT_DAGB_LAZY_TIMER`, `*_ADDR_DAGB_MAX_BURST0/1`, and `*_ADDR_DAGB_LAZY_TIMER0/1` families configure the DAGB request distribution and per-client burst/timer behavior.

Common fields include:

- `DAGB_ENABLE`
- `ENABLE_JUMP_AHEAD`
- `DISABLE_SELF_INIT`
- `WHOAMI`
- Four-bit `VC0` through `VC7` max-burst/lazy-timer values.
- Four-bit `CLIENT0` through `CLIENT15` max-burst/lazy-timer values split across `0` and `1` registers.

DAGB0 has both read and write address-path definitions in this chunk. DAGB0 write also has a separate data-path family (`DAGB0_WR_DATA_DAGB*`) for write data behavior. DAGB1 read address-path definitions are present up to the requested chunk boundary.

### Virtual-Channel Credit Control

`DAGB0_RD_VC0_CNTL` through `DAGB0_RD_VC7_CNTL`, `DAGB0_WR_VC0_CNTL` through `DAGB0_WR_VC7_CNTL`, and `DAGB1_RD_VC0_CNTL` through `DAGB1_RD_VC7_CNTL` define per-virtual-channel credits and limiters:

- `STOR_CREDIT`
- `EA_CREDIT`
- `MAX_BW_ENABLE`
- `MAX_BW`
- `MIN_BW_ENABLE`
- `MIN_BW`
- `OSD_LIMITER_ENABLE`
- `MAX_OSD`

These fields are scheduling and backpressure policy for request flow through the MMHub. They are persistent hardware register state after programming, not software-maintained state in this header.

### Credit Pools and TLB Credits

`DAGB0_RD_CNTL_MISC`, `DAGB0_WR_CNTL_MISC`, and the partial `DAGB1_RD_CNTL_MISC` define pool-credit and legacy/coherency fields:

- `STOR_POOL_CREDIT`
- `EA_POOL_CREDIT`
- `IO_EA_CREDIT`
- `STOR_CC_LEGACY_MODE`
- `EA_CC_LEGACY_MODE`
- `UTCL2_CID`

`DAGB0_RD_TLB_CREDIT`, `DAGB0_WR_TLB_CREDIT`, and the following `DAGB1_RD_TLB_CREDIT` block outside this chunk use six five-bit fields (`TLB0` through `TLB5`) to describe TLB credit allotments. In the covered range, DAGB0 read/write TLB credit definitions are complete; DAGB1 read TLB credit starts immediately after this chunk.

`DAGB0_WR_DATA_CREDIT` and `DAGB0_WR_MISC_CREDIT` add write-specific credit controls for deadlock virtual-channel credits, large/middle/small burst credits, atomic credit, deadlock VC number, OSD credit, and OSD deadlock credit.

### Pending and Status Registers

The pending registers are simple 32-bit `BUSY` bitmaps:

- Read side: `DAGB0_RDCLI_ASK_PENDING`, `DAGB0_RDCLI_GO_PENDING`, `DAGB0_RDCLI_GBLSEND_PENDING`, `DAGB0_RDCLI_TLB_PENDING`, `DAGB0_RDCLI_OARB_PENDING`, and `DAGB0_RDCLI_OSD_PENDING`.
- Write side: `DAGB0_WRCLI_ASK_PENDING`, `DAGB0_WRCLI_GO_PENDING`, `DAGB0_WRCLI_GBLSEND_PENDING`, `DAGB0_WRCLI_TLB_PENDING`, `DAGB0_WRCLI_OARB_PENDING`, `DAGB0_WRCLI_OSD_PENDING`, `DAGB0_WRCLI_DBUS_ASK_PENDING`, and `DAGB0_WRCLI_DBUS_GO_PENDING`.

`DAGB0_FIFO_EMPTY`, `DAGB0_FIFO_FULL`, `DAGB0_WR_CREDITS_FULL`, and `DAGB0_RD_CREDITS_FULL` expose aggregate empty/full state. These are likely read-mostly diagnostic or sequencing aids for power-management, reset, or debug flows. The header does not enforce polling order; call sites must know when hardware state is stable enough to read.

### Clock-Gating and Light-Sleep Control

The chunk defines clock-gating timer and override fields for several DAGB0 and DAGB1 subpaths:

- `DAGB0_RD_CGTT_CLK_CTRL`, `DAGB0_WR_CGTT_CLK_CTRL`, `DAGB1_RD_CGTT_CLK_CTRL`
- `DAGB0_L1TLB_RD_CGTT_CLK_CTRL`, `DAGB0_L1TLB_WR_CGTT_CLK_CTRL`, `DAGB1_L1TLB_RD_CGTT_CLK_CTRL`
- `DAGB0_ATCVM_RD_CGTT_CLK_CTRL`, `DAGB0_ATCVM_WR_CGTT_CLK_CTRL`, `DAGB1_ATCVM_RD_CGTT_CLK_CTRL`

These share fields such as `ON_DELAY`, `OFF_HYSTERESIS`, `SOFT_STALL_OVERRIDE`, `LS_OVERRIDE`, and per-direction light-sleep override bits (`WRITE`, `READ`, `RETURN`, `REGISTER`).

`DAGB0_CNTL_MISC2` is directly used by `amdgpu/mmhub_v1_0.c` to enable or disable medium-grain clock gating. Its covered fields include urgency enable bits, request/return/TLB clock-gating disable bits, EA busy-disable bits, and `SWAP_CTL`. In `mmhub_v1_0_update_medium_grain_clock_gating()`, the driver clears `DAGB0_CNTL_MISC2__DISABLE_WRREQ_CG_MASK`, `DAGB0_CNTL_MISC2__DISABLE_WRRET_CG_MASK`, `DAGB0_CNTL_MISC2__DISABLE_RDREQ_CG_MASK`, `DAGB0_CNTL_MISC2__DISABLE_RDRET_CG_MASK`, `DAGB0_CNTL_MISC2__DISABLE_TLBWR_CG_MASK`, and `DAGB0_CNTL_MISC2__DISABLE_TLBRD_CG_MASK` to allow clock gating, and sets them to disable it. The same source also uses `DAGB1_CNTL_MISC2` masks, but that block appears later in the header outside this chunk.

### Miscellaneous Control and Performance Counters

`DAGB0_DAGB_DLY` defines a delay/client/position triple (`DLY`, `CLI`, `POS`) for DAGB delay tuning.

`DAGB0_CNTL_MISC` remaps external-address virtual channels (`EA_VC0_REMAP` through `EA_VC7_REMAP`) and configures bandwidth initialization and read/write gap cycles (`BW_INIT_CYCLE`, `BW_RW_GAP_CYCLE`).

The DAGB0 performance-counter block includes:

- `DAGB0_PERFCOUNTER_LO`, a 32-bit low counter value.
- `DAGB0_PERFCOUNTER_HI`, a high counter field plus `COMPARE_VALUE`.
- `DAGB0_PERFCOUNTER0_CFG`, `DAGB0_PERFCOUNTER1_CFG`, and `DAGB0_PERFCOUNTER2_CFG`, each with `PERF_SEL`, `PERF_SEL_END`, `PERF_MODE`, `ENABLE`, and `CLEAR`.
- `DAGB0_PERFCOUNTER_RSLT_CNTL`, with counter selection, start/stop trigger fields, `ENABLE_ANY`, `CLEAR_ALL`, and `STOP_ALL_ON_SATURATE`.

The `DAGB0_RESERVE0` through `DAGB0_RESERVE17` blocks define full-width reserved registers. They preserve address-space shape for generated headers and should not be treated as meaningful programmable feature fields without hardware documentation.

## Important APIs, Types, and Functions

This chunk defines no callable APIs, C types, or functions. Its public interface is a flat set of C preprocessor macros consumed by MMHub and media-block driver code.

Important dependency conventions:

- `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` names must match the generic field helper naming convention used by AMDGPU.
- Offset macros in `mmhub_1_0_offset.h` provide the `mm<REGISTER>` addresses corresponding to these field macros.
- Default-value macros in `mmhub_1_0_default.h` may be used by runtime code alongside these masks when composing complete register values.

Primary direct consumers in this source tree include:

- `drivers/gpu/drm/amd/amdgpu/mmhub_v1_0.c`, which includes this header and uses MMHub masks during memory-management hub initialization, VM/TLB/cache setup, fault handling, and clock-gating control.
- `drivers/gpu/drm/amd/amdgpu/uvd_v7_0.c` and `drivers/gpu/drm/amd/amdgpu/vce_v4_0.c`, which include the header as part of the SOC15/MMHub register environment for Vega-era media blocks, though the DAGB-specific masks in this chunk are chiefly MMHub-facing.

## Control Flow

There is no control flow in the header itself. Runtime control flow is in the consumers that include it.

The main observed integration flow for fields in this chunk is in `mmhub_v1_0_update_medium_grain_clock_gating()`:

1. Read current MMHub clock-gating and DAGB misc-control registers.
2. If medium-grain clock gating is enabled and supported, clear the `DISABLE_*_CG` bits in `DAGB0_CNTL_MISC2` and, for non-Raven ASICs, the equivalent DAGB1 register.
3. If disabled or unsupported, set those disable bits.
4. Write back only if the composed values changed.

`mmhub_v1_0_get_clockgating()` also reads `DAGB0_CNTL_MISC2` and infers `AMD_CG_SUPPORT_MC_MGCG` when the ATC L2 clock-gating enable bit is set and the DAGB0 `DISABLE_*_CG` bits are clear.

Other field families in this chunk are not directly exercised by obvious local call sites in the sampled code, but remain part of the register ABI for diagnostics, bring-up, power management, and possible ASIC-specific paths.

## State and Persistence Behavior

The macros themselves have no runtime state and persist only as compile-time constants. The hardware registers they describe are persistent device state once written until reset, power-gating loss, firmware reinitialization, suspend/resume reprogramming, or another driver/firmware write changes them.

State described by this chunk includes:

- Per-client and per-virtual-channel arbitration configuration.
- Credit pools and outstanding-request limits.
- Clock-gating and light-sleep controls.
- Busy/pending/FIFO status snapshots.
- Performance-counter configuration and counter result fields.

Some fields are configuration fields intended to be written and retained. Others, such as `BUSY`, `EMPTY`, `FULL`, and performance-counter value fields, are status/result fields that should usually be read, not blindly written. Some counter-control fields (`CLEAR`, `CLEAR_ALL`, enable bits, start/stop triggers) are command/control state and may have side effects when toggled.

## Dependencies and Integration Points

This chunk depends on the AMDGPU register-access infrastructure but does not include it directly beyond being included by C files. Important integration pieces are:

- `mmhub_1_0_offset.h`: address definitions for the same register names.
- `mmhub_1_0_default.h`: reset/default values used by initialization code.
- `soc15.h` and `soc15_common.h`: SOC15 register address and read/write helpers.
- `amdgpu.h`, `amdgpu_ras.h`, `mmhub_v1_0.h`: device state and MMHub initialization interfaces.

The path belongs to the vendored or mirrored Linux AMDGPU source under `sources/distributed-fs/ceph-client/`, so consumers are kernel driver code, not Ceph client logic directly. The repository organization means research should stay source-tree-aligned under the AMDGPU/MMHub path rather than treating the file as distributed-filesystem business logic.

## Risks and Edge Cases

- Generated-header drift is the primary risk. Any mismatch between `mmhub_1_0_sh_mask.h`, `mmhub_1_0_offset.h`, and the hardware register specification can produce incorrect MMIO writes.
- The chunk boundary splits `DAGB1_RD_CNTL_MISC`. A merged report should not infer that only `STOR_POOL_CREDIT_MASK` exists for that register; the rest of the masks are in the next chunk.
- Per-client macro families are highly repetitive. Hand edits are risky because a single shifted field or mask typo can silently corrupt unrelated bits in a hardware register.
- Fields controlling credits, bandwidth windows, urgency, and outstanding request limits can affect memory-system forward progress and latency. Wrong values can cause hangs, underruns, excessive throttling, or unfair arbitration.
- Clock-gating disable bits use inverted semantics: setting `DISABLE_*_CG` disables clock gating, while clearing them permits it. This is easy to misuse in power-management changes.
- Busy/full/empty status fields are snapshots of live hardware state. Tests or diagnostics that poll them need timeouts and ASIC-specific sequencing knowledge.
- Performance-counter `CLEAR`, `CLEAR_ALL`, trigger, and saturation fields can perturb measurements if changed while counters are active.
- Reserved registers should remain reserved. Their full-width masks preserve generated layout but are not a license to program unknown state.

## Test Signals

Useful verification signals are mostly integration and hardware-observation based:

- Kernel build coverage for AMDGPU with MMHub 1.0 support verifies that macro names still match local consumers and field-helper conventions.
- Static checks can compare every covered `__SHIFT`/`_MASK` pair for non-overlap and expected bit width within each register family, especially repeated `RDCLI`, `WRCLI`, and `VC*_CNTL` groups.
- Bring-up logs should show MMHub initialization without VM faults, memory-controller hangs, or firmware/SMU clock-gating errors.
- Clock-gating tests should exercise `mmhub_v1_0_update_medium_grain_clock_gating()` and confirm that `mmhub_v1_0_get_clockgating()` reports `AMD_CG_SUPPORT_MC_MGCG` only when the DAGB disable masks are cleared.
- Suspend/resume and GPU reset tests should confirm that MMHub reinitialization restores stable DAGB state.
- Stress tests that drive GPU memory reads/writes, VM faults, UVD/VCE activity, and high concurrency are relevant because these fields sit in the MMHub request path.
- Performance-counter validation can program `DAGB0_PERFCOUNTER*_CFG` and `DAGB0_PERFCOUNTER_RSLT_CNTL`, generate known traffic, and verify nonzero/sane counter movement without saturation surprises.

### subset-b-002751: lines 2368-4742

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_0_sh_mask.h lines 2368-4742

## Scope

This chunk is part of the generated AMD MMHUB 1.0 register bitfield header. It contains C preprocessor constants only, using the normal AMDGPU generated-register convention:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

There are no functions, structs, variables, direct MMIO operations, branches, locking paths, or allocation paths in this range. The source is hardware ABI data: consumers pair these masks and shifts with address definitions from `mmhub_1_0_offset.h` and access helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15`.

The covered line range starts in the tail of `DAGB1_RD_CNTL_MISC`, then covers the `DAGB1` read/write arbitration and pending-state registers, and then enters the `mmhub_ea_mmeadec` address block for `MMEA0` DRAM/GMI/IO client grouping, priority, address-normalization, and address-decode registers. The chunk ends mid-register at `MMEA0_IO_WR_PRI_URGENCY_MASK__CID21_MASK_MASK`; later chunk reconciliation must merge the remaining CID masks from the following lines.

## Purpose

The constants in this range describe how MMHUB 1.0 hardware register fields are packed into 32-bit values. Driver code uses them to compose values written into MMHUB registers and to decode register values read back for clock gating, diagnostics, error collection, memory-address decoding, and memory-fabric arbitration.

The high-level hardware areas are:

- `DAGB1` data/address gather block fields for read/write client configuration, virtual-channel selection, urgency thresholds, bandwidth limits, credit accounting, clock gating, pending/busy state, debug delay selection, FIFO state, performance counters, and reserved scratch-like registers.
- `MMEA0` memory-mapping/address-decode fields for assigning client IDs to arbitration groups, mapping groups to virtual channels, tuning DRAM and IO priority algorithms, configuring normalized address ranges, DRAM holes, bank/channel/chip-select masks, hashing, harvesting, and chip-select decode tables.
- Status/counter-style fields such as pending masks, FIFO empty/full masks, credit fullness, and performance counter result controls.

This chunk does not implement MMHUB behavior by itself. Its effect is indirect: included C files use the symbolic field names when they program or inspect the MMHUB block.

## Important Macro Families

### DAGB1 Read/Write Client And Credit Controls

`DAGB1_RD_CNTL_MISC` and `DAGB1_WR_CNTL_MISC` define shared pool-credit and legacy coherency-control fields. The fields include storage pool credit, EA pool credit, IO-to-EA credit, storage/EA client-coherency legacy mode, and `UTCL2_CID`.

`DAGB1_RD_TLB_CREDIT` and `DAGB1_WR_TLB_CREDIT` split a register into six 5-bit TLB credit fields (`TLB0` through `TLB5`). These values bound MMHUB translation-side concurrency and are sensitive to deadlock and starvation tuning.

`DAGB1_WRCLI0` through `DAGB1_WRCLI15` repeat the same per-client layout: `VIRT_CHAN`, `CHECK_TLB_CREDIT`, high and low urgency thresholds, max/min bandwidth enable and value fields, OSD limiter enable, and max outstanding data. These define how each write client is routed and throttled. The repeated layout is regular, but the client indices are semantically distinct because hardware clients map to fixed CIDs.

`DAGB1_WR_CNTL`, `DAGB1_WR_GMI_CNTL`, `DAGB1_WR_ADDR_DAGB`, and `DAGB1_WR_DATA_DAGB` define aggregate write-path controls such as stalling, outstanding read/write client counts, urgent limits, GMI versus storage credit, buffer sizes, request size selection, bank-swizzle disable, virtual-channel enable, and LB/RTI buffers.

`DAGB1_WR_OUTPUT_DAGB_MAX_BURST`, `DAGB1_WR_OUTPUT_DAGB_LAZY_TIMER`, `DAGB1_WR_ADDR_DAGB_MAX_BURST[0-1]`, `DAGB1_WR_ADDR_DAGB_LAZY_TIMER[0-1]`, `DAGB1_WR_DATA_DAGB_MAX_BURST[0-1]`, and `DAGB1_WR_DATA_DAGB_LAZY_TIMER[0-1]` pack per-virtual-channel burst and lazy-timer limits. The recurring fields `VC0` through `VC7` are eight-bit or four-bit slices used to tune batching and flush behavior per virtual channel.

`DAGB1_WR_VC0_CNTL` through `DAGB1_WR_VC7_CNTL` repeat virtual-channel controls: storage credit, EA credit, max/min bandwidth enable and values, OSD limiter enable, and max OSD. These are group-level resource controls rather than per-client controls.

`DAGB1_WR_DATA_CREDIT` and `DAGB1_WR_MISC_CREDIT` add write-data and miscellaneous credit pools for deadlock virtual channels, burst categories, atomics, OSD, and OSD deadlock credits.

### DAGB1 Pending, Clock-Gating, Debug, And Perf State

`DAGB1_RDCLI_*_PENDING` and `DAGB1_WRCLI_*_PENDING` expose full-width `BUSY` masks for ask/go/global-send/TLB/OARB/OSD stages, plus DBUS ask/go pending masks on the write side. These are observational fields used to diagnose pipeline backlog or wait for quiescence.

`DAGB1_WR_CGTT_CLK_CTRL`, `DAGB1_L1TLB_WR_CGTT_CLK_CTRL`, and `DAGB1_ATCVM_WR_CGTT_CLK_CTRL` define clock-gating delay, hysteresis, light-sleep override, and soft override fields for write-side DAGB, L1 TLB, and ATCVM subblocks. In `mmhub_v1_0.c`, nearby `DAGB1_CNTL_MISC2` masks are used to enable and disable MMHUB clock-gating behavior, so this family is part of the same power-management register vocabulary.

`DAGB1_DAGB_DLY` selects debug delay, client, and position fields. `DAGB1_CNTL_MISC` and `DAGB1_CNTL_MISC2` provide EA virtual-channel remaps, EA/UTCL2 request forcing, FAW mode, L1 probe toggles, and disable bits for write/read request/return and TLB clock gating. `DAGB1_FIFO_EMPTY`, `DAGB1_FIFO_FULL`, `DAGB1_WR_CREDITS_FULL`, and `DAGB1_RD_CREDITS_FULL` are full-width status masks.

`DAGB1_PERFCOUNTER_LO`, `DAGB1_PERFCOUNTER_HI`, `DAGB1_PERFCOUNTER0_CFG`, `DAGB1_PERFCOUNTER1_CFG`, `DAGB1_PERFCOUNTER2_CFG`, and `DAGB1_PERFCOUNTER_RSLT_CNTL` define low/high counter data, event selection, event mode, client ID selection, and performance-result controls. `DAGB1_RESERVE0` through `DAGB1_RESERVE17` are full-width reserved data fields and should not be treated as stable feature controls without hardware documentation.

### MMEA0 DRAM Arbitration And Priority Controls

The `addressBlock: mmhub_ea_mmeadec` section begins with DRAM arbitration maps. `MMEA0_DRAM_RD_CLI2GRP_MAP0/1` and `MMEA0_DRAM_WR_CLI2GRP_MAP0/1` map CIDs 0-31 into four two-bit arbitration groups for DRAM reads and writes. `MMEA0_DRAM_RD_GRP2VC_MAP` and `MMEA0_DRAM_WR_GRP2VC_MAP` map the four groups to virtual channels.

`MMEA0_DRAM_RD_LAZY` and `MMEA0_DRAM_WR_LAZY` define per-group lazy delays. `MMEA0_DRAM_RD_CAM_CNTL` and `MMEA0_DRAM_WR_CAM_CNTL` define per-group CAM depths and reorder limits. `MMEA0_DRAM_PAGE_BURST` defines read/write page-burst limits.

`MMEA0_DRAM_RD_PRI_AGE`, `MMEA0_DRAM_WR_PRI_AGE`, `MMEA0_DRAM_RD_PRI_QUEUING`, `MMEA0_DRAM_WR_PRI_QUEUING`, `MMEA0_DRAM_RD_PRI_FIXED`, `MMEA0_DRAM_WR_PRI_FIXED`, `MMEA0_DRAM_RD_PRI_URGENCY`, and `MMEA0_DRAM_WR_PRI_URGENCY` describe the four-group priority algorithm: aging rate, age coefficient, queuing coefficient, fixed coefficient, urgency coefficient, and urgency mode. `MMEA0_DRAM_*_PRI_QUANT_PRI[1-3]` adds per-group priority thresholds.

These DRAM priority and grouping registers influence fairness and latency among MMHUB clients. Incorrect values can bias page traffic, IO traffic, or GMI traffic and can show up as bandwidth collapse, high latency, or starvation rather than as an obvious compile failure.

### MMEA0 Address Normalization And DRAM Decode

`MMEA0_ADDRNORM_BASE_ADDR0/1`, `MMEA0_ADDRNORM_LIMIT_ADDR0/1`, `MMEA0_ADDRNORM_OFFSET_ADDR1`, and `MMEA0_ADDRNORM_HOLE_CNTL` define address-range validity, legacy MMIO hole handling, channel/socket/die interleave settings, base/limit addresses, high-address offset, destination fabric ID, and DRAM hole offset.

`MMEA0_ADDRDEC_BANK_CFG` and `MMEA0_ADDRDEC_MISC_CFG` describe DRAM/GMI bank masks, bank-group selection, bank-group interleave, VCM enables, PCH/channel/chip-select/rank-module masks, and the GMI variants of those masks. These fields are address-layout critical: they define how physical/fabric addresses are decoded to memory topology.

`MMEA0_ADDRDECDRAM_ADDR_HASH_BANK0` through `BANK4`, `MMEA0_ADDRDECDRAM_ADDR_HASH_PC`, `MMEA0_ADDRDECDRAM_ADDR_HASH_PC2`, and `MMEA0_ADDRDECDRAM_ADDR_HASH_CS0/1` define XOR-enable and XOR-source fields for bank, pseudo-channel, and chip-select hashing. `MMEA0_ADDRDECDRAM_HARVEST_ENABLE` adds forced bank-harvest enable/value bits for banks 3 and 4.

`MMEA0_ADDRDEC0_*` and `MMEA0_ADDRDEC1_*` define two parallel address-decode table instances. Each instance contains base addresses for `CS0` through `CS3` and `SECCS0` through `SECCS3`, mask registers for CS pairs and secondary CS pairs, address configuration for CS01/CS23, address-selection registers for bank and row bits, low and high column-selection registers, and rank-module selection registers for primary and secondary chip selects. The repeated fields encode memory geometry: number of bank groups, rank modules, row-low bits, row-high bits, columns, banks, bank bit positions, column bit positions, rank-module bits, channel bit, and row-MSB inversion policy.

### MMEA0 IO Arbitration And Priority Controls

`MMEA0_IO_RD_CLI2GRP_MAP0/1` and `MMEA0_IO_WR_CLI2GRP_MAP0/1` mirror the DRAM CID-to-group mapping pattern for IO read and write clients. `MMEA0_IO_RD_COMBINE_FLUSH` and `MMEA0_IO_WR_COMBINE_FLUSH` define per-group combine-flush timers, while `MMEA0_IO_GROUP_BURST` defines read/write burst low/high limits.

`MMEA0_IO_RD_PRI_AGE`, `MMEA0_IO_WR_PRI_AGE`, `MMEA0_IO_RD_PRI_QUEUING`, `MMEA0_IO_WR_PRI_QUEUING`, `MMEA0_IO_RD_PRI_FIXED`, `MMEA0_IO_WR_PRI_FIXED`, `MMEA0_IO_RD_PRI_URGENCY`, and `MMEA0_IO_WR_PRI_URGENCY` define the same four-group priority components for IO traffic. `MMEA0_IO_RD_PRI_URGENCY_MASK` contains full CID0-CID31 one-bit masks, and this chunk contains the beginning of `MMEA0_IO_WR_PRI_URGENCY_MASK` through CID21. The trailing CID22-CID31 masks are outside this chunk and must be reconciled by the merge lane.

## Control Flow And State Behavior

This header has no local runtime control flow. Including C translation units receive constants at compile time. Runtime effects occur when AMDGPU code passes register values through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_ENTRY`.

Most fields describe persistent hardware configuration state. Once programmed, DAGB client routing, credit limits, burst timers, lazy timers, clock-gating settings, MMEA group maps, priority coefficients, normalized address ranges, address hashing, and chip-select decode tables remain in MMHUB registers until changed by initialization, reset, suspend/resume restore, firmware, or hardware power-state transitions.

Several fields are observational state rather than configuration: pending masks, FIFO empty/full state, credit-full state, performance counter results, and performance counter high/low data. These fields are read to infer MMHUB activity, debug routing, or collect counters.

Some fields are command-like or latch-like in practice even though this header only defines bit positions. Examples include performance counter result control fields, clock-gating soft override bits, delay/debug selectors, and force/harvest controls. Consumers must preserve reserved bits where required by the hardware register contract, especially for read-modify-write sequences.

The header itself stores no state and performs no persistence. Persistence lives in MMHUB hardware registers, GPU reset/save-restore flows, and driver code that reprograms the MMHUB during init/resume/reset.

## Dependencies And Integration Points

This chunk depends on the generated AMD MMHUB register-header set:

- `mmhub_1_0_offset.h` supplies the matching `mmDAGB1_*` and `mmMMEA0_*` register addresses.
- `mmhub_1_0_default.h` supplies default register values where generated defaults exist.
- `mmhub_1_0_sh_mask.h` supplies the field masks and shifts described here.

Direct include sites for `mmhub/mmhub_1_0_sh_mask.h` in this source tree include:

- `drivers/gpu/drm/amd/amdgpu/mmhub_v1_0.c`
- `drivers/gpu/drm/amd/amdgpu/uvd_v7_0.c`
- `drivers/gpu/drm/amd/amdgpu/vce_v4_0.c`
- `drivers/gpu/drm/amd/display/dc/resource/dce120/dce120_resource.c`

`mmhub_v1_0.c` is the main integration point. It initializes MMHUB virtual memory apertures, page-table base registers, TLB/L2/cache behavior, protection-fault controls, invalidation ranges, and clock-gating behavior with SOC15 accessors. It uses nearby generated MMHUB field definitions through `REG_SET_FIELD`, `REG_GET_FIELD`, and direct masks. In the clock-gating path it reads and writes `mmDAGB1_CNTL_MISC2` and toggles `DAGB1_CNTL_MISC2__DISABLE_*_CG_MASK` bits, which are in the same `DAGB1` control family as this chunk's write/read client and clock-gating fields.

The MMEA0 address-decode and arbitration macros also sit near RAS and error-counter integration. `mmhub_v1_0.c` defines MMHUB EDC counter table entries using `SOC15_REG_ENTRY` and `SOC15_REG_FIELD` for `MMEA0_EDC_CNT*_VG20` fields outside this chunk. That makes the `MMEA0` namespace part of both memory-routing setup and reliability/error-reporting paths.

The UVD, VCE, and display include sites share the same MMHUB field vocabulary for media/display blocks that need to program or interpret MMHUB-related register fields on MMHUB 1.0 ASICs.

## Risks And Edge Cases

- Bitfield drift is high impact. A wrong mask or shift can silently program the wrong MMHUB bits, changing memory routing, virtual-channel assignment, priority arbitration, credit limits, or address decoding.
- Repeated register families are easy to copy incorrectly. `DAGB1_WRCLI0-15`, `DAGB1_WR_VC0-7_CNTL`, DRAM/IO `CLI2GRP_MAP0/1`, `ADDRDEC0/1`, and CS01/CS23/SECCS variants have regular layouts but are not interchangeable.
- Address-decode fields are memory-topology critical. Incorrect `ADDRNORM`, `ADDRDEC_BANK_CFG`, hashing, chip-select base/mask/config/select, column select, rank-module select, or harvest bits can lead to wrong physical memory targeting and data corruption.
- Arbitration fields can fail as performance bugs. Bad CID-to-group maps, group-to-VC maps, urgency masks, priority coefficients, lazy timers, combine flush timers, or burst limits may appear as latency spikes, starvation, or bandwidth collapse rather than immediate faults.
- Credit fields are deadlock-sensitive. Incorrect TLB, storage, EA, OSD, atomic, or burst credits can overcommit queues or stall clients permanently.
- Status and pending masks are full-width. Consumers should treat them as unsigned 32-bit values; sign extension from `0x80000000L`-style masks or host-width assumptions can corrupt diagnostics.
- Reserved fields and `DAGB1_RESERVE*` registers should not be reinterpreted as software feature flags. Generated names describe register layout, not necessarily safe writable behavior.
- The chunk boundary is mid-register. `MMEA0_IO_WR_PRI_URGENCY_MASK` is incomplete in this document's source range; whole-file research must merge the following chunk before presenting that register as complete.

## Test And Validation Signals

There are no direct unit tests for this macro-only chunk. Useful validation is integration-level and hardware-facing:

- Build AMDGPU, display, UVD, and VCE code that includes `mmhub_1_0_sh_mask.h`; this catches missing, renamed, or syntactically broken macros.
- Static mask/shift consistency checks can verify that contiguous masks shift down to dense fields, single-bit masks match their bit index, full-width masks use shift zero, and repeated register families keep consistent layouts.
- Exercise MMHUB 1.0 initialization, suspend/resume, GPU reset, SR-IOV paths, and clock-gating enable/disable flows in `mmhub_v1_0.c`, especially paths that read-modify-write DAGB clock-gating and VM/MMHUB registers.
- Run VM/GART and memory stress tests that cover system aperture, VRAM aperture, page-table setup, invalidations, protection faults, media/display clients, and concurrent read/write pressure through MMHUB.
- Validate bandwidth and latency under DRAM, GMI, and IO traffic mixes to catch arbitration misconfiguration in CID group maps, virtual-channel maps, priority coefficients, urgency masks, lazy timers, and burst limits.
- Compare register dumps against known-good firmware/ASIC programming for `DAGB1_*` and `MMEA0_*` registers after boot, resume, and reset.
- Exercise RAS/EDC and MMHUB diagnostic flows where available, confirming that MMEA/DAGB counters and status fields decode correctly and do not report impossible client or group states.

## Chunk Notes For Merge Lane

This is a partial range of a larger generated register header. The final per-file document should treat it as the MMHUB 1.0 `DAGB1` arbitration/control plus early `MMEA0` memory-address-decode/arbitration section. It should merge with adjacent chunks for the full `DAGB1_RD_*` setup before line 2368 and the remainder of `MMEA0_IO_WR_PRI_URGENCY_MASK` plus later MMEA0 registers after line 4742.

### subset-b-002752: lines 4743-7093

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_0_sh_mask.h lines 4743-7093

## Scope

This chunk covers generated shift and mask macros from the AMD MMHUB 1.0 register mask header. It starts in the tail of `MMEA0_IO_WR_PRI_URGENCY_MASK`, covering only the `CID22` through `CID31` mask values, and then covers the rest of the visible `MMEA0` memory-export/arbitration support fields through `MMEA0_MISC2`. It then enters a large `MMEA1` section covering DRAM client grouping, DRAM and IO priority/arbitration, address normalization and address decoding, SDP arbitration/crediting, latency sampling, performance counters, EDC counters, and the beginning of DSM/error-injection control.

The file is a generated-style C preprocessor hardware ABI map. This chunk defines constants only. There are no functions, structs, storage objects, direct register accesses, loops, conditionals, or local runtime control flow in the covered lines.

## Purpose

The purpose of this section is to provide bit-level field metadata for MMHUB 1.0 registers. Each register field is represented by the conventional pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset of the field.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit mask used to isolate or compose the field.

AMDGPU code consumes these macros through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, and `WREG32_FIELD`, which paste together `reg##__##field##__SHIFT` and `reg##__##field##_MASK`. The sibling `mmhub_1_0_offset.h` header supplies the actual register addresses, for example `mmMMEA0_EDC_MODE`, `mmMMEA1_ADDRNORM_BASE_ADDR0`, and `mmMMEA1_IO_RD_PRI_URGENCY_MASK`; this file supplies the field packing for values written to or read from those addresses.

## Important Macro Families

### MMEA0 tail: IO urgency, SDP arbitration, diagnostics, and EDC/DSM controls

The opening lines are a partial continuation of `MMEA0_IO_WR_PRI_URGENCY_MASK`, defining one-bit masks for `CID22` through `CID31`. The matching shift definitions and lower client masks are in the previous chunk, so any merged report should treat this as an incomplete register family unless combined with earlier lines.

`MMEA0_IO_RD_PRI_QUANT_PRI1` through `MMEA0_IO_WR_PRI_QUANT_PRI3` define four 8-bit threshold fields per register, repeated for read and write IO arbitration priority quantum settings. These values describe priority thresholds for four client groups across three priority registers.

`MMEA0_SDP_ARB_DRAM` and `MMEA0_SDP_ARB_FINAL` define burst limits, early switch behavior, read-only virtual-channel flags, and error reaction flags such as `ERREVENT_ON_ERROR` and `HALTREQ_ON_ERROR`. These fields describe how MMHUB's SDP path arbitrates DRAM, GMI, and IO traffic and how the final arbiter reacts to hardware error conditions.

`MMEA0_SDP_DRAM_PRIORITY` and `MMEA0_SDP_IO_PRIORITY` pack four read group priorities and four write group priorities into 4-bit fields. `MMEA0_SDP_CREDITS`, `MMEA0_SDP_TAG_RESERVE0/1`, `MMEA0_SDP_VCC_RESERVE0/1`, and `MMEA0_SDP_VCD_RESERVE0/1` define tag/response limits and virtual-channel credit reservations. These registers are stateful hardware throttling contracts: incorrect values can alter request progress, fairness, or deadlock margins.

`MMEA0_SDP_REQ_CNTL` defines request override bits for read, write, atomic, DRAM chain behavior, and inner-domain mode. `MMEA0_MISC` and `MMEA0_MISC2` contain arbitration policy bits for relative priority, return swap mode, early SDP original data, link-manager dynamic mode and thresholds, chip-select favoring, read/write switching, chip-select group swapping, and burst limits.

`MMEA0_LATENCY_SAMPLING` selects two latency samplers across DRAM/GMI/IO, read/write/atomic traffic, and VC fields. `MMEA0_PERFCOUNTER_LO`, `MMEA0_PERFCOUNTER_HI`, `MMEA0_PERFCOUNTER0_CFG`, `MMEA0_PERFCOUNTER1_CFG`, and `MMEA0_PERFCOUNTER_RSLT_CNTL` define performance counter data, compare values, event selectors, modes, enable/clear bits, start/stop triggers, and stop-on-saturation control.

`MMEA0_EDC_CNT` and `MMEA0_EDC_CNT2` expose compact SEC/DED/SED count fields for DRAM read/write command memory, data memory, page memory, IO command/data memory, return tag memory, and GMI paths. `MMEA0_EDC_MODE` defines fault-counting and propagation policy bits such as `COUNT_FED_OUT`, `GATE_FUE`, `DED_MODE`, `PROP_FED`, and `BYPASS`. `MMEA0_ERR_STATUS` exposes SDP read/write response status, read-response data-parity error, clear status, and busy-on-error fields.

`MMEA0_DSM_CNTL`, `MMEA0_DSM_CNTLA`, `MMEA0_DSM_CNTL2`, and `MMEA0_DSM_CNTL2A` are diagnostic/self-test/error-injection controls. They define DSM irritator data, single-write enables, error-injection enables, delay selection bits, and a shared inject delay. `MMEA0_DSM_CNTLB` and `MMEA0_DSM_CNTL2B` appear as comments without field definitions in this span.

`MMEA0_CGTT_CLK_CTRL` defines clock-gating/test controls such as on delay, off hysteresis, soft stall override, light-sleep override, and soft override bits for write, read, return, and register paths.

### MMEA1 DRAM client grouping and DRAM arbitration

The `MMEA1_DRAM_RD_CLI2GRP_MAP0/1` and `MMEA1_DRAM_WR_CLI2GRP_MAP0/1` families map client IDs `CID0` through `CID31` into two-bit group fields for DRAM read and write traffic. `MAP0` covers clients 0-15 and `MAP1` covers clients 16-31. These mappings feed the later group-priority, aging, queueing, fixed-priority, urgency, and quantum controls.

`MMEA1_DRAM_RD_GRP2VC_MAP` and `MMEA1_DRAM_WR_GRP2VC_MAP` map four groups to two-bit virtual-channel identifiers. `MMEA1_DRAM_RD_LAZY` and `MMEA1_DRAM_WR_LAZY` define lazy timer and combined-write/lazy timer fields. `MMEA1_DRAM_RD_CAM_CNTL` and `MMEA1_DRAM_WR_CAM_CNTL` define high/low watermarks, warning watermarks, and high-priority write request thresholds for CAM control. `MMEA1_DRAM_PAGE_BURST` holds read and write page-burst controls.

`MMEA1_DRAM_RD_PRI_AGE`, `MMEA1_DRAM_WR_PRI_AGE`, `MMEA1_DRAM_RD_PRI_QUEUING`, `MMEA1_DRAM_WR_PRI_QUEUING`, `MMEA1_DRAM_RD_PRI_FIXED`, `MMEA1_DRAM_WR_PRI_FIXED`, `MMEA1_DRAM_RD_PRI_URGENCY`, and `MMEA1_DRAM_WR_PRI_URGENCY` define four-group priority coefficients. The urgency registers add per-group urgency mode bits. `MMEA1_DRAM_RD_PRI_QUANT_PRI1/2/3` and `MMEA1_DRAM_WR_PRI_QUANT_PRI1/2/3` define 8-bit quantum thresholds for the same four groups.

### MMEA1 address normalization and address decoding

`MMEA1_ADDRNORM_BASE_ADDR0/1` and `MMEA1_ADDRNORM_LIMIT_ADDR0/1` define address range validity, legacy MMIO hole enable, interleave channel selection, base address, destination fabric ID, socket/die interleave fields, and limit address fields. `MMEA1_ADDRNORM_OFFSET_ADDR1` and `MMEA1_ADDRNORM_HOLE_CNTL` provide high-address offset and DRAM-hole controls.

`MMEA1_ADDRDEC_BANK_CFG` and `MMEA1_ADDRDEC_MISC_CFG` define DRAM/GMI bank masks, bank-group selection, bank-group interleave, VCM enables, pseudo-channel/channel/chip-select/rank masks, and related DRAM/GMI selection fields. The address hash registers `MMEA1_ADDRDECDRAM_ADDR_HASH_BANK0` through `BANK4`, `PC`, `PC2`, `CS0`, and `CS1` define XOR-enable and column/row/NA/bank XOR masks. `MMEA1_ADDRDECDRAM_HARVEST_ENABLE` exposes force-enable/value bits for harvested bank bits.

`MMEA1_ADDRDEC0_*` and `MMEA1_ADDRDEC1_*` repeat two address-decoder instances. Each instance includes base address registers for `CS0` through `CS3` and `SECCS0` through `SECCS3`, address masks for chip-select pairs, geometry config fields for bank groups/rank maps/rows/columns/banks, bank/row bit selectors, low and high column selectors, and rank-map selectors. These macros are especially sensitive because they encode physical memory layout and chip-select decode behavior.

### MMEA1 IO arbitration and urgency masks

`MMEA1_IO_RD_CLI2GRP_MAP0/1` and `MMEA1_IO_WR_CLI2GRP_MAP0/1` mirror the DRAM client-to-group maps for IO read and write traffic. `MMEA1_IO_RD_COMBINE_FLUSH`, `MMEA1_IO_WR_COMBINE_FLUSH`, and `MMEA1_IO_GROUP_BURST` define flush and burst thresholds for grouped IO behavior.

`MMEA1_IO_RD_PRI_AGE`, `MMEA1_IO_WR_PRI_AGE`, queueing, fixed-priority, and urgency registers repeat the four-group coefficient layout for IO. `MMEA1_IO_RD_PRI_URGENCY_MASK` and `MMEA1_IO_WR_PRI_URGENCY_MASK` define one-bit masks for all 32 client IDs. These are full 32-bit client bitmaps; the macro naming produces fields like `CID17_MASK_MASK` because the hardware field name itself ends in `_MASK`.

`MMEA1_IO_RD_PRI_QUANT_PRI1/2/3` and `MMEA1_IO_WR_PRI_QUANT_PRI1/2/3` define the 8-bit group quantum thresholds for IO read and write arbitration.

### MMEA1 SDP, performance, EDC, and DSM controls

`MMEA1_SDP_ARB_DRAM`, `MMEA1_SDP_ARB_FINAL`, `MMEA1_SDP_DRAM_PRIORITY`, `MMEA1_SDP_IO_PRIORITY`, `MMEA1_SDP_CREDITS`, tag reserve, VCC/VCD reserve, `MMEA1_SDP_REQ_CNTL`, `MMEA1_MISC`, and `MMEA1_MISC2` repeat the same SDP arbitration, virtual-channel crediting, request override, link-manager, and chip-select group policy found in the MMEA0 tail.

`MMEA1_LATENCY_SAMPLING`, `MMEA1_PERFCOUNTER_LO/HI`, `MMEA1_PERFCOUNTER0_CFG`, `MMEA1_PERFCOUNTER1_CFG`, and `MMEA1_PERFCOUNTER_RSLT_CNTL` define the second MMEA block's latency sampler and performance counter register fields.

`MMEA1_EDC_CNT` and `MMEA1_EDC_CNT2` expose the same SEC/DED/SED counter layout for DRAM, IO, GMI, and tag/page memories. `MMEA1_DSM_CNTL` defines DSM irritator data and single-write enable fields for command/data/tag/GMI memories. The chunk ends partway through `MMEA1_DSM_CNTLA`; only the initial DRAM page memory, IO command/data memory, and GMI page memory shift definitions plus the first few masks through `IOWR_CMDMEM_DSM_IRRITATOR_DATA_MASK` are present. The rest of `MMEA1_DSM_CNTLA` and later DSM/error-injection registers are cross-chunk references.

## APIs, Types, and Functions

This chunk exports preprocessor macros only. There are no C types or functions.

The effective API is the generated naming contract used by register helpers:

- `REG_FIELD_SHIFT(reg, field)` expands to `reg__field__SHIFT`.
- `REG_FIELD_MASK(reg, field)` expands to `reg__field_MASK`.
- `REG_SET_FIELD(orig_val, reg, field, field_val)` clears `reg__field_MASK` in `orig_val`, shifts `field_val` by `reg__field__SHIFT`, masks it, and ORs it into the result.
- `REG_GET_FIELD(value, reg, field)` masks and right-shifts a packed register value.

That means macro spelling is ABI-significant. A register rename, field rename, missing shift, or missing mask breaks compile-time token pasting in consumers.

## Control Flow

There is no executable control flow in this header chunk. Runtime behavior emerges only in the C files that include it, read or compose register values, and write those values through MMIO helpers such as `RREG32_SOC15` and `WREG32_SOC15`.

The hardware-level sequencing implied by this chunk includes:

- Programming address normalization and address decode fields before memory traffic relies on those ranges.
- Programming client group maps before relying on group-based DRAM/IO priority policy.
- Programming credit/reserve/priority/urgency/quantum fields before enabling or tuning arbitration.
- Enabling, clearing, starting, stopping, and reading performance counters through the cfg/result-control/counter fields.
- Reading EDC and error-status fields after hardware has accumulated fault state, and writing clear/status or injection-related controls only in diagnostic paths.

## State and Persistence Behavior

The macros themselves have no storage and do not persist anything. The state they describe lives in MMHUB hardware registers. Register values are generally persistent until changed by the driver, hardware reset, power-gating/reset sequencing, firmware, or ASIC-specific initialization.

Important state categories represented here are:

- Arbitration and QoS state: group maps, virtual-channel maps, age/queue/fixed/urgency coefficients, priority quantum thresholds, SDP burst limits, and credit reservations.
- Memory topology state: address normalization ranges, holes, interleave fields, bank masks, chip-select base/mask/config/selector fields, column selectors, rank-map selectors, and hash/harvest settings.
- Performance/debug state: latency sampler selectors, counter event/mode/enable/clear fields, result-control start/stop triggers, and counter result fields.
- Reliability/error state: EDC counters, EDC mode, error-status fields, DSM irritator data, single-write enables, and error-injection controls.
- Clock/test override state: clock-gating delay/hysteresis and soft override fields.

Many fields are configuration fields, but some are command or latch-like controls, such as counter clear bits, result control clear/start/stop bits, error status clear bits, and error-injection enables. Consumers must account for hardware side effects when setting them.

## Dependencies and Integration Points

This header is included by MMHUB and related AMDGPU source files, including `amdgpu/mmhub_v1_0.c`, `amdgpu/uvd_v7_0.c`, `amdgpu/vce_v4_0.c`, and display resource code for DCE 12. It is paired with:

- `mmhub/mmhub_1_0_offset.h`, which defines register address macros such as `mmMMEA0_EDC_MODE`, `mmMMEA1_ADDRNORM_BASE_ADDR0`, and `mmMMEA1_IO_RD_PRI_URGENCY_MASK`.
- `mmhub/mmhub_1_0_default.h`, which provides default register values for the same generation.
- `amdgpu/amdgpu.h`, which defines `REG_FIELD_SHIFT`, `REG_FIELD_MASK`, `REG_SET_FIELD`, `REG_GET_FIELD`, and register write/read helper wrappers.
- SOC15 register helpers in AMDGPU code that combine IP block, instance, address macro, and packed value.

The chunk also aligns with later-generation MMHUB mask headers such as `mmhub_1_7_sh_mask.h`, `mmhub_2_0_0_sh_mask.h`, and `mmhub_9_4_1_sh_mask.h`. Those headers preserve many family names but may move fields or rename registers, so code must include the mask header matching the active ASIC generation.

## Risks and Edge Cases

- Bitfield correctness is critical. A wrong shift or mask silently writes the wrong hardware bits, potentially corrupting memory decode, arbitration policy, performance counters, or error handling.
- Address-decoder fields are high risk. Errors in base, mask, selector, row/column, rank-map, hash, or interleave fields can misroute memory requests or create GPU hangs and data corruption.
- QoS and credit fields are performance and forward-progress sensitive. Bad group mappings, urgency masks, credit reservations, or burst limits can starve clients, disturb virtual-channel fairness, or create difficult-to-debug latency spikes.
- Error/DSM fields are hazardous outside diagnostics. Accidentally enabling error injection, DSM irritator data, or single-write modes can produce artificial memory errors or alter fault reporting.
- The chunk contains partial register families at both ends: `MMEA0_IO_WR_PRI_URGENCY_MASK` begins before line 4743, and `MMEA1_DSM_CNTLA` continues after line 7093. Any whole-file synthesis must merge adjacent chunks to avoid treating these partial definitions as complete.
- Field names ending in `_MASK` produce macro names ending in `_MASK_MASK`, for example `MMEA1_IO_RD_PRI_URGENCY_MASK__CID0_MASK_MASK`. This is intentional under the generated naming scheme and should not be mechanically simplified.
- Signedness and width matter. Constants use `L` suffixes and 32-bit masks; consumers should use unsigned 32-bit register values and avoid shifting unbounded field values without the mask applied.
- Generation drift matters. Similar field families in newer MMHUB headers may have different shifts, masks, or register names, such as urgency masking naming in later versions. Copying values across ASIC generations is unsafe.

## Test Signals

Useful validation signals for this chunk are mostly build-time, boot-time, and hardware-behavioral:

- Compile coverage of files including `mmhub_1_0_sh_mask.h`; missing or misspelled macros fail where `REG_SET_FIELD` or `REG_GET_FIELD` token-pastes register and field names.
- Static consistency checks can verify every covered field has both a `__SHIFT` and `_MASK`, that masks match the declared shift/width pattern, and that fields within one register do not overlap unless intentionally aliased.
- Header-pair consistency checks can confirm registers referenced in this chunk have corresponding addresses in `mmhub_1_0_offset.h` and defaults where expected in `mmhub_1_0_default.h`.
- GPU initialization and resume tests should cover MMHUB programming paths, especially memory aperture setup, page-table/GART access, UVD/VCE/display use of MMHUB registers, and VM fault-free operation.
- Memory stress and display/video workloads are useful runtime signals for address normalization, address decoding, and arbitration correctness.
- Performance counter smoke tests should confirm `MMEA0/MMEA1_PERFCOUNTER*_CFG`, result-control, and counter result fields can be programmed, cleared, enabled, and read without hangs.
- RAS/ECC diagnostic tests, where supported by the hardware and test environment, should verify EDC counter reads, error-status clear behavior, and that error-injection controls are not enabled in normal initialization paths.
- Register readback tests can compare programmed values against expected packed values built from the same masks and shifts, especially for high-risk address-decoder and priority/credit registers.

## Unresolved Cross-Chunk References

- The lower part and shift definitions for `MMEA0_IO_WR_PRI_URGENCY_MASK` are in the previous chunk.
- The remaining masks for `MMEA1_DSM_CNTLA`, plus likely `MMEA1_DSM_CNTLB`, `MMEA1_DSM_CNTL2`, and later MMEA1 reliability/control fields, are in the next chunk.
- Whole-file research should reconcile this chunk with adjacent chunks to determine the full MMEA0/MMEA1 register coverage and to avoid double-counting repeated MMEA0/MMEA1 macro families.

### subset-b-002753: lines 7094-9528

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_0_sh_mask.h lines 7094-9528

## Scope And Purpose

This chunk is a generated-style MMHUB 1.0 register bitfield header for AMDGPU. It contains preprocessor constants only: each hardware register field is represented as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. There are no C functions, structs, storage objects, or executable branches in this source range.

The range covers the middle of the MMHUB 1.0 mask namespace. It starts inside the `MMEA1_DSM_CNTLA`/DSM error-injection area, then defines power/control, L1 TLB, ATC L2, VM L2 fault/cache, VM context, TLB invalidation-engine, and page-table-address register fields. These constants are the hardware contract used by AMDGPU code to program MMHUB MMIO registers through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_SOC15_OFFSET`.

The chunk is source-tree-aligned to the MMHUB 1.0 ASIC headers. It is paired with `mmhub_1_0_offset.h` for register addresses and `mmhub_1_0_default.h` for reset/default values.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the macro namespace:

- `MMEA1_DSM_CNTL2`, `MMEA1_DSM_CNTL2A`, and tail `MMEA1_DSM_CNTLA` masks describe DSM error injection and single-write/irritator controls for DRAM, RRET/WRET, GMI, and IO command/data/page memories. `MMEA1_CGTT_CLK_CTRL`, `MMEA1_EDC_MODE`, `MMEA1_ERR_STATUS`, and `MMEA1_MISC2` define clock-gating override, error-detection/correction mode, SDP response error status, and arbitration/burst-limit fields for the second memory-mapped engine instance.
- `PCTL_MISC`, `PCTL_MMHUB_DEEPSLEEP`, `PCTL_MMHUB_DEEPSLEEP_OVERRIDE`, `PCTL_PG_IGNORE_DEEPSLEEP`, and `PCTL_PG_DAGB` define MMHUB power-control/deepsleep and power-gating fields, including RSMU/DAGB idle thresholds, protection-fault ignore controls, deep-sleep bitsets `DS0` through `DS16`, and `SETCLEAR` semantics.
- `PCTL[0-2]_RENG_*`, `PCTL[0-2]_MISC`, and `PCTL[0-2]_STCTRL_REGISTER_SAVE_*` define three repeated power-controller register-engine banks. These cover RAM index/data accesses, execute controls (`EXECUTE_ON_PWR_UP`, `EXECUTE_ON_PWR_DOWN`, restart, busy, and program counter), replay/debug options, and register save/restore ranges or exclusion sets.
- `MC_VM_MX_L1_TLB[0-7]_STATUS` and `MC_VM_MX_L1_PERFCOUNTER*` define L1 TLB hit/miss status and event-counter controls/results. The status fields distinguish CAM and FIFO hits/misses; the counter config fields expose `PERF_MODE` and `PERF_SEL`.
- `ATC_L2_CNTL`, `ATC_L2_CNTL2`, `ATC_L2_CACHE_DATA*`, `ATC_L2_CNTL3`, `ATC_L2_STATUS*`, `ATC_L2_MISC_CG`, `ATC_L2_MEM_POWER_LS`, and `ATC_L2_CGTT_CLK_CTRL` define address-translation-cache L2 request counts, cache update behavior, VMID modes, cache data readout, busy/invalidation status, memory power, and clock-gating controls.
- `VM_L2_CNTL`, `VM_L2_CNTL2`, `VM_L2_CNTL3`, `VM_L2_CNTL4`, `VM_L2_STATUS`, and `VM_L2_CACHE_PARITY_CNTL` define MMHUB virtual-memory L2 cache enablement, fragment handling, endian/swap modes, LRU/update behavior, invalidation controls, bank select, effective sizes, force-miss bits, tap/snoop behavior, parity/interrupt behavior, and status bits.
- `VM_DUMMY_PAGE_FAULT_*`, `VM_L2_PROTECTION_FAULT_*`, `VM_L2_CONTEXT1_IDENTITY_APERTURE_*`, and `VM_L2_CONTEXT_IDENTITY_PHYSICAL_OFFSET_*` define how L2 VM faults are redirected, logged, interrupted, decoded, and optionally translated through identity apertures. Important decoded fault-status fields include `MORE_FAULTS`, `WALKER_ERROR`, `PERMISSION_FAULTS`, `MAPPING_ERROR`, `CID`, `RW`, `ATOMIC`, `VMID`, `VF`, and `VFID`.
- `VM_CONTEXT0_CNTL` through `VM_CONTEXT15_CNTL` define per-VMID context enable, page-table depth/block size, retry policy, and default/interrupt responses for range, dummy-page, PDE0, valid, read, write, and execute protection faults. `VM_CONTEXTS_DISABLE` supplies the per-context disable bitmap.
- `VM_INVALIDATE_ENG[0-17]_{SEM,REQ,ACK}` and `VM_INVALIDATE_ENG[0-17]_ADDR_RANGE_{LO32,HI32}` define 18 repeated invalidation engines. Request fields select VMIDs, flush type, L2 PTE/PDE invalidation, L1 PTE invalidation, and whether to clear the protection-fault status address; ACK fields report per-VMID completion.
- `VM_CONTEXT[0-15]_PAGE_TABLE_BASE_ADDR_{LO32,HI32}` and `VM_CONTEXT[0-15]_PAGE_TABLE_START_ADDR_{LO32,HI32}` define the low/high halves for page-directory entries and logical start page numbers. The chunk ends at the first fields for `VM_CONTEXT2_PAGE_TABLE_END_ADDR_HI32`; later context end-address definitions continue in the next chunk.

## Control Flow And State Behavior

This header chunk has no local runtime control flow. Runtime behavior appears in consumers that combine these bitfield constants with register offsets:

- `amdgpu/mmhub_v1_0.c` initializes MMHUB 1.0 GART and VM state. It writes `VM_CONTEXT0_PAGE_TABLE_BASE_ADDR_*`, `VM_CONTEXT0_PAGE_TABLE_START_ADDR_*`, and `VM_CONTEXT0_PAGE_TABLE_END_ADDR_*` for VMID0, programs `VM_CONTEXT1_CNTL` and page-table aperture registers for user VMIDs, enables `VM_L2_CNTL`/`VM_L2_CNTL2`/`VM_L2_CNTL3`/`VM_L2_CNTL4`, and configures invalidation-engine address ranges.
- `amdgpu/mmhub_v1_0.c` also uses the protection-fault masks in this chunk to set the dummy/default fault page and to toggle whether range/PDE/dummy/valid/read/write/execute faults are redirected to the default page or made crash-worthy.
- `amdgpu/gmc_v9_0.c` uses `VM_L2_PROTECTION_FAULT_STATUS` field masks to decode page-fault status into client ID, read/write direction, permission/mapping/walker bits, and fault metadata for logging and fault-cache updates.
- `amdgpu/gmc_v9_0.c` forms invalidation requests with `VM_INVALIDATE_ENG0_REQ` masks: it selects the target VMID bit, flush type, L2 PTE/PDE invalidations, L1 PTE invalidation, and the clear-fault-status-address bit. Hardware then reports completion through the corresponding ACK register fields.
- `amdgpu/amdgpu_gmc.h` includes mode2 save/restore storage for many registers represented here, including `VM_L2_CNTL`, `VM_L2_CNTL2`, dummy fault registers, L2 protection fault registers, `VM_CONTEXT_CNTL[16]`, context page-table base/start/end arrays, and `MC_VM_MX_L1_TLB_CNTL`.

The state described by these macros is persistent only as GPU register state. The header does not store state, serialize access, or enforce ordering. Driver code must sequence MMIO writes around GPU reset, GART enable/disable, VMID setup, page-table updates, TLB invalidation, power management, and interrupt handling.

## Dependencies And Integration Points

This chunk depends on the larger AMDGPU register-description scheme:

- `mmhub/mmhub_1_0_offset.h` supplies `mm*` register offsets, for example `mmVM_L2_CNTL`, `mmVM_CONTEXT0_CNTL`, `mmVM_INVALIDATE_ENG0_REQ`, and `mmVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32`.
- `mmhub/mmhub_1_0_default.h` supplies default values such as `mmVM_L2_CNTL_DEFAULT`, `mmVM_L2_CNTL3_DEFAULT`, `mmVM_CONTEXT0_CNTL_DEFAULT`, and `mmVM_INVALIDATE_ENG0_REQ_DEFAULT`.
- SOC15 access helpers (`RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, and offset variants) provide MMIO reads/writes against these registers.
- `REG_SET_FIELD` and `REG_GET_FIELD` expect the exact `<REGISTER>__<FIELD>_MASK` and `<REGISTER>__<FIELD>__SHIFT` naming used in this header. Renaming a field or changing the register prefix breaks table-free field access at compile time.
- VM hub setup in `mmhub_v1_0.c`, later MMHUB revisions such as `mmhub_v1_7.c`/`mmhub_v1_8.c`, and common GMC code in `gmc_v9_0.c` rely on these masks to keep MMHUB programming aligned with hardware layouts.
- Power-management code can use the PCTL, deepsleep, ATC, and clock-gating masks when enabling MMHUB clock/power gating. The chunk's PCTL save/restore ranges are especially relevant to power-gated register preservation.

The repeated register layout also defines software assumptions about register spacing. `mmhub_v1_0_init()` computes distances between `VM_CONTEXT0` and `VM_CONTEXT1` registers and between invalidation engines; code then uses those distances to program repeated contexts/engines with `WREG32_SOC15_OFFSET`.

## Risks And Edge Cases

- Hardware contract drift is the primary risk. A wrong shift or mask can direct page-table base writes to the wrong bits, leave VM fault handling disabled, fail to invalidate stale translations, or corrupt power-control state.
- The chunk contains many repeated register families. Copy/paste or generation errors can affect only one VM context, invalidation engine, or PCTL bank while the rest look correct. Static checks should compare repeated groups for expected sameness and spacing.
- Some fields span the full register (`0xFFFFFFFFL`) while others use high bits with an `L` suffix. Consumers should use unsigned 32-bit values when shifting/masking to avoid sign-extension and host-width surprises.
- VM fault handling is safety-critical. Misprogramming `VM_L2_PROTECTION_FAULT_CNTL`, `VM_L2_PROTECTION_FAULT_CNTL2`, or `VM_CONTEXT*_CNTL` can change whether faults are retried, redirected to a dummy/default page, logged, interrupted, or escalated to GPU reset/hang paths.
- Invalidation request fields are synchronization-critical. Omitting `INVALIDATE_L2_PTES`, `INVALIDATE_L2_PDE*`, or `INVALIDATE_L1_PTES`, selecting the wrong VMID bit, or polling the wrong ACK mask can leave stale translations active after page-table updates.
- Page-table base/start/end fields are split across LO32 and HI32 registers and encode page numbers rather than raw byte addresses in consumers. Callers must preserve the driver convention of shifting addresses to the correct page granularity before writing.
- Power/deepsleep and register-save fields can interact with runtime power management. Incorrect `PCTL_*` save ranges, exclusion sets, or deep-sleep override bits may make state vanish across power gating or prevent MMHUB from entering low-power states.
- The range starts and ends mid-family: it begins with tail masks for `MMEA1_DSM_CNTLA` and ends at `VM_CONTEXT2_PAGE_TABLE_END_ADDR_HI32`. Merge-lane research must combine adjacent chunks before making whole-file claims about those complete register groups.

## Test And Validation Signals

There are no direct unit tests for this generated macro chunk. Useful validation signals are build-time and hardware/runtime oriented:

- Build AMDGPU paths that include `mmhub_1_0_sh_mask.h`, especially `mmhub_v1_0.c`, `gmc_v9_0.c`, and related SOC15 MMHUB code. Field-name mismatches show up as compile failures in `REG_SET_FIELD` or `REG_GET_FIELD` users.
- Static consistency checks can verify that every mask shifted by its matching `__SHIFT` becomes a dense field and that single-bit masks match their bit index. Repeated `VM_CONTEXT[0-15]`, `VM_INVALIDATE_ENG[0-17]`, and `PCTL[0-2]` groups should be checked for expected identical field layouts.
- Runtime GART/VM smoke tests on MMHUB 1.0-class hardware should exercise GART aperture setup, VMID context programming, GPUVM page-table updates, and TLB flush paths without VM faults or stale mappings.
- Fault-injection or forced page-fault tests should produce readable `VM_L2_PROTECTION_FAULT_STATUS` logs with plausible `CID`, `RW`, `VMID`, permission, walker, and mapping fields, and should clear/update status according to driver policy.
- Suspend/resume, runtime power-gating, and mode2 reset tests should preserve MMHUB VM and PCTL state. Register dumps before and after these transitions are useful for validating PCTL save ranges and `amdgpu_gmc` mode2 restore coverage.
- Clock/power-gating validation should confirm that `ATC_L2_MISC_CG`, `ATC_L2_CGTT_CLK_CTRL`, `MMEA1_CGTT_CLK_CTRL`, and PCTL deep-sleep fields do not regress MMHUB idle behavior or translation correctness.

## Chunk Notes For Merge Lane

This is one chunk of a larger generated MMHUB 1.0 mask header. Whole-file documentation should merge it with the preceding MMEA/DAGB sections and the following VM context end-address continuation. Treat this chunk as the central MMHUB VM/power-control bitfield section rather than as standalone logic.

### subset-b-002754: lines 9529-10249

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_0_sh_mask.h lines 9529-10249

## Scope And Purpose

This chunk is the tail of the MMHUB 1.0 shader/register mask header. It is a generated-style hardware contract file: every exported symbol is a preprocessor macro that gives the bit shift or mask for a field inside a 32-bit MMHUB register. There are no functions, structs, variables, control-flow statements, or runtime decisions in this range.

The line range covers the final VM and shared MMHUB register groups:

- `VM_CONTEXT3_PAGE_TABLE_END_ADDR_*` through `VM_CONTEXT15_PAGE_TABLE_END_ADDR_*`, plus the tail of context 2 at the first two lines, describing low 32-bit and high 4-bit logical page-number fields for VMID page-table end addresses.
- `MC_VM_L2_PERFCOUNTER*`, defining eight MMHUB VM L2 performance counter selectors plus shared result/control and low/high counter read fields.
- `MC_VM_FB_SIZE_OFFSET_VF0` through `MC_VM_FB_SIZE_OFFSET_VF15`, defining per-SR-IOV-virtual-function framebuffer size and offset packing.
- Shared VM aperture, ATS, clock, reset, memory power, cacheable-DRAM, APT, local-HBM, FB/AGP, system-aperture, and L1 TLB control fields.
- `ATC_L2_PERFCOUNTER*`, defining ATC L2 performance counter selector/result fields.
- `MMEA0_EDC_CNT*_VG20` and `MMEA1_EDC_CNT*_VG20`, defining Vega20 MMHUB memory error-detection counter fields for RAS.
- `MC_VM_XGMI_LFB_CNTL` and `MC_VM_XGMI_LFB_SIZE`, defining xGMI local framebuffer region and segment-size fields.

The source header is paired with `mmhub_1_0_offset.h`, where the corresponding `mm*` register offsets live. Consumers combine the address macro, mask/shift macro, and helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_ENTRY`, and `SOC15_REG_FIELD` to read, modify, or decode MMIO registers without open-coded bit arithmetic.

## Important APIs, Types, And Constants

This chunk exports constants rather than C APIs or types. The important macro families are:

- `VM_CONTEXTn_PAGE_TABLE_END_ADDR_LO32__LOGICAL_PAGE_NUMBER_LO32_{MASK,__SHIFT}` and `VM_CONTEXTn_PAGE_TABLE_END_ADDR_HI32__LOGICAL_PAGE_NUMBER_HI4_{MASK,__SHIFT}` for contexts 3 through 15. The low half is full 32 bits and the high half uses bits 3:0, matching driver code that writes page frame numbers as `lower_32_bits(max_pfn - 1)` and `upper_32_bits(max_pfn - 1)` or as address shifts by 12 and 44.
- `MC_VM_L2_PERFCOUNTER[0-7]_CFG__*` with `PERF_SEL`, `PERF_SEL_END`, `PERF_MODE`, `ENABLE`, and `CLEAR`. These configure MMHUB VM L2 performance event selection and counter behavior. `MC_VM_L2_PERFCOUNTER_RSLT_CNTL__*` selects a counter, starts/stops trigger windows, enables any counter, clears all counters, and optionally stops on saturation. `MC_VM_L2_PERFCOUNTER_{LO,HI}` provides the readout fields, with `HI` split between `COUNTER_HI` and `COMPARE_VALUE`.
- `MC_VM_FB_SIZE_OFFSET_VF[0-15]__VF_FB_SIZE` and `__VF_FB_OFFSET`, each packed into lower and upper 16-bit halves. These are the per-VF framebuffer aperture description fields used by SR-IOV-oriented MMHUB hardware.
- `VM_IOMMU_MMIO_CNTRL_1__IOMMU_MMIO_EN`, the MARC base/relocation/length fields (`MC_VM_MARC_*_[0-3]`), `VM_IOMMU_*`, and `VM_PCIE_ATS_CNTL*`. These define IOMMU, MMIO, memory aperture relocation, and PCIe Address Translation Service bits for physical and virtual functions.
- `UTCL2_CGTT_CLK_CTRL__SOFT_OVERRIDE*`, `MC_SHARED_VIRT_RESET_REQ__VIRT_RESET_REQ`, `MC_MEM_POWER_LS__*`, `MC_VM_CACHEABLE_DRAM_ADDRESS_{START,END}`, `MC_VM_APT_CNTL__*`, `MC_VM_LOCAL_HBM_ADDRESS_*`, and `MC_VM_LOCAL_HBM_ADDRESS_LOCK_CNTL__LOCK`. These provide clock override, virtualization reset, memory light-sleep, cacheable-address, address-translation/protection table, and local HBM control fields.
- `MC_VM_FB_LOCATION_{BASE,TOP}`, `MC_VM_AGP_{TOP,BOT,BASE}`, `MC_VM_SYSTEM_APERTURE_{LOW,HIGH}_ADDR`, and `MC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_{LSB,MSB}`. These define framebuffer, AGP, and system aperture boundaries consumed by MMHUB GART setup paths.
- `MC_VM_MX_L1_TLB_CNTL__ENABLE_L1_TLB`, `SYSTEM_ACCESS_MODE`, `SYSTEM_APERTURE_UNMAPPED_ACCESS`, `ENABLE_ADVANCED_DRIVER_MODEL`, `ECO_BITS`, `MTYPE`, and `ATC_EN`. These fields are actively used when enabling or disabling the MMHUB L1 TLB.
- `ATC_L2_PERFCOUNTER[0-1]_CFG`, `ATC_L2_PERFCOUNTER_RSLT_CNTL`, and `ATC_L2_PERFCOUNTER_{LO,HI}` mirror the VM L2 perf-counter shape for the ATC L2 block.
- `MMEA0_EDC_CNT_VG20`, `MMEA0_EDC_CNT2_VG20`, `MMEA1_EDC_CNT_VG20`, and `MMEA1_EDC_CNT2_VG20` define 2-bit SEC/DED or SED counter fields for command, data, page, tag, GMI, and MAM memories. The `_VG20` suffix is significant: `mmhub_v1_0.c` uses these for Vega20-style MMHUB RAS field tables.
- `MC_VM_XGMI_LFB_CNTL__PF_LFB_REGION`, `MC_VM_XGMI_LFB_CNTL__PF_MAX_REGION`, and `MC_VM_XGMI_LFB_SIZE__PF_LFB_SIZE` describe xGMI physical function region ID, maximum region, and local framebuffer segment size.

## Control Flow And State Behavior

There is no local control flow. Inclusion makes the constants available at compile time, and runtime behavior is entirely in consumer code.

For page table bounds, `mmhub_v1_0_init_gart_aperture_regs()` writes VMID0 start/end registers from `adev->gmc.gart_start` and `adev->gmc.gart_end`. `mmhub_v1_0_setup_vmid_config()` iterates VMIDs 1 through 15 by using `hub->ctx_addr_distance`; it writes page-table start to zero and page-table end to `adev->vm_manager.max_pfn - 1`. The macros in this chunk describe the corresponding register bit layout, while the writes themselves use the paired offset macros.

For TLB control, `mmhub_v1_0_init_tlb_regs()` reads `mmMC_VM_MX_L1_TLB_CNTL`, sets `ENABLE_L1_TLB`, `SYSTEM_ACCESS_MODE`, `ENABLE_ADVANCED_DRIVER_MODEL`, `SYSTEM_APERTURE_UNMAPPED_ACCESS`, `MTYPE`, and `ATC_EN`, then writes the register back. `mmhub_v1_0_gart_disable()` clears `ENABLE_L1_TLB` and `ENABLE_ADVANCED_DRIVER_MODEL`. Those read-modify-write paths rely on these masks to preserve unrelated hardware bits.

For apertures, `mmhub_v1_0_get_fb_location()` reads `MC_VM_FB_LOCATION_BASE/TOP` and decodes `FB_BASE`/`FB_TOP` into `adev->gmc.fb_start` and `adev->gmc.fb_end` by shifting by 24. `mmhub_v1_0_init_system_aperture_regs()` writes AGP/system/default-address registers from `adev->gmc` state and scratch/dummy-page addresses; on several APUs it extends `MC_VM_SYSTEM_APERTURE_HIGH_ADDR` as a hardware workaround. SR-IOV VFs return early from part of this path, while `mmhub_v1_0_gart_enable()` explicitly programs VF copy `MC_VM_FB_LOCATION_BASE/TOP` registers before enabling GART.

For xGMI, display code calls `REG_GET(MC_VM_XGMI_LFB_CNTL, PF_MAX_REGION, &pf_max_region)` and treats zero as disabled. GFX hub code reads `MC_VM_XGMI_LFB_CNTL` and `MC_VM_XGMI_LFB_SIZE`, derives `num_physical_nodes` from `PF_MAX_REGION + 1`, derives `physical_node_id` from `PF_LFB_REGION`, and shifts `PF_LFB_SIZE` by 24 to compute the node segment size.

For RAS, `mmhub_v1_0.c` builds `soc15_ras_field_entry` tables from the `MMEA[01]_EDC_CNT*_VG20` masks and shifts. `mmhub_v1_0_query_ras_error_count()` reads the EDC counter registers, decodes SEC/DED counts with those fields, accumulates corrected and uncorrected error counts, and logs nonzero subblock counts. `mmhub_v1_0_reset_ras_error_count()` resets those counters by reading them back when MMHUB RAS is supported.

The persistent state is hardware state, not C storage in this header. Some fields are configuration state written during GART/MMHUB initialization, disable, SR-IOV setup, display xGMI probing, or power-management setup. Others are observational counters or status fields read from hardware. Their lifetime follows GPU reset, power gating, virtualization ownership, and firmware/BIOS programming rules.

## Dependencies And Integration Points

The immediate dependencies are:

- `mmhub_1_0_offset.h` for register addresses such as `mmVM_CONTEXT*_PAGE_TABLE_END_ADDR_*`, `mmMC_VM_MX_L1_TLB_CNTL`, `mmMMEA0_EDC_CNT_VG20`, and `mmMC_VM_XGMI_LFB_CNTL`.
- AMDGPU register helper macros from the SOC15 infrastructure, especially `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15_OFFSET`, `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_ENTRY`, and `SOC15_REG_FIELD`.
- `amdgpu_device` state, including `adev->gmc`, `adev->vm_manager`, `adev->vmhub`, `adev->gmc.xgmi`, `adev->mem_scratch`, SR-IOV state, RAS support state, and APU hardware flags.

Important integration points visible in this source tree:

- `drivers/gpu/drm/amd/amdgpu/mmhub_v1_0.c` includes this header directly and consumes page-table end registers, aperture fields, `MC_VM_MX_L1_TLB_CNTL`, framebuffer location fields, and `MMEA[01]_EDC_CNT*_VG20` RAS fields.
- `drivers/gpu/drm/amd/amdgpu/mmhub_v1_8.c` uses the same field names for newer MMHUB instances with multiple AIDs and PSP-mediated SR-IOV programming, which makes this header part of a broader family of similarly shaped MMHUB register contracts.
- `drivers/gpu/drm/amd/amdgpu/gfxhub_v1_1.c` and `gfxhub_v1_2.c` use `MC_VM_XGMI_LFB_CNTL` and `MC_VM_XGMI_LFB_SIZE` field names when deriving xGMI topology.
- `drivers/gpu/drm/amd/display/dc/hwss/dce120/dce120_hwseq.c` and `dce/dce_hwseq.h` expose `MC_VM_XGMI_LFB_CNTL` through display register tables and use `PF_MAX_REGION` as the xGMI-enabled signal.
- `amdgpu_gmc.h` carries mode2 save/restore slots for `VM_CONTEXT_PAGE_TABLE_END_ADDR_*` and `MC_VM_MX_L1_TLB_CNTL`, so values described by this chunk can be preserved by higher-level GMC reset/resume flows.

## Risks And Edge Cases

- The constants must exactly match the MMHUB 1.0 hardware spec. A one-bit mask or shift drift can silently set reserved bits, truncate a page-table end address, misconfigure TLB behavior, misreport xGMI topology, or undercount/overcount RAS errors.
- Page-table end address fields are split as 32 low bits plus 4 high bits. Consumers must pass page-frame/logical-page numbers, not raw byte addresses, and must use the expected 12/44-bit shifts or `lower_32_bits`/`upper_32_bits` PFN split. Mixing byte-address and page-number units can produce broad VM aperture faults.
- `REG_SET_FIELD` depends on exact `<REGISTER>__<FIELD>_MASK` and `<REGISTER>__<FIELD>__SHIFT` naming. Renaming or using the wrong register prefix breaks compile-time expansion or, worse, selects fields from another ASIC register namespace if a compatible name exists.
- Several register groups are repeated for 16 VM contexts or 16 VFs. Table or offset-distance consumers must maintain the same stride assumptions as `mmhub_1_0_offset.h`; manual edits to one repeated macro but not its siblings are high risk.
- Some fields are full-width masks (`0xFFFFFFFFL`) and many masks use an `L` suffix. Consumers should keep arithmetic in unsigned 32-bit or explicitly widened unsigned types to avoid sign-extension and formatting surprises.
- `MC_VM_XGMI_LFB_CNTL` differs for Aldebaran-specific code in `gfxhub_v1_1.c`, which carries local `_ALDE` field definitions with wider masks. Reusing MMHUB 1.0 `PF_*` widths on a different ASIC can misdecode node IDs or segment counts.
- RAS EDC counter fields are 2-bit packed counters. They can saturate or reset-on-read depending on hardware behavior; `mmhub_v1_0_reset_ras_error_count()` relies on readback to clear. Poll cadence and read ordering matter when interpreting field values.
- SR-IOV and PF/VF ownership matters. Some MMHUB registers are skipped in VF mode, some are VF copy registers, and some newer paths use PSP-mediated writes. Direct writes to shared PF-owned fields from the wrong context can be ineffective or unsafe.
- The chunk ends with the header guard `#endif`. Any generated merge, extraction, or regeneration must preserve it or every include of `mmhub_1_0_sh_mask.h` will fail.

## Test And Validation Signals

There are no direct unit tests for this macro-only chunk. Useful validation signals are integration-oriented:

- Compile AMDGPU and display code that includes `mmhub_1_0_sh_mask.h`, especially `mmhub_v1_0.c`, `gfxhub_v1_1.c`, and DCE hardware sequencer code that consumes `MC_VM_XGMI_LFB_CNTL`.
- Static consistency checks: for each mask/shift pair, `(mask >> shift)` should be a dense field of the expected width; full-width fields should have shift zero; repeated VM context and VF macros should preserve identical layouts.
- GART bring-up tests on MMHUB 1.0 hardware: VMID0 and VMID1-15 page-table end programming should not produce VM faults under normal GART and user-VM traffic.
- Suspend/resume, mode2 reset, and GPU reset tests should verify `MC_VM_MX_L1_TLB_CNTL` and VM context page-table end values are restored consistently.
- SR-IOV VF smoke tests should verify framebuffer location and VF aperture behavior, with no invalid MMHUB register access warnings.
- xGMI topology tests on Vega20/Arcturus-class systems should confirm `PF_MAX_REGION`, `PF_LFB_REGION`, and `PF_LFB_SIZE` decode to the expected physical node count, node ID, and segment size.
- RAS injection or hardware error-counter tests should verify `MMEA0/1` SEC/DED/SED fields map to the intended subblock names and that readback reset behavior clears counters as expected.
- Perf-counter validation can manually program `MC_VM_L2_PERFCOUNTER*` and `ATC_L2_PERFCOUNTER*` selector/control fields, collect low/high reads, and confirm counter selection, clear, enable, trigger, and saturation behavior.

## Chunk Notes For Merge Lane

This is the final chunk of `mmhub_1_0_sh_mask.h`, not a standalone implementation. Whole-file research should merge it as the MMHUB 1.0 tail section that completes VM context page-table end masks and supplies performance counter, SR-IOV framebuffer, shared aperture, TLB, RAS EDC, and xGMI LFB field definitions. The header is source-tree-aligned with `drivers/gpu/drm/amd/include/asic_reg/mmhub/` and should be interpreted alongside `mmhub_1_0_offset.h` and `mmhub_v1_0.c`.
