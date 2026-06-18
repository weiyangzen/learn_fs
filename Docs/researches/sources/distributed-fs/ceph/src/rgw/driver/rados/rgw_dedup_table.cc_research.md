# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_table.cc

## Purpose
`rgw_dedup_table.cc` implements the in-memory open-addressed hash table used by dedup MD5 shards. The table counts objects by dedup key, tracks a representative disk record for duplicate groups, estimates dedupable bytes, and prepares the table for a second pass by removing singletons.

## Important APIs, Types, And Functions
The constructor zeroes caller-provided slab memory and interprets it as an array of packed `table_entry_t`. `find_entry()` uses `key.hash() % entries_count` and linear probing until it finds a matching key or an empty slot.

`add_entry()` inserts or updates a key. On first insert it stores `block_id`, `rec_id`, and shared-manifest status. On duplicates it increments estimated duplicate counters, saturates the count at `uint16_t` max, and replaces the representative value with a shared-manifest record when one appears.

`remove_singletons_and_redistribute_keys()` clears singleton and nondedupable keys, then relocates surviving keys to their ideal hash positions where possible and resets counts for actual dedup counting. `update_entry()`, `set_src_mode()`, `inc_count()`, `get_val()`, and `count_duplicates()` support later passes.

## Control Flow
The first pass builds the table from disk records and counts duplicate candidates. After that, `remove_singletons_and_redistribute_keys()` compacts the table so only dedupable groups remain. Later processing looks up a record's key, finds the representative source block/record, loads source records from slabs, and increments counts as actual dedup proceeds.

## State And Persistence Behavior
The table is in-memory only and backed by raw memory supplied by the caller. Values store disk block ids and record ids that refer to persistent slab records. Dedup estimates use object size rounded to 4 KiB units and `calc_deduped_bytes()` from utilities.

## Dependencies And Integration Points
The table depends on `key_t` and disk record ids from `rgw_dedup_store.h`, dedup stats from utilities, and main pipeline settings for head object size, minimum object size, and split-head mode.

## Risks And Edge Cases
There is no dynamic resize. If the table fills, insert returns `-EOVERFLOW`. Linear probing assumes entries are not removed except during the controlled redistribution pass. Shared-manifest replacement mutates the representative source, so correctness depends on full-dedup rules for already-shared manifests.

## Test Signals
Tests should cover collision probing, table-full overflow, duplicate count saturation, singleton removal, nondedupable filtering, shared-manifest representative replacement, `get_val()` misses, and redistribution preserving lookup success.
