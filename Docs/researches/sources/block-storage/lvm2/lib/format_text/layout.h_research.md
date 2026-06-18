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
