# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h lines 20491-21073

## Scope And Purpose

This chunk is the final section of AMD's generated `soc24_enum.h` hardware enum header. It starts at the tail of the `SU_PERFCNT_SEL` enum, defines complete selector enums for RMI, UTCL1, GC EA SE, and LSDMA performance counters, defines the `ROM_SIGNATURE` constant, defines `EFC_SURFACE_PIXEL_FORMAT`, and closes the `_soc24_ENUM_HEADER` include guard.

The file is under a `ceph-client` source mirror, but this chunk is AMDGPU register and packet metadata for SoC24-era AMD GPUs. It does not implement Ceph filesystem behavior, allocate memory, call functions, branch, lock, perform MMIO, or persist software state. Its purpose is to give driver and tooling code stable symbolic names for numeric hardware encodings that are written into register fields, command packets, firmware interfaces, or decoded from hardware-visible values.

## Important APIs, Types, And Constants

The exported API in this range is a C enum/define namespace:

- `SU_PERFCNT_SEL` tail entries `PERF_OUTPUT_PRIM_1_SC` through `PERF_PA_BUSY`, which complete shader/geometry front-end and primitive/output performance counter event IDs.
- `RMIPerfSel`, whose `RMI_PERF_SEL_*` entries select RMI performance events, including RB-to-RMI write/read requests, per-client-ID request/return valid events, NACKs, FIFO occupancy/empty/idle/starve/stall/busy events, RMI-to-TC requests and returns, TCIW formatter/reorder activity, early write acknowledgements, and consumer probe-generator handshakes.
- `UTCL1PerfSel`, whose `UTCL1_PERF_SEL_*` entries select UTCL1 TLB/cache events: requests, hits, misses, miss-handler activity, UTCL2 requests/returns, XNACK retry and fault returns, invalidation requests/acks, bypass requests, page-size bucket hits/returns, per-cache-core request/stall/collision/eviction counters, and ALOG interrupt/cache/PMM-credit events.
- `GC_EA_SE_PERFCOUNT_SEL`, whose `GC_EA_SE_PERF_SEL_*` entries select graphics client export-address/shared-engine memory traffic events. The enum covers DRAM, GMI, and IO read/write request groups, chained requests, request sizes, latency start/end markers, SARB virtual-channel traffic, return-valid/probe activity, MAM ARAM/DBIT hit/evict/query/flush/aflush events, coherent size requests, and RW turn-around metrics.
- `LSDMA_PERF_SEL`, whose `LSDMA_PERF_SEL_*` entries select low-speed SDMA/copy-engine performance events. The enum covers ring-buffer and indirect-buffer state, executor idle, MC read/write traffic, semaphore and interrupt response paths, command packet counting, copy-engine and F32 paths, context changes and doorbells, UTCL1/ATCL2 invalidation/XNACK/ACK events, MMHUB request/return events, operation start/end matching, CE busy windows, perfcnt triggers, DRAM ECC, and generated NACK errors.
- `ROM_SIGNATURE`, fixed to `0x0000aa55`, the conventional ROM image signature value used when probing or validating option ROM/VBIOS content.
- `EFC_SURFACE_PIXEL_FORMAT`, whose `EFC_*` entries encode surface pixel formats, including 16-bit and 32-bit RGB(A), YCrCb/YCbCr channel orderings, 10/12/16-bit component formats, float/unorm/snorm variants, 4:2:0 planar formats, 4:2:2 packed formats, packed 11/10-bit RGB/BGR formats, ACrYCb/CrYCbA 10-bit formats, and mono 8/10/12/16 formats.

All enum values are explicit hexadecimal constants. That makes the names an ABI-like mapping to hardware selector values rather than compiler-chosen C enum ordinals.

## Control Flow And Runtime Behavior

There is no runtime control flow in this chunk. Runtime behavior is indirect:

1. SoC24 AMDGPU/KFD source files include `soc24_enum.h` together with SoC24 register offset/mask headers.
2. Driver, debug, profiling, or firmware-interface code selects one of these enum values when programming a performance counter's event-select field, validating a ROM signature, or describing a surface/pixel format.
3. Hardware interprets the programmed numeric value and routes the corresponding event, status source, or data-format interpretation.

The direct include users visible in this tree include `amdgpu/gfx_v12_0.c`, `amdgpu/gfx_v12_1.c`, `amdgpu/gmc_v12_0.c`, `amdgpu/gfxhub_v12_0.c`, `amdgpu/mmhub_v4_1_0.c`, and `amdkfd/kfd_device_queue_manager_v12.c`. This chunk's specific enum names are not directly referenced elsewhere in the local tree, which is consistent with a generated all-in-one hardware namespace: consumers include the complete header while using only the symbols relevant to a given ASIC path or diagnostic build.

## State And Persistence Behavior

The header stores no software state. The state represented by these constants lives in hardware blocks or ROM/image data:

- Performance selector enums become transient or programmed hardware state when software writes event IDs into performance counter select registers. Counter state then persists in the GPU block until reprogrammed, reset, power-gated, or restored by driver suspend/resume handling.
- RMI, UTCL1, GC EA SE, and LSDMA events observe hardware queues, cache/TLB behavior, memory-fabric traffic, invalidation handshakes, request/return paths, stalls, busy/idle cycles, and error conditions. Some selected events are instantaneous pulses, some count cycles, and some accumulate occupancy or latency-style values depending on the owning counter block.
- `ROM_SIGNATURE` is not state by itself; it is the expected little-endian marker in ROM/VBIOS data used to distinguish a valid image header from unrelated memory.
- `EFC_SURFACE_PIXEL_FORMAT` values describe persistent format fields in surfaces, scanout/copy/display paths, firmware tables, or packet/register payloads that reference these encodings. The header does not define layout stride, tiling, endian, modifier, or colorimetry policy.

Access type and side effects are not encoded in the enum names. For performance counters, the register programming model defines whether a selector can be changed while counting, whether counters must be stopped/reset first, and how overflow/latch behavior works. For ROM and pixel-format use, validation and compatibility rules live in the consumer code and hardware specification.

## Dependencies And Integration Points

This chunk depends on the broader generated SoC24 register header set. `soc24_enum.h` supplies numeric encodings, while other headers under `drivers/gpu/drm/amd/include/asic_reg/` supply register offsets, masks, and reset values. AMDGPU helper layers then compose these constants into register writes or packet fields.

Important integration surfaces include:

- GFX performance monitoring and profiling paths that select `SU_PERFCNT_SEL` tail events for shader/primitive pipeline observation.
- Memory-fabric and render-backend diagnostics that can use `RMIPerfSel` to attribute RB/RMI/TC request, return, NACK, FIFO, stall, and probe-generator behavior.
- GPU virtual-memory and MMU/TLB diagnostics that can use `UTCL1PerfSel` to inspect UTCL1 hit/miss behavior, UTCL2 interaction, invalidation latency, cache-core behavior, and translation fault/XNACK activity.
- Graphics memory-export and shared-engine performance tooling that can use `GC_EA_SE_PERFCOUNT_SEL` to measure DRAM/GMI/IO request mix, latency windows, SARB traffic, MAM flush/query behavior, and coherent request sizes.
- SDMA/copy-engine profiling, reset triage, and memory-translation debugging that can use `LSDMA_PERF_SEL` to isolate ring/IB pressure, MC/MMHUB request flow, ATCL2/UTCL1 invalidation and XNACK returns, CE/F32 paths, doorbells, command windows, ECC, and NACK-generation errors.
- ROM/VBIOS parsing or validation code that compares image contents with `ROM_SIGNATURE`.
- Display, encode/copy, or firmware table paths that need a SoC24 enum value for `EFC_SURFACE_PIXEL_FORMAT`.

Because these are generated hardware encodings, they must remain synchronized with the SoC24 hardware database and any firmware or tools that consume the same numeric values. Mixing selector values from another ASIC generation can compile cleanly but route counters to the wrong internal signal.

## Risks And Edge Cases

- Numeric drift is high impact. A wrong enum value can program a valid but unintended event selector, producing misleading performance data without an obvious build failure.
- The chunk starts in the middle of `SU_PERFCNT_SEL`; the final report must merge with the previous chunk before treating the SU selector enum as complete.
- Several enum families are dense but have intentional gaps, such as `LSDMA_PERF_SEL` skipping values around `0x16`, `0x17`, `0x24`, `0x2c`, and `0x2d`, and `EFC_SURFACE_PIXEL_FORMAT` leaving ranges unused. Filling gaps or renumbering entries would break the hardware ABI.
- Many performance events have similar per-client or per-cache-core names. Copy/paste mistakes between CID0-CID7, cache core 0-3, read/write, request/return, or start/end events can silently invert diagnostic conclusions.
- Performance counter semantics are block-specific. Some selectors count cycles, some count pulses, some count sizes or latency windows, and some may require an accompanying counter mode. The enum alone is not enough to interpret raw counter values.
- RMI, UTCL1, and LSDMA events touch memory translation, invalidation, XNACK, NACK, MMHUB, and fault paths. Misinterpreting those counters can lead to incorrect conclusions about IOMMU, VM fault, or DMA-engine behavior.
- `ROM_SIGNATURE` should be checked with correct byte ordering and bounds-checked ROM access. A matching signature alone is not a full VBIOS validation.
- `EFC_SURFACE_PIXEL_FORMAT` names encode component order and bit-depth, but not all display/color metadata. Consumers still need to pair these values with plane layout, pitch, tiling/modifier, color space, and hardware block support.

## Test And Validation Signals

Useful validation is mostly compile-time, generated-header comparison, and hardware/runtime diagnostics:

- Build AMDGPU and KFD paths that include `soc24_enum.h`, especially GFX12, GMC12, GFXHUB12, MMHUB 4.1, and KFD queue-manager code, to catch syntax or missing-symbol regressions.
- Mechanically compare this enum range against the authoritative SoC24 hardware register database or generated upstream header to confirm each explicit numeric value and intentional gap.
- For performance selectors, run hardware perf-counter smoke tests that program representative events from each family and confirm counters change under matching workloads: geometry/primitive workloads for SU tail events, render-backend/memory traffic for RMI and GC EA SE, VM pressure and invalidation workloads for UTCL1, and SDMA copy/fill/doorbell/IB workloads for LSDMA.
- Validate read/write event pairs and per-client/per-core selectors by using asymmetric workloads where one CID, cache core, or engine path is expected to dominate.
- Exercise fault and retry paths, where practical, to check UTCL1 XNACK/fault, LSDMA ATCL2 return, DRAM ECC, and NACK-generation event visibility.
- Check ROM parsing paths with valid and invalid ROM images to ensure `ROM_SIGNATURE` is used as an initial marker rather than a complete integrity check.
- Validate EFC format mappings with display/copy/firmware tests that cover RGB(A), YUV planar, YUV packed, high-bit-depth, float, and mono formats, watching for swapped channels, wrong bit significance, or unsupported-format fallbacks.

## Cross-Chunk Notes

This is the final chunk of `soc24_enum.h`; it closes the include guard at line 21073. The previous chunk is required for the beginning and main body of `SU_PERFCNT_SEL`, while this chunk completes it and then covers the final enum/define families. A later merge/reconciliation pass should combine all chunks for this source file before making whole-file claims about the SoC24 enum namespace.
