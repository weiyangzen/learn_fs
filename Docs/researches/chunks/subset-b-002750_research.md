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
