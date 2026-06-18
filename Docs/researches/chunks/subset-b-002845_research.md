# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 9461-11822

## Scope

This chunk is a generated AMDGPU MMHUB 9.4.1 shift/mask header slice. It contains only C preprocessor constants: no functions, structs, enums, local variables, allocations, locks, callbacks, or executable branches. The slice has 2,362 source lines and 2,171 `#define` entries: 1,087 `__SHIFT` constants and 1,184 `_MASK` constants.

The range starts at the complete `MMEA0_ADDRNORM_LIMIT_ADDR5` field definitions and ends inside `MMEA1_DRAM_WR_PRI_QUANT_PRI1` after `GROUP0_THRESHOLD_MASK`; the remaining masks for that write-priority quantum register continue in the next chunk. The previous chunk contains the immediately preceding `MMEA0_ADDRNORM_BASE_ADDR5` register.

Major covered areas are:

- `MMEA0` address normalization and address-decode programming for address range 5, DRAM/GMI holes, non-power-of-two channel spacing, bank/misc masks, DRAM and GMI address hashing, harvest override bits, and three address-decode tables.
- `MMEA0` IO arbitration controls: client-to-group maps, group-to-virtual-channel maps, lazy/flush behavior, CAM depth and reorder limits, burst limits, priority aging/queuing/fixed/urgency/quantum controls, and urgency masking.
- `MMEA0` SDP request/response arbitration, priority, credit reservation, request policy, misc link-manager behavior, latency sampling, and performance counters.
- `MMEA0` RAS/EDC and diagnostic controls: EDC count registers, DSM/single-write/error-injection controls, clock control, EDC mode, error status, misc2, address-decode channel select, and late `EDC_CNT3` DED counters.
- Beginning of `addressBlock: mmhub_ea_mmeadec1`, covering the first `MMEA1` DRAM read/write arbitration controls through the first mask of `MMEA1_DRAM_WR_PRI_QUANT_PRI1`.

Although the repository path is under `sources/distributed-fs/ceph-client`, this header is AMD GPU MMIO metadata, not Ceph or distributed-filesystem logic.

## Purpose

The purpose of this slice is to publish the bit-level ABI for MMHUB 9.4.1 memory endpoint/address-decode registers. Each hardware register field follows the generated AMD convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for composing or extracting the field value.
- `<REGISTER>__<FIELD>_MASK`: 32-bit mask for isolating or updating the field.

The matching `mmhub_9_4_1_offset.h` file supplies register addresses such as `mmMMEA0_ADDRNORM_LIMIT_ADDR5`, `mmMMEA0_EDC_CNT`, `mmMMEA0_ERR_STATUS`, and `mmMMEA1_DRAM_RD_CLI2GRP_MAP0`. This header supplies the masks and shifts consumed by SOC15 helpers such as `SOC15_REG_FIELD`, `SOC15_REG_ENTRY`, `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32`, and `RREG32_SOC15`.

Operationally, these constants describe how the MMHUB endpoint address logic maps normalized addresses to DRAM/GMI fabric resources and how MMHUB traffic is grouped, prioritized, credited, sampled, and diagnosed. The chunk is especially important for RAS reporting in `amdgpu/mmhub_v9_4.c`, where the `MMEA*_EDC_CNT*` and `MMEA*_ERR_STATUS` fields are decoded into correctable/uncorrectable error counts and status warnings.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this range. The public interface is the macro namespace.

Important macro groups include:

- Address normalization: `MMEA0_ADDRNORM_LIMIT_ADDR5`, `MMEA0_ADDRNORM_OFFSET_ADDR5`, `MMEA0_ADDRNORMDRAM_HOLE_CNTL`, `MMEA0_ADDRNORMGMI_HOLE_CNTL`, `MMEA0_ADDRNORMDRAM_NP2_CHANNEL_CFG`, `MMEA0_ADDRNORMGMI_NP2_CHANNEL_CFG`, and the DRAM/GMI global hash controls.
- Address-decode steering: `MMEA0_ADDRDEC_BANK_CFG`, `MMEA0_ADDRDEC_MISC_CFG`, DRAM/GMI hash-bank registers, hash program-counter/chip-select registers, and `MMEA0_ADDRDECDRAM_HARVEST_ENABLE` / `MMEA0_ADDRDECGMI_HARVEST_ENABLE`.
- Address-decode tables: repeated `MMEA0_ADDRDEC0_*`, `MMEA0_ADDRDEC1_*`, and `MMEA0_ADDRDEC2_*` groups. Each table covers chip-select base addresses for CS0-CS3 and SECCS0-SECCS3, CS pair masks, row/column/bank geometry, bank/row selectors, high/low column selectors, row-mask selectors, secondary CS row-mask selectors, channel-bit selection, and row-MSB inversion bits.
- IO arbitration and priority: `MMEA0_IO_RD_CLI2GRP_MAP*`, `MMEA0_IO_WR_CLI2GRP_MAP*`, `MMEA0_IO_RD_COMBINE_FLUSH`, `MMEA0_IO_WR_COMBINE_FLUSH`, `MMEA0_IO_GROUP_BURST`, `MMEA0_IO_RD_PRI_*`, `MMEA0_IO_WR_PRI_*`, and read/write urgency masking registers.
- SDP control: `MMEA0_SDP_ARB_DRAM`, `MMEA0_SDP_ARB_GMI`, `MMEA0_SDP_ARB_FINAL`, `MMEA0_SDP_DRAM_PRIORITY`, `MMEA0_SDP_GMI_PRIORITY`, `MMEA0_SDP_IO_PRIORITY`, `MMEA0_SDP_CREDITS`, tag/VCC/VCD reserve registers, and `MMEA0_SDP_REQ_CNTL`.
- Diagnostic and performance surfaces: `MMEA0_LATENCY_SAMPLING`, `MMEA0_PERFCOUNTER_LO`, `MMEA0_PERFCOUNTER_HI`, `MMEA0_PERFCOUNTER0_CFG`, `MMEA0_PERFCOUNTER1_CFG`, and `MMEA0_PERFCOUNTER_RSLT_CNTL`.
- RAS/EDC registers: `MMEA0_EDC_CNT`, `MMEA0_EDC_CNT2`, and `MMEA0_EDC_CNT3` count SEC/DED/SED events for DRAM read/write command memories, data memories, return tag memories, IO command/data memories, GMI command/data/page memories, and MAM D0-D3 memories.
- Error injection and EDC mode: `MMEA0_DSM_CNTL`, `MMEA0_DSM_CNTLA`, `MMEA0_DSM_CNTL2`, `MMEA0_DSM_CNTL2A`, `MMEA0_EDC_MODE`, and `MMEA0_ERR_STATUS`.
- Clock and misc controls: `MMEA0_CGTT_CLK_CTRL`, `MMEA0_MISC`, `MMEA0_MISC2`, and `MMEA0_ADDRDEC_SELECT`.
- Beginning of MMEA1 DRAM arbitration: `MMEA1_DRAM_RD_CLI2GRP_MAP*`, `MMEA1_DRAM_WR_CLI2GRP_MAP*`, `MMEA1_DRAM_RD_GRP2VC_MAP`, `MMEA1_DRAM_WR_GRP2VC_MAP`, lazy controls, CAM controls, page-burst limits, priority age/queue/fixed/urgency controls, read quantum threshold registers, and the first field mask of `MMEA1_DRAM_WR_PRI_QUANT_PRI1`.

## Control Flow

This header chunk has no runtime control flow. Runtime behavior is supplied by code that includes this generated header, primarily `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`.

Observed control-flow integration in this tree:

1. `mmhub_v9_4.c` includes `mmhub/mmhub_9_4_1_offset.h` and `mmhub/mmhub_9_4_1_sh_mask.h`, binding the register address namespace to the field shift/mask namespace.
2. Static RAS field tables use `SOC15_REG_ENTRY(MMHUB, 0, mmMMEA0_EDC_CNT)` and `SOC15_REG_FIELD(MMEA0_EDC_CNT, ...)` style initializers. The `SOC15_REG_FIELD` entries resolve to the shift/mask constants defined in this header.
3. `mmhub_v9_4_query_ras_error_count()` iterates `mmhub_v9_4_edc_cnt_regs`, reads each EDC register with `RREG32(SOC15_REG_ENTRY_OFFSET(...))`, and passes nonzero values to `mmhub_v9_4_get_ras_error_count()`.
4. `mmhub_v9_4_get_ras_error_count()` scans the static field table for matching register offsets, extracts SEC and DED counts with `(value & mask) >> shift`, logs nonzero subblock counts, and accumulates CE/UE totals.
5. `mmhub_v9_4_reset_ras_error_count()` reads each EDC count register to reset counters when MMHUB RAS is supported. The read-to-reset behavior is driver-commented in `mmhub_v9_4.c`, not encoded by the macros.
6. `mmhub_v9_4_query_ras_error_status()` reads each `MMEA*_ERR_STATUS` register and uses `REG_GET_FIELD(..., MMEA0_ERR_STATUS, SDP_RDRSP_STATUS)`, `SDP_WRRSP_STATUS`, and `SDP_RDRSP_DATAPARITY_ERROR` to warn before GPU reset when SDP response/parity conditions are present.

Most address-decode, arbitration, performance, DSM, and clock-control fields in this chunk are not actively programmed by the nearby Linux driver code found in this tree. They remain part of the generated register ABI for firmware, platform initialization, debug tooling, validation, or future driver paths.

## State And Persistence Behavior

The header itself stores no software state and persists nothing. It describes MMIO-backed hardware state in the MMHUB endpoint/address-decode path.

Hardware state represented by this chunk includes:

- Address normalization state: range limit/fabric destination, high-address offset enable/value, DRAM/GMI hole validity and offset, non-power-of-two 64K channel spacing, and global hash interleave control for 64K/2M/1G granularities.
- Address-decode state: bank masks, bank-group selection/interleave, pseudo-channel/channel/chip-select/rank-mask fields, DRAM/GMI hash XOR enables and XOR source bits, harvested bank force enables/values, and three complete address-decoder tables with CS enable/base/mask/geometry/selector fields.
- Arbitration state: client-to-group assignment for 32 client IDs, group-to-VC assignment, lazy request accumulation delays and thresholds, reorder CAM depth/limits, page-burst limits, age/queue/fixed/urgency priority coefficients, urgency modes, priority quantum thresholds, and urgency masking against response/credit/full/urgency sources.
- SDP state: DRAM/GMI/final arbitration burst limits, early switch behavior, priority selection, group credits, tag and virtual-channel credit reservations, request pass/chain override policy, and inner-domain mode.
- Diagnostic state: latency sampler selectors, performance-counter event selection, result selection, trigger/clear/stop-on-saturate bits, and 48-bit counter payload split across LO and HI/compare fields.
- RAS/EDC state: SEC/DED/SED counters for multiple MMHUB memories, DSM irritator/single-write controls, error-injection enables and delay selection, EDC mode controls, and fatal/error status fields.
- Power/clock state: CGTT on-delay/off-hysteresis, stall/soft overrides, light-sleep override, and misc traffic/link-manager arbitration bits.
- Multi-instance state: `MMEA0` registers represent range/endpoint instance 0, and the chunk starts the structurally similar `MMEA1` DRAM arbitration programming for range/endpoint instance 1.

Persistence and side effects are hardware-defined. Configuration fields generally persist until reset, power-gating loss, firmware/driver reinitialization, or explicit MMIO writes. EDC counters and error status fields are stateful status surfaces; the driver comments that reading EDC count registers resets those counters. Error-injection, clear-status, performance-counter clear, and request/override fields may have immediate side effects and must be sequenced by hardware-specific code rather than treated as passive data.

## Dependencies And Integration Points

Direct dependencies:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_offset.h` provides the matching register offsets and base indices. For example, this chunk's fields pair with offsets including `mmMMEA0_ADDRNORM_LIMIT_ADDR5`, `mmMMEA0_EDC_CNT`, `mmMMEA0_EDC_CNT2`, `mmMMEA0_EDC_CNT3`, `mmMMEA0_ERR_STATUS`, `mmMMEA1_DRAM_RD_CLI2GRP_MAP0`, and `mmMMEA1_DRAM_WR_PRI_QUANT_PRI1`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c` includes this header and uses its field names through SOC15 helper macros.
- Common AMDGPU/SOC15 register helpers provide `SOC15_REG_ENTRY`, `SOC15_REG_FIELD`, `SOC15_REG_ENTRY_OFFSET`, `REG_GET_FIELD`, `RREG32`, and related MMIO access abstractions.

Observed integration points:

- The `mmhub_v9_4_ras_fields` table decodes `MMEA0_EDC_CNT`, `MMEA0_EDC_CNT2`, and `MMEA0_EDC_CNT3` fields from this chunk for MMHUB range 0. It also decodes later `MMEA1`-`MMEA7` EDC count registers using the same generated naming pattern outside this slice.
- `mmhub_v9_4_edc_cnt_regs` enumerates `mmMMEA0_EDC_CNT`, `mmMMEA0_EDC_CNT2`, and `mmMMEA0_EDC_CNT3` from the paired offset header so RAS query/reset code can read every MMHUB endpoint's EDC counters.
- `mmhub_v9_4_query_ras_error_status()` uses `MMEA0_ERR_STATUS` fields as the decoding template while iterating over `MMEA0_ERR_STATUS` through `MMEA7_ERR_STATUS`; this relies on identical field layout across the endpoint instances.
- Firmware or low-level initialization code outside the observed Linux source may program address-decode and arbitration fields. These tables define fabric/channel/bank/chip-select mapping and traffic arbitration, so they integrate with memory topology, XGMI/GMI routing, RAS validation, and performance tuning.
- Performance/debug tooling can use `MMEA0_PERFCOUNTER*` and `MMEA0_LATENCY_SAMPLING` fields to select events, clear counters, enable counting, trigger start/stop, and read LO/HI counter values.

## Risks And Edge Cases

- Bitfield drift is high impact. A wrong shift or mask can silently decode the wrong error count, program the wrong address-decode selector, or change arbitration/credit behavior.
- The chunk ends mid-register. `MMEA1_DRAM_WR_PRI_QUANT_PRI1` is incomplete here: only shifts and `GROUP0_THRESHOLD_MASK` are in this slice, while the remaining masks continue after line 11822. The merge lane must reconcile adjacent chunks before making complete file-level claims for that register.
- Address-decode fields are topology-critical. Incorrect base/mask/CS enable, bank/row/column selector, channel bit, or row-MSB inversion fields can misroute memory accesses, alias addresses, or break DRAM/GMI interleave assumptions.
- Hashing and harvest override fields are sensitive. Changing XOR source fields or forced bank-enable/value fields can alter address distribution or collide with physical fuse/harvest state.
- Repeated decoder tables invite copy/stride mistakes. `ADDRDEC0`, `ADDRDEC1`, and `ADDRDEC2` use near-identical layouts, so consumers must match the correct register offset with the correct instance and CS pair.
- Arbitration fields can affect correctness under load as well as performance. Bad CAM depth, reorder limits, lazy thresholds, burst limits, urgency coefficients, or credit reservations can cause starvation, response stalls, or hard-to-reproduce hangs.
- RAS counter extraction depends on exact count widths. The `MMEA0_EDC_CNT*` fields are packed two-bit counters in many places; an incorrect mask/shift can report false CE/UE totals or miss real errors before reset.
- EDC counter reset is side-effectful. `mmhub_v9_4_reset_ras_error_count()` relies on readback to clear counters, so extra reads from debug paths may change later RAS accounting.
- Error-injection and DSM controls should not be used accidentally. Fields such as `ENABLE_ERROR_INJECT`, `SELECT_INJECT_DELAY`, and DSM irritator/single-write controls are validation-oriented and can intentionally perturb hardware behavior.
- `MMEA0_ERR_STATUS__CLEAR_ERROR_STATUS_MASK` and other clear/status bits are not self-describing from the macro names alone. Consumers need hardware sequencing rules to avoid losing status or leaving fatal conditions uncleared.
- Cross-instance decoding assumes identical layouts. `mmhub_v9_4_query_ras_error_status()` uses `MMEA0_ERR_STATUS` field names while iterating status registers for all instances; this is valid only while all `MMEA*` status registers retain identical bit positions.

## Test Signals

Useful validation signals for this chunk are generated-header consistency, build coverage, and RAS/arbitration behavior:

- Build AMDGPU with MMHUB 9.4 support enabled. Compile-time failures in `mmhub_v9_4.c` would catch missing or renamed macros used by `SOC15_REG_FIELD` and `REG_GET_FIELD`.
- Compare this slice against AMD's authoritative MMHUB 9.4.1 register database and the paired `mmhub_9_4_1_offset.h`; every field name must align with the intended register offset and bit layout.
- Run MMHUB RAS query paths with known injected or simulated EDC values. `mmhub_v9_4_get_ras_error_count()` should report the expected SEC/DED counts for `MMEA0_EDC_CNT`, `MMEA0_EDC_CNT2`, and `MMEA0_EDC_CNT3`.
- Verify read-to-clear behavior for EDC counters on supported hardware: after `mmhub_v9_4_reset_ras_error_count()`, subsequent RAS queries should not re-report the same counts.
- Exercise `MMEA*_ERR_STATUS` handling by provoking or injecting SDP read/write response and read-data parity status. The driver should log the expected MMHUB EA status before reset handling.
- Validate address-decode programming through firmware/platform tests: DRAM/GMI interleaving, hole handling, non-power-of-two channel mapping, chip-select routing, and harvested-bank behavior should match memory topology tables.
- Stress mixed read/write/atomic traffic across IO, DRAM, and GMI paths to expose arbitration regressions from client grouping, urgency, lazy/CAM, page-burst, or credit-reservation fields.
- Use performance-counter tooling to select events, enable/clear counters, trigger start/stop, read LO/HI values, and confirm stop-on-saturate or compare behavior.
- Run suspend/resume and power-gating tests where CGTT and clock/LS override state may be reinitialized or lost.

## Cross-Chunk Notes

The previous chunk owns the immediately preceding `MMEA0_ADDRNORM_BASE_ADDR5` register. This chunk owns the complete `MMEA0_ADDRNORM_LIMIT_ADDR5` through `MMEA1_DRAM_WR_PRI_QUANT_PRI1__GROUP0_THRESHOLD_MASK` range. The next chunk must add the remaining `MMEA1_DRAM_WR_PRI_QUANT_PRI1` masks and subsequent MMEA1 registers before the final per-file report describes the full `MMEA1` DRAM priority quantum register set.
