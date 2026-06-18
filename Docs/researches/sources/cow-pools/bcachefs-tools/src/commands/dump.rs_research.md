# File Research: sources/cow-pools/bcachefs-tools/src/commands/dump.rs

This file implements metadata dump and undump commands using qcow2 images.

Commands:
- `dump`: dumps filesystem metadata to one or more `.qcow2` images.
- `undump`: converts qcow2 dump files back to raw device images.

Dump behavior:
- Opens the filesystem read-only with no changes, no recovery, degraded-very, continue-on-error, and no fsck fixes.
- Collects ranges for:
  - superblock layout and all superblock copies
  - journal buckets
  - btree node locations
- Walks every alive btree id and every level using btree iterators, capturing nodes reachable through journal overlay.
- Writes one qcow2 image for a single online device, or indexed images for multiple devices.

Sanitization:
- `--sanitize` defaults to inline data sanitization.
- `--sanitize=filenames` also overwrites dirent names with `X`.
- Sanitizes journal key payloads and btree node key payloads.
- Handles encrypted journal/btree blocks by calling C decrypt bridge functions before sanitization.
- Clears checksums and checksum-type flags after modifying sanitized structures.

Undump behavior:
- Requires `.qcow2` input suffix.
- Refuses to overwrite outputs unless `--force` is used.
- Converts qcow2 contents back to raw images.

Dependencies:
- `crate::qcow2`
- btree/accounting/data bindings
- superblock wrapper helpers
- C decrypt bridge functions `rust_jset_decrypt()` and `rust_bset_decrypt()`
