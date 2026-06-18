# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h lines 18858-21209

## Scope

This chunk covers generated shift and mask macros from the AMD MMHUB 1.7 register mask header. It begins in the middle of `MMEA2_IO_WR_PRI_URGENCY_MASKING` and ends after the `MMEA3_ADDRDEC2_BASE_ADDR_SECCS0__CS_EN__SHIFT` definition, so both edges require adjacent chunks for complete register-family descriptions.

The covered range includes:

- The tail of MMEA2 IO write urgency masking for client IDs 27-31 and the complete 32-bit `CID*_MASK_MASK` layout.
- MMEA2 IO read/write priority quantum thresholds, SDP arbitration, final arbitration, priority, credit, tag reserve, VCC/VCD reserve, request-control, misc, latency sampling, perf counter, EDC counter, DSM, clock-gating, EDC mode, error-status, misc2, address-decoder select, and always-on misc fields.
- The `mmhub_ea_mmeadec3` address block start for MMEA3, covering DRAM/GMI client-to-group maps, group-to-VC maps, lazy accumulation, CAM controls, page burst, priority age/queuing/fixed/urgency/quantum controls, and GMI urgency masking.
- MMEA3 address normalization ranges, mega ranges, hole controls, non-power-of-two channel configuration, bank and misc decode configuration, harvest forcing, address-decoder 0 and 1 base/mask/config/select/column/rank-map fields, and the start of address-decoder 2 base-address fields.

The file is a generated hardware register bitfield map. It defines C preprocessor constants only: no functions, structs, variables, storage, or executable control flow are implemented in this chunk.

## Purpose

This header section provides the bit-level ABI used by AMDGPU code to compose and decode MMHUB 1.7 MMIO register values. Each field follows the generated AMD convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit mask for extracting or inserting that field.

The sibling `mmhub_1_7_offset.h` file supplies register addresses such as `regMMEA2_SDP_ARB_FINAL`, `regMMEA2_EDC_CNT`, `regMMEA3_ADDRNORM_BASE_ADDR0`, and `regMMEA3_ADDRDEC2_BASE_ADDR_CS0`; this file supplies the field locations for those registers. Driver code consumes these macros through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `SOC15_REG_ENTRY`, `RREG32_SOC15`, and `WREG32_SOC15`.

## Important Macro Families

### MMEA2 IO and SDP Arbitration

The chunk starts with the end of `MMEA2_IO_WR_PRI_URGENCY_MASKING`, mapping each client ID bit to an urgency-mask bit. It then defines read and write quantum threshold registers (`MMEA2_IO_RD_PRI_QUANT_PRI1..3` and `MMEA2_IO_WR_PRI_QUANT_PRI1..3`) with four 8-bit group thresholds per register.

The SDP arbitration group includes:

- `MMEA2_SDP_ARB_DRAM` and `MMEA2_SDP_ARB_GMI`, with read/write burst limits, early switch-to-read/write controls, end-of-burst-on-expire, decoupled read/write bank-state behavior, and GMI chain-breaking permission.
- `MMEA2_SDP_ARB_FINAL`, with DRAM/GMI/IO burst limits, burst multiplier, read-only virtual-channel bits for VC0-VC7, error event and halt request enables, GMI burst stretch, and DRAM/GMI read/write throttle bits.
- `MMEA2_SDP_DRAM_PRIORITY`, `MMEA2_SDP_GMI_PRIORITY`, and `MMEA2_SDP_IO_PRIORITY`, which pack four read priorities and four write priorities into 4-bit group fields.
- `MMEA2_SDP_CREDITS`, tag reserve registers, and VCC/VCD reserve registers, which define tag limits, response credits, per-VC credit reservations, and pool distribution.
- `MMEA2_SDP_REQ_CNTL`, which controls request pass-PW overrides, request-chain overrides for DRAM/GMI, inner-domain mode, and read/write/atomic block levels.

These definitions tune request scheduling and backpressure between MMHUB clients, DRAM, GMI, IO, virtual channels, and response paths.

### MMEA2 Misc, Performance, Clock, and Error Controls

The `MMEA2_MISC` and `MMEA2_MISC2` fields cover relative priority enablement across DRAM/GMI/IO read/write arbiters, early write return per virtual channel, link-manager dynamic and timing thresholds, CSGROUP swap controls, burst-limit data controls, IO read/write priority enablement, RRET swap mode, request blocking, and request-blocked status.

`MMEA2_LATENCY_SAMPLING`, `MMEA2_PERFCOUNTER_LO/HI`, `MMEA2_PERFCOUNTER0_CFG`, `MMEA2_PERFCOUNTER1_CFG`, and `MMEA2_PERFCOUNTER_RSLT_CNTL` expose a small performance-monitoring surface: sampling enable, sample ID, sample index, counter select/filtering, counter mode, bit range, and result control.

`MMEA2_CGTT_CLK_CTRL` defines clock-gating timing and override fields, including on delay, off hysteresis, soft stall overrides, light-sleep override, soft read/write/return/register overrides, and spare fields.

`MMEA2_EDC_MODE`, `MMEA2_ERR_STATUS`, `MMEA2_EDC_CNT`, `MMEA2_EDC_CNT2`, and `MMEA2_EDC_CNT3` describe error-detection and correction behavior and counters. They cover SEC/DED/SED counts for DRAM read/write command/page/data memories, IO command/data memories, GMI command/page/data memories, RRET/WRET tag memories, and MAM D0-D3 memories. `MMEA2_ERR_STATUS` also carries SDP read/write response status, read response data status, data parity, clear-error, busy-on-error, FUE, fatal interrupt, level interrupt, and completion fatal busy bits.

`MMEA2_DSM_CNTL*` and `MMEA2_DSM_CNTL2*` define diagnostic/error-injection controls for many of the same internal memories. The first set provides DSM irritator data and single-write enables; the second set provides error-injection enables, injection-delay selectors, and shared injection delay.

### MMEA2 Address Decoder Selection

`MMEA2_ADDRDEC_SELECT` defines start and end channel fields for DRAM and GMI address decoders. In this chunk it is a compact channel-routing register: 5-bit start/end fields for DRAM and 5-bit start/end fields for GMI.

`MMEA2_MISC_AON` adds always-on link-manager part-ack hysteresis and deassert mode controls.

### MMEA3 DRAM and GMI Request Grouping

The chunk then enters `addressBlock: mmhub_ea_mmeadec3`. The first MMEA3 families map clients, groups, virtual channels, and arbiter coefficients for DRAM and GMI request paths:

- `*_CLI2GRP_MAP0/1` maps 32 client IDs to four groups using 2-bit group fields.
- `*_GRP2VC_MAP` maps four groups to 3-bit virtual-channel fields.
- `*_LAZY` defines group delays plus request accumulation thresholds, timeout, and idle maximum.
- `*_CAM_CNTL` defines CAM depth per group, reorder limits per group, and refill-chain behavior.
- `*_PAGE_BURST` defines low/high page-burst limits for read and write traffic.
- `*_PRI_AGE`, `*_PRI_QUEUING`, `*_PRI_FIXED`, `*_PRI_URGENCY`, `*_PRI_URGENCY_MASKING`, and `*_PRI_QUANT_PRI1..3` define the priority model: aging rates and coefficients, queuing/fixed/urgency coefficients, urgency modes, per-client urgency masking, and four-group quantum thresholds.

The DRAM and GMI groups are structurally similar but independently named. The generated layout makes cross-channel copy-paste mistakes particularly risky because many masks are identical while register prefixes differ.

### MMEA3 Address Normalization and Decode

The address normalization families define how normalized MMHUB addresses map to fabric destinations and memory ranges:

- `MMEA3_ADDRNORM_BASE_ADDR0..3` and `LIMIT_ADDR0..3` define valid range bits, legacy MMIO hole enable, interleave channel/die/socket fields, interleave address selection, base address, destination fabric ID, and limit address.
- `MMEA3_ADDRNORM_OFFSET_ADDR1/3` define high-address offset enable and offset.
- `MMEA3_ADDRNORM_MEGABASE_ADDR0/1` and `MEGALIMIT_ADDR0/1` mirror the base/limit pattern for mega ranges.
- `MMEA3_ADDRNORMDRAM_HOLE_CNTL` and `MMEA3_ADDRNORMGMI_HOLE_CNTL` define hole-valid and hole-offset fields.
- `MMEA3_ADDRNORMDRAM_NP2_CHANNEL_CFG` and `MMEA3_ADDRNORMGMI_NP2_CHANNEL_CFG` define non-power-of-two 64K-space sizing fields.

The address-decoder families then describe DRAM/GMI bank, channel, chip-select, row, column, and rank-map decomposition:

- `MMEA3_ADDRDEC_BANK_CFG` selects bank masks, bank group selectors, and DRAM/GMI bank group interleave.
- `MMEA3_ADDRDEC_MISC_CFG` controls VCM enables and masks for PCH, channel, chip-select, and rank-map dimensions.
- `MMEA3_ADDRDECDRAM_HARVEST_ENABLE` and `MMEA3_ADDRDECGMI_HARVEST_ENABLE` can force bank bits B3-B5 enable/value pairs for harvested topology.
- `MMEA3_ADDRDEC0_*` and `MMEA3_ADDRDEC1_*` define base addresses for primary and secondary chip-selects, address masks, address configuration fields, bank/row selectors, extra bank/channel selection, low/high column selectors, rank-map selectors, channel-bit selection, and row-MSB inversion for even/odd rows.
- The chunk ends at the beginning of `MMEA3_ADDRDEC2_BASE_ADDR_SECCS0`, after completing `MMEA3_ADDRDEC2_BASE_ADDR_CS0..CS3` and defining only the `SECCS0` chip-select enable shift.

These fields are part of physical memory topology programming. They are not software allocation policy; they encode the hardware interpretation of address bits.

## Control Flow and State Behavior

There is no runtime control flow in this header. The macros affect compiled driver behavior by determining which bits AMDGPU code reads, writes, logs, or decodes in 32-bit MMIO registers.

The state described here is persistent hardware register state. Important state includes MMHUB arbitration thresholds, virtual-channel routing, tag and credit reservations, request blocking, link-manager behavior, performance counter configuration/results, clock-gating overrides, EDC mode and counters, sticky error status, diagnostic/error-injection controls, MMEA2 channel selection, MMEA3 client/group/VC mappings, priority coefficients, address normalization ranges, memory holes, non-power-of-two channel sizing, bank/channel/chip-select/rank/column address decode, and harvest-forced address bits.

Some fields are ordinary latched configuration fields, some are status fields, and some are command-like or clear bits. Examples include `MMEA2_ERR_STATUS__CLEAR_ERROR_STATUS`, request-blocked status in `MMEA2_MISC2`, diagnostic injection enable/select fields, performance result-control fields, and address decoder enable bits. Correct behavior depends on the owning AMDGPU code and hardware sequencing; the generated macros do not encode polling, timeout, reset, or write-one-to-clear semantics.

## Dependencies and Integration Points

This chunk depends on the generated MMHUB register-header set:

- `mmhub_1_7_offset.h` supplies the register offsets and base indices for the register names defined here.
- Other chunks of `mmhub_1_7_sh_mask.h` provide adjacent macro families, including the beginning of `MMEA2_IO_WR_PRI_URGENCY_MASKING` and the remaining `MMEA3_ADDRDEC2_BASE_ADDR_SECCS0` fields.
- AMDGPU SOC15 register helpers consume the `__SHIFT` and `_MASK` constants through `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, and register read/write wrappers.

The direct source-tree integration point is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.c`, which includes `mmhub/mmhub_1_7_sh_mask.h`. Within that file, the RAS tables use `SOC15_REG_FIELD(MMEA2_EDC_CNT*, ...)` and `SOC15_REG_FIELD(MMEA3_EDC_CNT*, ...)` to decode SEC/DED/SED counts, while RAS query/reset paths read and clear the corresponding EDC and error-status registers. This chunk supplies the MMEA2 EDC/status fields used there and the earlier MMEA3 arbitration/address-decode fields that share the same generated header namespace.

Many arbitration, performance, diagnostic, and address-decode fields in this chunk are hardware-facing definitions with no local function body in the header. They become integration points when platform initialization, RAS, bring-up diagnostics, firmware, or register-dump code reads or writes the matching `regMMEA*` offsets.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can write unrelated MMHUB fields, causing memory routing errors, hangs, incorrect RAS accounting, bad performance data, lost fatal-error reporting, or request starvation.
- The repeated MMEA2 and MMEA3 families are mechanically fragile. DRAM/GMI, read/write, `CS01`/`CS23`, primary/secondary chip-select, and address-decoder instance names differ only by small tokens while many masks are identical.
- Arbitration and credit fields affect live memory traffic. Incorrect burst limits, priority coefficients, VC read-only bits, response credits, or tag reserves can alter QoS, throttle traffic, or deadlock under load.
- RAS decoding depends on exact EDC counter fields. If `SOC15_REG_FIELD` receives the wrong mask or shift, SEC/DED/SED counts can be silently misreported or cleared incorrectly.
- Error-status fields mix status, interrupt behavior, busy behavior, and clear controls. Treating clear bits or fatal-interrupt bits as passive status can hide or amplify hardware faults.
- Diagnostic DSM and error-injection fields should remain in controlled test paths. Enabling single-write or error-injection fields unintentionally can create artificial ECC/parity failures.
- Address normalization and decoder fields are topology-critical. Wrong base/limit, interleave, hole, bank, channel, chip-select, rank-map, column, row, or harvest settings can misroute physical memory accesses.
- The chunk starts and ends mid-family. A final merged document must reconcile the preceding `MMEA2_IO_WR_PRI_URGENCY_MASKING` definitions and the following `MMEA3_ADDRDEC2_BASE_ADDR_SECCS0` masks/remaining secondary chip-select fields.

## Test and Validation Signals

Useful validation is mostly integration and hardware bring-up coverage:

- Build AMDGPU with `mmhub_v1_7.c` and the MMHUB 1.7 headers enabled; this catches missing or renamed register-field macros consumed by `SOC15_REG_FIELD` and `REG_SET_FIELD`.
- MMHUB RAS tests should inject or observe SEC/DED/SED events and verify reported counts for `MMEA2_EDC_CNT`, `MMEA2_EDC_CNT2`, `MMEA2_EDC_CNT3`, and adjacent MMEA3 counters match raw register values.
- RAS reset tests should verify EDC counter clearing and `MMEA2_ERR_STATUS`/`MMEA3_ERR_STATUS` handling do not leave stale busy, fatal, or FUE state.
- Stress tests with DRAM, GMI, and IO traffic should watch for regressions in memory bandwidth, latency, hangs, and starvation after any change to SDP arbitration, priority, credit, VC, or urgency fields.
- Performance-counter validation should confirm `MMEA2_PERFCOUNTER*` select/filter/mode/result fields produce stable and expected counter reads.
- Power/clock validation should check `MMEA2_CGTT_CLK_CTRL` changes through suspend/resume, reset, and idle transitions.
- Address topology validation should cover VRAM discovery, GART/FB aperture programming, XGMI/GMI paths, non-power-of-two channel configurations, harvested parts, and memory tests that cross base/limit/hole boundaries.
- Register-dump or golden-header comparison tests should compare generated `mmhub_1_7_sh_mask.h` field values against the vendor register database for MMHUB 1.7.

## Unresolved Cross-Chunk References

This chunk starts after the first 27 shift definitions for `MMEA2_IO_WR_PRI_URGENCY_MASKING`; the complete family requires the previous chunk. It ends immediately after `MMEA3_ADDRDEC2_BASE_ADDR_SECCS0__CS_EN__SHIFT`, before the `BASE_ADDR` shift and masks for `SECCS0` and the rest of address-decoder 2. The merge/reconciliation lane should join those adjacent chunks before producing the final per-file document.
