# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/progress.c

## Role

Implements coarse progress indicators for long btree scans during recovery/fsck.

## Major Responsibilities

- Initializes progress state with a message, target btree masks, and estimated node totals.
- Estimates total nodes from accounting counters, falling back to disk-sector estimates when older accounting data lacks node counts.
- Updates progress from a `btree_iter`, including cancellation checks.
- Periodically logs progress every 10 seconds unless silent.
- Formats progress as percent, nodes seen/total, and current btree position.

## Notable Details

The implementation explicitly treats totals as estimates because node replica counts can vary. It prefers underestimating missing accounting data as zero or using disk-sector estimates instead of blindly trusting incomplete counters.
