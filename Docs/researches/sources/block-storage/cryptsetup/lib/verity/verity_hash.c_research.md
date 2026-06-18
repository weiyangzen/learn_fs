# File Research: sources/block-storage/cryptsetup/lib/verity/verity_hash.c

## Purpose
Creates and verifies dm-verity hash trees in userspace.

## Key Responsibilities
- Computes hash tree level counts, offsets, and sizes.
- Hashes data or lower hash levels with version-dependent salt ordering.
- Writes hash blocks with proper digest padding/spare zeroing.
- Verifies existing hash blocks and spare zero regions.
- Computes and verifies the root hash.
- Ensures hash device is large enough, growing regular-file metadata devices when allowed.
- Exposes total hash-block count calculation.

## Important Details
- Version 1 hashes salt before data; version 0 hashes salt after data.
- Digest slots for version 1 are padded to the next power-of-two digest size.
- Creation flushes the hash output file before reading it through a second handle for upper levels, for portability beyond Linux page cache behavior.
- Verification distinguishes data-area failure (`-EPERM`) from root-hash mismatch (`-EFAULT`).
- Warns if data block size exceeds kernel page size during creation.

## Dependencies
Uses crypt hash backend APIs, device helpers, overflow helpers, block sizing, and `verity.h`.
