# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_store.h

## Purpose
`rgw_dedup_store.h` declares the on-disk data model for dedup intermediate records. It defines block and slab sizing, compact identifiers, record flags, the packed record layout, and APIs for loading and storing slabs.

## Important APIs, Types, And Functions
Constants define `DISK_BLOCK_SIZE` as 8 KiB, `DISK_BLOCK_COUNT` as 256, and `MAX_REC_IN_BLOCK` as 32. `disk_block_id_t` packs work shard id, slab id, and block offset into 32 bits. `record_flags_t` tracks valid hash, shared manifest, hash calculated, fastlane, split head, and tail ref-tag modes.

`disk_record_t::packed_rec_t` is the fixed prefix of a variable-length record. It includes a 256-bit hash array, shared-manifest fingerprint, MD5 high/low words, object size, part count, string lengths, ref tag and manifest lengths, record version, and flags.

`disk_block_header_t` contains the mutable block offset or closed-block magic, record count, block id, and record offsets. `disk_block_t`, `disk_block_seq_t`, and `disk_block_array_t` declare the write-side hierarchy.

## Control Flow
The header sets the structure for the ingress phase: worker shards append records to MD5-specific sequences, which batch blocks into slabs. The MD5 phase later loads slabs by worker shard and sequence number, iterates block records, and uses block id plus record id to reload source records when duplicates are found.

## State And Persistence Behavior
The file defines persistent binary ABI. `static_assert`s pin BLAKE3 hash size, packed record header size, and table element sizes. Changing fields or sizes affects all written dedup slabs. Slab object names are derived from `disk_block_id_t`; the header exposes `get_slab_name()` as the naming authority.

## Dependencies And Integration Points
It depends on Ceph RADOS and bufferlist types, RGW common types, dedup utility statistics, BLAKE3 constants, and SAL bucket metadata. It is included by the dedup table because table values point back to disk records.

## Risks And Edge Cases
The use of packed structs and manual endian conversion requires strict round-trip tests. `disk_block_id_t` asserts work shard and sequence bounds but stores only 8 bits of work shard and 24 bits of sequence. The record version is currently only version 0, so future migration needs compatibility logic.

## Test Signals
Tests should validate struct sizes, `disk_block_id_t` bit packing, max shard and slab sequence boundaries, flag setting and reading, record length calculation, and compatibility of slab names with reader expectations.
