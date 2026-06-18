# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h lines 7414-9893

## Scope

This chunk is a generated AMD GC 12.1.0 register-offset header segment. It contains C preprocessor constants only: `reg*` macros name graphics-core hardware register offsets, and paired `reg*_BASE_IDX` macros identify the SOC15 base-index slot used by AMDGPU register-address helpers.

The requested range contains 1,200 register-offset macros and 1,200 `_BASE_IDX` macros. The range starts on `regGE_SE_CNTL_STATUS_BASE_IDX`, whose offset macro is immediately before this chunk, and ends on `regWGS_COMPUTE_PIPELINESTAT_ENABLE`, whose `_BASE_IDX` macro is immediately after this chunk. Those artificial chunk boundaries should be reconciled when the final per-file document is assembled.

Although this source tree is rooted under a local `ceph-client` mirror, this file is AMDGPU DRM graphics metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

`gc_12_1_0_offset.h` supplies named MMIO/register offsets for AMD GC 12.1.0 graphics hardware. Driver code includes this header so ASIC-specific paths can address registers by stable symbolic names instead of copying numeric offsets into source files.

This chunk covers the shader engine and user-config/control portions of the GC register map:

- Tail GE/PA debug and safety controls preceding the SQ decoder block.
- SQ/SQC/SQG shader-queue configuration, debug, watchpoint, timeout, UTCL0 retry, PIT/WS, and indirect-index/data registers.
- SX and SPI shader processor interface debug, CU mask, wave lifetime, shader program, user-data, accumulator, arbiter, context-save, queue-reset, and DIDT control registers.
- Texture/depth/render/backend control blocks: TD, TA, DB, CB, GB, and RMI debug/status/arbitration/cache/FIFO/configuration registers.
- UTCL1, TCP, and PF-only TCP registers for L1 translation/cache behavior, invalidation, XNACK/retry handling, hashing masks, credit, thrashing, congestion, and watchpoints.
- The large `gfxdec0` user/context register space containing DB depth/stencil state, PA viewport/scissor/clip/rasterization state, SPI pixel-shader input state, SX blend optimization, CB render-target state, VGT/GE/NGG controls, HiZ/HiS controls, and multisample sample-location state.
- PF/VF and PF-only/second PF-only windows for PA/SQ/SPI/UTCL1/TCP controls, including virtualization-visible debug/trap/runtime controls and privileged resource-reserve controls.
- GFXU user-config registers for tessellation/offchip/ring resources, trap-screen controls, thread-trace userdata, SQC caches, occlusion counters, SPI attribute rings, and compute workgroup scheduler controls.
- The beginning of the WGS compute-dispatch register sequence for dispatch initiator, dimensions, starts, thread counts, and pipeline-stat enable.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, callbacks, or executable branches in this range. The public interface is the generated macro contract:

- `regNAME` gives the encoded register offset within the selected GC address space.
- `regNAME_BASE_IDX` gives the SOC15 base-index selector for that offset. In this chunk, 402 base-index entries are `0` and 798 are `1`.
- Address-block comments identify the generated hardware block and base address, such as `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_sqdec` at `0x8c00`, `gfxdec0` at `0x28000`, `gfxudec` at `0x30000`, and `comp_wgsdec` at `0x31a00`.
- Consumers combine these macros with AMDGPU register helpers such as SOC15 `RREG32*`/`WREG32*` paths, field helpers, indirect register access, command-stream register writes, and ASIC-specific save/restore code.
- Bitfield layouts are intentionally not present here; they are supplied by the companion GC 12.1.0 shift/mask header (`gc_12_1_0_sh_mask.h`) and by higher-level driver sequences.

Important macro families in this chunk include:

- `SQ_*`, `SQC_*`, and `SQG_*`: shader queue configuration, GL1/UTCL0 status, wave/prioritization controls, performance snapshot, interrupt masking, watch registers, timeout status, SQC PIT/WSM controls, and indirect index/data commands.
- `SPI_*`: shader processor interface controls spanning debug, CU masks, wave lifetime, scratch status, `SPI_SHADER_PGM_*`, `SPI_SHADER_USER_DATA_*`, `SPI_SHADER_USER_ACCUM_*`, arbiter percentages, compute queue reset, context-save, DIDT, resource reserve, attribute ring, and group-launch controls.
- `DB_*`: depth/stencil render control, Z/stencil surface bases, HTILE, depth bounds, shader/depth/stencil controls, occlusion counters, debug/status/FIFO/watermark/arbiter controls, and summarizer state.
- `PA_*` and `SC_*`: viewport, scissor, cliprect, user clip-plane, raster, VRS, binner, HiZ/HiS, anti-aliasing, conservative rasterization, point/line/stipple, polygon offset, trap-screen, and screen-extent controls.
- `CB_*`: blend constants, target masks, shader masks, color-control registers, per-render-target color base/view/attrib/FDCC/info state, memory info, cache control, and hardware/memory-arbiter controls.
- `TA_*`, `TD_*`, `TCP_*`, `TXA_*`, `UTCL1_*`, and `GCRD_*`: texture address/data and texture cache path control, invalidation/status/credits, set-hash masks, UTCL1 identity/hash/status, target-disable and credit-safe registers, XNACK/retry timers, and TCP watchpoints.
- `RMI_*`, `GB_*`, and `CC_*`: render backend/raster-memory-interface routing, scoreboard, crossbar, UTC/UTCL1, backend map/address configuration, GPU ID, backend disable, and redundancy controls.
- `VGT_*`, `GE_*`, and `WGS_*`: tessellation/offchip/ring resources, NGG/output controls, and compute dispatch/workgroup scheduler programming.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU/KFD consumers:

1. The active ASIC path includes GC 12.1.0 offset and shift/mask headers.
2. Driver code selects a symbolic `reg*` macro and the matching `_BASE_IDX` through SOC15-aware helpers.
3. For field-level programming, code combines the offset from this file with masks/shifts from `gc_12_1_0_sh_mask.h`.
4. The register is read, written, polled, or emitted into a command stream by higher-level graphics, compute, VM, debug, reset, or power-management code.
5. The higher-level sequence supplies ordering, privilege, polling, reset, and side-effect rules; this generated header only supplies addresses.

For shader setup, command streams and context state program SPI shader program addresses/resources, user-data slots, PS input controls, accumulators, and SQ/SQC/SQG controls. For graphics render state, context programming writes DB, PA/SC, CB, SX, GE, and VGT registers for depth/stencil, viewport/scissor/raster, blend/color target, NGG, tessellation, sample, and binner behavior. For cache/translation paths, driver code uses TCP/UTCL1/RMI/GCRD offsets for invalidation, retry, XNACK, identity mode, hash masks, target disable, and status/error handling.

## State And Persistence Behavior

The macros themselves hold no runtime state and persist nothing. They describe hardware-visible state:

- SQ/SQC/SQG and SPI registers affect shader scheduling, trap/watch behavior, interrupt delivery, shader program resources, scratch/user-data programming, wave lifetime limits, and compute context-save/reset flows.
- DB/CB/PA/SC/SX/VGT/GE registers are graphics context state. They are programmed by command streams or context setup and may be saved/restored, shadowed, reset, or rebuilt depending on the GPU mode and ring/context ownership.
- TCP/UTCL1/RMI/GCRD registers expose cache and translation behavior: invalidation, XNACK retry, hashing, identity mode, credits, target disable, status, and watchdog/debug state. These values can be reset-sensitive and may need reprogramming after GPU reset, suspend/resume, or virtualization transitions.
- PF/VF, PF-only, and PF-only2 blocks partition what can be accessed from virtualized or privileged contexts. The `_BASE_IDX` value is part of this partitioning; an otherwise correct offset can reach the wrong aperture if the base index is wrong.
- GFXU and WGS user-config state includes ring base/size registers, offchip/tessellation parameters, trap-screen state, occlusion counters, attribute rings, thread-trace userdata, SQC cache controls, and compute dispatch/workgroup scheduler setup.

This offset header does not encode whether a register is read-only, write-only, write-one-to-clear, clear-on-read, privileged, indexed, broadcast, shadowed, saved/restored, or safe for read-modify-write. Those semantics must come from the hardware specification and the AMDGPU code that uses the macros.

## Dependencies And Integration Points

This file depends on consistency with AMD's authoritative GC 12.1.0 register database and companion generated headers in the same directory, especially `gc_12_1_0_sh_mask.h`.

Observed include users in this source tree include GC 12.1.0 graphics, memory hub, MES, SDMA, IMU, SOC, and KFD paths such as `gfx_v12_1.c`, `gfxhub_v12_1.c`, `mes_v12_1.c`, `amdgpu_amdkfd_gfx_v12_1.c`, `imu_v12_1.c`, `sdma_v7_1.c`, and `soc_v1_0.c`.

Primary integration points are:

- AMDGPU SOC15 register helpers, which combine register offsets and `_BASE_IDX` selectors into MMIO addresses for the current GC instance/XCC.
- Graphics pipeline state setup and command submission, which use DB/CB/PA/SC/SX/VGT/GE/SPI offsets for render target, depth/stencil, viewport, scissor, blend, sample, shader, NGG, and tessellation state.
- Shader program and debug paths, which use SQ/SQC/SQG/SPI offsets for program resource registers, user data, traps, watchpoints, wave controls, indirect SQ access, and status polling.
- KFD and compute scheduling paths, which care about compute queue reset, context-save, wavefront context status, WGS dispatch registers, CU masks, resource reservation, and TCP/SQ/SPI watchpoint facilities.
- VM/cache/translation paths, which use TCP/UTCL1/RMI/GCRD offsets for invalidation, retry/XNACK behavior, hashing, target disable, identity mapping, and status.
- SR-IOV/virtualization paths, where PF/VF and PF-only block boundaries determine which software component may touch PA/SQ/SPI/UTCL1/TCP controls.
- Performance, diagnostics, and recovery paths that read status/debug/FIFO/watermark/occlusion/thread-trace counters or reinitialize state after GPU reset.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong numeric offset or base index compiles cleanly but can target the wrong hardware register.
- The chunk boundaries are artificial. `regGE_SE_CNTL_STATUS_BASE_IDX` lacks its offset macro inside the chunk, and `regWGS_COMPUTE_PIPELINESTAT_ENABLE` lacks its `_BASE_IDX` inside the chunk.
- `BASE_IDX` mismatches are as dangerous as offset mismatches because the same encoded offset can refer to a different physical aperture under SOC15 helpers.
- Large repeated families are copy-sensitive: viewport/scissor registers 0-15, user clip planes, PS input controls 0-31, shader user-data slots 0-31, CB color targets 0-7, TCP hash masks, watchpoint slots 0-3, SPI resource reserve entries 0-15, occlusion counters 0-3, thread-trace userdata 0-7, and WGS XYZ dimensions/starts/thread counts must preserve exact naming and stride.
- Shader program/resource and user-data offsets are execution-critical. A single bad offset can produce shader hangs, wrong descriptors, trap/debug failures, broken context save/restore, or missed wave control.
- DB/CB/PA/SC/SX/VGT/GE offsets are render-correctness sensitive. Errors can manifest as corrupt depth/stencil, wrong viewports or scissors, bad MSAA/VRS behavior, broken blending, invalid render target programming, missing occlusion counts, or GPU hangs during draws.
- TCP/UTCL1/RMI/GCRD mistakes can cause stale translations, invalid cache invalidation, XNACK retry failures, incorrect identity mappings, or backpressure/deadlock symptoms rather than immediate compile failures.
- PF/VF and PF-only register placement is security- and reliability-sensitive under virtualization. Programming a privileged-only register from the wrong path can break isolation or reset recovery.
- Status/debug registers may have side effects not represented here. Consumers must not infer read/write safety from the existence of an offset macro.

## Test Signals

Useful validation should combine generated-data checks, build coverage, and hardware/runtime testing:

- Build AMDGPU with GC 12.1.0 support and KFD enabled. Missing or renamed macros should surface in ASIC-specific include users.
- Mechanically compare this line range against the authoritative GC 12.1.0 register database, checking both offset values and `_BASE_IDX` values.
- Cross-check repeated families for count and stride consistency: SPI shader user-data slots, PS input controls, PA viewport/scissor state, CB color target blocks, TCP hash masks, watchpoint slots, resource reserve entries, thread-trace userdata, occlusion counters, and WGS XYZ registers.
- Verify that the split boundary macros are completed by adjacent chunks during final reconciliation.
- Run graphics render tests that stress depth/stencil, viewport/scissor, cliprects, VRS, MSAA sample locations, blending, color targets, HiZ/HiS, NGG, tessellation, and occlusion queries. Relevant signals include correct pixels, no CP/GC hangs, and plausible occlusion counter values.
- Run shader and debug workloads that exercise PS/GS/HS/LS program resources, user data, accumulators, traps, wave watchpoints, SQ indirect access, and thread trace. Watch for shader faults, invalid trap behavior, and unexpected SQ/SPI status.
- Run KFD compute queue, preemption/context-save, queue reset, and multi-process workloads. Watch for stuck waves, context-save timeouts, broken CU masking/resource reservation, and bad WGS dispatch dimensions.
- Run VM/cache stress with frequent memory mappings, invalidations, XNACK/retry activity, and suspend/resume or GPU reset. Relevant signals include no stale data, no retry storms, clean reset recovery, and sane TCP/UTCL1/RMI status.
- Exercise SR-IOV/PF-VF environments where available to validate PF/VF and PF-only register access boundaries.

## Cross-Chunk Notes

The previous chunk owns the offset macro for `regGE_SE_CNTL_STATUS`; this chunk begins with its `_BASE_IDX`, then covers GE/PA tail registers, SQ/SQC/SQG, SX/SPI, TD/TA/DB/CB/RMI/UTCL1/shader program/TCP/gfxdec0/PF-VF/PF-only/GFXU groups. The next chunk should provide `regWGS_COMPUTE_PIPELINESTAT_ENABLE_BASE_IDX` and continue the WGS compute-dispatch register sequence.
