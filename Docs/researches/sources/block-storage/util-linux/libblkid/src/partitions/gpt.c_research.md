# File Research: sources/block-storage/util-linux/libblkid/src/partitions/gpt.c

## Purpose
Parses EFI GPT partition tables and detects standalone protective MBRs.

## Main Components
- Defines GPT header/entry structs and EFI GUID representation.
- `count_crc32()` implements EFI CRC32 calculation with excluded checksum field support.
- `get_lba_buffer()` reads LBA-relative buffers.
- `swap_efi_guid()` converts EFI mixed-endian GUID fields to conventional UUID byte order.
- `last_lba()` computes the final LBA from device size and sector size.
- `is_pmbr_valid()` validates optional protective MBR unless GPT probing is forced.
- `get_gpt_header()` reads primary or backup GPT header, validates signature, header size, header CRC, `MyLBA`, usable range, entry size/count, reads entries, and validates entry-array CRC.
- `probe_gpt_pt()` validates PMBR, tries primary then backup header, records magic/wiper data, sets table UUID/PTUUID, creates a `gpt` table, and adds non-empty entries with UTF-16LE names, partition UUIDs, type UUIDs, and attributes.
- `probe_pmbr_pt()` detects a protective MBR without a valid GPT header.
- `gpt_pt_idinfo` has no fixed magic so it always probes; `pmbr_pt_idinfo` uses the MBR magic.

## Dependencies and Interactions
Uses MBR helpers for PMBR, partition helpers for binary objects and PTUUID values, CRC32 helpers, and UTF-16-to-UTF-8 conversion through `blkid_partition_set_utf8name()`.

## Research Notes
GPT entries are exposed in 512-sector units by multiplying LBAs by the sector-size factor. Unused entries still advance the proposed partition number to preserve GPT index semantics.
