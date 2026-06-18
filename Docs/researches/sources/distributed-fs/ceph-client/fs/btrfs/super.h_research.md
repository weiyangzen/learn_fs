# sources/distributed-fs/ceph-client/fs/btrfs/super.h

Purpose: Provides the small public header for Btrfs superblock-facing helpers shared outside `super.c`. It exposes option validation, sync, subvolume-name reconstruction, free-space-cache initialization, and inline accessors for `btrfs_fs_info` and read-only state transitions.

Important APIs/types/functions: Declares `btrfs_check_options()`, `btrfs_sync_fs()`, `btrfs_get_subvol_name_from_objectid()`, and `btrfs_set_free_space_cache_settings()`. Defines `btrfs_sb()` as the canonical cast from `struct super_block` to `struct btrfs_fs_info`. Defines `btrfs_set_sb_rdonly()` and `btrfs_clear_sb_rdonly()` to update both `sb->s_flags` and `BTRFS_FS_STATE_RO` together.

Control flow and state: Callers use `btrfs_sb()` throughout Btrfs superblock operations to reach filesystem-global state. Remount and error paths call the read-only helpers instead of manipulating `SB_RDONLY` alone so VFS-visible state and internal Btrfs state remain synchronized. Mount/open code calls the exported option and free-space-cache helpers from disk-io and reconfigure paths.

State and persistence behavior: The header itself has no persistence, but its read-only helpers gate whether later operations may start write transactions or background cleaners. `btrfs_get_subvol_name_from_objectid()` returns allocated memory or an error pointer, so callers own the returned string. `btrfs_sync_fs()` is the VFS sync bridge that can commit persistent transactions.

Dependencies and integration points: Includes Linux type/fs declarations and `fs.h` for `struct btrfs_fs_info` state bits. It is included by superblock, disk open, mount, and other filesystem code that needs a stable way to validate options or update superblock read-only status.

Risks: Directly setting `sb->s_flags` elsewhere without these helpers can desynchronize `BTRFS_FS_STATE_RO`. The header includes `fs.h`, so dependency cycles must be watched when moving declarations. The exported subvolume-name helper allocates up to `PATH_MAX`; callers must free successful results and handle `ERR_PTR`.

Test signals: Build coverage for all external declarations, remount tests that compare `SB_RDONLY` and `BTRFS_FS_STATE_RO`, sync tests through VFS, subvolume show-options tests that free returned names, and mount-option validation tests for callers outside `super.c`.
