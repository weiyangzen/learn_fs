# File Research: sources/cow-pools/bcachefs-tools/fs/sb/errors_types.h

This header defines in-memory superblock/fsck error count storage.

Key definitions:
- `struct bch_sb_error_entry_cpu`
  - 16-bit `id`
  - 48-bit `nr`
  - `last_error_time`
- `bch_sb_errors_cpu`: darray of CPU-side error entries.

Important invariants:
- The bit widths mirror the on-disk packed ID/count split.
- Callers keep entries sorted by error ID.

Research notes:
- This file separates runtime container type definitions from the on-disk format catalog.
