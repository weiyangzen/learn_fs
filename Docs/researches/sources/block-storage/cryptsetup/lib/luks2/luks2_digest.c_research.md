# File Research: sources/block-storage/cryptsetup/lib/luks2/luks2_digest.c

Implements generic LUKS2 digest management over JSON metadata. Digest-specific algorithms are dispatched through `digest_handler`; currently the handler table contains PBKDF2.

Core behavior:
- Locates digest handlers by JSON `"type"`.
- Finds free digest IDs under `LUKS2_DIGEST_MAX`.
- Creates digest JSON entries through handler `store()`.
- Finds digest IDs associated with keyslots or segments by scanning digest `"keyslots"` and `"segments"` arrays.
- Verifies a volume key by digest, keyslot, segment, or any matching digest.
- Optionally checks expected key size from digest/segment/keyslot metadata after cryptographic verification.

Assignment behavior:
- `LUKS2_digest_assign()` adds/removes keyslot IDs from one digest or all digests.
- `LUKS2_digest_segment_assign()` adds/removes segment IDs from one digest or all digests, with support for default segment and all segments.
- Empty digests with no segments and no keyslots can be erased by `LUKS2_digests_erase_unused()`.

Keyring helpers:
- Builds key descriptions in the form `cryptsetup:<uuid>-d<digest>`.
- Can attach segment-derived descriptions to volume keys and load digest-described keys into the kernel keyring.

Important invariants:
- Digest JSON objects must expose `"type"`, `"keyslots"`, and `"segments"` fields for generic assignment/removal.
- Segment and keyslot IDs are stored as decimal strings in arrays.
- Verification returns the digest ID on success or negative errno-style values on failure.

Role:
- Connects LUKS2 JSON references between volume-key digests, keyslots, and segments, while leaving algorithm-specific digest storage/verification to handlers.
