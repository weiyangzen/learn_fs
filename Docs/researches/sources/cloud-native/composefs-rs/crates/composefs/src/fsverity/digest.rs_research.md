# sources/cloud-native/composefs-rs/crates/composefs/src/fsverity/digest.rs

## Purpose
This module implements userspace fs-verity digest computation. It builds the Merkle tree root hash and then hashes the fs-verity descriptor fields so callers can compute the same digest the kernel reports, even when kernel fs-verity is unavailable.

## Important APIs, Types, and Functions
`FsVerityLayer<H, LG_BLKSZ>` wraps a hash context for one Merkle tree layer and tracks remaining bytes in the current block. `FsVerityHasher<H, LG_BLKSZ>` is the public incremental hasher with `BLOCK_SIZE`, `hash()`, `new()`, `add_block()`, and `digest()`. It is generic over `FsVerityHashValue`, so SHA-256 and SHA-512 share the same logic.

## Control Flow
`hash()` slices an input buffer into block-sized chunks and feeds `add_block()`. `add_block()` hashes a data block padded to the fs-verity block size, increments `n_bytes`, and propagates completed child hashes upward through `layers`. If a prior root value exists and more data arrives, that value is converted into a new upper layer before processing continues. `root_hash()` finalizes pending layers, using the all-zero `EMPTY` value for the empty-file case. `digest()` serializes the fs-verity descriptor fields manually in little-endian order, appends the Merkle root, pads the root hash field to 64 bytes, adds zero salt and reserved bytes, and returns the final hash.

## State and Persistence Behavior
All state is in memory: `layers`, cached `value`, and `n_bytes`. Calling `digest()` mutates the hasher by finalizing/caching the root. No file descriptors or persistent stores are touched. Correctness depends on callers feeding full blocks except for the final chunk.

## Dependencies and Integration Points
The module depends on `sha2::Digest` and the local `FsVerityHashValue` trait. It is used by `fsverity::compute_verity()`, fallback measurement paths, filesystem scanning without a store, and flat digest store insecure fallback. It mirrors kernel descriptor construction rather than relying on a packed struct.

## Risks and Edge Cases
`add_block()` trusts caller chunking and does not reject oversized or mid-stream short blocks, so misuse can produce non-kernel-equivalent digests. The descriptor serialization must stay aligned with Linux fs-verity rules; future support for salt or non-4096 block sizes would require careful changes. `root_hash()` mutates internal state, so repeated `digest()` calls are intended to be stable but should remain tested.

## Test Signals
Tests assert known SHA-256 and SHA-512 fs-verity digests for `hello world`. Cross-checks against the kernel for many sizes live in `fsverity/mod.rs`, giving stronger end-to-end confidence over Merkle boundary cases.
