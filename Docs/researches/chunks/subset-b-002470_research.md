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
