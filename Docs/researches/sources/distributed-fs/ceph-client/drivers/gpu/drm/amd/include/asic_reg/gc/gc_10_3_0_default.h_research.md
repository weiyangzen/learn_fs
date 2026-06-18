# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_default.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002467`: lines 1-2944, `Docs/researches/chunks/subset-b-002467_research.md`
- `subset-b-002468`: lines 2945-5886, `Docs/researches/chunks/subset-b-002468_research.md`
- `subset-b-002469`: lines 5887-7275, `Docs/researches/chunks/subset-b-002469_research.md`

## Chunk Research

### subset-b-002467: lines 1-2944

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

### subset-b-002468: lines 2945-5886

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_default.h lines 2945-5886

## Scope

This chunk is the middle slice of the generated GC 10.3.0 default-register header. It covers lines 2945-5886 of `gc_10_3_0_default.h`, containing 2,835 `#define ..._DEFAULT` constants, of which 2,350 are zero defaults and 485 are non-zero hardware reset/programming defaults. There are no C functions or types in this range; the API surface is the macro namespace consumed with the matching GC offset and shift/mask headers.

The chunk starts inside the `gc_gfxdec0` address block inherited from line 2707 and ends inside `gc_sdma3_sdma3dec`. Address-block comments inside this range introduce `gc_gfxudec`, `gc_cprs64dec`, `gc_gusdec`, GL1/GL2/cache blocks, perf-monitor blocks, RLC/RLCS blocks, hypervisor/SR-IOV blocks, PSP/GCVM blocks, and the first half of SDMA2 plus the opening SDMA3 public-engine defaults.

## Purpose

The file records ASIC-specific reset/default values for AMD GC 10.3.0 registers. This chunk is mainly a data contract for driver code that needs known baseline values when programming graphics, cache, command processor, micro-engine scheduler, RLC power/firmware, VM, performance counter, and SDMA register state.

Most entries are hardware state defaults rather than values actively written by this header itself. Consumers include `amdgpu/gfxhub_v2_1.c`, which includes `gc/gc_10_3_0_default.h` alongside `gc_10_3_0_offset.h` and `gc_10_3_0_sh_mask.h` and uses default macros such as `mmGCVM_L2_CNTL3_DEFAULT`, `mmGCVM_L2_CNTL4_DEFAULT`, `mmGCVM_L2_CNTL5_DEFAULT`, and field default macros while programming the GFXHUB VM path.

## Important Macro Groups

- `gc_gfxdec0` continuation, lines 2945-3350: viewport, clip/user clip plane, SPI pixel-shader input, SX blend/downconvert, CB blend/color target, DB depth, PA rasterizer, IA/VGT draw/tessellation/streamout, and CP draw/window defaults. Only `mmPA_SC_MODE_CNTL_1_DEFAULT = 0x06000000` and `mmIA_MULTI_VGT_PARAM_DEFAULT = 0x000000ff` are non-zero in this continued section; most render-state defaults are all-zero placeholders until command submission programs them.
- `gc_gfxudec`, lines 3351-3677: user/config graphics defaults covering scratch registers, CP DMA/coherency, CP/ME/PFP/CE queues and doorbells, GRBM index defaults, VGT piped parameters, screen extents, GDS append/atomic state, and CP GDS atom registers. Notable non-zero baselines include `mmCP_COHER_START_DELAY_DEFAULT = 0x20`, `mmCP_DMA_CNTL_DEFAULT = 0x00100020`, `mmGRBM_GFX_INDEX_DEFAULT = 0xe0000000`, `mmVGT_TF_RING_SIZE_UMD_DEFAULT = 0x0000c000`, `mmIA_MULTI_VGT_PARAM_PIPED_DEFAULT = 0x006000ff`, screen extent sentinel pairs `0x7fff7fff`/`0x80008000`, and `mmGDS_ATOM_COMPLETE_DEFAULT = 1`.
- `gc_cprs64dec`, lines 3678-3762: MES command processor scheduler defaults. Key values include `mmCP_MES_PRGRM_CNTR_START_DEFAULT = 0x800`, `mmCP_MES_CNTL_DEFAULT = 0x40000000`, pipe priority defaults of `2`, process quanta of `8`, and selected GP registers initialized to `0x00002001` or `0x40000000`.
- `gc_gusdec`, `gc_gl1dec`, `gc_chdec`, and `gc_gl2dec`, lines 3763-3919: graphics fabric/cache defaults. GUS contains many non-zero arbitration, priority, credit, reserve, and FIFO settings; GL1/CH provide burst masks and pipe steering; GL2 programs L2 control, address match masks/sizes, invalidate-related default bits, cache-manager controls, prefetch flags, and pipe steering.
- Perf blocks, lines 3920-4579: `gc_perfddec` and per-engine `perfddec` blocks are mostly zero result/control placeholders, while `gc_perfsdec` and the SDMA/GCVML2 `perfsdec` blocks provide disabled/select-all counter selector defaults. Common non-zero sentinel values are `0x000fffff`, `0x000003ff`, `0x0000ffff`, and result-control `0x04000000`.
- `gc_grtavfsdec`, lines 4580-4595: RTAVFS status/control defaults, with soft reset, PSM, and clock control defaulting to enabled/non-zero values.
- `gc_rlcdec`, `gc_rlcrdec`, and `gc_rlcsdec`, lines 4596-4958: RLC firmware, power-gating, scheduler, interrupt, SPM, SRM, and RLCS state. Important non-zero defaults include `mmRLC_CNTL_DEFAULT = 1`, GPM timer intervals `0x63`, load-balancer masks `0xffffffff`, clock-gating/power-gating controls, doorbell controls `0x00260000`, UTCL1 controls `0x80`, SPP thresholds `0x009f009f`, RLCS exception/auxiliary registers `0x0003b984`, and RLCS deep-sleep/power-brake defaults.
- `gc_hypdec` and per-SDMA hyp blocks, lines 4966-5210: hypervisor and SR-IOV register defaults for CP instruction-cache base controls, MES local aperture/masks/bounds, GFX pipe priority, GRBM save/restore index data, IOV interrupt/status/mask registers, and SDMA context/public register type maps. The per-SDMA hyp defaults repeat for SDMA0-3 and identify which SDMA registers are context, public, and virtualized.
- `gc_gcvmsharedhvdec`, `gc_pspdec`, and `gc_gcvml2pspdec`, lines 5211-5300: shared GCVM/IOMMU/PSP defaults. `mmGCVM_IOMMU_MMIO_CNTRL_1_DEFAULT = 0x100` and `mmGCVM_L2_ID_CTRL0..7_DEFAULT = 0xffffffff` plus `mmGCVM_L2_ID_CTRL_HI_DEFAULT = 0x0000ffff` are the significant non-zero entries.
- `gc_sdma2_sdma2dec`, lines 5301-5822: full SDMA2 public engine defaults through all exposed queues. This includes engine power/clock/control, GB address config, status, EDC, UTCL1, TLBI/GCR, GFX/PAGE rings, and RLC0-RLC7 ring contexts. Queue families share repeated non-zero patterns: ring control `0x80840000` for GFX/PAGE and `0x80040000` for RLC queues, write-pointer poll `0x00403000`, IB control `0x00000100`, context status `0x4` or `0x5`, dummy register `0x0000000f`, and AQL control `0x00004000`.
- `gc_sdma3_sdma3dec`, lines 5823-5886: the opening SDMA3 engine defaults, mirroring the SDMA2 global engine setup through `mmSDMA3_CRD_CNTL_DEFAULT = 0x1850c640`. The remainder of SDMA3 is in the next chunk.

## Control Flow And State

This header has no executable control flow. Runtime behavior emerges when init, resume, virtualization, performance-monitor, or debugging paths combine:

- register offsets from `gc_10_3_0_offset.h`,
- bit definitions from `gc_10_3_0_sh_mask.h`,
- these `_DEFAULT` values, and
- `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, and related AMDGPU register helpers.

The defaults describe hardware state rather than persistent software state. Persistence is indirect: if the driver saves/restores VM, RLC, SDMA, or performance state around reset/suspend, these constants provide expected reset baselines or seed values. Registers such as RLC status/masks, SDMA ring pointers, VM context addresses, and perf counters may later be written with live device-specific values, so the header should not be read as the final runtime state after initialization.

## Dependencies And Integration Points

- Generated ASIC register headers: this file is meaningful only with the matching offset and shift/mask headers under `include/asic_reg/gc/`.
- AMDGPU SOC15 register access layer: consumers use the `mm...` symbolic names and defaults through SOC15 register helper macros.
- GFXHUB VM code: `amdgpu/gfxhub_v2_1.c` includes this header and uses GCVM defaults while configuring page-table, system-aperture, L2, fault, and TLB invalidation behavior.
- RLC/RLCS firmware and power management: RLC defaults in this chunk are coupled to firmware expectations, power-gating behavior, clock gating, scheduler timing, and interrupt routing.
- SDMA engine setup: the SDMA2/SDMA3 values are tied to ring allocation, doorbell setup, polling mode, indirect buffers, context save area addresses, AQL controls, and virtualization register classification.
- Performance tooling: perf selector defaults such as `0x000fffff`/`0x000003ff` and result controls establish the inactive/reset state for counter programming.

## Risks

- The source is generated register data. Manual edits can silently desynchronize the defaults from the ASIC register database and create bring-up, reset, virtualization, or suspend/resume bugs that do not appear as normal compile errors.
- Chunk boundaries split hardware blocks: the `gc_gfxdec0` block starts before this chunk, and the `gc_sdma3_sdma3dec` block continues after it. Any merged per-file research or generated validation should reconcile those partial blocks.
- Many zero defaults are intentional. Treating zero as missing data would be wrong for render state, ring pointers, page table addresses, perf results, and scratch/context registers.
- Non-zero sentinel values carry hardware meaning: examples include `0xe0000000` GRBM broadcast index values, `0xffffffff` masks, `0x000fffff` perf selector sentinels, and SDMA queue controls. Small bit changes may affect all shader engines, virtualization exposure, or queue scheduling.
- Repeated SDMA queue blocks are structurally similar but not always identical. For example GFX/PAGE queue ring-control/context defaults differ from RLC queue defaults, and SDMA2 is complete here while SDMA3 is only partially covered.

## Test Signals

- Build coverage: compile the AMDGPU driver paths that include `gc_10_3_0_default.h`, especially `amdgpu/gfxhub_v2_1.c`, to catch missing/renamed macros.
- Register-header consistency: generated checks should confirm each `_DEFAULT` macro has matching offset and shift/mask definitions where applicable, and that duplicate SDMA/RLC queue families preserve the expected naming pattern.
- Runtime init/reset: boot or module-load on GC 10.3.x hardware should exercise GFXHUB setup, RLC initialization, SDMA ring creation, suspend/resume, and GPU reset paths without register timeout, VM fault storms, or ring test failures.
- Virtualization/SR-IOV: VF/PF tests should validate the `gc_hypdec` and per-SDMA hyp defaults by checking virtualized register access, SDMA context/public register classification, and IOV interrupt masks/status defaults.
- Performance counter tests: perf counter selection and readback should start from disabled/sentinel defaults and produce sane results after explicit programming.
- SDMA queue tests: SDMA2 GFX/PAGE/RLC queue ring tests should confirm doorbell, write-pointer polling, IB execution, context status, AQL, and preemption behavior. SDMA3 testing must include the next chunk because this slice ends before SDMA3 queue contexts.

### subset-b-002469: lines 5887-7275

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_default.h lines 5887-7275

## Scope

This chunk is the final segment of the generated AMD GC 10.3.0 default-register header. It contains only C preprocessor `#define` constants for register reset/default values; it declares no functions, structs, enums, storage objects, or executable initialization code.

The range starts in the `mmSDMA3_*` register-default area at `mmSDMA3_AQL_STATUS_DEFAULT`, covers SDMA3 queue defaults for the GFX, PAGE, and RLC0-RLC7 contexts, then transitions through generated indexed register address blocks:

- `gccacind`: global graphics CAC, PCC, power-brake, EDC, LUT, fixed-pattern counter, and hardware-LUT status defaults.
- `secacind`: per-shader-engine CAC selector/control defaults.
- `spmglbind`: global SPM sample-delay defaults.
- `spmind`: shader-engine and shader-array SPM sample-delay defaults.
- `grtavfsind`: RTAVFS register-table defaults.
- `spiind`: `ixSA_WGP_BLK_ID_DEFAULT`.
- `sqind`: SQ wave debug and interrupt-word defaults.
- `didtind`: DIDT/EDC throttle defaults for SQ, DB, TD, and TCP, ending with stall-event counters and the file `#endif`.

## Purpose

`gc_10_3_0_default.h` is generated hardware metadata for AMDGPU GC 10.3 ASICs. Its `_DEFAULT` macros give the reset value associated with register names from the matching GC register offset header. Driver code includes this header with `gc_10_3_0_offset.h` and `gc_10_3_0_sh_mask.h` so ASIC-specific code can use the correct register addresses, bit fields, and known reset values for this graphics generation.

This chunk documents late-file default surfaces rather than programming policy. The SDMA3 defaults describe the baseline state for the fourth SDMA engine's queue machinery: queue control, ring and indirect-buffer state, read/write pointers, doorbells, write-pointer polling, context status, preemption, AQL controls, mid-command scratch capture, and queue reset/status registers. The CAC/SPM/RTAVFS/DIDT indexed sections describe baseline power, droop, performance-monitoring, sampling, debug, and throttling registers used by graphics, shader-engine, shader-array, and texture/cache clients.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The important interface is the generated macro convention:

- `mm<REGISTER>_DEFAULT` gives a default for a memory-mapped register named by the matching `mm<REGISTER>` offset macro.
- `ix<REGISTER>_DEFAULT` gives a default for an indexed register accessed through an indirect address block.
- The corresponding register addresses live in `gc_10_3_0_offset.h`.
- The field shifts and masks live in `gc_10_3_0_sh_mask.h`.
- Normal consumers combine these definitions with AMDGPU register helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, and `REG_GET_FIELD`.

Notable macro groups in this chunk:

- `mmSDMA3_*`: starts with engine-level defaults such as `AQL_STATUS` = `0x00000003`, `TLBI_GCR_CNTL` = `0x40180454`, `STATUS4_REG` = `0x00000001`, and mostly-zero status, address, timestamp, scratch, interrupt, hole-address, and queue-reset defaults.
- `mmSDMA3_GFX_*` and `mmSDMA3_PAGE_*`: queue defaults for graphics and page queues. Their ring-buffer control defaults are `0x80840000`, write-pointer polling defaults are `0x00403000`, indirect-buffer control defaults are `0x00000100`, AQL control defaults are `0x00004000`, dummy-register defaults are `0x0000000f`, and the remaining pointer/base/status/doorbell/mid-command fields mostly reset to zero. `GFX_CONTEXT_STATUS_DEFAULT` is `0x00000005`; `PAGE_CONTEXT_STATUS_DEFAULT` is `0x00000004`.
- `mmSDMA3_RLC0_*` through `mmSDMA3_RLC7_*`: eight RLC queue contexts with repeated 44-register layouts. Each RLC queue uses `RB_CNTL_DEFAULT` = `0x80040000`, `RB_WPTR_POLL_CNTL_DEFAULT` = `0x00403000`, `IB_CNTL_DEFAULT` = `0x00000100`, `CONTEXT_STATUS_DEFAULT` = `0x00000004`, `DUMMY_REG_DEFAULT` = `0x0000000f`, `RB_AQL_CNTL_DEFAULT` = `0x00004000`, and zero defaults for base pointers, read/write pointers, doorbells, preemption, CSA, mid-command data, and status.
- `ixPCC_*`, `ixPWRBRK_*`, and `ixEDC_*`: power control and droop counter defaults. Stall-pattern controls default to nonzero values (`ixPCC_STALL_PATTERN_CTRL_DEFAULT` = `0x07fa0401`, `ixPWRBRK_STALL_PATTERN_CTRL_DEFAULT` = `0x00fa0401`), while the pattern payloads, hysteresis, and stretch/unstretch counters reset to zero.
- `ixGC_CAC_*`: global CAC metadata. `ixGC_CAC_CNTL_DEFAULT` is `0x000001fe`; selector/override fields reset to zero; CAC weights are generally `0x00010001` or `0x00000001`; the many `ixGC_CAC_ACC_*` activity accumulators and `ixGC_CAC_OVRD_*` override registers default to zero.
- `ixRELEASE_TO_STALL_*`, `ixSTALL_TO_RELEASE_*`, `ixSTALL_TO_PWRBRK_*`, and `ixPWRBRK_*_LUT_*`: LUT entries for stall/release and power-brake transitions, all zero defaults in this range.
- `ixFIXED_PATTERN_PERF_COUNTER_1_DEFAULT` through `_10_DEFAULT` and `ixHW_LUT_UPDATE_STATUS_DEFAULT`: fixed-pattern counters and update status, all zero defaults.
- `ixSE_CAC_*`: per-shader-engine CAC ID, control, override selector, and override value; `CNTL` mirrors the global `0x000001fe` default and the other values are zero.
- `ixGLB_*_SAMPLEDELAY_DEFAULT`: global SPM sample-delay registers for CPG/CPC/CPF, GDS/GCR/PH/GE/GUS, CHA/CHC, ATCL2/VML2, SDMA0-SDMA3, GL2A, GL2C0-15, EA0-15, and GE2SE links. All default to zero.
- `ixSE_*_SAMPLEDELAY_DEFAULT`: shader-engine SPM sample-delay registers for SPI, SQG, CBR, DBR, PA, SX, GL1, CB/DB, SC, RMI, and WGP-local TA/TD/TCP lanes for SA0 and SA1. All default to zero.
- `ixRTAVFS_REG0_DEFAULT` through `ixRTAVFS_REG165_DEFAULT`: RTAVFS table entries. Many entries are zero, but the table contains important nonzero reset words including repeated `0x01000000` values, `ixRTAVFS_REG134_DEFAULT` = `0x000211cd`, `REG135` = `0x000af12c`, `REG136` = `0x00000010`, `REG138` = `0x00000008`, `REG144` = `0x0015c040`, `REG146` = `0x83c00260`, `REG147` = `0x00000800`, `REG149`-`REG159` = `0x000000ff`, `REG161` = `0xcccdbcdd`, and `REG162` = `0x2587d190`.
- `ixSA_WGP_BLK_ID_DEFAULT`: SPI-indexed WGP block selector default, zero.
- `ixSQ_WAVE_*` and `ixSQ_INTERRUPT_WORD_*`: SQ wave debug state, trap temporary registers, program counter pieces, execution masks, shader-cycle counter, and interrupt payload words. Every SQ macro in this range defaults to zero.
- `ixDIDT_SQ_*`, `ixDIDT_DB_*`, `ixDIDT_TD_*`, and `ixDIDT_TCP_*`: dynamic droop/throttle defaults. The four clients share common defaults for `CTRL0` (`0x0000ff00`), `CTRL1` (`0x00ff00ff`), `CTRL2` (`0x18800004`), `STALL_CTRL` (`0x00fff000`), `TUNING_CTRL` (`0x00010004`), `STALL_AUTO_RELEASE_CTRL` (`0x00ffffff`), `CTRL3` (`0x00038000`), stall patterns (`0x01010001`, `0x11110421`, `0x25291249`, `0x00002aaa`), `EDC_CTRL` (`0x00001c00`), `EDC_TIMER_PERIOD` (`0x00003fff`), and mostly-zero thresholds, weights, statuses, overflow, rolling-power-delta, PCC counter, and throttle-control fields. `DIDT_TCP_CTRL_OCP_DEFAULT` is `0x0000ffff`; SQ/DB/TD OCP defaults are `0x000000ff`.

## Control Flow

This header has no runtime control flow. The only direct behavior is compile-time substitution of constants by the C preprocessor.

The implied consumer flow is:

1. Include the GC 10.3 offset, shift/mask, and default headers for a target ASIC block.
2. Select a register through an `mm...` or `ix...` macro.
3. Read, write, or read-modify-write that register through SOC15 and indirect-register helpers.
4. Use the `_DEFAULT` value as hardware reset documentation, a baseline for initialization tables, or a comparison/restoration value.

The SDMA3 RLC queue defaults integrate with runtime code that computes queue-register spacing from register symbols. For example, `amdgpu_amdkfd_gfx_v10_3.c` derives SDMA engine and RLC queue offsets using `mmSDMA3_RLC0_RB_CNTL` and adjacent RLC register spacing. This chunk does not execute that arithmetic, but the naming and generated layout must remain consistent with those consumers.

For DIDT/CAC/SPM/RTAVFS blocks, real sequencing occurs in power-management, performance-monitoring, debug, or hardware-init code outside this file: select an indirect address block, program thresholds, enable/disable counters or throttling, poll status, and clear counters. These defaults define the reset baseline before those sequences run.

## State And Persistence

The chunk stores no software state. All macros are compile-time constants and do not allocate memory or persist data.

The represented state is hardware state:

- SDMA3 queue state includes ring-buffer base addresses, read/write pointers, write-pointer polling addresses, doorbell state, context-save addresses, indirect-buffer state, preemption, AQL mode, and mid-command capture words.
- CAC and EDC state includes power/droop control words, stall patterns, activity weights, override registers, accumulators, counters, and transition LUT entries.
- SPM state includes sampling delay selectors for global, shader-engine, shader-array, and per-WGP units.
- RTAVFS state is a generated register table with several nonzero reset values that likely represent fused or specification-defined adaptive-voltage/frequency defaults.
- SQ state includes wave debug selection and readout registers that reset to idle/zero until a wave is selected and observed.
- DIDT state includes throttling thresholds, OCP limits, stall patterns, EDC timers, event counters, and rolling power metrics.

Hardware reset, GPU suspend/resume, ASIC initialization, runtime power management, and GPU reset paths are the events that make these defaults relevant. Any software that reinitializes these blocks must treat the defaults as ASIC-generation-specific, not as portable values.

## Dependencies And Integration Points

This generated header depends on the surrounding ASIC register description set:

- `gc_10_3_0_offset.h` supplies the register offsets and indirect register names that correspond to these `_DEFAULT` macros.
- `gc_10_3_0_sh_mask.h` supplies field shifts and masks for interpreting or modifying each value.
- SDMA-specific offset headers also contain SDMA3 register names used by consumers and by generated cross-block register layouts.
- AMDGPU SOC15 helpers provide address calculation and register I/O.
- KFD/AMDKFD queue code relies on the SDMA3 RLC register layout for MQD queue setup and per-engine/per-queue offset computation.
- `gfxhub_v2_1.c` includes this default header with the matching GC 10.3 offset and shift/mask headers for graphics hub programming.

The chunk is source-tree-aligned with `drivers/gpu/drm/amd/include/asic_reg/gc/`. It should be kept synchronized with any regenerated GC 10.3 register headers; manually changing a default without the corresponding offset and mask metadata risks creating inconsistent hardware descriptions.

## Risks And Edge Cases

- Generated-header drift is the main risk. If defaults, offsets, and masks are regenerated from different hardware databases or ASIC revisions, code can compile while silently using mismatched reset values.
- Queue layout symmetry is assumed by SDMA/KFD code. The repeated SDMA3 GFX/PAGE/RLC queue macro groups must stay ordered and named consistently because consumers derive offsets from adjacent register symbols rather than storing every queue's full address table.
- Nonzero SDMA queue-control defaults are meaningful. Values such as `0x80840000`, `0x80040000`, `0x00403000`, `0x00000100`, and `0x00004000` should not be normalized to zero during cleanup because they encode reset behavior for ring buffers, polling, IB handling, and AQL state.
- RTAVFS register names are opaque (`REG0`-`REG165`), making review harder. Nonzero words such as `0x83c00260`, `0xcccdbcdd`, and `0x2587d190` require validation against the generated source or hardware database rather than semantic code inspection.
- DIDT blocks are mostly symmetric but not perfectly identical: TCP has a wider OCP default (`0x0000ffff`) than SQ/DB/TD (`0x000000ff`), and DB lacks `EDC_STALL_DELAY_2`/`3` macros in this generated range while SQ, TD, and TCP include them. Treat these differences as hardware-description facts unless the upstream generator changes.
- The header itself cannot validate hardware behavior. A wrong default may only show up as power-management instability, counter mismatch, queue bring-up failure, suspend/resume regression, or ASIC-specific performance anomalies.

## Test Signals

There are no unit-testable functions in this chunk. Useful validation signals are integration and build oriented:

- Build coverage for AMDGPU and AMDKFD code that includes `gc_10_3_0_default.h`, especially `gfxhub_v2_1.c`, SDMA v4.x code, and `amdgpu_amdkfd_gfx_v10_3.c`.
- Compile-time detection of missing or renamed macros when generated offset/default/mask headers drift.
- Runtime dmesg traces from GPU initialization, SDMA/KFD queue setup, and GPU reset paths on GC 10.3 hardware.
- KFD queue tests that exercise SDMA RLC queue creation across multiple SDMA engines and RLC queue IDs.
- Suspend/resume and GPU reset testing, which can expose incorrect assumptions about reset/default queue, CAC, SPM, RTAVFS, or DIDT state.
- Power-management and throttling telemetry checks for CAC/DIDT/EDC counters, stall event counters, and power-brake behavior.
- SPM/performance-monitoring tests that confirm sample-delay and fixed-pattern counter registers can be programmed from their zero default baseline.
