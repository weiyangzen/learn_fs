# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_sh_mask.h lines 11751-14067

## Scope

This chunk covers 2,317 lines from the generated AMD MMHUB 1.8.0 shift/mask header. The range starts at `MMEA1_IO_WR_CLI2GRP_MAP0__CID0_GROUP__SHIFT` and ends at `MMEA2_IO_WR_PRI_URGENCY_MASKING__CID23_MASK_MASK`, so both boundaries are inside larger generated register families: the preceding chunk owns the `MMEA1_IO_RD_*` setup and the following chunk owns the remaining `MMEA2_IO_WR_PRI_URGENCY_MASKING` mask bits plus the later `MMEA2_IO_*` quantization and SDP/error-control fields.

The slice contains 2,190 `#define` field macros. There are no functions, structs, enums, variables, inline helpers, allocations, locks, or executable statements. Its API surface is entirely the preprocessor namespace of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants.

## Purpose

`mmhub_1_8_0_sh_mask.h` supplies bit positions and bit masks for fields in the MMHUB 1.8.0 register map. Driver code includes it with `mmhub_1_8_0_offset.h` so register accesses can use symbolic offsets plus symbolic fields through AMDGPU helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and RAS register-table helpers.

This chunk describes the memory-management engine arbiter (`MMEA`) fields for engine instance 1 and the beginning of instance 2:

- `MMEA1` IO read/write client grouping, combine-flush, group burst, priority aging, queuing, fixed-priority, urgency, urgency masking, quantized-priority thresholds, SDP arbitration, SDP priority, credit reserve, miscellaneous control, latency sampling, performance counters, correctable/uncorrectable error status, and DSM error-injection controls.
- `MMEA2` DRAM and GMI client grouping, group-to-virtual-channel mapping, lazy request accumulation, CAM/reorder controls, page-burst limits, priority aging/queuing/fixed/urgency/quantization, and the start of IO grouping and urgency masking.

These macros do not themselves configure the GPU. They are the generated ABI that lets MMHUB v1.8 code and diagnostics build correctly packed 32-bit register values for arbitration, routing, performance, RAS, and error-injection registers.

## Important APIs, Types, And Data

The exported data is organized by hardware register name. Important groups in this chunk include:

- `MMEA1_IO_WR_CLI2GRP_MAP0/1` map IO write client IDs 0-31 into four scheduler groups using two-bit `CID*_GROUP` fields. The corresponding `MMEA1_IO_RD_CLI2GRP_MAP0/1` fields are in the previous chunk.
- `MMEA1_IO_RD_COMBINE_FLUSH` and `MMEA1_IO_WR_COMBINE_FLUSH` expose four group timers plus `COMB_MODE` for combined read/write flush behavior.
- `MMEA1_IO_GROUP_BURST` exposes read/write low/high burst limits for IO traffic.
- `MMEA1_IO_RD_PRI_*` and `MMEA1_IO_WR_PRI_*` define per-group aging rates, age coefficients, queuing coefficients, fixed coefficients, urgency coefficients/modes, 32-client urgency masks, and three sets of four 8-bit quantized-priority thresholds.
- `MMEA1_SDP_ARB_DRAM`, `MMEA1_SDP_ARB_GMI`, and `MMEA1_SDP_ARB_FINAL` define SDP burst-cycle/data limits, early read/write switch behavior, end-of-burst behavior, read/write bank-state decoupling, chain breaking, final DRAM/GMI/IO burst limits, readonly virtual-channel bits 0-7, and error/halt-on-error behavior.
- `MMEA1_SDP_DRAM_PRIORITY`, `MMEA1_SDP_GMI_PRIORITY`, and `MMEA1_SDP_IO_PRIORITY` assign 4-bit read/write priorities for groups 0-3 on DRAM, GMI, and IO paths.
- `MMEA1_SDP_CREDITS`, `MMEA1_SDP_TAG_RESERVE0/1`, `MMEA1_SDP_VCC_RESERVE0/1`, and `MMEA1_SDP_VCD_RESERVE0/1` describe tag, response, and per-VC credit reservation fields.
- `MMEA1_SDP_REQ_CNTL` covers outstanding read/write request thresholds, blocking controls, and deadlock timers.
- `MMEA1_MISC`, `MMEA1_MISC2`, and `MMEA1_MISC_AON` expose global arbiter behavior: DRAM/GMI/IO disable and reset indicators, clock-enable and soft-reset bits, command-buffer disable, client stall behavior, request blocking/throttling, response swap mode, and link-manager always-on controls.
- `MMEA1_LATENCY_SAMPLING`, `MMEA1_PERFCOUNTER_LO/HI`, `MMEA1_PERFCOUNTER0_CFG`, `MMEA1_PERFCOUNTER1_CFG`, and `MMEA1_PERFCOUNTER_RSLT_CNTL` define local sampling, performance counter selection/mode/enable/clear, and result selector/control fields.
- `MMEA1_UE_ERR_STATUS_LO/HI` and `MMEA1_CE_ERR_STATUS_LO/HI` provide RAS status-valid, address-valid, address, memory-id, ECC, error-info, count, and poison fields for uncorrectable and correctable errors.
- `MMEA1_DSM_CNTL`, `MMEA1_DSM_CNTLA/B`, `MMEA1_DSM_CNTL2`, and `MMEA1_DSM_CNTL2A/B` cover DSM and EDC error injection across DRAM read/write command, data, page memories; GMI read/write command, data, page memories; IO read/write command/data memories; return-tag memories; and MAM data memories.
- `MMEA2_DRAM_*` and `MMEA2_GMI_*` repeat the grouping, virtual-channel, lazy accumulation, CAM/reorder, burst, priority, urgency, urgency-mask, and quantized-threshold model for MMHUB engine instance 2 DRAM and GMI traffic.
- `MMEA2_IO_RD_CLI2GRP_MAP0/1`, `MMEA2_IO_WR_CLI2GRP_MAP0/1`, `MMEA2_IO_RD/WR_COMBINE_FLUSH`, `MMEA2_IO_GROUP_BURST`, and `MMEA2_IO_RD/WR_PRI_*` begin the IO-side fields for `MMEA2`. The chunk ends before all write urgency-mask bits are present.

The `addressBlock: aid_mmhub_ea_mmeadec2` marker appears at line 12770 and identifies the transition from `MMEA1` to the `MMEA2` decode block. The `MMEA1` address-block marker itself is earlier in the file, outside this chunk.

## Control Flow

There is no runtime control flow in this header. The flow is indirect:

1. `amdgpu/mmhub_v1_8.c` includes `mmhub/mmhub_1_8_0_offset.h` and this `mmhub/mmhub_1_8_0_sh_mask.h` file.
2. Normal MMHUB bring-up functions program VM/GART/aperture/TLB/cache/invalidation registers using generated offset and field macros from this header family.
3. The RAS path builds CE and UE register lists for `MMEA0` through `MMEA4`, including the `MMEA1_*_ERR_STATUS_*` and `MMEA2_*_ERR_STATUS_*` register offsets from the companion offset header. Generic RAS helpers then use status-valid, address-valid, memory-id, error-info, count, and poison field definitions from this mask header family when decoding and resetting errors.
4. Arbitration, DSM, latency, and performance-counter fields in this slice are available to driver diagnostics, firmware interaction, debug tooling, or future tuning paths that need to read or write MMEA registers without hard-coded bit arithmetic.

No branch, loop, or callback is implemented here; all sequencing and error handling live in the C consumers and in hardware/firmware programming policy.

## State And Persistence Behavior

The macros are compile-time constants and hold no software state. The registers they describe are persistent MMHUB hardware state until reset, suspend/resume reinitialization, GPU reset, firmware reprogramming, or an explicit driver write changes them.

Key hardware state represented by this chunk includes:

- Client-to-group and group-to-VC mappings, which determine how MMHUB clients are classified for DRAM, GMI, and IO arbitration.
- Scheduler behavior such as lazy accumulation delays/timeouts, CAM depths, reorder limits, burst caps, priority aging, urgency modes, and quantized-priority thresholds.
- Credit pools and per-VC reserves, which control how many tags or response credits can be consumed by traffic classes.
- Request blocking, throttling, clock-gating overrides, soft reset, and busy/reset status bits.
- Latency sampling and performance counter selector/enabler/result registers.
- RAS CE/UE status latches and DSM error-injection controls for command, data, tag, page, and MAM memories.

Because these are hardware registers rather than kernel-owned memory, persistence is tied to device power and reset domains. The header does not define locking, ordering, barriers, atomicity, or lifetime rules; callers must obey MMIO ordering and ASIC-specific programming sequences.

## Dependencies

This chunk depends on the generated MMHUB 1.8.0 register specification. It must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_offset.h`, which provides the matching `regMMEA1_*` and `regMMEA2_*` register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_8.c`, the primary local MMHUB v1.8 C consumer.
- AMDGPU register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `AMDGPU_RAS_REG_ENTRY`, `amdgpu_ras_inst_query_ras_error_count`, and `amdgpu_ras_inst_reset_ras_error_count`.
- MMHUB RAS memory identifiers, including names such as `AMDGPU_MMHUB_WGMI_PAGEMEM`, `AMDGPU_MMHUB_RDRAM_CMDMEM`, `AMDGPU_MMHUB_MAM_DMEM*`, `AMDGPU_MMHUB_WRET_TAGMEM`, and IO/GMI/DRAM command/data/page memory IDs.
- The generated SOC15 include structure and ASIC selection in `gmc_v9_0.c`, which wires MMHUB v1.8 functions and RAS support for matching hardware.

The naming pattern also depends on adjacent chunks. The source range begins after the `MMEA1_IO_RD_CLI2GRP_MAP1` mask family and ends before the final `MMEA2_IO_WR_PRI_URGENCY_MASKING` masks, so full per-file analysis must reconcile this document with chunks `subset-b-002778` and `subset-b-002780`.

## Integration Points

- MMHUB v1.8 initialization in `mmhub_v1_8_gart_enable()` configures core address-translation state, then enables the system domain, disables identity aperture, sets VMID configuration, and programs invalidation. This chunk is less about VM address fields and more about the MMEA arbitration/error-control field namespace that the same generated header family exposes.
- RAS integration in `mmhub_v1_8_ce_reg_list` and `mmhub_v1_8_ue_reg_list` includes `MMEA1` and `MMEA2` CE/UE error status registers. Generic RAS code uses those register pairs plus field definitions to query and reset per-instance error counts across `adev->aid_mask`.
- The `mmhub_v1_8_ras_memory_list` maps MMEA memory IDs to readable labels such as WGMI/RGMI/DRAM/IO command/data/page memories, MAM memories, and return-tag memories. Those labels line up directly with the CE/UE/DSM memory families exposed in this chunk.
- Performance diagnostics can use the `MMEA1_LATENCY_SAMPLING` and `MMEA1_PERFCOUNTER*` fields to select events, enable/clear counters, and read low/high result halves.
- Firmware, bring-up scripts, or future kernel tuning code can use the DRAM/GMI/IO client grouping, priority, urgency, burst, CAM, lazy, and SDP fields to adjust memory traffic arbitration without introducing raw bit constants.
- Error-injection and validation paths can use `MMEA1_DSM_CNTL*` together with `MMEA1_EDC_MODE` and `MMEA1_ERR_STATUS` to force, count, propagate, clear, or gate injected and real error conditions.

## Risks

- Generated-field drift is the central risk. A wrong shift or mask still compiles but causes `REG_SET_FIELD`/`REG_GET_FIELD` to write or decode the wrong bits in MMHUB registers.
- This chunk has split-family boundaries. Treating it as self-contained would miss `MMEA1_IO_RD_*` fields before line 11751 and the final `MMEA2_IO_WR_PRI_URGENCY_MASKING` bits after line 14067.
- Many fields are repeated across `MMEA0`-`MMEA4`, DRAM/GMI/IO paths, read/write directions, and groups 0-3. Copying a macro with the wrong engine instance, path, or direction can silently tune a different scheduler.
- Client grouping and group-to-VC mappings affect traffic routing and fairness. Bad values can starve clients, send traffic to an unintended virtual channel, or trigger backpressure.
- Lazy accumulation, CAM depth, reorder limits, burst caps, priority aging, urgency modes, quantization thresholds, and credit reservations are performance-sensitive. Incorrect tuning can cause latency spikes, throughput loss, head-of-line blocking, or hangs under high memory pressure.
- `MMEA1_MISC`, `MMEA1_MISC2`, request blocking, reset, clock-gating, and stall/override fields can disable paths or hold requests. Misuse can make the hub appear wedged even if VM programming is correct.
- RAS status fields must be decoded with the exact valid/address/memory-id/count/poison masks. Incorrect masks can undercount real errors, misattribute a memory block, or clear evidence before diagnostics collect it.
- DSM error-injection bits are hazardous in production. Accidentally enabling injection or bypass/gating modes can manufacture CE/UE events, poison traffic, or obscure genuine hardware faults.
- Cross-generation similarity is high. MMHUB 1.7, 1.8, and later generated headers use many similar names with different offsets or field layouts; mixing offset and mask headers from different generations is valid C but invalid hardware programming.

## Test Signals

- Build an AMDGPU configuration that includes `mmhub_v1_8.c` and the generated MMHUB 1.8.0 headers; this catches missing macro names but not semantic drift.
- Generated-header validation should compare every `MMEA1_*` and `MMEA2_*` field in this range against the authoritative MMHUB 1.8.0 register database, including field widths and split boundary completeness.
- Static checks should ensure every `regMMEA1_*`/`regMMEA2_*` error-status register used by `mmhub_v1_8.c` has matching `_STATUS_VALID_FLAG`, `_ADDRESS_VALID_FLAG`, `_ADDRESS`, `_MEMORY_ID`, `_ERR_INFO`, `_CE_CNT`, `_POISON`, or related masks in the mask header family.
- Runtime MMHUB v1.8 smoke should boot matching hardware, enable GART, run VMID/GPUVM workloads, suspend/resume, and reset without MMHUB faults or hung requests.
- RAS validation should inject or simulate CE/UE events for MMEA1 and MMEA2 memories, verify `amdgpu_ras_inst_query_ras_error_count()` reports the expected counts and memory IDs, and confirm reset clears the status latches.
- Performance-counter validation should program `MMEA1_PERFCOUNTER0_CFG`/`MMEA1_PERFCOUNTER1_CFG`, sample `MMEA1_PERFCOUNTER_LO/HI`, and verify clear/enable/result-control behavior against expected traffic.
- Arbitration tuning tests should stress DRAM, GMI, and IO traffic classes under concurrent GPUVM workloads and watch for fairness regressions, timeouts, RAS events, or request-blocked status after changing grouping, priority, urgency, burst, CAM, or credit fields.
