# File Research: sources/block-storage/cryptsetup/lib/luks2/luks2_reencrypt_digest.c

This file builds and verifies the reencryption metadata digest. Its purpose is to authenticate the reencryption keyslot parameters plus backup segment definitions plus relevant volume keys.

Serialization model:
- Small typed serializer `struct jtype` supports strings, 64-bit numeric strings, 64-bit segment sizes including `"dynamic"`, and JSON ints stored as big-endian 32-bit.
- Segment serialization covers `linear` fields `type/offset/size`.
- Crypt segment serialization covers `type/offset/size/iv_tweak/encryption/sector_size`.
- Backup segment serialization requires `backup-previous` and `backup-final`; `backup-moved-segment` is optional.
- Reencrypt keyslot serialization includes `mode`, `direction`, area `type`, `offset`, `size`, plus resilience-specific fields such as `hash`, `sector_size`, and `shift_size`.

Digest data assembly:
- Starts with a version marker: bytes `0x76` and `0x30 + version`.
- Appends old volume key bytes when an old digest exists.
- Appends new volume key bytes when the new digest exists and differs from old.
- Appends serialized reencryption keyslot metadata.
- Appends serialized backup segments.

Main functions:
- `LUKS2_keyslot_reencrypt_digest_create()` assembles verification data, creates a PBKDF2 digest, clears any old assignment from the reencryption keyslot, and assigns the new digest to that keyslot.
- `LUKS2_reencrypt_digest_verify()` rebuilds the same verification data and verifies it against the reencryption keyslot digest. It logs missing digest and invalid metadata cases.

Important constraints:
- Required volume keys must already be unlocked and accessible by digest id.
- Serialization fails closed on missing fields, wrong JSON types, unknown segment types, overlong strings, or missing backup segments.
- The digest check deliberately does not check key size because the reencryption keyslot stores a bogus `key_size=1`.

Dependencies:
- LUKS2 segment/digest/keyslot helpers from `luks2_internal.h`
- volume key helpers
- JSON-C
- endian conversion helpers
- safe allocation/free helpers

This file is tightly coupled to the metadata schema in `luks2_reencrypt.c`; changes to reencryption segment or keyslot JSON fields must preserve this serialization contract or update digest versioning.
