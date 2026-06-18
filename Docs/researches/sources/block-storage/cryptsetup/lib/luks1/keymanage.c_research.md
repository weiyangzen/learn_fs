# File Research: sources/block-storage/cryptsetup/lib/luks1/keymanage.c

Implements LUKS1 header/keyslot lifecycle: header generation, read/write, backup/restore, repair, keyslot creation/open/delete, activation, wiping, and PBKDF reporting.

Core behavior:
- Calculates keyslot offsets and lengths from `luks_phdr.keyblock[]`, `AF_split_sectors()`, `SECTOR_SIZE`, and fixed `LUKS_STRIPES`.
- Validates device/header geometry: key material must fit after the binary header, before payload for attached headers, without overlapping other keyslots.
- Reads on-disk big-endian LUKS1 headers and converts integer fields to CPU endian; writes by converting back to network byte order.
- Generates new headers with magic/version/cipher/hash/UUID, keyslot layout, random master-key digest salt, and PBKDF2 digest over the volume key.
- Backs up/restores the header plus keyslot area, with restore checks for payload offset/key size compatibility and user confirmation.
- Repairs known legacy/broken header cases: uppercase hash names, `ecb-*` mode strings, damaged inactive keyslot offsets/stripes/salts, and partition-signature damage in keyslot metadata.

Keyslot operations:
- `LUKS_set_key()` derives a wrapping key from passphrase via PBKDF2, AF-splits the volume key, encrypts AF material to the keyslot area, marks the slot enabled, and writes the header.
- `LUKS_open_key_with_hdr()` tries a requested slot or all slots, decrypts AF material, merges it back to a volume key, verifies the master-key digest, and returns the opened slot index.
- `LUKS_del_key()` disables a slot, wipes key material with `CRYPT_WIPE_SPECIAL`, clears salt/iterations, and writes the updated header.
- Slot state is reported as inactive, active, active-last, or invalid from `active` magic values.

Important invariants:
- LUKS1 supports exactly 8 keyslots and assumes `LUKS_STRIPES == 4000`.
- Digest and keyslot PBKDF are PBKDF2-based.
- On-disk integer fields are big-endian.
- Keyslot area starts at or after `LUKS_ALIGN_KEYSLOTS` except legacy unaligned headers, where direct I/O is disabled.
- Null cipher activation only accepts an empty passphrase.

External dependencies:
- Uses cryptsetup internals for device I/O, locking-adjacent device helpers, PBKDF, random, AF split/merge, dm-crypt target assembly, secure allocation/free, wiping, logging, and confirmation prompts.
- Uses `uuid_parse`, `uuid_generate`, `uuid_unparse`.

Failure/security notes:
- Many validation failures map to `-EINVAL`; wrong passphrases map to `-EPERM`; inactive slots to `-ENOENT`.
- Header restore and wipe paths can destroy access to data, so restore requires confirmation and wipe carefully bounds header/keyslot areas.
- Sensitive buffers are allocated with safe allocators and zeroed/freed on exit paths.
