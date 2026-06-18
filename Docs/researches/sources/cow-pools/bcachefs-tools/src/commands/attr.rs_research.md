# File Research: sources/cow-pools/bcachefs-tools/src/commands/attr.rs

This file implements file-level option commands for bcachefs.

Commands:
- `set-file-option`
- `reflink-option-propagate`

`set-file-option` behavior:
- Builds dynamic clap arguments from inode option metadata.
- Sets extended attributes named `bcachefs.<option>`.
- Removes a specific option when value is `-`.
- Supports `--remove-all`, excluding `casefold` because it only works on empty directories.
- If the target is a directory, recursively propagates inherited attributes to children through `BCHFS_IOC_REINHERIT_ATTRS`.
- Skips symlink recursion.

`reflink-option-propagate` behavior:
- Propagates current IO options to reflinked extents.
- Optional `--set-may-update` calls an ioctl to set the permission bit on old reflink pointers.
- Maps `EPERM` to a user-facing error suggesting rerun as root with `--set-may-update`.

Key ioctls:
- `BCHFS_IOC_REINHERIT_ATTRS`
- `BCHFS_IOC_SET_REFLINK_P_MAY_UPDATE_OPTS`
- `BCHFS_IOC_PROPAGATE_REFLINK_P_OPTS`

Dependencies:
- `rustix::fs` for xattr operations.
- `bch_bindgen::c` for option metadata.
- Local `opts` helpers for option parsing.
