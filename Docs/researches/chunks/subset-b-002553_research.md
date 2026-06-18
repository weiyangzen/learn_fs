# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 9765-12372

## Scope

This chunk is a generated AMD GC 11.5.0 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is represented by a `__SHIFT` value and a matching `__MASK` value used by AMDGPU register helpers to compose or decode 32-bit MMIO/indexed-register values. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected lines start in the middle of the GCVM invalidation-engine address-range family, with the `GCVM_INVALIDATE_ENG7_ADDR_RANGE_LO32` masks visible before the matching `HI32` comment. The chunk then covers GCVM page-table base/start/end address fields for contexts 0 through 15, GCVM L2 per-PF/VF PTE cache fragment sizing, GCVM/GCMC/GCUTCL2/ATC/GCL2TLB performance counters and selector/control registers, GCVM ATS/IOMMU/translation-fault controls, shader-stage register fields for PS/GS/HS/ES/LS, compute dispatch and compute resource registers, and the beginning of CP command-processor public/decode fields. The slice ends after `CP_ECC_FIRSTOCCURRENCE__VMID_MASK`; the obsolete ring-specific ECC first-occurrence macros and following GB EDC fields continue in the next adjacent chunk.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for the GC 11.5.0 graphics IP and is not Ceph filesystem code.

## Purpose

`gc_11_5_0_sh_mask.h` supplies the bit layouts for GC 11.5.0 registers. Driver code pairs these macros with register addresses from the matching `gc_11_5_0_offset.h` header and, where available, generated reset/default values. Consumers normally use the constants through helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` so register fields can be packed or extracted without hard-coded bit positions.

This chunk focuses on virtual memory programming, shader/compute launch state, and CP queue/interrupt controls:

- GCVM invalidation range fields for engines 7 through 17, with split low/high logical page-address fields and an `S_BIT` flag in each low word.
- Per-context GCVM page-table base, start, and end address fields for contexts 0 through 15, plus per-PF/VF PTE cache fragment-size knobs.
- L2/ATC/TLB performance counter result, selection, mode, and configuration registers for GCVM, GCMC VM L2, GCUTCL2, GC ATC L2, and GCL2TLB blocks.
- ATS, IOMMU host-translation enable/control/optimization, translation fault control, GPUVA VMID translation assist, and UTCL2 translation-bypass controls.
- Shader program address/resource/checksum/user-data/request-control/accumulator fields for pixel shader, geometry shader, hull shader, and related ES/LS pairing registers.
- Compute dispatch dimensions, start/restart coordinates, thread counts, pipeline/perf enable, program addresses/resources, VMID, destination/static-thread controls, temporary ring sizing, wave relaunch/restore, dispatch tunnel/end, and user data.
- CP command-processor queue, doorbell, priority, VMID, interrupt, UTCL1, virtualization, ring pointer, power, fatal/error, and ECC first-occurrence fields.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Register-address symbols live in the companion offset header, commonly with `mm...` names matching these register names.
- AMDGPU callers normally access these fields through `REG_SET_FIELD`, `REG_GET_FIELD`, read-modify-write MMIO helpers, command-packet register programming, debugfs/perf tooling, reset paths, virtualization handling, and shader/compute queue setup.

The main macro families in this slice are:

- `GCVM_INVALIDATE_ENG7..17_ADDR_RANGE_{LO32,HI32}`: page-range invalidation address encodings. Low words expose `S_BIT` and low logical page address bits; high words expose the high logical page address bits.
- `GCVM_CONTEXT0..15_PAGE_TABLE_{BASE,START,END}_ADDR_{LO32,HI32}`: per-VMID/context page-table directory base and valid logical page-number bounds. Base addresses use full low/high PDE fields; start/end high words use four high logical page-number bits.
- `GCVM_L2*_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES`: base and per-context L2 PTE cache fragment-size fields for system and local memory fragment sizes.
- `GCVML2_PERFCOUNTER2_*`, `GCMC_VM_L2_PERFCOUNTER*`, `GCUTCL2_PERFCOUNTER*`, `GC_ATC_L2_PERFCOUNTER*`, and `GCL2TLB_PERFCOUNTER*`: performance counter low/high results, event selectors, selector extensions, mode controls, per-counter configs, result selection, clear, and enable controls.
- `GCVM_PCIE_ATS_CNTL`, `GCUTCL2_TRANSLATION_BYPASS_BY_VMID`, `GCVM_IOMMU_*`, `GCUTC_TRANSLATION_FAULT_CNTL*`, and `GCUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL`: translation and IOMMU controls for ATS, host translation enablement, optimization, fault-response behavior, VMID bypass masks, and GPU virtual-address assist behavior.
- `SPI_SHADER_*`: shader stage program registers for PS, GS, and HS plus ES/GS and LS/HS pair addresses. Resource fields include VGPR/SGPR counts, priority, float mode, DX10 clamp, debug mode, scratch enable, user SGPR counts, trap/debug flags, LDS sizing, CU enable, wave limit, and stage-specific controls such as meshlet dimensions.
- `COMPUTE_*`: compute dispatch state. These macros cover dispatch dimensions and starts, threadgroup sizes, program address and resource descriptors, VMID, resource limits, per-SE destination/static-thread controls through SE7, temporary ring size, relaunch controls, wave restore address, dispatch packet/scratch addresses, DDID, shader checksum, tunnel/end markers, and 16 user-data registers.
- `CP_*`, `CPG_*`, `CPC_*`, and `CPF_*`: command-processor public/decode controls for CU masks, EOP wait timing, MGCG sync, interrupt metadata, virtualization status, UTCL1 controls/errors, AQL status, ring-buffer bases/control/read/write pointers, doorbell ranges, priorities, VMIDs, process quantum, fatal/GFX error attribution, interrupt enable/status for generic and ring-specific paths, power clock-halt bits, and ECC first-occurrence attribution.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU consumers:

1. Select the GC 11.5.0 register header for the active ASIC generation.
2. Choose the matching register address from `gc_11_5_0_offset.h`.
3. Read an existing register value, prepare an indexed-register/debug/perf access, or construct an MMIO/command-packet register write.
4. Use the `__SHIFT`/`__MASK` pairs, usually through generated register helpers, to pack a field value or extract status bits.
5. Feed the resulting value into VM setup, TLB invalidation, IOMMU/ATS programming, shader or compute pipeline setup, CP ring setup, interrupt handling, virtualization, perf counter programming, hang diagnostics, reset, or power-management logic.

For GCVM context registers, driver VM setup programs page-table base and address bounds before GPU work uses a VMID, and invalidation code writes address-range fields before triggering per-engine TLB/cache invalidation. For performance counters, consumers select events and modes, configure counter routing, clear/enable accumulation, then read low/high result words. Shader and compute register flows are usually populated by command-stream packets or queue setup paths immediately before dispatch/draw work. CP register flows initialize rings and doorbells, update pointers, program priority/VMID/quantum state, enable interrupts, and inspect status/error/ECC state during interrupt, debug, or recovery handling.

This header does not encode ordering requirements, polling loops, latching sequences, clear-on-read behavior, or reset sequencing; those rules live in AMDGPU engine code, firmware interfaces, and hardware programming guides.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe GPU register fields whose state is owned by hardware, firmware, and AMDGPU runtime programming.

GCVM context page-table base/start/end registers are persistent VM context state until explicitly reprogrammed, evicted, reset, or lost through power transitions. Incorrect field packing can point a VMID at the wrong page directory or expose the wrong logical address range, causing memory faults, data corruption, or isolation failures. Invalidation address-range registers are transient control state used around TLB/cache invalidation operations, but stale or mispacked ranges can leave translations cached when callers expect them to be invalidated.

ATS/IOMMU/translation-fault controls affect memory translation and fault behavior globally or per VMID. Bypass masks and host-translation enable bits are high risk because they can change which transactions use GPU page tables, IOMMU translation, or fault-assist paths. Translation-fault controls may be sticky or policy-like hardware state; callers must preserve reserved bits and follow documented clear/acknowledge sequences outside this header.

Shader and compute registers are active pipeline/dispatch state. Program address, resource, user-data, scratch, temporary-ring, wave-restore, relaunch, and static-thread-management fields can remain live across dispatches, preemption, suspend/resume, or debug capture until overwritten by the command processor or reset. Bad masks in these fields can launch the wrong shader address, allocate invalid VGPR/SGPR/LDS resources, assign work to the wrong shader engines, or corrupt wave relaunch/restore.

CP ring and doorbell fields persist as queue execution state. Ring base/control, read/write pointer addresses and values, buffer-size masks, VMID/priority/quantum, doorbell ranges, interrupt enables, and UTCL1 controls must match the queue and process being scheduled. Error, fatal, interrupt-status, GFX-error, and ECC first-occurrence registers are live or sticky diagnostic state and may require hardware-defined clearing. `CP_PWR_CNTL` clock-halt fields have direct power/clock side effects and should not be treated as passive status bits.

Performance counter selector/configuration registers persist while counters accumulate. Low/high result registers may require a hardware-specific snapshot or read ordering to avoid torn values; the shift/mask header only describes bit positions and cannot express atomicity, overflow, or latching behavior.

Reserved and obsolete fields appear in this generated area. Callers should preserve reserved bits during read-modify-write unless a documented full-register write is required, especially around VM/IOMMU, shader resource, CP power, and error/interrupt registers.

## Dependencies And Integration Points

This chunk depends on the generated GC 11.5.0 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h` provides matching register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_default.h`, when present in the same generated register family, provides default/reset values for many registers.
- Common AMDGPU register helpers provide field packing/extraction and MMIO or command-packet access mechanisms.
- AMDGPU VM, GFX, CP, KFD/compute, shader setup, performance counter, reset, suspend/resume, SR-IOV/virtualization, debugfs, and hang-dump paths rely on these bit assignments.

Integration points include VMID/page-table setup, range-based GCVM invalidation, ATS/IOMMU enablement and translation-fault policy, per-VMID bypass/assist handling, graphics pipeline shader register programming, compute queue and dispatch packet setup, wave relaunch after preemption or recovery, CP ring creation and teardown, doorbell mapping, interrupt enable/status handling, priority/quantum scheduling, UTCL1 error handling, virtualization status/fault attribution, power/clock control, performance monitoring, and ECC/fatal-error diagnostics.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but can write the wrong hardware bits or decode misleading diagnostics.
- This chunk starts and ends mid-family. It begins after the `GCVM_INVALIDATE_ENG7_ADDR_RANGE_LO32` comment and ends before the ring-specific `CP_ECC_FIRSTOCCURRENCE_*` and following GB EDC fields; file-level conclusions must be merged with adjacent chunks.
- Context macros are repeated across VM contexts 0 through 15. Generator mistakes can affect only one context, producing VMID-specific faults that are difficult to diagnose.
- Split address fields are easy to misuse. Page-table, invalidation, shader program, dispatch-packet, scratch, read-pointer, CU-mask, and wave-restore addresses must be shifted/aligned according to their field definitions, not treated as always-full byte addresses.
- GCVM/IOMMU/ATS/bypass controls affect memory isolation and fault behavior. Incorrect masks can hide faults, bypass translation unexpectedly, or attribute translation failures to the wrong VMID.
- Shader and compute resource fields are densely packed. Incorrect widths for VGPR/SGPR counts, LDS size, scratch enable, CU enables, wave limits, or thread dimensions can cause invalid dispatches, hangs, or silent performance/debug errors.
- CP ring/doorbell/pointer fields are queue-critical. Bad buffer-size masks, pointer address fields, doorbell ranges, VMIDs, priorities, or quantum fields can cause lost work, wrong-process execution, stalled queues, or interrupt storms.
- Interrupt enable/status families are similar but not identical between generic CP and ring0/ring1 variants. Assuming symmetry can miss ring-specific fields or enable unsupported bits.
- `CP_PWR_CNTL`, fatal/error, virtualization, and UTCL1 controls have side effects or sticky state. Full-register writes that do not preserve reserved bits may change undocumented engine behavior.
- Counter result high/low registers can be race-prone if read without the documented latching sequence. This header cannot describe atomic snapshot requirements.

## Test Signals

Useful validation is primarily generated-data consistency, build coverage, and hardware/runtime diagnostics:

- Kernel build coverage for AMDGPU files that include `gc_11_5_0_sh_mask.h`, especially GC 11.5.0 VM, GFX, CP, KFD/compute, reset, virtualization, debug, and perf counter paths.
- Mechanical comparison against AMD's authoritative GC 11.5.0 register database to confirm every `__SHIFT` and `__MASK` value in this slice.
- Cross-checks that all registers in this chunk have matching address macros in `gc_11_5_0_offset.h` and expected defaults in the matching default header where generated.
- Static mask/shift sanity checks: masks should align with shifts, full-width data fields should use `0xFFFFFFFFL`, repeated context and user-data families should remain structurally aligned, and bitmap fields should not overlap unless documented.
- VM tests that create multiple VMIDs, program page-table base/start/end bounds, run range invalidations through engines 7 through 17, and verify no stale translations remain after mapping changes.
- IOMMU/ATS/fault tests that exercise host translation enablement, bypass-by-VMID, GPUVA VMID assist, and translation fault control paths with expected VMID and fault attribution.
- Graphics and compute dispatch tests that validate shader program/resource/user-data setup, compute thread dimensions, scratch/temporary ring programming, static-thread-management fields, and wave relaunch/restore after preemption or reset.
- CP ring tests covering ring base/control programming, read/write pointers, write-pointer high words, buffer-size masks, doorbell ranges, priorities, VMIDs, process quantum, and interrupt enable/status behavior for generic, ring0, and ring1 paths.
- Perf counter tests that select GCVM/GCMC/GCUTCL2/ATC/GCL2TLB events, clear/enable counters, read low/high results, and compare monotonicity or expected activity under controlled memory and dispatch workloads.
- Hang/debug dump tests that verify CP GFX/fatal error attribution, UTCL1 errors, virtualization status, interrupt metadata, power/clock-halt state, and ECC first-occurrence fields decode coherently.
- Runtime warning signals include VM faults after valid mappings, stale translations after invalidation, shader launch failures, compute hangs, invalid wave restore, lost doorbell updates, incorrect CP interrupts, misleading perf counters, unexpected UTCL/IOMMU faults, wrong VF/VMID attribution, and GPU reset loops.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002553`. It covers lines 9765-12372 of `gc_11_5_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the partial GCVM invalidation and CP ECC/GB EDC families and to place these GCVM, shader/compute, and CP definitions in the full GC 11.5.0 register map.
