# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/read.c

## Role

`read.c` implements bcachefs data reads. It handles extent lookup, reflink indirection, device selection, split reads, bounce buffers, checksum verification, decryption, decompression, stale-pointer detection, retry, self-healing, cache promotion, poison marking, and read diagnostics.

## High-Level Flow

`bch2_read()` walks the extents btree for the requested subvolume/inode range. For each covered fragment it:
1. resolves snapshot and extent slot,
2. follows reflink indirection if present,
3. limits the fragment to the current extent,
4. calls `__bch2_read_extent()`.

`__bch2_read_extent()` handles inline data, holes/reservations, poison checks, read-device selection, encryption-key checks, stale pointer checks in retry mode, bounce/full-read decisions, rbio allocation, bio submission, or EC reconstruction.

Completion runs through `bch2_read_endio()` and `__bch2_read_endio_work()`, which validate checksums, decrypt, decompress, copy bounced data back, and complete or retry.

## Retry and Self-Healing

Failures that should retry include transaction restart, explicit data-read retry, and block-device I/O error. `bch2_rbio_retry()` records the failed replica, clears hard device requirements, disables promotion, forces clone behavior, and retries from another replica or EC reconstruction.

If retry succeeds after checksum/I/O failure, the path can allocate a `promote_op` configured as self-heal. Failed pointers are marked in `data_update_opts.ptrs_io_error` and `ptrs_kill`.

`maybe_poison_extent()` marks an extent with `BCH_EXTENT_FLAG_poisoned` after checksum failure when the filesystem is writable, so future user reads fail unless poison checks are explicitly bypassed.

## Cache Promotion

Promotion is opportunistic and bounded by per-CPU semaphores and write refs. It is skipped when:
- the extent already has the promote target,
- the extent is unwritten,
- the target is congested,
- write refs cannot be acquired,
- rate limits or allocation fail.

Promotion uses the data update path with cached writes and may read whole extents depending on compression, errors, or the `promote_whole_extents` option.

## Encoded Extents

Checksummed, encrypted, or compressed extents often require full physical reads into bounce buffers. The completion path verifies checksum over the encoded extent, decrypts as needed, decompresses into the destination bio, or copies a selected live slice.

`bch2_rbio_narrow_crcs()` can opportunistically rewrite a CRC entry to a narrower checksum after a successful read of an uncompressed extent whose stored CRC covers more data than needed.

## Stale Pointer Handling

Read completion checks device pointer generation. If stale, normal reads enter retry. Retry-mode stale dirty pointers are treated as I/O failures and produce detailed inconsistency diagnostics.

## Diagnostics and Initialization

The file provides:
- congestion text output for latency accounting,
- read bio text formatting,
- async object list tracking for reads and promotions,
- bioset/mempool initialization and teardown for normal reads, split reads, and bounce buffers.

## Invariants

- Non-retry `__bch2_read_extent()` should not return hard errors directly; it schedules completion or retry.
- User-mapped buffers are bounced on suspicious checksum retry paths to avoid userspace scribble false positives.
- Compressed reads must bounce and read full encoded extents.
- Data-update reads may read into buffers larger than the key but reject too-small buffers.
- EC reconstruction is attempted only in retry context.
