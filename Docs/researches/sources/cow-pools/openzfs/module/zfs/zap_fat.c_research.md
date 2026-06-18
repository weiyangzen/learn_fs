# File Research: sources/cow-pools/openzfs/module/zfs/zap_fat.c

## Purpose
Implements the top half of fatzap: header and pointer-table management, microzap-to-fatzap upgrade, fatzap leaf lookup/split/growth/shrink coordination, attribute add/update/remove/lookup, cursor iteration, prefetch, and stats.

## Main Responsibilities
- Converts a microzap into a fatzap header, embedded pointer table, and first leaf block.
- Manages embedded and external pointer tables, including incremental growth through `zt_nextblk` and `zt_blks_copied`.
- Maps hash prefixes to leaf block IDs.
- Opens, creates, locks, and releases `zap_leaf_t` dbuf users.
- Splits full leaves and grows pointer tables as needed.
- Shrinks empty sibling leaves and truncates the object tail when possible.
- Implements fatzap CRUD operations by delegating entry storage to `zap_leaf.c`.
- Implements fatzap cursor iteration and stats collection.

## Key Data And State
- Tunables:
  - `zap_iterate_prefetch`: prefetch whole fatzap object when iterating from the beginning.
  - `zap_shrink_enabled`: enable collapsing empty sibling leaf blocks.
- `fzap_default_block_shift`: default 16 KiB fatzap block size.
- Fatzap physical state in `zap_phys_t`: block type, magic, salt, norm flags, flags, pointer table, free block cursor, leaf count, and entry count.
- `zap_table_phys_t`: external pointer table metadata, including current table, in-progress next table, copied block count, and shift.

## Important Functions
- `fzap_upgrade()`: rewrites a microzap header as fatzap, initializes embedded pointer table to leaf block 1, and initializes the first leaf.
- `zap_table_grow()` / `zap_grow_ptrtbl()`: allocate and incrementally copy larger pointer tables, first from embedded to external and then by doubling.
- `zap_table_store()` / `zap_table_load()`: read/write external pointer table entries, mirroring updates into an in-progress next table when growth is active.
- `zap_create_leaf()` / `zap_get_leaf_byblk()` / `zap_open_leaf()` / `zap_put_leaf()`: leaf dbuf lifecycle and locking.
- `zap_deref_leaf()`: validates the fatzap header and resolves a hash to the target leaf.
- `zap_expand_leaf()`: upgrades locks if needed, grows the pointer table if leaf prefix length equals table shift, creates a sibling leaf, splits entries, and updates pointer-table ranges.
- `fzap_lookup()`, `fzap_add_cd()`, `fzap_add()`, `fzap_update()`, `fzap_length()`, `fzap_remove()`: fatzap attribute operations.
- `fzap_cursor_retrieve()`: returns the next entry at or after cursor hash/cd, advances across leaf prefix ranges, and supports whole-object prefetch.
- `fzap_get_stats()`: collects header, pointer-table, and leaf histograms.
- `zap_shrink()`: recursively collapses empty sibling leaves, redirects pointer table entries, frees leaf blocks, and updates prefix lengths/freeblk.

## Control Flow Notes
- Fatzap pointer table entries reference fixed-size leaf blocks; leaves contain variable-length entry/name/value chunk chains.
- Splitting a leaf increases prefix length and moves entries with the next significant hash bit set into the new sibling.
- Pointer-table growth may span multiple transactions; `zt_nextblk` records the destination table while blocks are copied incrementally.
- Removing the last entry from a leaf may trigger recursive shrink only when the sibling exists and is also empty.
- Iteration uses hash/collision-differentiator ordering, not lexical name ordering.

## Error Handling And Invariants
- `fzap_checkname()` enforces name length limits, allowing new longer names only for directory ZAPs.
- `fzap_checksize()` accepts only 1, 2, 4, or 8-byte integers and caps value byte length.
- Corrupt fatzap headers return `EIO` from `zap_deref_leaf()`.
- Pointer-table I/O errors are checked before destructive split/shrink updates.
- `zap_expand_leaf()` handles concurrent split/growth by re-dereferencing after lock upgrade.

## Dependencies
Depends on DMU buffers, dnode prefetch and free-range operations, ZAP physical layout definitions, `zap_leaf.c` entry/chunk operations, ZAP locks from `zap_impl.c`, btree/cursor support, and object byteswap helpers.

## Research Notes
This file owns fatzap structural mutation. High-risk areas are pointer-table growth persistence, concurrent lock upgrades, leaf split/shrink races, cursor correctness across changing leaves, and long-name compatibility.
