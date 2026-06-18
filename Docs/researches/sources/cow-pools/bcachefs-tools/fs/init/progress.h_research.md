# File Research: sources/cow-pools/bcachefs-tools/fs/init/progress.h

Header for lightweight recovery/mount progress indicators.

Key contents:
- Includes `btree/bbpos_types.h`.
- Documents that these indicators are a fallback because dmesg output is spammy and userspace/thread-with-file reporting is preferred.
- Defines `struct progress_indicator`:
  - Message string.
  - Current `bbpos`.
  - Next print jiffies.
  - Nodes seen/total.
  - Last btree node.
  - Silent flag.
- Declares:
  - `bch2_progress_init()`
  - `bch2_progress_update_iter()`
  - `bch2_progress_to_text()`

Role:
- Shared utility for recovery/fsck passes that walk btrees and need coarse progress reporting during mount or non-interactive contexts.
