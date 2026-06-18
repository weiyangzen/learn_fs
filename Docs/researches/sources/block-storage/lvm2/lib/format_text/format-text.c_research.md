# File Research: sources/block-storage/lvm2/lib/format_text/format-text.c

## Summary
Implements the LVM2 text metadata format backend: PV initialization, label/MDA layout, raw metadata read/write/commit, file-backed metadata operations, metadata-area management, and registration of the `lvm2`/`text` format.

## Main Responsibilities
- Reads and validates raw metadata-area headers, including checksum, magic, version, start, size, and endian translation.
- Reads VG metadata from raw circular metadata areas, including committed and precommitted `raw_locn` slots.
- Writes exported VG text into the circular metadata buffer, enforcing that two copies fit, handling wraparound, sector alignment, CRC calculation, and precommit/commit slot updates.
- Supports file-backed metadata areas with temp-file write, fsync, rename-based commit, backup-only commit, and removal.
- Calculates and installs PV data areas, bootloader areas, first/second metadata areas, PV header extension flags, and label rewrites.
- Creates format instances, metadata-area operation tables, the orphan VG, and the text labeller.

## Important Behavior
Raw metadata updates are staged in three steps: `_vg_write_raw()` writes new text and saves the new `raw_locn` in memory; `_vg_precommit_raw()` writes it to slot 1; `_vg_commit_raw()` promotes it to slot 0 and clears slot 1. Revert clears the precommit slot by setting the in-memory `rlocn.size` to zero and rewriting the header.

`read_metadata_location_summary()` is the label-scan fast path. It records scan-time text offset/checksum, validates location bounds before `uint32_t` casts, optionally avoids reparsing already-known metadata by checksum, and populates `lvmcache_vgsummary`.

## State And Dependencies
The file owns `struct text_fid_context`, `struct mda_context` usage, raw/file `metadata_area_ops`, and `format_handler` callbacks. It depends on config import/export, CRC, device I/O, label handling, lvmcache, format instances, PV/LV metadata helpers, and LVM memory pools.

## Risks And Invariants
The circular buffer logic depends on exact byte arithmetic for old/new start/last/wrap positions and on the invariant that two metadata copies fit in the MDA. `raw_locn.flags` has legacy endian handling. MDA placement must avoid overlap with labels, bootloader areas, PE data, and second metadata areas.
