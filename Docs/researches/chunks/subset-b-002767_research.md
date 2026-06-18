# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h lines 21210-23545

## Purpose

This chunk is generated AMD MMHUB 1.7 register field metadata. It contains 2,336 source lines with 2,183 `#define` entries: 1,092 `__SHIFT` definitions and 1,235 `_MASK` definitions. The content is the bitfield half of the MMHUB register ABI; C code combines these field names with companion register offsets from `mmhub_1_7_offset.h` and SOC15 access helpers to pack, read, decode, and reset MMHUB hardware registers.

Although the source tree path is under a local `ceph-client` mirror, this file is AMDGPU memory-hub hardware metadata. It does not implement Ceph or distributed filesystem behavior.

The covered range starts inside the `MMEA3_ADDRDEC2_BASE_ADDR_SECCS0` definition and then covers late `MMEA3` external-address logic plus the beginning of `MMEA4`:

- `MMEA3_ADDRDEC2_*`: base-address, mask, address-configuration, address-select, column-select, and rank/memory-select fields for chip-select pairs `CS01`, `CS23`, secure chip-select pairs `SECCS01`, `SECCS23`, and individual `SECCS1..3`.
- `MMEA3_ADDRNORM*`: global address-normalization controls, mega-control bits, and masking controls for DRAM and GMI normalization.
- `MMEA3_IO_*`: IO read/write client-to-group maps, combine-flush controls, group burst controls, priority age/queue/fixed/urgency programming, urgency masking for client IDs 0-31, and priority quantum thresholds.
- `MMEA3_SDP_*`: system-data-port arbitration between DRAM, GMI, and IO, final arbitration controls, DRAM/GMI/IO priority fields, credits, tag/VCC/VCD reserve pools, and request-control behavior.
- `MMEA3_MISC`, `MMEA3_MISC2`, `MMEA3_MISC_AON`: broad control/status fields for memory access, clock gating, idle/response monitoring, error behavior, MAM/MCIC/SENDRSP enablement, interrupt handling, snoop, and TLB-related behavior.
- `MMEA3_LATENCY_SAMPLING`, `MMEA3_PERFCOUNTER*`: latency sampling and two performance counters with low/high result registers, event selection, source selection, instance selection, clear/start controls, edge/overflow behavior, and result control.
- `MMEA3_EDC_CNT*`, `MMEA3_DSM_CNTL*`, `MMEA3_CGTT_CLK_CTRL`, `MMEA3_EDC_MODE`, `MMEA3_ERR_STATUS`, `MMEA3_ADDRDEC_SELECT`: RAS/EDC counters, diagnostic scan controls, clock-gating controls, error-mode fields, EA error status/clear bits, and address-decoder selection.
- `MMEA4_DRAM_*` and `MMEA4_GMI_*`: read/write client grouping, group-to-virtual-channel mapping, lazy controls, CAM controls, page-burst controls, priority aging/queuing/fixed/urgency, urgency masking, and quantum thresholds for DRAM and GMI request paths.
- `MMEA4_ADDRNORM_*`: first normal and mega address range base/limit/offset fields, including range-valid, legacy MMIO hole, interleave topology, destination fabric ID, base/limit, and high-address offset controls.

The chunk boundary is artificial. The first line omits the preceding `MMEA3_ADDRDEC2_BASE_ADDR_SECCS0__CS_EN__SHIFT` definition, and the last covered register is `MMEA4_ADDRNORM_MEGALIMIT_ADDR0`; following `MMEA4_ADDRNORM_MEGABASE_ADDR1` and later fields are outside this work item.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, variables, callbacks, locks, allocations, or direct MMIO operations in this chunk. Its interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit position used by `REG_SET_FIELD`, `REG_GET_FIELD`, and SOC15 field table macros.
- `<REGISTER>__<FIELD>_MASK` gives the field mask for extracting or preserving bits during MMIO read-modify-write operations.
- `SOC15_REG_FIELD(<REGISTER>, <FIELD>)` consumers derive shift/mask pairs from these names for RAS tables and register helpers.

High-signal field groups include:

- Address decoding: `CS_EN`, `BASE_ADDR`, `ADDR_MASK`, `NUM_BANK_GROUPS`, `NUM_RM`, `NUM_ROW_LO`, `NUM_ROW_HI`, `NUM_COL`, `NUM_BANKS`, `HI_COL_EN`, bank selectors `BANK0..BANK5`, row selectors, column selectors `COL0..COL15`, rank-map selectors `RM0..RM2`, channel-bit selectors, and even/odd row-MSB inversion fields.
- Address normalization: `ADDR_RNG_VAL`, `LGCY_MMIO_HOLE_EN`, `INTLV_NUM_CHAN`, `INTLV_NUM_DIES`, `INTLV_NUM_SOCKETS`, `INTLV_ADDR_SEL`, `BASE_ADDR`, `LIMIT_ADDR`, `DST_FABRIC_ID`, `HI_ADDR_OFFSET_EN`, and `HI_ADDR_OFFSET`.
- Client grouping and virtual-channel routing: `CLIENT0_GROUP..CLIENT31_GROUP`, `GROUP0_VC..GROUP3_VC`, and read/write variants for IO, DRAM, and GMI paths.
- Request throttling and arbitration: `RD_LAZY_THRESHOLD`, `WR_LAZY_THRESHOLD`, `RD_LAZY_TIMER`, `WR_LAZY_TIMER`, CAM pop/disable/debug fields, page-burst fields, `READ_PRI_AGE`, `WRITE_PRI_AGE`, `AFA` age-control fields, queuing-enable fields, fixed-priority fields, urgent-priority fields, `CID0_MASK..CID31_MASK`, and priority quantum group thresholds.
- SDP and credits: DRAM/GMI burst limits, early switch behavior, end-of-burst behavior, chain-breaking, readonly virtual-channel flags, error/halt request controls, DRAM/GMI/IO priorities, SDP credit limits, tag reserve, VCC/VCD reserve, `ROrW`, shared-credit behavior, and exact-reserve mode.
- RAS and diagnostics: EDC counter fields for DRAM read/write command/data/page memories, IO read/write command/data memories, GMI read/write command/data/page memories, return tag memories, MAM data memories, diagnostic scan `ENABLE/RESET/TC_CYCLE/SRAM_*` fields, `CGTT_CLK_CTRL`, EDC mode, and `MMEA3_ERR_STATUS` status/clear bits.
- Performance and latency: latency sampling enable/done/reset/data-select fields, `MMEA3_PERFCOUNTER_LO/HI`, performance counter event fields, source selection, instance selection, counter clear, counter enable, edge detection, range mode, overflow mode, and result-control fields.

## Control Flow

This chunk has no runtime control flow. Its only direct effect is C preprocessing.

Typical consumer flow is:

1. MMHUB 1.7 code includes `mmhub/mmhub_1_7_offset.h` and `mmhub/mmhub_1_7_sh_mask.h`.
2. Driver code reads a register with `RREG32_SOC15`, `RREG32_SOC15_OFFSET`, or `RREG32(SOC15_REG_ENTRY_OFFSET(...))`.
3. It extracts fields through `REG_GET_FIELD` or through table-generated masks and shifts such as `SOC15_REG_FIELD(MMEA3_EDC_CNT, DRAMRD_CMDMEM_SEC_COUNT)`.
4. For writable controls, it updates fields with `REG_SET_FIELD` and writes the value back through `WREG32_SOC15` or `WREG32`.

Concrete local flows include:

- `amdgpu/mmhub_v1_7.c` includes this header and the companion offset header for MMHUB 1.7 initialization, GART setup, TLB/cache setup, VM context programming, invalidation-range setup, clock gating, and RAS handling.
- `mmhub_v1_7_query_ras_error_count()` iterates `mmhub_v1_7_edc_cnt_regs`, reads `MMEA0..5_EDC_CNT*`, and decodes SEC/DED subfields through `mmhub_v1_7_ras_fields`. The in-scope `MMEA3_EDC_CNT*` and `MMEA4_EDC_CNT*` fields are used in those tables.
- `mmhub_v1_7_reset_ras_error_count()` clears the EDC counter registers by writing zero to each listed counter register, including `MMEA3` and `MMEA4` counters represented by this chunk.
- `mmhub_v1_7_query_ras_error_status()` and `mmhub_v1_7_reset_ras_error_status()` read `MMEA0..5_ERR_STATUS`, check SDP read/write response and data-parity status fields, and set `CLEAR_ERROR_STATUS`. The in-scope `MMEA3_ERR_STATUS` field definitions provide the layout for the `MMEA3` instance; the code also relies on the repeated layout matching the `MMEA0_ERR_STATUS` field names it uses for decoding.

The header does not encode register access order, reset timing, write-one-to-clear semantics, firmware ownership, clock/power prerequisites, or whether a given field is safe to write while traffic is active. Those rules live in the MMHUB driver code, platform firmware contracts, and hardware specifications.

## State And Persistence Behavior

No software state is stored in this header. The macros describe persistent or live hardware state inside the MMHUB external-address, address-normalization, arbitration, RAS, and diagnostic blocks.

The hardware state represented here includes:

- Address-decoder state: chip-select enables, base addresses, masks, bank/row/column/rank selections, channel-bit selections, secure chip-select address maps, and decoder selection. These settings affect how MMHUB EA ranges translate addresses toward DRAM/GMI targets.
- Address-normalization state: range-valid bits, interleave geometry, destination fabric IDs, legacy MMIO hole behavior, base/limit ranges, and high-address offsets. These are topology-sensitive and normally persist until reset or explicit reprogramming.
- Request-routing and QoS state: per-client group assignments, virtual-channel mapping, lazy thresholds/timers, page-burst behavior, priority age/queue/fixed/urgency policy, client-ID urgency masks, and quantum thresholds. These values govern traffic ordering and fairness for IO, DRAM, and GMI request paths.
- SDP state: arbitration limits, switching policy, final arbitration, readonly channel flags, error/halt signaling, credits, tag/VCC/VCD reserves, and request-control behavior.
- Counter and status state: latency sampling, performance counters, EDC SEC/DED counters, error status latches, and diagnostic scan control/status fields.
- Clock and diagnostic state: `CGTT_CLK_CTRL`, DSM controls, EDC mode, idle-monitoring fields, MAM/MCIC/SENDRSP enable bits, snoop controls, and assorted `MISC` control/status bits.

Persistence is hardware-defined. Configuration registers can persist across normal driver operation until reset, suspend/resume, power-gating, or reinitialization. Counter/status registers can be live, sticky, clear-on-write, clear-on-read, or reset by explicit writes depending on the register. The generated mask header does not distinguish those behaviors.

## Dependencies

This chunk depends on the generated MMHUB 1.7 register family and AMDGPU SOC15 register access layer:

- `mmhub_1_7_offset.h` supplies the matching `reg*` offsets for the registers whose fields are defined here.
- `amdgpu/mmhub_v1_7.c` includes this header directly and uses many MMHUB 1.7 fields through `REG_SET_FIELD`, `REG_GET_FIELD`, and RAS table helpers.
- SOC15 helpers such as `SOC15_REG_ENTRY`, `SOC15_REG_ENTRY_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_FIELD` translate generated register and field names into actual MMIO operations.
- RAS infrastructure in `amdgpu_ras.h` and MMHUB RAS code depends on EDC counter masks and shifts matching hardware so SEC/DED totals are attributed to the correct subblocks.
- Sibling generated headers such as `mmhub_1_8_0_sh_mask.h` and later MMHUB versions have similar names but are not guaranteed layout-compatible. The matching offset and mask headers must be used for the same hardware generation.

## Integration Points

Primary integration points are:

- MMHUB 1.7 initialization: `amdgpu/mmhub_v1_7.c` uses this header for VM aperture setup, TLB/L2 control, VMID context programming, invalidation-range initialization, and clock-gating state. Those flows are outside this exact `MMEA3/MMEA4` slice but share the same generated header contract.
- MMHUB RAS accounting: `mmhub_v1_7_ras_fields` maps `MMEA3_EDC_CNT`, `MMEA3_EDC_CNT2`, `MMEA3_EDC_CNT3`, `MMEA4_EDC_CNT`, `MMEA4_EDC_CNT2`, and `MMEA4_EDC_CNT3` fields to named MMHUB memory subblocks such as DRAM command/page memories, IO command/data memories, GMI command/data/page memories, MAM data memories, and return tag memories.
- MMHUB RAS reset: `mmhub_v1_7_edc_cnt_regs` includes the same `MMEA3` and `MMEA4` EDC registers so the driver can reset accumulated error counters by writing zero.
- MMHUB EA error reporting: `mmhub_v1_7_ea_err_status_regs` includes `regMMEA3_ERR_STATUS` and `regMMEA4_ERR_STATUS`. The chunk provides the `MMEA3_ERR_STATUS` field layout for SDP read/write response status, read-response data parity, and clear-error behavior; `MMEA4_ERR_STATUS` is in a neighboring section.
- Hardware bring-up and tuning: address decode, normalization, DRAM/GMI/IO arbitration, SDP, priority, and diagnostic fields are generated definitions available to platform initialization, firmware golden settings, debug tooling, or future driver code even when the current C file does not touch each field explicitly.

## Risks And Edge Cases

- Mask/shift correctness is the main risk. These macros compile as constants; a wrong bit position silently programs or decodes the wrong hardware field.
- The range starts and ends mid-family. Final reconciliation should merge neighboring chunks before making file-level claims about complete `MMEA3_ADDRDEC2_BASE_ADDR_SECCS0` or `MMEA4_ADDRNORM_MEGALIMIT_ADDR0` coverage.
- Similar-looking MMHUB generations are not interchangeable. `mmhub_1_7_sh_mask.h`, `mmhub_1_8_0_sh_mask.h`, and later MMHUB headers use overlapping `MMEA*` names but may differ in register presence, field width, field meaning, or repeated-instance count.
- RAS fields are easy to misattribute because `MMEA3` and `MMEA4` repeat many counter names. A swapped mask can report SEC/DED counts against the wrong MMHUB subblock or miss a nonzero counter.
- `MMEA*_ERR_STATUS` fields may be sticky or clear-sensitive. Incorrect clear masks can leave stale RAS status, hide a real error, or repeatedly report the same event.
- Address-decoder and address-normalization fields are topology-critical. Bad base, limit, mask, interleave, fabric ID, high-offset, channel, bank, row, column, rank, or secure chip-select fields can route traffic to the wrong memory region or fabric target.
- Arbitration, priority, urgency masking, and SDP credit fields influence forward progress and fairness. Incorrect values can starve clients, produce latency spikes, trigger timeouts, or reduce GMI/DRAM/IO throughput.
- Diagnostic scan, clock-control, EDC mode, and reset-like fields are not ordinary configuration bits. They can affect live traffic, counter collection, RAS behavior, or clocking if written outside the expected sequencing window.
- Some consumers rely on repeated register-family layout. `mmhub_v1_7_query_ras_error_status()` decodes every `MMEA*_ERR_STATUS` value with `MMEA0_ERR_STATUS` field names, so the repeated instances must remain layout-equivalent.

## Test Signals

Useful validation signals include:

- Build AMDGPU with MMHUB 1.7 support enabled so all `mmhub_v1_7.c` uses of `mmhub_1_7_offset.h` and `mmhub_1_7_sh_mask.h` resolve.
- Static generated-header checks that every field in this chunk has both shift and mask definitions where expected, and that names line up with matching registers in `mmhub_1_7_offset.h`.
- RAS query tests that inject or observe MMHUB EDC events for `MMEA3` and `MMEA4`, then verify SEC/DED counts are decoded under the expected subblock names.
- RAS reset tests that write zero through `mmhub_v1_7_reset_ras_error_count()` and confirm `MMEA3_EDC_CNT*` and `MMEA4_EDC_CNT*` counters clear without disturbing unrelated state.
- EA error-status tests that exercise SDP read/write response and data-parity error paths, then verify status reporting and `CLEAR_ERROR_STATUS` behavior.
- Boot, suspend/resume, and GPU reset tests on MMHUB 1.7 hardware, watching for VM faults, MMHUB RAS warnings, GART setup failures, invalidation timeouts, or memory traffic hangs.
- Performance and stress tests that drive IO, DRAM, and GMI traffic while checking for unexpected starvation, latency regressions, RAS counter increments, or SDP arbitration errors.
- Hardware debug validation for address-decoder and address-normalization programming on multi-channel/interleaved systems, especially secure chip-select, fabric ID, high-offset, and legacy MMIO-hole behavior.

## Summary

Lines 21210-23545 of `mmhub_1_7_sh_mask.h` define generated bit shifts and masks for the tail of `MMEA3` address decoding plus `MMEA3` address normalization, IO/SDP arbitration, diagnostics, RAS, performance, and error-status fields, followed by the start of `MMEA4` DRAM/GMI arbitration and address-normalization fields. The chunk is hardware contract data, not executable logic. Correctness depends on exact field values, matching `mmhub_1_7_offset.h`, careful RAS/status handling, and hardware validation across MMHUB traffic, address routing, arbitration, diagnostics, reset, and error-reporting paths.
