# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h lines 11790-14143

## Scope

This chunk is part of the generated AMDGPU MMHUB 1.7 shift/mask header. It contains C preprocessor constants for register bit fields, not executable routines. The constants define `__SHIFT` and `_MASK` values consumed with matching register offsets from `mmhub_1_7_offset.h` and AMDGPU register access helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, and direct masked writes.

The covered range starts mid-register at `MMEA0_ADDRNORMGMI_HOLE_CNTL`, continues through most of `addressBlock: mmhub_ea_mmeadec0`, and ends in the early `addressBlock: mmhub_ea_mmeadec1` GMI read client-to-group map. The main functional surfaces are MMEA0 address normalization/decode, MMEA0 IO request grouping and arbitration, MMEA0 SDP arbitration/credits/error handling, and MMEA1 DRAM/GMI arbitration masks.

## Purpose

MMEA appears to be an MMHUB memory-client endpoint/address-decode block. These macros describe how firmware or driver code can program address decoding, client grouping, priorities, credits, error reporting, and clock/error-injection behavior for MMHUB 1.7 hardware. Because this is a register-definition header, its purpose is ABI-like: keep software field positions synchronized with the hardware register specification for this ASIC generation.

The chunk is especially important for memory topology and quality-of-service programming:

- `MMEA0_ADDRNORM*` and `MMEA0_ADDRDEC*` fields define how normalized addresses become DRAM/GMI chip-select, bank, row, column, rank-mirror, and channel selections.
- `MMEA0_IO_*` and `MMEA1_DRAM_*` fields map client IDs into four arbitration groups and tune group age, queuing, fixed-priority, urgency, and quantized priority thresholds.
- `MMEA0_SDP_*` fields control final request arbitration, virtual-channel credit/tag reservation, request block/pass behavior, and error escalation.
- `MMEA0_EDC*`, `MMEA0_DSM*`, and `MMEA0_ERR_STATUS` fields expose error-detection counters/status and hardware diagnostic/error-injection controls.

## Important Macro Families

Address normalization and decode:

- `MMEA0_ADDRNORMGMI_HOLE_CNTL` exposes DRAM hole validity and offset fields.
- `MMEA0_ADDRNORMDRAM_NP2_CHANNEL_CFG` and `MMEA0_ADDRNORMGMI_NP2_CHANNEL_CFG` define log2 non-power-of-two channel address spaces.
- `MMEA0_ADDRDEC_BANK_CFG`, `MMEA0_ADDRDEC_MISC_CFG`, `MMEA0_ADDRDECDRAM_HARVEST_ENABLE`, and `MMEA0_ADDRDECGMI_HARVEST_ENABLE` describe DRAM/GMI bank masks, bank-group selection/interleave, VCM enable bits, pseudo-channel/channel/chip-select/rank-mirror masks, and forced harvested bits.
- `MMEA0_ADDRDEC{0,1,2}_*` define three parallel address-decode channels. Each channel has primary and secondary chip-select base registers, masks for CS01/CS23 and SECCS01/SECCS23, geometry config (`NUM_BANK_GROUPS`, `NUM_RM`, row/column/bank counts, `HI_COL_EN`), bank/row selectors, optional `BANK5` and `CHAN_BIT` selectors, column low/high selectors, and rank-mirror selectors with row-MSB inversion.
- `MMEA0_ADDRNORM_MEGACONTROL_ADDR{0,1}`, `MMEA0_ADDRNORMDRAM_MASKING`, `MMEA0_ADDRNORMGMI_MASKING`, and `MMEA0_ADDRDEC_SELECT` provide wider selection/masking controls for normalized address high bits and channel ranges.

IO arbitration and grouping for MMEA0:

- `MMEA0_IO_RD_CLI2GRP_MAP{0,1}` and `MMEA0_IO_WR_CLI2GRP_MAP{0,1}` pack 32 client IDs into 2-bit group fields, with client IDs 0-15 in map0 and 16-31 in map1.
- `MMEA0_IO_RD_COMBINE_FLUSH` and `MMEA0_IO_WR_COMBINE_FLUSH` define per-group combine-flush timers and combine mode.
- `MMEA0_IO_GROUP_BURST` defines low/high burst limits for read and write IO traffic.
- `MMEA0_IO_*_PRI_AGE`, `MMEA0_IO_*_PRI_QUEUING`, `MMEA0_IO_*_PRI_FIXED`, `MMEA0_IO_*_PRI_URGENCY`, `MMEA0_IO_*_PRI_URGENCY_MASKING`, and `MMEA0_IO_*_PRI_QUANT_PRI{1,2,3}` provide group-based arbitration inputs: aging rates, age coefficients, queuing coefficients, fixed coefficients, urgency coefficients/modes, per-client urgency masks, and quantized priority thresholds.

SDP/final request path:

- `MMEA0_SDP_ARB_DRAM`, `MMEA0_SDP_ARB_GMI`, and `MMEA0_SDP_ARB_FINAL` describe burst limits, early read/write switch controls, end-of-burst behavior, read-only virtual-channel flags, GMI burst stretching, throttles, and error escalation bits such as `ERREVENT_ON_ERROR` and `HALTREQ_ON_ERROR`.
- `MMEA0_SDP_DRAM_PRIORITY`, `MMEA0_SDP_GMI_PRIORITY`, and `MMEA0_SDP_IO_PRIORITY` pack 4-bit read/write priorities for groups 0-3.
- `MMEA0_SDP_CREDITS`, `MMEA0_SDP_TAG_RESERVE{0,1}`, `MMEA0_SDP_VCC_RESERVE{0,1}`, and `MMEA0_SDP_VCD_RESERVE{0,1}` define tag, response, and per-virtual-channel credit reservation fields.
- `MMEA0_SDP_REQ_CNTL` has pass/chain override bits for reads, writes, atomics, DRAM, and GMI plus request block levels.

Observability, error, diagnostics, and clock control:

- `MMEA0_LATENCY_SAMPLING`, `MMEA0_PERFCOUNTER_LO`, `MMEA0_PERFCOUNTER_HI`, `MMEA0_PERFCOUNTER{0,1}_CFG`, and `MMEA0_PERFCOUNTER_RSLT_CNTL` support sampling and performance-counter configuration/result handling.
- `MMEA0_EDC_CNT`, `MMEA0_EDC_CNT2`, and `MMEA0_EDC_CNT3` expose SEC/SED/DED count fields for DRAM, GMI, IO, return tag, and MAM memories.
- `MMEA0_DSM_CNTL`, `MMEA0_DSM_CNTLA`, `MMEA0_DSM_CNTL2`, and `MMEA0_DSM_CNTL2A` define diagnostic single-write and error-injection controls for command/data/page/tag memories. `MMEA0_DSM_CNTLB` and `MMEA0_DSM_CNTL2B` are present as empty register comments in this chunk.
- `MMEA0_CGTT_CLK_CTRL` exposes clock-gating timing, soft stall overrides, light-sleep override, and soft read/write/return/register overrides.
- `MMEA0_EDC_MODE` and `MMEA0_ERR_STATUS` define fatal/uncorrectable error behavior, propagation/gating/bypass, error clearing, busy-on-error behavior, interrupt controls, and response status fields.
- `MMEA0_MISC`, `MMEA0_MISC2`, and `MMEA0_MISC_AON` contain miscellaneous arbitration, early write-return, request blocking, chip-select group swap, IO read/write priority enable, return swap, and link manager partial-ack fields.

MMEA1 block start:

- The range switches to `addressBlock: mmhub_ea_mmeadec1` near the end.
- `MMEA1_DRAM_RD_CLI2GRP_MAP{0,1}` and `MMEA1_DRAM_WR_CLI2GRP_MAP{0,1}` repeat the 32-client, 2-bit group mapping scheme for DRAM reads and writes.
- `MMEA1_DRAM_RD_GRP2VC_MAP` and `MMEA1_DRAM_WR_GRP2VC_MAP` map groups 0-3 to virtual channels.
- `MMEA1_DRAM_RD_LAZY`, `MMEA1_DRAM_WR_LAZY`, `MMEA1_DRAM_RD_CAM_CNTL`, `MMEA1_DRAM_WR_CAM_CNTL`, and `MMEA1_DRAM_PAGE_BURST` control lazy timer/max burst behavior, client CAM address/mask, match enable/update policy, and page burst limits.
- `MMEA1_DRAM_*_PRI_*` mirror the MMEA0 arbitration scheme for DRAM traffic: age, queuing, fixed, urgency, and quantized priority thresholds.
- The chunk ends after `MMEA1_GMI_RD_CLI2GRP_MAP1` begins, so the rest of MMEA1 GMI and later MMEA1 controls are cross-chunk dependencies.

## Control Flow and Data Flow

There is no runtime control flow in this header. At build time, the preprocessor exposes named bit positions and masks. At runtime, driver or firmware-facing code uses these macros to compose 32-bit register values, write MMIO registers, and decode readback/status values.

Typical flow implied by the macros:

1. Include `mmhub_1_7_offset.h` for register addresses and this header for fields.
2. Build register values by shifting field values by `__SHIFT` and applying `_MASK`, usually through AMDGPU helper macros.
3. Program address decode before memory traffic is enabled or when topology changes require updated channel/chip-select/bank mapping.
4. Program arbitration/group/credit controls before sustained traffic or power/performance transitions.
5. Read status/performance/error registers and extract fields using the masks.
6. For diagnostics, set DSM/error-injection controls, observe EDC counters/status, and clear error status through `CLEAR_ERROR_STATUS`.

## State and Persistence Behavior

The header itself has no state. The state represented by these fields lives in hardware MMIO registers. Register writes persist in the hardware block until reset, power-gating domain loss, driver reinitialization, suspend/resume restoration, or explicit reprogramming.

Several fields represent durable hardware configuration while the GPU is running:

- Address-decode base/mask/geometry/selector fields affect all subsequent address routing for the programmed channels.
- Client-to-group maps and priority coefficients persistently shape arbitration and QoS decisions.
- Credit/tag/VC reservation fields persistently affect outstanding request capacity and fairness.
- Diagnostic and error-injection bits can persist long enough to corrupt normal execution if left enabled outside controlled tests.
- Status and counter fields are hardware-observed state; some may be sticky or clear-on-write depending on the register spec. This chunk exposes the bit names but not write/clear semantics beyond visible names such as `CLEAR_ERROR_STATUS`.

## Dependencies and Integration Points

This chunk depends on the adjacent generated MMHUB headers:

- `mmhub_1_7_offset.h` provides the matching `reg...` addresses and base indices.
- Other chunks of `mmhub_1_7_sh_mask.h` provide the preceding MMEA0 fields, earlier DAGB fields, and the remainder of MMEA1 fields.
- AMDGPU register helper macros in the DRM AMD driver infrastructure consume the `REG__FIELD__SHIFT` and `REG__FIELD_MASK` naming convention.

Integration points are hardware-generation-specific. These masks should only be used by code paths that select MMHUB 1.7 register tables. Similar register names appear in other MMHUB generation headers, but bit layouts can differ, for example bank-mask widths and optional VCM/hash fields differ across ASIC versions. Code must not mix offsets from one MMHUB version with masks from another.

The register groups integrate with:

- GPU memory controller/topology setup through address decode and normalized-address controls.
- MMHUB arbitration and QoS policy through client group maps, priorities, credits, and virtual-channel controls.
- Power management through clock-gating override controls.
- RAS/EDC diagnostics through counters, status, error propagation/interrupt controls, and DSM/error-injection knobs.
- Performance tooling through latency sampling and performance counter fields.

## Risks and Edge Cases

- Incorrect address-decode masks, base addresses, chip-select enables, channel bits, bank selectors, row/column selectors, or rank-mirror inversion fields can route memory traffic incorrectly and cause data corruption or hangs.
- Programming DRAM/GMI/IO arbitration fields with mismatched client-group maps and priority coefficients can starve clients, reduce throughput, or break latency assumptions.
- Credit and tag-reservation values are capacity controls; bad values can deadlock, throttle, or overcommit the SDP path.
- Error-injection and DSM single-write fields are hazardous outside diagnostic sequences. Leaving them enabled can create artificial EDC events or corrupt internal memories.
- `MMEA0_ERR_STATUS` includes interrupt and busy-on-error controls; wrong configuration can either hide fatal faults or hold the block busy after an error.
- Empty comment-only registers such as `MMEA0_DSM_CNTLB` and `MMEA0_DSM_CNTL2B` should not be assumed to have no hardware behavior; they may be reserved or defined elsewhere in the hardware spec, but this header chunk provides no field macros for them.
- The chunk boundary splits MMEA1 GMI definitions after `MMEA1_GMI_RD_CLI2GRP_MAP1`. Whole-file research must reconcile later chunks before describing the full MMEA1 GMI path.
- Generated headers are easy to use mechanically but hard to validate by inspection. A one-bit shift/mask error can compile cleanly and only surface as hardware malfunction.

## Test and Verification Signals

Useful validation signals for this chunk are mostly integration and hardware tests rather than unit tests:

- Compile coverage for MMHUB 1.7 paths that include this header and use `REG_SET_FIELD`/`REG_GET_FIELD` with these macro names.
- Register readback tests after programming address-decode, arbitration, and credit fields, checking that packed values decode to the intended field values.
- GPU bring-up tests that exercise VRAM/DRAM and GMI traffic across all enabled channels/chip-selects, including harvested configurations and non-power-of-two channel spaces.
- Stress tests with mixed IO, DRAM, GMI, read, write, and atomic traffic to expose bad priority, urgency, credit, or virtual-channel programming.
- RAS/EDC diagnostic tests that intentionally inject errors through `MMEA0_DSM_CNTL2*`, observe `MMEA0_EDC_CNT*` and `MMEA0_ERR_STATUS`, then clear and verify recovery behavior.
- Suspend/resume and power-gating tests to ensure persistent hardware configuration is restored after domain loss.
- Cross-version register audit comparing `mmhub_1_7_offset.h` against this mask header and ensuring callers selected the matching MMHUB 1.7 tables.

## Cross-Chunk Notes

This chunk begins after the first line of `MMEA0_ADDRNORMGMI_HOLE_CNTL`; the register comment and any preceding fields are in the prior chunk. It ends inside the MMEA1 GMI client-group map area, so the remainder of MMEA1 GMI arbitration, MMEA1 SDP/error/diagnostic fields, and any later address blocks must be researched from subsequent chunks before producing a final per-file document.
