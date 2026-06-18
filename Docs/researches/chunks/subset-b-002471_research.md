# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h lines 2468-4982

## Scope And Purpose

This chunk is a generated AMD GC 10.3.0 register-offset header segment. It contains C preprocessor constants for graphics-core MMIO register offsets and their SOC15 base-index selectors, not executable logic. The constants are consumed by AMDGPU and KFD code through `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and related helpers so driver code can address GC hardware blocks by symbolic register names rather than raw offsets.

The requested range starts in the tail of a PA/SC rasterization block, then covers 1,214 non-`_BASE_IDX` register names across shader execution, shader input, texture/cache, render backend, graphics VM hub, command processor, SPI arbitration/debug, and hardware queue descriptor blocks. Each real register macro is paired with a `<register>_BASE_IDX` macro, and every pair in this chunk uses base index `0`.

## Address Blocks Covered

The chunk is organized by generated `addressBlock` comments and hardware base-address comments:

- Initial PA/SC tail before the first visible block marker: binning, scan converter, primitive assembler, and sideband tuning registers such as `mmPA_SC_BINNER_*`, `mmPA_SC_ENHANCE*`, and `mmPA_PH_*`.
- `gc_sqdec`, base `0x8c00`: 74 SQ/SQC/LDS/SP registers for shader-queue configuration, shader memory bases, wave watchpoints, thread tracing, indirect SQ access, timestamps, loop-buffer counters, EDC counters, and SQC I-cache/D-cache UTCL0 control/status.
- `gc_shsdec`, base `0x9000`: 64 shader/SPI registers including pixel-shader wave limits, SPI config controls, PS CU enables, wavefront lifetime limit/status sets, LDS debugging, SPI barrier/window/debug controls, shader prefetch/priority controls, and compute user-data registers.
- `gc_tpdec`, base `0x9400`: 8 texture/TA/TD status and scratch/control registers.
- `gc_gdsdec`, base `0x9700`: 13 Global Data Share configuration, status, protection-fault, EDC, and DSM registers.
- `gc_rbdec`, base `0x9800`: 51 depth/color backend registers, including DB debug/stutter/cacheline/watermark controls, HTILE/status reporting, DB EDC, CB scratch/debug/performance/debug-index controls, and RMI-to-RB interconnect tuning.
- `gc_gceadec2`, `gc_gceadec3`, and `gc_gceadec`, bases `0x9c00`, `0x9dc0`, and `0xa800`: GCEA fabric/DRAM/client mapping, credits, probe, DSCM/DSM, router/latency, reserve, outstanding request, and debug counter controls.
- `gc_spipdec2`, base `0x9c80`: two SPI queue/event and export throttle controls.
- `gc_rmi_rmidec`, base `0x9e00`: 30 RMI interconnect, demux, UTCL1, XNACK, RMI2MCIF, PACE, and credit/status registers.
- `gc_dbgu_gfx_dbgudec`, base `0x9f00`: block marker only in this range; no register defines follow before the next block.
- `gc_pmmdec`, base `0x9f80`: GCR/PMM general command/status and PIO registers.
- `gc_utcl1dec`, base `0x9fa0`: UTCL1 global control, logging, invalidation-disable, target-disable, and status registers.
- `gc_gcvml2pfdec`, base `0xa070`: 38 GCVM L2 control, invalidate, protection-fault, dummy-page-fault, interrupt, latency, perf counter, debug, and CRD register offsets.
- `gc_gcvml2vcdec`, base `0xa170`: 220 per-VM-context register offsets. This block defines `mmGCVM_CONTEXT0_*` through `mmGCVM_CONTEXT15_*` control/page-table/protection/fault registers and the context-distance pattern used by VM programming code.
- `gc_gcvmsharedpfdec`, base `0xa500`: 25 shared VM northbridge, PCI aperture, top-of-DRAM, FB offset, system aperture default, steering, reset, low-power, AGP-mode, and exception-control registers.
- `gc_gcvmsharedvcdec`, base `0xa570`: 8 shared virtual-context registers for VRAM aperture base/top, AGP aperture, system aperture low/high, and `mmGCMC_VM_MX_L1_TLB_CNTL`.
- `gc_tcdec`, base `0xac00`: 6 TCP/TCI invalidate/status/EDC/control registers.
- `gc_shdec`, base `0xb000`: 261 shader program, shader user data, dispatch, streamout, LS/HS/ES/GS/VS/PS/CS resource, thread-management, and SQ performance/event counter registers.
- `gc_cppdec`, base `0xc080`: 248 command-processor registers covering CP queues, interrupts, AQL/SMM status, ring-buffer bases/pointers, MEC/ME/PFP/CE debug and microcode state, pipe priorities, VMID preemption/status, suspend/resume, DDID, graphics HQD/CE queues, DMA watchpoints, timestamps, UTCL1 status, soft reset, and CPC graphics control.
- `gc_spipdec`, base `0xc700`: 41 SPI arbitration, wave control, graphics-debug trap, compute queue reset, CU reservation, compute wavefront context save, and shader resource limit registers.
- `gc_cpphqddec`, base `0xc800`: the beginning of the generic CP HQD register block, from `mmCP_HPD_MES_ROQ_OFFSETS` through `mmCP_HQD_IQ_RPTR` in this chunk.

## Important APIs, Types, And Register Families

There are no functions, structs, or enums in this chunk. Its API surface is the macro namespace:

- `mm<NAME>` macros provide register offsets relative to the SOC15 IP-instance base selected by the corresponding base-index macro.
- `mm<NAME>_BASE_IDX` macros select the index into `adev->reg_offset[GC_HWIP][inst]`. In this chunk the value is consistently `0`, so all listed GC register offsets are resolved against GC base-index slot 0.
- The values are consumed by AMDGPU macros from `soc15_common.h`, for example `SOC15_REG_OFFSET(GC, 0, mmCP_HQD_ACTIVE)` expands to `adev->reg_offset[GC_HWIP][0][mmCP_HQD_ACTIVE_BASE_IDX] + mmCP_HQD_ACTIVE`.

Register families with high integration value in this chunk include:

- SQ/SPI shader controls: `mmSQ_CONFIG`, `mmSQC_CONFIG`, `mmLDS_CONFIG`, `mmSH_MEM_BASES`, `mmSP_CONFIG`, `mmSQ_THREAD_TRACE_*`, `mmSPI_CONFIG_*`, `mmSPI_SHADER_PGM_*`, `mmSPI_SHADER_USER_DATA_*`, `mmCOMPUTE_*`, and `mmSQ_PERFCOUNTER*`.
- VM hub and memory apertures: `mmGCVM_L2_*`, `mmGCVM_INVALIDATE_*`, `mmGCVM_CONTEXT<n>_*`, `mmGCMC_VM_FB_LOCATION_BASE`, `mmGCMC_VM_FB_LOCATION_TOP`, `mmGCMC_VM_AGP_*`, and `mmGCMC_VM_SYSTEM_APERTURE_*`.
- Command-processor queue management: `mmCP_RB*`, `mmCP_PQ_*`, `mmCP_MEC_*`, `mmCP_ME*`, `mmCP_CE*`, `mmCP_GFX_HQD_*`, `mmCP_GFX_HQD_CE_*`, `mmCP_HQD_*`, and `mmCP_MQD_*`.
- Debug/performance/status points: `mmSQ_WATCH*`, `mmSQ_THREAD_TRACE_*`, `mmSQ_PERFCOUNTER*`, `mmGRBM_*`, `mmRMI_*STATUS*`, `mmDB_DEBUG*`, `mmCB_PERFCOUNTER*`, `mmCP_DMA_WATCH*`, `mmSPI_GDBG_*`, and EDC counters across SQ, SPI, GDS, DB, CB, TCP, and CP blocks.
- Reset, preemption, and suspension points: `mmCP_VMID_PREEMPT`, `mmCP_SUSPEND_*`, `mmCPC_SUSPEND_*`, `mmSPI_COMPUTE_QUEUE_RESET`, `mmCP_HQD_DEQUEUE_REQUEST`, and `mmCP_SOFT_RESET_CNTL`.

## Control Flow And Data Flow

The header itself has no runtime control flow. The effective control flow appears in call sites that combine these offsets with SOC15 access helpers:

- Direct register programming calls use `WREG32_SOC15(GC, inst, mmREGISTER, value)` or `WREG32(SOC15_REG_OFFSET(GC, inst, mmREGISTER), value)` to write device MMIO registers.
- Status and polling paths use `RREG32_SOC15` with the same symbolic offsets. KFD queue code reads `mmCP_HQD_ACTIVE`, `mmCP_HQD_PQ_BASE`, and `mmCP_HQD_PQ_BASE_HI` to determine whether a hardware queue descriptor is occupied, then writes `mmCP_HQD_DEQUEUE_REQUEST` and polls `mmCP_HQD_ACTIVE` during queue destruction.
- VM hub setup uses the GCVM/GCMC offsets to program VRAM apertures, AGP/system apertures, per-VMID page-table bases, start/end ranges, invalidation engines, L2 controls, and fault reporting. `gfxhub_v2_1_get_fb_location` reads `mmGCMC_VM_FB_LOCATION_BASE`; SR-IOV VF setup may write `mmGCMC_VM_FB_LOCATION_BASE` and `mmGCMC_VM_FB_LOCATION_TOP`.
- Shader and graphics initialization, golden settings, debug, tracing, and performance-counter paths use SQ/SPI/SH/RB/CP registers to configure queues, dispatch behavior, user data, counters, ring pointers, and interrupt/debug capture surfaces.

Some register runs are intentionally dense and patterned. `mmGCVM_CONTEXT0_*` through `mmGCVM_CONTEXT15_*` and `mmSPI_SHADER_USER_DATA_*` are addressed both by explicit names and by offset arithmetic in call sites. Their numeric spacing is therefore part of the ABI between generated headers and driver code.

## State And Persistence Behavior

The macros do not store state. They name hardware stateful registers whose values live in GPU MMIO space and are changed by the kernel driver, firmware, rings, and hardware engines.

Persistent or semipersistent hardware state represented by this chunk includes:

- VM aperture and context state: framebuffer base/top, AGP and system aperture bounds, per-VMID page-table bases and protection-fault defaults, L1/L2 TLB/cache settings, and invalidate-engine configuration.
- Queue state: MQD base addresses, HQD active bits, VMID bindings, pipe/queue priority, PQ/IB/EOP bases, read/write pointers, doorbell control, dequeue requests, and context-save controls.
- Shader and pipeline state: shader program base/resource registers, user-data registers, streamout controls, compute dimensions, CU reservations, wave limits, and dispatch/debug controls.
- Runtime observability state: performance counter select/value registers, EDC counters, watchpoints, thread-trace buffers/write pointers/status, protection-fault status, DMA watchpoint status, and CP/SPI/SQ/DB/RMI status registers.

Because these registers sit in hardware, initialization order and reset behavior matter. Driver save/restore, suspend/resume, GPU reset, SR-IOV VF initialization, queue preemption, and GART enable/disable code must write consistent register sets and avoid leaving stale VM, doorbell, or queue-pointer state active.

## Dependencies And Integration Points

This file is part of the AMDGPU ASIC register include tree for GC 10.3.0. It is normally included beside matching generated headers for bit fields, masks, shifts, and defaults, especially files such as `gc_10_3_0_sh_mask.h` and related GC 10.x default headers.

Primary integration points are:

- AMDGPU SOC15 register helpers in `drivers/gpu/drm/amd/amdgpu/soc15_common.h`, where `<register>_BASE_IDX` is used to select the MMIO base and `<register>` is added as the register offset.
- GFX hub code such as `gfxhub_v2_1.c`, which programs GCMC/GCVM registers for VM aperture, page-table, invalidation, cache/TLB, and protection-fault handling.
- KFD and compute queue code such as `amdgpu_amdkfd_gfx_v10_3.c`, which loads, inspects, and destroys CP HQDs using `mmCP_HQD_*`, `mmCP_MQD_*`, `mmSPI_COMPUTE_QUEUE_RESET`, and related command-processor offsets.
- GFX generation setup and debugging code, including golden register settings, shader/SQ/SPI tuning, CP ring setup, performance counters, thread trace, and interrupt/status handling.
- Firmware, microcode, and command ring protocols that expect these register offsets to match the GC 10.3.0 hardware specification.

## Risks And Edge Cases

- Offset drift is high impact. A wrong numeric value can redirect a read or write to a different hardware register, causing hangs, incorrect VM mappings, queue corruption, bad interrupts, or silent performance/debug failures.
- Patterned context registers are easy to misuse. VM setup relies on consistent spacing between `mmGCVM_CONTEXT<n>_*` registers and on the correct offset distance when using `WREG32_SOC15_OFFSET`.
- Aliased names must remain intentional. The chunk contains same-offset aliases such as `mmCP_HPD_MES_ROQ_OFFSETS` and `mmCP_HPD_ROQ_OFFSETS`, `mmCP_HQD_DMA_OFFLOAD` and `mmCP_HQD_OFFLOAD`, `mmCP_RB0_ACTIVE` and `mmCP_RB_ACTIVE`, and several phase aliases for `mmCPG_RCIU_CAM_DATA`. Consumers may use either name depending on generation or feature context.
- Some duplicate-looking definitions can be surprising. For example, `mmSQ_WREXEC_EXEC_HI` and `mmSQ_WREXEC_EXEC_LO` both map to `0x1151` in this generated chunk, so code must rely on the hardware spec and matching field-mask header before assuming a distinct low/high register pair.
- Register access often has side effects. Status clears, invalidate controls, queue dequeue requests, reset controls, perf counter latches, and debug/trace registers can change hardware state when read or written; tests should avoid treating all offsets as passive metadata.
- Base-index uniformity is an assumption in this chunk. If future ASIC generations use different base-index values, call sites that hard-code or infer base selection outside the generated macro pairs would break.
- These constants are architecture-specific. Reusing GC 10.3.0 offsets with GC 10.1, GC 9.x, or newer GC blocks can compile but program the wrong hardware addresses.

## Test Signals

Useful validation for this chunk is mostly integration and hardware bring-up oriented:

- Compile coverage from AMDGPU/KFD objects that include `gc_10_3_0_offset.h`, proving all referenced macros and `_BASE_IDX` pairs exist.
- Static consistency checks between offset, mask/shift, and default headers for GC 10.3.0, especially for same-name register families and generated aliases.
- Boot and probe smoke tests on GC 10.3.0 hardware or emulation, verifying golden register programming, GFX ring init, compute ring init, KFD queue creation/destruction, and GPU reset paths.
- VM/GART tests that exercise `gfxhub_v2_1` aperture setup, page-table programming, invalidation, protection-fault reporting, and SR-IOV VF framebuffer-location programming.
- KFD tests that create compute queues, map/unmap HQDs, trigger queue preemption/reset/save paths, and validate `mmCP_HQD_ACTIVE` polling reaches the expected state.
- Graphics and compute workload tests that cover shader program/user-data registers, CU reservations, wave limits, TCP/TCI cache invalidation, render backend state, and command-processor ring pointers.
- Debug and observability tests that enable SQ thread trace, SPI debug traps, CP DMA watchpoints, and perf counters, then confirm counters/status registers change coherently and do not hang the engine.
