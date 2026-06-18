# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/passes_types.h

## Role

Defines runtime recovery-pass state embedded in `struct bch_fs`.

## Contents

`struct bch_fs_recovery` tracks:

- Ephemeral scheduled passes.
- Current pass set and current pass.
- Rewind source/target and `pass_done`.
- Completed, failing, and ratelimited pass masks.
- A spinlock for state updates.
- A `run_lock` mutex to serialize pass execution.
- A work item for async online recovery passes.

## Notable Details

The separation between persistent superblock bits and `scheduled_passes_ephemeral` lets the filesystem request immediate recovery ordering without committing every transient prerequisite to disk.
