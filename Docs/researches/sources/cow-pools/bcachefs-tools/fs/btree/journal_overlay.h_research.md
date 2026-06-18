# File Research: sources/cow-pools/bcachefs-tools/fs/btree/journal_overlay.h

## Purpose
`journal_overlay.h` declares the journal overlay iterator interface and inline comparison/access helpers used by btree iterators during journal replay.

## Main Responsibilities
- Defines `struct journal_iter` and `struct btree_and_journal_iter`.
- Provides `journal_entry_radix_idx()` and `journal_key_k()` to locate replay keys, whether they are separately allocated or embedded in a replayed journal entry.
- Defines journal-key ordering helpers: `__journal_key_btree_cmp()`, `__journal_key_cmp()`, and `journal_key_cmp()`.
- Declares peek, insert, delete, overwrite-check, overlay iteration, sort, shoot-down, dump, init, and put functions.
- Provides `bch2_journal_keys_put_initial()` to release the initial journal key reference once appropriate.

## Important Behaviors
- Ordering compares level in reverse priority before btree ID, then bpos. This must stay aligned with the overlay search/merge logic.
- `btree_and_journal_iter` carries both a btree node iterator and a journal iterator plus merge state (`pos`, `at_end`, prefetch flags).

## Dependencies and Coupling
- Includes btree key definitions and references `struct journal_keys`, `journal_replay`, btree node iterator state, btree transactions, and filesystem journal replay storage.
- Implemented by `journal_overlay.c` and consumed by `iter.c`, `key_cache.c`, and recovery code.

## Research Notes
- This header is small but defines the comparison contract that makes journal overlay binary search and btree merge iteration valid.
