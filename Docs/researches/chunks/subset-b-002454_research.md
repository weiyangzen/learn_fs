# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 12433-14880

## Scope

This chunk is a middle segment of the generated AMD GC 10.1.0 shift/mask header. It covers line 12433 through line 14880 and defines 1,064 `__SHIFT` macros and 1,088 `_MASK` macros across 314 visible register groups. The range begins inside the `GCVM_CONTEXT2_CNTL` field list, continues through GCVM context, invalidation, page-table address, shared GCMC aperture/TLB, and GCEA memory-client arbitration/address-decode fields, and ends inside `GCEA_ADDRDEC1_ADDR_MASK_SECCS01` before the following `SECCS23` and later address-decode fields.

The content is declarative only. There are no C functions, structs, enums, branches, loops, allocations, locks, or software-side side effects. The exported surface is a set of preprocessor constants that describe bit positions and masks for GC 10.1.0 memory-mapped registers.

## Purpose

`gc_10_1_0_sh_mask.h` supplies symbolic bitfield definitions for AMDGPU and KFD code that targets Navi/GC 10.1.0 register layouts. Consumers pair these macros with offsets from `gc_10_1_0_offset.h` and use helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, and `RREG32_SOC15` to program GPU VM contexts, invalidate VM translation caches, configure system/frame-buffer apertures, and tune GC memory-client arbitration and physical DRAM address decode without embedding raw bit numbers in driver logic.

This slice focuses on three major hardware surfaces:

- GCVM per-VMID context state, including context enable, page-table depth/block size, retry behavior, and per-fault interrupt/default routing.
- GCVM invalidate engines, including per-engine semaphores, invalidate request fields, acknowledgement bits, and optional logical page address ranges.
- GCMC and GCEA address/aperture/memory-client controls, including NB MMIO/DRAM aperture registers, system aperture/default address fields, L1 TLB control, DRAM client-to-group mappings, priority/arbitration coefficients, normalized address ranges, DRAM holes, bank/hash/harvest controls, and chip-select address decode fields.

## Exported API Surface

There are no callable APIs or local types. The public interface is the generated macro namespace:

- `GCVM_CONTEXT2_CNTL` through `GCVM_CONTEXT15_CNTL`: repeated VM context-control fields for enabling contexts, selecting page-table geometry, configuring retry behavior, and selecting interrupt/default behavior for range, dummy-page, PDE0, valid, read, write, and execute protection faults.
- `GCVM_CONTEXTS_DISABLE`: one disable bit per context 0 through 15.
- `GCVM_INVALIDATE_ENG0_SEM` through `GCVM_INVALIDATE_ENG17_SEM`: single-bit semaphore fields for 18 invalidation engines.
- `GCVM_INVALIDATE_ENG0_REQ` through `GCVM_INVALIDATE_ENG17_REQ`: invalidate request fields for per-VMID invalidation, flush type, L2 PTE invalidation, PDE0/PDE1/PDE2 invalidation, L1 PTE invalidation, protection-fault status-address clearing, and 4K-page-only invalidation.
- `GCVM_INVALIDATE_ENG0_ACK` through `GCVM_INVALIDATE_ENG17_ACK`: per-VMID acknowledge fields for invalidation completion.
- `GCVM_INVALIDATE_ENG0_ADDR_RANGE_*` through `GCVM_INVALIDATE_ENG17_ADDR_RANGE_*`: low/high logical page address range fields, split into `S_BIT`, low 31 bits, and high 5 bits.
- `GCVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_*` through `GCVM_CONTEXT15_PAGE_TABLE_BASE_ADDR_*`: 64-bit page-directory-entry base addresses split into low/high 32-bit register fields.
- `GCVM_CONTEXT0_PAGE_TABLE_START_ADDR_*` and `GCVM_CONTEXT0_PAGE_TABLE_END_ADDR_*` through context 15: logical-page-number aperture start/end fields, split into low 32 bits and high 4 bits.
- `GCMC_VM_*`: shared PF/VC decoder fields for MMIO base/limit, PCI control/arbitration, DRAM top, frame-buffer offset/location, system aperture default/low/high address, steering, reset request, memory power, cacheable DRAM ranges, APT control, local HBM address lock/range, and `GCMC_VM_MX_L1_TLB_CNTL`.
- `GCEA_DRAM_*`: DRAM read/write client mapping, group-to-VC mapping, lazy timing, CAM depth/reorder controls, page-burst limits, aging/queueing/fixed/urgency coefficients, and quantum-priority thresholds.
- `GCEA_ADDRNORM*` and `GCEA_ADDRDEC*`: normalized address base/limit/offset, DRAM hole, NP2 channel space, bank and misc masks, DRAM hash/harvest fields, and address-decode base/mask/config/selection registers for chip-select and secondary chip-select groups.

Most complete register groups follow the generated pair pattern `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. This chunk has intentional boundary exceptions: it begins after the `GCVM_CONTEXT2_CNTL` comment and ends before the complete `GCEA_ADDRDEC1_ADDR_MASK_SECCS01`/later address-decode sequence.

## Control Flow And State Behavior

This header has no local control flow. Runtime behavior appears only when driver code includes the generated constants and uses them in MMIO read-modify-write or direct write sequences.

The field names describe several hardware-controlled state machines and persistent register banks:

- VM context programming: each VMID context holds a page-table root, start/end logical-page range, enable bit, page-walk depth, page-table block size, and fault handling policy. The corresponding hardware state persists until reset, power-domain loss, driver reprogramming, or firmware/golden-register restore.
- Fault handling: context-control fields select whether range, dummy-page, PDE0, valid, read, write, and execute faults interrupt the driver or resolve through a default path. Retry fields interact with XNACK/no-retry behavior exposed through KFD per-process state.
- Translation invalidation: invalidate engines use semaphore, request, acknowledge, and optional range registers. Software composes a request word, writes the appropriate engine request register, and waits for the matching acknowledgement path outside this header.
- Aperture and TLB configuration: GCMC registers define frame-buffer, AGP, system aperture, default page address, cacheable DRAM windows, local HBM windows, and L1 TLB behavior. These are global memory-controller state, not per-process data.
- GCEA arbitration and address decode: DRAM read/write client maps, VC maps, priority coefficients, CAM limits, and address-normalization/decode/hash settings shape how GC memory traffic is routed and scheduled. These settings are hardware configuration state and may be established by firmware, BIOS, golden-register tables, or early driver init depending on ASIC mode.

Readback/status semantics are not encoded by the macro names alone. Fields named `ACK`, `STATUS`, or `*_OUT` are likely readback-oriented by naming convention, while `REQ`, `CNTL`, `BASE`, `LIMIT`, `MASK`, `CFG`, and priority fields are configuration-oriented. Actual read-only, write-only, sticky, clear-on-read, and reset semantics must come from the register database and calling driver code.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. Semantically, these macros are tied to the matching GC 10.1.0 register offsets in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h` and defaults in `gc_10_1_0_default.h`.

Important integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_0.c`, which includes this header and uses the GCVM invalidation, context-control, page-table base/start/end, GCMC frame-buffer/system aperture, and TLB fields during GFXHUB VM setup. It also derives `ctx_distance`, `ctx_addr_distance`, `eng_distance`, and `eng_addr_distance` from adjacent offsets and builds a VM fault interrupt mask from `GCVM_CONTEXT1_CNTL` masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v12_1.c` and related KFD queue-manager files, which use context retry bits together with per-process XNACK/retry policy.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0.c` and `imu_v11_0_3.c`, whose IMU/RLC golden-register tables include `GCVM_CONTEXT*_CNTL` and `GCEA_DRAM_PAGE_BURST` programming values.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c`, KFD packet/MQD management, and other GC 10.x code that includes the same generated namespace for graphics and compute queue bring-up.

At runtime the macros feed AMDGPU's register helper layer, VM hub initialization, GART aperture setup, system aperture setup, VMID context configuration, TLB/cache invalidation, suspend/resume restore, SR-IOV PF/VF split handling, and hardware fault reporting.

## Risks

- Generated-header drift is the primary risk. A wrong shift or mask can silently program the wrong VM context bit, fault policy, invalidation request field, aperture field, or DRAM address-decode bit.
- The VM context groups are highly repetitive. Driver code often programs context 1 and then walks adjacent contexts by offset distance; inconsistent context register spacing or a wrong context-specific macro can produce VMID-dependent faults.
- Invalidation request construction is sensitive to bit placement. Missing `INVALIDATE_L1_PTES`, `INVALIDATE_L2_PTES`, PDE bits, or using an incorrect `PER_VMID_INVALIDATE_REQ` mask can leave stale translations after page-table updates.
- Retry/no-retry behavior affects fault storms and process-visible XNACK behavior. Incorrect `RETRY_PERMISSION_OR_INVALID_PAGE_FAULT` handling can break KFD process isolation, recoverability, or performance.
- Page-table base/start/end fields are split across registers. Bad high/low masking or shifting can expose the wrong virtual address range or page-table root.
- GCMC aperture and default-address registers affect global memory routing. Incorrect frame-buffer, AGP, system aperture, or dummy/default page programming can convert invalid GPU accesses into host-memory corruption, unexpected VRAM access, or unrecoverable faults.
- GCEA DRAM arbitration and address-decode fields are low-level memory-controller configuration. Mistakes in bank, chip-select, row/column, hash, harvest, or priority fields may only reproduce as performance loss, ECC/RAS-like symptoms, data corruption, or ASIC-specific boot failures.
- Some registers are likely firmware- or PF-owned in SR-IOV and power-management modes. Blind writes from a VF or late driver path can conflict with PF/firmware ownership.
- This slice starts and ends at chunk boundaries inside register groups, so merge-time validation should not treat missing comments or trailing pairs at the boundaries as local omissions.

## Test Signals

Useful validation is mostly build-time, generated-data, and hardware-integration oriented:

- Compile or preprocess AMDGPU/KFD code paths that include `gc_10_1_0_offset.h`, `gc_10_1_0_sh_mask.h`, and `gc_10_1_0_default.h`.
- Static generation checks that complete register groups in the full header have matching `__SHIFT` and `_MASK` definitions, with explicit chunk-boundary exceptions for the start at `GCVM_CONTEXT2_CNTL` and the end at `GCEA_ADDRDEC1_ADDR_MASK_SECCS01`.
- Cross-check this chunk against the GC 10.1.0 register database and matching offset/default headers for register name alignment and field width consistency.
- VM bring-up tests on GC 10.1.0-class hardware: GART setup, VMID context programming, user queue creation, page-table root updates, VM fault interrupt/default routing, and per-process XNACK/no-retry behavior.
- Translation invalidation tests: update PTEs/PDEs, issue VMID and range invalidations, verify acknowledge completion, and check that stale translations do not survive context switches or queue submissions.
- Suspend/resume, GPU reset, SR-IOV VF/PF, and firmware restore tests that confirm GCVM/GCMC/GCEA state is either restored by the driver or intentionally owned by firmware/PF.
- Fault-injection and diagnostics: trigger read/write/execute/valid/PDE faults and confirm fault reporting, default-page routing, fault-status clearing, and retry behavior match the expected policy.
- Memory-controller validation: bandwidth and latency tests across read/write clients, page-burst and priority settings, VRAM/HBM aperture boundaries, and address-decode/hash/harvest configurations on affected ASIC revisions.

## Chunk Notes For Merge

This document is intentionally source-tree aligned and covers only lines 12433-14880 of `gc_10_1_0_sh_mask.h`. Earlier chunks should cover the beginning of `GCVM_CONTEXT2_CNTL` and prior GCVM/L2 fields. Later chunks should continue `GCEA_ADDRDEC1_ADDR_MASK_SECCS01`, the remaining address-decode fields, and subsequent GC register groups. The final per-file report should treat the whole file as a generated GC 10.1.0 register bitfield map used by AMDGPU and KFD hardware programming paths, not as handwritten executable logic.
