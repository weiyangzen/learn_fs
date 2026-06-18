# sources/distributed-fs/ceph-client/drivers/mtd/mtdsuper.c

Purpose: provides common superblock mounting helpers for filesystems that live directly on MTD devices rather than normal block devices. Filesystems call `get_tree_mtd()` during mount and `kill_mtd_super()` during teardown.

Important APIs and types: exported APIs are `get_tree_mtd()` and `kill_mtd_super()`. Internal helpers are `mtd_get_sb()` and `mtd_get_sb_by_nr()`. The code attaches `struct mtd_info` to `super_block.s_mtd`, uses `sget_dev()` with `MKDEV(MTD_BLOCK_MAJOR, mtd->index)`, and calls the filesystem-provided `fill_super()` callback.

Control flow: `get_tree_mtd()` requires `fc->source`. It first accepts modern `mtd:<name>` syntax via `get_mtd_device_nm()`, then `mtdN` numeric syntax via `get_mtd_device()`. With `CONFIG_BLOCK`, it also supports legacy `/dev/mtdblockN`-style sources by resolving a block device and checking `MTD_BLOCK_MAJOR`. `mtd_get_sb()` either reuses an already-mounted superblock and releases the extra MTD reference, or initializes a fresh superblock, assigns `s_mtd`, gets the shared MTD backing-dev info, invokes `fill_super()`, and activates the superblock.

State and persistence: there is no on-flash state management here. Runtime state is the superblock reference, the held MTD device reference, `s_mtd`, `s_bdi`, and the filesystem root in the mount context.

Dependencies and integration points: integrates VFS fs_context mount flow, MTD device lookup/reference APIs, optional block-device lookup compatibility, and the MTD core backing-dev object. Direct consumers include MTD-backed filesystems that need common parsing and reference handling.

Risks and test signals: correctness hinges on balanced `get_mtd_device*()`/`put_mtd_device()` references, reuse of existing superblocks, and error unwind after `fill_super()` failure. Tests should cover `mtd:<name>`, `mtdN`, legacy block source with and without `CONFIG_BLOCK`, nonexistent devices, non-MTD sources, duplicate mounts, and `kill_mtd_super()` releasing the MTD reference after `generic_shutdown_super()`.
