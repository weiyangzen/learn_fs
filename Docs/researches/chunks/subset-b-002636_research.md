# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_sh_mask.h lines 9654-12153

## Scope

This chunk covers a generated AMD GC 9.1 shader/register mask header range. It starts in the middle of the `GCEA_IO_RD_PRI_FIXED` definition and ends in the middle of `CPF_UTCL1_CNTL`, so the file-level report should reconcile this chunk with adjacent chunks before treating those boundary registers as complete. The range contains 2,143 `#define` macros that provide bit shifts and masks for GC 9.1 register fields.

The covered region spans the tail of the GCEA block, the `gc_tcdec` texture/cache block, the `gc_shdec` shader/compute register block, and the beginning of the `gc_cppdec` command-processor block. It is data-only C preprocessor surface: no functions, structs, or executable statements are defined here.

## Purpose

`gc_9_1_sh_mask.h` supplies compile-time bitfield metadata for AMDGPU code that programs GC 9.1 registers. The macros follow the generated naming pattern `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`, allowing driver code to build register values through helpers such as `REG_SET_FIELD()` and to decode register dumps without hard-coded bit positions.

In this chunk, the register fields describe:

- GCEA request arbitration, priority, urgency, credit/reserve, miscellaneous, latency-sampling, and performance-counter controls.
- TCP/TCI/TCC/TCA cache and texture-channel controls, including invalidate/status bits, cache policy masks, EDC counters, redundancy, DSM controls, writeback/invalidate, and soft reset.
- Graphics shader stage programming registers for PS, VS, ES, GS, LS, and HS, including program base addresses, resource descriptors, late allocation, user-data SGPR payload registers, and pointer-to-user-data address registers.
- Compute dispatch state, including grid dimensions, starts/restarts, thread counts, shader program addresses, scratch bases, resource descriptors, VMID/resource limits, thread management, dispatch identifiers, wave restore addresses, relaunch controls, and compute user data.
- CP/CPC/CPF command-processor debug/fault/UTCL1 controls, including CP DFY address/data/cmd registers, EOP queue wait timing, CPC interrupt metadata, `CP_GFX_ERROR`, and UTCL1 invalidate/drop/bypass/snoop controls.

## Important API Surface

- `GCEA_IO_*` and `GCEA_SDP_*` macros define arbitration coefficients, urgency modes and masks, quantum priorities, SDP DRAM/final priority behavior, credits, tag/VCC/VCD reserves, request controls, latency sampling, and performance counters. These fields affect how GC clients arbitrate traffic and how performance tooling can sample that behavior.
- `TCP_INVALIDATE`, `TCP_STATUS`, `TCP_CNTL`, `TCP_CHAN_STEER_LO/HI`, `TCP_ADDR_CONFIG`, `TCP_CREDIT`, and `TCP_BUFFER_ADDR_HASH_CNTL` describe texture cache invalidation, busy/status reporting, control bits, channel steering, address hashing, and credit behavior. GC 9.1 golden settings in `amdgpu/gfx_v9_0.c` program `mmTCP_CHAN_STEER_LO` and `mmTCP_CHAN_STEER_HI`.
- `TC_CFG_L1_*`, `TC_CFG_L2_*`, `TCI_*`, `TCC_*`, and `TCA_*` define cache-policy and cache-controller fields for load/store/atomic behavior, volatile modes, L2/TCC controls, EDC counters, redundancy, DSM configuration, execution-disable, writeback/invalidate, and reset. These are low-level memory-hierarchy controls rather than user-facing APIs.
- `SPI_SHADER_PGM_RSRC*_{PS,VS,GS,HS}`, `SPI_SHADER_PGM_LO/HI_*`, `SPI_SHADER_LATE_ALLOC_VS`, and `SPI_SHADER_PGM_RSRC2_GS_VS` expose shader-stage program address and resource fields. Important fields include VGPR/SGPR counts, priority, float mode, privilege/debug/IEEE modes, scratch enable, LDS size, trap/debug wavefront behavior, EXCP_EN, user SGPR count, shared VGPR count, CU enable/disable controls, and wave limits.
- `SPI_SHADER_USER_DATA_{PS,VS,ES,LS,COMMON}_0` through `_31` and `SPI_SHADER_USER_DATA_ADDR_{LO,HI}_{GS,HS}` are the ABI-facing registers used to pass shader user data and indirect user-data addresses into graphics pipeline stages.
- `COMPUTE_DISPATCH_INITIATOR`, `COMPUTE_DIM_*`, `COMPUTE_START_*`, `COMPUTE_NUM_THREAD_*`, `COMPUTE_PGM_LO/HI`, `COMPUTE_DISPATCH_PKT_ADDR_*`, `COMPUTE_DISPATCH_SCRATCH_BASE_*`, `COMPUTE_PGM_RSRC1/2`, `COMPUTE_VMID`, `COMPUTE_RESOURCE_LIMITS`, `COMPUTE_STATIC_THREAD_MGMT_SE*`, `COMPUTE_TMPRING_SIZE`, `COMPUTE_RESTART_*`, `COMPUTE_THREAD_TRACE_ENABLE`, `COMPUTE_DISPATCH_ID`, `COMPUTE_THREADGROUP_ID`, `COMPUTE_RELAUNCH`, `COMPUTE_WAVE_RESTORE_ADDR_*`, and `COMPUTE_USER_DATA_0` through `_15` form the compute-dispatch register ABI. `COMPUTE_DISPATCH_INITIATOR` includes fields such as `COMPUTE_SHADER_EN`, partial-threadgroup/ordering controls, scalar/vector L1 invalidate controls, reserved/DATA_ATC-position behavior, and restore.
- `CP_DFY_*` registers expose command-processor debug/fabric-yield style address, data, command, status, and control fields. `CP_DFY_DATA_0` through `_15` are full-width payload registers, while `CP_DFY_CMD` carries offset and size fields.
- `CP_EOPQ_WAIT_TIME`, `CP_CPC_MGCG_SYNC_CNTL`, `CPC_INT_INFO`, `CPC_INT_ADDR`, `CPC_INT_PASID`, and `CP_VIRT_STATUS` describe CP/CPC wait timing, clock-gating sync periods, interrupt address/type/VMID/queue metadata, PASID, and virtualization status.
- `CP_GFX_ERROR` defines a dense fault bitmap for command-processor and graphics-path UTCL1 errors, including SUA, SEM, queue stream/EOP/pipe/read, sync memory read/write, shadow, append, CE DMA/init, PFP/VGT DMA, DMA source/destination, PFP/ME/CE TC, PRT LOD, read-pointer report, RB and instruction/constant/stream fetcher errors.
- `CPG_UTCL1_CNTL`, `CPC_UTCL1_CNTL`, and the visible start of `CPF_UTCL1_CNTL` define UTCL1 XNACK retry timer, VMID reset, drop, bypass, invalidate, fragment-limit, force-snoop, force-dirty, no-PTE memory type, and CPF force-no-execute fields.

## Control Flow

There is no direct control flow in this header slice. Runtime behavior is indirect and comes from C code that includes this generated header, selects the matching `mmREGISTER` offset from the GC 9.1 address header, and writes values through MMIO, ring packets, golden-register initialization, or debug-register paths.

A typical consumer flow is:

1. Pick a register offset, usually from `gc_9_1_d.h` or SOC15 register macros.
2. Construct or patch a 32-bit value using `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`, commonly through `REG_SET_FIELD()`.
3. Write the result through an AMDGPU register helper, a `PACKET3_SET_SH_REG` packet, or a golden-register table entry.
4. Hardware latches that value into graphics, compute, cache, or CP state until a later context restore, command stream, reset, or golden-setting pass changes it.

The chunk has concrete consumers in the surrounding AMDGPU tree. `gfx_v9_0.c` uses `REG_SET_FIELD(0, COMPUTE_DISPATCH_INITIATOR, COMPUTE_SHADER_EN, 1)` while building internal compute dispatch packets, and its GC 9.1 golden-setting tables program `mmCPC_UTCL1_CNTL`, `mmCPF_UTCL1_CNTL`, `mmCPG_UTCL1_CNTL`, `mmTCP_CHAN_STEER_LO`, and `mmTCP_CHAN_STEER_HI`. Register-dump tables include `CP_GFX_ERROR` for GFX generations, making these masks relevant to diagnostic decoding as well.

## State and Persistence

The macros themselves are stateless build artifacts, but they describe persistent hardware state:

- GCEA priority, urgency, reserve, and credit fields persist as arbitration policy for GC traffic until reprogrammed or reset.
- TCP/TCC/TCA/TCI controls persist as cache and memory-path policy; invalidate bits and writeback/invalidate controls can trigger transient hardware actions, but control fields such as channel steering, cache policy, redundancy, DSM, and EDC behavior remain configured state.
- Shader program address/resource and user-data registers persist as context state used by graphics draws. Incorrect user-data or resource fields can survive across draws until overwritten by later state emission.
- Compute dispatch registers persist as compute context state. Dispatch initiation and DATA_ATC/PTR32-related address-mode behavior integrate with KFD/HSA aperture interpretation; `kfd_flat_memory.c` documents that compute SUA mode is decoded from `COMPUTE_DISPATCH_INITIATOR:DATA_ATC` together with `SH_MEM_CONFIG:PTR32`.
- CP/CPC/CPF debug, interrupt, error, and UTCL1 fields persist as command-processor state. Error registers may be read for diagnostics; UTCL1 invalidate/drop/bypass/snoop settings affect address translation and memory consistency behavior for CP front-end paths.

Because this is generated hardware metadata, persistence risk is mostly in consumers using constants from the wrong ASIC generation or pairing a GC 9.1 mask with a non-GC-9.1 register offset.

## Dependencies and Integration Points

- The header depends on AMD's generated GC 9.1 register specification. It must stay synchronized with companion address headers such as `gc_9_1_d.h`; masks alone are not useful without matching register offsets.
- AMDGPU SOC15 helpers, register golden tables, ring packet emission, and debug/register-dump code are the main kernel integration points. The macros are consumed via preprocessor expansion rather than through typed C APIs.
- The compute fields connect to internal AMDGPU GPU tests and KFD/HSA dispatch semantics. `COMPUTE_DISPATCH_INITIATOR` is especially important because command packets, memory aperture mode, restore behavior, and cache invalidation semantics meet there.
- Shader user-data and program-resource fields are the ABI boundary between userspace driver state emission and the kernel/hardware register model. Userspace-generated command streams ultimately program these registers through the GPU command processor.
- Cache, TC/TCP/TCC/TCA, and UTCL1 fields integrate with VM, memory fault handling, cache flush/invalidate sequencing, golden-register initialization, and performance/debug tooling.

## Risks

- Boundary incompleteness: this chunk omits the start of `GCEA_IO_RD_PRI_FIXED` and the end of `CPF_UTCL1_CNTL`. Merge-time documentation must use neighboring chunks for complete field lists.
- Bitfield drift: if the generated shift/mask values diverge from the GC 9.1 hardware spec or the companion address header, register writes can silently program wrong bits.
- Untyped macro misuse: the compiler cannot prevent mixing `*_SHIFT` and `*_MASK` from different registers, different shader stages, or different GC generations.
- Repeated indexed registers create copy/paste hazards. `SPI_SHADER_USER_DATA_*_0..31`, `COMPUTE_USER_DATA_0..15`, `CP_DFY_DATA_0..15`, and stage-specific `SPI_SHADER_PGM_*` fields are parallel but not interchangeable.
- Address split fields are sensitive. `SPI_SHADER_PGM_LO/HI_*`, `COMPUTE_PGM_LO/HI`, dispatch packet address, scratch base, and wave-restore address fields must respect hardware alignment and high/low split rules.
- Cache and translation-control fields can cause severe failures. Incorrect invalidate, bypass, force-snoop, no-PTE memory type, XNACK retry, or VMID reset settings may surface as hangs, stale memory, VM faults, or data corruption.
- Debug/error masks are diagnostic-critical. Misdecoding `CP_GFX_ERROR`, `CPC_INT_INFO`, or `CPC_INT_PASID` can send triage toward the wrong queue, VMID, PASID, or faulting CP sub-block.

## Test Signals

- Build coverage: compiling AMDGPU with GC 9.1 support catches syntax errors, duplicate definitions, and missing macro names used by `REG_SET_FIELD()` or golden-setting tables.
- Generation consistency: compare the macros in this slice against AMD's GC 9.1 register source and verify one-to-one pairing with `gc_9_1_d.h` offsets for the same register names.
- Golden-register validation: boot GC 9.1 hardware or emulation and verify golden settings that program `mmCPC_UTCL1_CNTL`, `mmCPF_UTCL1_CNTL`, `mmCPG_UTCL1_CNTL`, `mmTCP_CHAN_STEER_LO`, and `mmTCP_CHAN_STEER_HI` apply without warnings or unexpected readback differences.
- Compute dispatch smoke tests: AMDGPU internal compute dispatch paths that write `COMPUTE_PGM_LO/HI` and `COMPUTE_DISPATCH_INITIATOR` should complete without fence timeouts, VM faults, or shader launch failures.
- KFD/HSA memory-mode tests: dispatches exercising HSA64/HSA32/GPUVM64 aperture behavior provide coverage for `COMPUTE_DISPATCH_INITIATOR` address-mode interactions.
- Graphics pipeline tests: draw workloads covering PS/VS/GS/HS/LS shader programming and user-data delivery validate the `SPI_SHADER_PGM_*` and `SPI_SHADER_USER_DATA_*` masks indirectly.
- Cache/VM stress: memory-coherency, cache-invalidate, XNACK, VM fault, and GPU reset tests are the strongest signals for the TC/TCP/TCC/TCA and CP/CPC/CPF UTCL1 fields.
- Debug validation: register dumps after injected or observed faults should decode `CP_GFX_ERROR`, `CPC_INT_INFO`, `CPC_INT_ADDR`, and `CPC_INT_PASID` consistently with the failing queue, VMID, PASID, and fault address.
