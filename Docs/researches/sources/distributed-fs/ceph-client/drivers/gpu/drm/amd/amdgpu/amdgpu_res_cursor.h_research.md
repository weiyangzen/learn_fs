## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_res_cursor.h

Purpose: provides an inline cursor for walking the physical backing ranges of TTM resources used by AMDGPU memory management. It abstracts VRAM buddy blocks and range-manager nodes behind a common `start`, `size`, and `remaining` iteration API.

Important APIs and types: `struct amdgpu_res_cursor` stores current physical start, current segment size, remaining requested bytes, current backend node pointer, and memory type. `amdgpu_res_first()` initializes a cursor for a resource subrange. `amdgpu_res_next()` advances by bytes, crossing nodes as needed. `amdgpu_res_cleared()` reports whether the current VRAM buddy block is marked cleared.

Control flow: initialization validates `start + size <= res->size`, selects behavior by `res->mem_type`, walks VRAM buddy block lists or TTM range-manager `drm_mm_node` arrays until the requested start offset is located, and sets the first segment to the minimum of node remainder and requested size. Advancing decrements remaining, adjusts within-segment offsets when possible, or moves to the next VRAM block/range node when the current segment is exhausted. Unsupported or null resources fall back to a linear cursor with no backend node.

State and persistence: the cursor is stack/local iteration state; it does not mutate TTM resources. It reads VRAM manager block metadata, range-manager nodes, and cleared flags.

Dependencies and integration points: depends on DRM MM, TTM resource/range manager, and `amdgpu_vram_mgr.h`. It is used by VM updates, TTM moves, display pinning, VRAM SG-table creation, and coredump code to translate logical BO offsets into physical GPU-addressable chunks.

Risks: off-by-one or unit errors between bytes, pages, and dwords can corrupt DMA/VM operations. `BUG_ON(size > cur->remaining)` and `BUG_ON(start + size > res->size)` make invalid callers fatal. The fallback path can hide unsupported memory types by returning linear offsets, which is useful for special paths but risky if callers assume physical placement. `amdgpu_res_cleared()` only supports VRAM.

Test signals: migration and VM-update tests should cover VRAM multi-block resources, GTT/range-manager resources, doorbell/MMIO remap placements, zero-size ranges, and cleared VRAM skip behavior in TTM clearing paths.
