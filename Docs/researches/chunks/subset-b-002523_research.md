# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h lines 5012-7489

## Scope

This chunk is a generated AMD GC 11.0.3 register-offset header slice. It contains C preprocessor `#define` constants only: one register-offset macro and one `<REGISTER>_BASE_IDX` macro for each register. There are no functions, structs, enums, global variables, allocations, locks, direct MMIO operations, or executable branches in this range.

The selected lines contain 2,406 `#define` statements: 1,203 register offset macros and 1,203 matching base-index macros. The chunk starts in the middle of the `gc_gdspdec` address block at `regGDS_VMID6_BASE`, then covers RAS signature registers, GUS fabric/register controls, a large graphics context-space block, SR-IOV PF/VF and PF-only privileged blocks, SPI per-CU resource reservation, and the beginning of the `gc_gfxudec` user/config-space command-processor block. It ends at `regVGT_NUM_INDICES`, so the surrounding VGT/GE user-config register group continues in the next chunk.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU DRM hardware metadata and is unrelated to Ceph filesystem behavior.

## Purpose

`gc_11_0_3_offset.h` maps symbolic GC 11.0.3 register names to the numeric offsets used by AMDGPU MMIO and packet-building helpers. Driver code combines these offsets with register field definitions from `gc_11_0_3_sh_mask.h` and SOC15 addressing helpers to read, write, or decode graphics-core hardware state without embedding raw register numbers throughout the driver.

This chunk covers these register surfaces:

- GDS partitioning and reset state for VMID-owned global data share resources.
- RAS signature capture controls for graphics sub-block reliability diagnostics.
- GUS fabric, queue, credit, priority, combine-flush, and L1 shader-array traffic controls.
- Core graphics context registers for depth/stencil, scissor/rasterization, primitive assembly, shader/export setup, color buffer state, context rolls, coherency, and performance/event counters.
- PF/VF-visible and PF-only privileged control registers used by SR-IOV, command processor debug paths, DIDT/EDC/throttling, TCP/UTCL1/GCR/PMM, and current/activity counter logic.
- SPI resource reservation controls for per-CU availability and enable masks.
- User/config-space command processor registers for EOP fences, pipeline statistics, scratch registers, atomic pre-operation values, DMA, indirect-buffer command bases, index/dispatch addresses, coherency commands, and front-end draw/dispatch controls.

## Important APIs, Types, And Macros

The only interface in this chunk is the generated macro namespace:

- `reg<NAME>` expands to a register offset relative to its address block.
- `reg<NAME>_BASE_IDX` expands to the SOC15 base-address table index used with the offset.
- `// addressBlock:` comments identify the generated hardware address block.
- `// base address:` comments document each block's physical/register-base address in AMD's register database.

There are no callable APIs or C types here. Consumers normally use these constants through AMDGPU helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `WREG32_SOC15_RLC`, golden-register table macros, and debug/register-dump helpers. Field composition and extraction live in the companion shift/mask header, not this offset header.

Important address blocks and families in this range include:

- Tail of `gc_gdspdec`: `regGDS_VMID6_BASE/SIZE` through `regGDS_VMID15_BASE/SIZE`, `regGDS_GWS_VMID0..15`, `regGDS_OA_VMID0..15`, GWS/OA reset registers, GDS context-switch counters/status, and `regGDS_MEMORY_CLEAN`.
- `gc_rasdec`: `regRAS_SIGNATURE_CONTROL`, `regRAS_SIGNATURE_MASK`, and signature registers for SX, DB, PA, SC, SPI, CB, and BCI sub-blocks.
- `gc_gusdec`: GUS IO/DRAM/GCEA combine flush controls, priority age/queuing registers, SDP credit/reserve/enable controls, RMI and EA controls, shader-array pipe configuration, VM safety controls, L2/EA mapping, PASID/L2A selection, SDP window registers, and L1 per-shader-array command/data in/out registers.
- `gc_gfxdec0`: the largest block in the chunk. It starts with DB depth/stencil render state, screen and generic scissors, target masks, viewport controls, primitive and rasterization controls, SX export controls, SPI interpolation/barycentric/attribute controls, shader wait counters, texture address and coherency controls, VGT/PA/GE primitive and tessellation state, context counters, DB/CB render-target and compression metadata bases, and color-buffer descriptors for slots 0 through 7.
- `gc_pfvf_cpdec`, `gc_pfvf_grbmdec`, `gc_pfvf_padec`, and `gc_pfvf_sqdec`: PF/VF-accessible controls including `regCP_MEC_CNTL`, `regCP_ME_CNTL`, `regGRBM_GFX_CNTL`, PA/VRS/binning/enhance controls, SQ runtime/performance/debug controls, and shader TMA base registers.
- `gc_pfonly_cpdec`, `gc_pfonly_cpphqddec`, `gc_pfonly_didtdec`, `gc_pfonly_spidec`, `gc_pfonly_tcpdec`, `gc_pfonly_gdsdec`, `gc_pfonly_utcl1dec`, `gc_pfonly_pmmdec`, and `gc_pfonly_gccacdec`: privileged-only controls for CP debug/fetch/DFY data, HPD/MES queue offsets/status, DIDT EDC thresholds/stall patterns/status, SPI debug/trap/reset/arbitration/resource-limit and compute wavefront context-save status, TCP invalidate/status/control/credit, GDS enhancement/restore, UTCL1 and GCR target/credit controls, PMM control, and extensive GC/SE CAC, EDC, PCC, power-break, throttle, hysteresis, and weighting registers.
- `gc_pfonly2_spidec`: `regSPI_RESOURCE_RESERVE_CU_0..15` and `regSPI_RESOURCE_RESERVE_EN_CU_0..15`, which reserve and enable compute-unit resources per CU index.
- Beginning of `gc_gfxudec`: command processor EOP done/fence addresses and data, pipeline statistics addresses and counters, scratch and atomic scratch registers, append/fence data, PFP/ME atomic pre-operation values, GDS atomic pre-operation values, ME memory command addresses/data, semaphore/timer registers, CP DMA PFP/ME controls and addresses, indirect-buffer and stream-table bases/sizes, doorbell base/size, PFP completion and metadata addresses, indirect draw/dispatch addresses, index base/type, GDS backup address, CP ME coherency command registers, RLC GPM perf counters, `regGRBM_GFX_INDEX`, and initial VGT/GE draw state through `regVGT_NUM_INDICES`.

## Control Flow

This header has no runtime control flow. Its effect is compile-time substitution of symbolic register names into numeric offsets.

The implied runtime flow is:

1. A GC 11.0.3 driver path selects a `reg...` macro from this header.
2. The SOC15 helper combines the macro's offset with the GC instance and the macro's `_BASE_IDX` to form the actual register address.
3. The driver reads, writes, or read-modify-writes that register through AMDGPU MMIO, RLC-safe, indirect, or golden-setting helper paths.
4. The hardware block, firmware, command processor, shader processor, graphics pipeline, or privileged management logic applies the state.

For GDS and CP registers, higher-level code performs sequencing around queue setup, VMID assignment, context switch, fence emission, ring execution, DMA, and coherency commands. For DB/CB/PA/SPI/VGT/GE graphics state, command streams or driver setup code program these offsets as part of graphics pipeline state. For privileged PF-only blocks, firmware, bring-up, diagnostics, power management, or SR-IOV host code controls access and sequencing. This header does not encode access permissions, side effects, polling loops, reset ordering, or clear-on-read/write behavior.

## State And Persistence Behavior

The macros themselves are stateless compile-time constants. Persistent and volatile state exists only in the GPU registers and in memory objects whose addresses are programmed through those registers.

Hardware state represented by this chunk includes VMID-specific GDS ranges, GWS/OA ownership, GDS context-switch counters, RAS signature latches, GUS credit and queue policy, graphics context state, render-target descriptors, compression/decompression bases, primitive/tessellation/raster state, shader interpolation/export setup, scratch registers, CP fence and statistics addresses, CP DMA addresses and commands, indirect-buffer bases, doorbell buffer layout, coherency command state, and privileged CAC/EDC/throttle/debug controls.

Many of these registers persist until rewritten, queue/context teardown, graphics state reprogramming, GPU reset, suspend/resume restoration, clock/power-gating loss, firmware reinitialization, or PF-level management intervention. Others are live counters, latches, status registers, command registers, or self-clearing controls. This generated offset header does not distinguish read-only, write-only, clear-on-write, sticky, or self-clearing semantics; consumers must rely on hardware documentation and existing driver sequences.

The `_BASE_IDX` value is part of address persistence at the software level. Most early registers in this chunk use base index `0` before the later address blocks switch to base index `1`, reflecting different SOC15 base entries. A wrong base index can address the wrong hardware aperture even when the offset value is correct.

## Dependencies And Integration Points

This chunk depends on the generated GC 11.0.3 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h` supplies matching bit shifts and masks for many registers named here.
- AMDGPU SOC15 register helpers supply the actual address calculation and MMIO access behavior.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0_3.c` includes this header and directly references GUS registers such as `regGUS_IO_RD_COMBINE_FLUSH`, `regGUS_IO_WR_COMBINE_FLUSH`, `regGUS_DRAM_COMBINE_FLUSH`, `regGUS_MISC2`, `regGUS_SDP_CREDITS`, and related SDP reserve/enable registers in IMU/RLC golden-value tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3.c` includes this offset header with the matching shift/mask header for GC 11.0.3-specific graphics behavior.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0_3.c` includes this offset header for GC 11.0.3 graphics-hub integration.
- Broader `gfx_v11_0.c` code uses same-generation register families such as `regGDS_VMID0_BASE/SIZE`, `regCP_MEC_CNTL`, and `regPA_SC_VRS_SURFACE_CNTL_1` for GDS setup, CP pipe control, and golden settings.
- Nearby generation headers, especially GC 11.x and GC 12.x offset headers, use similar names but may not share identical offsets or base indices. Cross-generation reuse must go through the correct ASIC-specific header.

Runtime integration points include graphics pipeline state setup, command submission, KFD/compute queue management, VMID resource assignment, fence and event writeback, pipeline statistics, GDS backup/restore, coherency commands, SR-IOV PF/VF access partitioning, RAS diagnostics, power and current/activity management, EDC/DIDT throttling, clock/power gating, debug/trap handling, and GPU reset/suspend/resume restore paths.

## Risks And Edge Cases

- Generated-header drift is the central risk. A wrong offset or `_BASE_IDX` compiles cleanly but directs MMIO to the wrong register or aperture.
- This chunk starts mid-block. The `gc_gdspdec` address-block comment and `GDS_VMID0..5` definitions are in the previous chunk, while this chunk starts at `GDS_VMID6_BASE`.
- This chunk ends mid logical user-config sequence. Later VGT/GE draw-state registers follow `regVGT_NUM_INDICES` in the next chunk.
- Repeated families are easy to mis-index. GDS VMID base/size pairs, GWS/OA VMID registers, CB color slot descriptors, SPI resource reserve/enables, and per-SE/CAC weight registers rely on stable numeric ordering.
- `_BASE_IDX` transitions matter. The early GDS/RAS block uses base index `0`, while GUS and most later graphics/PF/user-config blocks use base index `1`. Copying offsets without base-index awareness can break address calculation.
- PF/VF and PF-only boundaries are security-sensitive. Exposing PF-only controls to the wrong path could affect virtualization isolation, debug visibility, throttling, power behavior, or queue ownership.
- CP registers in `gc_gfxudec` are command-submission critical. Bad offsets for EOP fences, append data, DMA commands, IB bases/sizes, doorbells, or coherency registers can produce lost fences, stuck rings, corrupted command streams, or invalid memory accesses.
- DB/CB metadata and base-address registers are render-output critical. Wrong offsets can corrupt depth/stencil, color, compression metadata, or fast-clear state.
- GUS, UTCL1, GCR, and TCP controls interact with traffic ordering, credits, invalidation, and translation behavior. Incorrect programming can appear as hangs, memory faults, performance cliffs, or intermittent cache-coherency symptoms.
- RAS, EDC, CAC, DIDT, PCC, and power-break status/control registers may be latched, threshold-driven, or clear-sensitive. Offset mistakes can hide fault evidence or trigger inappropriate throttling.
- Register names that look generic, such as `regSCRATCH_REG*`, `regCP_*_ATOMIC_PREOP_*`, or `regGCR_*`, have generation- and block-specific semantics. They should not be substituted across ASIC families by name alone.

## Test Signals

Useful validation is mostly generated-data consistency plus hardware integration:

- Build AMDGPU configurations that include GC 11.0.3 support. Missing, malformed, or renamed macros should surface in `imu_v11_0_3.c`, `gfx_v11_0_3.c`, `gfxhub_v3_0_3.c`, and shared GFX 11 paths.
- Mechanically compare every offset and `_BASE_IDX` in this chunk against AMD's authoritative GC 11.0.3 register database.
- Cross-check that registers with field-level programming have corresponding entries in `gc_11_0_3_sh_mask.h`.
- Verify repeated families for monotonic spacing and expected count: GDS VMID base/size pairs, GDS GWS/OA VMID registers, CB color slots 0-7, SPI resource reserve/enables 0-15, per-SE CAC weights, scratch registers, and CP address low/high pairs.
- Run IMU/RLC golden-setting initialization on GC 11.0.3 hardware and confirm the GUS golden values program the expected registers without RLC/IMU load failures.
- Exercise graphics workloads that use depth/stencil, scissor, rasterization, color targets, compression metadata, tessellation, primitive assembly, VRS/binning controls, and pipeline statistics.
- Exercise compute/KFD and graphics submission paths that depend on GDS allocation, CP MEC/ME controls, EOP fence writes, append buffers, CP DMA, indirect buffers, doorbells, wait/signal semaphores, coherency commands, and GDS backup addresses.
- Exercise SR-IOV or virtualized configurations where PF/VF-visible and PF-only blocks are separated, checking for access faults, isolation failures, or missing privileged setup.
- Exercise reset, suspend/resume, preemption, power/clock gating, throttling, and RAS/EDC injection or monitoring paths while checking CP status, EOP fences, queue progress, RAS signatures, EDC/DIDT status, CAC counters, and throttle status.
- Decode known-good register dumps with these offsets and compare the resolved names and base indices against reference tools, especially across the base-index `0` to `1` transition.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002523`. The final per-file research should merge this with neighboring chunks for full `gc_11_0_3_offset.h` coverage. In particular, the previous chunk owns the start of `gc_gdspdec` and the first GDS VMID registers, while the next chunk continues the `gc_gfxudec` VGT/GE user-config register sequence after `regVGT_NUM_INDICES`.
