# File Research: sources/block-storage/cryptsetup/lib/luks2/luks2_luks1_convert.c

Bidirectional LUKS1/LUKS2 conversion implementation. It constructs LUKS2 JSON metadata from a LUKS1 header, moves binary keyslot material between LUKS1 and LUKS2 area layouts, checks compatibility constraints for down-conversion, creates placeholder keyslots for inactive LUKS1 slots, and writes the target header format.

Key responsibilities:
- Converts active LUKS1 keyblocks into LUKS2 `luks2` keyslot JSON with PBKDF2 KDF, base64 salt, LUKS1 AF settings, raw encrypted area, area offset, and area size.
- Builds LUKS2 keyslots, one dynamic crypt segment, one PBKDF2 digest, empty tokens, and config objects from a LUKS1 header.
- Encodes the LUKS1 master-key digest, digest salt, keyslot salts, and iteration counts into LUKS2 JSON.
- Moves keyslot area offsets in JSON when converting LUKS1 to LUKS2, because LUKS2 stores two metadata areas before binary keyslot areas.
- Moves binary keyslot material on disk between LUKS1 offset 4 KiB and LUKS2 offset 32 KiB layouts with page-aligned buffers and blockwise I/O.
- Checks whether the mapped LUKS device is active before destructive conversion.
- Detects LUKSMETA foreign metadata after the LUKS1 area and refuses conversion when present.
- Converts LUKS1 to LUKS2 by checking keyslot offset, cipher compatibility, keyslot cipher compatibility, available space, JSON validity, active-device state, binary keyslot move, and LUKS2 header write.
- Checks whether each LUKS2 keyslot can be represented as LUKS1: type `luks2`, PBKDF2, digest hash match, AF stripes/hash match, matching data/keyslot cipher and key size, and compatible binary area length.
- Converts LUKS2 to LUKS1 only for single-segment, no-token, single-PBKDF2-digest, 512-byte-sector, LUKS1-compatible metadata.
- Rejects down-conversion when keyslots are invalid, unbound, above the LUKS1 slot limit, or not LUKS1 compatible.
- Allocates placeholder LUKS2 keyslots for inactive LUKS1 slots so each LUKS1 keyblock gets a distinct key material offset.
- Reconstructs the LUKS1 binary header fields: keyblock active state, stripes, key material offsets, PBKDF iteration counts/salts, cipher name/mode, hash, key size, digest fields, payload offset, UUID, magic, and version.
- Wipes the old LUKS2 binary header area before writing the new LUKS1 header.

Important behavior:
- LUKS1 to LUKS2 assumes the LUKS1 keyslot material starts at `LUKS_ALIGN_KEYSLOTS / SECTOR_SIZE`; other layouts are refused.
- LUKS1 to LUKS2 requires enough space for the shifted keyslot area. It attempts fallocate when the current max size is too small.
- The generated LUKS2 header is fixed to 16 KiB metadata area, seqid 1, version 2, sha256 header checksum, fresh salts, and the existing LUKS UUID.
- Conversion validates the future LUKS2 metadata before moving binary keyslot material to avoid destructive changes when JSON would later fail.
- LUKS2 to LUKS1 refuses wrapped-key ciphers, multiple segments, tokens, non-512-byte default segment sector size, and non-PBKDF2 digest layouts.
- Inactive LUKS2 slots are temporarily represented by invalid placeholder keyslots only to reserve unique binary areas for the LUKS1 header calculation.
- Down-conversion subtracts the LUKS2 keyslot shift from stored keyslot material offsets to recover LUKS1-relative offsets.
- LUKS2 to LUKS1 moves binary keyslots from 32 KiB back to 4 KiB, zeros the old LUKS2 header prefix, then calls `LUKS_write_phdr()`.

Dependencies:
- Depends on `luks2_internal.h` for LUKS2 JSON/header helpers, validation, size calculations, keyslot area lookup, keyslot placeholder allocation, token count, volume-key size, cipher lookup, and header write/free.
- Depends on LUKS1 structures and helpers from `../luks1/luks.h` and AF sizing from `../luks1/af.h`.
- Uses cryptsetup device size, data offset, cipher checking, hash checking, dm active lookup, metadata-device I/O, wipe, sync, and allocation helpers.
- Uses base64 encoding/decoding for LUKS1 salts and digests stored in LUKS2 JSON.

Notable risks:
- Both conversion directions move live keyslot material on disk; failures during movement or after partial writes can leave the device requiring recovery from backup.
- The code intentionally refuses many valid LUKS2 features because LUKS1 cannot represent them; callers must surface those compatibility failures clearly.
- Placeholder keyslots are deliberately invalid and must not be written as a final LUKS2 header.
- LUKSMETA detection treats a matching magic after the LUKS1 area as a hard blocker because the conversion shift would overwrite or invalidate foreign metadata.
