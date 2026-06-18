# File Research: sources/cow-pools/bcachefs-tools/fs/data/reconcile/trigger.h

## Purpose
Public reconcile trigger API, position mapping helpers, IO-option cache types, and helpers for converting IO opts to reconcile entries.

## Main Interfaces and Behavior
- `data_to_rb_work_pos()` maps stripes, reflink, and extents into a shared reconcile work position space. Stripes use inode 0, reflink positions are shifted, and extents start at `BCACHEFS_ROOT_INO`.
- `rb_work_to_data_pos()` reverses that mapping into `struct bbpos`.
- `rb_work_id()` maps a reconcile entry to none/pending/hipri/normal, and `rb_work_id_phys()` suppresses pending for physical work.
- `io_opts_to_reconcile_opts()` copies six IO options and their from-inode flags into a `bch_extent_reconcile` entry with the correct type bit.
- Declares reconcile validation, backpointer get/set/add/delete/resolve helpers, text renderers, reconcile option extraction, work ID calculation, trigger implementation, IO option lookup, reconcile mutation, and extent-trigger lazy mutation.
- `rb_needs_trigger()` quickly checks whether a reconcile entry has work or moving pointers.
- Inline `bch2_trigger_extent_reconcile()` extracts old/new reconcile entries and calls the heavy trigger only when necessary.
- Defines `enum set_needs_reconcile_ctx` for option change, indirect option change, foreground write, and other contexts.
- `struct per_snapshot_io_opts` caches effective IO options across ordered scans, including filesystem options, per-inode snapshot entries, scan-cookie cache bits, and device-cookie cache.

## Risks and Invariants
- The position mapping is shared by checkers, triggers, and work processors; changing it would require migrating reconcile work btrees.
- `per_snapshot_io_opts` caches positive scan-cookie/device-cookie state but deliberately avoids trusting cached non-existence in some paths.
