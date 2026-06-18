# sources/distributed-fs/glusterfs/libglusterfs/src/fd-lk.c

## Purpose
This file maintains a per-file-descriptor lock context that tracks and merges byte-range locks. It records active ranges, coalesces compatible locks, splits or removes ranges on unlock/conflicting updates, and exposes an empty-context check.

## Important APIs, types, and functions
Public APIs include `fd_lk_ctx_create`, `fd_lk_ctx_ref`, `fd_lk_ctx_unref`, `fd_lk_insert_and_merge`, `fd_lk_ctx_empty`, and `fd_lk_overlap`. Internal helpers manage lock nodes: `_fd_lk_delete_lock`, `_fd_lk_destroy_lock`, `_fd_lk_destroy_lock_list`, `fd_lk_ctx_node_new`, `_fd_lk_add_locks`, `_fd_lk_sub_locks`, `_fd_lk_insert_and_merge`, and `_fd_lk_delete_unlck_locks`.

## Control flow
`fd_lk_insert_and_merge()` references `fd->lk_ctx`, creates a node from the requested `gf_flock`, locks the context, recursively merges it into the list, prints debug state, unlocks, and unreferences the context. Overlapping ranges of the same type are combined. Overlapping ranges of different types create a union range, subtract the new lock from the union, delete old nodes, recursively insert resulting fragments, and remove `F_UNLCK` entries.

## State and persistence behavior
State is an in-memory `fd_lk_ctx_t` with an atomic refcount, mutex, and `lk_list` of `fd_lk_ctx_node_t`. Ranges store normalized `fl_start` and inclusive `fl_end`; `l_len == 0` maps to `LLONG_MAX`. There is no disk persistence. Destruction occurs when the context refcount reaches zero.

## Dependencies and integration points
It depends on `glusterfs/fd.h`, `glusterfs/fd-lk.h`, lock owner/type formatting helpers, `gf_flock_copy`, atomics, list macros, and GlusterFS allocation/logging. It is attached to `fd_t` and used by lock handling paths that need local knowledge of fd-associated locks.

## Risks and edge cases
Recursive merge/split logic is subtle and allocation failures can leave the list partly updated or silently drop the requested lock. `_fd_lk_delete_unlck_locks()` initializes `ret = -1` and never sets success, though callers ignore it. `_fd_lk_sub_locks()` copies whole nodes with list pointers and then callers reinitialize list heads; any missed path could corrupt lists. Range math can overflow when computing `flock->l_start + flock->l_len - 1`. Debug printing assumes initialized owner/type fields.

## Test signals
Tests should cover non-overlap insertion, same-type coalescing, unlock exact match, unlock middle split into two retained ranges, left/right edge overlaps, opposing lock type replacement, `l_len == 0` infinite ranges, negative or overflowing range inputs, allocation failure during split, refcount destruction, and `fd_lk_ctx_empty()` under concurrent access.
