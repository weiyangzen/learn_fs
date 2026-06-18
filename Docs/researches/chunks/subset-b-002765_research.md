# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h lines 16498-18857

## Scope And Purpose

This chunk is a generated-style AMD MMHUB 1.7 register shift/mask header slice. It contains only C preprocessor constants that describe bit positions and masks for memory-mapped MMHUB registers. There are no functions, structs, enums, storage objects, or local executable paths in this line range.

The slice starts in the tail of `MMEA1_DSM_CNTL2` masks and then covers `MMEA1` controls for error injection, clock gating, EDC/error status, miscellaneous arbitration, address-decode selection, and always-on link-manager timing. Most of the range is the `// addressBlock: mmhub_ea_mmeadec2` block, which defines `MMEA2` arbitration, address normalization, address decode, GMI, DRAM, and IO priority fields. The range ends in the middle of `MMEA2_IO_WR_PRI_URGENCY_MASKING`, after CID26 shift definitions and before the remaining fields for that register.

The purpose of these macros is to let AMDGPU code form and decode MMIO register values with helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15`, while register addresses come from the paired `mmhub_1_7_offset.h` header.

## Important APIs, Types, And Constants

This chunk exports constants rather than APIs. The macro naming contract is `<REGISTER>__<FIELD>__SHIFT` for bit positions and `<REGISTER>__<FIELD>_MASK` for corresponding register masks.

Important register families in this slice are:

- `MMEA1_DSM_CNTL2` tail and `MMEA1_DSM_CNTL2A`: error-injection controls for GMI read/write command memory, GMI write data memory, page memory, IO command/data memory, DRAM read/write page memory, and an injection-delay selector. `MMEA1_DSM_CNTL2B` appears only as an empty register marker in this range.
- `MMEA1_CGTT_CLK_CTRL`: memory-client clock-gating timing and overrides, including on delay, off hysteresis, soft stall overrides for write/read/return paths, light-sleep override, and soft override bits.
- `MMEA1_EDC_MODE`, `MMEA1_ERR_STATUS`, and `MMEA1_EDC_CNT3`: EDC behavior, fatal/uncorrectable status propagation, clear/error/busy status bits, interrupt policy bits, and DED count fields for DRAM, IO, and GMI page/command memories.
- `MMEA1_MISC2`, `MMEA1_ADDRDEC_SELECT`, and `MMEA1_MISC_AON`: arbitration swaps, burst limits, IO read/write priority enablement, request blocking/status, DRAM/GMI channel range selection, and always-on link-manager part-ack hysteresis/deassert mode.
- `MMEA2_DRAM_*`: DRAM read/write client-to-group maps for CIDs 0-31, group-to-VC maps, lazy request accumulation timers and thresholds, CAM depth/reorder/refill controls, page burst limits, and age/queue/fixed/urgency/quantum-priority coefficients.
- `MMEA2_GMI_*`: the same group mapping, lazy, CAM, page burst, age, queue, fixed, urgency, quantum-priority, and per-CID urgency masking surfaces for GMI traffic. GMI CAM control adds `PAGEBASED_CHAINING` along with refill-chain control.
- `MMEA2_ADDRNORM*` and `MMEA2_ADDRDEC*`: address range validation, legacy MMIO hole enablement, interleave topology fields, base/limit/offset and mega-base/mega-limit ranges, DRAM/GMI hole controls, non-power-of-two channel config, bank and bank-group selection, harvest enable overrides, and three repeated address-decode sets (`ADDRDEC0`, `ADDRDEC1`, `ADDRDEC2`) with chip-select base addresses, masks, row/column/bank/RM selections, secondary chip-select selections, and row-MSB inversion controls.
- `MMEA2_IO_*`: IO read/write client-to-group maps, combine-flush controls for CIDs, group burst limits, age/queue/fixed/urgency coefficients, urgency modes, and per-CID urgency masks. This chunk cuts off before the full write urgency-masking register is visible.

Representative layouts include two-bit client group fields packed across 32 CIDs, three-bit group coefficient fields for four groups, 8-bit burst/threshold lanes, single-bit control/status masks, and full upper-bit address masks such as `0xFFFFFFFEL` for base/mask registers with enable at bit 0.

## Control Flow And State Behavior

There is no local control flow in this header. Runtime control flow exists in consumers that include this header and the paired offset header.

In `amdgpu/mmhub_v1_7.c`, the MMHUB 1.7 code includes `mmhub/mmhub_1_7_offset.h` and `mmhub/mmhub_1_7_sh_mask.h`, then programs VM, aperture, TLB, cache, snoop, and power-management registers through SOC15 register helpers. The MMEA EDC and error-status families are integrated with the RAS path: `mmhub_v1_7_ras_fields` uses `SOC15_REG_FIELD(...)` entries for MMEA EDC counters, `mmhub_v1_7_query_ras_error_count()` decodes those counters, and `mmhub_v1_7_query_ras_error_status()` reads EA error-status registers and checks `SDP_RDRSP_STATUS`, `SDP_WRRSP_STATUS`, and `SDP_RDRSP_DATAPARITY_ERROR`.

The state represented here is hardware state. Error injection, EDC mode, error status, clock gating, arbitration, address normalization/decode, and priority coefficients persist in the MMHUB register file until reset, power-gating loss, firmware/driver reprogramming, or explicit counter/status clear operations. The header does not cache values, validate field ranges, serialize MMIO accesses, or define reset sequencing.

Some fields are configuration state, such as client-to-group maps, address-decode selectors, lazy thresholds, CAM depths, and priority coefficients. Others are status or command-like fields, such as `REQUESTS_BLOCKED`, `CLEAR_ERROR_STATUS`, EDC counters, combine-flush CIDs, and error-injection enable/delay bits. Correct read-modify-write semantics are owned by the hardware specification and by AMDGPU call sites, not by these masks.

## Dependencies And Integration Points

The direct companion for this chunk is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_offset.h`, which provides `regMMEA1_*` and `regMMEA2_*` offsets matching these masks. `amdgpu/mmhub_v1_7.c` is the primary in-tree MMHUB 1.7 consumer.

Register access integrates through the SOC15 AMDGPU register layer: `SOC15_REG_ENTRY`, `SOC15_REG_FIELD`, `SOC15_REG_ENTRY_OFFSET`, `RREG32`, `WREG32`, `RREG32_SOC15`, `WREG32_SOC15`, and offset variants. Field packing and unpacking integrate through `REG_SET_FIELD` and `REG_GET_FIELD`.

RAS integration is visible for the MMEA EDC and error-status blocks. The driver enumerates MMEA0-MMEA5 EDC counters, including MMEA2 counters whose related page-memory DED fields are represented in this header family, and it resets counters by writing zero to EDC counter registers. EA status registers are queried and cleared as part of MMHUB RAS operations.

The arbitration and address-decode definitions in this chunk are lower-level hardware contract surfaces. They are expected to be consumed by initialization tables, firmware handoff flows, debug tooling, or future driver code that needs to inspect or program MMHUB EA decode behavior for DRAM, GMI, and IO traffic. Nearby generation headers (`mmhub_1_8_0_*`, `mmhub_9_*`) carry similar names with generation-specific differences, so include ordering and ASIC selection matter.

## Risks And Edge Cases

- The line range is not register-complete at either end: it begins after the start of `MMEA1_DSM_CNTL2` and ends before all `MMEA2_IO_WR_PRI_URGENCY_MASKING` fields and masks. Whole-file conclusions must merge adjacent chunks.
- A wrong shift or mask can silently program the wrong MMHUB bit. In this chunk the highest-impact cases are address-normalization/decode fields, client group mappings, priority/urgency masks, and error clear/injection bits.
- Similar MMEA names recur across MMHUB versions, but layouts are not guaranteed identical. For example, the same high-level error-status names differ across older `mmhub_1_0`/`mmhub_9_1` and newer MMHUB headers. Consumers must include the active ASIC generation's header.
- The mask header does not encode access type. Some bits may be read-only status, write-one-to-clear, pulse commands, sticky counters, or reserved fields. Generic read-modify-write code can accidentally clear sticky status, enable injection, or preserve invalid reserved bits.
- Address decode fields pack topology assumptions into small bitfields: chip-select enables, base/mask values, row/column/bank/RM selections, interleave counts, hole controls, and harvest overrides. Invalid combinations can lead to incorrect memory routing, lost memory ranges, or GPU hangs.
- Per-CID priority and urgency masks cover many clients. Misprogramming can starve a client, mask urgent traffic, over-prioritize IO, or perturb DRAM/GMI arbitration in ways that are difficult to diagnose from software logs alone.
- RAS decoding depends on fields matching hardware counter positions. If masks drift, CE/UE accounting may undercount, overcount, or attribute errors to the wrong MMEA subblock.

## Test And Validation Signals

There are no direct unit tests for these generated macros. Useful validation signals are integration-level:

- Build coverage of `amdgpu/mmhub_v1_7.c` with `mmhub_1_7_offset.h` and `mmhub_1_7_sh_mask.h` included, confirming all referenced `reg*` and field macros resolve.
- Static consistency checks for generated fields: single-bit masks should match `1u << shift`, packed multi-bit masks should be contiguous after shifting, full register/address fields should use expected low-bit enables and upper-bit masks, and repeated CID/group fields should follow the visible packing pattern.
- MMHUB RAS tests on supported hardware should exercise EDC counter reads, error-status reads, and reset paths. Expected signals include nonzero CE/UE counts decoded through `mmhub_v1_7_get_ras_error_count()`, EA warnings when status bits are set, and successful clearing through `CLEAR_ERROR_STATUS`.
- GART and VM initialization smoke tests should complete without MMHUB faults, invalid MMIO accesses, or protection-fault regressions, because the same header is included by the MMHUB 1.7 initialization path.
- Hardware bring-up or debug validation should inspect DRAM/GMI/IO arbitration fields, client-to-group maps, urgency masks, and address decode registers before and after firmware/driver programming to ensure only intended bits change.
- Stress tests that mix SDMA, graphics, display, peer/GMI, and CPU-visible IO traffic can expose priority, urgency, lazy accumulation, CAM depth, and page-burst misconfiguration through hangs, timeouts, RAS events, or performance anomalies.

## Chunk Notes For Merge Lane

Treat this as the MMEA1 tail plus the main `mmhub_ea_mmeadec2` MMEA2 slice of `mmhub_1_7_sh_mask.h`. The previous chunk is needed for the full `MMEA1_DSM_CNTL2` definition. The next chunk is needed for the remainder of `MMEA2_IO_WR_PRI_URGENCY_MASKING` and any following MMEA2 registers.
