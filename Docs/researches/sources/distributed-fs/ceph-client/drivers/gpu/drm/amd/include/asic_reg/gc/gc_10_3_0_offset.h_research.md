# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002470`: lines 1-2467, `Docs/researches/chunks/subset-b-002470_research.md`
- `subset-b-002471`: lines 2468-4982, `Docs/researches/chunks/subset-b-002471_research.md`
- `subset-b-002472`: lines 4983-7445, `Docs/researches/chunks/subset-b-002472_research.md`
- `subset-b-002473`: lines 7446-9968, `Docs/researches/chunks/subset-b-002473_research.md`
- `subset-b-002474`: lines 9969-12437, `Docs/researches/chunks/subset-b-002474_research.md`
- `subset-b-002475`: lines 12438-13625, `Docs/researches/chunks/subset-b-002475_research.md`

## Chunk Research

### subset-b-002470: lines 1-2467

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h lines 1-2467

## Scope

This chunk is the opening segment of the generated AMD GC 10.3.0 register-offset header. It covers lines 1 through 2467 and includes the license, include guard, top-level SQ debug offsets, complete `gc_sdma0_sdma0dec` and `gc_sdma1_sdma1dec` register blocks, complete `gc_grbmdec` and `gc_cpdec` blocks, and the beginning of `gc_padec`.

The range contains 2,425 `#define` entries: 1 include-guard define, 1,212 `mm*` register-offset macros, and 1,212 matching `*_BASE_IDX` macros. It is declarative only. There are no C functions, structs, enums, branches, loops, locks, allocations, or software-owned persistent variables in this slice.

## Purpose

`gc_10_3_0_offset.h` supplies symbolic dword offsets for AMD GPU Graphics Core 10.3.0 MMIO registers. Driver code pairs these offsets with register access helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_IP`, `WREG32_SOC15_IP`, `RREG32_SDMA`, and `WREG32_SDMA` so GC 10.3.0 hardware can be programmed without embedding raw numeric addresses in handwritten code.

This chunk covers the early GC register namespace:

- SQ debug status/control registers at the top of the file, including `mmSQ_DEBUG_STS_GLOBAL`, `mmSQ_DEBUG_STS_GLOBAL2`, and `mmSQ_DEBUG`.
- SDMA0 at address block `gc_sdma0_sdma0dec`, base address `0x4980`, with offsets from `mmSDMA0_DEC_START` through `mmSDMA0_RLC7_MIDCMD_CNTL`.
- SDMA1 at address block `gc_sdma1_sdma1dec`, base address `0x6180`, with the same queue/control structure shifted to the `mmSDMA1_*` namespace.
- GRBM at address block `gc_grbmdec`, base address `0x8000`, with graphics register bus manager status, reset, clock, trap, scratch, fence, and violation registers.
- CP at address block `gc_cpdec`, base address `0x8200`, with command processor status, busy/stall counters, instruction/header dumps, queue thresholds, ring read pointers, ROQ/STQ/MEQ availability, command index/data, and privilege violation offsets.
- The start of PA at address block `gc_padec`, base address `0x8800`, covering VGT/WD/IA/GE/CC/GC user configuration and early PA/SC trap/binning control offsets through `mmPA_SC_BINNER_EVENT_CNTL_2`.

## Exported API Surface

There are no callable APIs or local types. The public surface is the generated preprocessor macro namespace:

- Each register is exported as `mm<REGISTER_NAME>` with a dword offset relative to the SOC15 GC register space or to the relevant address-block instance selected by the register helper layer.
- Each register has a paired `mm<REGISTER_NAME>_BASE_IDX`, and all base indices in this chunk are `0`. Consumers pass these constants to SOC15 register-entry and register-access macros.
- SDMA queue windows repeat a standard register set for `GFX`, `PAGE`, and `RLC0` through `RLC7`: ring control/base/read pointer/write pointer, pointer polling, indirect buffer control/base/size/offset, skip and context status, doorbell, watermark, context save area address, preempt, AQL, minor pointer update, and mid-command data/control registers.
- Engine-wide SDMA registers include power/clock/control/status, global timestamp, GB address configuration, UTCL1 controls/status/invalidation/XNACK, TLBI/GCR, tiling, interrupt, error, scratch, queue reset, physical-address logging, EDC, atomic, and public dummy/debug registers.
- GRBM exports status and control points such as `mmGRBM_STATUS`, `mmGRBM_STATUS2`, `mmGRBM_STATUS3`, `mmGRBM_STATUS_SE0` through `SE3`, `mmGRBM_SOFT_RESET`, `mmGRBM_GFX_CLKEN_CNTL`, `mmGRBM_GFX_CNTL`, `mmGRBM_INT_CNTL`, trap address/data masks, scratch registers, and `mmVIOLATION_DATA_ASYNC_VF_PROG`.
- CP exports command processor diagnostic and scheduling offsets such as `mmCP_CPC_STATUS`, `mmCP_CPF_STATUS`, `mmCP_BUSY_STAT`, `mmCP_STAT`, `mmCP_*_HEADER_DUMP`, `mmCP_*_INSTR_PNTR`, `mmCP_MEC_CNTL`, `mmCP_ME_CNTL`, `mmCP_RB{0,1,2}_RPTR`, `mmCP_ROQ*_THRESHOLDS`, `mmCP_STQ_*`, `mmCP_MEQ_*`, `mmCP_CMD_INDEX`, `mmCP_CMD_DATA`, and `mmCP_PRIV_VIOLATION_ADDR`.
- PA-side macros in this chunk include `mmVGT_CACHE_INVALIDATION`, ring-size and tessellation memory offsets, VGT/WD/IA UTCL1 and status registers, shader-array configuration and user override registers, primitive configuration, DMA primitive/control registers, and early PA CL/SU/SC control registers.

## Control Flow And State Behavior

This header has no software control flow. Runtime behavior is created by included driver code that treats these constants as hardware register addresses.

The visible register families describe several hardware state machines:

- SDMA engine lifecycle: `PG`, `POWER`, `CLK`, `CNTL`, `FREEZE`, phase quantum, queue reset, status, interrupt, and clock-gating offsets are used by driver paths that start, stop, reset, power gate, debug, and recover SDMA engines.
- SDMA queue lifecycle: each queue window exposes ring base/size, read and write pointers, read-pointer writeback address, write-pointer polling, doorbell, VM/context status, IB state, preempt state, CSA address, AQL controls, and mid-command save/restore registers. Driver code programs these registers before enabling queues and reads status/pointers during interrupt, hang, reset, and recovery handling.
- Translation and memory state: SDMA UTCL1, XNACK, invalidate, TLBI/GCR, tiling, GB address configuration, physical-address logging, and hole address registers connect SDMA command execution to GPU virtual memory, memory tiling, and fault diagnostics.
- GRBM state: GRBM status registers are used to observe graphics/compute block idleness and per-shader-engine activity; soft reset and clock enable registers affect global graphics-block lifecycle; trap and scratch registers support diagnostics and firmware/driver coordination.
- CP state: command processor status/busy/stall, queue threshold, ROQ/STQ/MEQ availability, ring read pointer, header dump, instruction pointer, and command index/data registers expose command submission front-end progress and debugging state.
- PA/VGT/WD/IA/GE state: early PA block offsets control cache invalidation, geometry/tessellation ring sizing, shader-array enablement/user masking, primitive setup, vertex DMA, UTCL1 status, and rasterizer/scan-converter trap/binning controls.

No software state is persisted in this file. The hardware registers named here persist according to ASIC reset, power-gating, firmware, SR-IOV, suspend/resume, and driver reinitialization behavior. In consumer code, selected values are mirrored in structures such as `amdgpu_ring`, SDMA instance state, KFD queue/MQD state, and golden-register tables, but this header only defines the numeric addresses used to reach the hardware.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. The semantic dependencies are AMD's generated GC 10.3.0 register database and the companion generated headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h` for bit shifts and masks used with these offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_default.h` for reset/default values corresponding to many registers in this offset namespace.

Direct include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c`, which uses GC 10.3.0 SDMA offsets and shift/mask macros to initialize, enable, halt, resume, and debug SDMA rings.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.c`, which includes the offset header for GC 10.3.0 graphics hub setup and polling, including GRBM status integration.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c`, which exposes GC 10.3.0 register offsets to KFD for compute/queue integration.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c`, which includes the header from the SMU power-management side for Vangogh-era GC register references.

The broader call sites found by register-name search include `gfx_v10_0.c` debug/regdump and idle-wait paths for `mmGRBM_STATUS*` and `mmCP_RB0_RPTR`, `sdma_v5_2.c` for `mmSDMA0_GFX_RB_CNTL`, and `gfxhub_v2_1.c` polling of `mmGRBM_STATUS2`. These integration points rely on the offsets being exactly aligned with the ASIC generation selected by the include path.

## Risks

- Generated-header drift is the primary risk. A wrong offset can make a correct-looking `RREG32` or `WREG32` access touch a different hardware register, which can cause hangs, data corruption, missed interrupts, or unrecoverable GPU reset paths.
- The SDMA0 and SDMA1 blocks are highly repetitive and separated by a fixed offset pattern. A one-register shift, missing register, or wrong SDMA1 base can create engine-specific failures that only occur on multi-SDMA workloads.
- Queue windows are repetitive across `GFX`, `PAGE`, and `RLC0` through `RLC7`. Incorrect offsets for ring base, pointers, doorbells, IB state, CSA address, AQL, preempt, or mid-command registers can break queue bring-up, KFD queue scheduling, suspend/resume, preemption, or reset recovery.
- Status/control names are exported with the same macro shape. This header does not encode read-only, write-one-to-clear, sticky, privileged, VF/PF-owned, or reset-sensitive semantics; those rules must come from the register spec and calling code.
- SDMA translation-related offsets are connected to VM and fault behavior. Wrong UTCL1, XNACK, TLBI/GCR, tiling, or physical-address logging offsets can leave stale translations, hide page faults, or mislead diagnostics.
- GRBM and CP offsets are central to idle polling and hang diagnosis. Incorrect `mmGRBM_STATUS*`, `mmCP_BUSY_STAT`, queue availability, or instruction-pointer offsets can make the driver believe the GPU is idle or hung incorrectly.
- PA/VGT/WD/IA/GE offsets in this chunk are only the beginning of a larger PA register block. Merge-time analysis should not treat missing later PA registers as omissions in this chunk.
- The file is generated and shared by graphics, compute, VM, SDMA, KFD, and PM paths. Local changes to satisfy one subsystem can silently regress another because the macro namespace has no type checking.

## Test Signals

Useful validation is mostly build-time, generation-time, and hardware-integration oriented:

- Compile or preprocess the GC 10.3.0 include users: `sdma_v5_2.c`, `gfxhub_v2_1.c`, `amdgpu_amdkfd_gfx_v10_3.c`, and `vangogh_ppt.c`.
- Static generated-header checks that every visible `mm*` register offset in this chunk has a matching `_BASE_IDX`, that all base indices remain `0` for this address-space view, and that the include guard closes in a later chunk of the full file.
- Cross-check the register names in this offset header against `gc_10_3_0_sh_mask.h` and `gc_10_3_0_default.h`, especially for high-risk offsets such as `mmSDMA0_GFX_RB_CNTL`, `mmSDMA1_GFX_RB_CNTL`, `mmGRBM_STATUS`, `mmGRBM_STATUS2`, `mmCP_RB0_RPTR`, and `mmVGT_CACHE_INVALIDATION`.
- SDMA runtime tests on GC 10.3.0-class hardware: ring initialization, command submission, fences, IB execution, traps, page queue operation, preemption, suspend/resume, GPU reset, and multi-engine SDMA0/SDMA1 workloads.
- KFD compute tests that create, load, preempt, restore, and destroy SDMA queues across RLC queue windows while validating doorbells, read/write pointers, VMIDs, and context idle/status behavior.
- Graphics idle/hang tests that exercise GRBM/CP status polling, command processor debug dumps, queue availability counters, and reset paths.
- VM/fault diagnostics that exercise SDMA UTCL1 invalidation/XNACK/TLBI paths, address logging, interrupt status, and physical-address reporting.
- PA/VGT bring-up and rendering tests that cover cache invalidation, primitive setup, shader-array disable/user masks, tessellation/geometry ring sizing, and scan-converter/binning control paths.

## Chunk Notes For Merge

This document intentionally covers only lines 1-2467 of `gc_10_3_0_offset.h`. Later chunks should continue the `gc_padec` register block after `mmPA_SC_BINNER_EVENT_CNTL_2`, cover the remainder of the generated GC 10.3.0 offset namespace, and eventually close the include guard. The final per-file report should treat the whole source as a generated ASIC register address map for AMD GC 10.3.0 hardware rather than handwritten executable driver logic.

### subset-b-002471: lines 2468-4982

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

### subset-b-002472: lines 4983-7445

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h lines 4983-7445

## Scope

This chunk is a generated AMD GPU GC 10.3.0 register-offset header slice. It contains 2,435 `#define` lines in the requested range: 1,217 visible register-offset macros plus 1,218 `_BASE_IDX` macros. The extra base-index macro is the first line of the chunk, `mmCP_HQD_IQ_RPTR_BASE_IDX`, whose matching offset definition is immediately before the chunk boundary.

The range starts inside the `gc_cpphqddec` queue descriptor block, then covers `gc_didtdec`, `gc_gccacdec`, `gc_tcpdec`, `gc_gdspdec`, `gc_gfxdec0`, `gc_gfxudec`, and the beginning of `gc_cprs64dec`. It ends at `mmCP_MES_GP5_LO_BASE_IDX`, so the MES general-purpose register sequence continues in a later chunk.

This file is declarative hardware metadata. There are no C functions, structs, enums, branches, loops, allocations, locks, or direct MMIO reads/writes in this range.

## Purpose

`gc_10_3_0_offset.h` gives AMDGPU code symbolic register numbers for the GC 10.3.0 graphics IP block. Runtime code combines these `mm...` constants with SOC15 register helpers such as `SOC15_REG_OFFSET`, `WREG32_SOC15`, `RREG32_SOC15`, and offset variants to address the correct MMIO register for queue management, GDS partitioning, graphics context programming, counters, scratch registers, and MES control.

Although this repository path is under `sources/distributed-fs/ceph-client`, the source is AMDGPU DRM driver metadata, not distributed filesystem or Ceph logic.

## Exported API Surface

The public surface is a generated preprocessor namespace:

- `mm<REGISTER>` defines the register's offset inside its decoded GC address block.
- `mm<REGISTER>_BASE_IDX` selects the SOC15 base-index slot used by register access helpers. In this chunk, early CP/GDS/DIDT/CAC/TCP registers use base index `0`; graphics context, user/config, GDS atomics/remap, and MES registers use base index `1`.

Major register families in the chunk are:

- `mmCP_HQD_*`, `mmCP_MQD_*`, and `mmCP_HPD_*`: compute hardware queue descriptor, memory queue descriptor, pipe/queue priority, dequeue/offload, AQL, EOP, context-save, pointer, DDID, scheduler, and status offsets. The chunk begins after the `mmCP_HQD_IQ_RPTR` offset and includes only its base-index line.
- `mmDIDT_*`: indexed DIDT access registers and auto-increment control.
- `mmGC_CAC_*`, `mmGC_EDC_*`, `mmGC_THROTTLE_*`, `mmEDC_*`, `mmPCC_*`, `mmPWRBRK_*`, `mmGC_CAC_IND_*`, and `mmSE_CAC_IND_*`: clock/power/current/EDC/throttle and indirect CAC register surfaces.
- `mmTCP_*`: texture cache pipe watchpoint address/control registers, UTCL status, and performance-counter filters.
- `mmGDS_*`: VMID base/size tables, GWS and ordered-append VMID mappings, reset masks, context-switch counters, resource state, atomics, reads/writes, GWS resources, OA counters, and GDS memory cleanup.
- `mmDB_*`, `mmCB_*`, `mmPA_*`, `mmVGT_*`, `mmSPI_*`, `mmSX_*`, `mmTA_*`, `mmIA_*`, `mmGE_*`, `mmWD_*`, `mmCOHER_*`, and `mmCONTEXT_*` in `gc_gfxdec0`: depth/color backend, primitive assembly, scissor/viewport, clipping, streamout, shader interpolation/resource, rasterization, and context-state offsets used by graphics pipelines.
- `mmCP_*`, `mmSCRATCH_*`, `mmSQ_THREAD_TRACE_*`, `mmRLC_GPM_*`, `mmUCONFIG_*`, `mmSQC_*`, and additional `mmGDS_*` in `gc_gfxudec`: command processor counters, EOP/fence/append data, streamout and pipeline statistics, scratch registers, atomics, indirect buffers, wait/dispatch/draw state, thread trace control, and user/config-space GDS access.
- `mmCP_MES_*`: MES program counter, trap/vector, interrupt, scratch, instruction pointer, RISC-V-style machine CSRs, cycle/time/instret counters, doorbell controls, process quantum, debug interrupt pointer, and general-purpose register halves.

## Address Blocks Covered

The chunk covers these generated address-block declarations and visible register counts:

- Continuation of `gc_cpphqddec` at base `0xc800`: 43 visible register-offset definitions, plus the dangling `mmCP_HQD_IQ_RPTR_BASE_IDX` from the previous register.
- `gc_didtdec` at base `0xca00`: 3 offsets.
- `gc_gccacdec` at base `0xca10`: 24 offsets.
- `gc_tcpdec` at base `0xca80`: 16 offsets.
- `gc_gdspdec` at base `0xcc00`: 92 offsets.
- `gc_gfxdec0` at base `0x28000`: 641 offsets.
- `gc_gfxudec` at base `0x30000`: 328 offsets.
- `gc_cprs64dec` at base `0x32000`: 70 offsets in this chunk, with more MES registers expected after the boundary.

The largest region is `gc_gfxdec0`, where repeated viewport, scissor, color target, blend, streamout, and shader/geometry setup registers dominate the range. `gc_gfxudec` then switches to CP-visible counters, scratch, atomics, dispatch/draw, GDS, and remap/user-data style registers.

## Control Flow And State Behavior

There is no local control flow. Runtime behavior is introduced by driver code that includes this header, selects a GC instance/base via SOC15 helpers, and performs MMIO reads or writes using the generated constants.

The hardware state named by this chunk includes:

- Compute queue state: HQD active state, VMID, queue priority, quantum, packet queue base/read/write pointers, doorbell control, indirect-buffer pointers, dequeue/offload requests, EOP buffers, context-save locations, suspend offsets, error/status registers, and DDID counters.
- Power and telemetry state: DIDT indirect indexes/data, CAC aggregate and soft controls, EDC thresholds/status/overflow/rolling power delta, throttle controls/status, and performance counters.
- Texture-cache debug state: TCP watchpoints, UTCL status, and performance-counter filtering.
- GDS state: per-VMID GDS base/size allocation, GWS/OA ownership, resource resets, context-switch counters, memory-clean controls, atomics, ordered-append ring controls, and per-resource counters.
- Graphics pipeline context state: depth/stencil control and base addresses, color target masks/bases/views/DCC/compression, scissor and viewport rectangles, viewport depth ranges, raster config, primitive assembly limits, streamout controls, shader stage resource/user-data pointers, interpolation/barycentric settings, and geometry/NGG controls.
- Command processor and user/config state: EOP done/fence addresses, primitive/shader invocation counters, pipe statistics, streamout addresses, scratch registers, atomic preop registers, append/fence data, indirect-buffer tracking, wait/draw/dispatch state, thread-trace controls, and GDS atomic/read/write windows.
- MES microcontroller state: program and trap vectors, interrupts, scratch/indexed scratch, instruction pointer, machine status/cause/bad-address/IP registers, cycle/time/instret counters, machine identity registers, cache op controls, timer compare, doorbells, and general-purpose register halves.

Persistence is entirely hardware-defined. The header does not encode reset values, access permissions, sticky status semantics, write-one-to-clear behavior, self-clearing bits, privilege requirements, power-domain validity, or ordering constraints. Related `gc_10_3_0_default.h` and `gc_10_3_0_sh_mask.h` files provide defaults and bitfields, while actual sequencing lives in AMDGPU runtime code and firmware.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. Semantically, this chunk must stay synchronized with the GC 10.3.0 register database, the companion `gc_10_3_0_sh_mask.h` bitfield header, and `gc_10_3_0_default.h` reset/default values.

Direct include sites in this tree include:

- `drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c`, which uses this header for KFD compute queue setup, VMID/PASID mapping support, interrupt setup, queue dequeue, HQD loading/dumping, and SRBM-selected queue access.
- `drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c`, `gfxhub_v2_1.c`, and shared SDMA/GFX paths that include matching GC 10.3.0 register metadata.
- `drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c`, which includes the GC offset and mask headers for power-management interactions on Vangogh-family hardware.

Common integration mechanisms are `SOC15_REG_OFFSET(GC, inst, mm...)`, `WREG32_SOC15`, `RREG32_SOC15`, `WREG32_SOC15_OFFSET`, and SRBM/GRBM selection for per-queue or per-VMID registers. Several offsets in this chunk are also accessed by adding small register strides, such as per-VMID GDS base/size tables and repeated color/viewport/scissor/counter families.

## Risks And Edge Cases

- Generated-header drift is the central risk. A wrong offset or base index can compile cleanly while reading or writing the wrong MMIO register.
- The first line is a chunk-boundary fragment: `mmCP_HQD_IQ_RPTR_BASE_IDX` belongs with an offset macro in the previous chunk. Merge logic should not treat this as an orphan in the full file.
- The last visible MES register, `mmCP_MES_GP5_LO`, is not the end of the MES register set. Later chunks should continue the GP register sequence and any remaining `gc_cprs64dec` definitions.
- Register aliases share offsets, such as HQ scheduler/status and DMA/offload names in the HQD region, or scratch/atomic and append/fence low-word aliases in `gc_gfxudec`. Consumers must preserve the intended semantic name for the operation being performed.
- Base index matters. Mixing index `0` queue/GDS telemetry offsets with index `1` graphics/user/MES offsets can point access helpers at the wrong address aperture.
- Many registers are sequencing-sensitive. Queue dequeue/offload, MQD/HQD programming, context-save/suspend pointers, EOP buffers, GDS VMID allocation, and MES doorbells require driver/firmware ordering outside this header.
- Address pairs and high/low halves are common. Partial writes to 64-bit addresses, counters, fences, append data, MES CSRs, or GDS atomics can create inconsistent hardware-visible state.
- Context registers are often packet-programmed by command streams rather than arbitrary CPU MMIO writes. Incorrect direct writes can desynchronize command processor state, shadow state, or per-context programming.
- Status and control surfaces are represented the same way as macros. The header does not distinguish read-only status, clear-on-read, write-one-to-clear, privileged, debug-only, or reserved registers.

## Test Signals

Useful validation is primarily build-time, generation-time, and hardware-integration oriented:

- Compile AMDGPU configurations that include GC 10.3.0, KFD, SMU11/Vangogh, SDMA v5.2, and GFXHUB v2.1 paths. Missing or renamed macros should fail at include or register-table use sites.
- Mechanically compare the full `gc_10_3_0_offset.h` against the authoritative register database and the companion `gc_10_3_0_sh_mask.h`/`gc_10_3_0_default.h` files.
- Verify that every visible `mm...` offset in this chunk has a matching `_BASE_IDX`, allowing the known boundary case for `mmCP_HQD_IQ_RPTR`.
- Exercise KFD compute queue creation, MQD/HQD load, queue drain/reset/save, context save/restore, suspend/resume, and queue teardown on GC 10.3.0 hardware.
- Exercise GDS allocation and release across VMIDs, GWS/OA usage, ordered append, GDS atomics, and context-switch accounting.
- Run graphics workloads that stress depth/stencil, color targets, DCC, scissor/viewport arrays, streamout, geometry/tessellation/NGG, shader resource programming, and draw/dispatch CP paths.
- Validate counters and diagnostics: primitive/shader invocation counters, pipe statistics, scratch registers, thread trace, TCP watchpoints, CAC/EDC/throttle telemetry, and MES debug/interrupt state.
- Include suspend/resume, GPU reset, power-gating, and firmware reload tests to catch persistence assumptions around HQD/MQD, GDS, CP fences, scratch, and MES registers.

## Chunk Notes For Merge

This document intentionally covers only lines 4983-7445 of `gc_10_3_0_offset.h`. The previous chunk should provide the beginning of `gc_cpphqddec` and the `mmCP_HQD_IQ_RPTR` offset. The next chunk should continue `gc_cprs64dec` after `mmCP_MES_GP5_LO_BASE_IDX`. The final per-file research should treat the whole file as generated GC 10.3.0 offset metadata paired with mask/default headers, not as standalone runtime logic.

### subset-b-002473: lines 7446-9968

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h lines 7446-9968

## Scope

This chunk is a late segment of the generated AMD GC 10.3.0 register-offset header. It covers lines 7446 through 9968 and defines 1,212 register-offset macros plus 1,212 matching `_BASE_IDX` macros. The range begins in the tail of the CP MES register block, continues through GUS, GL1/CH/GL2, GC performance counter data/select/config blocks, GRTAVFS, RLC, RLC shadow/control blocks, GC power/clock-gating controls, and ends inside the beginning of the hypervisor CP microcode access block.

The content is declarative only. There are no C functions, structs, enums, branches, loops, locks, allocations, or direct software side effects. The exported interface is a set of preprocessor constants that name GC 10.3.0 MMIO register offsets and the register-base selector used by SOC15 register helpers.

## Purpose

`gc_10_3_0_offset.h` supplies symbolic register addresses for AMDGPU, KFD, SDMA, and SMU code that targets GC 10.3.0-class hardware. Driver code pairs these offsets with field definitions from `gc_10_3_0_sh_mask.h` and reset/default values from `gc_10_3_0_default.h`, then uses helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, `RREG32_FIELD15`, and SMU/PSP register access wrappers instead of embedding raw MMIO addresses.

This slice concentrates on low-level graphics-control surfaces:

- CP MES scratch/general-purpose, debug-memory index/data, performance counter control, and pending-interrupt registers.
- GUS arbitration, priority, queueing, credit/reserve, latency, error, L1 channel/statistics, and performance counter registers.
- GL1, channel, GL2 cache/arbiter/status, steering, L2 writeback/invalidate, soft-reset, match/mask, and load-balancer registers.
- Performance counter data and select/config spaces for CP, GRBM, GE, PA, SPI, SQ, SX, GDS, TA/TD/TCP, CB/DB, RLC, RMI, UTCL1, GCR, GL1A/GL1C, CH/CHA/CHC/CHCG, GUS, GCVML2, GCUTCL2, and SDMA0-3.
- GRTAVFS/RTAVFS indirect access and target frequency/voltage controls.
- RLC firmware/control/status, timers, interrupts, load-balancer, power-gating, clock counting, doorbells, safe mode, scratch, log, ucode/IRAM, debug, GPM, SRM, XT, and microcontroller-control registers.
- RLCR and RLCS shadow/control/status registers for RLC context, exceptions, clock/power-management handshakes, interrupt handling, virtualization/IOV state, diagnostics, and bootload status.
- GC power decoder clock-gating/throttling controls for most graphics subblocks.
- Hypervisor CP ucode address/data aliases at the chunk end.

## Address Blocks Covered

Visible address-block boundaries in this range are:

- Continuation from the preceding CP MES block: `mmCP_MES_GP5_HI` through `mmCP_MES_PENDING_INTERRUPT`.
- `gc_gusdec`, base `0x33000`: GUS IO/DRAM priority, combining, credits, reserves, misc, latency/error, L1 channel, and GUS performance/status registers.
- `gc_gl1dec`, base `0x33400`: GL1 DRAM burst, arbiter status, pipe steering, GL1C status/UTCL0 retry.
- `gc_chdec`, base `0x33600`: channel arbiter, burst, credit, pipe steering, VC5, CHC/CHCG control and status.
- `gc_gl2dec`, base `0x33800`: GL2C/GL2A control, address match, writeback/invalidate, soft reset, CM/LB state, and pipe steering.
- `gc_perfddec`, base `0x34000`: performance counter result low/high and latency data registers across many GC subblocks.
- `gc_gcvml2prdec`, base `0x353a0`, and `gc_gcvml2perfddec`, base `0x353e0`: GCMC VM L2, GCUTCL2, and GCVML2 performance counter result registers.
- `gc_sdma0_sdma0perfddec` through `gc_sdma3_sdma3perfddec`, bases `0x35980`, `0x359b0`, `0x359e0`, and `0x35a10`: SDMA performance counter result registers.
- `gc_perfsdec`, base `0x36000`: performance counter select, select1, mode, bins, config, result-control, window, draw-object/window, and misc control registers.
- `gc_gcvml2pldec`, base `0x374b0`, and `gc_gcvml2perfsdec`, base `0x374f0`: GCMC VM L2, GCUTCL2, and GCVML2 performance counter config/select/mode registers.
- `gc_sdma0_sdma0perfsdec` through `gc_sdma3_sdma3perfsdec`, bases `0x37880`, `0x378b0`, `0x378e0`, and `0x37910`: SDMA performance counter config/select/misc registers.
- A bare generated `base address: 0x3a000` marker with no visible `addressBlock:` label in this chunk and no local register definitions before the next block.
- `gc_grtavfsdec`, base `0x3ac00`: GRTAVFS/RTAVFS indirect register address/data/control/status and target frequency/voltage controls.
- `gc_rlcdec`, base `0x3b000`: the largest local region, covering RLC control, firmware, status, timing, interrupts, power-gating, load-balancer, debug, logs, scratch, doorbell, safe-mode, ucode, IRAM, SRM, GPM, and XT registers.
- `gc_rlcrdec`, base `0x3b800`: RLC SPP CAM and PACE scratch access registers.
- `gc_rlcsdec`, base `0x3b980`: RLC shadow/control/status, exception, clock/power, IOV, interrupt-handler, WGP, bootload, auxiliary, KMD log, and decoder-end registers.
- `gc_pwrdec`, base `0x3c000`: CGTS status/disable registers and CGTT/CAC clock-gating controls across SPI, PC, BCI, VGT, IA, WD, GS/NGG, PA, SC, SQ, SX, TD/TA, TCPI/TCPF, GDS, DB, CB, GL2, CP/CPF/CPC, RLC, RMI, GCR, UTCL1, GCEA, SE, GC, GRBM, GUS, and PH.
- `gc_hypdec`, base `0x3e000`: CP PFP/ME/CE microcode address/data aliases at the end of the chunk.

## Exported API Surface

There are no callable APIs or local types. The public surface is the generated macro namespace:

- Every register name is emitted as `#define mm<REGISTER> <offset>`.
- Every register has a companion `#define mm<REGISTER>_BASE_IDX 1` in this range. Consumers pass the base index into SOC15-style address calculation so the same offset can be resolved against the proper register aperture/base.
- Alias registers intentionally share offsets in several places. Examples include `mmGRTAVFS_RTAVFS_REG_ADDR` and `mmRTAVFS_RTAVFS_REG_ADDR`, `mmRLC_GPM_STAT` and `mmRLC_RLCS_GPM_STAT`, and the hypervisor/non-hypervisor CP ucode aliases such as `mmCP_HYP_PFP_UCODE_ADDR` and `mmCP_PFP_UCODE_ADDR`.
- Low/high register pairs are common for 64-bit counters, timestamps, clock counts, doorbell payloads, scratch/log addresses, and ucode/data access windows.
- Repeated performance blocks are named by client and counter number, for example `mmSQ_PERFCOUNTER*_LO/HI`, `mmSQ_PERFCOUNTER*_SELECT`, `mmPA_SC_PERFCOUNTER*`, `mmSDMA*_PERFCOUNTER*`, and `mmGCMC_VM_L2_PERFCOUNTER*`.
- Control/status/readback naming conventions are visible in suffixes such as `CNTL`, `CTRL`, `STAT`, `STATUS`, `REQ`, `RESPONSE`, `ENABLE`, `DISABLE`, `CLEAR`, `FORCE`, `DEBUG`, `SCRATCH`, `LOG`, `UCODE`, `IRAM`, `DOORBELL`, `SOFT_RESET`, `CLK_CTRL`, and `PERFCOUNTER`.

The header does not encode field widths, read/write permissions, sticky-bit behavior, reset values, or clear semantics. Those come from the matching shift/mask/default headers and from hardware documentation or calling-code conventions.

## Control Flow And State Behavior

There is no local software control flow. Runtime behavior happens when included driver code uses these constants to read or write MMIO registers.

The named registers describe several hardware state machines and persistent register banks:

- CP MES state: general-purpose registers, debug-memory indirect access, performance counter control, and pending interrupts reflect micro-engine scheduling/diagnostic state.
- Cache/channel/GUS state: GL1/GL2/channel/GUS controls and status registers affect arbitration, client credits, data-path steering, cache invalidation/writeback, retry, soft reset, latency sampling, and error reporting. Values persist in hardware until reset, power-gating loss, firmware restore, or explicit driver/firmware writes.
- Performance monitoring state: counter result registers accumulate or expose selected events; select/config/mode registers determine which events are counted. Programming normally follows a configure-select-enable-sample-read sequence in caller code, not in this header.
- GRTAVFS/RTAVFS state: indirect register address/data/control/status plus target frequency/voltage registers participate in adaptive voltage/frequency scaling handshakes.
- RLC state: RLC control, firmware, timers, interrupts, GPM threads, load balancing, power-gating, clock counting, doorbells, scratch/log/ucode/IRAM access, safe-mode, and SRM registers are part of the RLC firmware and graphics power-management control plane. These registers are often tightly ordered with firmware loading, PSP/SMU handshakes, GFXOFF, CG/PG transitions, and GPU reset.
- RLCR/RLCS state: shadow/context, exception, bootload, IOV, interrupt-handler, WGP, and auxiliary registers reflect saved/restored RLC context and virtualization/diagnostic state.
- GC power/clock-gating state: `CGTS_*`, `CGTT_*`, `*_CGTT_*`, and `*_CAC_*` registers influence clock gating, coarse/fine-grained power behavior, and per-block clock controls. Writes can immediately affect access latency and block availability.
- CP hypervisor ucode windows: address/data aliases are indirect windows for PFP/ME/CE microcode access. Correct sequencing and ownership are external to this generated file.

Read-only, write-only, write-one-to-clear, sticky, and volatile behavior cannot be proven from the offset macros alone. Names such as `STATUS`, `STAT`, `RD_DATA`, `RD_REG`, `BUSY`, and `RESPONSE` imply readback-oriented state; names such as `CTRL`, `CNTL`, `SELECT`, `CFG`, `ENABLE`, `DISABLE`, `CLEAR`, `FORCE`, `UCODE_ADDR`, and `UCODE_DATA` imply configuration or command paths. The authoritative semantics remain in the ASIC register database and hardware-facing call sites.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. Semantically, this chunk is coupled to:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h` for bit fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_default.h` for reset/default values.
- SOC15 register access helpers and AMDGPU register macros that combine IP block, instance, base index, and offset.

Direct GC 10.3.0 include users in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.c`, which includes the offset, sh/mask, and default headers for GC 10.3.0 VM hub setup and register programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c`, which includes GC 10.3.0 offsets and masks for SDMA register programming and performance/engine integration.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c`, which includes GC 10.3.0 offsets and masks for KFD/GFX 10.3 queue and compute-facing integration.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c`, which includes the GC 10.3.0 offset and mask headers for Vangogh SMU power-management paths, including GFXOFF-related register access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.c`, which includes the GC 10.3.0 sh/mask companion and interacts with SDMA/shared register fields.

Important runtime integration areas are firmware loading, PSP/SMU/RLC handshakes, GFXOFF and power-gating transitions, GPU reset and suspend/resume restore, performance monitoring, debugfs/perf diagnostics, VM hub setup, SDMA bring-up, and KFD compute queue enablement. Many registers in this chunk are also likely firmware-owned or PF-owned under some modes; caller code must respect the ownership model for the active ASIC, virtualization mode, and power state.

## Risks

- Generated-header drift is the primary risk. A wrong offset or base index can direct a read/write to the wrong GC register even when the field mask and caller logic are correct.
- Alias offsets must remain intentional. Removing or changing aliases such as `RLC_GPM_STAT`/`RLC_RLCS_GPM_STAT`, RTAVFS aliases, or CP hypervisor/non-hypervisor ucode aliases can break code that uses older or block-specific names for the same register.
- Performance counter blocks are highly repetitive. A single off-by-one offset in low/high result pairs, select/select1 pairs, or SDMA instance spacing can produce misleading telemetry rather than an obvious crash.
- RLC registers are sensitive because they sit in firmware loading, power-gating, clock-gating, interrupt, reset, and context-save/restore paths. Bad offsets can hang firmware bring-up, block GFXOFF, break WGP power management, lose interrupts, or make GPU reset unreliable.
- Clock-gating and power-control offsets can make later MMIO accesses unreliable if code writes the wrong control register or writes it at the wrong time in SMU/RLC sequencing.
- Registers with names such as `SOFT_RESET`, `CLEAR`, `FORCE`, `DISABLE`, `UCODE_DATA`, and `IRAM_DATA` can have destructive or command-like semantics. Treating them as ordinary read/write scratch registers in diagnostics can perturb hardware state.
- Split low/high registers require stable ordering in caller code. Reading counters or timestamps without latching/capture semantics may race hardware increments; writing address/data windows in the wrong order can corrupt indirect access state.
- The chunk starts and ends mid-file, including a CP MES continuation at the start and partial `gc_hypdec` at the end. Merge-time review should not mark missing earlier/later names as local omissions.
- The bare `base address: 0x3a000` marker without local registers is a generated artifact in this slice. A parser that assumes each base-address line has a local address-block name and registers can misclassify this boundary.

## Test Signals

Useful validation is mostly build-time, generated-data, and hardware-integration oriented:

- Compile or preprocess GC 10.3.0 AMDGPU, SDMA, SMU, and KFD paths that include `gc_10_3_0_offset.h`, `gc_10_3_0_sh_mask.h`, and `gc_10_3_0_default.h`.
- Static generation checks that every non-boundary register macro in this range has exactly one matching `_BASE_IDX` macro and that duplicate offsets are limited to known aliases.
- Cross-check this offset slice against the GC 10.3.0 register database and companion sh/mask/default headers for name alignment, base-index consistency, and expected address-block membership.
- Boot and reset GC 10.3.0-class hardware, including Vangogh-style SMU/GFXOFF paths, and verify RLC firmware load, safe-mode transitions, GFXOFF entry/exit, clock-gating enablement, and suspend/resume restore.
- Exercise SDMA0-3 and KFD compute paths on GC 10.3.0 hardware to confirm queue bring-up, interrupts, VM integration, and engine reset do not regress.
- Run performance-counter smoke tests across graphics, shader, cache, memory, GUS, GCVML2, and SDMA blocks: configure counters, sample low/high results, reset/reconfigure, and verify sane monotonic or event-correlated behavior.
- Exercise GPU reset, RLC/SMU mailbox or response paths, power-gating transitions, and debugfs/perf readbacks while checking for MMIO timeouts or stuck status bits.
- For virtualization/SR-IOV-like modes, verify PF/VF ownership boundaries around RLC, RLCS, CP hypervisor ucode, clock-gating, and power-management registers.

## Chunk Notes For Merge

This document is source-tree aligned and covers only lines 7446-9968 of `gc_10_3_0_offset.h`. Earlier chunks should cover the start of the CP MES address block and prior GC offset regions. Later chunks should continue the `gc_hypdec` register list and the remainder of the GC 10.3.0 offset namespace. The final per-file report should describe the whole file as a generated MMIO offset map for GC 10.3.0 hardware, used by AMDGPU, KFD, SDMA, and SMU code, rather than as handwritten executable logic.

### subset-b-002474: lines 9969-12437

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h lines 9969-12437

## Scope

This chunk is a generated register-offset segment from the AMD GC 10.3.0 ASIC register header. It covers line 9969 through line 12437 and contains 1,217 visible register offset macros plus their generated `_BASE_IDX` companion macros where the companion falls inside this range. The range starts in the tail of a CP/GC hypervisor register area, continues through SDMA hypervisor, GCVM shared hypervisor, PSP, GCVM L2 PSP, and SDMA2/SDMA3 decoder blocks, and ends inside the `SDMA3_RLC5` queue register family before the next line's `_BASE_IDX` companion.

The content is declarative only. There are no C functions, structs, enums, branches, loops, allocations, locks, or local side effects. Its public interface is the preprocessor namespace of `mm...` offset constants and `mm..._BASE_IDX` selector constants consumed by AMDGPU/KFD register access helpers.

## Purpose

`gc_10_3_0_offset.h` supplies symbolic MMIO register offsets for GC 10.3.0-class AMD GPU IP. Consumers combine these macros with SOC15 register-base tables and helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_ENTRY_STR` so driver code can address hardware registers without embedding raw offsets.

This chunk maps three broad hardware surfaces:

- Command processor, graphics register bus, RLC, SR-IOV, and GCVM hypervisor-visible registers under base index 1.
- SDMA0 through SDMA3 hypervisor decoder windows for microcode, VM context, active function, VF enable, and register-type classification.
- SDMA2 and SDMA3 public decoder windows under base index 2, including engine-global control/status registers and per-queue GFX/PAGE/RLC ring and indirect-buffer registers.

The chunk is especially important for virtualization and multi-SDMA support on GC 10.3.0. It names the offsets used to program CP firmware windows, classify and access virtualized SDMA registers, expose per-VF framebuffer and MARC ranges, service GCVM/IOMMU handshakes, and compute SDMA engine/queue register addresses for KFD and SDMA ring management.

## Exported API Surface

There are no callable APIs or local types. The exported surface is the generated macro set:

- CP and MES firmware/register windows: `mmCP_HYP_CE_UCODE_ADDR`, `mmCP_CE_UCODE_DATA`, `mmCP_HYP_MEC1_UCODE_ADDR`, `mmCP_MEC_ME1_UCODE_DATA`, `mmCP_HYP_MEC2_UCODE_ADDR`, `mmCP_MEC_ME2_UCODE_DATA`, plus PFP/ME/CE/CPC/MES instruction-cache base/control/op registers and MES instruction/data/local base, mask, bound, and aperture registers.
- GRBM and GC interrupt routing registers: `mmGFX_PIPE_PRIORITY`, `mmGRBM_GFX_INDEX_SR_SELECT`, `mmGRBM_GFX_INDEX_SR_DATA`, `mmGRBM_GFX_CNTL_SR_SELECT`, `mmGRBM_GFX_CNTL_SR_DATA`, GRBM CAM index/data/upper aliases including hypervisor names, `mmGC_IH_COOKIE_0_PTR`, and `mmGRBM_SE_REMAP_CNTL`.
- RLC GPU IOV and virtualization registers: `mmRLC_GPU_IOV_VF_ENABLE`, config registers, VM busy and scheduler registers, active function ID, VF doorbell status/set/clear/mask, hypervisor semaphores, pace/timer/interrupt controls, SRM/FW/host/SCP responses, scratch and ucode address/data registers, graphics idle/workload counters, and SDMA0 through SDMA7 status and busy-status mirrors.
- SDMA hypervisor decoder blocks: `gc_sdma0_sdma0hypdec` through `gc_sdma3_sdma3hypdec` provide `mmSDMA{0,1,2,3}_UCODE_ADDR`, `UCODE_DATA`, `VM_CTX_LO/HI`, `ACTIVE_FCN_ID`, `VM_CTX_CNTL`, `VIRT_RESET_REQ`, `VF_ENABLE`, `CONTEXT_REG_TYPE0..3`, `PUB_REG_TYPE0..3`, and `VM_CNTL`; SDMA0 also includes broadcast ucode address/data.
- GCVM shared hypervisor registers: `mmGCMC_VM_FB_SIZE_OFFSET_VF0` through `VF31`, `mmGCVM_IOMMU_MMIO_CNTRL_1`, MARC base/reloc/length low/high registers for four ranges, `mmGCVM_IOMMU_CONTROL_REGISTER`, `mmGCVM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER`, and `mmGCMC_VM_XGMI_GPUIOV_ENABLE`.
- PSP-facing GC registers: `mmCPG_PSP_DEBUG`, `mmCPC_PSP_DEBUG`, `mmGRBM_SEC_CNTL`, `mmRLC_FWL_FIRST_VIOL_ADDR`, and `mmRLC_SRM_FWL_FIRST_VIOL_ADDR`.
- GCVM L2 PSP decoder registers: `mmGCVM_L2_ID_CTRL0..7`, `mmGCVM_L2_ID_CTRL_HI`, `mmGCVM_L2_ID_STATUS`, `mmGCUTCL2_TRANSLATION_BYPASS_BY_VMID`, `mmGCVM_IOMMU_GPU_HOST_TRANSLATION_ENABLE`, and GPUVA VMID translation assist request/response low/high registers.
- SDMA2 public decoder registers: engine-wide control/status and telemetry (`DEC_START`, timestamps, power/clock/control/chicken bits, GB address config, status, burst, EDC, atomic, UTCL1, timeout, error log, scratch, timestamp, interrupt, queue reset), followed by GFX, PAGE, and RLC0 through RLC7 queue register families.
- SDMA3 public decoder registers: the same generated engine-wide and queue-family pattern as SDMA2, beginning at offset `0x0400`; this chunk covers GFX, PAGE, RLC0 through RLC4 completely and starts RLC5 through `mmSDMA3_RLC5_RB_RPTR_ADDR_LO`.

Most SDMA queue families follow the same register pattern: `RB_CNTL`, ring-buffer base low/high, read/write pointers low/high, write-pointer polling control and polling address, indirect-buffer control/read pointer/offset/base/size, skip control, context status, doorbell, status/log/watermark/doorbell offset, context-save-area address low/high, indirect-buffer sub-remain, preempt, dummy register, AQL control, minor pointer update, and `MIDCMD_DATA0..10` plus `MIDCMD_CNTL`.

## Control Flow And State Behavior

The header itself has no runtime control flow. It affects runtime behavior when included driver code resolves a symbolic register name to an MMIO address and reads or writes the hardware register.

The named registers describe several persistent hardware state areas:

- CP/MES microcode and cache programming registers persist firmware addressing and instruction/data-cache control state until reset, firmware reinitialization, power-domain loss, or explicit driver/firmware reprogramming.
- GRBM shadow-register and CAM controls steer which graphics instance, shadow register, or virtualized context is accessed. These registers are tied to register-indexing and virtualization state rather than process-owned memory.
- RLC GPU IOV registers hold SR-IOV/PF/VF scheduling, active-function, doorbell, interrupt, semaphore, VM-busy, and SDMA status state. Some are status/readback-oriented, while others are control or clear/set registers with side effects outside this header.
- SDMA hypervisor decoder registers expose per-engine virtualization controls: active function, VF enable, VM context, virtual reset request, and public/context register classification. Those settings determine what SDMA state is visible to guest functions and how SDMA MMIO is partitioned.
- GCVM shared hypervisor registers persist per-VF framebuffer size/offset and MARC base/relocation/length windows. These are global virtualization memory-controller settings, not per-process driver data.
- GCVM L2 PSP/IOMMU translation-assist registers participate in host translation, VMID bypass, and request/response handshakes. The macros do not encode ownership, ordering, or clear semantics; those must be inferred from register documentation and caller paths.
- SDMA2/SDMA3 public decoder registers represent live DMA engine state: ring-buffer and indirect-buffer pointers, base addresses, doorbell offsets, preemption, context-save addresses, UTCL1 translation status, queue reset requests, EDC/error counters, and mid-command capture/control state. These registers persist while the engine is powered and are restored or rebuilt during driver init, reset, suspend/resume, or queue recreation.

Repeated SDMA queue offsets are used arithmetically by callers. KFD code computes a queue's register window by taking the delta between `mmSDMA*_RLC1_RB_CNTL` and `mmSDMA*_RLC0_RB_CNTL`, while SDMA code maps instance IDs to SOC15 base-index windows. Incorrect spacing in this header changes runtime address calculation even if the caller never references every individual macro.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. Semantically, these offsets must stay aligned with the matching GC 10.3.0 shift/mask and default headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_default.h`

Important integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c`, which includes this offset header, builds SDMA register debug lists, computes SDMA instance offsets with base index 0/1/2 windows, and reads/writes GFX/PAGE/RLC ring pointers, doorbells, VM controls, and queue reset state through the generated SDMA names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c`, which includes this header and computes KFD SDMA RLC queue offsets for SDMA0 through SDMA3 using `mmSDMA*_RLC0_RB_CNTL` and the RLC queue stride.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.c`, which includes the GC 10.3.0 offset/sh_mask/default set for GFXHUB VM setup, system aperture/default-page programming, TLB/cache setup, VM invalidation, and fault reporting. This chunk contributes related GCMC/GCVM hypervisor and PSP-facing names, while earlier/later chunks hold many of the ordinary VM context offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c`, which carries local definitions for `mmCP_HYP_CE_UCODE_ADDR` and writes that register during CE firmware version handling. The duplicate local definition signals that the CP hypervisor offset is a known integration point even in code paths not directly using this header name from the include.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c`, which includes this header from a power-management path, making compile-time namespace stability relevant outside the graphics and KFD files.

At runtime, these macros integrate with AMDGPU's SOC15 register-offset tables, firmware loading, SR-IOV PF/VF handling, GFXHUB/GCVM memory management, SDMA ring and queue bring-up, KFD compute queue management, diagnostics/register dumps, suspend/resume restore, GPU reset, and hardware error/fault reporting.

## Risks

- Generated-header drift is the primary risk. A wrong offset or base index can silently direct reads or writes to the wrong MMIO register.
- The range mixes base index 1 hypervisor/GCVM/PSP registers with base index 2 SDMA2/SDMA3 public decoder registers. Misclassified `_BASE_IDX` values can make SOC15 helpers address the wrong register aperture.
- Several macros are aliases for the same offset, such as CP hypervisor and non-hypervisor CE/MEC ucode names, and GRBM CAM hypervisor aliases. Removing or changing aliases can break consumers that depend on either naming convention.
- SDMA queue families are highly repetitive and are used with computed strides. Any inconsistent offset inside `RLC0..RLC7`, GFX, or PAGE queues can cause only one queue or one engine to fail, which is harder to diagnose than a global compile failure.
- SDMA2 and SDMA3 offsets share the same base index but different internal offsets. Instance mapping in `sdma_v5_2_get_reg_offset()` depends on the relationship among SDMA0/1 and SDMA2/3 windows; wrong constants can corrupt the wrong engine's queue state.
- Ring pointer, polling-address, doorbell, and CSA address registers are live queue-control state. Bad addresses can hang queues, lose interrupts, corrupt context-save memory, or leave firmware polling stale pointers.
- RLC GPU IOV and SDMA hypervisor registers are ownership-sensitive. PF, VF, firmware, PSP, and host-driver responsibilities differ by mode; blind writes through a wrong macro can violate virtualization boundaries or collide with firmware-managed state.
- GCVM shared hypervisor and IOMMU/MARC registers affect address translation and per-VF memory windows. Incorrect programming can expose the wrong framebuffer range, break XGMI/GPUIOV isolation, or route DMA to unintended physical memory.
- PSP-facing security and firewall violation registers are likely security-sensitive. Misaddressed debug or violation-address registers can hide genuine protection faults or produce misleading diagnostics.
- This chunk starts and ends at generated-file boundaries inside larger groups. Merge-time validation should not treat the missing address-block comment before line 9969 or the missing `mmSDMA3_RLC5_RB_RPTR_ADDR_LO_BASE_IDX` line after 12437 as defects in this chunk alone.

## Test Signals

Useful validation is mostly build-time, generation-time, and hardware-integration oriented:

- Compile or preprocess AMDGPU, KFD, and SW-SMU files that include `gc_10_3_0_offset.h`, `gc_10_3_0_sh_mask.h`, and `gc_10_3_0_default.h`.
- Generated-data checks that every register macro in the full header has the expected `_BASE_IDX` companion, allowing explicit chunk-boundary exceptions at line 12437.
- Cross-check the offsets and base indices against the GC 10.3.0 register database and the matching shift/mask/default headers.
- SDMA v5.2 bring-up tests on GC 10.3.0-class hardware: firmware load, ring creation, read/write pointer updates, doorbell and non-doorbell paths, indirect-buffer execution, queue reset, preemption, and register-dump readability across SDMA0 through SDMA3.
- KFD SDMA queue tests that create queues on multiple SDMA engines and RLC queue IDs, validating that queue stride arithmetic lands on the expected `RLCn` register windows.
- SR-IOV PF/VF tests that exercise active-function selection, VF enable/disable, virtual reset, doorbell status, SDMA status mirrors, and per-VF framebuffer/MARC window programming.
- VM and translation tests around GFXHUB/GCVM/IOMMU integration: GART/system aperture setup, VMID translation-assist request/response paths, invalidation, and protection-fault reporting.
- Suspend/resume and GPU reset tests that verify SDMA, RLC IOV, GCVM, and CP/MES state is restored by the correct owner or intentionally reinitialized.
- Fault-injection or diagnostics tests for SDMA UTCL1 status/XNACK, EDC/error counters, PSP/RLC firewall violation address reporting, and GCVM L2 ID/status registers.

## Chunk Notes For Merge

This document is intentionally source-tree aligned and covers only lines 9969-12437 of `gc_10_3_0_offset.h`. Earlier chunks should cover the start of the surrounding CP/GC hypervisor address block and earlier SDMA0/SDMA1 public decoder families. Later chunks should continue `SDMA3_RLC5` after `mmSDMA3_RLC5_RB_RPTR_ADDR_LO`, then cover the rest of RLC5, RLC6/RLC7, and subsequent GC 10.3.0 register blocks. The final per-file report should describe the whole file as a generated GC 10.3.0 MMIO offset map consumed by AMDGPU, KFD, SDMA, GFXHUB, firmware, virtualization, and diagnostics paths.

### subset-b-002475: lines 12438-13625

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h lines 12438-13625

## Scope

This chunk is the tail of the generated AMD GC 10.3.0 register-offset header. It covers line 12438 through the file end at line 13625 and contains 1,150 preprocessor definitions: 1,027 register index/offset macros plus 123 `*_BASE_IDX` macros. The range starts mid-way through the `SDMA3_RLC5` queue register group, continues through complete `SDMA3_RLC6` and `SDMA3_RLC7` queue groups, and then defines several indirect address blocks: `gccacind`, `secacind`, `spmglbind`, `spmind`, `grtavfsind`, `spiind`, `sqind`, and `didtind`.

The file is declarative. It has no C functions, structs, enums, branches, loops, allocations, locks, or direct side effects. Its exported API is a generated macro namespace used by AMDGPU, KFD, power-management, debug, and performance-monitor code to address GC 10.3.0 MMIO or indexed registers without hard-coded numeric offsets.

## Purpose

`gc_10_3_0_offset.h` maps symbolic GC 10.3.0 register names to register indices and base-index selectors. Consumers pair these offsets with `gc_10_3_0_sh_mask.h` field definitions and AMDGPU register helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_IP`, `WREG32_SOC15_IP`, and plain `RREG32`/`WREG32` after computing a dynamic offset.

This slice describes three major hardware surfaces:

- SDMA3 compute/RLC queue registers for queue slots 5 through 7, including ring-buffer, indirect-buffer, doorbell, context-save, preemption, write-pointer polling, AQL, minor-pointer-update, and mid-command preemption state registers.
- GC current-average-current/power and performance-monitor indexed blocks, including CAC weights, accumulators, overrides, stall/release/power-break LUTs, fixed-pattern counters, shader-engine CAC control, global and per-shader-engine SPM sample-delay registers, and RTAVFS indexed registers.
- Shader/debug and dynamic power-control indexed blocks, including SQ wave debug state and TTMP/EXEC registers plus DIDT control, stall-pattern, EDC, throttle, and event-counter registers for SQ, DB, TD, and TCP.

## Exported API Surface

There are no callable APIs or local types. The public interface is the macro set itself:

- `mmSDMA3_RLC5_*`: the chunk begins after the start of this queue group. The visible portion includes IB control/read-pointer/offset/base/size, skip/context status, doorbell/status/log/watermark/offset, CSA address, IB remaining/preempt/dummy, write-pointer poll address, AQL control, minor pointer update, and `MIDCMD_DATA0` through `MIDCMD_DATA10` plus `MIDCMD_CNTL`.
- `mmSDMA3_RLC6_*` and `mmSDMA3_RLC7_*`: complete repeated SDMA RLC queue register groups. They include `RB_CNTL`, ring base high/low, ring read/write pointers high/low, write-pointer polling control and poll-address registers, read-pointer writeback address, IB control/base/size, context status, doorbell control and offset, queue status/log/watermark, CSA address, preemption, AQL control, minor-pointer update, and mid-command state registers.
- `*_BASE_IDX` macros for the visible SDMA3 queue registers: all visible SDMA3 entries use base index `2`, matching the GC base aperture selected by the SOC15 register helper layer for this SDMA instance window.
- `ixPCC_*`, `ixPWRBRK_*`, `ixEDC_*`, `ixGC_CAC_*`, `ixRELEASE_*`, `ixSTALL_*`, `ixFIXED_*`, and `ixHW_LUT_UPDATE_STATUS` in `gccacind`: indirect CAC/power-break/performance-monitor registers for GC-wide power estimation, stall/release pattern control, per-block weights, per-block accumulators, override values, and LUT update status.
- `ixSE_CAC_*` in `secacind`: shader-engine CAC identity/control/override selector/value registers.
- `ixGLB_*_SAMPLEDELAY` in `spmglbind`: global SPM sample-delay registers for CPG/CPC/CPF, GDS/GCR/PH/GE/GUS/CHA/CHC, ATCL2/VML2, SDMA0-3, GL2A/GL2C slices, EA0-15, and CHC/GE2SE paths.
- `ixSE_*_SAMPLEDELAY` in `spmind`: per-shader-engine sample-delay registers for SPI, SQG, CBR/DBR/PA, shader-array GL1/SX/CB/DB/SC/RMI/GL1C blocks, and WGP-local TA/TD/TCP instances for SA0 and SA1.
- `ixRTAVFS_REG0` through `ixRTAVFS_REG165` in `grtavfsind`: a dense RTAVFS indexed register bank.
- `ixSA_WGP_BLK_ID` in `spiind`: a single SPI indirect register identifying or selecting WGP block context.
- `ixSQ_*` and `ixSQ_WAVE_*` in `sqind`: SQ local debug status, wave active/valid state, wave mode/status/trap status, hardware IDs, GPR/LDS allocation, IB state, program counter, instruction word, flat scratch, scheduler mode, VGPR offset, shader cycle counter, TTMP0-15, `M0`, `EXEC_LO`, `EXEC_HI`, and shared interrupt-word aliases.
- `ixDIDT_SQ_*`, `ixDIDT_DB_*`, `ixDIDT_TD_*`, and `ixDIDT_TCP_*` in `didtind`: DIDT control, OCP, stall/tuning/auto-release, stall patterns, MPD scale, stall-release controls, weights, EDC controls/thresholds/patterns/timers/delays/status/overflow/rolling-power-delta/PCC counters, throttle controls, and final per-block stall event counters.

## Control Flow And State Behavior

This header has no local control flow. Runtime behavior appears only when included driver code uses the macros to build MMIO addresses or indexed-register accesses.

The SDMA queue macros describe persistent hardware queue state. KFD and AMDGPU code programs an SDMA RLC queue by computing an engine base plus `queue_id * (mmSDMA0_RLC1_RB_CNTL - mmSDMA0_RLC0_RB_CNTL)`, disabling `RB_ENABLE`, waiting for `CONTEXT_STATUS` idle, programming doorbell offset/enable, ring read/write pointers, ring base, read-pointer writeback address, and then re-enabling the queue. Pointer state, doorbell routing, CSA addresses, AQL mode, preemption state, and mid-command data remain in hardware until queue teardown, reset, suspend/resume restore, firmware/PF intervention, or later writes.

The CAC, SPM, RTAVFS, SQ, and DIDT macros describe indexed register banks rather than plain per-file data. Their state is held in hardware power, performance, debug, and shader-control blocks. Typical access goes through register helper paths that select an indirect index aperture and then read or write the indexed data. Names such as `*_STATUS`, `*_PERF_COUNTER`, `*_OVERFLOW`, `*_ACTIVE`, and `*_VALID_AND_IDLE` imply readback/counter/debug semantics, while `*_CTRL`, `*_CNTL`, `*_TUNING_CTRL`, `*_SAMPLEDELAY`, `*_WEIGHT*`, `*_OVRD*`, and `*_PATTERN*` are configuration-oriented. Exact read-only, write-one-clear, sticky, reset, and ownership semantics are not encoded in this offset header and must be taken from the hardware register database plus caller behavior.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. Semantically, this chunk must stay aligned with the matching GC 10.3.0 bitfield and reset-value headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_default.h`

Important consumers and integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c`, which includes this offset header for GC 10.3.0 SDMA setup. The file programs SDMA ring pointers, write-pointer polling, doorbells, ring bases, firmware loading, halt/unhalt, context-switch control, and ring tests. Its register-offset helper maps logical SDMA instances onto the correct GC base aperture and internal offset.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c`, which includes this header and computes SDMA RLC queue offsets from `mmSDMA0_RLC0_RB_CNTL`, `mmSDMA1_RLC0_RB_CNTL`, `mmSDMA2_RLC0_RB_CNTL`, `mmSDMA3_RLC0_RB_CNTL`, and queue spacing. That pattern is the direct integration model for the `mmSDMA3_RLC5` through `mmSDMA3_RLC7` offsets in this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v10.c` and related KFD MQD managers, which use the matching SDMA RLC bitfields to encode queue size, VMID, read-pointer writeback, doorbell offsets, and queue privilege state before AMDGPU writes the corresponding registers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.c`, which includes the GC 10.3.0 generated namespace for GFXHUB/GC VM programming elsewhere in the same header family.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c`, which includes this offset header for GC 10.3.0 power-management integration.
- Older PM/DPM paths such as `kv_dpm.c`, `smu7_powertune.c`, and `vega10_powertune.c` show the same `ixDIDT_*` conceptual integration pattern through DIDT indexed-register helpers, even though those files target other ASIC generations.

At a hardware level, these macros tie into SDMA queue bring-up/teardown, KFD process queues, doorbell aperture management, SR-IOV PF/VF register ownership, firmware restore, suspend/resume, performance monitoring, power tuning, wave debug, and fault/hang diagnostics.

## Risks

- Generated-header drift is the main risk. A single wrong SDMA3 queue offset or base index can write the wrong queue slot, wrong SDMA instance, or unrelated GC register.
- The visible SDMA groups are highly repetitive and are often addressed by arithmetic spacing. If queue spacing differs from the assumed `RLC1 - RLC0` pattern or if one queue macro is out of sequence, only some queues may fail, making the bug workload- and queue-id-dependent.
- The chunk starts inside `SDMA3_RLC5`, so local completeness checks must not flag the missing beginning of that group as a defect in this chunk.
- Doorbell, read/write pointer, ring base, and pointer-poll address registers are DMA control-plane state. Bad offsets can cause silent queue stalls, writes to stale rings, wrong process signaling, or memory corruption.
- `MINOR_PTR_UPDATE`, `PREEMPT`, `CSA_ADDR_*`, `IB_SUB_REMAIN`, and `MIDCMD_*` registers interact with preemption and context-save/restore. Incorrect addressing can break queue eviction, reset recovery, or mid-command preemption after a timeout.
- SDMA RLC registers may be PF- or firmware-owned in SR-IOV and some reset/power states. Bare-metal sequences in AMDGPU explicitly avoid some writes for VFs; using these offsets from the wrong ownership context can conflict with PF/SMU control.
- CAC, DIDT, PWRBRK, and RTAVFS registers influence power estimation, throttling, and adaptive voltage/frequency behavior. Wrong indices may not fail at compile time but can cause throttling regressions, unstable clocks, performance loss, or thermal/power-limit anomalies.
- SQ wave debug registers are sensitive to selected shader/queue/wave context. Reading or writing them without the correct debug selection/locking path can produce misleading diagnostics or disturb wave state.
- Many `ix*` registers are indirect. Confusing indirect offsets with direct MMIO offsets, or using the wrong indirect aperture helper, can address the wrong register block even when the macro value is numerically correct.

## Test Signals

Useful validation is mostly build-time, generated-data, and hardware-integration oriented:

- Compile or preprocess AMDGPU/KFD code paths that include `gc_10_3_0_offset.h`, `gc_10_3_0_sh_mask.h`, and `gc_10_3_0_default.h`.
- Generated-header checks that every complete visible `mmSDMA3_RLC6_*` and `mmSDMA3_RLC7_*` offset has the expected `*_BASE_IDX`, that offset order and queue spacing are monotonic, and that the `SDMA3_RLC5` start is treated as a chunk-boundary exception.
- Cross-check this chunk against the GC 10.3.0 register database and matching sh/mask/default headers for name, offset, base-index, and field-definition alignment.
- KFD SDMA queue tests on GC 10.3.0-class ASICs: create queues across engines and queue ids including higher RLC slots, submit copies, exercise doorbells, poll read/write pointer progression, then destroy and recreate queues.
- Reset, suspend/resume, GPU timeout recovery, and queue eviction tests that verify SDMA RLC state is stopped, saved, restored, and re-enabled correctly.
- SR-IOV VF/PF tests that confirm VF paths avoid PF-owned SDMA/power registers and that allowed doorbell/wptr paths still work.
- Power/performance validation for CAC, DIDT, PWRBRK, SPM, and RTAVFS paths: confirm counters read sanely, sample-delay programming affects expected streams, and power/throttle behavior remains stable under graphics and compute load.
- Wave-debug diagnostics that read `ixSQ_WAVE_*` state under controlled queue selection and verify PC, EXEC, TTMP, mode/status, and trap status are coherent during hangs or debug capture.

## Chunk Notes For Merge

This document is intentionally source-tree aligned and covers only lines 12438-13625 of `gc_10_3_0_offset.h`. Earlier chunks should cover the beginning of `SDMA3_RLC5` and all preceding GC 10.3.0 register blocks. The final per-file report should treat the whole file as a generated GC 10.3.0 register offset map used by AMDGPU, KFD, PM/SMU, debug, and performance-monitoring paths, not as handwritten executable logic.
