# File Research: sources/cow-pools/openzfs/module/zfs/zap_leaf.c

## Purpose
Implements fatzap leaf blocks: byteswapping, initialization, chunk allocation/free, name/value array storage, hash-chain lookup, entry create/read/update/remove, normalization conflict detection, leaf split transfer, and leaf statistics.

## Main Responsibilities
- Defines the internal leaf chunk model: entry chunks, array chunks, free chunks, and hash chains.
- Converts leaf physical blocks between byte orders.
- Initializes a leaf header, hash table, and freelist.
- Stores variable-length names and values in chains of array chunks.
- Searches exact or closest entries by hash and collision differentiator.
- Reads entry names/values with integer-size conversion.
- Creates, updates, and removes entries while maintaining chunk/free counts and hash chains.
- Transfers entries between leaves during fatzap split.
- Generates per-leaf histograms for ZAP stats.

## Key Data And State
- `CHAIN_END` marks the end of chunk chains.
- `LEAF_HASH()` and `LEAF_HASH_ENTPTR()` derive the per-leaf hash bucket from global hash bits and leaf prefix length.
- Leaf physical state includes header fields `lh_prefix`, `lh_prefix_len`, `lh_nfree`, `lh_nentries`, `lh_freelist`, flags, hash table, and chunk array.
- `zap_entry_handle_t` points at a leaf entry and the hash-chain link that references it, enabling efficient removal/update.

## Important Functions
- `zap_leaf_byteswap()`: byteswaps leaf header, hash table, entry chunks, free chunks, and array metadata.
- `zap_leaf_init()`: clears and initializes a new leaf block and optionally marks collision-differentiator-sorted chains.
- `zap_leaf_chunk_alloc()` / `zap_leaf_chunk_free()`: freelist operations for individual chunks.
- `zap_leaf_array_create()` / `zap_leaf_array_copy()` / `zap_leaf_array_free()` / `zap_leaf_array_read()`: variable-length array chain management for names and values.
- `zap_leaf_array_match()`: compares stored keys against a `zap_name_t`, supporting uint64 keys, normalized matching, and fast exact string matching.
- `zap_leaf_lookup()`: finds an entry by key/hash in the appropriate hash chain.
- `zap_leaf_lookup_closest()`: finds the next entry at or after a `(hash, cd)` cursor position.
- `zap_entry_read()` / `zap_entry_read_name()`: copy value/name data out of an entry.
- `zap_entry_update()`: replace an entry value if enough free chunks exist.
- `zap_entry_remove()`: unlink an entry and free value/name/entry chunks.
- `zap_entry_create()`: allocate chunks, choose the lowest unused collision differentiator, populate an entry, and link it into the hash chain.
- `zap_entry_normalization_conflict()`: detects another same-hash entry with equivalent normalized form.
- `zap_leaf_split()`: updates prefixes, rebuilds hash chains, and moves entries whose next hash bit belongs in the new leaf.
- `zap_leaf_stats()`: fills histograms for pointer fanout, entries per leaf, fullness, chunks per entry, and bucket depth.

## Control Flow Notes
- Names and values are stored as big-endian byte streams inside array chunks; `ldv()` and `stv()` convert supported integer widths.
- Hash chains are sorted by collision differentiator for normalized ZAPs so normalized lookup finds the lowest-cd match.
- Entry creation may return `EAGAIN` when the leaf lacks enough free chunks, signalling `zap_fat.c` to split the leaf.
- `zap_leaf_split()` scans chunks sequentially, moving entries based on the next prefix bit and rehashing remaining entries.

## Error Handling And Invariants
- Integer widths are limited to 1, 2, 4, and 8 bytes; invalid paths panic in low-level conversion helpers.
- `zap_entry_read()` returns `EINVAL` when the stored integer size exceeds caller size and `EOVERFLOW` when the caller buffer is too small.
- `zap_entry_create()` returns `E2BIG` when a single entry cannot fit in any leaf and `EAGAIN` when this leaf needs splitting.
- Assertions validate leaf magic, chunk bounds, chunk types, freelist counts, and sorted-chain assumptions.

## Dependencies
Depends on ZAP physical layout macros from `zap_leaf.h`, key normalization/matching from `zap_impl.c`, fatzap split/growth orchestration from `zap_fat.c`, DMU buffer sizing, ARC headers, and SPA/ZIO definitions.

## Research Notes
This file is the low-level packed storage engine for fatzap entries. Bugs here can corrupt directories and metadata ZAPs, so changes need focused tests for long names, uint64 keys, collision chains, value resizing, split behavior, byteswap, and cursor iteration.
