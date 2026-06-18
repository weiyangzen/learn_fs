# sources/distributed-fs/ceph-client/fs/ubifs/sb.c

## Purpose
`sb.c` owns the UBIFS superblock media contract. It can create a default filesystem on an empty UBI volume, read and validate an existing superblock, authenticate it when UBIFS authentication is enabled, update persistent superblock flags, and perform the one-time free-space fixup needed for images whose free areas were programmed as literal `0xff` bytes instead of being truly erased.

The file treats the superblock as mostly immutable UBIFS geometry: LEB size/count, log/LPT/orphan/main area layout, fanout, journal sizing, default compressor, reserved pool, feature flags, format version, UUID, encryption, double-hash, big-LPT, and authentication metadata.

## Important APIs, Types, And Functions
`get_default_compressor()` chooses ZSTD, LZO, ZLIB, then none based on compiled compressor availability. `create_default_filesystem()` formats an empty volume by synthesizing and writing the superblock, master nodes, root index node, root inode, LPT, and initial commit-start node. `validate_sb()` checks superblock-derived state in `struct ubifs_info` against UBI geometry, minimum area sizes, journal constraints, fanout, LPT save table sizing, feature/version rules, compression type, reserved-pool bounds, and time granularity.

`ubifs_read_superblock()` is the mount-time entry point. It optionally formats an empty volume, reads `UBIFS_SB_LNUM`, fills `struct ubifs_info`, handles forward format versions and read-only compatibility, selects key hash and key format, validates authentication and feature flags, performs automatic resize to the UBI volume limit, computes area boundaries, and calls `validate_sb()`.

`ubifs_write_sb_node()` rewrites the aligned superblock LEB after preparing HMAC metadata. `ubifs_fixup_free_space()` performs the first-mount free-space rewrite and clears `UBIFS_FLG_SPACE_FIXUP` in memory, deferring persistent write through `c->superblock_need_write`. `ubifs_enable_encryption()` is the ioctl-facing persistent feature enable path: it validates kernel support, writeability, and format version, sets `UBIFS_FLG_ENCRYPTION`, writes the superblock immediately, and flips `c->encrypted`.

## Control Flow
On empty mount, `create_default_filesystem()` computes journal/log/orphan/LPT/main-area sizes, asks `ubifs_create_dflt_lpt()` for LPT geometry, allocates aligned node buffers, initializes superblock and master fields, creates root inode/index content, calculates hashes, writes the superblock/master nodes with HMAC where needed, writes the root inode/index, and writes an initial commit-start node into the log. On normal mount, `ubifs_read_superblock()` reads the superblock, populates `c`, authenticates, may auto-resize, derives area offsets, and validates. One-time space fixup later walks master, log, LPT, orphan, and main areas to unmap empty LEBs or rewrite used prefixes with `ubifs_leb_change()`.

## State And Persistence
Persistent state is the on-flash superblock, initial master nodes, root inode, root index, LPT, and log commit-start node. `c->sup_node` keeps the in-memory copy. `c->superblock_need_write` bridges state changes made during mount, such as auto-resize, authentication HMAC conversion, or space-fixup flag clearing, to a later safe superblock rewrite. Feature flags are high risk because they gate compatibility and later mount behavior: authentication and encryption require support/key material, double hash requires format version 5+, and unknown flags reject the mount.

## Dependencies And Integration Points
This file integrates with UBI IO wrappers (`ubifs_leb_read`, `ubifs_leb_change`, `ubifs_leb_unmap`, `ubifs_write_node*`), media definitions from `ubifs-media.h`, key helpers, compressor registration, LPT creation and lookup, authentication/HMAC/signature helpers, mount setup in `super.c`, and encryption enablement through `ioctl.c`. `ubifs_read_superblock()` is called from `mount_ubifs()`, while `ubifs_fixup_free_space()` is called during mount and remount-rw when the superblock flag requires it.

## Risks And Edge Cases
Geometry arithmetic must avoid overflow and preserve UBIFS minimum-area invariants. Bad format-version handling could accidentally allow writes to incompatible media. Auto-resize mutates the superblock path only after validation and requires a later write; failure before that write can leave resize pending. Authentication mode mismatches are hard failures. Free-space fixup rewrites or unmaps broad media ranges and must not run on read-only mounts. Encryption enablement is persistent and irreversible for old kernels, so it strictly requires format version 5 and write access.

## Test Signals
Useful signals include mounting an empty UBI volume and checking default layout/root inode creation, mounting malformed superblocks for each `validate_sb()` branch, authentication mount combinations with and without keys, auto-resize on a grown UBI volume, `space_fixup` first-mount behavior followed by flag clearing, encryption ioctl behavior on unsupported/read-only/old-format filesystems, and fault injection around `ubifs_write_sb_node()` and LEB rewrite/unmap operations.
