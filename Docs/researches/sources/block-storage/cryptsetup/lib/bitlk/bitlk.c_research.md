# File Research: sources/block-storage/cryptsetup/lib/bitlk/bitlk.c

## Purpose
Implements BitLocker-compatible (`BITLK`) metadata parsing, keyslot extraction, passphrase/startup/recovery/clearkey unlock, FVEK decryption, metadata dumping, and dm-crypt/dm-zero activation.

## Key Content
Defines on-disk packed structures for BITLK signatures, superblocks, FVE metadata, validation metadata, VMK entries, BEK startup keys, and KDF state. `BITLK_read_sb()` reads the boot signature, rejects v1 boot code, detects normal vs BitLocker To Go layout, reads all three FVE metadata copies, validates CRC32, hashes the validated FVE block with SHA-256, parses VMKs, FVEK, volume header metadata, GUIDs, creation time, description, and cipher mode. Supported encryption maps include CBC Elephant, CBC EBOIV, and XTS.

Unlock flow is in `BITLK_get_volume_key()`: passphrases use the BitLocker SHA-256 KDF loop, recovery keys are parsed from the eight-part decimal format, startup keys are parsed from BEK metadata, and clear-key VMKs decrypt nested VMK material. VMK validation decrypts the validation datum and compares its SHA-256 hash against the validated FVE metadata before decrypting the FVEK.

Activation builds a multi-segment device-mapper table: metadata areas and relocated volume header become `dm-zero` targets, while data gaps become `dm-crypt` targets with correct IV offsets and optional large-sector IV flag.

## Dependencies and Coupling
Depends on `bitlk.h`, `internal.h`, crypto backend hash/CRC/AES-CCM helpers, UTF conversion, volume-key helpers, device I/O wrappers, and device-mapper target construction. Kernel support for BITLK IVs, Elephant diffuser, dm-zero, and large sectors is checked after activation failure.

## Invariants and Risks
The parser is defensive about entry sizes, metadata bounds, CRC, and double-fetch avoidance by copying entries from the validated buffer. Supported VMK protection types are passphrase, recovery passphrase, startup key, and clear key; TPM and smart-card paths are intentionally skipped. The `sha256_fve` field is treated as a 32-byte buffer even though the header declares it as an array of pointers, which is a type-safety hazard for future maintenance. Segment calculation assumes a maximum of ten dm targets.
