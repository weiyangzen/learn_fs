# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/navi10_enum.h lines 14864-20395

## Scope And Purpose

This chunk covers the third generated-header slice of `navi10_enum.h` for AMD Navi10/GFX10-era register programming. The range starts in the tail of `GL1C_PERF_SEL`, includes the complete `GL1CG_PERF_SEL` enum, then spans generated enum groups for texture/cache/performance counters, command processor state, shader export and depth-buffer controls, texture/vertex resource fields, primitive/rasterization counters and raster configuration, RMI/GCR/UTCL1/SDMA performance selectors, and the first ADDRLIB surface tiling/address-configuration enums. It ends immediately after `NumLowerPipes`; `ColorTransform` begins in the next chunk.

The file section is not executable code. Its purpose is to provide symbolic, generation-specific integer values that driver code can place into register fields defined by companion offset and shift/mask headers. Most definitions are performance event selectors for hardware perfmon muxes; the smaller enums define legal field encodings for command processor IDs, perfmon state machines, texture and vertex descriptors, depth/stencil/raster controls, binning controls, SDMA selectors, and address-library tiling geometry.

## Important APIs, Types, And Constants

The exported API is the enum namespace. There are no functions, structs, globals, locks, allocation paths, or inline helpers. Consumers include this header and write enum constants into MMIO fields through AMDGPU helpers such as `REG_SET_FIELD`, `WREG32_SOC15`, `RREG32_SOC15`, `SOC15_REG_OFFSET`, or generated register programming tables. The relevant source-tree include points found for this header are `amdgpu/gfx_v10_0.c`, `amdgpu/gfx_v11_0.c`, `amdgpu/gfxhub_v2_0.c`, `amdgpu/gmc_v11_0.c`, and `amdkfd/kfd_device_queue_manager_v10.c`.

Major enum families in this span are:

- Texture/cache and memory path selectors: `GL1CG_PERF_SEL`, `TA_TC_REQ_MODES`, `TA_TC_ADDR_MODES`, `TA_PERFCOUNT_SEL`, `TD_PERFCOUNT_SEL`, `TCP_PERFCOUNT_SELECT`, `TCP_CACHE_POLICIES`, `TCP_CACHE_STORE_POLICIES`, `TCP_WATCH_MODES`, `TCP_DSM_*`, `TCP_OPCODE_TYPE`, `GL2C_PERF_SEL`, and `GL2A_PERF_SEL`.
- Graphics register-bus and command processor selectors: `GRBM_PERF_SEL`, `GRBM_SE0_PERF_SEL` through `GRBM_SE3_PERF_SEL`, `CP_RING_ID`, `CP_PIPE_ID`, `CP_ME_ID`, `SPM_PERFMON_STATE`, `CP_PERFMON_STATE`, `CP_PERFMON_ENABLE_MODE`, `CPG_PERFCOUNT_SEL`, `CPF_PERFCOUNT_SEL`, `CPC_PERFCOUNT_SEL`, CP perf-window and latency-stat enums, and `CP_DDID_CNTL_*`.
- Shader export and depth-buffer controls: `SX_BLEND_OPT`, `SX_OPT_COMB_FCN`, `SX_DOWNCONVERT_FORMAT`, `SX_PERFCOUNTER_VALS`, `ForceControl`, `ZSamplePosition`, `ZOrder`, `ZpassControl`, `ZModeForce`, `ZLimitSumm`, `CompareFrag`, `StencilOp`, `ConservativeZExport`, `DbPSLControl`, `DbPRTFaultBehavior`, `PerfCounter_Vals`, `RingCounterControl`, `DbMemArbWatermarks`, `DFSMFlushEvents`, `PixelPipeCounterId`, `PixelPipeStride`, and `FullTileWaveBreak`.
- Texture, sampler, and vertex descriptor encodings: `TEX_BORDER_COLOR_TYPE`, `TEX_BC_SWIZZLE`, `TEX_CHROMA_KEY`, `TEX_CLAMP`, `TEX_COORD_TYPE`, `TEX_DEPTH_COMPARE_FUNCTION`, `TEX_DIM`, `TEX_FORMAT_COMP`, `TEX_MAX_ANISO_RATIO`, `TEX_MIP_FILTER`, `TEX_REQUEST_SIZE`, `TEX_SAMPLER_TYPE`, `TEX_XY_FILTER`, `TEX_Z_FILTER`, `VTX_CLAMP`, `VTX_FETCH_TYPE`, `VTX_FORMAT_COMP_ALL`, `VTX_MEM_REQUEST_SIZE`, `TVX_DATA_FORMAT`, `TVX_DST_SEL`, `TVX_ENDIAN_SWAP`, `TVX_INST`, `TVX_NUM_FORMAT_ALL`, `TVX_SRC_SEL`, `TVX_SRF_MODE_ALL`, and `TVX_TYPE`.
- Primitive/rasterization and backend counters/configuration: `PH_PERFCNT_SEL`, `SU_PERFCNT_SEL`, `SC_PERFCNT_SEL`, `SePairXsel`, `SePairYsel`, `SePairMap`, `SeXsel`, `SeYsel`, `SeMap`, `ScXsel`, `ScYsel`, `ScMap`, `PkrXsel2`, `PkrXsel`, `PkrYsel`, `PkrMap`, `RbXsel`, `RbYsel`, `RbXsel2`, `RbMap`, `BinningMode`, `BinSizeExtend`, `BinMapMode`, `BinEventCntl`, `CovToShaderSel`, and `ScUncertaintyRegionMode`.
- Memory-system, DMA, and address-library enums: `RMIPerfSel`, `GCRPerfSel`, `UTCL1PerfSel`, `SDMA_PERF_SEL`, `NUM_PIPES_BC_ENUM`, `NUM_BANKS_BC_ENUM`, `SWIZZLE_TYPE_ENUM`, `TC_MICRO_TILE_MODE`, `SWIZZLE_MODE_ENUM`, `SurfaceEndian`, `ArrayMode`, `NumPipes`, `NumBanksConfig`, `PipeInterleaveSize`, `BankInterleaveSize`, `NumShaderEngines`, `NumRbPerShaderEngine`, `NumGPUs`, `NumMaxCompressedFragments`, `ShaderEngineTileSize`, `MultiGPUTileSize`, `RowSize`, and `NumLowerPipes`.

The largest selector tables in this chunk are `PH_PERFCNT_SEL` with 960 values, `SC_PERFCNT_SEL` with 501 values, `SU_PERFCNT_SEL` with 427 values, `PerfCounter_Vals` with 346 values, `RMIPerfSel` with 257 values, `GL2C_PERF_SEL` with 228 values, and `SX_PERFCOUNTER_VALS` with 221 values. These wide enums are hardware perf event IDs rather than dense software state machines.

## Control Flow

This header has no runtime control flow. It affects compiled control flow indirectly by naming constants used when a driver chooses a register field value or selects a hardware performance event.

Typical usage flow is:

1. The driver selects an IP block and register field using the generation's offset and shift/mask headers.
2. It chooses one of these enum constants as the semantic value for that field, for example a CP perfmon state, a texture descriptor clamp mode, a DB compare or stencil operation, a raster config selector, or a perf counter event.
3. It packs the value into the register field and writes it through SOC15/MMIO helpers.
4. For diagnostic/performance paths, it later reads hardware counters or status registers and interprets the result according to the same generation-specific selector value.

The perf-selector enums are especially mux-oriented. Values such as `TA_PERF_SEL_*`, `TCP_PERF_SEL_*`, `GL2C_PERF_SEL_*`, `CPG_PERF_SEL_*`, `SX_PERF_SEL_*`, `DB_PERF_SEL_*`, `PH_*`, `PERF_*`, `SC_*`, `RMI_PERF_SEL_*`, `GCR_PERF_SEL_*`, `UTCL1_PERF_SEL_*`, and `SDMA_PERF_SEL_*` are intended to be written into perfmon select registers before counter collection. The smaller descriptor/config enums drive normal rendering and memory behavior rather than counter selection.

## State And Persistence Behavior

The enums themselves do not store state. They describe hardware-visible values that become persistent only after a consumer writes them into GPU registers or descriptors.

Longer-lived programmed state includes command processor ring/pipe/ME IDs, CP/SPM perfmon state and enable modes, texture/sampler resource encodings, vertex fetch descriptors, depth/stencil compare and update modes, DB pixel pipe counter controls, rasterization layout maps, binning controls, SDMA perf selector values, and ADDRLIB address-configuration fields. These persist in hardware or command streams until overwritten, context-switched, reset, or restored after suspend/resume.

Transient state is represented by the counters selected by the perf enums. The selector value is stable, but the counter result is live hardware state. Many selector names expose busy/idle cycles, stalls, FIFO full/empty conditions, cache hits/misses, TLB requests and misses, XNACK activity, latency bins, credit stalls, dealloc events, primitive/binning events, and clock-gating status. The header does not encode how counters latch, reset, overflow, multiplex, or synchronize with command submissions; those semantics live in the perfmon hardware and driver sequencing.

Some enum values are command-like or side-effect sensitive when written into their matching fields. CP perfmon states such as disable/reset/start/count/dump alter collection state; bin event controls can break, pipeline, or drop batches; DB force and flush-related values affect depth/stencil behavior; SDMA and GCR perf selectors expose invalidation, UTCL2, and TLB shootdown activity; texture and vertex descriptor encodings affect memory fetch interpretation.

## Dependencies And Integration Points

This chunk depends on the generated AMDGPU register-header convention. The enum values are meaningful only with matching Navi10/GFX10-era register offsets, masks, defaults, packet definitions, and hardware documentation. They complement headers such as GC/GFXHUB offset and sh/mask files, which provide register addresses and bitfield positions. On their own, these enums do not identify which register field consumes each value.

Integration points include:

- AMDGPU graphics initialization and context programming, where CP IDs, perfmon state, GRBM selectors, raster configuration maps, DB/SX state, and texture/vertex descriptor values are emitted into registers or command streams.
- KFD queue management for GFX10, which includes this header alongside queue and CP definitions.
- GMC/GFXHUB paths, which include the header for memory-type, cache, translation, invalidation, and hub-related enum values elsewhere in the file and may rely on matching generation constants.
- Performance monitoring and SPM collection, where the large TA/TD/TCP/GL2/GRBM/CP/SX/DB/PH/SU/SC/RMI/GCR/UTCL1/SDMA selector sets map software-visible perf event choices to hardware mux IDs.
- Texture and vertex fetch programming, where `TEX_*`, `VTX_*`, and `TVX_*` values define descriptor fields for sampler behavior, formats, request size, endian swap, destination/source swizzles, and instruction/resource type.
- Address library and surface layout code, where swizzle, array mode, pipe/bank/interleave, shader-engine, RB, GPU, compressed-fragment, tile-size, row-size, and lower-pipe enums express hardware memory-layout geometry.

There are overlapping enum names in older and newer generated headers under `include/asic_reg/` and top-level generation headers. Similar names do not guarantee identical numeric values. For example, `SDMA_PERF_SEL` and `ArrayMode` appear in other ASIC enum headers with generation-specific contents and gaps, so cross-generation code must include the correct header for the active IP version.

## Risks And Edge Cases

The primary risk is hardware ABI drift. These constants are numeric encodings for silicon register fields. A wrong value can still compile but select the wrong perf event, program an illegal descriptor mode, corrupt raster/backend routing, break binning, or misreport memory/cache/translation behavior.

The chunk boundary is important. The requested range begins after the `GL1C_PERF_SEL` typedef line and includes only its last five selector entries plus closing brace; a complete file-level description of `GL1C_PERF_SEL` needs the previous chunk. The range ends after `NumLowerPipes`; `ColorTransform`, `CompareRef`, and later ADDRLIB/display/format enums are in the next chunk.

Large perf selector tables are easy to treat as generic event lists, but they are block-specific. A `PH_PERFCNT_SEL` value cannot be substituted for an `SC_PERFCNT_SEL` value even when names mention similar events. Many tables include reserved holes or non-contiguous jumps, and those holes should remain exactly as generated.

Descriptor/config enums have visible rendering consequences. Incorrect `TEX_CLAMP`, depth compare, stencil op, `SX_DOWNCONVERT_FORMAT`, `TVX_DATA_FORMAT`, `SWIZZLE_MODE_ENUM`, or `ArrayMode` use can produce incorrect pixels, GPUVM faults, bad compression layout, or invalid memory interpretation.

Raster configuration and binning enums are topology-sensitive. `Se*`, `Sc*`, `Pkr*`, and `Rb*` mapping values describe how shader engines, scan converters, packers, and render backends are tiled or routed. Incorrect use can affect load balancing, primitive distribution, or backend addressing.

Performance and diagnostic fields can be privileged or timing-sensitive. Counter selection may need clocks enabled, stable perfmon state transitions, counter resets, and serialization around workloads. The header does not encode those ordering requirements.

## Test Signals

Useful validation signals are build and hardware-integration oriented:

- Build coverage for AMDGPU/KFD files that include `navi10_enum.h`, especially `gfx_v10_0.c`, `gfx_v11_0.c`, `gfxhub_v2_0.c`, `gmc_v11_0.c`, and `kfd_device_queue_manager_v10.c`.
- Perfmon/SPM tests that select representative TA, TD, TCP, GL2C/GL2A, GRBM, CP, SX, DB, PH, SU, SC, RMI, GCR, UTCL1, and SDMA events and verify nonzero or expected counter behavior under targeted workloads.
- Graphics conformance workloads that exercise texture clamp/filter/request-size behavior, vertex formats and fetch types, depth compare/stencil operations, SX downconversion/blend optimization, rasterization maps, and binning modes.
- GPU reset, suspend/resume, and power-gating tests that ensure perfmon state, texture/cache/raster/DB configuration, and address-configuration values are restored or regenerated correctly.
- Memory-layout and address-library tests that validate swizzle modes, array modes, pipe/bank/interleave geometry, row sizes, compressed-fragment modes, and shader-engine/RB topology on Navi10-class devices.
- Negative diagnostics for invalid or reserved selector values, ensuring driver interfaces either reject unsupported events or confine them to debug-only paths without affecting normal command submission.
