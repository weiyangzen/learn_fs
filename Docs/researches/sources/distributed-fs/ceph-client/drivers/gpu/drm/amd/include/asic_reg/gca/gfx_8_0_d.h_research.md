<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_0_d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_0_d.h

## Purpose
`gfx_8_0_d.h` is a generated-style AMD GFX 8.0 register-address header for the GCA/GC graphics block. It exports symbolic preprocessor names for direct MMIO-style `mm*` register offsets and indexed/debug `ix*` register selectors used by the VI/GFX8 AMDGPU, KFD, SDMA, VCE, and PowerPlay paths.

The file contains address constants only. It does not describe bit layouts, legal field values, access ordering, or reset semantics; consumers combine these offsets with masks and shifts from `gfx_8_0_sh_mask.h`, enumerants from `gfx_8_0_enum.h`, and register access helpers such as `RREG32()`, `WREG32()`, and indirect/indexed debug helpers.

## Important APIs, Types, and Constants
There are no C functions, structs, enums, variables, or inline helpers. The exported API is the guarded macro namespace under `GFX_8_0_D_H`.

The address map is broad and covers most GFX8 graphics/compute sub-blocks:

- Color/depth render backend registers: `mmCB_*`, `mmDB_*`, `mmCC_*`, and `mmGB_*` define color targets, DCC/CMASK/FMASK metadata, blend/control state, depth/stencil state, tile and macrotile modes, backend disable/redundancy, occlusion/Z-pass counters, and CB/DB performance/debug registers.
- Command processor and queues: `mmCP_*`, `mmCPC_*`, `mmCPF_*`, and `mmCPG_*` define graphics ring buffers, MEC rings, read/write pointers, doorbell ranges, MQD/HQD queue descriptors, VMID/preemption/context controls, microcode upload ports, interrupts, fences, append/atomic/GDS preop state, DMA commands, queue thresholds, packet status, and many CP performance counters.
- Geometry and raster pipeline: `mmPA_*`, `mmVGT_*`, `mmIA_*`, and `mmWD_*` define viewport transforms, clip planes, scissor rectangles, AA sample locations, setup/raster state, index/primitive draw state, tessellation/GS rings, stream-out buffers, work distributor controls, and related debug/performance counters.
- Shader dispatch and shader front end: `mmSPI_*`, `mmSQ_*`, `mmSQC_*`, `mmSX_*`, `mmSH_*`, and `mmCOMPUTE_*` cover graphics shader programs and user data for PS/VS/GS/ES/HS/LS, compute dispatch dimensions, compute user data, queue reset/trap registers, resource reservation, wave lifetime/debug state, SQ/SQC configuration, thread trace buffers, SQ instruction/debug selectors, shader memory apertures, and export/performance counters.
- Texture/cache/memory path: `mmTA_*`, `mmTD_*`, `mmTCP_*`, `mmTCI_*`, `mmTCC_*`, `mmTCA_*`, and `mmTC_CFG_*` define texture address/data front-end controls, TCP cache invalidation/status/watchpoints, L1/L2 cache policies, TCC/TCA controls, EDC counters, and cache performance counters.
- Global data share and synchronization: `mmGDS_*` defines GDS read/write/atomic apertures, GWS/OA resources, VMID base/size partitions, GWS/OA ownership per VMID, context-switch counters, protection faults, and GDS performance/debug state.
- Run-list/power and global register block management: `mmRLC_*`, `mmGRBM_*`, `mmCGTT_*`, `mmCGTS_*`, `mmGC_*`, `mmGFX_*`, `mmRAS_*`, `mmDIDT_*`, and `mmGPU_*` define RLC safe mode, save/restore, power/clock gating, CU power-gating controls, GRBM status/indexing/reset/debug, RAS signatures, DIDT indexed controls, and clock-throttle registers.
- Indexed debug selectors: `ixCLIPPER_*`, `ixPA_SC_*`, `ixSQ_*`, `ixGDS_*`, `ixWD_*`, `ixIA_*`, `ixVGT_*`, and `ixDIDT_*` name values written to debug or indirect index registers before reading/writing paired data registers.

The file also contains intentional aliases where multiple symbolic concepts share one offset, such as `mmCP_RB0_BASE`/`mmCP_RB_BASE`, `mmCP_RING0_PRIORITY`/`mmCP_ME0_PIPE0_PRIORITY`, `mmCP_HQD_DMA_OFFLOAD`/`mmCP_HQD_OFFLOAD`, `mmGRBM_HYP_CAM_INDEX`/`mmGRBM_CAM_INDEX`, and several SQ thread-trace or instruction-word names. These aliases are part of the hardware naming contract and should not be treated as duplicates to remove.

## Control Flow
There is no runtime control flow in this header. The only local flow is the include guard: after `GFX_8_0_D_H` is defined, repeated includes skip the macro body.

Runtime control flow lives in consumers. For example, `amdgpu/gfx_v8_0.c` includes this header and writes `mmCP_RB0_BASE`/`mmCP_RB0_BASE_HI` while programming graphics ring buffers, then reads or updates `mmRLC_CNTL` while enabling, disabling, or querying RLC behavior. The same address map is included by KFD integration code, SDMA 2.4/3.0 code, VI common code, VCE 3.0 code, MXGPU VI virtualization code, and multiple PowerPlay SMU manager files.

The macro values are therefore inputs to larger initialization, reset, interrupt, queue setup, context-switch, power-management, virtualization, and debug flows. The header itself cannot enforce sequencing such as halting a block before programming it, polling an idle bit, flushing posted writes, or selecting the right shader engine/instance through GRBM.

## State and Persistence Behavior
The header is stateless and persists nothing. Its macros name hardware registers whose values live in the GPU register file or indexed debug/register spaces until reset, power transition, firmware action, context switch, or a driver write changes them.

The represented hardware state includes render target base addresses and metadata, depth/stencil surfaces, graphics and compute ring-buffer pointers, doorbell ranges, HQD/MQD queue descriptors, VMID assignments, shader program bases and user data, compute dispatch dimensions, stream-out buffers, tessellation/GS ring sizes, GDS partitions and ownership, cache/TCP/TCC policy and invalidation state, RLC save/restore and power-gating state, GRBM selected instance state, RAS/DIDT diagnostics, and performance-counter selectors and counter values.

Many of these registers are sequencing-sensitive or scope-sensitive. Some values are per shader engine, per pipe, per queue, per VMID, per render target, or per shader stage. This file encodes only numeric offsets; persistence domain, reset domain, write-one-clear behavior, privilege requirements, and indexed-access side effects must be supplied by hardware documentation and the calling code.

## Dependencies and Integration Points
The syntactic dependency is only the C preprocessor. Practical use depends on:

- `gfx_8_0_sh_mask.h` for field masks, shifts, and bit names that match these register addresses.
- `gfx_8_0_enum.h` for symbolic field values used in packet, queue, shader, and pipeline programming.
- AMDGPU register access helpers and GRBM/indexed-register selection helpers that know whether an address is direct MMIO, per-instance, indexed debug, or otherwise aperture-specific.
- ASIC-family dispatch that selects the GFX8/GCA map instead of neighboring GFX6/7 maps or later GC 9/10 `*_offset.h` maps, where offsets and base-index models differ.

Direct include sites found in this tree include `amdgpu/gfx_v8_0.c`, `amdgpu/vi.c`, `amdgpu/amdgpu_amdkfd_gfx_v8.c`, `amdgpu/sdma_v2_4.c`, `amdgpu/sdma_v3_0.c`, `amdgpu/vce_v3_0.c`, `amdgpu/mxgpu_vi.c`, `pm/powerplay/inc/smu7_common.h`, and SMU manager files for `fiji`, `polaris10`, `smu8`, and `vegam`.

Major integration points are GFX ring bring-up, MEC/HQD compute queue programming, KFD queue and MQD handling, shader-stage resource setup, render backend state programming, CP/RLC firmware upload and control, clock/power gating, SR-IOV/MXGPU support, SMU/PowerPlay register scripts, performance monitoring, thread tracing, and low-level diagnostics.

## Risks and Edge Cases
Register-address drift is high impact. A wrong offset can write unrelated graphics hardware, causing GPU hangs, bad memory access, broken command submission, failed queue preemption, corrupted render state, missed interrupts, invalid cache or GDS isolation, power-management failures, or virtualization isolation bugs.

The `mm*` and `ix*` prefixes are conventions, not type-safe access classes. Passing an indexed debug selector to a direct MMIO helper, programming a per-instance register without selecting the intended GRBM scope, or using a GFX8 address on a different ASIC generation can silently target the wrong hardware.

Aliases and repeated numeric offsets are intentional in several places. Static audits must distinguish true generation errors from names that represent multiple hardware views of the same register word or one debug data aperture reused for multiple decoded payloads.

This header is especially sensitive around queue and VM state. CP/HQD/MQD, doorbell, VMID, GDS, and shader context-save registers interact with user queues and KFD/AMDGPU scheduling; stale values or incorrect sequencing can expose data across contexts or wedge queues. RLC, clock-gating, DIDT, and RAS registers may also require firmware coordination and safe-mode sequences not visible in this file.

## Test Signals
Primary validation is build and hardware integration rather than unit tests:

- Kernel build coverage for VI/GFX8 AMDGPU, KFD, SDMA, VCE, MXGPU, and PowerPlay configurations catches missing symbol names, include-guard breakage, and incompatible macro renames.
- Static checks should compare register names used with bit fields from `gfx_8_0_sh_mask.h` and enumerants from `gfx_8_0_enum.h`, and should flag suspicious cross-generation includes or use of `ix*` selectors in direct MMIO helpers.
- Driver probe on matching GFX8 hardware should exercise GRBM status/reset, CP ring setup, MEC/HQD queue setup, RLC firmware/control, render backend setup, shader dispatch, compute dispatch, interrupts, and performance-counter access.
- KFD and compute tests should cover queue creation/destruction, doorbell signaling, VMID assignment, preemption/context save, GDS/GWS/OA allocation, and shader trap/debug paths.
- Graphics tests should cover draw/dispatch submission, color/depth targets, tessellation/geometry/stream-out paths, scissor/viewport state, cache invalidation, and suspend/resume or reset recovery.
- Failure signals include CP/RLC idle timeouts, ring pointer stalls, HQD dequeue failures, bad doorbell behavior, VM faults after queue setup, render corruption, GDS protection faults, thread-trace/perf-counter read failures, RLC safe-mode hangs, clock/power-gating regressions, and generation-specific probe failures on VI-family ASICs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_0_d.h -->
