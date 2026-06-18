# File Research: sources/block-storage/lvm2/lib/striped/striped.c

## Purpose

`striped.c` implements the segment type handler for both striped and linear LVM segments. Linear is represented as the same handler with one area.

## Metadata and Display

- `_striped_name()` reports `linear` when `area_count == 1`, otherwise the segment type name.
- `_striped_display()` prints a single stripe via `display_stripe()` for linear segments, or prints stripe count, stripe size, and each stripe for striped segments.
- `_striped_text_import_area_count()` reads `stripe_count`.
- `_striped_text_import()` reads `stripe_size` for multi-stripe segments, reads the `stripes` array, divides `area_len` by area count, and imports areas via `text_import_areas()`.
- `_striped_text_export()` writes `stripe_count`, optional `stripe_size`, and area mappings via `out_areas()`.

## Segment Merge Logic

- `_striped_segments_compatible()` allows merges only when area count, stripe size, area types, PV identity, PE continuity, and tags match.
- It currently only supports merging PV-backed areas, with comments noting possible relaxation.
- `_striped_merge_segments()` extends length and area length, then merges corresponding PV segments.

## Device-Mapper Support

When enabled:

- `_striped_target_status_compatible()` treats `linear` target status as compatible.
- `_striped_add_target_line()` emits either a linear target for one area or a striped target for multiple areas, then appends area mappings with `add_areas_line()`.
- `_striped_target_present()` caches target availability and requires both `linear` and `striped` targets when activation is enabled.

## Segment Type Registration

`_striped_ops` wires name/display/import/export/merge and optional device-mapper callbacks.

`_init_segtype()` allocates and initializes the handler with:

- supplied name (`striped` or `linear`)
- target flags (`SEG_STRIPED_TARGET` or `SEG_LINEAR_TARGET`)
- common flags `SEG_CAN_SPLIT | SEG_AREAS_STRIPED`

Public constructors:

- `init_striped_segtype()`
- `init_linear_segtype()`

## Important Edge Cases

- `_striped_add_target_line()` rejects segments with zero areas.
- Linear and striped share most behavior; the distinction is primarily `area_count` and target/name selection.
- Target presence is cached statically.
