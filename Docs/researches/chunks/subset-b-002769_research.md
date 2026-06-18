# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h lines 25903-28256

## Scope And Purpose

This chunk is a generated-style AMDGPU MMHUB 1.7 register mask header section. It contains preprocessor constants only: each hardware register field is exposed as a `MMEA5_*__FIELD__SHIFT` and/or `MMEA5_*__FIELD_MASK` macro. There are no functions, structs, variables, local storage, or executable control-flow paths in this range.

The covered register namespace is the `MMEA5` MMHUB memory-management engine/arbitration range. The chunk defines bit layouts for:

- GMI read/write client-to-group mapping, group-to-virtual-channel mapping, lazy request accumulation, CAM depth/reorder control, page burst limits, and priority aging/queuing/fixed/urgency/quantum controls.
- Address normalization and address decode fields, including base/limit/offset windows, megabase/megalimit windows, DRAM/GMI hole controls, non-power-of-two channel sizes, bank/channel/chip-select/rank mapping, channel harvest enablement, and repeated `ADDRDEC0`, `ADDRDEC1`, and `ADDRDEC2` selectors.
- IO read/write client grouping, combine-flush timers, group burst limits, and priority controls parallel to the GMI priority model.
- SDP arbitration, priority, credit, tag reserve, virtual-channel credit reserve, and request-control fields.
- Miscellaneous MMEA5 arbitration/link-manager options, latency sampler selection, performance counter configuration/result controls, EDC/RAS counters, and DSM/error-injection controls.

The practical purpose is to let AMDGPU code use symbolic bit names with register access helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `RREG32`, and `WREG32`, instead of embedding raw masks and shifts beside MMIO operations.

## Important APIs, Types, And Constants

This chunk exports no C API or type. Its interface is the macro namespace. The important families are:

- `MMEA5_GMI_RD_CLI2GRP_MAP1`, `MMEA5_GMI_WR_CLI2GRP_MAP0`, and `MMEA5_GMI_WR_CLI2GRP_MAP1`: 2-bit client ID group assignments. `MAP0` covers CIDs 0-15 and `MAP1` covers CIDs 16-31; this chunk starts midway through the read `MAP1` definition and then covers the write maps completely.
- `MMEA5_GMI_RD_GRP2VC_MAP` and `MMEA5_GMI_WR_GRP2VC_MAP`: 3-bit virtual-channel selections for groups 0-3.
- `MMEA5_GMI_RD_LAZY` and `MMEA5_GMI_WR_LAZY`: per-group delay fields plus request accumulation threshold, timeout, and idle maximum fields.
- `MMEA5_GMI_RD_CAM_CNTL` and `MMEA5_GMI_WR_CAM_CNTL`: per-group CAM depth, reorder limits, refill chaining, and page-based chaining controls.
- `MMEA5_GMI_PAGE_BURST`: 8-bit low/high read and write burst limits.
- `MMEA5_GMI_{RD,WR}_PRI_AGE`, `_PRI_QUEUING`, `_PRI_FIXED`, `_PRI_URGENCY`, `_PRI_URGENCY_MASKING`, and `_PRI_QUANT_PRI{1,2,3}`: four-group arbitration tuning. These describe aging rate/coefficient, queueing/fixed/urgency coefficients, urgency mode, per-client urgency masking for CIDs 0-31, and priority quantum thresholds.
- `MMEA5_ADDRNORM_BASE_ADDR{0,1,2,3}` and `MMEA5_ADDRNORM_MEGABASE_ADDR{0,1}`: address range valid bits, legacy MMIO hole enable, interleave channel/die/socket fields, interleave address selector, and base address fields. The matching limit registers carry destination fabric ID and limit address fields. `OFFSET_ADDR1` and `OFFSET_ADDR3` define high-address offset enable/value fields.
- `MMEA5_ADDRNORMDRAM_HOLE_CNTL`, `MMEA5_ADDRNORMGMI_HOLE_CNTL`, `MMEA5_ADDRNORMDRAM_NP2_CHANNEL_CFG`, `MMEA5_ADDRNORMGMI_NP2_CHANNEL_CFG`, `MMEA5_ADDRNORM_MEGACONTROL_ADDR{0,1}`, and `MMEA5_ADDRNORM{DRAM,GMI}_MASKING`: DRAM/GMI hole offsets, non-power-of-two 64K address space sizes, die-space sizing, and high-address masking.
- `MMEA5_ADDRDEC_BANK_CFG`, `MMEA5_ADDRDEC_MISC_CFG`, `MMEA5_ADDRDEC{DRAM,GMI}_HARVEST_ENABLE`, and `MMEA5_ADDRDEC{0,1,2}_*`: address-decoder field layouts for bank masks, bank group selection/interleave, VCM enables, PCH/channel/chip-select/rank masks, harvest masks for channels 0-5, chip-select base addresses, mask registers, address config registers, bank/row/channel selectors, column selectors, and rank-mapping selectors for primary and secondary chip selects.
- `MMEA5_IO_RD_CLI2GRP_MAP{0,1}`, `MMEA5_IO_WR_CLI2GRP_MAP{0,1}`, `MMEA5_IO_{RD,WR}_COMBINE_FLUSH`, `MMEA5_IO_GROUP_BURST`, and the `MMEA5_IO_{RD,WR}_PRI_*` families: IO-side equivalents for client grouping, flush timers, burst limits, and arbitration priority coefficients/masks/thresholds.
- `MMEA5_SDP_ARB_DRAM`, `MMEA5_SDP_ARB_GMI`, and `MMEA5_SDP_ARB_FINAL`: SDP arbitration controls for group selection, credit/retry behavior, round-robin or priority arbitration, and final request selection.
- `MMEA5_SDP_{DRAM,GMI,IO}_PRIORITY`, `MMEA5_SDP_CREDITS`, `MMEA5_SDP_TAG_RESERVE{0,1}`, `MMEA5_SDP_VCC_RESERVE{0,1}`, `MMEA5_SDP_VCD_RESERVE{0,1}`, and `MMEA5_SDP_REQ_CNTL`: per-group priorities, tag/read/write response credit limits, virtual-channel reserve pools, distributed-pool control, pass-PW overrides, chain overrides, inner-domain mode, and request block levels for read/write/atomic traffic.
- `MMEA5_MISC`: relative-priority enable bits for DRAM/GMI/IO read/write arbiters, per-VC early write return enables, early SDP original-data control, link-manager dynamic mode and timing thresholds, chip-select favoring, and write-to-read chip-select switching.
- `MMEA5_LATENCY_SAMPLING`: two sampler selectors across DRAM/GMI/IO, read/write/atomic request types, and virtual-channel masks.
- `MMEA5_PERFCOUNTER_LO`, `MMEA5_PERFCOUNTER_HI`, `MMEA5_PERFCOUNTER{0,1}_CFG`, and `MMEA5_PERFCOUNTER_RSLT_CNTL`: counter low/high fields, compare value, perf event range, mode, enable/clear bits, start/stop trigger masks, global enable/clear, and stop-on-saturate.
- `MMEA5_EDC_CNT` and `MMEA5_EDC_CNT2`: 2-bit SEC/DED/SED counter fields for DRAM read/write command memories, data memories, return tag memories, IO command/data memories, GMI command/page memories, and MAM D0-D3 memories.
- `MMEA5_DSM_CNTL`, `MMEA5_DSM_CNTLA`, and the beginning of `MMEA5_DSM_CNTL2`: DSM irritator data, single-write enable controls, and early error-injection controls for DRAM/GMI/IO command/page/data memory blocks.

## Control Flow And State Behavior

There is no local runtime control flow in this header. The macros become compile-time constants used by C files that already know the matching register offsets from `mmhub_1_7_offset.h`.

Runtime state is entirely hardware state:

- GMI and IO grouping/priority fields influence how client requests are grouped, delayed, reordered, masked for urgency, and mapped to virtual channels.
- Address normalization and decoder fields describe how incoming addresses are matched to ranges, transformed by high-address offsets, routed to destination fabric IDs, interleaved across channels/dies/sockets, and split into bank/row/column/rank/chip-select fields.
- SDP fields drive downstream arbitration, tag and response credit accounting, and request forwarding policy.
- `MISC`, latency sampling, and perf counter fields expose runtime tuning and observation controls for arbitration/link-manager behavior.
- EDC counter fields are hardware-maintained counts. `mmhub_v1_7.c` reads them through `mmhub_v1_7_query_ras_error_count()` and clears them in `mmhub_v1_7_reset_ras_error_count()` by writing zero to the relevant EDC count registers.
- DSM and error-injection fields describe diagnostic/test behavior; they do not provide any safety gate in the header itself.

Persistence is therefore register-defined. Values can persist until GPU reset, clock/power gating, firmware reprogramming, driver initialization, or an explicit counter reset. This file does not cache values in memory and has no save/restore sequencing.

## Dependencies And Integration Points

The masks are useful only with the matching address definitions in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_offset.h`, where this chunk's registers appear as `regMMEA5_GMI_*`, `regMMEA5_ADDRNORM*`, `regMMEA5_ADDRDEC*`, `regMMEA5_IO_*`, `regMMEA5_SDP_*`, `regMMEA5_MISC`, `regMMEA5_LATENCY_SAMPLING`, `regMMEA5_PERFCOUNTER*`, `regMMEA5_EDC_CNT*`, and `regMMEA5_DSM*` offsets.

The concrete consumer visible in this repository is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.c`. It includes `mmhub_1_7_sh_mask.h` and uses `SOC15_REG_FIELD(MMEA5_EDC_CNT, ...)` and `SOC15_REG_FIELD(MMEA5_EDC_CNT2, ...)` entries in `mmhub_v1_7_ras_fields[]` for MMHUB RAS reporting. The RAS path:

- associates subblock names such as `MMEA5_DRAMRD_CMDMEM`, `MMEA5_DRAMWR_CMDMEM`, `MMEA5_GMIRD_CMDMEM`, `MMEA5_GMIWR_DATAMEM`, and `MMEA5_MAM_D*MEM` with `regMMEA5_EDC_CNT` or `regMMEA5_EDC_CNT2`;
- decodes SEC/DED/SED bitfields through the generated masks and shifts;
- accumulates corrected errors into `ras_err_data.ce_count` and uncorrected errors into `ras_err_data.ue_count`;
- logs nonzero subblock counts and resets EDC counters by writing zero when MMHUB RAS is supported.

Other families in this chunk are register vocabulary for MMHUB initialization, firmware programming, diagnostics, register dumps, and low-level tuning paths. Even when no direct C reference appears for every macro in this source tree, the generated names must stay synchronized with the hardware register spec and offset header because table-driven register access code can construct `REG_SET_FIELD`/`REG_GET_FIELD` use from these names.

## Risks And Edge Cases

- Hardware contract drift is the dominant risk. A wrong shift or mask can silently program the wrong MMHUB arbitration, address decode, virtual-channel, or error-counter field.
- This chunk begins in the middle of `MMEA5_GMI_RD_CLI2GRP_MAP1`; the `CID16`-`CID19` shift definitions are in the previous chunk while their masks are visible here. Whole-file analysis must merge adjacent chunks before treating that register as complete.
- This chunk ends inside `MMEA5_DSM_CNTL2`. Only three shift definitions are present here; matching masks and later error-injection fields are in the next chunk. Do not infer complete DSM error-injection coverage from this chunk alone.
- The generated double suffix pattern is intentional for fields named `MASK`, for example `MMEA5_GMI_RD_PRI_URGENCY_MASKING__CID0_MASK_MASK`. Cleanup scripts must not collapse these names.
- Many packed fields use adjacent 2-bit, 3-bit, 4-bit, 5-bit, 6-bit, 7-bit, or 8-bit lanes. Off-by-one field widths are easy to miss and can corrupt neighboring settings.
- Address decode fields are especially sensitive. Incorrect `BASE_ADDR`, `LIMIT_ADDR`, `DST_FABRIC_ID`, `INTLV_*`, `CHAN_BIT`, bank/row/column selectors, or harvest masks can route memory requests to the wrong channel, chip select, rank, or fabric target.
- GMI/IO priority, lazy accumulation, CAM depth, reorder, and credit fields can affect fairness, latency, deadlock avoidance, and throughput. Bad defaults could show up as hangs or severe performance regressions rather than straightforward register errors.
- EDC counts are small 2-bit fields packed into 32-bit registers. Saturation, read-clear behavior, and reset semantics are hardware-defined; the driver RAS path assumes the masks identify the correct sub-counter and that writing zero resets the count registers.
- DSM and error-injection fields are diagnostic/destructive controls. Enabling them in normal runtime paths could inject memory errors or stress internal memories unexpectedly.
- High-bit masks such as `0x80000000L` and full-width fields such as `0xFFFFFFFFL` must be handled as unsigned 32-bit quantities. Signed shifts or implicit signed comparisons can misbehave in consumers.

## Test And Validation Signals

There are no direct unit tests for this macro-only chunk. Useful validation signals are:

- Compile coverage of `amdgpu/mmhub_v1_7.c` with this header and the matching `mmhub_1_7_offset.h`, especially the `SOC15_REG_FIELD(MMEA5_EDC_CNT, ...)` and `SOC15_REG_FIELD(MMEA5_EDC_CNT2, ...)` entries.
- Static consistency checks that every visible `_MASK` has the expected contiguous bit range for its matching `__SHIFT`, and that repeated register families use consistent layouts across read/write and GMI/IO variants.
- Cross-header validation that every `MMEA5_*` mask family in this chunk has a matching `regMMEA5_*` offset when the hardware register is addressable.
- RAS validation on MMHUB 1.7 hardware: inject or observe correctable/uncorrectable MMHUB errors, confirm `mmhub_v1_7_query_ras_error_count()` attributes nonzero counts to the expected `MMEA5_*` subblock, and confirm `mmhub_v1_7_reset_ras_error_count()` clears the relevant counters.
- Register-dump comparison against AMD's register specification for address normalization/decode and arbitration fields, with special attention to `ADDRDEC{0,1,2}` repeated layouts and `MMEA5_DSM_CNTL2` continuation across chunks.
- Runtime smoke tests for GPU memory traffic, GMI/IO request pressure, suspend/resume, reset, and RAS polling. Failures would likely present as hangs, page faults, unexpected RAS counts, or major latency/throughput changes.

## Chunk Notes For Merge Lane

This is one chunk of a much larger generated MMHUB 1.7 mask header. Merge it with neighboring chunks before preparing whole-file research. The beginning is a continuation of `MMEA5_GMI_RD_CLI2GRP_MAP1`, and the end is a continuation into `MMEA5_DSM_CNTL2`; the complete MMEA5 register story spans adjacent line ranges.
