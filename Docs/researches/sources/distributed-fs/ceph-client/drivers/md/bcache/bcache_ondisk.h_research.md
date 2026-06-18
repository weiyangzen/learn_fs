# sources/distributed-fs/ceph-client/drivers/md/bcache/bcache_ondisk.h

## Purpose
`bcache_ondisk.h` defines bcache's on-disk metadata format and key encoding. It is shared with userspace-visible layout expectations via the Linux syscall-note license.

## Important APIs, Types, and Functions
Key structures are `bkey`, `cache_sb_disk`, in-memory `cache_sb`, `jset`, `prio_set`, `bucket_disk`, `uuid_entry`, `bset`, and obsolete `uuid_entry_v0`. It defines bitfield helpers for key fields, pointer fields, superblock flags, cache modes, backing-device states, replacement policies, magic-number helpers `jset_magic()`, `pset_magic()`, `bset_magic()`, and bkey utility helpers such as `bkey_u64s()`, `bkey_bytes()`, `bkey_next()`, and `bkey_idx()`.

## Control Flow, State, and Persistence
There is no active control flow. The file encodes persistent metadata: sector-addressed btree keys with variable pointer counts, cache/backing superblocks at `SB_SECTOR`, journal entries containing replay keys and btree roots, priority/generation buckets for allocation safety, UUID table entries for backing devices and flash-only volumes, and bsets that form log-structured btree nodes. The in-memory `cache_sb` intentionally differs from `cache_sb_disk`, so conversion code elsewhere must be explicit.

## Dependencies and Integration Points
The header depends on Linux integer types and sector constants and is included by core bcache headers, superblock handling, journal, allocator, and btree code. Its constants define compatibility boundaries for formatted bcache devices.

## Risks and Test Signals
Risks include incompatible bitfield changes, endian conversion mistakes, checksum/magic mismatch, superblock version handling, generation wrap semantics, and copying variable-length bkeys without padding. Tests should include format compatibility, superblock read/write round trips, journal replay, priority set checksum validation, UUID table migration, and fuzzing malformed bkeys/bsets.
