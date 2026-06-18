# File Research: sources/block-storage/lvm2/lib/format_text/format-text.h

## Summary
Declares the public interface and core constants for the LVM2 text metadata format.

## Main Contents
Defines `FMT_TEXT_NAME`, `FMT_TEXT_ALIAS`, orphan VG naming, and the maximum two metadata areas per PV. Declares archive/backup listing APIs, `create_text_format()`, `text_labeller_create()`, PV header read, data/bootloader/metadata-area list helpers, outdated MDA wiping, and text format instance buffer preservation helpers.

## Key Structures
`struct text_context` describes file-backed metadata paths and description text. `struct disk_locn` is the packed on-disk offset/size pair used in PV headers. `struct data_area_list` links disk locations for PE data areas.

## Risks And Invariants
`disk_locn` is packed because it is persisted on disk. The helper declarations are shared across label, layout, and format code, so callers must respect ownership differences between pool-allocated lists and malloc/free-backed lists.
