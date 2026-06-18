# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/init.h

## Role

Declares journal allocation, startup/shutdown, replay completion, and init/exit helpers.

## Contents

Functions cover device bucket count changes, bucket deletion, device/fs journal allocation, per-device stop, fs stop/start, replay-done transition, and early/full init/exit for device and filesystem journal objects.

## Notable Details

`bch2_fs_journal_start()` consumes `struct journal_start_info`, which is produced by journal read/recovery.
