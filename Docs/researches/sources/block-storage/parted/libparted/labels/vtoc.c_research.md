# File Research: sources/block-storage/parted/libparted/labels/vtoc.c

## Purpose

`vtoc.c` implements lower-level IBM/S390 DASD VTOC helper routines used by libparted’s DASD support. It handles EBCDIC/ASCII conversion, volume labels, CCHH/CCHHB address encoding, DSCB format label initialization, label IO, and VTOC free-space extent updates.

## Main Responsibilities

- Provides ASCII-to-EBCDIC and EBCDIC-to-ASCII translation tables.
- Encodes and decodes DASD CCHH and CCHHB cylinder/head/block addresses, including large-volume cylinder bits.
- Converts CCHH/CCHHB addresses to block or track numbers.
- Reads and writes DASD volume labels.
- Handles a CMS/FBA special case where the label is at offset 512 within block zero.
- Gets and sets VOLSER and volume label identifiers.
- Reads and writes VTOC DSCB labels:
  - FMT1,
  - FMT4,
  - FMT5,
  - FMT7,
  - FMT9.
- Initializes FMT1, FMT4, FMT5, FMT7, FMT8, and FMT9 records.
- Updates FMT4 highest-used DSCB and unused-record counters.
- Maintains FMT5 free-space extents for smaller disks.
- Maintains FMT7 free-space extents for large disks.
- Chooses FMT5 or FMT7 free-space representation in `vtoc_set_freespace()`.

## Important Functions

- `vtoc_ebcdic_enc()` and `vtoc_ebcdic_dec()` translate fixed-size byte strings.
- `vtoc_set_cchh()`, `vtoc_get_cyl_from_cchh()`, and `vtoc_get_head_from_cchh()` manage CCHH addresses.
- `vtoc_set_cchhb()`, `vtoc_get_cyl_from_cchhb()`, and `vtoc_get_head_from_cchhb()` manage CCHHB addresses.
- `cchhb2blk()`, `cchh2blk()`, and `cchh2trk()` convert DASD addresses through geometry.
- `vtoc_volume_label_init()` fills a volume label with EBCDIC spaces.
- `vtoc_read_volume_label()` validates `VOL1`, `LNX1`, or `CMS1` labels.
- `vtoc_volume_label_set_volser()` uppercases, truncates, pads, and EBCDIC-encodes a VOLSER.
- `vtoc_read_label()` and `vtoc_write_label()` perform positional DSCB IO.
- `vtoc_init_format4_label()` initializes the VTOC anchor/format-4 DSCB with device geometry and FMT8/FMT9 support.
- `vtoc_init_format_1_8_label()` initializes common FMT1/FMT8 partition dataset fields.
- `vtoc_update_format5_label_add()` and `vtoc_update_format5_label_del()` merge/split FMT5 free extents.
- `vtoc_update_format7_label_add()` and `vtoc_update_format7_label_del()` merge/split FMT7 free extents.
- `vtoc_set_freespace()` dispatches free-space updates to FMT5 or FMT7 based on `BIG_DISK_SIZE`.

## Behavior Details

FMT5 extents represent free space using track/cylinder counts and track remainders. FMT7 extents represent large-disk free space using relative track addresses. Both add paths merge adjacent extents and both delete paths handle exact, left-bounded, right-bounded, and split removal cases.

When a disk is large enough to require FMT7, `vtoc_set_freespace()` marks FMT4 extended free-space state with `DS4VTOCI = 0xa0`, `DS4EFLVL = 0x07`, and sets `DS4EFPTR` to the FMT7 location.

## Dependencies and Interactions

- Includes `<parted/vtoc.h>`, `<parted/parted.h>`, and DASD geometry types such as `struct fdasd_hd_geometry`.
- Used by DASD/fdasd label code and by S390 volser/VTOC tests in this group.

## Notable Edge Cases

- Many internal consistency failures print `BUG:` and call `exit(EXIT_FAILURE)` rather than returning an error.
- `vtoc_error()` builds an 8192-byte stack buffer with `sprintf`.
- Several routines operate on fixed-width fields and intentionally do not NUL-terminate the on-disk data.
- `vtoc_read_volume_label()` returns success after copying the CMS/FBA fallback label without revalidating it.
