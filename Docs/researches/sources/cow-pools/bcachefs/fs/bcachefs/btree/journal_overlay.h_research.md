# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/journal_overlay.h

## Role

This header declares the journal overlay iterator API and provides inline helpers for journal key addressing and comparison.

## Major Contents

- `struct journal_iter`: a list-linked iterator over `journal_keys` for one btree ID and level.
- `struct btree_and_journal_iter`: a combined iterator over one btree node iterator plus journal overlay entries.
- `journal_entry_radix_idx()`: maps a journal sequence to the genradix index.
- `journal_key_k()`: resolves a `journal_key` either to an allocated key or to a key embedded in a replay journal entry.
- `__journal_key_btree_cmp()`, `__journal_key_cmp()`, and `journal_key_cmp()`: shared ordering helpers.

## Exported Operations

The header exports forward, reverse, and slot journal peek helpers; key insertion/deletion helpers; overwrite checking; combined btree+journal iterator advance/peek/init/exit helpers; journal key ref release; journal key sorting; range shoot-down; dumping; and filesystem journal key initialization.

It also includes `bch2_journal_keys_put_initial()`, which drops the initial replay-key reference once replay consumers no longer need it.
