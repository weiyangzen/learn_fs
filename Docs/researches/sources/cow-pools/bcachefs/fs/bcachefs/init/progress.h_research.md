# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/progress.h

## Role

Declares the recovery/fsck progress indicator structure and helpers.

## Contents

- `struct progress_indicator` stores message, current `bbpos`, next print time, seen/total node counts, last node, and silent mode.
- Declares initialization, iterator update, and text formatting functions.

## Notable Details

The header comments call these indicators a fallback for contexts where userspace progress reporting is not wired up, especially older code and mount-time recovery.
