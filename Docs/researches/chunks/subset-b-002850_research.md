# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 21242-23604

## Scope

This chunk is a generated AMD MMHUB 9.4.1 shift/mask header segment. It is almost entirely the `MMEA4` address-decode, arbitration, address-normalization, address-decode, IO, SDP, performance, RAS, error-injection, clock, and miscellaneous field layout, followed by the start of the `mmhub_pctldec0` power-control block with complete `PCTL0_CTRL` field masks. The final covered line is only the `//PCTL0_MMHUB_DEEPSLEEP_IB` comment; the `PCTL0_MMHUB_DEEPSLEEP_IB__*` definitions begin in the following line/chunk.

The file contains preprocessor constants only. Each concrete hardware register field is represented by a `REGISTER__FIELD__SHIFT` macro and a matching `REGISTER__FIELD_MASK` macro. There are no C functions, structs, global variables, runtime branches, loops, locks, memory allocation, or direct MMIO reads/writes in this chunk. Runtime behavior comes from AMDGPU code that includes this header together with `mmhub_9_4_1_offset.h` and expands the field macros through helpers such as `SOC15_REG_FIELD`, `REG_SET_FIELD`, and `REG_GET_FIELD`.

Major covered register families are:

- Tail of `MMEA4_GMI_RD_PRI_URGENCY` and full `MMEA4_GMI_WR_PRI_URGENCY`, plus GMI read/write urgency masks and quantum priority thresholds.
- `MMEA4_ADDRNORM_*` normal address ranges 0 through 5, DRAM/GMI hole controls, and non-power-of-two channel configuration.
- `MMEA4_ADDRDEC_*` DRAM/GMI bank, hash, harvest, chip-select base/mask/config/select/column/rank-multiplier fields for address-decode instances 0 through 2.
- `MMEA4_IO_*` client-to-group maps, combine-flush controls, burst controls, priority age/queue/fixed/urgency/masking/quantum registers.
- `MMEA4_SDP_*` arbitration, priority, credit, reserve, and request-control fields.
- `MMEA4_MISC`, `MMEA4_MISC2`, latency sampling, MMHUB performance counters, EDC counters, DSM error-injection controls, CGTT clock controls, EDC mode, error status, and address-decode select.
- `PCTL0_CTRL` in the `mmhub_pctldec0` address block.

## Purpose

The purpose of this header segment is to define the bit layout for programming and decoding MMHUB 9.4.1 hardware registers. The companion offset header gives the register addresses, for example `mmMMEA4_GMI_WR_PRI_URGENCY`, `mmMMEA4_EDC_CNT`, `mmMMEA4_ERR_STATUS`, and `mmPCTL0_CTRL`; this shift/mask header gives the field positions and bit masks inside those registers.

This chunk is especially relevant to the fourth MMHUB memory-engine/address-decode range, `MMEA4`. The fields describe how MMHUB routes address ranges to DRAM or GMI, hashes addresses into bank/channel/chip-select selections, groups clients for arbitration, assigns priority and urgency policy to GMI and IO traffic, exposes SDP credits and arbitration controls, counts reliability events, injects diagnostic memory errors, reports SDP response errors, and controls local MMHUB clock/power policy.

Because the file is generated register metadata, exactness is the contract. A typo in a mask or shift normally compiles cleanly but can make the driver set the wrong MMIO bit, misdecode hardware status, or report incorrect RAS data.

## Important Macro Families

### GMI Priority and Urgency

The chunk starts mid-register in the tail of `MMEA4_GMI_RD_PRI_URGENCY` with group urgency-mode masks, then fully defines `MMEA4_GMI_WR_PRI_URGENCY`. The write urgency register has four group urgency coefficients and four group urgency-mode bits. `MMEA4_GMI_RD_PRI_URGENCY_MASKING` and `MMEA4_GMI_WR_PRI_URGENCY_MASKING` expose one mask bit for each CID 0 through 31, allowing per-client urgency participation to be suppressed or enabled by register programming.

`MMEA4_GMI_RD_PRI_QUANT_PRI1..3` and `MMEA4_GMI_WR_PRI_QUANT_PRI1..3` define four 8-bit group thresholds per register. Together with the urgency and fixed/age/queuing fields defined in neighboring regions, these constants describe GMI request-priority policy for the MMEA4 path.

### Address Normalization

`MMEA4_ADDRNORM_BASE_ADDR0..5`, `LIMIT_ADDR0..5`, and `OFFSET_ADDR1/3/5` define address-normalization windows. Base registers include fields for range validity, legacy MMIO-hole behavior, DRAM/GMI selection, reverse-invert control, symmetric-mode topology, xGMI interleave mode, destination fabric ID, and high base address bits. Limit registers carry the high limit address bits, and offset registers carry high address-offset bits for translated ranges.

`MMEA4_ADDRNORMDRAM_HOLE_CNTL` and `MMEA4_ADDRNORMGMI_HOLE_CNTL` define offset controls for DRAM and GMI holes. `MMEA4_ADDRNORMDRAM_NP2_CHANNEL_CFG` and `MMEA4_ADDRNORMGMI_NP2_CHANNEL_CFG` define non-power-of-two channel masking for 3/5/6/7/10/12/14-channel configurations. These fields are topology-sensitive and must match the memory fabric layout exposed by firmware and the ASIC register database.

### Address Decode, Hashing, Harvesting, and Chip Selects

`MMEA4_ADDRDEC_BANK_CFG` defines bank, bank-group, pseudo-channel, and channel-count settings. `MMEA4_ADDRDEC_MISC_CFG` adds rank count, bank xor, rank-bit selection, channel xor, dimm-pair, low-bit, bank-hash, hashing-enable, and linear/xor remap controls.

The DRAM and GMI hash families are parallel:

- `MMEA4_ADDRDECDRAM_ADDR_HASH_BANK0..5`, `PC`, `PC2`, `CS0`, and `CS1`.
- `MMEA4_ADDRDECGMI_ADDR_HASH_BANK0..5`, `PC`, `PC2`, `CS0`, and `CS1`.

The bank hash registers select address-bit inputs and optionally enable hashing. PC and chip-select hash registers provide compact hash-selection and enable bits. `MMEA4_ADDRDECDRAM_HARVEST_ENABLE` and `MMEA4_ADDRDECGMI_HARVEST_ENABLE` define per-channel harvest-disable masks for CH0 through CH5, plus aggregate channel harvest disable and enable bits. These are integration points for SKU harvesting and memory-channel availability.

`MMEA4_ADDRDEC0`, `MMEA4_ADDRDEC1`, and `MMEA4_ADDRDEC2` then repeat full chip-select layouts. Each decode instance has base-address enable/address fields for CS0 through CS3 and secondary CS0 through CS3; masks for CS01, CS23, secondary CS01, and secondary CS23; address configuration for row/rank/bank/bank-group/channel/pseudo-channel bit counts; address select and select2 fields; low/high column selects; and rank-multiplier selects for normal and secondary chip selects. These macros are the detailed bit map for constructing the physical memory address from normalized inputs.

`MMEA4_ADDRDEC_SELECT` appears later and selects DRAM and GMI address-decode channel start/end indices. It is a compact selector for which decode-channel range is active for each memory fabric path.

### IO Arbitration and Priorities

`MMEA4_ADDRNORMDRAM_GLOBAL_CNTL` and `MMEA4_ADDRNORMGMI_GLOBAL_CNTL` each expose an address-hashing disable bit. The IO priority block follows:

- `MMEA4_IO_RD_CLI2GRP_MAP0/1` and `MMEA4_IO_WR_CLI2GRP_MAP0/1` map CIDs 0 through 15 to 2-bit group IDs for read and write paths.
- `MMEA4_IO_RD_COMBINE_FLUSH` and `MMEA4_IO_WR_COMBINE_FLUSH` provide per-group flush controls and data flush enablement.
- `MMEA4_IO_GROUP_BURST` defines 4-bit burst limits for groups 0 and 1.
- `MMEA4_IO_RD_PRI_AGE` and `MMEA4_IO_WR_PRI_AGE` define per-group age controls, plus read/write-disable bits.
- `MMEA4_IO_RD_PRI_QUEUING` and `MMEA4_IO_WR_PRI_QUEUING` define per-group queuing thresholds.
- `MMEA4_IO_RD_PRI_FIXED` and `MMEA4_IO_WR_PRI_FIXED` define fixed-priority levels.
- `MMEA4_IO_RD_PRI_URGENCY` and `MMEA4_IO_WR_PRI_URGENCY` mirror the GMI urgency coefficient/mode model.
- `MMEA4_IO_RD_PRI_URGENCY_MASKING` and `MMEA4_IO_WR_PRI_URGENCY_MASKING` expose per-CID urgency masks for all 32 CIDs.
- `MMEA4_IO_RD_PRI_QUANT_PRI1..3` and `MMEA4_IO_WR_PRI_QUANT_PRI1..3` define group quantum priority thresholds.

These definitions describe policy knobs for scheduling IO reads and writes through MMEA4. The header itself does not choose the policy; it only supplies the field map used by platform-specific programming.

### SDP Arbitration, Credits, and Request Controls

The SDP block defines downstream arbitration among DRAM, GMI, IO, and final paths:

- `MMEA4_SDP_ARB_DRAM`, `MMEA4_SDP_ARB_GMI`, and `MMEA4_SDP_ARB_FINAL` include LRU disablement, disable bits for request classes, burst controls, priority ordering, and urgent arbitration masks.
- `MMEA4_SDP_DRAM_PRIORITY`, `MMEA4_SDP_GMI_PRIORITY`, and `MMEA4_SDP_IO_PRIORITY` provide PRI0 through PRI3 fields for read/write or path-specific priority order.
- `MMEA4_SDP_CREDITS` exposes read and write response credit fields.
- `MMEA4_SDP_TAG_RESERVE0/1`, `VCC_RESERVE0/1`, and `VCD_RESERVE0/1` reserve tags or virtual-channel credits for multiple MMHUB clients.
- `MMEA4_SDP_REQ_CNTL` exposes start time, stop response/data, combined write-disconnect status, and idle-mask fields.

These fields integrate MMEA4 with the SDP request/response path. Bad masks here would affect fairness, throughput, backpressure, and idle detection rather than normal C data structures.

### Miscellaneous Controls, Latency, and Performance Counters

`MMEA4_MISC` is a dense control/status register with virtual-channel switching, credit-send disablement, requester ID, force-urgent, reorder disablement, AID ID, error-capture ID, no-allocate ID, reorder and read-credit controls, optimized write flush, no-allocate credit status, GMI-link-down disablement, force response-decode, response status selection, XSP/MAM route controls, GART aperture disablement, forced inactivity, performance-counter clock enablement, and HBM backup-request controls.

`MMEA4_LATENCY_SAMPLING` defines a request-ID match, read/write ID, request path selector, sample enable, and minimum latency threshold. `MMEA4_PERFCOUNTER_LO`, `MMEA4_PERFCOUNTER_HI`, `MMEA4_PERFCOUNTER0_CFG`, `MMEA4_PERFCOUNTER1_CFG`, and `MMEA4_PERFCOUNTER_RSLT_CNTL` provide a 64-bit counter view, compare value, performance selector, mode, enable, clear, global enable, clear-all, and stop-on-saturate controls.

These fields are observability and tuning hooks. Performance-counter and latency-sampling controls are stateful hardware controls, not passive constants.

### RAS Counters, DSM Injection, EDC Mode, and Error Status

`MMEA4_EDC_CNT`, `MMEA4_EDC_CNT2`, and `MMEA4_EDC_CNT3` define SEC/SED and DED counters for internal MMEA4 memories. Covered subblocks include DRAM read/write command memories, DRAM write data memory, return tag memories, DRAM page memories, IO read/write command/data memories, GMI read/write command/data/page memories, and MAM data memories. `mmhub_v9_4.c` consumes these fields through `mmhub_v9_4_ras_fields`, using `SOC15_REG_FIELD(MMEA4_EDC_CNT*, ...)` entries to decode counts for MMHUB RAS reporting.

`MMEA4_DSM_CNTL`, `MMEA4_DSM_CNTLA`, `MMEA4_DSM_CNTL2`, and `MMEA4_DSM_CNTL2A` define diagnostic error-injection enable and delay-selection bits for the same broad memory families. They include an `INJECT_DELAY` field where present. These should be treated as lab/debug controls; accidentally setting them in a production path can create synthetic RAS events or hardware faults.

`MMEA4_EDC_MODE` defines output counting, FUE gating, DED mode, FED propagation, and EDC bypass controls. `MMEA4_ERR_STATUS` exposes SDP read/write response status, read-response data status, data parity error, clear-error-status, busy-on-error, and FUE flag fields. `mmhub_v9_4.c` includes `mmMMEA4_ERR_STATUS` in `mmhub_v9_4_err_status_regs` for MMHUB error-status queries.

`MMEA4_CGTT_CLK_CTRL` defines on delay, off hysteresis, spare fields, soft stall override bits, light-sleep override, and soft override bits for write/read/return/register paths. `MMEA4_MISC2` includes DRAM/GMI CS-group swap controls, burst-limit data fields, IO read/write priority enablement, and return-swap mode.

### PCTL0 Control Boundary

The chunk enters a new address block at `// addressBlock: mmhub_pctldec0` and fully defines `PCTL0_CTRL`. Its fields include power-gating enablement, allowed deep-sleep mode, RSMU and DAGB idle thresholds, state-controller ignore-protection-fault behavior, EA0 through EA4 SDP partial-ack and full-ack override bits, and a `PGFSM_CMD_STATUS` field.

The next comment, `//PCTL0_MMHUB_DEEPSLEEP_IB`, is included as the final line of this chunk, but none of its DS bit definitions are in scope here. Neighboring code such as JPEG ring start/end paths references the `PCTL0_MMHUB_DEEPSLEEP_IB` register by offset/comment, so the merge lane should connect this boundary to the following chunk before making file-level statements about PCTL deep-sleep IB fields.

## Control Flow and State Behavior

There is no executable control flow in this chunk. All control flow is in consumers such as `drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`, which includes `mmhub_9_4_1_offset.h` and `mmhub_9_4_1_sh_mask.h`.

The state represented by these macros is hardware MMIO state:

- Configuration state: address ranges, address-normalization policy, channel/chip-select topology, hashing, harvesting, arbitration policy, priority policy, SDP reserves, PCTL power behavior, CGTT clock controls, and EDC mode.
- Status state: no-allocate credit status, SDP request/idle status, error status, FUE flag, and PGFSM command status.
- Counter state: EDC SEC/DED counters, performance counters, and latency sampling thresholds/results.
- Request/debug state: combine flush controls, performance clear/enable bits, DSM error-injection controls, and clear-error-status bits.

Persistence is not implemented in this header. Register values live in hardware and are initialized, queried, reset, or restored by driver code and firmware sequencing. Some counters are read-to-reset in the RAS path: `mmhub_v9_4_reset_ras_error_count()` reads EDC counter registers, including `mmMMEA4_EDC_CNT`, `mmMMEA4_EDC_CNT2`, and `mmMMEA4_EDC_CNT3`, to reset counts when MMHUB RAS is supported.

## Dependencies and Integration Points

Direct dependencies are the AMD generated-register convention and the matching headers:

- `mmhub_9_4_1_offset.h` supplies `mm...` offsets and base indices for the same register names. For this chunk, examples include `mmMMEA4_GMI_WR_PRI_URGENCY` at offset `0x07ab`, `mmMMEA4_GMI_WR_PRI_URGENCY_MASKING` at `0x07ad`, `mmPCTL0_CTRL` at `0x08c0`, and `mmPCTL0_MMHUB_DEEPSLEEP_IB` at `0x08c1`.
- `mmhub_9_4_1_default.h` supplies generated default values for the same register generation where available.
- `soc15.h` and related AMDGPU helpers provide `SOC15_REG_ENTRY`, `SOC15_REG_FIELD`, `RREG32`, `WREG32`, `REG_SET_FIELD`, and `REG_GET_FIELD` behavior that expands these masks and shifts.

Observed local integration points include:

- `drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`, which includes this header and the matching offset header.
- `mmhub_v9_4_ras_fields`, which maps `MMEA4_EDC_CNT`, `MMEA4_EDC_CNT2`, and `MMEA4_EDC_CNT3` fields to named MMHUB RAS subblocks such as `MMEA4_DRAMRD_CMDMEM`, `MMEA4_GMIRD_CMDMEM`, `MMEA4_GMIWR_PAGEMEM`, and `MMEA4_MAM_D*MEM`.
- `mmhub_v9_4_edc_cnt_regs`, which lists the MMEA4 EDC counter registers that are read by `mmhub_v9_4_query_ras_error_count()` and `mmhub_v9_4_reset_ras_error_count()`.
- `mmhub_v9_4_err_status_regs`, which lists `mmMMEA4_ERR_STATUS` for MMHUB RAS error-status polling.
- `mmhub_v9_4_set_clockgating()` and adjacent clock/power paths, which are part of the same MMHUB generation and rely on generated field headers for clock-gating and power-control programming, even when specific fields from this chunk are not all referenced directly in the visible code.
- `gmc_v9_0.c`, which selects `mmhub_v9_4_funcs` and `mmhub_v9_4_ras` for the relevant GMC/MMHUB IP path, making this generated header part of GPU memory-management bring-up for that ASIC family.

## Risks

- Generated mask/shift drift is silent at compile time. A wrong mask can still build but program a different hardware bit than intended.
- Address-normalization and address-decode fields are data-integrity sensitive. Incorrect base/limit/offset, hash, channel, chip-select, column, or rank-multiplier fields can route memory traffic incorrectly or make RAS reports point at the wrong channel/rank.
- Harvest-enable and non-power-of-two channel fields are SKU/topology sensitive. A field mismatch may only appear on partially harvested dies or uncommon channel-count configurations.
- IO and GMI priority fields affect fairness and forward progress. Incorrect client-to-group maps, urgency masks, quantum thresholds, or burst controls can cause starvation, latency spikes, or reduced fabric throughput.
- SDP credit/reserve and arbitration masks control backpressure. Bad values can produce hangs or poor utilization without obvious software-side errors.
- EDC and error-status fields feed RAS accounting. Wrong SEC/DED masks can invert corrected versus uncorrected counts, double-count, miss a failing subblock, or emit misleading `MMHUB SubBlock ...` logs.
- DSM error-injection controls are hazardous outside diagnostics. Misprogramming injection enable or delay bits can synthesize faults and pollute RAS telemetry.
- Clear/status fields such as `MMEA4_ERR_STATUS__CLEAR_ERROR_STATUS` should not be treated as ordinary persistent configuration; writing them can acknowledge or drop hardware error state.
- `PCTL0_CTRL` power-gating/deep-sleep policy is timing and platform sensitive. Bad idle thresholds, ack overrides, or protection-fault ignore behavior may only fail under suspend/resume, reset, low-power, or high-load concurrency.
- The chunk begins and ends at artificial boundaries. The first covered lines are the tail of `MMEA4_GMI_RD_PRI_URGENCY`, and the final `PCTL0_MMHUB_DEEPSLEEP_IB` comment has no field definitions until the next chunk.

## Test and Validation Signals

Useful validation is mostly build and hardware integration testing:

- Build AMDGPU with MMHUB 9.4 support to catch missing, renamed, or malformed field macros used by `mmhub_v9_4.c`.
- Boot on hardware using `mmhub_v9_4_funcs` and verify GART/VM bring-up, memory allocation, DMA, and page-table update workloads. Address-decode mistakes can surface as VM faults, memory corruption, or GPU hangs.
- Query MMHUB RAS counters and confirm `MMEA4_EDC_CNT*` decoding reports expected subblock names and separates SEC/SED from DED counts correctly.
- Reset MMHUB RAS counts and verify read-to-reset behavior clears the relevant `MMEA4_EDC_CNT*` counters without losing unrelated state.
- Trigger or inject controlled MMHUB reliability events in a lab environment and check that `MMEA4_ERR_STATUS` and EDC counter fields decode consistently with hardware documentation.
- Stress GMI and IO traffic with mixed read/write clients to expose priority, urgency, quantum, and SDP arbitration regressions as latency, starvation, or throughput anomalies.
- Exercise platform power-management paths, including clock gating, light sleep, suspend/resume, and reset, to catch `PCTL0_CTRL` and `MMEA4_CGTT_CLK_CTRL` field problems.
- Compare regenerated `mmhub_9_4_1_sh_mask.h` and `mmhub_9_4_1_offset.h` against the authoritative register database, paying special attention to repeated per-CID/per-group/per-channel macros where copy-generation errors are easy to miss.

## Cross-Chunk Notes

The range starts after the beginning of `MMEA4_GMI_RD_PRI_URGENCY`, so the complete read-urgency register must be reconciled with the previous chunk. The range ends immediately after the `//PCTL0_MMHUB_DEEPSLEEP_IB` marker, before any `PCTL0_MMHUB_DEEPSLEEP_IB__DS*` shift/mask definitions. The final per-file report should merge this chunk with its neighbors before describing complete GMI urgency or PCTL deep-sleep IB coverage.
