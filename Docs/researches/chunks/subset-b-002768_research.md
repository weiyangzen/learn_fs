# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h lines 23546-25902

## Scope And Purpose

This chunk is a generated-style AMD MMHUB 1.7 register mask header segment. It contains C preprocessor constants only: each hardware register field is exported as a `<REGISTER>__<FIELD>__SHIFT` and/or `<REGISTER>__<FIELD>_MASK` macro. There are no functions, structs, storage objects, branches, loops, or direct MMIO accesses in this line range.

The line range covers the tail of `mmhub_ea_mmeadec4` and the beginning of `mmhub_ea_mmeadec5`. In practical driver terms, it is part of the bitfield contract for the MMEA4/MMEA5 MMHUB EA address-decode engines: address normalization, DRAM/GMI channel decode, IO/DRAM/GMI arbitration and priority, SDP routing, performance counters, EDC/RAS counters, DSM/error-injection controls, clock gating, error status, and early MMEA5 DRAM/GMI priority map fields.

The source path is important because this header is paired with the matching MMHUB 1.7 offset header and the `amdgpu/mmhub_v1_7.c` implementation. The masks in this chunk let runtime code use symbolic register-field helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, and `SOC15_REG_FIELD` without open-coded bit literals.

## Important APIs, Types, And Constants

There are no callable APIs or C types defined here. The usable interface is the macro namespace.

Major macro groups in this chunk:

- `MMEA4_ADDRNORM_*`: address-normalization base/limit, mega-range, DRAM/GMI hole, NP2 channel, global control, mega-control, and masking fields. These describe validity, legacy MMIO hole handling, interleave channel/die/socket selection, base/limit address pieces, destination fabric IDs, DRAM/GMI hole offsets, and address-mask controls.
- `MMEA4_ADDRDEC_*`: bank and miscellaneous address-decode controls plus DRAM/GMI harvest force bits. The repeated `ADDRDEC[0-2]_*` groups define chip-select enable/base registers, address masks, DRAM geometry (`NUM_BANK_GROUPS`, `NUM_RM`, row/column/bank counts), bank/row/column bit selectors, channel bit selectors, and row-machine inversion fields for primary and secondary chip-select pairs.
- `MMEA4_IO_*`: IO read/write client-to-priority-group maps for CIDs 0-31, combine-flush timers, group burst limits, aging/queuing/fixed/urgency coefficients, per-CID urgency masking, and quantum-priority thresholds.
- `MMEA4_SDP_*`: DRAM/GMI/final SDP arbitration controls, DRAM/GMI/IO priority maps, credit limits, tag and VCC/VCD reserve controls, and request-control fields.
- `MMEA4_MISC`, `MMEA4_MISC2`, and `MMEA4_MISC_AON`: miscellaneous routing, request blocking, swap, stall, bypass, clock, and always-on link-manager fields.
- `MMEA4_LATENCY_SAMPLING` and `MMEA4_PERFCOUNTER*`: latency sampler enables/reset/count/type fields and two performance-counter configuration/result-control register layouts.
- `MMEA4_EDC_CNT`, `MMEA4_EDC_CNT2`, and `MMEA4_EDC_CNT3`: compact 2-bit single-error, double-error, and syndrome/error counters for DRAM, GMI, IO, return-tag, page memory, and MAM submemories.
- `MMEA4_DSM_CNTL*`: diagnostic/syndrome-memory controls and error-injection fields. These expose irritator data, single-write enable, error-injection enable, per-memory injection delay selectors, and global delay fields.
- `MMEA4_CGTT_CLK_CTRL`, `MMEA4_EDC_MODE`, and `MMEA4_ERR_STATUS`: clock-gating delay/override fields, EDC bypass/propagation/counting mode, and fatal/read/write response status bits including `CLEAR_ERROR_STATUS`.
- `MMEA4_ADDRDEC_SELECT`: selects DRAM and GMI address-decode channel start/end ranges.
- `MMEA5_DRAM_*` and early `MMEA5_GMI_RD_CLI2GRP_MAP*`: the beginning of the next EA decode block. This includes DRAM read/write client-to-group maps, group-to-virtual-channel maps, lazy/CAM/page-burst controls, priority coefficients, urgency modes, and quantum thresholds, followed by the start of GMI read client-to-group mapping.

The macros all represent 32-bit register field layouts. Common packing patterns include 2-bit group/CID fields at shifts `0, 2, 4, ...`, 3-bit priority coefficients at shifts `0, 3, 6, 9`, 4-bit row/column selectors at nibble boundaries, and full high address masks such as `0xFFFFF000L` or `0xFFFFFFFEL`.

## Control Flow And State Behavior

This header chunk has no local control flow. Its behavior appears when other AMDGPU files include it and compile the masks into register reads, writes, or field decoders.

Runtime state is hardware-owned:

- Address-normalization and address-decode fields shape how MMEA4 maps physical/fabric address ranges into DRAM or GMI resources, including chip-select windows, base/mask matching, row/column/bank extraction, channel selection, interleave geometry, and harvested/forced bank bits.
- IO, DRAM, and GMI priority fields influence arbitration policy for request classes. Client-to-group maps assign CIDs to four groups, group-to-VC maps select virtual channels, and age/queue/fixed/urgency/quantum fields determine when traffic is promoted or throttled.
- SDP and reserve fields control downstream request arbitration, credit reservation, tag/VCC/VCD reserve behavior, and request throttling/blocking. These values affect live traffic scheduling rather than any software data structure.
- EDC counters and error status fields are observed by RAS code. Counters accumulate in MMHUB hardware until reset by the driver or hardware reset, while `ERR_STATUS` records fatal/read/write response status and is cleared by writing `CLEAR_ERROR_STATUS`.
- DSM and error-injection fields are diagnostic controls. They can deliberately perturb internal memories or select injection timing; their persistence and side effects are hardware-defined and reset/power-state dependent.
- Clock-gating and EDC mode fields configure hardware block behavior. They are not cached by this header; any restore policy must live in the MMHUB implementation, firmware, or broader ASIC reset/resume flows.

The chunk itself does not enforce sequencing. Any consumer that changes address decode, arbitration, EDC, DSM, or clock-gating fields must handle hardware quiescing, read-modify-write ordering, polling, and reset interactions outside this file.

## Dependencies And Integration Points

This header depends on matching register-address definitions in `mmhub_1_7_offset.h`. For example, the same MMEA4 block appears under `addressBlock: mmhub_ea_mmeadec4`, with offsets such as `regMMEA4_ADDRNORM_MEGABASE_ADDR1`, `regMMEA4_ADDRDEC0_BASE_ADDR_CS0`, `regMMEA4_IO_RD_CLI2GRP_MAP0`, `regMMEA4_EDC_CNT`, and `regMMEA4_ERR_STATUS`. The MMEA5 definitions continue in the following address block.

Important in-tree consumers:

- `drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.c` includes `mmhub/mmhub_1_7_offset.h` and this mask header. It uses `SOC15_REG_FIELD(MMEA4_EDC_CNT, ...)`, `SOC15_REG_FIELD(MMEA4_EDC_CNT2, ...)`, `SOC15_REG_FIELD(MMEA4_EDC_CNT3, ...)`, and the matching MMEA5 fields to build RAS field tables for MMHUB ranges 4 and 5.
- The same file builds `mmhub_v1_7_edc_cnt_regs` from `regMMEA4_EDC_CNT`, `regMMEA4_EDC_CNT2`, `regMMEA4_EDC_CNT3`, `regMMEA5_EDC_CNT`, `regMMEA5_EDC_CNT2`, and `regMMEA5_EDC_CNT3`, then reads them in `mmhub_v1_7_query_ras_error_count()` and clears them in `mmhub_v1_7_reset_ras_error_count()`.
- `mmhub_v1_7_query_ras_error_status()` and `mmhub_v1_7_reset_ras_error_status()` iterate over `regMMEA0_ERR_STATUS` through `regMMEA5_ERR_STATUS`. The code decodes status using the shared MMEA error-status field layout and clears errors by setting `CLEAR_ERROR_STATUS`.
- Later MMHUB generations, including `mmhub_v9_4.c` and `mmhub_9_4_1_sh_mask.h`, mirror the same generated field pattern. That makes this chunk part of a cross-generation register contract, not a standalone hand-written interface.
- Lower-level register helpers from the SOC15 AMDGPU infrastructure consume these macros through token-pasting. If a field name, mask suffix, or shift suffix is renamed, `SOC15_REG_FIELD` and `REG_{GET,SET}_FIELD` users fail to build or silently decode the wrong bits if the name still resolves to a bad value.

## Risks And Edge Cases

- Hardware contract drift is the dominant risk. A wrong mask or shift can misprogram MMEA4/MMEA5 address windows, route traffic to the wrong fabric target, corrupt DRAM/GMI chip-select decoding, or make RAS counters report the wrong subblock.
- This range starts in the middle of the `MMEA4_ADDRNORM_MEGALIMIT_ADDR0` definition pair: only the two mask lines are inside the chunk, while its shift definitions are in the previous chunk. The merge lane should join adjacent chunks before making whole-register coverage claims.
- This range ends in the middle of `MMEA5_GMI_RD_CLI2GRP_MAP1`; only the early CID16-CID19 shift lines are included at the tail. The remainder of that register belongs to the next chunk.
- The `MMEA4_ADDRDEC[0-2]_*` groups are highly repetitive. Mechanical edits or generated-regeneration mismatches can easily swap `CS01` and `CS23`, primary and secondary chip-selects, low and high column selectors, or address-decode instance numbers.
- Many fields have high-bit masks such as `0x80000000L`, `0xC0000000L`, or full-width masks. Consumers should keep operations unsigned and 32-bit, and avoid signed intermediate shifts.
- Several fields are operationally dangerous if written at the wrong time: `BLOCK_REQUESTS`, `CLEAR_ERROR_STATUS`, EDC bypass/propagation, DSM single-write/error-inject enables, address-decode enable/base/mask fields, clock-gating overrides, and priority/credit settings can alter live request handling.
- RAS error status handling in `mmhub_v1_7.c` uses the MMEA0 error-status field names to decode all MMEA instances because the layout is replicated. If one later instance diverged from that common layout, the current shared decode approach would become incorrect.
- Diagnostic EDC/DSM controls can intentionally generate or mask errors. Tests that exercise them need strict cleanup so injected errors do not look like persistent hardware faults.

## Test And Validation Signals

There are no unit tests for this generated macro chunk. Useful validation signals are build-time and hardware integration checks:

- Compile AMDGPU with `mmhub_v1_7.c` enabled. This verifies that `SOC15_REG_FIELD` can resolve all MMEA4/MMEA5 EDC counter fields used by the RAS tables.
- Static mask/shift checks: each `_MASK` should match its `_SHIFT` and field width; repeated CID map registers should pack 16 2-bit fields into 32 bits; priority coefficient registers should pack four 3-bit fields; column/bank selector registers should use nibble-aligned 4-bit or 5-bit masks as specified.
- Register-address alignment checks against `mmhub_1_7_offset.h`: every macro base in this chunk should have a matching `reg<base>` definition in the offset header, except where the chunk intentionally begins or ends mid-register.
- RAS runtime smoke tests on MMHUB 1.7 hardware: `mmhub_v1_7_query_ras_error_count()` should report nonzero SEC/DED values under controlled injection and zero/expected counts after `mmhub_v1_7_reset_ras_error_count()`.
- Error-status tests should verify that fatal/read/write response bits are detected and that writing `CLEAR_ERROR_STATUS` clears the relevant MMEA instance without clearing unrelated state.
- Suspend/resume, GPU reset, and SR-IOV paths should be checked for MMHUB stability because this header defines fields whose state may be reinitialized by firmware or the driver after reset.
- Performance and traffic tests should watch for regressions in memory/GMI/IO latency or starvation after any change to arbitration, grouping, burst, priority, or credit-reserve masks.

## Chunk Notes For Merge Lane

This is one chunk of a much larger generated register mask header. The whole-file research should merge it with adjacent chunks for `mmhub_1_7_sh_mask.h` before summarizing complete MMEA4/MMEA5 coverage. This specific range is best treated as: tail of MMEA4 address-normalization and address-decode masks, full MMEA4 IO/SDP/perf/RAS/DSM/error-status mask coverage, and the beginning of MMEA5 DRAM/GMI arbitration masks.
