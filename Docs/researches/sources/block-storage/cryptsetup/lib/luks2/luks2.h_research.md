# File Research: sources/block-storage/cryptsetup/lib/luks2/luks2.h

Defines the LUKS2 on-disk binary header, in-memory header, sizing limits, object limits, and public internal API surface for LUKS2 metadata operations.

Key constants:
- Primary magic is `LUKS\xba\xbe`; secondary magic is `SKUL\xba\xbe`.
- Max object counts are 32 for keyslots, tokens, and segments; digest max is 8.
- Default metadata/header sizing: 16 KiB minimum header, 16 MiB default header area, 128 MiB max keyslots area, 4 MiB max metadata offset.
- Secondary header scan offsets are enumerated up to `LUKS2_HDR_OFFSET_MAX`.
- Defines special segment/digest IDs such as `CRYPT_ANY_SEGMENT`, `CRYPT_DEFAULT_SEGMENT`, and `CRYPT_ANY_DIGEST`.

On-disk structures:
- `struct luks2_hdr_disk` is packed and contains magic, version, header size, sequence ID, label, checksum algorithm, per-header salt, UUID, subsystem, header offset, checksum, padding to 4096 bytes, then JSON area.
- Checksum is calculated with the checksum field zeroed over the binary header plus the full JSON area.
- `struct luks2_hdr` stores in-memory metadata, salts for both copies, JSON object pointers, rollback object, and tracked on-disk JSON end offset.

API coverage:
- Header read/write/rollback/dump/backup/restore/labels/UUID/free and size helpers.
- Keyslot open/store/wipe/priority/swap/area/PBKDF helpers.
- Segment creation/query helpers, including OPAL and OPAL+dm-crypt segments.
- Token assignment, creation, status, keyring helpers, and passphrase/key unlock.
- Digest creation, assignment, lookup, and verification.
- Activation/deactivation, header generation, storage parameter calculation, wipe, conversion between LUKS1/LUKS2, OPAL key splitting, requirements, and reencryption support.

Role:
- Central declaration point for LUKS2 metadata layout and operations shared by JSON formatting, disk metadata I/O, digest/keyslot/token handling, reencryption, activation, and OPAL support.
