# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h lines 2470-4973

## Scope

This chunk covers lines 2470-4973 of the generated GFX10.1 GC register offset header. It is a hardware register map, not executable driver logic. The chunk contains 1,214 non-`_BASE_IDX` `mm*` register offset macros, plus the paired `*_BASE_IDX` macros used by SOC15 register-address helpers. The region starts mid-pair with `mmSQ_SHADER_TBA_LO_BASE_IDX` at line 2470, then continues with shader/SQ registers at offsets around `0x10bd`; it ends at line 4973 with `mmCP_IQ_WAIT_TIME3` and its paired base-index macro is outside this chunk.

The generated format is consistent with the rest of `gc_10_1_0_offset.h`: each hardware register is represented as a preprocessor constant such as `mmGCVM_CONTEXT0_CNTL 0x1620` and usually a companion `mmGCVM_CONTEXT0_CNTL_BASE_IDX 0`. Driver code combines these values with the GC IP instance and the SOC15 base table through helpers such as `SOC15_REG_OFFSET(GC, 0, ...)`, `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_SOC15_OFFSET`.

## Purpose

The purpose of this chunk is to provide the numerical MMIO offsets for a large portion of the Navi/GFX10.1 graphics and compute command, shader, texture, render backend, memory-translation, and VM register space. These constants are effectively an ABI between AMD's generated register database and the in-kernel AMDGPU/KFD code that programs GFX10.1 hardware.

The covered range is especially important because it includes:

- Shader queue/SQ debugging and thread trace controls, including watchpoints and thread-trace buffer programming.
- SPI shader processor interpolation, wave lifetime, per-stage shader program registers, and performance counters.
- Texture front-end, GDS, DB/CB/RB, GB tiling, and color/depth backend register offsets.
- GCVM/GCMC graphics VM context, invalidate, L2 cache, ATC, TLB, and protection-fault register offsets.
- GCEA address decode and memory-client routing controls.
- Shader register-space offsets for graphics and compute pipeline state.
- Command processor ring, interrupt, VMID, queue priority, context, suspend/resume, and microcode-entry-point registers.

## Address Blocks and Register Families

The chunk crosses multiple generated `addressBlock` sections:

| Lines | Address block | Base | Non-base macros | Main register families |
| --- | --- | ---: | ---: | --- |
| 2470-2574 | continued previous block | inherited | 52 | `SQ`, `SQC` shader control, watch, trace, counters, UTCL0 cache controls |
| 2577-2725 | `gc_shsdec` | `0x9000` | 74 | `SX`, `SPI` graphics setup, SPI config, wave lifetime, trap-screen bounds, SPI counters |
| 2729-2753 | `gc_tpdec` | `0x9400` | 12 | `TD`, `TCP`, `TA` texture pipe controls, DSM and scratch registers |
| 2757-2783 | `gc_gdsdec` | `0x9700` | 13 | `GDS` config, EDC counters, DSM, CSB registers |
| 2787-2983 | `gc_rbdec` | `0x9800` | 98 | `DB`, `CB`, `GB`, `CC`, `GC_USER` render backend, tiling, stutter, pipe/backend disable |
| 2987-3033 | `gc_gceadec2` | `0x9c00` | 23 | `GCEA` SDP, IO, probe, DSM, performance, misc controls |
| 3037-3043 | `gc_spipdec2` | `0x9c80` | 3 | `SPI` PQ event and SYS WIF controls |
| 3047-3069 | `gc_gceadec3` | `0x9dc0` | 11 | `GCEA` DRAM bank, arbitration, and SDP enable controls |
| 3073-3133 | `gc_rmi_rmidec` | `0x9e00` | 30 | `RMI` routing, scoreboards, UTCL1/TCIW errors, redundancy |
| 3137-3151 | `gc_pmmdec` | `0x9f80` | 7 | `PMM`, `GCR` power/performance and spare controls |
| 3155-3163 | `gc_utcl1dec` | `0x9fa0` | 4 | `UTCL1`, `GCRD` UTCL/SA target controls |
| 3167-3191 | `gc_gcatcl2dec` | `0xa000` | 12 | `GC_ATC_L2` ATC L2 address-translation cache controls |
| 3195-3265 | `gc_gcvml2pfdec` | `0xa100` | 35 | `GCVM_L2`, protection-fault, dummy page, context identity aperture, walker throttle |
| 3269-3675 | `gc_gcvml2vcdec` | `0xa200` | 203 | `GCVM_CONTEXT0..15`, invalidate engines 0-17, invalidate acknowledgements and ranges |
| 3679-3719 | `gc_gcvmsharedpfdec` | `0xa590` | 20 | `GCMC_VM`, shared VM MMIO apertures, FB/AGP/TLB reset requests |
| 3723-3739 | `gc_gcvmsharedvcdec` | `0xa600` | 8 | `GCMC_VM` framebuffer/AGP location, system aperture, L1 TLB control |
| 3743-4001 | `gc_gceadec` | `0xa800` | 129 | `GCEA` address-decode maps, DRAM remap, DSM, SDP/VCD, IO and spare controls |
| 4005-4023 | `gc_tcdec` | `0xac00` | 9 | `TCP`, `TCI` invalidate, address config, depth controls |
| 4027-4679 | `gc_shdec` | `0xb000` | 326 | `SPI_SHADER_*`, `COMPUTE_*`, `SPI_CSQ`, user data, resource, trap, dispatch, scratch |
| 4683-4973 | `gc_cppdec` | `0xc080` | 145 | `CP`, `CPC`, `CPG`, `CPF` EOP, rings, interrupts, VMID, queue priority, context, suspend/resume |

Dominant families by macro count are `SPI` (mostly shader program registers), `GCVM`/`GCMC` (graphics VM), `GCEA` (address decode), `CP`/`CPC` (command processor), `COMPUTE`, `GB`, `DB`, `RMI`, and `GDS`.

## Important APIs, Types, and Macros

This header does not define C types or functions. Its important exported API is the set of preprocessor constants consumed by AMDGPU and AMDKFD:

- `mmSQ_*` and `mmSQC_*`: shader queue/sequencer controls, debug watch registers, thread-trace buffer setup, LB counters, EDC counters, indirect index/data, shader TBA/TMA addresses, and SQC cache UTCL0 controls.
- `mmSPI_*`: shader processor interpolator and shader program register offsets. The chunk includes graphics-stage resource/user-SGPR/user-data groups such as `mmSPI_SHADER_PGM_RSRC4_PS`, `mmSPI_SHADER_PGM_LO_GS`, `mmSPI_SHADER_USER_DATA_PS_*`, and many `mmSPI_SHADER_USER_ACCUM_*` registers.
- `mmCOMPUTE_*`: compute shader command state such as `mmCOMPUTE_PGM_LO/HI`, `mmCOMPUTE_PGM_RSRC*`, dispatch dimensions, start coordinates, thread-management masks, user data, scratch, trap, restart, perf, and dispatch tunneling controls.
- `mmGCVM_*`: graphics VM context and invalidation registers. The chunk defines context 0-15 control, page-table base, start, and end address pairs; L2 cache and protection fault controls; invalidate engine semaphores, requests, acknowledgements, and address ranges.
- `mmGCMC_VM_*`: shared graphics-memory-controller VM aperture and TLB controls, including framebuffer and AGP location registers.
- `mmGC_ATC_L2_*`: ATC L2 cache control/status registers used by address-translation paths.
- `mmDB_*`, `mmCB_*`, `mmGB_*`, `mmCC_*`: render backend, depth buffer, color buffer, tile/macrotiling, stutter, and backend-disable offsets.
- `mmGCEA_*`: address decode, DRAM client/group maps, SDP, DSM, IO, probe, and performance-counter controls.
- `mmCP_*`, `mmCPC_*`, `mmCPG_*`, `mmCPF_*`: command processor EOP queue wait, ring buffer base/control/read-pointer/write-pointer, interrupt control/status, power, ECC, fetcher, queue priority, program-counter starts, context controls, VMID reset/preempt/status, and suspend/resume controls.
- `*_BASE_IDX`: base-index companions for each register. In this chunk all visible `*_BASE_IDX` values are `0`, meaning callers use SOC15 GC base segment index 0 for these offsets.

The sibling `gc_10_1_0_sh_mask.h` supplies bit masks and shifts for many of these offsets. The driver normally writes an offset macro together with a mask macro, for example reading `mmGCVM_CONTEXT0_CNTL`, modifying fields with `GCVM_CONTEXT0_CNTL__...` masks/shifts, then writing the same register back.

## Control Flow

There is no runtime control flow in this header. The practical control flow happens in consumers:

1. A GFX10.1 driver source includes `gc/gc_10_1_0_offset.h` and usually `gc/gc_10_1_0_sh_mask.h`.
2. A register macro is passed to a SOC15 helper. For direct MMIO, code uses `RREG32_SOC15(GC, 0, mm...)` or `WREG32_SOC15(GC, 0, mm..., value)`. For offsets stored in structs or packet payloads, code uses `SOC15_REG_OFFSET(GC, 0, mm...)`.
3. For repeated register groups, code computes distances from adjacent offset macros. A representative pattern in `gfxhub_v2_0_init()` computes `hub->ctx_distance = mmGCVM_CONTEXT1_CNTL - mmGCVM_CONTEXT0_CNTL` and similar distances for page-table bases and invalidate engines.
4. Runtime code then iterates over contexts, invalidation engines, rings, pipes, or queues by applying those distances with `WREG32_SOC15_OFFSET` or by storing absolute register offsets in `struct amdgpu_vmhub`.

The generated ordering is therefore semantically important. Even if no C loop exists in this file, several consumers assume that register instances are evenly spaced and ordered exactly as represented by this header.

## State and Persistence Behavior

The header itself has no persistent state, allocation, locking, or side effects. It describes persistent hardware state that survives in GPU registers until reset, reinitialization, context switch, or explicit driver programming. Important state categories represented by this chunk include:

- VM state: `mmGCVM_CONTEXT*` page-table roots, virtual address bounds, translation-control bits, invalidate engine requests/acks, and protection-fault status. These registers control GPU virtual-memory translation for graphics/compute traffic.
- Shader and compute state: `mmSPI_SHADER_*` and `mmCOMPUTE_*` registers describe currently programmed shader addresses, resources, scratch, user data, trap addresses, dispatch dimensions, and thread-management state.
- Debug and profiling state: `mmSQ_WATCH*`, `mmSQ_THREAD_TRACE_*`, `mmSQ_LB_*`, `mmSPI_WF_LIFETIME_*`, and performance-counter registers configure debug watchpoints, thread trace buffers, lifetime counters, and diagnostic counters.
- Command processor state: `mmCP_RB*`, `mmCP_INT_*`, `mmCP_EOPQ_*`, `mmCP_CONTEXT_CNTL`, `mmCP_VMID_*`, and `mmCPC_SUSPEND_*` program ring buffers, interrupt routing/status, queue priorities, VMID behavior, and suspend/context-save memory layout.
- Render backend and memory-routing state: `mmDB_*`, `mmCB_*`, `mmGB_*`, `mmGC_USER_*`, `mmRMI_*`, and `mmGCEA_*` configure tiling, backend masks, stutter behavior, memory route/decode settings, and redundancy.

Because these are register offsets, incorrect constants usually do not cause ordinary memory corruption in this header. Instead, they cause later driver code to write a valid value to the wrong hardware register or read a status bit from the wrong location. That can manifest as VM faults, queue hangs, corrupt rendering, failed reset, lost interrupts, broken debugger/profiler output, or invalid SR-IOV behavior.

## Dependencies

Direct dependencies are compile-time only:

- C preprocessor inclusion by AMDGPU/KFD source files.
- The SOC15 register-base infrastructure that interprets `GC`, instance `0`, and the `*_BASE_IDX` values.
- Bitfield macros in `gc_10_1_0_sh_mask.h`.
- Defaults in related generated headers such as `gc_10_1_0_default.h` when consumers reset registers to hardware default values before setting fields.

Representative consumers under `drivers/gpu/drm/amd` include:

- `amdgpu/gfx_v10_0.c`, which includes this header and programs CP graphics rings with offsets such as `mmCP_RB0_BASE`, `mmCP_RB0_BASE_HI`, `mmCP_RB0_CNTL`, and write/read pointer registers.
- `amdgpu/gfxhub_v2_0.c`, which includes this header and uses `mmGCVM_CONTEXT0_CNTL`, `mmGCVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32`, `mmGCVM_INVALIDATE_ENG0_REQ`, and related offsets to initialize the graphics VM hub.
- `amdgpu/gfxhub_v2_1.c`, which uses the same GFX10-family VM layout and stores/restores `mmGCVM_CONTEXT0_CNTL`-based state.
- `amdkfd/kfd_mqd_manager_v10.c` and `amdgpu/amdgpu_amdkfd_gfx_v10.c`, which use this generation's offsets and masks for KFD queue descriptors, HQD load/destroy/dump paths, and queue occupancy checks.
- Other GFX10-family modules including `amdkfd/kfd_device_queue_manager_v10.c`, `amdgpu/amdgpu_sdma.c`, `amdgpu/sdma_v5_0.c`, `amdgpu/mmhub_v2_0.c`, `amdgpu/mxgpu_nv.c`, and `amdgpu/nv.c`.

## Integration Points

Key integration points are hardware-programming paths rather than function calls from this header:

- Graphics VM initialization: `gfxhub_v2_0_enable_system_domain()` reads `mmGCVM_CONTEXT0_CNTL`, sets context-enable, depth, and retry fields, then writes it back. `gfxhub_v2_0_init()` stores SOC15 offsets for context page-table bases, invalidate engine registers, and protection-fault registers, and computes distances from adjacent macros.
- VM disable and invalidation: `gfxhub_v2_0_gart_disable()` disables all contexts by iterating over `mmGCVM_CONTEXT0_CNTL` with `hub->ctx_distance`. Any spacing error in the context macros would disable or modify the wrong context registers.
- Ring setup: `gfx_v10_0` programs CP ring state using `mmCP_RB0_*`, `mmCP_RB1_*`, `mmCP_RB2_*`, `mmCP_RB_WPTR_POLL_ADDR_*`, and `mmCP_RB_ACTIVE`. These offsets are central to command submission.
- KFD queue management: KFD v10 code includes this offset header with the matching mask header and uses the same generation's register vocabulary for HQD load/dump/destroy and MQD setup. Queue control correctness depends on CP/HQD register offsets aligning with firmware/hardware expectations.
- Shader dispatch and packet construction: code that builds compute or graphics packets uses shader and compute register offsets, often as packet payload register addresses. The `mmSPI_SHADER_*` and `mmCOMPUTE_*` ranges in this chunk are therefore part of command-stream ABI.
- Debug/profiling tools: SQ watch, thread trace, lifetime, and performance counter offsets integrate with developer tooling, hang diagnostics, and profiling paths. Misalignment may not be detected by basic boot tests but can break debug signal collection.

## Risks and Edge Cases

- Generated-header drift: these constants should match AMD's hardware register database for GC 10.1. Manual edits are high risk because a one-line offset change silently redirects MMIO.
- Chunk boundary risk: line 2470 is the `BASE_IDX` for a macro that begins before this chunk, and line 4973 is `mmCP_IQ_WAIT_TIME3` without its paired `BASE_IDX` line. Merge/reconciliation should account for pairs crossing chunk boundaries.
- Register instance spacing assumptions: VM context and invalidate-engine consumers compute distances from adjacent macros. If one member of a repeated group is missing, reordered, or assigned the wrong offset, loops that program 16 contexts or 18 invalidation engines can corrupt unrelated registers.
- Same-offset aliases: some registers deliberately share an offset, such as the visible `mmSQ_WREXEC_EXEC_HI` and `mmSQ_WREXEC_EXEC_LO` both mapped to `0x1151`. A naive duplicate-offset checker could flag legitimate aliases; validation should distinguish hardware aliases from accidental collisions.
- Base-index assumptions: all visible base-index values in the chunk are `0`. If a future ASIC revision moves some blocks to a different SOC15 base index, changing only offsets without base indexes would be incomplete.
- 32-bit/64-bit register pairs: many base address and range registers are split into LO/HI pairs, for example VM page-table bases, CP ring bases, SQ thread-trace buffers, and CPC suspend context-save addresses. Programming order, alignment, and shifting are handled by consumers, but wrong offsets break the pair.
- Security and isolation impact: GCVM context, protection fault, VMID, page table, invalidate, and suspend context-save offsets affect address translation and process isolation. Errors here can produce GPU memory faults, stale translations, incorrect VMID preemption, or queue state leakage across contexts.
- Diagnostics coverage gap: offsets used only by profiling, EDC, or debug paths may not be covered by ordinary rendering or compute smoke tests.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-behavior checks:

- Build coverage: compile AMDGPU/KFD with `gc_10_1_0_offset.h` and `gc_10_1_0_sh_mask.h` included by GFX10/KFD sources. Preprocessor failures catch missing macros but not wrong values.
- Register offset smoke checks: compare generated offsets against AMD's authoritative register database or known-good upstream header for GC 10.1. This is the most direct way to catch value drift.
- GFX ring bring-up: boot a GC 10.1 device and verify `gfx_v10_0` initializes CP rings without ring test timeout, especially paths programming `mmCP_RB0_BASE`, `mmCP_RB0_BASE_HI`, `mmCP_RB*_CNTL`, and pointer registers.
- VM/GART tests: exercise GART enable/disable, VM fault handling, and TLB invalidation. Good signs include successful `gfxhub_v2_0` initialization, no unexpected VM fault storms, and correct handling of invalid page faults.
- KFD compute queue tests: create/destroy AQL queues, dispatch compute kernels, and trigger preemption/CWSR where available. These paths stress CP/HQD, VMID, suspend, and compute program registers.
- Graphics rendering tests: run basic DRM/KMS and userspace rendering workloads that exercise SPI shader program state, DB/CB/RB backend state, GB tiling state, and command submission.
- Debug/profiling tests: run SQ thread trace, performance counter collection, and debugger watchpoint flows if available. These are needed to cover the SQ/SPI diagnostic registers that normal rendering may not touch.
- Suspend/reset tests: trigger GPU reset and system suspend/resume paths on supported hardware; observe CP, VM, and CPC suspend/context-save programming behavior.

## Research Notes

This chunk is source-tree-aligned to the original generated header and intentionally does not produce a final per-file report. The later merge lane should combine this with the neighboring chunks for `gc_10_1_0_offset.h`, especially because the line boundaries cut through register/base-index pairs at both ends.
