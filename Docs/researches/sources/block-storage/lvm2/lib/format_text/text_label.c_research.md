# File Research: sources/block-storage/lvm2/lib/format_text/text_label.c

## Summary
Implements the LVM2 text-format labeller: label recognition, PV header writing, PV label layout validation, label scan summary reads, and metadata/data/bootloader area list management.

## Main Responsibilities
- Recognizes `LVM2 001` label headers.
- Writes PV headers with PV UUID, device size, data areas, metadata-area header locations, PV header extension, flags, and bootloader areas.
- Allocates and frees data areas, bootloader areas, and metadata areas.
- Validates PV label buffer layout before iterating embedded disk-location lists.
- During label scan, creates/updates lvmcache entries, records data/MDA/BA locations, reads MDA headers and summaries, and saves bad MDAs for repair.
- Registers label operation callbacks through `text_labeller_create()`.

## Important Behavior
`label_check_pv_layout()` checks the PV header offset and ensures both data-area and metadata-area lists terminate within the label sector before callers iterate them. `_text_read()` scans up to two MDAs, updates VG name/id from summaries, and removes bad MDAs from normal use while saving them in lvmcache bad-MDA lists for `vgck --updatemetadata`.

## State And Dependencies
The file bridges label buffers to `lvmcache_info`, `metadata_area`, and `mda_context`. It depends on label headers, endian translation, raw MDA summary reading, device cache invalidation, and lvmcache duplicate/bad-MDA handling.

## Risks And Invariants
PV labels require at least one data area when written. Label scan has a retry path for races where an unlocked scan sees an MDA header and metadata text from different rewrites. MDA numbering and bad-field tracking are important for later repair.
