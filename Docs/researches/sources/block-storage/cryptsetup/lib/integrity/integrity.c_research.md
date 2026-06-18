# File Research: sources/block-storage/cryptsetup/lib/integrity/integrity.c

Implements dm-integrity metadata handling, activation, tag/key sizing, and formatting helper flows.

Key points:
- LUKS2 integrity metadata is read from the data device even for detached headers; other types use metadata device.
- `INTEGRITY_read_superblock()` reads dm-integrity superblock, checks magic/version, converts endian fields, and validates sector-size shift.
- `INTEGRITY_read_sb()`, `INTEGRITY_dump()`, and `INTEGRITY_data_sectors()` expose parsed superblock fields.
- `INTEGRITY_key_size()` maps supported integrity algorithms to required key sizes, with required-size validation.
- `INTEGRITY_hash_tag_size()` infers tag size from CRC/xxhash constants or crypt backend hash size for hash/HMAC/phmac names.
- `INTEGRITY_tag_size()` combines random-IV tag overhead and authentication tag overhead for AEAD/HMAC/PHMAC/Poly1305/CMAC cases.
- `INTEGRITY_create_dmd_device()` constructs a `crypt_dm_active_device` with flags adjusted from superblock flags and calls `dm_integrity_target_set()`.
- `INTEGRITY_activate_dmd_device()` validates target shape, creates/reloads the device, and reports unsupported kernel features such as dm-integrity, fixed padding, secure recalc, or inline mode.
- `INTEGRITY_activate()` supports refresh mode by querying existing keys/params and reusing them when new ones are omitted.
- `_create_reduced_device()` builds a temporary dm-linear reduced mapping for formatting a bounded backing size.
- `INTEGRITY_format()` creates a temporary private dm-integrity device to format metadata, handles inline mode, optional reduced device, exclusive device checks, and reloads superblock flags afterward.

Storage relevance:
- Bridges cryptsetup format/activation flows to the kernel dm-integrity target.
- Critical for authenticated encryption, standalone integrity devices, LUKS2 integrity segments, and inline integrity support.
