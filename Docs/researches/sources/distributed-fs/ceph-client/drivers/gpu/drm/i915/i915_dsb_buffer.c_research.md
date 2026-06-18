# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_dsb_buffer.c

## Purpose
`i915_dsb_buffer.c` implements the i915 backing-buffer interface used by display DSB command submission. It allocates a GEM object, pins it in the GGTT, maps it write-combined, exposes read/write/fill/flush helpers, and exports those hooks through `intel_display_dsb_interface`.

## Important APIs, Types, and Functions
The local `struct intel_dsb_buffer` stores `cmd_buf`, pinned `vma`, and `buf_size`. Interface methods are `intel_dsb_buffer_ggtt_offset()`, `intel_dsb_buffer_write()`, `intel_dsb_buffer_read()`, `intel_dsb_buffer_fill()`, `intel_dsb_buffer_create()`, `intel_dsb_buffer_cleanup()`, and `intel_dsb_buffer_flush_map()`. The exported object is `i915_display_dsb_interface`.

## Control Flow
Create allocates the wrapper, creates contiguous LMEM if `HAS_LMEM()` or an internal shmem GEM object otherwise, sets shmem cache coherency to uncached for system memory, pins the object globally in the GGTT via `i915_gem_object_ggtt_pin()`, maps it with `I915_MAP_WC`, and stores state. Cleanup calls `i915_vma_unpin_and_release()` with map release and frees the wrapper. Fill bounds-checks the byte range against `buf_size` and then writes through the CPU mapping.

## State and Persistence Behavior
The buffer persists while display code owns the returned `intel_dsb_buffer`. Its GEM object remains pinned in GGTT and mapped WC. The GGTT offset is stable until cleanup. Writes are CPU-visible in the mapping and `flush_map` pushes GEM map writes as needed.

## Dependencies and Integration Points
This file integrates display DSB code with i915 GEM internal/shmem/LMEM allocation, GGTT pinning, VMA lifetime management, cache coherency, and display parent interfaces. It is reached through `i915_driver.c`'s display parent interface.

## Risks
Allocation and pinning failures must release the GEM object and wrapper exactly once. DSB command memory must be contiguous in LMEM where required. Fill takes a byte size but an index in dwords; incorrect callers can still trigger WARN-only bounds issues. Forgetting `flush_map` before hardware consumption can leave stale command contents.

## Test Signals
Display DSB paths should allocate buffers, program commands, flush maps, and complete modeset/plane update flows. Exercise both LMEM and system-memory platforms, error injection in object creation/pinning/mapping, and warnings for fill bounds.
