# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_sh_mask.h lines 14068-16391

## Scope

This chunk is a generated shift/mask section from the AMDGPU MMHUB 1.8.0 register header. It contains only C preprocessor constants and register-block comments; there are no functions, structs, enums, variables, allocations, locks, or executable branches in the requested range.

The range starts in the tail of `MMEA2_IO_WR_PRI_URGENCY_MASKING`, covers the rest of the MMEA2 memory-engine-address-decoder field map through `MMEA2_CE_ERR_STATUS_HI`, then starts `addressBlock: aid_mmhub_ea_mmeadec3` and covers most of the matching MMEA3 field map. It ends inside `MMEA3_LATENCY_SAMPLING`, after the `SAMPLER0_WRITE` shift definition and before the remaining latency-sampling fields and masks in the next chunk.

Major covered families are:

- MMEA2 IO priority quantization, SDP arbitration/priority/credits/tag and VC reserve controls, request control, miscellaneous arbitration behavior, latency sampling, performance counters, uncorrectable and correctable error status, DSM/error-injection controls, clock control, EDC mode, error status, request throttling, and always-on link-manager fields.
- MMEA3 DRAM/GMI/IO client-to-group maps, group-to-VC maps, lazy accumulation, CAM and page/group burst controls, priority aging/queuing/fixed/urgency/urgency masking/quantization controls, SDP arbitration/priority/credits/tag and VC reserve controls, request control, miscellaneous arbitration behavior, and the beginning of latency sampling.

## Purpose

The purpose of this header slice is to publish the bit-level ABI for MMHUB 1.8.0 MMEA2 and MMEA3 registers. Each field is represented with the generated AMD register-header convention:

- `<REGISTER>__<FIELD>__SHIFT`: the field's bit offset.
- `<REGISTER>__<FIELD>_MASK`: the 32-bit mask used to isolate or compose that field.

The sibling `mmhub_1_8_0_offset.h` header supplies the register offsets such as `regMMEA2_CE_ERR_STATUS_LO`, `regMMEA3_UE_ERR_STATUS_HI`, and the MMEA arbitration/control register names. This chunk supplies the field positions and masks that AMDGPU code can use with helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15`.

Although the source tree path is under a local `ceph-client` mirror, the content is AMD GPU MMIO metadata, not Ceph or distributed filesystem logic.

## Important APIs, Types, And Macros

There are no normal C APIs or types in this range. The public interface is the macro namespace for MMEA2/MMEA3 register fields.

Important macro groups include:

- `MMEA2_IO_RD_PRI_QUANT_PRI*` and `MMEA2_IO_WR_PRI_QUANT_PRI*`: four 8-bit group threshold fields per priority-quantization register.
- `MMEA2_SDP_ARB_DRAM`, `MMEA2_SDP_ARB_GMI`, and `MMEA2_SDP_ARB_FINAL`: burst limits, early read/write switch controls, error-event and halt-request controls, read-only VC flags, and burst stretching.
- `MMEA2_SDP_{DRAM,GMI,IO}_PRIORITY`: packed 4-bit read/write priorities for groups 0 through 3.
- `MMEA2_SDP_CREDITS`, `MMEA2_SDP_TAG_RESERVE*`, `MMEA2_SDP_VCC_RESERVE*`, and `MMEA2_SDP_VCD_RESERVE*`: tag limits, response credits, tag reserves, and VC credit reserves for VCC/VCD pools, including `DISTRIBUTE_POOL`.
- `MMEA2_SDP_REQ_CNTL` and `MMEA3_SDP_REQ_CNTL`: request pass/write/atomic override bits, DRAM/GMI chain override bits, inner-domain mode, and block-level controls for read/write/atomic traffic.
- `MMEA2_MISC`, `MMEA2_MISC2`, `MMEA2_MISC_AON`, and `MMEA3_MISC`: relative arbitration priority flags, early write-return enable flags per VC, link-manager thresholds/delays, chain-switch/favour flags, CSGROUP swapping, IO read/write priority enable, request blocking, and DRAM/GMI throttles.
- `MMEA2_PERFCOUNTER_LO`, `MMEA2_PERFCOUNTER_HI`, `MMEA2_PERFCOUNTER0_CFG`, `MMEA2_PERFCOUNTER1_CFG`, and `MMEA2_PERFCOUNTER_RSLT_CNTL`: counter result fields, compare value, performance event range selection, mode, enable/clear, trigger controls, global clear, and stop-on-saturate behavior.
- `MMEA2_UE_ERR_STATUS_*` and `MMEA2_CE_ERR_STATUS_*`: valid flags, address fields, memory IDs, ECC/parity/poison flags, error-info fields, and UE/CE/FED counters. These are directly referenced by the MMHUB 1.8 RAS register tables.
- `MMEA2_DSM_CNTL*` and `MMEA2_DSM_CNTL2*`: data-share-memory single-write controls and error-injection enables/delay selectors for DRAM, GMI, IO, read-return/write-return tags, page memories, and MAM D0-D3 memories.
- `MMEA2_CGTT_CLK_CTRL` and `MMEA2_EDC_MODE`: on/off clock-gating timing, soft overrides, light-sleep override, EDC count/gate/dedicated-mode/propagate/bypass controls.
- `MMEA2_ERR_STATUS`: SDP response status/data status, parity error, clear/busy flags, fatal interrupt control, level-interrupt mode, and FUE client status.
- MMEA3 `*_CLI2GRP_MAP0/1`: 32 client-ID group mappings split into low and high halves for DRAM, GMI, and IO read/write paths.
- MMEA3 `*_GRP2VC_MAP`, `*_LAZY`, `*_CAM_CNTL`, page/group burst, and priority families: group-to-VC mapping, accumulation thresholds/timeouts/idle limits, CAM depth/reorder limits, chaining controls, read/write burst windows, aging/queuing/fixed/urgency coefficients, per-client urgency masking, and quantization thresholds.

## Control Flow

This chunk has no runtime control flow. Its effect is compile-time name binding for driver code that reads or writes MMHUB registers.

Runtime sequencing is owned by consumers:

1. AMDGPU MMHUB 1.8 code includes `mmhub_1_8_0_offset.h` and `mmhub_1_8_0_sh_mask.h`.
2. Code selects a register offset with `reg...` or `mm...` symbols from the offset header.
3. Register helpers compose field values using the `__SHIFT` and `_MASK` macros from this file.
4. MMIO helpers read, update, or write the register on the relevant MMHUB instance.

The chunk does not describe when a register may be written, whether a field is read-only, self-clearing, sticky, or write-one-to-clear, or what polling is required. Those rules come from the hardware specification and the higher-level MMHUB/RAS/performance/clock-gating code.

## State And Persistence Behavior

The header itself stores no software state and persists nothing. It describes MMIO-backed hardware state in the MMHUB memory-engine address-decode path.

The represented hardware state includes:

- Traffic classification state: mapping up to 32 client IDs into four arbitration groups for MMEA3 DRAM, GMI, and IO read/write paths.
- Arbitration and QoS state: group-to-VC mapping, priority coefficients, urgency modes, per-client urgency masking, priority quantization thresholds, burst limits, read-only VC flags, chain-breaking and page-based chaining controls, CAM depth/reorder limits, and read/write switch preferences.
- Credit and reserve state: SDP tag limits, read/write response credits, tag reservations for VC0-VC7, and VCC/VCD credit reserves with optional distributed pools.
- Request-control state: pass/write/atomic overrides, DRAM/GMI chain overrides, request block levels, and inner-domain mode.
- Error and RAS state: CE/UE status valid bits, failing address and memory ID fields, ECC/parity/poison flags, error-info payloads, CE/UE/FED counters, SDP response error state, FUE flags, fatal-interrupt control, and clear/busy bits.
- Diagnostic state: MMEA2 performance counter selection/results, result triggers, latency-sampling enables, DSM irritator/single-write controls, and DSM error-injection delay/enables.
- Power/clock and link-manager state: CGTT delay/override fields, EDC mode flags, early write-return flags, relative priority flags, link-manager dynamic mode/thresholds/reconnect delay/idle behavior, and always-on part-ack hysteresis/deassert mode.

Persistence is hardware-defined. Configuration fields generally persist until reprogrammed, reset, power-gated, or restored after suspend/resume. Status, error, interrupt, counter, clear, and injection fields may be sticky, read-only, write-one-to-clear, self-clearing, or sequencing-sensitive. The masks alone do not encode those semantics.

## Dependencies And Integration Points

This chunk depends on the generated MMHUB 1.8.0 register-header set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_offset.h` supplies the matching register addresses and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_default.h`, where present for this ASIC generation, supplies reset/default values.
- AMDGPU SOC15 register helpers consume the offset and mask headers together.

The direct include site observed in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_8.c`, which includes this header together with `mmhub_1_8_0_offset.h`.

The clearest direct consumer for this specific chunk is MMHUB RAS setup in `mmhub_v1_8.c`. The CE and UE register lists reference `regMMEA2_CE_ERR_STATUS_LO/HI`, `regMMEA3_CE_ERR_STATUS_LO/HI`, `regMMEA2_UE_ERR_STATUS_LO/HI`, and `regMMEA3_UE_ERR_STATUS_LO/HI`. The RAS framework can then pair those offsets with generated status fields such as valid flags, address, memory ID, ECC/parity, error-info, and counters.

Other integration is implied by the generated register contract rather than visible direct references in this source slice:

- MMHUB QoS/arbitration tuning code can use MMEA2/MMEA3 DRAM/GMI/IO priority, burst, urgency, client mapping, and credit fields.
- Performance/debug paths can use MMEA2 performance counter and latency-sampling macros to select events, clear counters, set triggers, and read results.
- RAS and validation paths can use DSM and EDC/error-status fields for error injection, error propagation, and status decoding.
- Clock-gating and power-management paths can use CGTT/link-manager fields when coordinating MMHUB power and traffic-idle behavior.

Cross-generation similarity is high but not safe to assume. The repeated MMEA2/MMEA3 families resemble other MMHUB versions, but masks, field presence, and register offsets must remain matched to the 1.8.0 offset/mask/default set.

## Risks And Edge Cases

- Bitfield drift is high impact. A wrong shift or mask can silently program a different hardware field, causing traffic starvation, incorrect VC assignment, MMHUB hangs, bad RAS decoding, or broken performance counters.
- The repeated DRAM/GMI/IO and read/write families are copy-sensitive. Many field layouts are identical, but a typo across `MMEA3_DRAM_*`, `MMEA3_GMI_*`, and `MMEA3_IO_*` may affect only one traffic class or direction.
- Client-ID maps cover 32 clients in two registers. Off-by-one or low/high-half mistakes can route a single client to the wrong arbitration group and only appear under specific engines or workloads.
- QoS and arbitration fields interact. Priority coefficients, urgency masking, quantization thresholds, burst limits, CAM depth/reorder limits, VC mapping, and credit reserves should be validated as a set; changing one field can starve or over-prioritize another traffic class.
- Error status fields are RAS-visible. Misdecoding valid flags, memory IDs, address bits, CE/UE counts, FED counts, or poison/parity/ECC flags can produce wrong user-visible error reports or hide actionable failures.
- DSM and EDC controls are diagnostic and fault-injection sensitive. Enabling injection, bypassing EDC, or changing delay/single-write behavior in production paths can create artificial errors or mask real ones.
- Some fields are command-like or status-like despite being represented as plain masks, such as clear-error bits, counter clear bits, request-blocked status, injection enables, and busy-on-error controls. Consumers must follow hardware sequencing.
- The chunk starts and ends mid-family: `MMEA2_IO_WR_PRI_URGENCY_MASKING` begins before this range, and `MMEA3_LATENCY_SAMPLING` continues after it. The merge lane should join adjacent chunk research before making complete file-level claims about those two registers.

## Test Signals

Useful validation is mostly build coverage, generated-header consistency, and hardware/RAS behavior:

- Build AMDGPU with MMHUB 1.8 support enabled. Missing or renamed macros should fail in `mmhub_v1_8.c` and related SOC15 register code.
- Mechanically compare this generated header against AMD's authoritative MMHUB 1.8.0 register database and the matching `mmhub_1_8_0_offset.h`; each register field here must correspond to the correct offset name and bit layout.
- RAS tests should inject or observe MMHUB CE/UE events and verify that MMEA2/MMEA3 status valid flags, address fields, memory IDs, ECC/parity/poison flags, error-info fields, and CE/UE/FED counters decode correctly.
- MMHUB stress tests should exercise DRAM, GMI, and IO read/write traffic under mixed GPU engines to catch client-group, priority, urgency, credit, and VC-reserve programming errors.
- Performance-counter validation should select MMEA2 events, clear counters, use start/stop triggers, read LO/HI results, and verify stop-on-saturate or compare behavior where supported.
- Clock-gating and suspend/resume tests should cover CGTT, link-manager, EDC, and arbitration state restoration around reset, power gating, and resume.
- Error-path diagnostics should watch kernel logs and RAS telemetry for stuck busy/error bits, incorrect fatal interrupt behavior, unexpected request blocking, malformed memory IDs, or repeated CE/UE counter values.

## Cross-Chunk Notes

Adjacent chunks are required for complete coverage of the surrounding generated file. The previous chunk owns the beginning of `MMEA2_IO_WR_PRI_URGENCY_MASKING`, and the next chunk owns the rest of `MMEA3_LATENCY_SAMPLING` plus later MMHUB 1.8.0 register fields. The final per-file research document should reconcile those boundaries before describing complete MMEA2/MMEA3 latency and urgency-masking behavior.
