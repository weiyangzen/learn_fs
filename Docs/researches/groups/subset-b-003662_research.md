# subset-b-003662 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a6xx_descriptors.xml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a6xx_descriptors.xml

## Purpose
`a6xx_descriptors.xml` is an rnndb/freedreno XML database fragment for A6xx texture and UBO descriptor dword layouts. It does not execute at runtime; it is consumed by `drivers/gpu/drm/msm/registers/gen_header.py` through the DRM msm Makefile to generate C macros in `generated/a6xx_descriptors.xml.h`. Those macros are part of the low-level contract used by Adreno command-stream and state programming code to pack descriptor dwords consistently with A6xx hardware.

## Important definitions
The file imports `freedreno_copyright.xml`, `adreno_common.xml`, `adreno_pm4.xml`, and `a6xx_enums.xml`, so its bitfields can refer to common compare, MSAA, color-swap, texture format, tiling, filter, clamp, anisotropy, reduction, border-color, swizzle, and texture-type enums. It defines three 32-bit domains: `A6XX_TEX_SAMP`, `A6XX_TEX_CONST`, and `A6XX_UBO`.

`A6XX_TEX_SAMP` is a four-dword sampler descriptor. Dword 0 holds mip-filtering, magnification/minification filter modes, S/T/R wrap modes, anisotropy, and signed fixed-point LOD bias. Dword 1 carries clamp-enable, depth-compare function, cubemap seam filtering disable, unnormalized coordinates, far mip filtering, and min/max LOD. Dword 2 carries reduction mode, fast border color controls, chroma-linear enable, and the border-color table/address field. Dword 3 is intentionally empty/reserved.

`A6XX_TEX_CONST` is a 16-dword texture-resource descriptor with `varset="chip"`. It covers tile mode, sRGB, component swizzles, mip levels, chroma midpoint flags, sample count, `a6xx_format`, color swap, width/height, A7xx+ mutable enable, buffer-texture struct size/start offset overlays, pitch alignment, pitch/stride, texture type, array pitch, minimum layer size, tile-all, UBWC/flag controls, base and flag addresses, depth, min LOD clamp, plane pitch, flag-buffer array pitch, flag-buffer pitch, and flag-buffer log dimensions. Several fields intentionally overlap, such as `MIPLVLS` with chroma midpoint flags, buffer-typed fields with pitch fields, `MIN_LOD_CLAMP` with `PLANE_PITCH`, and resource address fields for planar/flag layouts.

`A6XX_UBO` is a compact two-dword uniform-buffer descriptor: dword 0 is the low address, and dword 1 stores high address bits plus `SIZE`, documented in vec4 units.

## Control flow and generation behavior
The XML is declarative input to the header generator. The control flow is: the kernel build sees generated header targets in `drivers/gpu/drm/msm/Makefile`, invokes `gen_header.py --rnn registers --xml registers/adreno/a6xx_descriptors.xml c-defines`, resolves imports, validates against `rules-fd.xsd` when `CONFIG_DRM_MSM_VALIDATE_XML` enables validation, and emits C preprocessor definitions. Driver code then uses generated field macros while building descriptors, rather than parsing this XML at runtime.

## State and persistence
There is no runtime persistence in this XML. Its persistent state is the checked-in hardware description and the generated header products under the build directory. Descriptor fields here represent GPU-visible packed state that is later written into command buffers or descriptor memory; mistakes persist indirectly as incorrect GPU state packets, texture fetch behavior, or uniform buffer addressing.

## Dependencies and integration points
The file depends on `a6xx_enums.xml` for the A6xx texture-specific field types and on `adreno_common.xml` for cross-generation fields such as `adreno_compare_func`, `a3xx_msaa_samples`, and `a3xx_color_swap`. It integrates with the msm generated-header build path listed in the Makefile and with A6xx/A7xx code paths that include generated XML headers via `a6xx_gpu.h` and related Adreno sources. The descriptor domains are also conceptually coupled to userspace Mesa/freedreno descriptor packing because kernel and userspace must agree on hardware encodings.

## Risks
The highest risk is silent field-position drift: a one-bit error in format, pitch, address shift, or swizzle fields can produce corrupted sampling, out-of-bounds memory access, or GPU faults. Overlapping fields require careful use-site discipline because valid interpretation depends on texture type, planar format, UBWC flag use, and chip generation. The `MUTABLEEN` field is gated with `variants="A7XX-"`, so generated code must preserve variant guards correctly. Comments also flag uncertain hardware details, such as LOD bias bit width and D3D structured UAV interpretation; those are research debt and should be treated conservatively.

## Test signals
Useful validation signals are successful XML schema validation, successful generation of `a6xx_descriptors.xml.h`, and successful compilation of msm Adreno sources that include generated headers. Runtime signals include texture-format conformance tests, mipmapping and LOD tests, sampler clamp/wrap/filter tests, planar and UBWC texture tests, CTS/deqp coverage for Vulkan/OpenGL texture sampling, and absence of GPU faults when exercising buffer textures, multisample textures, and UBO addressing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a6xx_descriptors.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a6xx_enums.xml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a6xx_enums.xml

## Purpose
`a6xx_enums.xml` defines A6xx-family enum values and one inline protection bitset used by generated Adreno register headers. It centralizes hardware numeric encodings for texture descriptors, shader/debug state identifiers, 2D interface formats, tessellation modes, depth modes, and sampler behavior so descriptor and register XML can reference named values instead of duplicating numbers.

## Important definitions
The file imports `freedreno_copyright.xml`, `adreno_common.xml`, and `adreno_pm4.xml`. Its inline bitset `a6x_cp_protect` packs CP protected-register regions with `BASE_ADDR` bits 0..17, `MASK_LEN` bits 18..30, and a boolean `READ` bit.

It defines 17 enums. `a6xx_tile_mode` covers linear and tiled modes. `a6xx_format` is the large 131-entry texture/render format catalog, spanning normalized, signed, unsigned, float, packed, depth/stencil, ETC, BC, and ASTC formats and ending with `FMT6_NONE = 0xff`. `a6xx_polygon_mode`, `a6xx_depth_format`, `a6xx_ztest_mode`, `a6xx_tess_spacing`, and `a6xx_tess_output` encode draw/raster/depth/tessellation choices. `a6xx_shader_id` maps shader-state and internal RAM selector IDs, while `a6xx_debugbus_id` maps debug-bus blocks from CP/RBBM/VBIF/HLSQ through SPTP instances. Texture-specific enums include `a6xx_2d_ifmt`, `a6xx_tex_type`, `a6xx_tex_filter`, `a6xx_tex_clamp`, `a6xx_tex_aniso`, `a6xx_reduction_mode`, `a6xx_fast_border_color`, and `a6xx_tex_swiz`.

## Control flow and generation behavior
This file is resolved by `gen_header.py` before any XML that references its enum names. Generated C definitions are then included by `a6xx_gpu.h` through `a6xx_enums.xml.h`. Descriptor XML such as `a6xx_descriptors.xml` and `a8xx_descriptors.xml` use these enum names as bitfield `type` attributes, so the generator can emit typed masks, shifts, and value constants with stable names.

## State and persistence
The XML has no runtime state. Its persistent effect is the numeric ABI between driver command construction and Adreno hardware. Values such as `FMT6_*`, texture type, swizzle, and debug-bus IDs are embedded into generated headers and then into compiled driver code or command streams.

## Dependencies and integration points
The enum catalog is shared by A6xx and by later XML where encodings remain compatible. `a8xx_descriptors.xml` imports it for common texture formats, filter/clamp/aniso modes, tile modes, sample count dependencies through `adreno_common.xml`, and texture type. The generated header is listed in the msm Makefile and included by `a6xx_gpu.h`, making it visible to A6xx/A7xx driver code.

## Risks
The broad `a6xx_format` enum is a high-risk compatibility surface because format numbers must match GPU hardware and userspace expectations exactly. Debug-bus and shader IDs are diagnostic rather than normal rendering state, but wrong values can break crash capture, performance debugging, or firmware/state inspection. The `a6x_cp_protect` bitset differs from the common `adreno_cp_protect` layout, so accidental interchange can program the wrong protected region policy.

## Test signals
Build-time signals include XML validation and successful generation/compilation of `a6xx_enums.xml.h`. Functional signals include format conversion tests, sampler descriptor tests, protected-register programming tests, GPU state capture/debug-bus reads, and conformance suites that exercise ASTC/BC/depth/stencil formats, texture buffers, swizzles, and tessellation modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a6xx_enums.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a6xx_gmu.xml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a6xx_gmu.xml

## Purpose
`a6xx_gmu.xml` describes the register map for the A6xx-generation GMU and related GMU/RSCC address space, with variant annotations extending through A7xx and A8xx offsets where the same logical register moved. The generated header `a6xx_gmu.xml.h` is used directly by GMU, HFI, preemption, GPU state capture, catalog, and A8xx code paths.

## Important definitions
The file imports `freedreno_copyright.xml` and `adreno_common.xml`, then defines one 32-bit domain named `A6XX` with `prefix="variant"` and `varset="chip"`. It contains 171 registers and 41 explicit bitfields.

The register set covers GMU boot and memory windows (`GMU_CM3_ITCM_START`, `GMU_CM3_DTCM_START`, `GMU_CM3_SYSRESET`, `GMU_CM3_BOOT_CONFIG`, `GMU_CM3_FW_BUSY`, `GMU_CM3_FW_INIT_RESULT`), firmware/version state (`GMU_CORE_FW_VERSION` with `MAJOR`, `MINOR`, and `STEP` fields), cache and bus configuration (`GMU_ICACHE_CONFIG`, `GMU_DCACHE_CONFIG`, `GMU_SYS_BUS_CONFIG`, `GMU_MRC_GBIF_QOS_CTRL`), DCVS votes/settings (`GMU_GX_VOTE_IDX`, `GMU_MX_VOTE_IDX`, `GMU_DCVS_*`), power counters and always-on counters, power collapse/nap/RPMh controls, HFI queue registers (`GMU_HFI_*`), GMU-to-host and host-to-GMU interrupts, AO interrupt status/control, CX/GX busy status, OOB request/ack/clear registers, watchdog, fence ranges, idle status, and RSCC sequence/TCS/timestamp registers.

Variant-specific entries are central. Examples include `GMU_CX_GMU_POWER_COUNTER_ENABLE` at an A6xx/A7xx offset and a separate A8xx offset, `GMU_SPTPRAC_PWR_CLK_STATUS` with A6xx and A7xx bit layouts, `GMU_PWR_CLK_STATUS` for A8xx+, and `GMU_ALWAYS_ON_COUNTER_*` / keepalive registers moving between A6xx-A7xx and A8xx+. Several RSCC registers also carry A740-specific or A8xx+ variants.

## Control flow and generation behavior
The XML is converted to `generated/a6xx_gmu.xml.h` during the msm build. Runtime code calls inline helpers such as `gmu_read()`, `gmu_write()`, `gmu_rmw()`, and `gmu_read64()` with generated register constants. The practical control flow is visible in `a6xx_gmu.c`: initialize clocks/memory/IRQs, load firmware, configure power/RPMh, start HFI, manage out-of-band requests, set frequencies/bandwidth, read idle and power status, and shut down or force off the GMU. `a6xx_hfi.c` uses the HFI registers for queue setup and messaging. `a6xx_gpu_state.c` uses generated constants for crash/state capture. `a8xx_gpu.c` and `a8xx_preempt.c` also include this generated header for shared/newer GMU controls.

## State and persistence
The XML itself is static, but it names registers controlling persistent device state while the GPU is powered: firmware boot state, HFI queues, interrupt masks/status, RPMh votes, power-collapse policy, OOB ownership, watchdog/fault state, performance-counter OOB access, and RSCC sequences. Incorrect values can survive until GMU reset, GPU suspend/resume, or full device power cycle.

## Dependencies and integration points
The generated header is listed in the msm Makefile and included by `a6xx_gmu.c`, `a6xx_hfi.c`, `a6xx_gpu.c`, `a6xx_gpu_state.c`, `a6xx_preempt.c`, `a6xx_catalog.c`, `a8xx_gpu.c`, and `a8xx_preempt.c`. It integrates with firmware HFI protocols, devfreq/OPP frequency setup, RPMh power-vote programming, GPU state capture, IRQ handling, and preemption. The `chip` varset from `adreno_common.xml` is required for variant selection.

## Risks
This is a high-risk hardware-control map. Wrong offsets or variant guards can write power, interrupt, OOB, or firmware-control values to the wrong register, causing boot failures, hangs, spurious interrupts, broken suspend/resume, or power-collapse instability. The A8xx remaps are especially sensitive because the same logical names can exist at different offsets. Bitfield layout changes in `GMU_SPTPRAC_PWR_CLK_STATUS`, `GMU_PWR_CLK_STATUS`, and RPMh controls can invert readiness or power-state checks.

## Test signals
Validation starts with XML schema validation, generated-header compilation, and successful inclusion by all GMU/HFI/A8xx objects. Runtime signals include GMU firmware boot, HFI init and message acknowledgments, successful devfreq changes, suspend/resume cycles, OOB set/clear for GPU/perfcounter/boot-slumber states, interrupt handling without storms, GPU state capture after a fault, and A6xx/A7xx/A8xx smoke tests that exercise both legacy and variant-remapped offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a6xx_gmu.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a6xx_perfcntrs.xml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a6xx_perfcntrs.xml

## Purpose
`a6xx_perfcntrs.xml` defines A6xx performance-counter selector enums for GPU blocks. These enums become generated constants used when programming counter select registers and when decoding or exposing performance metrics for profiling, debugging, and system profiling.

## Important definitions
The file imports common Adreno and PM4 definitions, then defines 16 selector enums with 543 total values. Blocks include CP, RBBM, PC, VFD/VFDP, HLSQ, VPC, TSE, RAS, UCHE, TP, SP, RB, VSC, CCU, LRZ, and CMPDECMP. Counts range from small fixed catalogs such as `a6xx_vsc_perfcounter_select` with 5 values to larger shader/texture catalogs such as `a6xx_sp_perfcounter_select` with 85 values and `a6xx_tp_perfcounter_select` with 57 values.

The counters cover always-count/busy cycles, stall/starve cycles, preemption timing, PM4/SQE activity, primitive and tessellation activity, vertex fetch stalls, HLSQ waves and latency, VPC allocations, raster tile/block activity, UCHE/VBIF traffic, texture cache requests/misses/latency, shader ALU/EFU/wave occupancy, render backend depth/color/CCU interactions, LRZ activity, and compression/decompression read/write/flag events.

## Control flow and generation behavior
The XML is converted to `generated/a6xx_perfcntrs.xml.h` during the msm build and included through `a6xx_gpu.h`. At runtime, driver sysprof/perf code selects a counter by writing one of these values into the relevant block's select registers, then reads the corresponding counter registers. The XML does not define the counter register addresses; it defines the mux values that make those registers count a specific event.

## State and persistence
There is no state in the XML. The selected values become transient GPU performance-counter state after the driver programs counter select registers. Those selections affect profiling observations until changed, reset, or power-cycled. Bad selector values generally do not persist beyond counter configuration, but they can make profiling data misleading.

## Dependencies and integration points
The generated header is part of the Makefile's generated Adreno header set and is included by `a6xx_gpu.h`. It integrates with GMU/sysprof code paths that may need OOB perfcounter access (`GMU_OOB_PERFCOUNTER_SET`) before touching counters, and with tools or debugfs/perf interfaces that map user-visible metrics to selector values.

## Risks
Performance-counter enums are easy to regress without compile failures because the values are just numbers accepted by hardware muxes. Wrong names or values can silently report a different event, breaking profiling and power/performance analysis. Some counters are block- or generation-specific; using A6xx selectors on A7xx/A8xx without checking compatibility can produce reserved counts or misleading data. Typos in names also matter because external tooling may key off generated symbol names.

## Test signals
Build signals include generated-header creation and compilation. Runtime signals include nonzero and plausible counter deltas for busy counters under load, idle counters near expected baselines, block-specific counters responding to targeted workloads such as texture sampling, shader ALU loops, render backend writes, LRZ/depth tests, and preemption tests. Cross-checks against known-good freedreno/Mesa perf queries and vendor traces are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a6xx_perfcntrs.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a7xx_enums.xml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a7xx_enums.xml

## Purpose
`a7xx_enums.xml` defines A7xx-specific state and debug selector enums. It complements the shared A6xx enum catalog where encodings remain compatible, while adding A7xx state type, state location, cluster, and debug-bus IDs needed by generated headers and A7xx-aware driver logic.

## Important definitions
The file imports `freedreno_copyright.xml`, `adreno_common.xml`, and `adreno_pm4.xml`, then defines four enums. `a7xx_statetype_id` has 76 values ranging over TP context registers/data, SP instruction and local-buffer data, USPTP data, HLSQ state/data-path/frontend/indirect/backend metadata, and similar state blocks. `a7xx_state_location` has five locations: HLSQ state, HLSQ data path, SP top, USPTP, and HLSQ DP string. `a7xx_cluster` identifies front-end, shader, PC/VPC, GRAS, and pixel clusters. `a7xx_debugbus_id` has 106 values mapping CP, RBBM, GBIF, HLSQ, UCHE, PC, VFD, VPC, TSE, RAS, LRZ, SP, TP, RB, CCU, CMP, UFC, and CGC debug-bus endpoints, with multi-instance IDs up to the 400s.

## Control flow and generation behavior
The generated `a7xx_enums.xml.h` is listed in the msm Makefile and included by `a6xx_gpu.h` alongside A6xx headers. The XML is not parsed at runtime; generated constants are compiled into driver paths that need A7xx state/debug IDs. Those values are typically used when selecting internal state blocks or debug-bus sources for state capture and diagnostics.

## State and persistence
The XML has no mutable state. Its values influence transient debug/state selection when the driver or diagnostic paths request hardware state. Incorrect values do not persist as normal rendering state, but can make captured state incomplete or wrong until fixed.

## Dependencies and integration points
The file depends on common Adreno definitions and shares generation infrastructure with the rest of `registers/adreno`. It integrates with A7xx GPU support through `a6xx_gpu.h` and state/debug code that uses generated enum constants. It also parallels `a8xx_enums.xml`, making differences in cluster and debug-bus topology explicit.

## Risks
The main risk is diagnostic blind spots: wrong state type or debug-bus IDs can make crash dumps, debugbus reads, and state capture point at the wrong hardware block. Because many values are sparse and topology-specific, accidental renumbering or copy-forward from A6xx/A8xx can compile cleanly while breaking A7xx debugging. Names also encode topology expectations, so inconsistent naming can confuse downstream tooling.

## Test signals
Build-time signals are XML validation and generated-header compilation. Runtime signals include successful GPU state capture on A7xx devices, debugbus selection returning plausible block-specific activity, crashdump decoders resolving A7xx state IDs, and comparison with known hardware traces or freedreno expectations for A7xx clusters and state locations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a7xx_enums.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a7xx_perfcntrs.xml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a7xx_perfcntrs.xml

## Purpose
`a7xx_perfcntrs.xml` defines A7xx performance-counter selector enums. It is the larger A7xx counterpart to the A6xx counter catalog, adding selectors for newer front-end, shader, ray tracing, VRS, UFC, GBIF, cache, and mesh/task-style activity while preserving familiar block categories.

## Important definitions
The file imports common Adreno and PM4 definitions, then defines 18 enums with 966 total values. Shared-style blocks include CP, RBBM, PC, VFD, HLSQ, VPC, TSE, RAS, UCHE, TP, SP, RB, VSC, CCU, LRZ, and CMPDECMP. A7xx-specific or expanded blocks include `a7xx_gbif_perfcounter_select` with 81 GBIF/AXI events and `a7xx_ufc_perfcounter_select` with 58 UFC/filter/cache events.

The larger catalogs show A7xx architectural growth: CP includes AQE and mesh/task chunk counters; HLSQ includes SPTROC and per-stage cache miss events; TP grows to 133 selectors including packed-point and richer cache/filter activity; SP grows to 151 selectors including RTU ray-box/ray-triangle intersections and RTU stall cycles; RB includes VRS quad counters; UCHE includes CCHE/GMEM/UBWC traffic; GBIF exposes AXI read/write beat and held-off events.

## Control flow and generation behavior
The file is converted into `generated/a7xx_perfcntrs.xml.h` and included through `a6xx_gpu.h`. Runtime counter programming selects events by writing these values to performance-counter selector registers. The XML controls the symbolic constants for mux values; register addresses and readout mechanics live in the broader Adreno driver.

## State and persistence
The XML itself is immutable source. Generated values become transient counter selections on hardware during profiling sessions. Counter selection may require GMU OOB ownership for perf-counter access in A6xx-family runtime paths, and selections last until the driver changes them, the GPU resets, or power state tears down the programming.

## Dependencies and integration points
It shares imports and generation with other Adreno XML files and is listed in the msm Makefile. The generated header integrates with A7xx-capable performance monitoring and any debugfs/perf/sysprof layer that maps metric names to selector values. It also needs to remain distinct from `a6xx_perfcntrs.xml` because many A7xx values are expanded, reserved, or shifted.

## Risks
The risk profile is silent observability corruption. Misnumbered selectors can make performance analysis, regression triage, and power tuning wrong without affecting normal rendering. Reserved values and expanded A7xx-only counters increase the chance of using a selector unsupported by a specific SKU. Names with stage-specific suffixes, RTU/VRS/AQE terms, and cache/traffic distinctions must stay exact enough for tooling and humans to interpret data correctly.

## Test signals
Build checks include XML validation and header generation. Runtime checks should compare idle/busy deltas for each block, exercise workloads targeted at texture, shader, ray tracing, VRS, render backend, UCHE/UBWC, and GBIF traffic, and verify tool-facing metric names resolve to plausible counters. Cross-generation tests should ensure A6xx and A7xx metric tables do not accidentally share incompatible selector constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a7xx_perfcntrs.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a8xx_descriptors.xml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a8xx_descriptors.xml

## Purpose
`a8xx_descriptors.xml` defines A8xx texture sampler and texture memory-object descriptor layouts. It reflects a descriptor reorganization from A6xx/A7xx texture constants into A8xx sampler plus memory-object dwords while reusing common A6xx format/filter/clamp/type encodings and A8xx-specific swizzles.

## Important definitions
The file imports `freedreno_copyright.xml`, `adreno_common.xml`, `adreno_pm4.xml`, `a6xx_enums.xml`, and `a8xx_enums.xml`. It defines two 32-bit domains: `A8XX_TEX_SAMP` and `A8XX_TEX_MEMOBJ`.

`A8XX_TEX_SAMP` is a four-dword sampler descriptor. Dword 0 contains near mip filtering, `MIPMAPING_DIS`, XY filters, wrap modes, MSAA box filtering, LOD bias, and anisotropy. Dword 1 contains max/min LOD, reduction mode, compare function, chroma-linear enable, cubemap seam filtering disable, and unnormalized coordinates. Dword 2 contains fast-border-color enable, fast border color value, and border-color field. Dword 3 is reserved.

`A8XX_TEX_MEMOBJ` is a 16-dword memory-object descriptor with `varset="chip"`. It holds base address, texture type, depth, width/height, sample count, format, color swap, A8xx swizzle fields, tile mode, UBWC/flag state, sparse/PRT enable, tile-all and sRGB, U/V planar base overlays, flag buffer pitch/address, all-samples-center, mutable enable, line offset and alignment, mip levels, array slice offset, array offset unit, minimum array slice offset, GMEM fallback/full-surface/corner flags, UV chroma offset overlays, flag array pitch/log dimensions, V-plane overlays, min LOD clamp, and UV pitch.

## Control flow and generation behavior
The XML is intended for the same generated-header path as other Adreno XML files. `a8xx_enums.xml.h` is listed in the Makefile, while this descriptor file supplies the A8xx descriptor domain source for generator use alongside A6xx descriptors. Runtime packing code uses generated masks/shifts to build sampler and memory-object descriptors that are submitted to the GPU. The XML itself has no runtime parser.

## State and persistence
The file is static source. Its generated constants control GPU-visible descriptor state stored in command buffers or descriptor memory. Those descriptor dwords persist for the life of the submitted state/buffer and affect texture fetches, memory layout interpretation, UBWC/flag access, planar formats, and sparse/PRT behavior.

## Dependencies and integration points
The file depends on `a6xx_enums.xml` for shared texture formats and sampler enum types, `a8xx_enums.xml` for `a8xx_tex_swiz`, and `adreno_common.xml` for MSAA, compare, and color swap types. It integrates with A8xx driver code that includes generated A8xx/A6xx enum headers and with any userspace or kernel descriptor packing logic that must match A8xx memory-object layout.

## Risks
Address shift changes from A6xx are high risk: A8xx base/flag/U/V fields use bit ranges starting at bit 6 with `shr="6"`, while A6xx uses bit 5 shifts in many descriptor address fields. The descriptor has many intentional overlays for multiplanar and single-planar interpretations, so a generator or use-site misunderstanding can corrupt UV planes, flag buffers, or min-LOD/pitch fields. A typo such as `MIN_ARRAY_SLIZE_OFFSET` is part of the generated naming surface and could leak into code or tooling. Sparse/PRT and GMEM flags are also sensitive because incorrect bits can affect memory residency or tiling behavior.

## Test signals
Build signals include successful XML validation and generated-header use. Runtime signals include A8xx texture sampling tests for 1D/2D/3D/cube/buffer textures, MSAA texture fetches, mipmapping, min/max LOD, anisotropy, planar YUV formats, UBWC/flag-buffer formats, sparse/PRT cases if supported, GMEM fallback behavior, and conformance tests comparing swizzle/format results against expected pixels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a8xx_descriptors.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a8xx_enums.xml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a8xx_enums.xml

## Purpose
`a8xx_enums.xml` defines A8xx-specific state, cluster, debug-bus, USPTP, and texture-swizzle enums. It provides the symbolic values needed by generated headers for A8xx state selection, diagnostics, and descriptor packing.

## Important definitions
The file imports `freedreno_copyright.xml`, `adreno_common.xml`, and `adreno_pm4.xml`, then defines six enums. `a8xx_statetype_id` has 89 values covering TP context and data records, SP instruction/local-buffer data, USPTP data, and HLSQ metadata. `a8xx_state_location` has five values matching HLSQ state, HLSQ data path, SP top, USPTP, and HLSQ DP string locations. `a8xx_cluster` has 10 values and splits some A7xx-style front-end/cluster concepts into FE_US, FE_S, SP_VS, VPC_VS, VPC_US, GRAS, SP_PS, VPC_PS, and PS. `a8xx_debugbus_id` has 158 topology-specific values spanning GBIF/GMU/CX/GX/DBGC/RBBM/LARC/HLSQ/UCHE/PC/VFD/VPC/TSE/RAS/LRZ/SP/TP/RB/CCU/CMP/UFC and multiple GC/S/US instance IDs. `a8xx_usptp_id` identifies uSPTP0, uSPTP1, and SPTOP. `a8xx_tex_swiz` defines seven swizzle selectors: identity, zero, one, X, Y, Z, and W.

## Control flow and generation behavior
The XML is generated into `a8xx_enums.xml.h` through the msm Makefile. A8xx descriptor XML references `a8xx_tex_swiz`, and A8xx driver/debug paths can use the generated state, cluster, debugbus, and USPTP constants. No runtime code parses this XML directly.

## State and persistence
The XML does not own runtime state. It defines selector values that affect transient state capture, debugbus selection, and descriptor swizzle programming. Values compiled from this file persist in the built kernel and generated headers until the source is changed and rebuilt.

## Dependencies and integration points
It shares the common Adreno XML generation stack and is imported by `a8xx_descriptors.xml`. It also parallels `a7xx_enums.xml`, allowing A8xx driver code to use generation-specific topology and swizzle names rather than reusing incompatible A7xx IDs. The Makefile includes `generated/a8xx_enums.xml.h` in the generated header set.

## Risks
A8xx debugbus IDs are sparse and topology-heavy, with values up to 465; incorrect numbering can silently break debug capture on specific blocks or instances. The cluster enum changed shape from A7xx, so reused assumptions can route state collection to the wrong cluster. Texture swizzle values are directly consumed by A8xx descriptors; wrong values can produce incorrect channel mapping in normal rendering.

## Test signals
Build validation and generated-header compilation are the first checks. Runtime signals include A8xx state capture resolving state types and locations, debugbus reads for representative GC/S/US instances, descriptor tests that verify identity/zero/one/component swizzles, and crashdump/profiling tooling that recognizes A8xx-specific cluster and USPTP IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a8xx_enums.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/adreno_common.xml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/adreno_common.xml

## Purpose
`adreno_common.xml` is the shared Adreno rnndb fragment for cross-generation enums, inline bitsets, and common CP/register definitions. It is imported by most generation-specific Adreno XML files and generates `adreno_common.xml.h`, which is included directly by `adreno_gpu.h`.

## Important definitions
The file imports `freedreno_copyright.xml`, defines a `chip` enum with bare generation values `A2XX` through `A8XX`, and provides common rendering enums: draw primitive mode, compare function, stencil op, blend factor/op, surface endian, dither mode, depth format, copy-control mode, ROP code, render mode, MSAA sample count, shader thread/instruction modes, color swap, tessellation spacing, A5xx+ address and line modes, A6xx texture prefetch commands, and `adreno_pipe`.

It defines three inline bitsets. `adreno_rb_stencilrefmask` packs stencil reference, mask, and write-mask bytes. `adreno_reg_xy` packs X/Y coordinates plus `WINDOW_OFFSET_DISABLE`. `adreno_cp_protect` packs common protected-register region fields with base address, mask length, trap-write, and trap-read bits.

The `AXXX` 32-bit domain defines 71 common CP and scratch/event registers. Important groups include ringbuffer registers (`CP_RB_BASE`, `CP_RB_CNTL`, read/write pointer registers, write pointer delay/base), queue threshold and availability registers, scratch mask/address/registers, micro-engine state (`CP_ME_RDADDR`, `CP_ME_CNTL`, `CP_ME_STATUS`, ME RAM access), interrupt control/status/ack, CSQ/IB status, bin mask/select, indirect buffer base/size registers, CP status, and ME event source/address/data registers for VS, PS, CF, NRT, and VS fetch-done events.

## Control flow and generation behavior
The XML is a foundational import for generation-specific files. The Makefile passes XML inputs through `gen_header.py`, and `adreno_common.xml.h` is generated as part of the Adreno header set. Runtime control flow appears in the C driver through generated constants included by `adreno_gpu.h`; CP ringbuffer setup, interrupt handling, scratch register use, event programming, and protected register setup use these names and bit masks.

## State and persistence
The source itself is static. The generated constants describe persistent hardware state while the GPU is running: CP ringbuffer base/control and pointers, interrupt enables/status, scratch registers, protected register windows, event write addresses/data, and command processor status. Those hardware states persist until rewritten, reset, or power-cycled.

## Dependencies and integration points
This file is the dependency root for the generation-specific XML files in this work item. `a6xx_descriptors.xml`, `a6xx_enums.xml`, `a6xx_gmu.xml`, `a6xx_perfcntrs.xml`, `a7xx_enums.xml`, `a7xx_perfcntrs.xml`, `a8xx_descriptors.xml`, and `a8xx_enums.xml` all import it directly or rely on types it defines. Generated `adreno_common.xml.h` is included by `adreno_gpu.h`, so the common register and enum surface reaches the broader msm Adreno driver.

## Risks
Because this file is shared across generations, changes have a wide blast radius. Wrong CP ringbuffer or interrupt register definitions can break GPU submission, interrupt handling, or hang recovery. Misdefined blend/depth/stencil/MSAA enums can corrupt rendering across multiple generations. The common `adreno_cp_protect` layout differs from `a6x_cp_protect`, so protected-register programming must use the correct bitset for the target generation/path. Comments note limited confidence for some behavior, such as A5xx+ line mode and A6xx texture prefetch commands, so those areas should be validated on hardware before broadening use.

## Test signals
Build signals include XML validation, generated `adreno_common.xml.h`, and successful compilation of `adreno_gpu.h` consumers. Runtime signals include successful ringbuffer initialization/submission, CP interrupts and acknowledgments, scratch register reads/writes, protected register fault behavior, draw mode/depth/stencil/blend correctness under CTS/deqp, line rendering with and without MSAA, and stable hang recovery/state capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/adreno_common.xml -->
