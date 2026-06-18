# File Research: sources/block-storage/lvm2/lib/format_text/import.c

## Summary
Implements generic text metadata import dispatch and checksum-aware metadata read helpers.

## Main Responsibilities
- Initializes the text metadata version handler list with version 1 operations.
- Reads metadata summaries from a device or file into a config tree, optionally doing checksum-only validation to skip reparsing.
- Reads full VG metadata from raw device ranges or files, reusing previously parsed VG data when MDA checksum and size match cached format data.
- Imports a VG from an already-built config tree and restores cached PV device state.
- Provides wrappers for metadata-file reads and config-tree-to-VG conversion.

## Important Behavior
`text_read_metadata()` stores `cached_mda_checksum` and `cached_mda_size` in `cached_vg_fmtdata`; when a later MDA matches, it can set `use_previous_vg` and avoid reparsing duplicate metadata. Successful full reads attach the config tree to `vg->committed_cft` for committed VG reconstruction.

## Risks And Invariants
The skip-parse path assumes checksum and size are enough to identify identical metadata content. Version dispatch currently has a fixed two-entry list, with only version 1 installed.
