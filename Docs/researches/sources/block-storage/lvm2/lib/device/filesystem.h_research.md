# File Research: sources/block-storage/lvm2/lib/device/filesystem.h

## Purpose
Declares filesystem resize/discovery data structures and APIs used by LVM lvresize code.

## Main Types
`struct fs_info` stores target size, filesystem type, mount directory, filesystem UUID, actual filesystem device path, filesystem block size, last filesystem byte, crypt offset/dev_t/size, and state bits for no filesystem, mounted/unmounted, resize direction, fsck, unmount/mount, and crypt handling.

## Exported API Surface
Declares `fs_get_info`, filesystem extend/reduce helper invocations, crypt resize helper invocation, LV rename/mount-state safety check, active-crypt check, and mounted-XFS size correction.

## Dependencies
Uses `device.h`, Linux `PATH_MAX`, and forward declarations for command context and logical volumes.

## Risk Notes
`fs_info` mixes detected state and planned operation flags. Callers must initialize it and set resize intent fields consistently before invoking helper scripts.
