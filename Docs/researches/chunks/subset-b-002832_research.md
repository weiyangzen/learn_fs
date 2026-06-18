# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_3_0_sh_mask.h lines 4744-7094

## Scope

This chunk is a middle range of the generated AMDGPU MMHUB 9.3.0 shift/mask header. It contains only C preprocessor constants for register-field bit positions and bit masks. There are no functions, structs, storage declarations, includes, or executable branches in this range.

The chunk begins in the middle of `MMEA0_IO_WR_PRI_URGENCY_MASK`, then completes the remaining `MMEA0` arbiter, SDP, performance, EDC, DSM, clock-gating, and error-status field definitions. It then starts the parallel `MMEA1` register block, covering DRAM arbitration, DRAM address normalization/decoding, IO arbitration, SDP, performance, and EDC fields before ending in the middle of `MMEA1_DSM_CNTL`.

The constants in this file must be paired with `mmhub_9_3_0_offset.h`, which supplies matching `mmMMEA*` register offsets. In this tree there is no exact C runtime file including `mmhub_9_3_0_sh_mask.h`; nearby MMHUB generations, especially `amdgpu/mmhub_v9_4.c`, show the same SOC15-style integration pattern for `MMEA*` EDC/RAS fields.

## Purpose

The purpose of this chunk is to expose the bit-level software contract for two MMHUB memory-macro/arbiter instances, `MMEA0` and `MMEA1`, on MMHUB 9.3.0 hardware. These register definitions describe how software can compose or decode MMIO values for:

- DRAM and IO client-to-group mapping.
- Read/write group-to-virtual-channel mapping.
- DRAM address normalization, bank/channel/hash/harvest configuration, chip-select base/mask/config/select fields, column selection, and row-machine selection.
- DRAM and IO priority arbitration, aging, queuing, fixed priority, urgency, urgency masking, and quantum thresholds.
- SDP arbitration limits, response/tag credit reservation, virtual-channel credit reservation, request overrides, and miscellaneous link-manager behavior.
- Latency sampling and per-instance performance counters.
- EDC/RAS correctable, deferred, and single-error-detected counter fields.
- DSM irritator and single-write controls used for memory-test or debug-style behavior.
- Clock gating/training-test control and error status fields.

The macros are generated ABI-like data: driver code, debug tooling, firmware-facing paths, or RAS/perf code can rely on exact `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` names and values to program 32-bit registers safely.

## Important Macro Families

### `MMEA0` IO Priority Tail

The first visible lines finish `MMEA0_IO_WR_PRI_URGENCY_MASK`, defining one bit per client ID from `CID4_MASK` through `CID31_MASK` in the visible range. The matching shifts for the full register start before this chunk. The following `MMEA0_IO_RD_PRI_QUANT_PRI1..3` and `MMEA0_IO_WR_PRI_QUANT_PRI1..3` blocks define four 8-bit `GROUP0_THRESHOLD` through `GROUP3_THRESHOLD` fields per priority-quantum register.

These fields belong with the `mmMMEA0_IO_*` offsets around `0x01dc` through `0x01eb` in `mmhub_9_3_0_offset.h`. They govern IO read/write arbitration policy by group and client ID.

### `MMEA0` SDP Arbitration and Credits

The `MMEA0_SDP_ARB_DRAM` and `MMEA0_SDP_ARB_FINAL` blocks define burst-limit and switching controls:

- DRAM arbitration has `RDWR_BURST_LIMIT_CYCL`, `RDWR_BURST_LIMIT_DATA`, early read/write switching on priority or reservation, and `EOB_ON_EXPIRE`.
- Final SDP arbitration splits burst limits across DRAM, GMI, and IO, adds `BURST_LIMIT_MULTIPLIER`, read-only controls for `VC0..VC7`, and error policy bits `ERREVENT_ON_ERROR` and `HALTREQ_ON_ERROR`.

`MMEA0_SDP_DRAM_PRIORITY` and `MMEA0_SDP_IO_PRIORITY` define 4-bit priorities for read and write groups 0 through 3. `MMEA0_SDP_CREDITS` defines tag, write-response, and read-response credit limits. `MMEA0_SDP_TAG_RESERVE0/1`, `MMEA0_SDP_VCC_RESERVE0/1`, and `MMEA0_SDP_VCD_RESERVE0/1` reserve tag and credit resources by virtual channel.

### `MMEA0` Request, Misc, Latency, and Perf Counters

`MMEA0_SDP_REQ_CNTL` contains request override bits for read, write, atomic, and DRAM-chain behavior plus `INNER_DOMAIN_MODE`.

`MMEA0_MISC` defines relative-priority selection for DRAM/GMI/IO read and write arbiters, return-data swap behavior, early SDP original-data behavior, link-manager dynamic mode, halt/reconnect/idle thresholds, midchain/last chip-select favoring, and write-to-read switch controls.

`MMEA0_LATENCY_SAMPLING` defines two independent samplers. Each sampler can filter by DRAM/GMI/IO, read/write/atomic-return/atomic-no-return traffic, and virtual channel. The VC fields are eight-bit masks at `SAMPLER0_VC` and `SAMPLER1_VC`.

`MMEA0_PERFCOUNTER_LO`, `MMEA0_PERFCOUNTER_HI`, `MMEA0_PERFCOUNTER0_CFG`, `MMEA0_PERFCOUNTER1_CFG`, and `MMEA0_PERFCOUNTER_RSLT_CNTL` define low/high counter value fields, high-word compare value, event-selection ranges, counter mode, enable/clear bits, trigger selectors, global enable, clear-all, and stop-on-saturate behavior.

### `MMEA0` EDC, DSM, Clock, and Error Fields

`MMEA0_EDC_CNT` and `MMEA0_EDC_CNT2` expose compact 2-bit counters for memory error classes:

- DRAM read command memory SEC/DED.
- DRAM write command memory SEC/DED.
- DRAM write data memory SEC/DED.
- Read-return and write-return tag memory SEC/DED.
- DRAM page memory SED.
- IO read/write command memory SED.
- IO write data memory SED.
- GMI read/write command memory SEC/DED.
- GMI write data memory SEC/DED.
- GMI page memory SED.

`MMEA0_DSM_CNTL`, `MMEA0_DSM_CNTLA/B`, `MMEA0_DSM_CNTL2`, and `MMEA0_DSM_CNTL2A/B` define DSM irritator data and single-write enable fields for the same memory categories, with duplicated A/B blocks for command/data/page/tag domains.

`MMEA0_CGTT_CLK_CTRL` has test clock-gating and handshake fields such as `SOFT_OVERRIDE0..3`, `ACTIVATE`, `WEIGHT`, delay, `LS_OVERRIDE`, and auto-calibration controls. `MMEA0_EDC_MODE` enables EDC-related operation for command, data, page, tag, and auto mode. `MMEA0_ERR_STATUS` reports address and credit FIFO error bits, split between clearable and raw status fields. `MMEA0_MISC2` currently exposes `TAG_PARITY_CHECK_EN`.

### `MMEA1` DRAM Arbitration and Address Decoding

The `MMEA1` block starts at `MMEA1_DRAM_RD_CLI2GRP_MAP0`. `DRAM_RD_CLI2GRP_MAP0/1` and `DRAM_WR_CLI2GRP_MAP0/1` assign client IDs `CID0..CID31` to four arbitration groups using two-bit fields. `MMEA1_DRAM_RD_GRP2VC_MAP` and `MMEA1_DRAM_WR_GRP2VC_MAP` then map groups 0 through 3 to virtual channels.

`MMEA1_DRAM_RD_LAZY`, `MMEA1_DRAM_WR_LAZY`, `MMEA1_DRAM_RD_CAM_CNTL`, `MMEA1_DRAM_WR_CAM_CNTL`, and `MMEA1_DRAM_PAGE_BURST` define lazy timer, header/response age, hash modes, CAM enablement, CAM depth, sequence maintenance, and page-burst controls.

The priority blocks mirror the IO priority pattern:

- `MMEA1_DRAM_RD_PRI_AGE` and `MMEA1_DRAM_WR_PRI_AGE` define 8-bit per-group aging limits.
- `MMEA1_DRAM_RD_PRI_QUEUING` and `MMEA1_DRAM_WR_PRI_QUEUING` define 2-bit per-group queuing priorities.
- `MMEA1_DRAM_RD_PRI_FIXED` and `MMEA1_DRAM_WR_PRI_FIXED` define 2-bit fixed priorities.
- `MMEA1_DRAM_RD_PRI_URGENCY` and `MMEA1_DRAM_WR_PRI_URGENCY` define 4-bit per-group urgency.
- `MMEA1_DRAM_*_QUANT_PRI1..3` define 8-bit per-group quantum thresholds.

The `MMEA1_ADDRNORM*`, `MMEA1_ADDRDEC*`, and `MMEA1_ADDRDECDRAM*` groups are the densest register families in this chunk. They describe normalized DRAM apertures, hole control, tri-channel config, bank config, misc decoder settings, address hash selection for banks/page control/chip selects, harvest enablement, base addresses for primary and secondary chip selects, masks for chip-select pairs, chip-select address configuration, address bit selection, column bit selection, and row-machine selection for two decoder instances (`ADDRDEC0` and `ADDRDEC1`).

### `MMEA1` IO, SDP, Perf, EDC, and DSM Start

`MMEA1_IO_RD_CLI2GRP_MAP0/1` and `MMEA1_IO_WR_CLI2GRP_MAP0/1` mirror the `MMEA1` DRAM client mapping layout for IO traffic. `MMEA1_IO_RD_COMBINE_FLUSH`, `MMEA1_IO_WR_COMBINE_FLUSH`, and `MMEA1_IO_GROUP_BURST` add flush timers and per-group burst behavior. The `MMEA1_IO_*_PRI_*`, urgency-mask, and quantum-priority blocks then mirror the same age/queuing/fixed/urgency/threshold layout used by `MMEA0`.

`MMEA1_SDP_*`, `MMEA1_MISC`, `MMEA1_LATENCY_SAMPLING`, and `MMEA1_PERFCOUNTER*` mirror the `MMEA0` SDP, misc, latency sampling, and perf-counter register layouts. The corresponding offsets in `mmhub_9_3_0_offset.h` run from `mmMMEA1_SDP_ARB_DRAM` at `0x032c` through `mmMMEA1_PERFCOUNTER_RSLT_CNTL` at `0x0340`.

The chunk then defines `MMEA1_EDC_CNT` and `MMEA1_EDC_CNT2` with the same 2-bit SEC/DED/SED counter fields described for `MMEA0`. It ends in the middle of `MMEA1_DSM_CNTL`, after defining DRAM, return-tag, and GMI DSM irritator/single-write fields through `GMIWR_DATAMEM_ENABLE_SINGLE_WRITE_MASK`; `MMEA1_DSM_CNTLA` and later DSM definitions continue in the next chunk.

## Control Flow and Runtime Use

There is no control flow in this header chunk. Runtime behavior comes from code that includes the generated shift/mask header and uses these macros with matching offsets.

The common AMDGPU usage pattern is:

1. Select the correct register offset from `mmhub_9_3_0_offset.h`, such as `mmMMEA1_EDC_CNT`.
2. Use a field macro from this header through helpers such as `SOC15_REG_FIELD`, `REG_SET_FIELD`, or `REG_GET_FIELD`.
3. Read or write the 32-bit MMIO register through SOC15 helpers such as `RREG32_SOC15`, `WREG32_SOC15`, or `SOC15_REG_OFFSET`.

Nearby generation code in `amdgpu/mmhub_v9_4.c` illustrates direct RAS integration for the same `MMEA*` family: it builds `soc15_ras_field_entry` rows using `SOC15_REG_ENTRY(MMHUB, 0, mmMMEA0_EDC_CNT)` and `SOC15_REG_FIELD(MMEA0_EDC_CNT, DRAMRD_CMDMEM_SEC_COUNT)` style macros, then lists EDC counter registers for reset/collection. MMHUB 9.3.0 does not have an exact runtime include in this checked tree, so direct in-tree execution for these 9.3.0 constants was not found.

## State and Persistence Behavior

This file stores no software state. It names hardware state in MMIO registers. Values represented by these masks persist in the GPU register file until reset, power-gating loss, suspend/resume reinitialization, firmware/PF reprogramming, or explicit driver writes.

The state represented here is high impact:

- Priority, urgency, aging, and quantum fields can change DRAM/IO fairness and latency for clients.
- Client-to-group and group-to-VC maps determine which clients share arbitration groups and virtual channels.
- Address normalization and address-decoder fields control how physical DRAM addresses map to banks, channels, chip selects, columns, rows, and harvested regions.
- SDP credit and reserve fields govern outstanding tags and response credits; over-reservation can starve traffic while under-reservation can expose backpressure or ordering problems.
- Perf-counter and latency-sampling registers are diagnostic state and should be programmed/cleared consistently around sampling windows.
- EDC counters are RAS-observable hardware counters. They may be read, logged, and cleared by RAS flows, so field masks must preserve correct SEC/DED/SED classification.
- DSM and clock/test-control fields are debug/test state. Accidentally enabling irritator or test clock controls in production paths could perturb memory behavior.

## Dependencies and Integration Points

Generated-register dependencies:

- `mmhub_9_3_0_offset.h` provides the corresponding `mmMMEA0_*` and `mmMMEA1_*` register offsets. The visible chunk pairs with offsets such as `mmMMEA0_IO_RD_PRI_QUANT_PRI1` at `0x01e6`, `mmMMEA0_EDC_CNT` at `0x0206`, `mmMMEA1_DRAM_RD_CLI2GRP_MAP0` at `0x0240`, `mmMMEA1_IO_RD_PRI_URGENCY_MASK` at `0x0324`, and `mmMMEA1_EDC_CNT2` at `0x0347`.
- Earlier chunks of `mmhub_9_3_0_sh_mask.h` define the start of `MMEA0`, including the fields that precede the visible `MMEA0_IO_WR_PRI_URGENCY_MASK` tail.
- Later chunks define the rest of `MMEA1_DSM_CNTL` and the remaining `MMEA1` register families after line 7094.
- SOC15 register macros depend on the generated naming convention: `SOC15_REG_FIELD(MMEA1_EDC_CNT, DRAMRD_CMDMEM_SEC_COUNT)` expands through this header's `MMEA1_EDC_CNT__DRAMRD_CMDMEM_SEC_COUNT_MASK` and shift macro.

Driver and subsystem integration:

- MMHUB RAS code in nearby generations uses `MMEA*_EDC_CNT*` fields to build error-counter tables. The fields in this chunk are the natural source for any MMHUB 9.3.0 RAS table that reports SEC, DED, or SED counts.
- Performance and debug tools can use `MMEA*_PERFCOUNTER*` and `MMEA*_LATENCY_SAMPLING` for sampling MMEA traffic classes and VC activity.
- Memory-training, firmware, or low-level bring-up code can depend on `MMEA*_ADDRDEC*`, `MMEA*_ADDRNORM*`, and `MMEA*_ADDRDECDRAM*` to reflect the actual DRAM topology and harvest state.
- SR-IOV/PF-VF ownership matters for these registers. Address-decoder, RAS, DSM, and arbitration policy registers are typically PF-owned or firmware-owned resources; VF code should not assume it can safely program them.

## Risks and Edge Cases

- Mixing `mmhub_9_3_0_sh_mask.h` with another generation's offset header can silently program wrong registers or bit positions. Many `MMEA*` names recur across MMHUB generations.
- This chunk starts and ends across register boundaries. A merge or generated-header split that drops the preceding `MMEA0_IO_WR_PRI_URGENCY_MASK` shifts, or the following `MMEA1_DSM_CNTL` continuation, will leave incomplete research context and may hide field-pairing mistakes.
- Client-to-group maps use dense 2-bit fields for 32 client IDs across paired registers. Off-by-one client IDs can move traffic into the wrong arbitration group.
- Urgency mask registers use one bit per client ID. Wrong polarity or wrong CID bit can make a client permanently urgent or permanently masked from urgency handling.
- Address decoder fields are topology-sensitive. Incorrect base, mask, select, column, row-machine, hash, or harvest fields can misroute memory traffic, corrupt data, or break memory interleaving.
- SDP credit/tag reservations can deadlock or starve traffic if programmed inconsistently with hardware capacity and VC policy.
- RAS EDC counters pack many 2-bit fields into one register. A bad mask can swap SEC and DED accounting or hide uncorrectable/deferred conditions from RAS reporting.
- DSM irritator and single-write fields should be treated as test/debug controls. Unexpected writes to these fields can intentionally inject unusual memory behavior.
- Read-modify-write users must preserve reserved bits. These masks are field-level helpers, not whole-register default values.

## Test and Verification Signals

Useful validation signals for this chunk are generated-header build coverage, register-field expansion checks, and hardware readback on supported ASICs:

- Compile any MMHUB 9.3.0 consumer with both `mmhub_9_3_0_offset.h` and `mmhub_9_3_0_sh_mask.h` included, ensuring all `SOC15_REG_FIELD`, `REG_SET_FIELD`, and `REG_GET_FIELD` references resolve.
- Add or run static checks that every visible `REGISTER__FIELD__SHIFT` has a matching `REGISTER__FIELD_MASK` where appropriate, especially for cross-boundary `MMEA0_IO_WR_PRI_URGENCY_MASK` and `MMEA1_DSM_CNTL`.
- RAS tests should read `MMEA0_EDC_CNT`, `MMEA0_EDC_CNT2`, `MMEA1_EDC_CNT`, and `MMEA1_EDC_CNT2`, decode SEC/DED/SED fields, and verify that clear/readback flows do not conflate adjacent 2-bit counters.
- Perf tests should program `MMEA*_PERFCOUNTER*_CFG`, enable counting through `MMEA*_PERFCOUNTER_RSLT_CNTL`, and verify low/high counter readback plus clear and stop-on-saturate behavior.
- Latency-sampling tests should toggle sampler filters and VC masks and verify only expected DRAM/GMI/IO and read/write/atomic traffic is counted.
- Firmware or bring-up validation should compare `MMEA1_ADDRDEC*` and `MMEA1_ADDRNORM*` readback against expected DRAM topology, chip-select layout, hash, and harvest state.
- Arbitration smoke tests should exercise representative DRAM and IO clients under load and look for starvation, unexpected latency spikes, or deadlocks after priority/credit programming.
- Suspend/resume, GPU reset, and SR-IOV tests should verify that PF-owned MMEA arbitration, address-decoder, EDC, and debug/test registers are restored or left under firmware ownership as appropriate.

## Cross-Chunk Notes

This chunk is not a complete per-file view. The final reconciliation report should merge it with earlier chunks that define the beginning of `MMEA0` and with later chunks that complete `MMEA1_DSM_CNTL` plus the remaining MMEA/MMHUB 9.3.0 register blocks. The source path and line range above should remain attached to this chunk because it covers only lines 4744-7094.
