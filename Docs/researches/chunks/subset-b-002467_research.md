# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_default.h lines 1-2944

## Scope

This chunk is the opening segment of AMD's generated GFX 10.3.0 GC register default-value header. It covers the license/header guard and lines 1 through 2944 of `gc_10_3_0_default.h`. The chunk defines 2,826 `mm..._DEFAULT` preprocessor constants, grouped by generated `addressBlock:` comments. It starts at `gc_sdma0_sdma0dec`, includes the full SDMA0 and SDMA1 default blocks, then continues through GRBM, CP, shader, texture, render backend, GCVM/GCMC virtual-memory, CP/HQD, power/throttle, TCP, GDS, and the beginning of the graphics context register block `gc_gfxdec0`.

The content is declarative only. There are no C functions, structs, enums, branches, allocations, runtime loops, or direct MMIO accesses in this header. Its exported surface is the set of reset or recommended hardware default constants used by GC 10.3.0-class AMDGPU code alongside the companion offset and shift/mask headers.

## Purpose

`gc_10_3_0_default.h` gives driver code symbolic default values for GC 10.3.0 memory-mapped registers. These constants let AMDGPU initialization and recovery code start from hardware-approved reset defaults, then override only specific fields with `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and related register helpers. This is safer than reconstructing full register words from hard-coded literals in runtime code.

This chunk is broad because GC 10.3.0 combines graphics, compute, SDMA, virtual memory, cache, and queue-management register surfaces in one generated namespace. The dominant areas are:

- `gc_sdma0_sdma0dec` and `gc_sdma1_sdma1dec`: defaults for SDMA engine control, power/clock control, UTCL1, ring buffers, indirect buffers, doorbells, AQL, RLC queues 0-7, status, timestamps, error logs, and queue reset/preemption surfaces.
- `gc_gcvml2pfdec`, `gc_gcvml2vcdec`, `gc_gcvmsharedpfdec`, and `gc_gcvmsharedvcdec`: graphics VM L2 cache, page fault, invalidation, per-context page-table, aperture, framebuffer, AGP, and TLB defaults.
- `gc_cpdec`, `gc_cppdec`, and `gc_cpphqddec`: command processor defaults for CPC/CPF/CPG/MEC/ME state, VMID handling, queue/HQD state, ring/doorbell registers, interrupts, preemption, DDID, and watchpoints.
- `gc_sqdec`, `gc_shsdec`, `gc_spipdec`, and `gc_spipdec2`: shader queue, scalar/vector cache front-end, SPI arbitration, wave lifetime, thread trace, trap screen, and compute queue defaults.
- `gc_padec`, `gc_rbdec`, `gc_gfxdec0`, and related geometry/raster/backend blocks: PA/SC/DB/CB/VGT viewport, depth, color, raster, scissor, primitive, shader-array, and backend defaults.
- `gc_gceadec`, `gc_gceadec2`, `gc_gceadec3`, `gc_rmi_rmidec`, `gc_tcdec`, `gc_tcpdec`, and `gc_gdspdec`: fabric/arbitration, cache/request routing, texture/cache watch, GDS VMID and context-switch state, and debug/performance register defaults.

## Exported API Surface

There are no callable APIs or local types. The public interface is the macro namespace:

- `mm<REGISTER>_DEFAULT`: 32-bit hexadecimal default value for a register whose address is defined as `mm<REGISTER>` in `gc_10_3_0_offset.h`.
- Register field interpretation is supplied separately by `gc_10_3_0_sh_mask.h`, whose `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros are consumed by `REG_SET_FIELD` and `REG_GET_FIELD`.
- The header guard is `_gc_10_3_0_DEFAULT_HEADER`.

Important defaults visible in this chunk include `mmSDMA0_POWER_CNTL_DEFAULT`, `mmSDMA0_GFX_RB_CNTL_DEFAULT`, `mmSDMA1_POWER_CNTL_DEFAULT`, `mmGRBM_GFX_CLKEN_CNTL_DEFAULT`, `mmGCVM_L2_CNTL3_DEFAULT`, `mmGCVM_L2_CNTL4_DEFAULT`, `mmGCVM_L2_CNTL5_DEFAULT`, `mmGCVM_CONTEXT0_CNTL_DEFAULT` through `mmGCVM_CONTEXT15_CNTL_DEFAULT`, `mmGCMC_VM_MX_L1_TLB_CNTL_DEFAULT`, `mmCP_CONTEXT_CNTL_DEFAULT`, `mmCP_HQD_PERSISTENT_STATE_DEFAULT`, `mmCP_HQD_PQ_CONTROL_DEFAULT`, `mmGC_THROTTLE_CTRL_DEFAULT`, `mmGDS_VMID*_SIZE_DEFAULT`, `mmGDS_GWS_VMID*_DEFAULT`, and early `gc_gfxdec0` graphics context defaults such as DB, PA_SC, CB, VGT, and viewport/scissor registers.

Many default values are zero because hardware state is either reset/disabled, programmed dynamically by driver initialization, or read back at runtime. Non-zero values capture hardware-approved reset policy, queue defaults, cache fragment defaults, fault policy defaults, arbiter/timing defaults, resource sizes, and known-good control bits.

## Register Areas Covered

The SDMA blocks are complete for SDMA0 and SDMA1 in this chunk. Each engine has common engine defaults, GFX/PAGE queue defaults, and RLC0-RLC7 queue defaults. The queue register pattern repeats for ring-buffer control/base/read/write pointers, write-pointer polling, indirect-buffer control/base/size, context status, doorbell, watermark, CSA, preemption, AQL, and mid-command state. Defaults such as `0x80840000` for GFX/PAGE ring control, `0x80040000` for RLC ring control, `0x00403000` for write-pointer polling control, and `0x00004000` for AQL control indicate non-zero hardware queue policy even though ring addresses and pointers are initialized to zero.

The GRBM and PA/RB sections establish core graphics management and geometry/backend defaults. GRBM includes status, reset, trap, scratch, fence, interrupt, GFX clock enable, and UTCL2 invalidation range defaults. PA and RB cover VGT/WD/GE setup, primitive and shader-array config, raster/binning defaults, depth/color backend configuration, backend disable/redundancy defaults, GB address config, CB/DB cache and arbiter defaults, and user-visible mirror registers.

The SQ/SH/SPI/TCP sections provide defaults for shader execution and instrumentation surfaces. These include shader queue config, LDS config, thread trace buffers/control/status, watchpoint registers, SQC UTCL0 controls, SPI pixel/compute wave limits, trap screen addresses, wave lifetime counters, GDS/SX buffer sizing, compute queue reset and CU resource reservation, and TCP watch/perf-counter filters.

The GCVM and GCMC sections are the most directly consumed by `gfxhub_v2_1.c`. They define L2 cache defaults, page fault control, invalidate request/ack/address-range defaults for engines 0-17, context control defaults for VM contexts 0-15, per-context page table base/start/end defaults, PTE cache fragment-size defaults, framebuffer and aperture defaults, cacheable/local-HBM ranges, SR-IOV/virtual reset hooks, and L1 TLB defaults.

The CP and HQD sections define command processor defaults. The `gc_cpdec` and `gc_cppdec` ranges cover CP status, stalls, micro-engine/MEC counters, interrupt controls, context control, VMID/preemption/suspend state, queue indexing, program-counter starts, DDID, GFX HQD, ring/doorbell, DMA watchpoints, fetcher and timestamp state. The `gc_cpphqddec` block is the compute HQD/MQD programming surface: queue active/VMID/priority, persistent state, PQ/IB bases and pointers, dequeue/offload/semaphore/message controls, EOP event queue, context save areas, GDS resource state, AQL, DDID, and dequeue status.

The GDS block assigns per-VMID GDS base/size and GWS/OA defaults, then exposes reset, maximum wave id, context-switch counters/status, and memory clean defaults. The `gc_gfxdec0` block begins per-context graphics state defaults for DB render/depth/stencil control, HTILE/Z/stencil base addresses, coherency destinations, scissor and viewport arrays, raster config, CP context identity, VGT index registers, CB blend/DCC/stencil state, and PA_CL viewport scale/offset entries. This chunk ends mid-`gc_gfxdec0` at `mmPA_CL_VPORT_XSCALE_15_DEFAULT`, so the final per-file report must merge later chunks before treating graphics context coverage as complete.

## Control Flow And State Behavior

This file has no local control flow. Runtime behavior appears when AMDGPU code includes the generated constants and uses them as initial register words or as masks for preserving default bit values.

The main state behavior implied by the constants is hardware state initialization:

- SDMA queue state persists in MMIO registers for ring buffer addresses, pointers, polling, doorbells, IB state, context status, and preemption until reset, queue teardown, or driver reprogramming.
- GCVM/GCMC state controls GPU virtual memory translation, L1/L2 cache behavior, invalidation engines, page fault handling, page table roots, aperture bounds, and default fault addresses.
- CP/HQD state controls compute and graphics queue scheduling, VMID binding, preemption, persistent MQD state, EOP/event queues, DDID, and context save/restore surfaces.
- Graphics context state covers raster, viewport, scissor, depth/stencil/color, primitive assembly, and shader-array configuration values that command submission paths may load or patch as part of context programming.
- Debug and status defaults are represented the same way as writable controls, but actual read-only, sticky, clear-on-read, and write-one-to-clear behavior is determined by the hardware register specification and the access helpers, not by this header.

No software persistence is implemented here. The constants are compile-time preprocessor values. Hardware registers persist according to ASIC reset domains, power-gating domains, SR-IOV PF/VF ownership, firmware programming, and runtime driver writes.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. Semantically, the file is part of a generated register triplet:

- `gc_10_3_0_offset.h` defines `mm...` addresses and base indices for the same register names.
- `gc_10_3_0_sh_mask.h` defines field shifts and masks for those registers.
- `gc_10_3_0_default.h` defines reset/default full-register words.

The direct include of this exact default header in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.c`, which includes all three GC 10.3.0 generated headers. Its GFXHUB initialization uses this chunk's `mmGCVM_L2_CNTL3_DEFAULT`, `mmGCVM_L2_CNTL4_DEFAULT`, and `mmGCVM_L2_CNTL5_DEFAULT` as base values before setting cache and fragment-size fields. It also writes many GCVM/GCMC registers whose offsets and fields are paired with defaults in this chunk, including context controls, page-table roots/ranges, invalidation engines, fault default addresses, framebuffer location, AGP aperture, and L1/L2 TLB/cache controls.

Other GC 10.3.0 consumers include `sdma_v5_2.c`, `amdgpu_amdkfd_gfx_v10_3.c`, and `amdgpu_sdma.c`, which include the offset and shift/mask headers and program many registers covered by these defaults. KFD queue-management code relies on CP/HQD, SH, and SDMA register layouts from the same namespace. SDMA code uses the SDMA0/1 register offsets and field masks for queue, doorbell, and ring programming; related SDMA generation headers and older SDMA code also demonstrate the default-value pattern for preserving reset timing bits.

This header also integrates indirectly with SOC15 register access infrastructure: `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `WREG32_FIELD15`, `REG_SET_FIELD`, and `REG_GET_FIELD`. The generated defaults are meaningful only when used with the matching IP block, instance, base index, and ASIC version.

## Risks

- Generated-header drift is the central risk. If a default value no longer matches the ASIC register database, driver code that seeds a register from `mm..._DEFAULT` can silently program reserved or changed bits.
- Full-register defaults do not encode access permissions. A consumer must know whether a register is writable, read-only, sticky, clear-on-read, PF-only, VF-copy, or firmware-owned.
- Defaults reused as base values can preserve unwanted reset bits if the runtime code forgets to override an ASIC-specific field. This is especially relevant for GCVM L2/cache controls, protection-fault policy, CP/HQD queue state, and SDMA queue control.
- The SDMA0 and SDMA1 sections are highly repetitive. A copy/generation error in one queue instance or engine can create asymmetric queue failures that only appear for specific engines or RLC queues.
- VM context defaults cover contexts 0-15 and invalidation engines 0-17. Incorrect distances or mismatched register names between offset/default/mask headers can corrupt neighboring VMID or invalidate-engine state.
- CP/HQD and KFD queue registers are sensitive to ordering and ownership. Wrong defaults for persistent state, PQ/IB/EOP control, dequeue status, or context-save registers can cause queue hangs, lost interrupts, or failed preemption.
- Many graphics context defaults are zero, but the early `gc_gfxdec0` block also contains non-zero raster and backend defaults. Accidentally treating all context state as zeroed can miss required reset policy.
- This chunk ends in the middle of `gc_gfxdec0`; merge-time analysis should not conclude that PA_CL, VGT, CB, DB, and other graphics context defaults are complete until later chunks are reconciled.

## Test Signals

Useful validation is build-time, generation-time, and hardware-integration oriented:

- Compile AMDGPU targets that include `gfxhub_v2_1.c`, `sdma_v5_2.c`, and `amdgpu_amdkfd_gfx_v10_3.c` with `gc_10_3_0_offset.h`, `gc_10_3_0_sh_mask.h`, and this default header visible.
- Preprocessor/static checks that every `mm..._DEFAULT` in this chunk has a matching `mm...` offset in `gc_10_3_0_offset.h`; when fields are used, corresponding shift/mask definitions should exist in `gc_10_3_0_sh_mask.h`.
- Generation checks against the authoritative GC 10.3.0 register database, especially for non-zero defaults and repeated SDMA/GCVM/HQD instance arrays.
- GFXHUB bring-up tests on GC 10.3.0-class ASICs: GART enable/disable, VM context programming, page-table base/range setup, L1/L2 TLB and cache initialization, invalidation engine requests/acks, VM fault logging, default-page fault redirection, SR-IOV PF/VF handling, and suspend/resume.
- SDMA tests: engine initialization, GFX/PAGE/RLC queue setup, doorbell writes, ring read/write pointer behavior, IB execution, preemption, queue reset, UTCL1/XNACK behavior, and power-gating transitions.
- KFD/compute tests: HQD/MQD load/unload, VMID/PASID mapping, compute queue scheduling, AQL queues, EOP event handling, dequeue/preemption, context save/restore, and GDS/GWS allocation by VMID.
- Graphics tests: context creation, viewport/scissor programming, primitive assembly, rasterization, depth/stencil/color target state, render backend/cache behavior, wave/thread trace and watchpoint diagnostics.
- Runtime register dumps around `gfxhub_v2_1_init_cache_regs()` should show `GCVM_L2_CNTL3/4/5` initialized from the defaults in this chunk and then patched only in the intended fields.

## Chunk Notes For Merge

This document is source-tree aligned and covers only lines 1-2944 of `gc_10_3_0_default.h`. Earlier lines do not exist; later chunks must cover the remainder of `gc_gfxdec0` and all subsequent address blocks in the 7,275-line file. The final per-file document should treat the complete file as a generated GC 10.3.0 register default map paired with `gc_10_3_0_offset.h` and `gc_10_3_0_sh_mask.h`, with this chunk contributing the SDMA0/1, GCVM/GCMC, CP/HQD, GDS, shader, backend, and opening graphics-context default coverage.
