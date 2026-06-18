<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_7_2_d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_7_2_d.h

## Purpose
`gfx_7_2_d.h` is the GFX_7_2 register-address map for the AMD GPU driver subtree. It contains preprocessor constants that bind symbolic register names, mostly `mm*` memory-mapped registers and `ix*` indexed/debug selectors, to the numeric offsets used by low-level register accessors. The file is data-only: it has a license block, an include guard, and 2,500+ `#define` entries, but no functions, structs, enums, or executable logic.

The header lets GFX 7-era driver code use stable symbolic names such as `mmCP_RB0_BASE`, `mmCP_HQD_ACTIVE`, `mmRLC_CNTL`, `mmSPI_SHADER_PGM_LO_PS`, `mmGDS_VMID0_SIZE`, and `ixSQ_WAVE_STATUS` instead of embedding raw register offsets at call sites. It is ASIC-generation-specific; adjacent headers such as `gfx_7_0_d.h`, `gfx_8_0_d.h`, and `gfx_8_1_d.h` carry similar names but may differ in offsets or register coverage.

## Important APIs, Types, And Functions
There are no C APIs or types in this file. The practical API is the macro namespace exposed to includers:

- `mmCB_*`, `mmDB_*`, `mmPA_*`, `mmVGT_*`, `mmIA_*`, and `mmWD_*` cover graphics pipeline color buffer, depth buffer, primitive assembly, scan conversion, vertex/geometry/tessellation, input assembler, and work distributor state.
- `mmCP_*`, `mmCPC_*`, `mmCPF_*`, `mmCPG_*`, and `mmCP_HQD_*` cover the command processor, rings, interrupts, indirect buffers, DMA, queue descriptors, MQD/HQD state, doorbells, write/read pointers, context control, and EOP/fence/status registers.
- `mmCOMPUTE_*` and `mmSPI_SHADER_*` define compute dispatch registers, shader program/TBA/TMA addresses, per-stage resource registers, and user data windows for PS, VS, GS, ES, HS, and LS stages.
- `mmRLC_*` defines run-list controller, power-gating, save/restore, firmware upload, SPM performance monitoring, load-balancing, scratch, and clock-count registers.
- `mmSQ_*`, `mmSQC_*`, `mmSPI_*`, `mmSX_*`, `mmTA_*`, `mmTD_*`, `mmTCP_*`, `mmTCC_*`, `mmTCA_*`, and `mmTCS_*` expose shader core, interpolation, export, texture, cache, and thread-trace/performance-counter registers.
- `mmGDS_*` defines global data share, VMID partitioning, GWS/OA resources, atomics, protection-fault, debug, and performance-counter registers.
- `mmGRBM_*`, `mmGB_*`, `mmRAS_*`, `mmCGTT_*`, `mmCGTS_*`, `mmDIDT_*`, and `mmGC_*` expose graphics register bus, tiling/backend topology, reliability signatures, clock-gating, thermal/current throttling, and global graphics configuration registers.
- `ixCLIPPER_*`, `ixPA_SC_*`, `ixSQ_*`, `ixGDS_*`, `ixVGT_*`, `ixIA_*`, `ixWD_*`, and `ixDIDT_*` are selector constants for indexed debug/register windows rather than normal directly-addressed MMIO registers.

Several names intentionally alias the same offset to preserve naming used by different driver generations or hardware blocks. Examples include `mmCP_RB0_BASE` and `mmCP_RB_BASE`, `mmCP_RING_PRIORITY_CNTS` and `mmCP_ME0_PIPE_PRIORITY_CNTS`, `mmCP_RINGID` and `mmCP_PIPEID`, `mmCP_ATOMIC_PREOP_LO` and `mmCP_ME_ATOMIC_PREOP_LO`, and multiple SQ instruction decode aliases mapped to `mmSQ_INST`.

## Control Flow
The header has no runtime control flow. Its compile-time flow is limited to `#ifndef GFX_7_2_D_H`, `#define GFX_7_2_D_H`, macro definitions, and the closing `#endif`.

Runtime control flow appears in includers. GFX 7 code passes these constants to register helpers such as `RREG32()` and `WREG32()` to program hardware during initialization, suspend/resume, queue management, command submission, power management, and debug collection. Representative paths include ring setup writing `mmCP_RB0_BASE`/`mmCP_RB0_BASE_HI`, MQD/HQD management reading and writing `mmCP_HQD_*`, RLC firmware and power-gating setup using `mmRLC_*`, GDS setup using `mmGDS_VMID*` entries, and draw/geometry setup writing `mmVGT_*`.

Because each macro expands to a literal offset, there is no validation layer in this file. Correctness depends on the including driver selecting this ASIC register map only for compatible hardware and combining it with the matching mask/shift headers and access method.

## State And Persistence
The header itself owns no memory and persists no state. It describes hardware state locations. Persistence and volatility belong to the GPU registers and firmware-visible buffers addressed by callers:

- Ring, IB, EOP, HQD, MQD, doorbell, VMID, GDS, shader, and scratch registers control hardware state that persists until reset, reprogramming, suspend, or power-gating transitions.
- Performance-counter, status, debug, and timestamp registers expose volatile hardware state and can change asynchronously with GPU execution.
- RLC save/restore registers such as `mmRLC_SAVE_AND_RESTORE_BASE`, `mmRLC_JUMP_TABLE_RESTORE`, and `mmRLC_GPM_SCRATCH_*` point the hardware at driver-allocated GPU memory used across power-gating or context save/restore operations.
- Fence, EOP, stream-out, counter, and CP DMA address registers cause hardware reads or writes to external GPU/CPU-visible memory when programmed by command processor paths.

## Dependencies And Integration Points
This file depends only on the C preprocessor. It is included by AMD driver components such as `amdgpu/cik.c`, `amdgpu/cik_sdma.c`, `amdgpu/gfx_v7_0.c` through shared GFX 7 register use, `amdgpu/amdgpu_amdkfd_gfx_v7.c`, legacy DPM code, BACO/powerplay code, and CI SMU manager code.

It integrates with:

- Register access macros and wrappers (`RREG32`, `WREG32`, indirect indexed access helpers, and debug dump helpers) that interpret these offsets against the device MMIO aperture or indexed register windows.
- Companion register mask/shift/default headers in the AMD `include/asic_reg` tree, which provide bitfield semantics for many of the offsets defined here.
- GFX 7 initialization and teardown paths that program CP rings, MEC/HQD queues, RLC firmware, power-gating, clock-gating, GDS partitioning, shader state, and render/compute pipeline defaults.
- KFD queue-management code, where `mmCP_HQD_*` offsets are used to locate, activate, drain, and dump compute queues.
- Power-management paths that use clock-gating, CGTT/CGTS, RLC, DIDT, and BACO-related registers.

## Risks And Edge Cases
- A wrong offset can produce severe device behavior: hangs, incorrect rendering or compute results, failed queue teardown, broken power management, memory corruption through CP DMA/EOP/GDS programming, or unhandled interrupts.
- The file has no type safety. Any macro can be passed to any register accessor unless the caller enforces the correct block, register window, index mode, and access ordering.
- Direct `mm*` offsets and indexed `ix*` selectors are easy to confuse. Indexed debug constants require the corresponding index/data path, not normal MMIO access.
- Aliased macro names are useful for compatibility but can hide semantic differences between hardware blocks or generations when code is ported.
- Register arrays are manually expanded (`CB_COLOR0..7`, viewports 0..15, `GDS_VMID0..15`, shader user data 0..15, SQ perf counters, etc.). Off-by-one loop bounds in callers can silently program unrelated registers.
- Some registers reference persistent GPU memory addresses, high/low address pairs, or shifted addresses. Callers must preserve alignment, address split, VMID, endian, and ordering requirements.
- The header is generation-specific. Mixing it with GFX 8+ SOC15 base-index headers or a different ASIC's mask/default header can compile while targeting the wrong register space.

## Test Signals
Useful signals are mostly integration and hardware-level because this header has no unit-testable behavior:

- Build coverage for GFX 7 AMDGPU, KFD, legacy DPM, and powerplay paths confirms all macro names still resolve.
- Boot/probe logs on compatible GFX_7_2 ASICs should show successful GPU initialization, firmware loading, ring tests, IRQ setup, and no register-access faults.
- Ring and queue tests should pass for graphics, compute, DMA, MQD/HQD activation/dequeue, doorbell write pointer updates, and fence/EOP completion.
- Suspend/resume and runtime power-management tests should cover RLC save/restore, clock gating, power gating, BACO transitions, and reinitialization after reset.
- Rendering and compute workloads should validate CB/DB/PA/VGT/SPI/SQ register programming through real command submission.
- GDS/KFD workloads should cover VMID partitioning, GWS/OA allocation, atomics, and queue preemption/drain paths.
- Debugfs or driver register dumps and performance counter reads can confirm expected offsets for `GRBM`, `CP`, `RLC`, `SQ`, `SPI`, `GDS`, `VGT`, and other blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_7_2_d.h -->
