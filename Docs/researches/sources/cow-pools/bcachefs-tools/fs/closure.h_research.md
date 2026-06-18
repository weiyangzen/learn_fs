# File Research: sources/cow-pools/bcachefs-tools/fs/closure.h

Read completeness: full file read, 6 lines.

Purpose: bcachefs-local compatibility wrapper around `vendor/closure.h`.

Definitions:
- Includes `vendor/closure.h`.
- Renames generic closure helper symbols to bcachefs-prefixed symbols through macros: `closure_wait`, `closure_return_sync`, `__closure_wake_up`, and `closure_sync_unbounded`.

Dependencies and integration:
- Used by bcachefs code that wants closure APIs without exporting or colliding with generic names.
- In this group, closure synchronization appears in node scan, write buffer shard flushing, and btree cache/write wait paths.

Risks and validation notes:
- This file is intentionally tiny but globally visible; macro renames can affect any later include order that expects the unprefixed names.
