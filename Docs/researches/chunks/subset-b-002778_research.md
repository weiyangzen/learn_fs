# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_sh_mask.h lines 9432-11750

## Scope

This chunk covers a large generated field-mask slice from the AMD MMHUB 1.8.0 register mask header. It starts mid-register at the tail of `MMEA0_GMI_WR_PRI_AGE`, covers the rest of the MMEA0 GMI/IO arbitration fields, the MMEA0 SDP, performance, error, DSM, clock-gating, and RAS status fields, then begins the `aid_mmhub_ea_mmeadec1` block for MMEA1 DRAM/GMI/IO arbitration. The final line is only the next register marker, `//MMEA1_IO_WR_CLI2GRP_MAP0`; its field definitions are outside this chunk.

The range contains 2,189 `#define` entries grouped under 128 register names with actual field definitions, plus comment delimiters. It has no C functions, structs, enums, storage objects, or executable statements. Its exported surface is a preprocessor namespace of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants used with the matching `mmhub_1_8_0_offset.h` register-address constants and AMDGPU register helper macros.

## Purpose

`mmhub_1_8_0_sh_mask.h` gives symbolic bit positions and bit masks for MMHUB 1.8.0 hardware registers. This chunk describes fields for two MMHUB EA/MMEA decoder instances:

- `MMEA0` fields for GMI and IO request classification, arbitration, priority aging, urgency, quantization, SDP arbitration, performance counters, error reporting, error injection, clock-gating, and corrected/uncorrected error status.
- The start of `MMEA1` fields for DRAM and GMI request classification, virtual-channel mapping, lazy request accumulation, CAM depth/reorder control, page burst limits, priority policy, urgency masking, and the beginning of IO client-to-group mapping.

The header lets driver code set or inspect individual hardware fields without raw shifts and masks. Typical consumers combine a register value with `REG_SET_FIELD()` or `REG_GET_FIELD()`, then write/read the address from `mmhub_1_8_0_offset.h` with SOC15 MMIO helpers.

## Important APIs, Types, And Data

There are no normal C APIs or types. The important interface is the naming contract of generated macros:

- `*_CLI2GRP_MAP0/1__CIDn_GROUP__SHIFT` and `_MASK` map 32 client IDs to four arbitration groups, packed as 2-bit fields. This appears for MMEA0 IO and MMEA1 DRAM/GMI/IO read/write paths.
- `*_GRP2VC_MAP__GROUPn_VC__SHIFT` and `_MASK` map arbitration groups to virtual channels with 3-bit fields. This appears for MMEA1 DRAM and GMI paths in this chunk.
- `*_LAZY__GROUPn_DELAY`, `REQ_ACCUM_THRESH`, `REQ_ACCUM_TIMEOUT`, and `REQ_ACCUM_IDLEMAX` describe request coalescing/accumulation timing for MMEA1 DRAM/GMI read and write traffic.
- `*_CAM_CNTL__DEPTH_GROUPn`, `REORDER_LIMIT_GROUPn`, `REFILL_CHAIN`, and `PAGEBASED_CHAINING` define CAM sizing and chaining behavior for MMEA1 DRAM/GMI reorder control.
- `*_PAGE_BURST__RD_LIMIT_LO/HI` and `WR_LIMIT_LO/HI` define page burst windows for DRAM/GMI traffic.
- `*_PRI_AGE`, `*_PRI_QUEUING`, `*_PRI_FIXED`, `*_PRI_URGENCY`, `*_PRI_URGENCY_MASKING`, and `*_PRI_QUANT_PRI1/2/3` define the priority scheduler model: age rate/coefficient, queueing coefficient, fixed coefficient, urgency coefficient/mode, client urgency masks, and per-group priority thresholds.
- `MMEA0_SDP_ARB_DRAM`, `MMEA0_SDP_ARB_GMI`, and `MMEA0_SDP_ARB_FINAL` define burst limits, read/write switching policy, VC read-only controls, error-event/halt behavior, and burst stretching for the SDP arbitration stage.
- `MMEA0_SDP_*_PRIORITY`, `MMEA0_SDP_CREDITS`, `MMEA0_SDP_TAG_RESERVE*`, `MMEA0_SDP_VCC_RESERVE*`, `MMEA0_SDP_VCD_RESERVE*`, and `MMEA0_SDP_REQ_CNTL` tune SDP read/write group priority, credit accounting, tag/VC reserve sizes, and request control.
- `MMEA0_MISC` and `MMEA0_MISC2` define broader MMEA0 behavior such as group swaps, null request rate, flow control, request blocking, IO read/write priority enablement, and DRAM/GMI throttle bits.
- `MMEA0_LATENCY_SAMPLING`, `MMEA0_PERFCOUNTER_LO/HI`, `MMEA0_PERFCOUNTER0_CFG`, `MMEA0_PERFCOUNTER1_CFG`, and `MMEA0_PERFCOUNTER_RSLT_CNTL` expose latency/performance sampling, counter selection, reset, start/stop, and counter-bank selection fields.
- `MMEA0_UE_ERR_STATUS_LO/HI` and `MMEA0_CE_ERR_STATUS_LO/HI` define status-valid, address-valid, address, memory-ID, ECC, error-info, count, poison, and reserved fields used by RAS error collection.
- `MMEA0_DSM_CNTL`, `MMEA0_DSM_CNTLA`, and `MMEA0_DSM_CNTLB` define diagnostic single-write/irritator controls for DRAM, GMI, IO, return tag, page, and MAM memories.
- `MMEA0_DSM_CNTL2`, `MMEA0_DSM_CNTL2A`, and `MMEA0_DSM_CNTL2B` define error-injection enable/select-delay fields and a global `INJECT_DELAY`.
- `MMEA0_CGTT_CLK_CTRL` defines clock-gating transition delays and soft override bits for write, read, return, register, and light-sleep behavior.
- `MMEA0_EDC_MODE` and `MMEA0_ERR_STATUS` define EDC/FED/FUE behavior, fatal interrupt controls, status clearing, busy-on-error policy, and SDP response status fields.

The first few lines are only masks for `MMEA0_GMI_WR_PRI_AGE` because this chunk begins after that register group's shift definitions. The last line is a marker for `MMEA1_IO_WR_CLI2GRP_MAP0`; its fields are not included here.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by including C files:

1. `amdgpu/mmhub_v1_8.c` includes both `mmhub/mmhub_1_8_0_offset.h` and this `mmhub/mmhub_1_8_0_sh_mask.h` file.
2. Register addresses such as `regMMEA0_CE_ERR_STATUS_LO` come from the offset header; field extraction and updates use this mask header.
3. SOC15 helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, `REG_GET_FIELD`, `AMDGPU_RAS_REG_ENTRY`, and `SOC15_REG_FIELD` provide the actual control flow that reads, writes, or describes the registers.
4. In `mmhub_v1_8.c`, the RAS tables use MMEA0 and MMEA1 CE/UE status register pairs. The RAS framework later reads those registers, checks validity flags, decodes memory IDs and error metadata, and reports corrected or uncorrected MMHUB errors.
5. Other arbitration, DSM, performance-counter, and clock-gating fields are generated ABI for firmware, diagnostics, or later driver paths even when the local `mmhub_v1_8.c` file does not actively program each field.

## State And Persistence Behavior

The macros themselves are compile-time constants and hold no state. The hardware registers they describe do hold persistent MMHUB state until reset or reprogramming:

- Client-to-group, group-to-VC, lazy accumulation, CAM, page-burst, priority, urgency, and quantization fields shape how MMEA instances schedule DRAM/GMI/IO memory traffic. Bad values can remain active across normal workloads until a GPU reset, suspend/resume restore, or explicit MMHUB reinitialization rewrites them.
- SDP arbitration, reserve, credit, and request-control fields affect downstream request dispatch and fairness for MMEA0 traffic.
- Performance-counter and latency-sampling fields select what hardware events are counted and whether counters run, reset, or dump accumulated values.
- CE/UE status registers persist hardware error observations, including valid flags, addresses, memory IDs, error-info fields, ECC/poison information, and count fields, until the relevant RAS clear/read flow or hardware reset changes them.
- DSM and error-injection fields can intentionally perturb or inject memory errors. These are diagnostic hardware state, not normal software allocations.
- Clock-gating and EDC mode fields influence low-power entry/exit and error propagation behavior for MMEA0.

No disk state, heap allocation, reference counting, locks, or software-owned object lifetime exists in the header. Ordering and synchronization belong to the driver paths that perform MMIO reads and writes.

## Dependencies

This chunk depends on the generated MMHUB 1.8.0 hardware register specification and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_offset.h`, which supplies the matching `regMMEA*` register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_8.c`, the primary local MMHUB 1.8 consumer, including RAS register lists for `MMEA0` and `MMEA1`.
- AMDGPU SOC15 register helpers and field helpers: `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, `REG_GET_FIELD`, `AMDGPU_RAS_REG_ENTRY`, and `SOC15_REG_FIELD`.
- The AMDGPU RAS framework, which interprets CE/UE status pairs and memory IDs using register metadata and validity flags.
- Hardware/firmware flows that program arbitration, urgency, DSM, error injection, clock-gating, performance counters, and SDP policy for MMHUB EA/MMEA blocks.

Because this is a generated ASIC header, dependency correctness is mostly about version alignment: MMHUB 1.8.0 field masks must be used with MMHUB 1.8.0 offsets and with driver code that targets the same IP version.

## Integration Points

- `mmhub_v1_8.c` includes this header directly, so all `MMEA*__FIELD_MASK` and `MMEA*__FIELD__SHIFT` definitions are available to the MMHUB 1.8 implementation.
- `mmhub_v1_8_ce_reg_list` references `regMMEA0_CE_ERR_STATUS_LO/HI` and `regMMEA1_CE_ERR_STATUS_LO/HI`; the field definitions in this chunk describe how those status words encode valid flags, address bits, memory IDs, ECC, error info, count, and poison state.
- `mmhub_v1_8_ue_reg_list` references `regMMEA0_UE_ERR_STATUS_LO/HI` and `regMMEA1_UE_ERR_STATUS_LO/HI`; this chunk includes the MMEA0 UE masks and starts the MMEA1 register families used by the same RAS block.
- `mmhub_v1_8_ras_memory_list` maps reported memory IDs to names such as `MMEA_WGMI_PAGEMEM`, `MMEA_RGMI_PAGEMEM`, `MMEA_WDRAM_PAGEMEM`, `MMEA_RDRAM_CMDMEM`, `MMEA_MAM_DMEM*`, `MMEA_WRET_TAGMEM`, and `MMEA_RRET_TAGMEM`. Those names align with the DSM/error-injection and CE/UE status fields in this mask slice.
- `mmhub_1_8_0_offset.h` places these register groups in the address space, for example MMEA0 error/DSM/clock fields around `regMMEA0_UE_ERR_STATUS_LO`, `regMMEA0_DSM_CNTL*`, `regMMEA0_CGTT_CLK_CTRL`, `regMMEA0_EDC_MODE`, `regMMEA0_ERR_STATUS`, `regMMEA0_CE_ERR_STATUS_LO/HI`, and MMEA1 DRAM/GMI/IO policy fields beginning at `regMMEA1_DRAM_RD_CLI2GRP_MAP0`.
- Diagnostic or bring-up tooling can use the performance-counter, latency-sampling, DSM, and error-injection fields to select internal MMEA events, inject failures, and verify RAS reporting paths.

## Risks

- Generated-header drift is the primary risk. A wrong shift or mask compiles cleanly but can cause driver code to read or write the wrong bits in a live MMHUB register.
- The chunk starts and ends on partial register boundaries. A reconciled final document must not treat `MMEA0_GMI_WR_PRI_AGE` or `MMEA1_IO_WR_CLI2GRP_MAP0` as fully covered by this chunk alone.
- Cross-generation copying is hazardous. MMEA/MMHUB names recur across MMHUB 1.0, 1.7, 1.8, 9.4, and related ASIC headers, but offsets, masks, and supported fields can differ.
- Arbitration and priority fields can alter memory fairness and latency. Incorrect client grouping, VC mapping, lazy thresholds, CAM depth, urgency masking, or priority coefficients can cause starvation, performance collapse, timeout behavior, or fabric backpressure.
- RAS status masks are safety-critical for observability. Mis-decoding valid flags, memory IDs, CE counts, poison bits, or error-info fields can hide real hardware faults or attribute them to the wrong MMHUB memory.
- DSM and error-injection fields are intentionally disruptive. Enabling them outside controlled diagnostics can create synthetic faults or corrupt normal validation signals.
- Clock-gating and EDC/FED/FUE policy bits interact with power and fault handling. Bad settings can cause stalls, missed fatal interrupts, spurious busy state, or failure to propagate fatal errors.
- Many fields are densely packed. Updating a field without preserving unrelated bits, or using a mask with the wrong register instance, can silently change neighboring fields.

## Test Signals

- Build AMDGPU with MMHUB 1.8 enabled so `mmhub_v1_8.c` compiles against `mmhub_1_8_0_offset.h` and this mask header.
- Generated-header validation should compare every shift/mask pair in this line range against the authoritative MMHUB 1.8.0 register database and verify that each field lies inside the expected 32-bit register.
- Static checks should ensure `REG_SET_FIELD`/`REG_GET_FIELD`, `SOC15_REG_FIELD`, and RAS register entries use field names that exist in this header and register names that exist in the matching offset header.
- Runtime RAS testing should inject or provoke corrected and uncorrected MMHUB errors, then verify CE/UE valid flags, memory IDs, addresses, error-info fields, poison flags, and counts decode correctly for MMEA0 and MMEA1.
- Stress testing should exercise DRAM, GMI, and IO traffic under GPUVM workloads, peer/XGMI traffic, and display/media access while monitoring for VM faults, fabric stalls, request timeouts, and RAS noise.
- Diagnostic validation should program performance counters and latency sampling to known event selections and confirm counter reset/start/stop/dump behavior.
- Power-management smoke should verify clock-gating transitions around MMHUB activity do not introduce stalls or missed error reporting.
- Resume/reset tests should confirm MMHUB arbitration, error status, RAS, and diagnostic state either reinitializes to known-good values or is intentionally preserved according to the platform reset model.
