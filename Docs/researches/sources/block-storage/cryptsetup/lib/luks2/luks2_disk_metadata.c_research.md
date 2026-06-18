# File Research: sources/block-storage/cryptsetup/lib/luks2/luks2_disk_metadata.c

Implements low-level LUKS2 binary header and JSON metadata read/write, checksum calculation, sequence handling, validation, and recovery between primary and secondary headers.

Read path:
- Reads the 4096-byte binary header at a given offset, validates magic/version/header size/header offset before reading JSON.
- Reads the full JSON area, checks checksum over binary header with zeroed checksum plus full JSON area, then clears the in-memory checksum field.
- Parses JSON with json-c while tracking the parsed byte offset.
- Validates JSON area starts with `{`, has a trailing NUL after parsed data, and contains only zero bytes in unused space.
- Validates the resulting LUKS2 JSON object and attempts known metadata repair before failing.

Write path:
- Serializes JSON in compact on-disk form.
- Ensures JSON fits inside the configured JSON area with room for trailing NUL.
- Writes binary header without checksum, writes JSON area, calculates checksum, then rewrites binary header with checksum.
- `LUKS2_disk_hdr_write()` checks device size, takes a write lock, increments sequence ID, writes primary then secondary copies, tracks JSON end offset, and unlocks.

Recovery/selection:
- Reads primary at offset 0.
- Reads secondary at `hdr_size` from primary when possible, otherwise scans known secondary offsets.
- If both headers are valid, the lower sequence ID copy is considered obsolete.
- If one copy is valid and the other invalid, optional recovery rewrites the bad copy with regenerated salt after optional blkid signature safety checks.
- Refuses auto-recovery when metadata locking is disabled in normal probe mode.

Concurrency:
- `LUKS2_device_write_lock()` acquires device write lock and checks the on-disk sequence ID matches the in-memory header on the first lock, unless reencryption is in progress.
- Detects concurrent metadata update attempts and aborts.

Other helpers:
- `LUKS2_hdr_version_unlocked()` reads only magic/version from a device or backup file without full metadata locking.
- Foreign-signature detection uses blkid and filters out crypto_LUKS signatures before allowing auto-recovery.

Important invariants:
- LUKS2 has two metadata copies with separate salts and shared sequence semantics.
- Header checksum algorithm comes from the header field and is used over the full JSON area, not just live JSON bytes.
- The secondary header offset must match the header size.
