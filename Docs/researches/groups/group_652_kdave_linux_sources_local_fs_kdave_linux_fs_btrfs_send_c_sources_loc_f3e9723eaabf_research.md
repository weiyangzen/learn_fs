# Group Research: group_652_kdave_linux_sources_local_fs_kdave_linux_fs_btrfs_send_c_sources_loc_f3e9723eaabf

Scope: subset A from `Docs/research_subset_a.md`, covering the listed `sources/local-fs/kdave-linux/fs/btrfs` send-stream files. Both listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/send.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/send.c

## Scope

`send.c` implements the kernel side of Btrfs send. It converts a read-only subvolume, optionally relative to a parent snapshot and clone-source roots, into a serialized Btrfs send stream written to a userspace file descriptor. It covers stream command construction, full and incremental tree comparison, path resolution at receiver-time state, inode/ref/xattr/extent processing, clone and encoded-write selection, directory move ordering, verity metadata emission, and the public `btrfs_ioctl_send()` entry point.

## Main Interfaces

- Public entry point: `btrfs_ioctl_send()`.
- Stream driver: `send_subvol()`, `send_subvol_begin()`, `full_send_tree()`, `btrfs_compare_trees()`, `changed_cb()`.
- Command writers: `send_header()`, `begin_cmd()`, `send_cmd()`, `send_rename()`, `send_link()`, `send_unlink()`, `send_rmdir()`, `send_create_inode()`, `send_truncate()`, `send_chmod()`, `send_chown()`, `send_utimes()`, `send_fileattr()`, `send_set_xattr()`, `send_remove_xattr()`, `send_write()`, `send_clone()`, `send_update_extent()`, `send_fallocate()`, `send_verity()`.
- Data paths: `send_extent_data()`, `send_write_or_clone()`, `clone_range()`, `send_encoded_inline_extent()`, `send_encoded_extent()`, `send_hole()`.
- Incremental reference logic: `record_new_ref()`, `record_deleted_ref()`, `record_changed_ref()`, `process_recorded_refs()`, pending/waiting directory move helpers, orphan directory helpers.

## Core State

- `struct send_ctx` is the central execution context. It owns the output file, stream buffer/pages, protocol version, send/parent/clone roots, compare-tree paths, current inode state, progress cursor, recorded references, LRU caches, pending directory move indexes, orphan directory tracking, backref cache, and current inode page-cache cleanup state.
- `struct fs_path` is a small-inline dynamic path builder. It supports normal and reversed construction so paths can be assembled from leaf inode references up toward the root and then unreversed.
- Clone discovery uses `struct clone_root`, `struct backref_ctx`, and an optional LRU backref cache mapping leaf bytenrs to clone-root IDs.
- Directory rename ordering uses `struct pending_dir_move`, `struct waiting_dir_move`, and `struct orphan_dir_info` rb-trees to delay moves that depend on higher-numbered ancestors or destination-name conflicts.
- Reference processing uses `struct recorded_ref` lists plus rb-trees to collect new/deleted refs before issuing stream operations in a safe order.

## Stream Encoding

- The stream uses the structures and command/attribute IDs from `send.h`.
- `tlv_put*()` helpers append attributes to the per-command buffer and reject attributes after a data payload has been added.
- Protocol v2+ treats `BTRFS_SEND_A_DATA` specially: the data attribute header contains only the type, with length implied by the remaining command size. Protocol v1 writes a full TLV header.
- `send_cmd()` fills command length, computes crc32c with the crc field zeroed, writes the command to `send_filp`, then resets per-command buffer state.
- Protocol checks gate v2/v3 commands such as fallocate, file attributes, encoded writes, and verity.

## Path And Inode Resolution

- `get_inode_info()`, `get_inode_gen()`, `get_first_ref()`, `get_inode_path()`, `iterate_inode_ref()`, and `iterate_dir_item()` read commit-root metadata through send-safe paths.
- `get_cur_path()` reconstructs the path an inode should have at the current receiver progress point. It chooses send-root refs for already processed inodes, parent-root refs for unprocessed inodes, and generated orphan names for not-yet-existing, overwritten, deleted, waiting, or orphanized directories.
- The name cache stores `(ino, gen) -> parent/name/result` lookups and invalidates entries whose later state can change after progress advances or orphanization happens.
- Generated orphan names are checked for uniqueness in send and parent roots.

## Incremental Send Behavior

- `changed_inode()` establishes current inode state from compare-tree results, including new, deleted, changed, reused generation, zero-nlink orphan handling, current size/mode/rdev, and whether an inode should be ignored.
- `changed_ref()` records new/deleted/changed inode refs instead of immediately emitting link/unlink/rename operations. This lets `process_recorded_refs()` handle overwrites, hard links, directory moves, and unlink/rmdir ordering consistently.
- `process_recorded_refs()` first orphanizes conflicting unprocessed inodes, creates parent directories out of order when required, delays directory renames whose ancestors or destination names are still pending, emits rename/link/unlink/rmdir operations, and queues parent directory utime updates.
- Deleted non-empty directories are renamed to orphan names until their children have been processed and `can_rmdir()` determines they can be removed.
- Directory utime updates are cached and trimmed so final directory timestamps are sent after likely child-entry changes.

## Extents, Clones, Holes, And Encoded Data

- `process_extent()` skips symlink data, ignores unchanged extents in incremental sends, handles no-data/update-extent mode, and otherwise tries clone discovery before falling back to write data.
- `find_extent_clone()` walks extent backrefs against allowed clone roots, rejects unusable future receiver state, avoids excessive backref walking for highly shared extents, handles relocation races, and selects the clone source with the longest useful range.
- `clone_range()` verifies the source file extent layout over the intended clone range. If the clone source has holes, mismatched extents, EOF alignment hazards, or ranges beyond source i_size, it emits a mix of clone and write operations.
- `send_write()` reads file data through the page cache using readahead and optionally evicts pages it pulled into cache for send-only reads.
- With `BTRFS_SEND_FLAG_COMPRESSED` and protocol v2+, compressed extents may be sent as `BTRFS_SEND_C_ENCODED_WRITE` when the encoded payload is not larger than the requested logical range.
- Holes are sent as fallocate punch-hole commands for protocol v2+ when possible, as update-extent in no-file-data mode, or as zero writes for older streams when needed.

## Tree Comparison

- Full sends iterate the send root from `BTRFS_FIRST_FREE_OBJECTID` and treat every item as new.
- Incremental sends use `btrfs_compare_trees()` to walk send and parent commit roots together. Shared tree blocks are skipped, leaf items are deep-compared, and changed/new/deleted items are passed to `changed_cb()`.
- The compare code clones root and leaf extent buffers when needed so callbacks can drop `commit_root_sem` before writing to the output file, avoiding deadlocks with receive or same-filesystem output writes.
- Block-group relocation is tracked through `last_reloc_trans`; tree walks and backref-cache state are restarted or invalidated when relocation may have made nodes or extent bytenrs stale.

## Ioctl Setup And Cleanup

- `btrfs_ioctl_send()` requires `CAP_SYS_ADMIN`, read-only live send/parent/clone roots, no dedupe in progress, valid flags, and a writable output fd.
- It selects protocol version from flags, defaults to v1 when no version flag is supplied, rejects compressed sends before v2, and allocates the send buffer using v1 or v2 sizing.
- It copies and validates clone-source root IDs from userspace, increments `send_in_progress` on participating roots, adds the send root itself as an eligible clone source, sorts clone roots for bsearch, flushes delalloc, and commits roots when commit roots are stale after orphan cleanup.
- On success it sends the optional stream header, subvol/snapshot command, file-item stream, delayed directory utimes, and optional END command.
- Cleanup drains pending move/orphan rb-trees, decrements `send_in_progress`, drops root/file/inode references, frees buffers and caches, and closes any current inode.

## Dependencies

- Btrfs tree/search helpers, commit roots, inode items, dir items, file extents, backref walking, encoded read helpers, compression translation, verity helpers, transaction commit, root lookup/refcounting, and LRU cache helpers.
- Linux VFS/MM primitives: `kernel_write()`, file references, page cache/folios, readahead, xattrs, POSIX ACL xattr format, capabilities, fallocate flags, crc32c, fsverity descriptor APIs, rb-trees, sorting/bsearch, and vmalloc/kvmalloc allocation.

## Risks And Invariants

- The send root, parent root, and clone roots must remain read-only and not be deduplicated while send is in progress.
- Path reconstruction depends on `send_progress`; moving it too early or too late can emit paths that do not exist at the receiver.
- Directory move dependencies must avoid cycles, parent-before-child ordering errors, and stale orphanized path components.
- Clone commands are only valid when the receiver has already materialized the source path/range and when EOF/sector-alignment rules are respected.
- Relocation can make held metadata or extent bytenrs stale; relocation generation checks are part of correctness, not just optimization.
- `commit_root_sem` must not be held while writing stream data because output may block on receive or same-filesystem writes that need transaction progress.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/send.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/send.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/send.h

## Scope

`send.h` defines the Btrfs send-stream wire constants, command and attribute IDs, TLV/header layouts, protocol-version limits, buffer sizing, and the kernel-internal declaration for `btrfs_ioctl_send()`.

## Interfaces And Constants

- Stream identity: `BTRFS_SEND_STREAM_MAGIC` and `BTRFS_SEND_STREAM_VERSION`.
- Protocol version selection is conditional: version 3 is exposed only with `CONFIG_BTRFS_EXPERIMENTAL`; otherwise the maximum is version 2.
- Buffer sizes: v1 uses `BTRFS_SEND_BUF_SIZE_V1` at 64 KiB; v2 uses `BTRFS_SEND_BUF_SIZE_V2`, aligned to fit command overhead plus maximum compressed extent payload.
- Wire structs: `struct btrfs_stream_header`, `struct btrfs_cmd_header`, and `struct btrfs_tlv_header`, all packed and little-endian.
- TLV type enum describes expected value encodings: integers, binary, string, UUID, and Btrfs timespec.
- Public declaration: `long btrfs_ioctl_send(struct btrfs_root *send_root, const struct btrfs_ioctl_send_args *arg);`.

## Command Space

- Version 1 commands cover subvol/snapshot creation, file and special-file creation, symlink, rename/link/unlink/rmdir, xattr updates, write/clone, truncate/chmod/chown/utimes, END, and update-extent.
- Version 2 adds fallocate, file-attribute updates, and encoded writes.
- Version 3 adds enable-verity.
- `BTRFS_SEND_C_MAX_V1`, `_V2`, `_V3`, and `BTRFS_SEND_C_MAX` define protocol-specific command ceilings used by `send.c`.

## Attribute Space

- Version 1 attributes cover UUIDs, ctransids, inode metadata, xattr name/data, paths, write offsets/data, and clone source metadata.
- `BTRFS_SEND_A_DATA` has a v2+ special encoding: it must be the final command attribute and its length is implied by the remaining command bytes.
- Version 2 adds fallocate mode, Btrfs inode file attributes, unencoded lengths/offsets, compression, and encryption metadata for encoded writes.
- Version 3 adds verity algorithm, block size, salt, and signature data.

## Dependencies

- Includes Linux scalar/size/alignment headers and forward-declares `struct btrfs_root` and `struct btrfs_ioctl_send_args`.
- Consumed by `send.c` for stream construction and by any internal caller needing the ioctl implementation declaration.

## Risks And Invariants

- Command and attribute numeric values are wire format and must remain stable for userspace receive compatibility.
- Packed little-endian headers are part of the stream ABI.
- Protocol-gated maximum constants must stay synchronized with the enums, `proto_cmd_ok()` logic, and userspace receiver support.
- The v2 data-attribute special case constrains command-building order: payload data must be emitted last.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/send.h -->