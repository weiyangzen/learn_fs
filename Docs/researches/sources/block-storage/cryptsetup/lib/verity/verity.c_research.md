# File Research: sources/block-storage/cryptsetup/lib/verity/verity.c

## Purpose
Implements dm-verity superblock read/write, parameter verification, activation, UUID generation, hash offset calculation, and metadata dump.

## Key Responsibilities
- Reads and validates the on-disk verity superblock.
- Writes normalized verity superblocks with lower-case hash algorithm names.
- Calculates hash-area offset in hash blocks.
- Generates verity UUIDs.
- Verifies verity data in userspace when requested and optionally attempts FEC repair.
- Activates dm-verity mappings through device-mapper.
- Loads root-hash signatures into the thread keyring for kernel activation.
- Dumps verity metadata and derived hash/FEC sizing.

## Important Details
- Superblock format follows the dm-verity documented `verity\0\0` signature structure.
- Headerless verity mode rejects superblock read/write.
- Read path updates loop block sizes for metadata and data devices based on header block sizes.
- Activation checks data/hash/fec device access and maps kernel unsupported cases to `-ENOTSUP`.
- Signature keys are unlinked from the thread keyring after activation attempt.

## Dependencies
Uses UUID library, dm target APIs, keyring APIs, device helpers, FEC/hash helpers, volume keys, and `internal.h`.
