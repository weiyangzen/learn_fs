# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/passes_format.h

## Role

Defines the recovery-pass catalog, persistent pass identifiers, pass flags, dependency masks, and the on-disk superblock recovery-pass record format.

## Major Responsibilities

- Defines pass flags: silent, fsck, unclean, always, online, alloc, nodefer, and debug fsck behavior.
- Defines `BCH_RECOVERY_PASSES()` as the single source for pass enum order, stable IDs, flags, dependencies, and descriptions.
- Generates `enum bch_recovery_pass` in run order.
- Generates `enum bch_recovery_pass_stable` for superblock persistence.
- Defines `struct recovery_pass_entry` with `last_run`, `last_runtime`, and flags.
- Defines `struct bch_sb_field_recovery_passes`.
- Provides `recovery_passes_nr_entries()`.

## Pass Categories

The list spans topology scan/repair, accounting/alloc initialization, journal setup/replay, allocator consistency checks, snapshot/subvolume checks, inode/extent/directory/xattr checks, logged-op resume, dead inode/snapshot cleanup, migration passes, reconcile-work checks, btree bitmap GC, and final root inode lookup.

## Notable Details

The file explicitly warns that passes may be reordered but stable IDs must never change. This is the compatibility anchor for persisted recovery requirements and pass history.
