# File Research: sources/block-storage/linux-dm/drivers/md/dm-verity-target.c

## Purpose
Implements the `verity` device-mapper target for transparent read-only block integrity verification. It maps reads to a data device, verifies each data block against a Merkle hash tree stored on a hash device, optionally corrects corruption through FEC, optionally validates the root hash signature, and exposes corruption status.

## Main Interfaces
- Target lifecycle and DM hooks: `verity_ctr()`, `verity_dtr()`, `verity_map()`, `verity_status()`, `verity_prepare_ioctl()`, `verity_iterate_devices()`, and `verity_io_hints()`.
- Hash helpers exported to FEC: `verity_hash()`, `verity_hash_for_block()`, and `verity_for_bv_block()`.
- Verification path: `verity_end_io()`, `verity_work()`, `verity_verify_io()`, `verity_verify_level()`, and `verity_handle_err()`.
- Prefetch path: `verity_submit_prefetch()` and `verity_prefetch_io()`.
- Optional argument handling: `verity_parse_opt_args()`, `verity_parse_verity_mode()`, `verity_alloc_zero_digest()`, and `verity_alloc_most_once()`.

## Control Flow
The constructor parses the fixed dm-verity table fields: version, data device, hash device, data and hash block sizes, number of data blocks, hash start, hash algorithm, root digest, and salt. It validates read-only mode, block-size constraints, device sizes, digest size, and hash-tree level count; initializes the crypto ahash transform, hash bufio client, verification workqueue, per-bio data size, optional FEC, optional zero-block digest, optional at-most-once bitset, and optional root-hash signature verification.

`verity_map()` rejects writes, unaligned IO, and out-of-range IO. Valid reads are remapped to the data device, equipped with a `dm_verity_io` per-bio context, hooked with `verity_end_io()`, optionally prefetched, and submitted. Completion either returns an underlying IO error immediately when FEC is unavailable or the system is shutting down, or queues CPU-intensive verification work.

`verity_verify_io()` walks each data block in the bio. It obtains the expected digest through `verity_hash_for_block()`, which verifies hash-tree metadata from the root down unless a cached bufio hash block is already marked verified. It then hashes the data block and compares the digest. Mismatches try FEC recovery first; if recovery fails, `verity_handle_err()` records corruption, emits a uevent with block information, and applies the configured error mode: return EIO, log only, restart, or panic.

## State And Synchronization
`struct dm_verity` stores opened devices, bufio client, crypto transform, digest/salt state, tree geometry, corruption status, workqueue, per-level hash-block starts, optional FEC state, optional validated-block bitset, and optional signature key description. Hash-block verification state is stored in bufio auxiliary data as `struct buffer_aux::hash_verified`; it is intentionally lockless because duplicate verification races are harmless.

Per-bio state is held in `struct dm_verity_io`, followed in memory by variable-sized ahash request storage, real digest, wanted digest, and possibly FEC per-bio state. Verification work runs on an unbound CPU-intensive workqueue named `kverityd`.

## Integration Points
Uses Linux crypto ahash, dm-bufio, DM target registration, kobject uevents, reboot/panic APIs, FEC helpers from `dm-verity-fec.c`, and root-hash signature helpers from `dm-verity-verify-sig.c`. It registers the `verity` target with version `{1, 8, 0}`.

## Notable Behaviors
- Hash salt placement depends on verity version: version 1 salts before data; version 0 salts during finalization.
- Hash-tree metadata buffers are cached as verified and never reset to unverified.
- `ignore_zero_blocks` replaces expected zero blocks with zero-filled output rather than reading/validating data content.
- `check_at_most_once` records successfully validated data blocks in a bitset and skips later checks for those blocks.
- Prefetching skips root-level blocks and clusters level-0 hash reads according to the `prefetch_cluster` module parameter.
- Status info is `V` or `C`; table status reconstructs all configured options, while IMA status emits a semicolon-terminated measurement string.

## Risks And Review Focus
- Per-bio memory layout must stay aligned with `dm_verity_io`, digest helpers, and appended FEC state.
- `check_at_most_once` trades repeated verification for performance and should be evaluated carefully for mutable or unreliable lower layers.
- Error modes can restart or panic the system; option parsing must prevent conflicting modes.
- Hash-tree offset and level arithmetic must prevent overflow and keep the root-to-leaf chain exact.
- FEC and zero-block handling must not bypass the final digest comparison for nonzero corrected data.
