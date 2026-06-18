# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 14187-16550

## Scope

This chunk is a generated AMDGPU MMHUB 9.4.1 shift/mask header slice. It contains C preprocessor constants only: no functions, structs, enums, storage, allocations, locks, loops, or executable branches. The range starts inside `MMEA1_PERFCOUNTER1_CFG` after its field shifts were emitted in the previous chunk, then covers the end of the `mmhub_ea_mmeadec1` block and most of the `mmhub_ea_mmeadec2` block. It ends inside `MMEA2_IO_WR_CLI2GRP_MAP1` after `CID30_GROUP_MASK`; the `CID31_GROUP_MASK` definition and later MMEA2 registers continue in the next chunk.

Within those boundaries the slice defines bit offsets and masks for these major areas:

- MMEA1 performance-counter result control, EDC/RAS counters, DSM error-injection controls, clock-gating controls, EDC mode, error status, miscellaneous arbitration controls, address-decoder channel selection, and extra DED counters.
- `addressBlock: mmhub_ea_mmeadec2`, covering MMEA2 DRAM/GMI read and write client-to-group maps, group-to-virtual-channel maps, lazy request accumulation, CAM/reorder controls, page-burst limits, priority aging/queuing/fixed/urgency coefficients, GMI urgency client masks, and priority quantum thresholds.
- MMEA2 address normalization ranges 0-5, limit and offset registers, DRAM/GMI hole controls, non-power-of-two channel configuration, address-decoder bank and misc configuration, DRAM/GMI hash controls, harvest-enable controls, and repeated channel/chip-select address-decoder tables for decoders 0, 1, and 2.
- MMEA2 DRAM/GMI global address-normalization hash controls and the start of MMEA2 IO read/write client grouping.

Although this path lives under `sources/distributed-fs/ceph-client`, this file is AMD GPU MMIO register metadata, not distributed-filesystem logic.

## Purpose

The purpose of this chunk is to publish the bit-level ABI for MMHUB 9.4.1 MMEA register programming. Each generated definition follows the AMD register-header convention:

- `<REGISTER>__<FIELD>__SHIFT`: the bit position of a field.
- `<REGISTER>__<FIELD>_MASK`: the 32-bit mask for isolating or composing that field.

The matching `mmhub_9_4_1_offset.h` header supplies register addresses such as `mmMMEA1_EDC_CNT`, `mmMMEA1_EDC_CNT2`, `mmMMEA1_EDC_CNT3`, `mmMMEA1_ERR_STATUS`, and the MMEA2 address-decoder and arbitration registers. This header supplies the field masks used by helper macros such as `SOC15_REG_FIELD`, `REG_GET_FIELD`, `REG_SET_FIELD`, `SOC15_REG_ENTRY`, `RREG32`, `RREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15`, and `WREG32_SOC15_OFFSET`.

Operationally, the covered registers describe the MMHUB external-address/memory-fabric path for the second and third MMEA ranges: request grouping and virtual-channel selection, read/write arbitration behavior, address normalization and interleave geometry, bank/rank/column address decoding, DRAM/GMI hash selection, harvested-bank overrides, clock-gating behavior, performance counters, and RAS/ECC/error-injection surfaces.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this range. The public interface is the generated macro namespace consumed by AMDGPU MMHUB code and by generated/default register-setting tables.

Important macro groups include:

- `MMEA1_PERFCOUNTER1_CFG` tail and `MMEA1_PERFCOUNTER_RSLT_CNTL`: event selection, event-range end, mode, enable/clear, result-counter select, start/stop triggers, clear-all, enable-any, and stop-on-saturate fields for MMEA1 performance measurement.
- `MMEA1_EDC_CNT`, `MMEA1_EDC_CNT2`, and `MMEA1_EDC_CNT3`: SEC/DED/SED counter fields for DRAM read command memory, DRAM write command/data/page memory, GMI read/write command/data/page memory, IO read/write command/data memory, return tag memories, and MAM D0-D3 memories.
- `MMEA1_DSM_CNTL`, `MMEA1_DSM_CNTLA`, `MMEA1_DSM_CNTL2`, and `MMEA1_DSM_CNTL2A`: diagnostic/scrub/error-injection controls. These select irritator data, single-write behavior, enable-error-inject values, per-memory inject-delay selection, and a common inject-delay field.
- `MMEA1_CGTT_CLK_CTRL`: clock-gating timing and overrides, including on delay, off hysteresis, spare fields, soft stall override for write/read/return, light-sleep override, and write/read/return/register soft overrides.
- `MMEA1_EDC_MODE`, `MMEA1_ERR_STATUS`, `MMEA1_MISC2`, and `MMEA1_ADDRDEC_SELECT`: EDC policy bits, response/error status bits, clear-error/busy-on-error/FUE status, arbitration swap and burst-limit controls, IO read/write priority enable, return swap mode, and DRAM/GMI decoder channel start/end selectors.
- `MMEA2_DRAM_*` and `MMEA2_GMI_*` arbitration registers: `*_CLI2GRP_MAP0/1` map client IDs 0-31 into four traffic groups; `*_GRP2VC_MAP` maps groups to virtual channels; `*_LAZY` controls per-group delay and request accumulation thresholds/timeouts; `*_CAM_CNTL` controls group CAM depth, reorder limits, and refill-chain behavior; `*_PAGE_BURST`, `*_PRI_AGE`, `*_PRI_QUEUING`, `*_PRI_FIXED`, `*_PRI_URGENCY`, `*_PRI_URGENCY_MASKING`, and `*_PRI_QUANT_PRI*` define arbitration policy.
- `MMEA2_ADDRNORM_BASE_ADDR0` through `MMEA2_ADDRNORM_BASE_ADDR5`, their `LIMIT_ADDR*` companions, and `OFFSET_ADDR1/3/5`: range-valid bits, legacy MMIO hole enable, channel/die/socket interleave geometry, address-select fields, base/limit address fields, fabric-destination IDs, and high-address offset controls.
- `MMEA2_ADDRNORMDRAM_HOLE_CNTL`, `MMEA2_ADDRNORMGMI_HOLE_CNTL`, `MMEA2_ADDRNORMDRAM_NP2_CHANNEL_CFG`, `MMEA2_ADDRNORMGMI_NP2_CHANNEL_CFG`, `MMEA2_ADDRNORMDRAM_GLOBAL_CNTL`, and `MMEA2_ADDRNORMGMI_GLOBAL_CNTL`: DRAM/GMI hole validity and offset, non-power-of-two channel address-space sizing, and 64K/2M/1G global hash interleave controls.
- `MMEA2_ADDRDEC_BANK_CFG` and `MMEA2_ADDRDEC_MISC_CFG`: DRAM/GMI bank masks, bank-group selection, bank-group interleave, VCM enable bits, package-channel/channel/chip-select/rank-multiplier masks.
- `MMEA2_ADDRDECDRAM_*` and `MMEA2_ADDRDECGMI_*`: XOR hash controls for bank0-bank5, pseudo-channel, pseudo-channel extension, and chip-select hash registers, plus harvest-enable force bits for banks 3-5.
- `MMEA2_ADDRDEC0_*`, `MMEA2_ADDRDEC1_*`, and `MMEA2_ADDRDEC2_*`: repeated decoder tables for chip-select base enables and base addresses, address masks, chip-select address geometry, bank and row address-source selection, bank5 selection, column low/high selection, rank-multiplier selection, channel bit selection, and even/odd row-MSB inversion for primary and secondary chip-select pairs.
- `MMEA2_IO_RD_CLI2GRP_MAP0/1` and partial `MMEA2_IO_WR_CLI2GRP_MAP0/1`: IO traffic client-to-group maps. The chunk contains complete IO read maps, complete IO write map0, and all but the final mask of IO write map1.

## Control Flow

This header chunk has no runtime control flow. Runtime sequencing is supplied by consumers, mainly `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`, which includes `mmhub_9_4_1_offset.h`, `mmhub_9_4_1_sh_mask.h`, and `mmhub_9_4_1_default.h`.

The most direct consumer path in this range is RAS counting:

1. `mmhub_v9_4_ras_fields` maps human-readable subblock names to `SOC15_REG_ENTRY(MMHUB, 0, mmMMEA*_EDC_CNT*)` and `SOC15_REG_FIELD(MMEA*_EDC_CNT*, ...)` pairs. For MMEA1 and MMEA2, the `EDC_CNT`, `EDC_CNT2`, and `EDC_CNT3` field macros in this chunk provide the SEC/DED/SED shifts and masks.
2. `mmhub_v9_4_edc_cnt_regs` lists the EDC counter registers to poll, including `mmMMEA1_EDC_CNT`, `mmMMEA1_EDC_CNT2`, `mmMMEA1_EDC_CNT3`, `mmMMEA2_EDC_CNT`, `mmMMEA2_EDC_CNT2`, and `mmMMEA2_EDC_CNT3`.
3. `mmhub_v9_4_query_ras_error_count()` reads each listed register with `RREG32(SOC15_REG_ENTRY_OFFSET(...))`.
4. `mmhub_v9_4_get_ras_error_count()` compares the register offset, extracts SEC and DED values by applying the generated masks and shifts, logs nonzero subblock counts, and accumulates corrected and uncorrected error totals.
5. `mmhub_v9_4_reset_ras_error_count()` resets those counters by reading the EDC counter registers when MMHUB RAS is supported.

`MMEA1_ERR_STATUS` is also integrated through `mmhub_v9_4_err_status_regs` and `mmhub_v9_4_query_ras_error_status()`, though the current code path compares status bits with the `MMEA0_ERR_STATUS` field names because sibling MMEA status registers share the same layout.

The other macros in this chunk are primarily register-programming surfaces. They are used through SOC15 register helpers, golden/default register tables, firmware initialization, or debug tooling rather than through explicit C branches in this header. For example, `gmc_v9_0.c` has an older-generation golden setting for `mmMMEA1_DRAM_WR_CLI2GRP_MAP0`, illustrating how the client-to-group maps are patched through mask/value register writes.

## State And Persistence Behavior

The header stores no software state and persists nothing. It describes MMIO-backed hardware state whose lifetime is the GPU's programmed register state across initialization, reset, suspend/resume, and RAS service operations.

The represented hardware state includes:

- RAS and EDC counters for MMEA1/MMEA2 internal memories. These counters are read by the driver for error reporting; in the v9.4 code path the EDC counters are reset by readback when MMHUB RAS is enabled.
- Error status and mode bits for MMEA1, including response status, data status/parity flags, clear-error-status, busy-on-error, FUE status, DED mode, propagation/gating policy, and EDC bypass.
- Diagnostic and error-injection state for selected MMEA1 SRAM/tag/page memories. These fields can intentionally inject or delay memory errors and should be treated as validation/RAS controls rather than normal data-path tuning.
- Clock-gating state for MMEA1. Values affect power-management timing and whether write/read/return/register blocks are held in software override or light-sleep override modes.
- DRAM/GMI/IO traffic-group and virtual-channel state for MMEA2. These registers shape how clients are grouped, which virtual channel each group uses, how requests accumulate, and how priority is computed under age, queueing, fixed, urgency, mask, and quantum policies.
- Address-normalization and address-decoder state for MMEA2. These fields define base/limit ranges, interleave geometry, address offsets, address holes, non-power-of-two channel sizing, hash behavior, bank/chip-select/rank/channel/column extraction, and harvested-bank override behavior.

Because these are hardware registers, state persistence depends on GPU reset and power-management sequencing. The generated masks do not encode whether a field is read-only, write-one-to-clear, sticky, self-clearing, shadowed by firmware, or safe to change while traffic is active; that semantic contract lives in the hardware specification and driver sequencing.

## Dependencies

This chunk depends on the AMDGPU SOC15 register-header ecosystem:

- `mmhub_9_4_1_offset.h` provides the corresponding register offsets and base indices.
- `mmhub_9_4_1_default.h` can provide reset/default values for the same register namespace.
- `amdgpu/mmhub_v9_4.c` includes this header and consumes the RAS counter/status fields through `SOC15_REG_FIELD`, `SOC15_REG_ENTRY`, `RREG32`, and MMHUB RAS helpers.
- `soc15.h` and `soc15_common.h` supply register-address construction and register access helpers used by the consumer code.
- `amdgpu_ras.h` and RAS core types such as `struct ras_err_data` consume the decoded EDC counters as corrected and uncorrected error totals.
- Hardware/firmware initialization flows depend on field layout compatibility between this generated header and the actual MMHUB 9.4.1 silicon.

The generated names are coupled to exact register layout. A shift/mask mismatch is not a local compile-only problem; it can silently misprogram memory-fabric arbitration or misdecode RAS counters.

## Integration Points

- `mmhub_v9_4.c` is the direct integration point for this header in the source tree. It includes the header at file scope and uses MMEA1/MMEA2 `EDC_CNT*` field macros in the RAS field table.
- MMHUB RAS reporting integrates through `mmhub_v9_4_query_ras_error_count()`, `mmhub_v9_4_reset_ras_error_count()`, and `mmhub_v9_4_query_ras_error_status()`.
- SOC15 MMIO helpers integrate these macros with register offsets. `SOC15_REG_FIELD(REG, FIELD)` relies on both `REG__FIELD_MASK` and `REG__FIELD__SHIFT` existing and matching the generated naming convention.
- Address-normalization and decoder definitions in this chunk align with physical memory layout programming. They must remain synchronized with any code or firmware that programs DRAM/GMI base/limit/interleave/hash tables.
- Arbitration/client grouping fields align with GPU client IDs and virtual channels. Changes affect memory QoS, request ordering, fairness, and latency behavior for DRAM, GMI, and IO paths.
- Golden-setting and default-register infrastructure can apply selected masks during ASIC initialization. Even when a specific MMEA2 field is not referenced by hand-written C in this repository, generated defaults and firmware-facing initialization may still depend on it.

## Risks

- Boundary risk: this research chunk starts and ends in the middle of registers. `MMEA1_PERFCOUNTER1_CFG` is incomplete at the start, and `MMEA2_IO_WR_CLI2GRP_MAP1` is incomplete at the end. Consumers need the merged file-level view to see those full register definitions.
- Silent misdecode risk: wrong `EDC_CNT*` shifts/masks would cause RAS code to undercount, overcount, or mislabel corrected/uncorrected MMHUB errors. Since the extraction is simple mask-and-shift arithmetic, errors may compile cleanly.
- Error-injection risk: DSM controls can inject hardware memory errors. Accidentally programming these outside validation/RAS flows could create artificial faults or stress paths that look like real hardware failures.
- Memory-fabric risk: address-normalization, interleave, hash, bank, chip-select, rank, and column-selection masks describe physical address routing. Incorrect values can steer requests to the wrong memory location, break interleave assumptions, or reduce usable memory.
- QoS/performance risk: client-to-group, group-to-VC, lazy accumulation, CAM, page-burst, and priority fields influence ordering and fairness. Incorrect tuning can create starvation, latency spikes, throughput loss, or deadlock-like backpressure symptoms.
- Power-management risk: clock-gating override fields can affect idle behavior and wake latency. Misprogramming can increase power, mask busy state, or stall register/read/write/return paths.
- Generated-header drift risk: manual edits to generated masks are brittle. The shift/mask names must match offsets, default values, ASIC register specs, and all `SOC15_REG_FIELD` users.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware/RAS oriented:

- Build coverage: compile AMDGPU code that includes `mmhub_v9_4.c`. This catches missing or renamed macros used through `SOC15_REG_FIELD`, especially MMEA1/MMEA2 `EDC_CNT*` and `ERR_STATUS` fields.
- Static macro consistency: verify every `SOC15_REG_FIELD(MMEA1_EDC_CNT*)` and `SOC15_REG_FIELD(MMEA2_EDC_CNT*)` use in `mmhub_v9_4.c` has both matching `__SHIFT` and `_MASK` definitions in this header.
- RAS query behavior: on MMHUB 9.4.1 hardware with RAS enabled, inject or observe known SEC/DED events and confirm `mmhub_v9_4_query_ras_error_count()` reports the expected subblock names and corrected/uncorrected totals.
- Counter reset behavior: after reading EDC counter registers through `mmhub_v9_4_reset_ras_error_count()`, re-query counters and confirm the read-to-clear behavior matches hardware expectations.
- Register smoke tests: read MMEA1/MMEA2 EDC and error-status registers through debugfs or driver tracing and confirm decoded fields align with raw register values.
- Initialization stability: boot/resume/reset tests on supported ASICs should show no MMHUB faults, memory-training fallout, VM faults caused by address routing, or unexplained fabric/RAS status bits after default/golden programming.
- Performance regression signals: memory bandwidth, latency, GMI traffic, and IO-heavy workloads are sensitive to the client grouping, virtual-channel, lazy, CAM, and priority fields covered here.
