# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h lines 4974-7439

## Scope

This chunk is a generated AMD GC 10.1.0 register offset header slice. It covers lines 4974 through 7439 of `gc_10_1_0_offset.h` and contains 2,434 `#define` entries: 1,217 register offset macros and 1,217 matching `_BASE_IDX` macros inside this line range. The visible register namespace starts with the tail `_BASE_IDX` for `mmCP_IQ_WAIT_TIME3`, then the first complete offset macro in this chunk is `mmCPC_DDID_BASE_ADDR_LO` at `0x1e6b`. The chunk ends at `mmVGT_PRIMITIVE_TYPE 0x2242`; its `_BASE_IDX` partner is just after the requested range.

The file is declarative only. It has no functions, structs, enums, variables, branches, loops, local storage, locking, allocation, or direct MMIO. Its public API is the preprocessor macro namespace consumed by AMDGPU GC 10.x code through SOC15 register helpers.

## Purpose

`gc_10_1_0_offset.h` maps symbolic GC 10.1.0 register names to register offsets and base-address-selector indices. This chunk describes a large portion of the graphics command processor, shader processor interface, compute queue, global data share, graphics pipeline, color/depth, and user-data register windows.

The range crosses these generated address blocks:

- Lines 4974-5170 continue the preceding CP/CPC block with DDID, GFX HPD/HQD, DMA watch, ring-buffer doorbell, RCIU, UTCL1, soft reset, and CPC graphics control registers.
- `gc_spipdec`, base address `0xc700`, starts at line 5171 and covers SPI arbitration, work-class percentages, graphics debug/trap controls, compute queue reset, CU resource reservation, and shader resource-limit controls.
- `gc_cpphqddec`, base address `0xc800`, starts at line 5289 and covers CP HPD/HQD/MQD queue descriptors, PQ/IB/EOP/context-save/GDS/DDID/dequeue registers for compute queues.
- `gc_didtdec`, base address `0xca00`, starts at line 5437 and exposes DIDT indirect index/data controls.
- `gc_gccacdec`, base address `0xca10`, starts at line 5447 and covers GC CAC, DIDT, throttle, EDC, performance counters, and indirect CAC data ports.
- `gc_tcpdec`, base address `0xca80`, starts at line 5499 and covers TCP watchpoint, UTCL0, and performance-counter filter registers.
- `gc_gdspdec`, base address `0xcc00`, starts at line 5541 and covers GDS per-VMID base/size, GWS/OA ownership, reset, wave-id, context-switch status, and context-switch counters.
- `gc_gfxdec0`, base address `0x28000`, starts at line 5727 and switches to `_BASE_IDX 1`, covering DB, PA, COHER, CB, SPI, SX, VGT, IA, WD, GE, and other graphics pipeline state registers.
- `gc_gfxudec`, base address `0x30000`, starts at line 7011 and covers CP user-facing EOP, streamout, primitive/invocation counters, scratch, atomic/preop, semaphore, DMA, coherency, command-buffer, doorbell, metadata, indirect draw/dispatch, GDS backup, RLC perf, GRBM index, and early VGT user registers.

## Exported API Surface

There are no callable APIs or local types. The exported interface is a pair of generated macros for each register:

- `mm<REGISTER>`: the register offset within the selected GC address block.
- `mm<REGISTER>_BASE_IDX`: the base-address selector used by `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_ENTRY_STR`, `SOC15_REG_GOLDEN_VALUE`, and related AMDGPU helpers.

Important visible macro families include:

- `mmCP_*`, `mmCPC_*`, `mmCPF_*`, and `mmCPG_*`: command processor, compute/gfx queue descriptor, ring-buffer, doorbell, DDID, DMA, semaphore, coherency, scratch, streamout, EOP, counter, and metadata offsets.
- `mmCP_GFX_HQD_*` and `mmCP_HQD_*`: graphics and compute hardware queue descriptor registers used to initialize, deactivate, dump, and restore queues.
- `mmSPI_*`: shader processor interface arbitration, graphics debug/trap, compute queue reset, CU reservation, pixel-shader input controls, barycentric/interpolation controls, temporary-ring size, and shader format registers.
- `mmDIDT_*`, `mmGC_CAC_*`, `mmGC_DIDT_*`, `mmGC_THROTTLE_*`, `mmGC_EDC_*`, `mmEDC_*`, `mmPCC_*`, and `mmPWRBRK_*`: dynamic power, throttling, cumulative activity, error/droop, and related performance monitor register offsets.
- `mmTCP_*`: texture/cache pipe watchpoint and UTCL0/performance-filter offsets.
- `mmGDS_*`: global data share VMID range allocation, GWS/OA ownership, reset, compute max wave id, and context-switch status/counter offsets.
- `mmDB_*`, `mmCB_*`, `mmPA_*`, `mmVGT_*`, `mmIA_*`, `mmWD_*`, `mmGE_*`, `mmTA_*`, `mmCOHER_*`, and `mmSX_*`: fixed-function graphics state, depth/color buffer state, scissor/viewport/rasterization/sample state, vertex/geometry/tessellation state, render target layout, blend controls, and coherency destination base offsets.
- `mmRLC_*` and `mmGRBM_*`: late chunk entries for RLC GPM performance counters and graphics block indexing.

Several macro names alias the same numeric offset where hardware or software supports old/new names. Examples in this chunk include `mmCPC_DDID_*` and `mmCP_DDID_*`, `mmCP_HPD_MES_ROQ_OFFSETS` and `mmCP_HPD_ROQ_OFFSETS`, `mmCP_HQD_DMA_OFFLOAD` and `mmCP_HQD_OFFLOAD`, scheduler/status aliases around `mmCP_HQD_HQ_*`, and low/high aliases such as `mmCP_APPEND_DATA` and `mmCP_APPEND_DATA_LO`.

## Control Flow

This header has no local runtime control flow. Runtime behavior emerges when AMDGPU code includes this file and passes its macros through register helper layers:

1. `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c` includes both `gc/gc_10_1_0_offset.h` and `gc/gc_10_1_0_sh_mask.h`.
2. Register dump and diagnostics tables use macros from this range through `SOC15_REG_ENTRY_STR`, including CP HQD/GFX HQD queue registers.
3. Golden settings tables use graphics pipeline macros such as PA, SPI, TCP, and related GC registers with mask/value pairs.
4. Queue setup, teardown, and restore code uses `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `SOC15_REG_OFFSET`, and `REG_SET_FIELD` against macros from this chunk.
5. The actual sequencing, polling, masking, and field composition lives in `gfx_v10_0.c` and companion code; this header only supplies offsets and base indices.

The `_BASE_IDX` transition is important. CP/CPC/SPI/HQD/DIDT/CAC/TCP/GDS blocks in the early part of the chunk use base index `0`; `gc_gfxdec0` and `gc_gfxudec` register ranges use base index `1`. Consumers must preserve this pairing because the same offset value can mean different physical registers under different SOC15 base selectors.

## State And Persistence Behavior

This chunk stores no software state and persists nothing itself. It names hardware registers whose contents are owned by GC command processor, graphics pipeline, queue, cache, and shader hardware. Persistence and reset behavior are defined by the ASIC, firmware, power domains, and AMDGPU sequencing code, not by this header.

The named hardware state includes:

- Queue and command submission state: MQD/HQD base addresses, VMID, priorities, quantum, ring/pointer addresses, doorbell controls, active/dequeue status, IB controls, EOP buffers, context-save buffers, and DDID counters.
- Synchronization and memory operation state: scratch registers, append/atomic preop registers, semaphore wait/signal addresses, wait timeouts, DMA source/destination/command registers, coherency ranges, and command buffer sizes/bases.
- Graphics pipeline state: depth/stencil/color buffer bases and attributes, HTILE/DCC/FMASK metadata, scissor and viewport windows, sample locations and masks, rasterization and clip controls, shader input/interpolation formats, blend controls, primitive topology, streamout, tessellation, geometry, and draw/dispatch indirect addresses.
- GDS state: per-VMID GDS base/size, GWS and OA ownership, reset masks, compute wave-id limits, and context-switch counters.
- Debug and telemetry state: CP DMA watch registers, SPI graphics debug/trap controls, RLC GPM counters, GC CAC/DIDT/EDC/throttle counters, TCP performance filters, and CP/VGT/PA/SC invocation and primitive counters.

In `gfx_v10_0.c`, many registers from this range back real driver state transitions. For example, graphics MQD initialization reads and composes `mmCP_GFX_HQD_QUEUE_PRIORITY`, `mmCP_GFX_MQD_CONTROL`, `mmCP_GFX_HQD_VMID`, `mmCP_GFX_HQD_QUANTUM`, `mmCP_GFX_HQD_CNTL`, `mmCP_RB_DOORBELL_CONTROL`, and `mmCP_GFX_HQD_RPTR`. Compute queue initialization writes `mmCP_HQD_ACTIVE`, `mmCP_HQD_DEQUEUE_REQUEST`, PQ base/control/pointer registers, EOP base/control registers, MQD base/control registers, and doorbell controls. GDS clear and programming paths use offset arithmetic from `mmGDS_VMID0_BASE`, `mmGDS_VMID0_SIZE`, `mmGDS_GWS_VMID0`, and `mmGDS_OA_VMID0`.

## Dependencies And Integration Points

Syntactically this header depends only on the C preprocessor and its include guard from the full file. Semantically it must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h`, which defines matching register fields used with these offsets.
- AMD's generated GC 10.1.0 register database and address-block layout.
- SOC15 register helper macros in AMDGPU, especially helpers that combine hardware IP, instance, `mm...` offset, and `mm..._BASE_IDX`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c`, the direct consumer in this tree for GFX10 queue management, register dumps, golden settings, GDS setup, ring operations, and debug flows.
- GPU firmware and microcode expectations for CP/MEC/PFP/ME queue state, EOP handling, context save/restore, GDS allocation, and synchronization registers.
- UAPI-observable behavior through command submission, graphics and compute queue scheduling, KFD/AMDKFD integration, VMID/GDS assignment, preemption, reset, suspend/resume, and debug/register-dump paths.

Although the repository path includes `ceph-client`, this file is AMDGPU hardware metadata from a Linux kernel-style source tree. It does not implement Ceph, distributed filesystem behavior, network protocol handling, or persistent filesystem data structures.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong offset or base index compiles cleanly but directs MMIO reads or writes to the wrong register.
- Base-index mistakes are especially dangerous at the `gc_gfxdec0` and `gc_gfxudec` transitions. Many offsets in base index `1` are small values or high user offsets that only make sense under their correct address block.
- Queue descriptor registers are sequencing-sensitive. Wrong CP HQD/MQD/PQ/EOP/doorbell offsets can break queue activation, deactivation, preemption, ring pointer reporting, firmware handoff, or timeout recovery.
- The header exposes aliases for the same offset. Consumers must not assume every macro name identifies a unique register address when building dumps, validation lists, or generated documentation.
- Offset-only macros do not encode bitfields, access permissions, reset values, read-only/write-only behavior, write-one-to-clear behavior, sticky status, self-clearing behavior, clock-domain validity, or power-domain validity. Those semantics must come from the matching shift/mask header, hardware docs, and driver sequencing.
- Graphics state macros in the `gc_gfxdec0` block cover broad rendering state. Bad offsets can appear as subtle rendering corruption, hangs, incorrect depth/color resolves, blend/scissor bugs, or mode-specific failures rather than immediate compile errors.
- GDS offsets are used with register-offset arithmetic over VMIDs. A base offset or stride assumption error can corrupt the wrong VMID allocation or leave stale GWS/OA ownership after queue teardown.
- Counter, debug, and trap registers can affect diagnostics. Incorrect mappings can produce misleading register dumps, failed golden-setting programming, or debug traps that do not correspond to the failing hardware state.
- The chunk boundaries split macro pairs: line 4974 is only the previous register's `_BASE_IDX`, and line 7439 contains `mmVGT_PRIMITIVE_TYPE` without its following `_BASE_IDX`. Merge-time validation should tolerate these boundary artifacts while checking the full file for complete pairs.

## Test Signals

Useful validation is mostly compile-time, generation-time, and hardware-integration oriented:

- Build AMDGPU with GFX10 support so `gfx_v10_0.c` preprocesses successfully against `gc_10_1_0_offset.h` and `gc_10_1_0_sh_mask.h`.
- Mechanically verify that every complete `mm...` macro in the full file has the expected `mm..._BASE_IDX` partner, allowing this chunk's known start and end boundary splits.
- Cross-check this chunk against the authoritative GC 10.1.0 register database, especially address-block boundaries at `gc_spipdec`, `gc_cpphqddec`, `gc_didtdec`, `gc_gccacdec`, `gc_tcpdec`, `gc_gdspdec`, `gc_gfxdec0`, and `gc_gfxudec`.
- Diff generated offsets against nearby GC 10.x variants where the layout should be stable, while preserving known ASIC-specific deltas and aliases.
- Run or inspect GFX10 queue initialization, KIQ/compute queue setup, graphics queue setup, queue teardown, GPU reset, suspend/resume, and SR-IOV VF paths that read or write CP HQD/GFX HQD registers.
- Exercise GDS allocation and cleanup paths for compute queues and KFD workloads, checking `mmGDS_VMID0_*`, `mmGDS_GWS_VMID0`, and `mmGDS_OA_VMID0` offset arithmetic.
- Validate rendering and command submission workloads that stress DB/CB/PA/SPI/SX/VGT state, including depth/stencil, DCC/FMASK, scissor/viewport, MSAA sample locations, blend state, streamout, tessellation, indirect draw, and dispatch.
- Capture register dumps around hangs or resets and confirm CP HQD, CP GFX HQD, GDS, SPI trap, RLC perf, PA/CB/DB, and VGT registers decode at expected addresses.
- Run golden-settings programming paths for GFX10 ASIC variants and check for register-access faults or mismatches around PA, SPI, TCP, and related GC registers.

## Chunk Notes For Merge

This document covers only lines 4974-7439 of `gc_10_1_0_offset.h`. Earlier chunks should own the opening file license/include guard, earlier SDMA/RLC/GC blocks, and the register whose `_BASE_IDX` appears at line 4974. Later chunks should start by completing the `mmVGT_PRIMITIVE_TYPE_BASE_IDX` pair and continue the remaining `gc_gfxudec` and later GC 10.1.0 offset blocks. The final per-file report should treat the whole file as generated ASIC register-offset metadata consumed by AMDGPU GFX10 code, not as handwritten runtime control logic.
