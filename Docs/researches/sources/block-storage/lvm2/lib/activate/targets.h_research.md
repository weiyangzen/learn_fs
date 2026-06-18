# File Research: sources/block-storage/lvm2/lib/activate/targets.h

## Role

`targets.h` is a small bridge header for segment target-line construction. It forward-declares the activation/device-manager and libdm tree types needed by target builders and exposes `add_areas_line()`.

## Interface

`add_areas_line(struct dev_manager *dm, struct lv_segment *seg, struct dm_tree_node *node, uint32_t start_area, uint32_t areas)` adds a range of LV segment areas to an in-progress DM tree node target line.

The implementation in `dev_manager.c` handles PV-backed areas, LV-backed areas, RAID data/metadata pairs, unassigned RAID areas, partial/degraded activation filler devices, and error handling for incomplete non-RAID/non-integrity segments.

## Dependency Context

This header avoids including full metadata or libdm headers by forward-declaring `struct dev_manager`, `struct lv_segment`, and `struct dm_tree_node`. Segment-type implementation files can include it to call the area builder without depending on the full `dev_manager.c` internals.

## Invariants

- The function assumes the caller has already created a compatible target on `node`.
- Segment type, area count, and metadata-area layout must match the target being generated.
- Partial/degraded activation policy is read through `seg->lv->vg->cmd`, so target builders must pass real metadata-backed segments.
