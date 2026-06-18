# File Research: sources/block-storage/lvm2/lib/metadata/lv_alloc.h

Purpose: declares LV segment allocation and area manipulation APIs used to allocate extents, build LV segments, connect segment areas to PVs/LVs, release areas, and derive parallel allocation constraints.

Read coverage: complete file read, 88 lines.

Key contents:
- Declares `alloc_lv_segment()` for constructing an `lv_segment` with segment type, LV, LE/length/reshape metadata, status, stripe/cache/mirror sizing, area counts, copies, copied extents, and pvmove source.
- Declares area setters and movers for PV-backed and LV-backed segment areas.
- Declares release helpers, including a discard-aware release path.
- Forward-declares `struct alloc_handle` and declares `allocate_extents()` for central VG/LV extent allocation.
- Declares helpers to add allocated areas as normal segments, mirror areas, segmented mirror images, mirror LVs, log segments, and virtual segments.
- Declares `alloc_destroy()` and `build_parallel_areas_from_lv()`.

Dependencies:
- Includes `metadata-exported.h` for LV, VG, PV, segment type, allocation policy, and list types.
- Implemented by LV allocation/manipulation code and used by cache/integrity/merge/layering code when constructing or splitting segments.

Risk and edge cases:
- Segment area ownership and back references must remain consistent with `segs_using_this_lv` and PV segment lists, or validation in `merge.c` will fail.
- `allocate_extents()` has many geometry and policy parameters; incorrect stripe/mirror/log values can create invalid metadata even if allocation succeeds.
