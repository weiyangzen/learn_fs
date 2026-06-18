# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/update.c

This file implements transaction-facing B-tree mutation helpers.

Key behavior:
- Maintains sorted pending updates by trigger order, cached/noncached status, level, and key position.
- Handles extent insertion by merging with adjacent compatible extents and splitting overwritten extents into front/middle/back fragments.
- Emits snapshot whiteouts when deletes or splits would otherwise expose ancestor snapshot keys incorrectly.
- Routes cached-btree leaf updates through the key cache when required for coherency.
- Records old overwritten keys from either the B-tree path or journal overlay during replay.
- Provides helpers to grow trigger-mutated new keys safely before atomic trigger phase.
- Implements public insert, delete, delete-range, bit-set/clear, and buffered bit update operations.
- Provides transaction log entries for strings and bkeys, with early-journal fallback before the journal is running.

Important invariants:
- Pending updates own path references until reset.
- Extent overwrite handling preserves snapshot visibility and reserves extra disk space for compressed extent splits.
- Cached key updates must ensure the key also exists in the underlying B-tree.
- Write-buffered updates are journaled as `BCH_JSET_ENTRY_write_buffer_keys` unless replay rules require direct insertion.

Dependencies include iterators, journal overlay, locking, keylist/data extent helpers, snapshot logic, and journal transaction commit.
