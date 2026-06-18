# sources/distributed-fs/ceph-client/fs/f2fs/super.c

## Purpose
`super.c` is the F2FS superblock and filesystem-type implementation. It wires F2FS into the VFS mount API, parses and applies mount options, validates raw on-disk superblocks and checkpoints, initializes per-mount state, registers superblock operations, handles remount/freeze/unfreeze/sync/shutdown, manages quota integration, records critical filesystem errors, and owns module-level cache/sysfs/shrinker registration.

## Important APIs, Types, And Functions
The central local type is `struct f2fs_fs_context`, which holds a pending `struct f2fs_mount_info`, an option bitmask, a specification bitmask, and quota filename change state while VFS parses a mount or remount. The file exports or defines `f2fs_printk()`, `f2fs_sync_fs()`, `f2fs_sanity_check_ckpt()`, `f2fs_commit_super()`, `f2fs_handle_error()`, `f2fs_stop_checkpoint()`, `max_file_blocks()`, quota helpers such as `f2fs_dquot_initialize()` and `f2fs_do_quota_sync()`, and the module entry points `init_f2fs_fs()` and `exit_f2fs_fs()`.

Mount parsing is table driven through `f2fs_param_specs`, `f2fs_parse_param()`, enum option tokens, and constant tables for background GC, allocation mode, fsync mode, compression mode, discard unit, memory mode, errors behavior, and lookup mode. Consistency checks are split into `f2fs_check_quota_consistency()`, `f2fs_check_test_dummy_encryption()`, `f2fs_check_compression()`, `f2fs_check_opt_consistency()`, and `f2fs_sanity_check_options()`. Application is handled by `f2fs_apply_options()` plus dedicated quota, dummy encryption, and compression apply functions.

The VFS integration points are `f2fs_sops`, `f2fs_export_ops`, optional `f2fs_cryptops`, optional `f2fs_verityops`, `f2fs_context_ops`, and `f2fs_fs_type`. `f2fs_fill_super()` is the main mount routine called through `get_tree_bdev()`, while `__f2fs_remount()` backs `->reconfigure`.

## Control Flow
Mount setup starts in `f2fs_init_fs_context()`, where VFS receives a private context and `f2fs_context_ops`. `f2fs_parse_param()` records user options without immediately mutating mounted state. `f2fs_get_tree()` calls `f2fs_fill_super()`, which allocates `struct f2fs_sb_info`, initializes locks, sets the block size, reads both raw superblock copies with `read_raw_super_block()`, applies defaults and parsed options, installs superblock operations, and initializes F2FS subsystems in a strict order.

`f2fs_fill_super()` then reads the meta inode and checkpoint, initializes devices including multi-device and zoned-device state, starts checkpoint machinery, builds segment and node managers, reads root and node inodes, initializes compression state, registers sysfs/procfs entries, enables quotas when needed, recovers orphan inodes and fsync data, handles checkpoint-disabled state, optionally starts GC, repairs a bad backup superblock, joins the global shrinker list, and returns with `SBI_POR_DOING` cleared. Every failure label unwinds only the resources initialized so far.

Remount follows a save, validate, apply, activate pattern. `__f2fs_remount()` snapshots old mount options and quota names, attempts pending superblock recovery, reapplies defaults, validates the new context, applies options, and then starts or stops GC, flush, discard, checkpoint, and quota machinery according to the requested read-only state and option changes. On failure, it rolls runtime threads and options back using the saved state.

Unmount and shutdown paths are split between `kill_f2fs_super()` and `f2fs_put_super()`. `kill_f2fs_super()` stops GC/discard, writes a final checkpoint when needed, and calls `kill_block_super()`. `f2fs_put_super()` unregisters sysfs early, turns quotas off, stops checkpoint work, writes an umount checkpoint if dirty, drains discards and merged writes, validates page counters, destroys all per-mount managers and caches, releases raw super/checkpoint buffers, unloads Unicode state, and invalidates block devices.

## State And Persistence Behavior
Persistent state includes the raw F2FS superblock copies, checkpoint packs, quota files or quota inodes, feature flags, stop reasons, error bits, extension lists, and recovered fsync/orphan metadata. `sanity_check_raw_super()` validates magic, checksums, block geometry, segment layout, area boundaries, device segment totals, extension counts, payload sizes, and reserved inode numbers before mount continues. `f2fs_sanity_check_ckpt()` validates checkpoint counters, current segment positions, SIT/NAT bitmap sizes, payload placement, NAT bits sizing, and error flags.

Superblock writes use `f2fs_commit_super()` and `__f2fs_commit_super()`, writing backup first, optionally updating CRC, and using synchronous prefush/FUA I/O. If write access is unavailable, recovery is recorded with `SBI_NEED_SB_WRITE` so a later writable remount can repair. Critical errors set `CP_ERROR_FLAG`, persist `s_errors` and `s_stop_reason` asynchronously through `s_error_work`, and follow the mount `errors=` policy: continue, panic, or stop future updates and behave as read-only without directly changing `SB_RDONLY` outside remount locking.

Checkpoint enable and disable are active state transitions. `f2fs_disable_checkpoint()` may run urgent foreground GC until unusable blocks fit the requested cap, writes a pause checkpoint, sets `SBI_CP_DISABLED`, and records unusable blocks. `f2fs_enable_checkpoint()` flushes dirty/skipped data, clears checkpoint-disabled state, marks the filesystem dirty, syncs a checkpoint, and flushes the checkpoint thread.

## Dependencies And Integration Points
This file is tightly coupled to nearly every F2FS subsystem: node manager, segment manager, checkpoint, recovery, GC, discard, compression, xattr, iostat, sysfs, extent cache, post-read processing, and shrinker registration. Kernel dependencies include VFS superblock and fs_context APIs, block devices, quota, fscrypt, fsverity, Unicode casefolding, KUnit-visible module init behavior, shrinkers, workqueues, procfs/sysfs, and zoned block device reporting.

The file also exposes F2FS behavior to users through mount options, `/proc/mounts` show-options output, `statfs`, NFS export handles, quota operations, freeze/unfreeze, shutdown, and module registration under filesystem name `f2fs`.

## Risks
The highest-risk areas are mount/remount rollback, checkpoint-disabled transitions, quota state changes, and raw metadata validation because they combine persistent media state with live kernel threads and VFS flags. Option interactions are complex: zoned devices require discard and LFS-compatible settings, device aliasing requires extent cache, readonly features restrict writable mounts, and several options cannot be switched dynamically. Error handling must avoid deadlocks because it may run from I/O completion or recovery paths. Any change to cleanup labels in `f2fs_fill_super()` can leak inodes, kobjects, block devices, or leave background threads running.

## Test Signals
Useful signals include mounting clean and unclean images, corrupt-superblock and corrupt-checkpoint tests, remount option matrices, checkpoint disable/enable stress, quota-on/quota-off and journaled quota tests, fscrypt/fsverity mount combinations, zoned block device tests, fault injection through `CONFIG_F2FS_FAULT_INJECTION`, freeze/thaw tests, `statfs` with project quotas, and teardown leak checks from F2FS page counters and lockdep.
