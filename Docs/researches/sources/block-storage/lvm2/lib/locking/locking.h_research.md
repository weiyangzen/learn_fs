# File Research: sources/block-storage/lvm2/lib/locking/locking.h

## Purpose
Declares LVM's generic locking API, lock mode/flag constants, special lock resource names, VG unlock helper macros, LV activation helper, and global lock entry points.

## Main Contents
- Declares locking lifecycle functions: `init_locking`, `fin_locking`, `reset_locking`, and `vg_write_lock_held`.
- Declares `lock_vol`, the central VG/global lock function.
- Defines lock type bits for read, write, and unlock plus nonblocking and conversion flags.
- Defines special resource names `VG_ORPHANS` and `VG_GLOBAL`.
- Defines mode aliases for VG read/write/unlock operations.
- Defines `unlock_vg` and `unlock_and_release_vg` macros that sync local device names, trigger VG backup if needed, unlock, and optionally release the VG object.
- Declares file/lvmlockd global lock helpers.

## Dependencies
Includes LVM IDs and config definitions, and forward-declares `struct logical_volume` and `struct volume_group`.

## Risk Notes
The `unlock_vg` macro performs more than unlocking: it may sync device names and write backups. Call sites using it inherit those side effects. The comment requiring alphabetical acquisition of multiple VG locks is a deadlock prevention rule for callers.
