<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_1_d.h -->
# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_1_d.h

## Purpose

`gfx_8_1_d.h` is an AMD GFX 8.1 register-address header in the `gca` ASIC register namespace. It defines 2,764 preprocessor constants that map symbolic graphics-core register names to dword MMIO, context-register, or indirect/debug-register offsets. The file contains no executable driver logic; it is a compile-time address vocabulary for code that programs the GFX command processor, compute queues, shader engines, render backends, rasterization, depth/color state, caches, tiling, clock/power management, RLC firmware interfaces, diagnostics, and performance counters.

This header is paired by convention with `gfx_8_1_sh_mask.h` for bitfield masks/shifts and `gfx_8_1_enum.h` for enum values. In this tree, the main VI/GFX8 implementation file `amdgpu/gfx_v8_0.c` includes the closely related `gfx_8_0_d.h` instead of this file directly; `gfx_8_1_d.h` still exposes the same register-address API shape for GFX 8.1-specific consumers or generated-table users.

## Important APIs, Types, And Macros

The file defines no structs, functions, variables, or runtime APIs. Its API is the macro namespace:

- `mmCB_*`, `mmCC_*`, `mmGB_*`, and `mmGC_*` cover color-buffer/render-backend state, DCC/CMASK/FMASK surfaces, blend controls, render target masks, backend disable/redundancy, tile/macro-tile modes, `mmGB_ADDR_CONFIG`, shader-array configuration, and GPU identity/configuration registers.
- `mmCP_*`, `mmCPC_*`, `mmCPF_*`, and `mmCPG_*` cover command processor rings, queues, doorbells, VMIDs, interrupts, CP DMA, coherency, semaphores, indirect buffers, microcode loading, MEC/CPC/CPF status, EOP/fence counters, draw/dispatch counters, and HQD/MQD queue descriptors.
- `mmCOMPUTE_*` and `mmSPI_SHADER_*` define compute dispatch state and per-stage shader program registers: dimensions, starts, thread counts, program addresses, TBA/TMA trap state, program resources, user data, and PS/VS/GS/ES/HS/LS shader configuration.
- `mmDB_*`, `mmPA_*`, `mmVGT_*`, `mmIA_*`, and `mmWD_*` define depth/stencil state, occlusion/zpass counters, viewport/scissor/clip/setup/raster state, primitive assembly, tessellation, geometry/streamout rings, vertex/index handling, draw-initiation state, and related debug/performance counters.
- `mmRLC_*`, `mmSMU_*`, `mmCGTT_*`, and `mmCGTS_*` define run-list-controller control/status, RLC microcode interfaces, safe mode, save/restore and SPM performance monitor registers, RLC-to-SMU messaging, clock-gating controls, CU clock/power controls, and GPU virtualization registers.
- `mmSQ_*`, `mmSQC_*`, `mmSPI_*`, `mmSX_*`, `mmTA_*`, `mmTD_*`, `mmTCP_*`, `mmTCI_*`, `mmTCC_*`, `mmTCA_*`, `mmGDS_*`, and `mmSH_*` name shader queues, shader/debug wave state, scalar/vector resource descriptors, thread trace, texture/cache blocks, global data share, memory aperture/static configuration, and performance/debug registers.
- `ix...` constants such as `ixCLIPPER_DEBUG_REG*`, `ixSQ_WAVE_*`, `ixSQ_INTERRUPT_WORD_*`, `ixWD_DEBUG_REG*`, `ixVGT_DEBUG_REG*`, and `ixDIDT_*` are indirect-register indices for debug windows, wave inspection, interrupt words, and DIDT tuning rather than ordinary MMIO register names.

Several names intentionally alias the same numeric offset. Examples include legacy CP ring aliases (`mmCP_RB0_BASE` and `mmCP_RB_BASE`), queue offload aliases (`mmCP_HQD_DMA_OFFLOAD` and `mmCP_HQD_OFFLOAD`), GRBM hypervisor/non-hypervisor CAM aliases, and multiple SQ instruction/trace word names that map to a shared decode or data register.

## Control Flow

Local control flow is limited to the include guard `GFX_8_1_D_H`. There are no branches, calls, callbacks, loops, or initialization routines in this header.

Runtime control flow is in consumers that pass these offsets to register helpers or command packet builders. The related GFX8 paths show the intended flow:

- Golden-register setup writes tables containing offsets such as `mmGRBM_GFX_INDEX` and `mmGB_ADDR_CONFIG` before normal IP operation.
- Compute shader test packets use offsets such as `mmCOMPUTE_PGM_LO` relative to `PACKET3_SET_SH_REG_START` to build command streams.
- MEC/HQD setup loops over dense register ranges from `mmCP_MQD_BASE_ADDR` through `mmCP_HQD_*`, writes queue base/read/write pointers, programs doorbells, and sets `mmCP_HQD_ACTIVE`.
- Queue teardown writes `mmCP_HQD_DEQUEUE_REQUEST`, polls `mmCP_HQD_ACTIVE`, then clears queue state.
- RLC safe-mode entry/exit writes `mmRLC_SAFE_MODE` and polls the same register until the command field reaches the expected state.
- Per-shader-engine or per-CU programming selects hardware instances through `mmGRBM_GFX_INDEX` before writing replicated registers.

This header supplies the numeric operands for those flows; ordering, locking, polling, and error handling are owned by the including driver code.

## State And Persistence Behavior

`gfx_8_1_d.h` has no mutable software state, no allocation, no locking, and no persistence beyond preprocessor constants embedded into compiled objects.

The hardware registers named by the macros are persistent GPU state until changed by the driver, firmware, reset, suspend/resume, power gating, or virtualization context switching. High-impact persistent state includes CP ring and HQD/MQD queue descriptors, doorbell routing, shader program addresses and user data, render target/depth/stencil surfaces, tile and macro-tile configuration, backend and shader-array masks, RLC safe-mode and power/clock-gating controls, GDS allocation registers, thread-trace buffers, and performance counter setup. A wrong macro value therefore silently redirects later reads/writes to the wrong register rather than causing a compile-time failure.

## Dependencies

The header depends on AMD's generated GFX 8.1 register map and naming conventions. It is normally useful only with:

- `gca/gfx_8_1_sh_mask.h` for field masks/shifts used with these offsets, such as HQD active/doorbell fields, RLC safe-mode fields, GB tile-mode fields, and shader-resource fields.
- `gca/gfx_8_1_enum.h` for companion enum values used when programming the same registers.
- AMDGPU register access helpers and packet builders such as `RREG32`, `WREG32`, `WREG32_P`, `REG_SET_FIELD`, `REG_GET_FIELD`, and `PACKET3_SET_SH_REG_START`.
- Neighboring ASIC block headers for the same VI-era driver stack, including GMC 8.x, OSS 3.x, BIF 5.x, DCE 10.x, SMU 7.x, and interrupt source headers.
- Firmware/runtime code for CE/PFP/ME/MEC/RLC engines, because many offsets here address microcode upload windows, command processor queues, and RLC-mediated state.

Numeric offsets in this header are family-specific. Similar macro names in `gfx_8_0_d.h`, later `gc_*` SOC15 headers, or older GFX6/GFX7 headers must not be mixed unless the target ASIC's register map is known to match.

## Integration Points

Direct include references to `gfx_8_1_d.h` were not found in the checked C sources, while `gfx_v8_0.c` includes `gfx_8_0_d.h`. The strongest integration points are therefore the GFX8 register-programming patterns that use the same macro families and would consume this header when built for a GFX 8.1 map:

- `amdgpu/gfx_v8_0.c` programs golden registers, tile modes, GDS offsets, compute test packets, HQD/MQD setup/restore, RLC safe mode, clock/power gating, GRBM instance selection, and command processor lifecycle using the same `mm*` register namespace.
- `amdgpu/amdgpu_amdkfd_gfx_v8.c` uses HQD/MQD offsets for KFD queue loading, queue detection by `mmCP_HQD_PQ_BASE`/`HI`, doorbell programming, dequeue requests, wave-control dispatch through `mmGRBM_GFX_INDEX`, and active-queue polling.
- KFD MQD managers and VI structures depend on the same CP HQD/MQD hardware layout when translating kernel queue state to GPU queue descriptor registers.
- Debug, profiling, and diagnostic code can use the `mm*_PERFCOUNTER*`, `mmSQ_THREAD_TRACE*`, `ixSQ_WAVE_*`, GRBM status, CP status, RLC status, and block debug-register constants for inspection.

Because the header is generated and standalone, it may also serve as source material for register databases, validation scripts, or out-of-tree GFX8.1 code even when in-tree C files prefer the GFX8.0 variant.

## Risks And Edge Cases

The main risk is silent address drift. Plain macros do not encode address space, access width, privilege level, side effects, reset requirements, or field layout. If a value is wrong, later driver code can corrupt unrelated GPU state, hang command submission, break queue scheduling, misprogram shader resources, or produce invalid performance/debug data.

The file contains many intentional duplicate values. Alias-aware validation is required for names such as CP ring aliases, GRBM CAM aliases, SQ instruction decode aliases, SQ trace-word aliases, and per-block debug-window indices. Treating every duplicate as a defect would produce false positives; treating every duplicate as harmless would miss real copy errors.

Several register ranges are used arithmetically by consumers. HQD/MQD save/restore loops depend on contiguous offsets from `mmCP_MQD_BASE_ADDR` through `mmCP_HQD_*`; viewport/scissor, color target, tile-mode, macro-tile, GDS VMID, and performance counter families similarly imply dense layouts. A single base or endpoint error can shift a whole loop into adjacent registers.

Some constants are context or packet register offsets in the `0xA000`/`0xC000` ranges, not simple always-safe MMIO writes. Consumers often subtract packet base constants or write them through command streams. Using the wrong access path can be as damaging as using the wrong address.

Compared with `gfx_8_0_d.h`, this 8.1 header drops some GFX8.0-specific virtualization/EDC/RLC definitions and adds a smaller set of GFX8.1-specific names such as `mmCP_ATCL1_CNTL`, `mmPA_SC_DSM_CNTL`, `mmPA_SC_ENHANCE_1`, additional RLC GPM/SMU argument registers, and SX blend optimization controls. Regeneration or cross-family substitution should review these deltas explicitly.

## Test Signals

Build-time signals include successful compilation of any GFX8.1 consumer with `gfx_8_1_d.h`, `gfx_8_1_sh_mask.h`, and `gfx_8_1_enum.h`; no undefined register names in queue, RLC, shader, GDS, tiling, and diagnostics code; and generated-register validation against AMD metadata while allowing known aliases.

Runtime signals on matching hardware include successful GPU probe, CE/PFP/ME/MEC/RLC firmware loading, passing graphics and compute ring tests, stable KFD queue creation/destruction, correct doorbell and HQD active-state behavior, clean RLC safe-mode transitions, working suspend/resume and power-gating transitions, correct render output with color/depth/DCC/tile-mode state, and absence of CP/RLC/GRBM hang reports.

Diagnostic signals include sensible values from GRBM/CP/RLC status registers, valid performance counter programming/readback, working SQ thread trace and wave debug reads, correct GDS allocation behavior, and expected debugfs or amdgpu diagnostics for tile modes, backend masks, shader arrays, and queue state.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_1_d.h -->
