# File Research: sources/block-storage/lvm2/tools/pvck.c

## Purpose

`pvck.c` implements `pvck`, a diagnostic and repair utility for LVM PV on-disk structures. It can inspect labels, PV headers, metadata area headers, raw metadata locations, current/all metadata text, and can repair label headers, PV headers, and metadata areas from supplied settings or metadata files.

## Major Modes

- Historical check mode: finds and reports LVM labels and metadata areas for one or more PVs.
- `--dump headers`: prints label, PV header, PV header extension, metadata-area headers, and raw location fields.
- `--dump metadata`: dumps current metadata text referenced by raw location.
- `--dump metadata_all`: scans a metadata area for all discoverable metadata copies.
- `--dump metadata_area`: writes/dumps an entire metadata area.
- `--dump metadata_search`: searches common or user-specified MDA ranges without trusting headers.
- `--dump backup_to_raw`: converts an LVM backup file into raw text metadata form.
- `--repairtype label_header`: rewrites the LVM label header.
- `--repairtype pv_header`: rebuilds label and PV header fields.
- `--repairtype metadata`: writes metadata text and MDA headers.
- `--repair`: combined PV header plus metadata repair.

## Core Data Structures

- `struct settings`: parsed from `--settings`; carries byte offsets/sizes, sequence number, PV UUID, MDA number, device/data sizes, and backup file path.
- `struct metadata_file`: represents input metadata text, its size, CRC, filename, and VG UUID string.

## Read Abstraction

The file supports both real block devices and regular files:

- `get_devicefile()` opens regular files for dump operations.
- `_read_bytes()` dispatches to `dev_read_bytes()` for LVM devices or `lseek/read` for regular files.

Repair operations require an LVM device, not just a regular file.

## Metadata Discovery

- `_dump_label_and_pv_header()` reads the 512-byte label sector, validates label header fields, parses PV header disk locations, metadata area locations, and PV header extension bootloader areas.
- `_dump_mda_header()` validates the MDA header and raw locations, then optionally dumps current text, all text, or the whole area.
- `_dump_all_text()` scans 512-byte boundaries inside an MDA for plausible VG metadata starts, extracts full circular-buffer metadata copies, calculates CRCs, parses text, and warns on parse or termination problems.
- `_dump_search()` can infer likely MDA locations from defaults, device size, header values, or explicit `--settings`.

## Validation Logic

- `_check_label_header()` validates label ID, sector, CRC, offset, and type.
- `_check_pv_header()` validates PV UUID format.
- `_check_mda_header()` validates MDA checksum, magic, version, start, and size.
- `_dump_raw_locn()` validates raw metadata size and notes precommit/non-empty and ignored raw locations.
- `_dump_current_text()` reads wrapped or contiguous metadata text, checks CRC, parses config, extracts VG name and seqno, and optionally prints or writes text.

## Repair: Label Header

`_repair_label_header()`:

- Reads the label sector.
- Rewrites constant label ID/type, sector, offset, and recalculated CRC.
- Warns if no existing LVM label is found.
- Honors test mode and prompts unless `--yes` is supplied.

## Repair: PV Header

`_repair_pv_header()`:

- Determines PV UUID, device size, and data offset from either complete settings or a metadata file.
- If using metadata, `_get_pv_info_from_metadata()` parses VG metadata and selects the PV by existing UUID, user-supplied UUID, or matching device hint.
- Checks that the chosen PVID is not already present on another device with `label_scan_for_pvid()`.
- Determines whether MDA1/MDA2 should be represented, with special caution for MDA2 to avoid writing into data space.
- Rebuilds label header, PV header data-area and metadata-area disk locations, and PV header extension.
- Writes one 512-byte header sector after confirmation/test checks.

## Repair: Metadata

`_repair_metadata()`:

- Requires an input metadata file.
- Requires a valid label and MDA locations in the PV header.
- Writes metadata to selected MDA(s), defaulting to all existing MDAs if no `mda_num` is set.
- `_update_mda()` writes raw metadata text immediately after the MDA header, sets `raw_locn[0]`, clears `raw_locn[1]`, calculates the MDA header checksum, then writes text and header.

## Backup and Raw Metadata Handling

- `_backup_file_to_raw_metadata()` strips backup-file preamble/comment formatting and reconstructs raw metadata text with expected termination.
- `_read_metadata_file()` accepts raw metadata or backup files, converts backup files automatically, appends a null terminator, validates likely VG metadata, and stores CRC.
- `_check_metadata_file()` rejects common invalid inputs such as captured `pvck` stdout or unconverted backup files, warns about unexpected final bytes, and extracts VG UUID.

## Command-Level Flow

`pvck()` creates a `metadata_file`, calls `_pvck_mf()`, and frees metadata text. `_pvck_mf()` handles argument mode selection, locking for repair, device setup/filtering, optional metadata-file loading, bcache setup, dump dispatch, repair dispatch, and historical scan mode.

## Safety Characteristics

- Repair takes the global lock exclusively and clears hints.
- Writes are skipped in test mode.
- Potentially destructive writes require confirmation unless `--yes` is used.
- Output files use exclusive creation (`"wx"`) to avoid overwriting.
- MDA2 repair is intentionally conservative because an incorrect MDA2 location can overlap data.
