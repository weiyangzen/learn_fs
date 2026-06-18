# Group Research: group_1128_lvm2_sources_block_storage_lvm2_lib_format_text_format_text_c_sourc_85f9cc5ddd47

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/format_text/format-text.c -->
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
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/format_text/format-text.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/format_text/format-text.h -->
# File Research: sources/block-storage/lvm2/lib/format_text/format-text.h

## Summary
Declares the public interface and core constants for the LVM2 text metadata format.

## Main Contents
Defines `FMT_TEXT_NAME`, `FMT_TEXT_ALIAS`, orphan VG naming, and the maximum two metadata areas per PV. Declares archive/backup listing APIs, `create_text_format()`, `text_labeller_create()`, PV header read, data/bootloader/metadata-area list helpers, outdated MDA wiping, and text format instance buffer preservation helpers.

## Key Structures
`struct text_context` describes file-backed metadata paths and description text. `struct disk_locn` is the packed on-disk offset/size pair used in PV headers. `struct data_area_list` links disk locations for PE data areas.

## Risks And Invariants
`disk_locn` is packed because it is persisted on disk. The helper declarations are shared across label, layout, and format code, so callers must respect ownership differences between pool-allocated lists and malloc/free-backed lists.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/format_text/format-text.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/format_text/import-export.h -->
# File Research: sources/block-storage/lvm2/lib/format_text/import-export.h

## Summary
Defines the shared text metadata import/export contract, format-version dispatch table, flag conversion APIs, and metadata read/export entry points.

## Main Contents
- Text metadata identity fields: `contents = "Text Format Volume Group"` and `version = 1`.
- `enum pv_vg_lv_e` distinguishes PV, VG, and LV flag namespaces.
- Flag masks distinguish compatible flags, status flags, and segment-type/LV flags.
- `struct text_vg_version_ops` supplies version-specific `check_version`, `read_vg`, `read_desc`, and `read_vgsummary` callbacks.

## Key APIs
Declares version-1 initialization, flag printing/reading, LV flag parsing, file/raw export, full metadata read, metadata-file read, and metadata-summary read.

## Risks And Invariants
Import dispatch assumes version handlers can reject incompatible config trees cleanly. Summary reads and full reads share checksum and wraparound parameters, so callers must pass consistent raw MDA location data.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/format_text/import-export.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/format_text/import.c -->
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
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/format_text/import.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/format_text/import_vsn1.c -->
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
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/format_text/import_vsn1.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/format_text/layout.h -->
# File Research: sources/block-storage/lvm2/lib/format_text/layout.h

## Summary
Defines the on-disk layout structures and constants for LVM2 text-format PV labels and metadata areas.

## Main Contents
- PV header extension version `2`, with bootloader area support and `PV_EXT_USED` flag support.
- Packed `struct pv_header_extension`, `struct pv_header`, `struct raw_locn`, and `struct mda_header`.
- `RAW_LOCN_IGNORED` flag and helpers for ignored metadata locations.
- Metadata constants: `FMTT_MAGIC`, `FMTT_VERSION`, `MDA_HEADER_SIZE`, `LVM2_LABEL`, and original metadata alignment.
- `struct mda_lists` and `struct mda_context` for format-private raw/file MDA operations.

## API Surface
Declares MDA header parsing/reading, PV label layout validation, metadata-location summary reading, and raw location ignore helpers.

## Risks And Invariants
All persisted structs are packed and fields with `_xl` require endian translation. PV header disk-location arrays are null-terminated lists embedded in one label sector, so bounds validation is required before iteration.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/format_text/layout.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/format_text/text_export.h -->
# File Research: sources/block-storage/lvm2/lib/format_text/text_export.h

## Summary
Declares formatter helpers used by text metadata export code.

## Main Contents
Provides convenience macros `outsize`, `outhint`, `outfc`, `outf`, and `outnl` that return failure to the caller when output operations fail. Declares formatted output helpers, config-node output, segment-area output, indentation controls, and newline output.

## Risks And Invariants
The output functions are annotated with `printf` format checking and `warn_unused_result`; callers are expected to propagate write failures immediately through the macros.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/format_text/text_export.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/format_text/text_import.h -->
# File Research: sources/block-storage/lvm2/lib/format_text/text_import.h

## Summary
Small import header exposing the shared segment-area parser.

## API Surface
Declares `text_import_areas(struct lv_segment *seg, const struct dm_config_node *sn, const struct dm_config_value *cv, uint64_t status)`, used by segment-type import handlers to parse area arrays from text metadata.

## Risks And Invariants
The function expects the segment’s area count to be established before import and consumes config values as name/offset pairs.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/format_text/text_import.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/format_text/text_label.c -->
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
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/format_text/text_label.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/freeseg/freeseg.c -->
# File Research: sources/block-storage/lvm2/lib/freeseg/freeseg.c

## Summary
Registers the internal `free` segment type.

## Main Behavior
Allocates a `segment_type`, assigns the destroy handler, sets the name to `SEG_TYPE_NAME_FREE`, and marks it `SEG_VIRTUAL | SEG_CANNOT_BE_ZEROED`.

## Risks And Invariants
This is a minimal virtual segtype; it has no import/export or activation behavior beyond registration and destruction.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/freeseg/freeseg.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/id/id.c -->
# File Research: sources/block-storage/lvm2/lib/id/id.c

## Summary
Implements LVM ID generation, validation, comparison, formatting, parsing, and pool-backed formatted copies.

## Main Responsibilities
- Generates 32-byte IDs from `/dev/urandom`, mapping bytes into LVM’s printable character alphabet while avoiding the final two characters for LVM1 compatibility.
- Creates LVIDs by combining a VG ID with a newly generated LV ID.
- Validates IDs by checking each character against the allowed alphabet.
- Formats IDs into the standard dashed 6-4-4-4-4-4-6 grouping.
- Parses formatted IDs by stripping dashes, enforcing exact length, and validating characters.

## Important Behavior
IDs beginning with `#` are copied as-is in `id_write_format()`, which preserves a special legacy/internal representation path.

## Risks And Invariants
The ID validity check has no checksum, so corruption that preserves allowed characters is not detected. Formatting assumes `ID_LEN == 32` and requires at least 39 bytes including the terminator.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/id/id.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/id/id.h -->
# File Research: sources/block-storage/lvm2/lib/id/id.h

## Summary
Declares LVM ID and logical-volume ID structures and helper APIs.

## Main Contents
Defines `ID_LEN` as 32, `struct id` as a 32-byte UUID-like printable identifier, and `union lvid` as two IDs plus string padding for historical format compatibility.

## API Surface
Declares LVID creation, ID creation, validation, equality, formatted write/read, quiet parse try, and pool-backed format-and-copy.

## Risks And Invariants
`union lvid` layout preserves older format expectations. Consumers should use helper functions rather than assuming C-string semantics for raw `struct id`.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/id/id.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/integrity/integrity.c -->
# File Research: sources/block-storage/lvm2/lib/integrity/integrity.c

## Summary
Implements the LVM segment type for device-mapper `integrity` targets, including text metadata import/export, target-line construction, module reporting, and segtype registration.

## Main Responsibilities
- Imports integrity segment metadata: origin LV, optional metadata LV, data sectors, mode, tag/block sizes, internal hash, recalculation flag, and optional journal/bitmap/discard settings.
- Exports the same fields back to text metadata.
- Marks the owning LV as `INTEGRITY` and optional metadata LV as `INTEGRITY_METADATA`.
- Checks for the dm-integrity target and enforces minimum target version 1.6.0.
- Adds the `dm-integrity` module requirement and builds dm-tree integrity target lines.

## State And Dependencies
The segment stores settings in `seg->integrity_settings`, uses segment area 0 for the origin LV, optionally references `seg->integrity_meta_dev`, and integrates with segtype handler callbacks, activation, dm-tree, and LV dependency tracking.

## Risks And Invariants
The import path requires several fields to be present and type-correct. Optional settings have separate “set” flags, but export uses direct value checks for some fields, so zero-valued optional settings may need care. Activation requires a sufficiently new kernel target.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/integrity/integrity.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/label/hints.c -->
# File Research: sources/block-storage/lvm2/lib/label/hints.c

## Summary
Implements LVM’s runtime hint-file cache under `/run/lvm`, used to reduce device scanning by remembering which devices previously contained LVM labels.

## Main Responsibilities
- Manages `hints`, `newhints`, and `nohints` files and their locking protocol.
- Reads and validates hint files against version, global filter, filter, `scan_lvs`, devices-file setting, and a CRC/hash of scan-relevant device names.
- Applies hints by moving matching devices from the full scan list to the reduced scan list, optionally narrowed by a single VG command argument.
- Validates used hints after scanning against observed PVIDs, VG names, duplicate PVs, duplicate VG names, and unread devices.
- Writes fresh hint files after full scans, including device path, PVID, device major/minor, VG name, filters, devices-file, and device-set hash.
- Clears or invalidates hints for commands that change global PV/VG state or for `pvscan --cache`.

## Important Behavior
`get_hints()` returns either “use these hints” or “scan everything and maybe write new hints later.” Stale hints are detected before use by config/device-set checks and after use by comparing scan results to hint entries. `clear_hint_file()` touches `nohints`, takes an exclusive lock, empties the hint file, touches `newhints`, and keeps the lock until later write/unlock paths.

## State And Dependencies
Uses global `_hints_fd`, static path constants, `struct hint` lists, device iterators, lvmcache, command filter callbacks, devices-file lookups, CRC helpers, and flock-based synchronization.

## Risks And Invariants
The device-set hash depends on stable device iteration order. Hints intentionally err toward refresh rather than missing a device. Locking is split between shared readers, exclusive clear/recreate paths, and sentinel files, so callers must pair `get_hints()` new-hints outcomes with `write_hint_file()` to release the exclusive lock.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/label/hints.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/label/hints.h -->
# File Research: sources/block-storage/lvm2/lib/label/hints.h

## Summary
Declares the hint-file data structure and public hint cache APIs.

## Main Contents
`struct hint` stores list linkage, device number, path name, VG name, PVID, and a `chosen` bit indicating that the hint’s device was selected for scanning.

## API Surface
Declares hint list freeing, hint writing, clearing, invalidation, loading/applying, validation, shutdown cleanup, `pvscan --cache` recreation setup, and single-VG command-argument extraction.

## Risks And Invariants
Fixed-size aligned string buffers use `PATH_MAX`, `NAME_LEN`, and `ID_LEN + 1`; producers must keep parsed names bounded and null-terminated.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/label/hints.h -->