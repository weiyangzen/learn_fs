# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_client_blt.c

## Purpose
Validates copy-engine BLT copies among linear, X-tiled, and Y-major/Tile4 buffers. It verifies that software-visible tiling layouts remain correct across object rebinding and GGTT eviction-like placement changes.

## APIs And Control Flow
Important pieces are `enum client_tiling`, `struct blit_buffer`, `struct tiled_blits`, `linear_x_y_to_ftiled_pos()`, `prepare_blit()`, `tiled_offset()`, `verify_buffer()`, `tiled_blit()`, and `igt_client_tiled_blits()`. The test creates buffers and a batch VMA, fills scratch data, emits `XY_FAST_COPY_BLT` when supported or legacy copy commands with BCS tiling controls otherwise, relocates buffers into selected holes, and verifies expected tiled offsets.

## State, Dependencies, Integration, Risks, And Tests
State is per-run GEM objects, VMAs, batch buffers, and random placement. Dependencies include copy-engine lookup, BLT command definitions, VMA pinning, memory-region allocation, and display capability checks for fast X tiling. Risks include F-tile subtile remapping, Tile4 flags, X-tile fastblit restrictions, swizzle quirks, pitch units, and relocation offsets. Signals include buffer creation errors, BLT submission failures, verification mismatches, and skips on unsupported swizzle or engine/platform combinations.
