# File Research: sources/block-storage/cryptsetup/lib/luks2/luks2_internal.h

Declares private LUKS2 internals shared across implementation files.

Main areas:
- Disk metadata read/write and write-lock helpers.
- JSON object accessors for keyslots, tokens, digests, segments, and top-level segment collections.
- JSON scalar helpers, object-copy/add/delete helpers, compact on-disk JSON serialization, and debug dumping.
- JSON validation/repair entry points for headers, tokens, and keyslots.
- JSON array lookup/removal helpers.

Plugin-style handler interfaces:
- `keyslot_handler` declares alloc/update/open/store/wipe/dump/validate/repair operations for keyslot implementations.
- `digest_handler` declares verify/store/dump operations for digest implementations.
- Token handler internals wrap public/deprecated token handler versions while preserving prefix layout compatibility.

Reencryption support:
- Defines `struct reenc_protection`, supporting checksum, journal, and datashift protection variants.
- Declares reencryption keyslot allocate/update/load/store/digest helpers and reencryption segment/digest lookup functions.

Segment/keyslot/digest internals:
- Declares JSON segment getters for offsets, sizes, ciphers, sector sizes, OPAL IDs/key sizes, backup flags, and reencryption flags.
- Declares JSON segment creation for linear, crypt, OPAL, and OPAL+crypt segments.
- Declares area gap search, keyslot dump, segment assembly into dm targets, segment flags, default segment lookup, volume-key size lookup, and digest verification helpers.

Role:
- This is the private coordination header for LUKS2 modular implementation files; it exposes internal contracts but not the on-disk ABI itself, which lives in `luks2.h`.
