# sources/cloud-native/composefs/libcomposefs/lcfs-fsverity.c

## Purpose
`lcfs-fsverity.c` computes fs-verity-compatible SHA-256 digests in userspace. It supports OpenSSL when available and includes a fallback SHA-256 implementation otherwise.

## Important APIs, Types, And Functions
`FsVerityContext` stores per-level 4096-byte Merkle buffers, positions, max level, file size, and optionally an OpenSSL `EVP_MD_CTX`. Public functions are `lcfs_fsverity_context_new`, `free`, `update`, and `get_digest`. Private helpers include fallback `sha256_sum_*`, `do_sha256`, level update/flush routines, and `struct fsverity_descriptor`.

## Control Flow
Updates append data to level 0. Full 4096-byte blocks are hashed lazily into 32-byte digests passed to the next level. Finalization zero-pads partial blocks, recursively flushes upper levels, hashes the root block into an fs-verity descriptor, and hashes that descriptor to produce the exported digest.

## State And Persistence
State is streaming and in-memory. The output digest is persisted by callers as overlay metacopy xattr data, digest store naming input, or image digest output.

## Dependencies And Integration Points
It depends on endian helpers from `lcfs-internal.h`, `lcfs-fsverity.h`, OpenSSL when `HAVE_OPENSSL`, and composefs constants `FSVERITY_BLOCK_SIZE` and digest length. `lcfs-writer.c` wraps it for fd/data/content digest APIs.

## Risks
The fallback SHA-256 uses 32-bit bit counters, so extremely large streams rely on existing logic and should be tested carefully. `get_digest` mutates/flushed context state; repeated calls are not a general reset. OpenSSL assertions abort on impossible EVP failures.

## Test Signals
`test-units.sh` verifies known `composefs-info measure-file` digests and compares kernel fs-verity measurements when available. Integration and mount digest tests exercise end-to-end digest behavior.
