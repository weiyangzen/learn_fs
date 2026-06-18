# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/intel_memory_region.c

## Purpose
This file tests Intel memory-region allocation behavior, especially the TTM buddy-backed region manager and local memory (LMEM). It covers mock region fill/reserve/contiguous fragmentation, non-power-of-two region geometry, scatterlist segment limits, mappable IO aperture behavior, live LMEM creation/clearing/CPU/GPU writes, and memcpy performance between regions.

## Important APIs, Types, And Functions
- Public entries are `intel_memory_region_mock_selftests()`, `intel_memory_region_live_selftests()`, and `intel_memory_region_perf_selftests()`.
- Object helpers include `close_objects()`, `igt_object_create()`, `igt_object_release()`, and `is_contiguous()`.
- Mock tests include `igt_mock_fill()`, `igt_mock_reserve()`, `igt_mock_contiguous()`, `igt_mock_splintered_region()`, `igt_mock_max_segment()`, and `igt_mock_io_size()`.
- Live LMEM tests include `igt_lmem_create()`, `igt_lmem_create_with_ps()`, `igt_lmem_create_cleared_cpu()`, `igt_lmem_write_gpu()`, and `igt_lmem_write_cpu()`.
- Perf helpers include `create_region_for_mapping()`, `_perf_memcpy()`, and `perf_memcpy()`.

## Control Flow
Mock tests create a mock 2 GiB region and allocate progressively or randomly sized objects, pin pages, reserve random subranges, fragment contiguous space, inspect TTM buddy block metadata, verify scatterlist segment size/alignment, and model mappable-vs-non-mappable allocation pressure. Live tests skip without LMEM or on wedged GTs. They create LMEM objects with page-size constraints, verify DMA alignment, alternate cleared/dirty allocations, issue GPU dword writes and CPU readback, or use a copy engine migration clear followed by randomized WC CPU writes. Perf tests iterate all source/destination memory-region pairs, map objects WB/WC, and measure `memcpy`, long-word copy, and `i915_memcpy_from_wc` across fixed sizes.

## State And Persistence
State consists of mock memory regions, GEM objects, pinned pages, TTM buddy resources, scatterlists, context/file handles, engine PM references, DMA reservation fences, mapped CPU pointers, and temporary migration requests. Cleanup unpins pages, drops object pages to avoid region pollution, drains freed objects, destroys mock regions, and releases contexts/files. No persistent storage is written.

## Dependencies And Integration Points
It depends on memory-region APIs, GEM LMEM/TTM helpers, `gpu_buddy`, migrate context, copy engines, object mapping/cache-domain helpers, mock region/device setup, random helpers, and live flush behavior. It integrates with mock, live, and perf registries.

## Risks
Allocation-size tests intentionally approach region exhaustion; `-ENOMEM`, `-ENXIO`, and `-E2BIG` can be expected in bounded cases. Contiguous allocation logic is sensitive to buddy fragmentation and page size. Live CPU/GPU write tests depend on copy-engine availability, cache-domain transitions, and proper fence reservation. Perf numbers are diagnostic rather than pass/fail, but mapping failures must be normalized for unavailable regions.

## Test Signals
Signals include matching allocation/free-space accounting, contiguous scatterlists where required, expected failure for too-large contiguous requests, correct buddy `max_order`, no oversized scatterlist segments, mappable allocation totals, zeroed CPU-cleared LMEM, aligned page-size allocations, correct CPU readback after GPU writes, randomized CPU write verification, and memcpy throughput logs.
