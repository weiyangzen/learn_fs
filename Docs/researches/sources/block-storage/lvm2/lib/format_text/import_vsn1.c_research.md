# File Research: sources/block-storage/lvm2/lib/format_text/import_vsn1.c

## Summary
Implements version-1 text metadata parsing into `struct volume_group`, including PVs, LVs, segments, historical LVs, tags, profiles, locks, and VG summaries.

## Main Responsibilities
- Validates top-level `contents` and `version` fields.
- Reads IDs, status/compatible flags, tags, and string lists.
- Parses physical volumes, device hints/IDs, PE layout, bootloader areas, and PV summary records.
- Parses logical volume names first, then segment contents in a second pass.
- Resolves segment areas to PVs or LVs via names, validates area counts and offsets, and merges/checks segment layout.
- Reads historical logical volumes and later resolves origin/descendant interconnections.
- Builds lightweight `lvmcache_vgsummary` data for label scans.

## Important Behavior
LV import is deliberately multi-pass: `_read_lvnames()` creates LV objects and status; `_read_lvsegs()` reads the LV UUID and segments after all LV names exist; historical LV interconnections are resolved after live and historical names are known.

`text_import_areas()` consumes alternating volume-name and offset values, resolves each to a PV or LV, rejects missing/bad/out-of-range offsets, and verifies the exact expected number of areas.

## State And Dependencies
The parser allocates from `vg->vgmem`, uses radix trees for temporary PV/LV name lookup, links PVs into VG lists, adjusts VG extent/free counts, and calls segtype-specific `text_import` handlers. It depends on metadata allocators, segtype registry, lvmlockd metadata strings, profile loading, and lvmcache summary structures.

## Risks And Invariants
Metadata is trusted only after strict required-field checks, but many optional fields are backward-compatible. Segment order, counts, and gap/overlap checks are critical because later allocation and activation rely on a coherent LV segment list. Temporary radix trees are intentionally destroyed before returning the VG.
