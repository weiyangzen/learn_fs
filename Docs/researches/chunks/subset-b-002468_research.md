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
