<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pt_walk.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pt_walk.h

## Purpose

`xe_pt_walk.h` defines the generic page-table walker interface used by Xe GPU page-table code.

## Important APIs and Types

`struct xe_ptw` is the embeddable base for page-table nodes with optional `children` and `staging` arrays. `struct xe_pt_walk` stores callback ops, level shift array, max level, shared-walk mode, and whether to walk staging state. `xe_pt_entry_fn` is the callback signature, receiving parent, offset, level, address range, child pointer, action, and walk state. `struct xe_pt_walk_ops` provides `pt_entry` and optional `pt_post_descend`. Inline helpers `xe_pt_covers()`, `xe_pt_num_entries()`, and `xe_pt_offset()` compute coverage, entry counts, and offsets.

## Control Flow and State

The header has inline math only. Runtime traversal is implemented in `xe_pt_walk.c`. The `shifts` pointer may be changed during a walk, which lets bind code switch between normal 4K and compact 64K leaf layouts.

## Dependencies and Integration Points

It includes Linux `pagewalk.h` for `enum page_walk_action` and is used by `xe_pt_types.h` and `xe_pt.c`.

## Risks and Test Signals

Shift arrays, alignment math, and max-level selection define the walk shape. Off-by-one errors here affect all bind/unbind/zap paths. Tests should validate offset/count calculations at every level, partial edges, max-level masking, and compact shift changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pt_walk.h -->
