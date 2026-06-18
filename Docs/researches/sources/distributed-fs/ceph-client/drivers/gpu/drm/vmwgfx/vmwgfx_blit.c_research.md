# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_blit.c

## Purpose
Provides CPU-side buffer-object copy helpers and a differential memcpy implementation that computes the bounding rectangle of modified pixels while copying. It is used where GPU blits are unavailable or inappropriate and where dirty tracking should avoid full-surface updates.

## Important APIs, Types, And Functions
- Generated `vmw_find_first_diff_*()` and `vmw_find_last_diff_*()` compare byte ranges using u8/u16/u32/u64 widths depending on alignment and architecture.
- `vmw_find_first_diff()` and `vmw_find_last_diff()` return granularity-aligned changed offsets.
- `vmw_memcpy()` is a plain copy callback for `struct vmw_diff_cpy`.
- `vmw_diff_memcpy()` copies only the changed span of a line and expands `diff->rect`.
- `struct vmw_bo_blit_line_data` caches mapped source/destination pages and copy metadata.
- `vmw_bo_cpu_blit_line()` copies one logical line across page boundaries using kmap.
- `vmw_bo_cpu_blit()` validates/populates TTM pages and copies a rectangle line-by-line.

## Control Flow
The main blit path asserts source and destination differ and are pinned or reserved, populates TTs if needed, dispatches external objects to a vmap copy path, converts scatter-gather lists to page arrays when necessary, then loops over rows. Each row maps only the current source and destination pages, copies up to the next page boundary, and advances offsets. The diff callback updates line/offset state to track a destination dirty rectangle.

## State, Persistence, Dependencies, And Integration
State is transient per copy. It depends on TTM TT population, page arrays or SG tables, `kmap_atomic_prot()`, dma-buf vmap/vunmap for imported objects, `vmw_bo_map_and_cache()` for local external-style mapping, and DRM rectangles. It integrates with fb/surface update paths and dirty tracking code that provide `struct vmw_diff_cpy`.

## Risks And Test Signals
Risks are page-boundary off-by-one errors, unbalanced atomic maps, insufficient bounds validation by callers, dirty rectangles not matching copied bytes, and external-object full memcpy not using the diff callback. Test signals include unaligned source/destination offsets, strides different from width, copies spanning many pages, imported dma-buf BOs, identical source data producing empty dirty rects, and granularity equal to bytes-per-pixel for 16/32/64-bit paths.
