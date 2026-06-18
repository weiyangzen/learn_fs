# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 12289-14934

## Purpose

This chunk is generated AMD GC 11.0.0 register bitfield metadata. It has no executable C control logic; it publishes preprocessor `__SHIFT` and `_MASK` constants used by AMDGPU, AMDKFD, MES, SDMA, display, GFXHUB, and SOC21 code to compose and decode 32-bit MMIO register values. The companion offset and base-index definitions live in `gc_11_0_0_offset.h`.

The selected range covers GCVM invalidate engines and VM context address registers, GCVM L2/UTC performance counter controls, SR-IOV/MARC virtualization address controls, shader-program resource registers for pixel/geometry/hull/local shader stages, and the front half of compute dispatch state. Although the subtree is under `ceph-client`, this header is AMD graphics hardware metadata, not distributed-filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, allocations, locks, callbacks, or direct MMIO helpers in this range. The exposed interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit for a field inside a 32-bit hardware register.
- `<REGISTER>__<FIELD>_MASK` gives the corresponding in-register bit mask.
- Consumers pair these masks with `reg<REGISTER>` and `reg<REGISTER>_BASE_IDX` symbols from `gc_11_0_0_offset.h`, then use AMDGPU helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15_OFFSET`, `REG_SET_FIELD`, and `REG_GET_FIELD`.

Major register families in this chunk:

- `GCVM_INVALIDATE_ENG10_REQ` through `GCVM_INVALIDATE_ENG17_REQ` complete the per-engine GCVM invalidate request set that started in an earlier chunk. Each request has a 16-bit `PER_VMID_INVALIDATE_REQ`, `FLUSH_TYPE`, invalidation selects for L2 PTEs/PDE0/PDE1/PDE2 and L1 PTEs, plus `CLEAR_PROTECTION_FAULT_STATUS_ADDR`, `LOG_REQUEST`, and `INVALIDATE_4K_PAGES_ONLY`.
- `GCVM_INVALIDATE_ENG0_ACK` through `GCVM_INVALIDATE_ENG17_ACK` define per-VMID acknowledgement and semaphore bits for invalidate engines 0-17.
- `GCVM_INVALIDATE_ENG0_ADDR_RANGE_LO32/HI32` through engine 17 provide invalidation address-range low/high masks. Low halves use bit 12 alignment (`0xFFFFF000L`), while high halves expose a 24-bit high address field.
- `GCVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_*` through `GCVM_CONTEXT15_PAGE_TABLE_BASE_ADDR_*`, then matching `START_ADDR_*` and `END_ADDR_*`, define per-VMID page-table base and virtual address aperture registers. Low halves are aligned from bit 12; high halves expose the upper physical or virtual address bits.
- `GCVM_L2_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` and `GCVM_L2_CONTEXT0` through `CONTEXT15` variants define small-page and big-page PTE cache fragment sizes plus bank selection.
- `GCVML2_PERFCOUNTER2_*`, `GCMC_VM_L2_PERFCOUNTER_*`, `GCUTCL2_PERFCOUNTER_*`, `GCVML2_PERFCOUNTER2_*_SELECT/SELECT1/MODE`, `GCMC_VM_L2_PERFCOUNTER0-7_CFG`, and `GCUTCL2_PERFCOUNTER0-3_CFG` expose GCVM L2 and UTC L2 performance counter result, select, mode, enable, clear, trigger, and saturate controls.
- `GCMC_VM_FB_SIZE_OFFSET_VF0` through `VF15` define per-virtual-function framebuffer size and offset fields for SR-IOV style partitioning.
- `GCUTCL2_TRANSLATION_BYPASS_BY_VMID` and `GCUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL` define VMID translation-bypass/GPA-mode masks and a translation-assist enable bit.
- `GCMC_VM_MARC_BASE_*`, `GCMC_VM_MARC_RELOC_*`, `GCMC_VM_MARC_LEN_*`, and `GCMC_VM_MARC_PFVF_MAPPING_0-15` define 16 MARC windows with base, relocation, length, enable, readonly, and PF/VF mapping fields. Low base/reloc/length fields are page-aligned from bit 12; high fields use 20-bit masks.
- `GCUTC_TRANSLATION_FAULT_CNTL0/1` defines the default physical page address and IO/SPA/SNOOP attributes used for translation-fault fallback behavior.
- `SPI_SHADER_PGM_RSRC4_PS`, `SPI_SHADER_PGM_CHKSUM_PS`, `SPI_SHADER_PGM_RSRC3_PS`, `SPI_SHADER_PGM_LO/HI_PS`, `SPI_SHADER_PGM_RSRC1_PS`, `SPI_SHADER_PGM_RSRC2_PS`, `SPI_SHADER_USER_DATA_PS_0-31`, `SPI_SHADER_REQ_CTRL_PS`, and `SPI_SHADER_USER_ACCUM_PS_0-3` define pixel shader program base, resource sizing, CU enablement, trap/checksum/image flags, user SGPR payloads, request throttling, and accumulator contribution fields.
- Geometry/tessellation shader families mirror the same pattern: `SPI_SHADER_PGM_*_GS`, `SPI_SHADER_USER_DATA_GS_0-31`, `SPI_SHADER_GS_MESHLET_DIM`, `SPI_SHADER_GS_MESHLET_EXP_ALLOC`, `SPI_SHADER_REQ_CTRL_ESGS`, `SPI_SHADER_USER_ACCUM_ESGS_*`, `SPI_SHADER_PGM_*_ES`, `SPI_SHADER_PGM_*_HS`, `SPI_SHADER_USER_DATA_HS_0-31`, `SPI_SHADER_REQ_CTRL_LSHS`, `SPI_SHADER_USER_ACCUM_LSHS_*`, and `SPI_SHADER_PGM_LO/HI_LS`.
- `COMPUTE_DISPATCH_INITIATOR` starts the compute dispatch register set with shader enable, partial-threadgroup, ordering, cache invalidation, tunnel, restore, wave32, AMP shader, and preemption-disable fields.
- `COMPUTE_DIM_*`, `COMPUTE_START_*`, and `COMPUTE_NUM_THREAD_*` describe grid dimensions, starting coordinates, and full/partial thread counts per X/Y/Z dimension.
- `COMPUTE_PGM_LO/HI`, `COMPUTE_DISPATCH_PKT_ADDR_*`, `COMPUTE_DISPATCH_SCRATCH_BASE_*`, `COMPUTE_PGM_RSRC1/2/3`, `COMPUTE_VMID`, `COMPUTE_RESOURCE_LIMITS`, `COMPUTE_DESTINATION_EN_SE0-3`, `COMPUTE_STATIC_THREAD_MGMT_SE0-7`, `COMPUTE_TMPRING_SIZE`, `COMPUTE_REQ_CTRL`, `COMPUTE_RELAUNCH*`, `COMPUTE_WAVE_RESTORE_ADDR_*`, `COMPUTE_USER_DATA_0-15`, `COMPUTE_DISPATCH_TUNNEL`, `COMPUTE_DISPATCH_END`, and `COMPUTE_NOWHERE` define compute shader program address/resources, dispatch packet and scratch pointers, VMID, occupancy limits, CU masks, thread-management masks, temporary-ring sizing, request throttling, relaunch/restore payloads, user data, and dispatch termination/data sink registers.

The chunk has 2,646 source lines, 2,070 `#define` lines, 1,033 shift macros, 1,037 mask macros, and 562 register/comment sections.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by driver code and the hardware blocks:

1. GC 11 code includes `gc_11_0_0_offset.h` and `gc_11_0_0_sh_mask.h`.
2. The driver selects a register using a `reg*` offset and base-index macro from the offset header.
3. It composes or extracts register fields with the shift/mask macros in this header, commonly through `REG_SET_FIELD` or `REG_GET_FIELD`.
4. SOC15 MMIO helpers perform the actual read or write, while the GFXHUB VM walker, GCVM L2/UTCL2, shader front-end, compute scheduler, firmware/MES, KFD queue management, and GPU hardware define the ordering and side effects.

The chunk describes fields needed for TLB/cache invalidation request/ack handling, VM context programming, per-PF/VF virtualization windows, performance counter configuration, shader program state, and compute dispatch setup. It does not encode the sequencing for VM context updates, invalidate polling, shader upload, command submission, ring scheduling, memory barriers, reset handling, or preemption.

## State And Persistence Behavior

This file stores no software state and persists nothing. It describes hardware state in GC 11 registers.

The represented state includes invalidate-engine request bits and acknowledgements, invalidate address ranges, per-context page-table bases and virtual apertures, PTE cache fragment sizing, GCVM/UTCL2 performance counter selectors/results, virtual-function framebuffer partitioning, translation bypass/assist controls, MARC remap windows and PF/VF visibility, translation fault defaults, shader code base addresses, shader resource declarations, user data registers, shader request scheduling controls, compute grid dimensions, dispatch packet/scratch/program pointers, compute VMID, occupancy/CU routing controls, temporary ring sizing, restart/relaunch/restore data, and dispatch-end payloads.

Persistence is hardware-defined. Some fields are durable configuration until reset or power-gating, such as page-table bases, VM apertures, MARC windows, shader resource registers, and compute resource limits. Some fields are live hardware-owned status or counter values, such as invalidate acknowledgements and performance counter results. Some bits act like action requests or clears, such as invalidate requests, `CLEAR`, `CLEAR_ALL`, relaunch events, fault-status clear, or log/capture style bits. The masks do not state read-only, write-only, sticky, self-clearing, write-one-to-clear, or reserved-bit semantics; consumers must follow the GC 11 programming guide and preserve unrelated fields during read-modify-write operations.

## Dependencies And Integration Points

The direct generated companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h`. Representative matching offsets include `regGCVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32`, `regGCMC_VM_MARC_BASE_LO_0`, `regSPI_SHADER_PGM_RSRC4_PS`, and `regCOMPUTE_DISPATCH_INITIATOR`.

Observed include sites in this tree include `amdgpu/gfx_v11_0.c`, `amdgpu/gfxhub_v3_0.c`, `amdgpu/mes_v11_0.c`, `amdgpu/sdma_v6_0.c`, `amdgpu/imu_v11_0.c`, `amdgpu/soc21.c`, `amdgpu/amdgpu_amdkfd_gfx_v11.c`, `amdkfd/kfd_device_queue_manager_v11.c`, `amdkfd/kfd_mqd_manager_v11.c`, `display/amdgpu_dm/amdgpu_dm_plane.c`, and `amdgpu/amdgpu_display.c`. That inclusion pattern matches the register families in this chunk: GFXHUB VM management, queue/MQD and MES dispatch state, shader setup, reset/firmware support, display/GFX integration, and SDMA/SOC-level register access.

Important integration points are VMID/context initialization, page table base/start/end programming, TLB invalidation and ACK polling, page-fault/default-address setup, SR-IOV PF/VF framebuffer/MARC isolation, GCVM performance telemetry, shader program resource setup for graphics pipelines, KFD/MES compute queue state, command processor dispatch packets, scratch memory programming, preemption/relaunch/restore, thread trace/debug controls, and GPU reset/suspend/resume flows that must restore hardware state.

## Risks And Edge Cases

- Header/offset mismatch is the primary correctness risk. Pairing `gc_11_0_0_sh_mask.h` with a different GC revision's offset header can compile while addressing the wrong bits.
- The range starts at the tail of `GCVM_INVALIDATE_ENG9_REQ` and ends after `COMPUTE_NOWHERE`; adjacent chunks are required for complete first-family context and for later registers in the same generated header.
- The macros are untyped constants. Accidentally mixing `GCVM_CONTEXTn`, `GCMC_VM_MARC_*_n`, shader-stage suffixes (`PS`, `GS`, `HS`, `LSHS`, `ESGS`), or compute resource registers can silently program the wrong VMID, VF window, shader stage, or dispatch resource.
- Address fields are alignment-sensitive. Many low halves begin at bit 12 or expose only high bits, so consumers must shift and mask page-aligned GPU addresses correctly.
- Invalidate request/ack sequencing is concurrency-sensitive. Drivers must avoid losing requests, must poll the correct engine/VMID ACK bits, and must handle timeouts or protection-fault clear/log bits without racing other VM work.
- VM context and MARC fields are security-sensitive. Incorrect PF/VF mapping, translation bypass, GPA mode, readonly, default fault address, or aperture limits can break isolation or route memory accesses unexpectedly.
- Performance counter fields include enables, clears, trigger controls, compare modes, and saturate behavior. Writing a full-width mask as a literal value can clear or stop counters instead of only selecting events.
- Shader program resource fields encode ABI-sensitive compiler and pipeline metadata: VGPR/SGPR counts, scratch, LDS, user SGPR counts, trap presence, exception enables, FP mode, WGP mode, CU enablement, meshlet dimensions, and image operation flags. Wrong values can cause shader hangs, invalid waves, memory faults, or bad rendering.
- Compute dispatch fields combine hardware-owned state and software-programmed state. VMID, scratch/program addresses, thread counts, CU masks, relaunch payloads, and wave restore addresses must match queue/MQD state and command processor expectations.
- Full-width `0xFFFFFFFFL` data masks do not imply safe blind writes. Many are addresses, user data, counters, checksums, or payload registers whose interpretation depends on stage, queue, firmware, or dispatch context.
- Reserved fields and stage-specific aliases should be preserved unless the relevant ASIC documentation explicitly requires a value.

## Test Signals

Useful validation is primarily build coverage, generated-header consistency, and hardware/driver smoke testing:

- Build AMDGPU, AMDKFD, MES, display, SDMA, GFXHUB, and SOC21 code that includes `gc_11_0_0_sh_mask.h` with `gc_11_0_0_offset.h`.
- Generated-header checks that every field's `__SHIFT` has a matching `_MASK`, masks align to shifts, and register names in this slice have matching `reg*` and `reg*_BASE_IDX` entries in `gc_11_0_0_offset.h`.
- Static checks for non-overlapping fields within each register, excluding deliberate aliases or full-width payload registers.
- VM tests that program context page-table base/start/end registers for multiple VMIDs, issue TLB/cache invalidations, poll the correct `GCVM_INVALIDATE_ENGn_ACK` bits, and verify stale translations are not observed.
- Fault-handling tests that exercise protection-fault clear/log paths, translation default address attributes, and invalid aperture accesses under normal and SR-IOV configurations.
- SR-IOV or partitioning tests that vary `GCMC_VM_FB_SIZE_OFFSET_VFn`, MARC base/reloc/length, readonly, and PF/VF mapping registers, then verify isolation and expected address translation.
- GCVM/UTCL2 performance-counter tests that configure event selects, enable/clear counters, use start/stop triggers, and confirm low/high result reads are monotonic or saturate as expected.
- Graphics pipeline tests that load PS/GS/HS/LS shader programs with varied resource declarations, user data, traps, scratch, LDS, CU masks, meshlet dimensions, and request-control settings, then check rendering correctness and absence of GPU hangs.
- Compute/KFD/MES tests that initialize MQDs, set compute dispatch initiator, grid dimensions, thread counts, VMID, scratch/program addresses, resource limits, CU masks, temporary ring size, user data, relaunch/restore fields, and dispatch-end payloads, then submit kernels and validate completion.
- Reset, suspend/resume, runtime power management, and GPU recovery tests while VM contexts and compute queues are active, because page tables, invalidate engines, MARC mappings, shader state, and compute dispatch state may need restoration.
- Regression indicators include invalidate timeouts, stale VM translations, unexpected protection faults, bad PF/VF isolation, incorrect performance-counter values, shader compile/run mismatches, failed KFD queue bring-up, stuck compute waves, incorrect scratch accesses, GPU reset during dispatch, or failures isolated to one shader stage or VMID.
