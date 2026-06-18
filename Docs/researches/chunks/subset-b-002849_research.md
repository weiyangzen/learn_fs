# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 18900-21241

## Scope

This chunk covers generated shift and mask macros from the AMD MMHUB 9.4.1 register mask header. It starts inside the `MMEA3_ADDRDEC0_COL_SEL_LO_CS23` field list at `COL4` and ends inside `MMEA4_GMI_RD_PRI_URGENCY`, after the urgency coefficient masks and before the urgency mode masks that continue in the next chunk.

The covered range includes 2,180 preprocessor definitions and no executable C. The major register families are:

- Remaining `MMEA3_ADDRDEC0` column-selection and row/memory-channel selection fields.
- Complete `MMEA3_ADDRDEC1` and `MMEA3_ADDRDEC2` address decoder windows for chip-select base addresses, masks, address geometry, bank/row/column selection, and row-mask selection.
- `MMEA3_ADDRNORMDRAM_GLOBAL_CNTL` and `MMEA3_ADDRNORMGMI_GLOBAL_CNTL` normalization controls.
- `MMEA3_IO_*` client-to-group maps, combine flush controls, group burst limits, priority aging/queuing/fixed/urgency settings, urgency client masks, and quantum thresholds.
- `MMEA3_SDP_*` arbitration, priority, credit, reserve, and request-control fields.
- `MMEA3_MISC`, latency sampling, performance counter, EDC counter/mode/status, DSM, clock-gating, address-decoder select, and miscellaneous control/status fields.
- Start of the `mmhub_ea_mmeadec4` address block, covering `MMEA4_DRAM_*` arbitration and priority fields, then `MMEA4_GMI_*` mapping, lazy accumulation, CAM, page burst, and priority fields through `MMEA4_GMI_RD_PRI_URGENCY`.

## Purpose

This header section is the bitfield ABI for MMHUB's memory-mapping and memory-client arbitration hardware on ASICs using the 9.4.1 MMHUB register set. Each hardware field is represented by the conventional generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when composing or extracting the field.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit mask for the field.

The sibling `mmhub_9_4_1_offset.h` header supplies addresses such as `mmMMEA3_EDC_CNT` or `mmMMEA4_EDC_CNT2`; this file supplies only field layouts. The main consumer in this source tree is `drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`, which includes `mmhub_9_4_1_offset.h`, `mmhub_9_4_1_sh_mask.h`, and `mmhub_9_4_1_default.h`. AMDGPU helpers such as `REG_SET_FIELD`, `SOC15_REG_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15` depend on these exact `__SHIFT` and `_MASK` names.

## Important Macro Families

### MMEA3 Address Decode

The first part completes `MMEA3_ADDRDEC0_COL_SEL_LO_CS23` and then defines `MMEA3_ADDRDEC0_COL_SEL_HI_*` plus `MMEA3_ADDRDEC0_RM_SEL_*`. These fields describe how selected physical address bits are interpreted as DRAM column bits and row-mask bits for chip-select groups `CS01`, `CS23`, `SECCS01`, and `SECCS23`.

`MMEA3_ADDRDEC1_*` and `MMEA3_ADDRDEC2_*` are complete repeated decoder windows. Each decoder has:

- `BASE_ADDR_CS0..CS3` and `BASE_ADDR_SECCS0..SECCS3`, with `CS_EN` plus a wide `BASE_ADDR` field.
- `ADDR_MASK_*`, with a wide `ADDR_MASK` field.
- `ADDR_CFG_*`, encoding `NUM_BANK_GROUPS`, `NUM_RM`, row low/high widths, column width, bank count, and `HI_COL_EN`.
- `ADDR_SEL_*` and `ADDR_SEL2_*`, selecting source address bits for bank and row fields, including a separate `BANK5` selector.
- `COL_SEL_LO_*` and `COL_SEL_HI_*`, selecting source address bits for columns `COL0..COL15`.
- `RM_SEL_*`, selecting row-mask source bits and row-MSB inversion behavior for even and odd rows.

These fields are low-level DRAM/GMI address mapping controls. They are data-driven from hardware strap/fuse/platform policy rather than ordinary driver algorithm state.

### MMEA3 Normalization and IO Arbitration

`MMEA3_ADDRNORMDRAM_GLOBAL_CNTL` and `MMEA3_ADDRNORMGMI_GLOBAL_CNTL` provide a `BIG_PAGE` field that affects address normalization for DRAM and GMI paths.

The `MMEA3_IO_*` block maps IO clients into arbitration groups and tunes request handling:

- `IO_RD_CLI2GRP_MAP0/1` and `IO_WR_CLI2GRP_MAP0/1` pack sixteen client-to-group fields per direction as 2-bit values.
- `IO_RD_COMBINE_FLUSH` and `IO_WR_COMBINE_FLUSH` expose per-client flush bits for combined request paths.
- `IO_GROUP_BURST` provides read/write burst limits.
- `IO_RD_PRI_AGE` and `IO_WR_PRI_AGE` encode aging rates and age coefficients for four groups.
- `IO_RD_PRI_QUEUING`, `IO_WR_PRI_QUEUING`, `IO_RD_PRI_FIXED`, and `IO_WR_PRI_FIXED` encode group priority coefficients.
- `IO_RD_PRI_URGENCY` and `IO_WR_PRI_URGENCY` encode group urgency coefficients and per-group urgency mode bits.
- `IO_RD_PRI_URGENCY_MASKING` and `IO_WR_PRI_URGENCY_MASKING` expose one mask bit per `CID0..CID31`.
- `IO_RD_PRI_QUANT_PRI1..3` and `IO_WR_PRI_QUANT_PRI1..3` provide per-group quantum thresholds.

Together these definitions describe MMHUB scheduling policy between IO clients before their traffic enters later MMHUB/SDP paths.

### MMEA3 SDP and Diagnostics

`MMEA3_SDP_*` fields configure the shared data path arbitration stage. They cover DRAM/GMI/final arbitration weights or controls, DRAM/GMI/IO priorities, credits, tag reserves, virtual channel command/data reserves, and request-control bits such as `DISABLE_CREDITS` and `DISABLE_FORCE_ORDERED`.

The diagnostic/control group includes:

- `MMEA3_MISC`, including field-update disallowing, self-init, clock gating, black-hole mode, address range behavior, clock switching, and extra latency.
- `MMEA3_LATENCY_SAMPLING`, with period, threshold, reset, count, overflow, enable, interrupt enable/status, and select fields.
- `MMEA3_PERFCOUNTER_LO/HI`, `PERFCOUNTER0_CFG`, `PERFCOUNTER1_CFG`, and `PERFCOUNTER_RSLT_CNTL`, which select performance counter events, control instances, and expose results.
- `MMEA3_EDC_CNT`, `MMEA3_EDC_CNT2`, and `MMEA3_EDC_CNT3`, which pack correctable, single-error-detected, and double-error-detected counters for DRAM, GMI, IO, return-tag, and MAM memories.
- `MMEA3_DSM_CNTL*`, `MMEA3_DSM_CNTL*A`, and `MMEA3_DSM_CNTL2*`, which expose DSM dump controls, modes, timers, offsets, memory selection, and status.
- `MMEA3_CGTT_CLK_CTRL`, `MMEA3_EDC_MODE`, `MMEA3_ERR_STATUS`, `MMEA3_MISC2`, and `MMEA3_ADDRDEC_SELECT`.

The EDC fields are directly integrated by `mmhub_v9_4.c` in its error-counter table for `MMEA3_*` entries. The driver maps readable labels such as `MMEA3_DRAMRD_CMDMEM`, `MMEA3_GMIRD_CMDMEM`, and `MMEA3_MAM_D0MEM` to `SOC15_REG_ENTRY(MMHUB, 0, mmMMEA3_EDC_CNT*)` plus `SOC15_REG_FIELD(MMEA3_EDC_CNT*, ...)` field descriptors.

### MMEA4 DRAM and GMI Arbitration

The chunk then enters `addressBlock: mmhub_ea_mmeadec4`, starting the `MMEA4` range. Covered `MMEA4_DRAM_*` fields mirror the memory-client scheduler structures used for MMEA3 paths:

- Read/write client-to-group maps.
- Read/write group-to-virtual-channel maps.
- Read/write lazy request accumulation delays, thresholds, timeouts, and idle maximums.
- Read/write CAM depth, reorder limits, refill chaining, and page-based chaining.
- Page burst limits.
- Read/write priority aging, queuing, fixed priority, urgency, and quantum thresholds.

The covered `MMEA4_GMI_*` fields repeat the same scheduler pattern for GMI traffic: client-to-group maps, group-to-VC maps, lazy request accumulation, CAM controls, page burst limits, priority aging, queuing, fixed priority, and the start of read urgency. The range ends before the `MMEA4_GMI_RD_PRI_URGENCY__GROUP*_URGENCY_MODE_MASK` definitions, so that register is incomplete in this chunk.

## Control Flow and State Behavior

There is no runtime control flow in this header chunk. It changes driver behavior only by determining how compile-time macros compose and decode MMIO register values.

The state described is persistent hardware register state. Address-decoder fields determine how MMHUB maps address bits into chip selects, banks, rows, columns, row masks, and normalized DRAM/GMI addressing. Arbitration fields persist priority, grouping, burst, lazy accumulation, CAM/reorder, reserve, and credit policy until hardware reset or reprogramming. Diagnostic fields persist counter configuration, sampled latency status, performance counter control, DSM capture mode/status, EDC mode/status, and clock-gating behavior.

Some fields are status or action-like rather than passive configuration. Examples include latency sampling reset/overflow/interrupt status, combine flush bits, DSM dump controls/status, EDC error status, and field-update disallowing. The macros do not encode required ordering, polling, or clear semantics; users must follow MMHUB initialization, RAS, and debug code sequencing.

## Dependencies and Integration Points

This chunk depends on the generated AMD register header convention:

- `mmhub_9_4_1_offset.h` supplies register offsets and base indices.
- `mmhub_9_4_1_default.h` supplies reset/default values where generated.
- `soc15.h` and related AMDGPU helpers use `__SHIFT` and `_MASK` suffixes to implement `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, and register read/write helpers.

Observed integration in this tree:

- `amdgpu/mmhub_v9_4.c` includes this header and programs MMHUB through SOC15 register helpers for the 9.4 generation.
- `mmhub_v9_4.c` directly consumes `MMEA3_EDC_CNT*` and `MMEA4_EDC_CNT*` field macros in its RAS/error-count table, exposing corrected/detected MMHUB memory errors by source memory label.
- The same C file initializes MMHUB address translation, apertures, TLB/cache behavior, VMID contexts, invalidation ranges, and snoop override registers. Those paths rely on the same offset/mask/default header set, even though the exact fields in this chunk are primarily MMEA address decoder, scheduler, perf, and EDC surfaces.
- Generated MMEA3/MMEA4 address-decoder and scheduler fields are likely consumed by firmware, bring-up tooling, debugfs/register-dump tooling, or future driver paths rather than high-level filesystem code. Their names remain part of the source-level hardware contract.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can write unrelated MMHUB hardware fields and produce memory misrouting, broken chip-select decoding, bad GMI/DRAM normalization, starvation, hangs, or misleading diagnostics.
- The chunk starts and ends mid-register family. Adjacent chunks are required to describe the complete `MMEA3_ADDRDEC0_COL_SEL_LO_CS23` and `MMEA4_GMI_RD_PRI_URGENCY` registers.
- The address-decoder families are highly repetitive across decoder index, chip-select pair, and secondary chip-select pair. Mechanical edits can easily copy a `CS01` mask into `CS23`, omit `SECCS`, or mismatch `ADDRDEC1` and `ADDRDEC2`.
- Scheduler fields encode policy tradeoffs between latency and fairness. Incorrect client-to-group maps, urgency masks, CAM depths, reorder limits, lazy thresholds, or quantum thresholds can starve clients or collapse bandwidth under IO, DRAM, or GMI load.
- EDC counter fields are operationally visible through RAS. Wrong `MMEA3_EDC_CNT*` or `MMEA4_EDC_CNT*` masks can misclassify correctable versus uncorrectable errors, attribute faults to the wrong internal memory, or hide an error signal.
- Performance counter and latency sampling fields can be confused with ordinary status fields. Reset, overflow, interrupt, instance selection, and event selection need explicit sequencing to avoid stale or partial observations.
- DSM and clock-gating fields are debug/power-sensitive. Incorrect dump mode, clock gating, or black-hole configuration can perturb the hardware while debugging the hardware.

## Test and Validation Signals

Useful validation is mostly build, hardware bring-up, and RAS/debug observation:

- Build AMDGPU code that includes `mmhub/mmhub_9_4_1_sh_mask.h`; this catches missing or renamed macros consumed through `REG_SET_FIELD` and `SOC15_REG_FIELD`.
- On MMHUB 9.4.1 hardware, verify GART/VM initialization, suspend/resume, reset, and multi-hub operation still complete after any mask update.
- RAS tests should read/inject MMHUB EDC paths and confirm `MMEA3_*` and `MMEA4_*` labels in `mmhub_v9_4.c` report expected SEC/SED/DED counts from `EDC_CNT`, `EDC_CNT2`, and `EDC_CNT3`.
- Register-dump comparison against known-good hardware or generated headers should confirm address-decoder base/mask/config/selection fields match the hardware spec for `ADDRDEC1` and `ADDRDEC2`.
- Stress tests with IO, DRAM, and GMI traffic should watch for starvation, timeout, VM faults, or bandwidth regression that could indicate broken priority, grouping, CAM, burst, or lazy accumulation fields.
- Performance-counter and latency-sampling validation should confirm selected `MMEA3_PERFCOUNTER*` events count, reset, overflow, and interrupt as expected.
- Debug capture validation should exercise DSM control/status fields without leaving dump state, clock gating, or field-update blocking enabled unexpectedly.
