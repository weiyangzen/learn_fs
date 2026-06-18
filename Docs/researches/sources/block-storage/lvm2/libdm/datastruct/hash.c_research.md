# File Research: sources/block-storage/lvm2/libdm/datastruct/hash.c

## Purpose
Implements libdm’s general-purpose hash table with binary-key and string-key APIs, optional duplicate-key entries, iteration, wipe, and lookup-by-key/value helpers.

## Main Responsibilities
- Allocate a power-of-two slot array sized from a hint.
- Hash keys using an adapted Jenkins-style hash.
- Store keys inline in `dm_hash_node`.
- Resolve collisions with singly linked chains.
- Support replacement insert for unique keys and prepend insert for duplicate-key mode.

## Key Functions
- `dm_hash_create()` rounds the size hint up to a power of two, allocates table metadata and slots.
- `_hash()` hashes input bytes two at a time where supported.
- `_findh()` searches a chain by hash, key length, and key bytes while updating debug counters.
- `dm_hash_lookup_binary()`, `dm_hash_insert_binary()`, and `dm_hash_remove_binary()` provide raw binary-key operations.
- `dm_hash_lookup()`, `dm_hash_insert()`, and `dm_hash_remove()` wrap string keys including the terminating NUL.
- `dm_hash_insert_allow_multiple()` allows repeated keys with potentially distinct values.
- `dm_hash_lookup_with_val()` and `dm_hash_remove_with_val()` find duplicate-key entries by matching value bytes.
- `dm_hash_lookup_with_count()` returns the first matching value and counts all entries with the same key.
- `dm_hash_iter()`, `dm_hash_get_first()`, and `dm_hash_get_next()` provide table iteration.
- `dm_hash_wipe()` frees nodes and resets slots/counters without destroying the table itself.

## Edge Cases and Invariants
- Normal insert replaces data for an existing key; duplicate insert never searches first.
- Duplicate-key value matching requires stored `data_len` and non-null data.
- Table size is fixed after creation; there is no resize path.
- `dm_hash_destroy()` frees nodes, slots, and table but not user data.
