# Group Research: group_955_linux_stable_sources_os_linux_linux_stable_fs_btrfs_send_c_sources_o_4436e6ac90ab

Scope verified against `Docs/research_subset_a.md`. Both listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/send.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/send.c

## Purpose

`send.c` implements the kernel side of Btrfs send stream generation. It walks a read-only send root, optionally compares it against a read-only parent root for incremental send, and writes a serialized command stream to a userspace file descriptor. The stream describes subvolume creation, inode creation/deletion, renames, links, xattrs, file data, clones, truncates, metadata updates, fallocate hole punching, compressed encoded writes, file attributes, and optional fs-verity enablement.

The main public entry point is:

- `long btrfs_ioctl_send(struct btrfs_root *send_root, const struct btrfs_ioctl_send_args *arg)`

## Main State

`struct send_ctx` is the central operation context. It tracks:

- output file and stream buffer state: `send_filp`, `send_off`, `send_buf`, `send_size`, `send_max_size`, `put_data`, `send_buf_pages`
- protocol and flags: `flags`, `proto`
- roots: `send_root`, optional `parent_root`, sorted clone roots
- compare-tree paths and current key
- relocation tracking through `last_reloc_trans`
- current inode metadata and lifecycle state
- current inode page-cache read state and optional page-cache cleanup
- recorded new/deleted refs for deferred processing
- path/name caches and clone backref cache
- pending directory move indexes, waiting move indexes, and orphaned directory tracking
- delayed directory `utimes` and out-of-order directory creation caches

The file uses a compact `struct fs_path` helper for building normal and reversed paths with inline storage and growth up to `PATH_MAX`.

## Stream Serialization

The command writer builds one command at a time:

- `send_header()` writes the stream magic and version.
- `begin_cmd()` reserves a `btrfs_cmd_header`.
- `tlv_put*()` helpers append typed attributes.
- `put_data_header()` handles `BTRFS_SEND_A_DATA`, including the v2+ special trailing data attribute format.
- `send_cmd()` finalizes length and CRC32C, writes the buffer, and resets command state.

Command-specific helpers emit operations such as `send_rename`, `send_link`, `send_unlink`, `send_rmdir`, `send_truncate`, `send_chmod`, `send_chown`, `send_utimes`, `send_fileattr`, `send_fallocate`, `send_update_extent`, `send_write`, `send_clone`, `send_verity`, and `send_subvol_begin`.

## Path and Reference Logic

A large part of the file is devoted to reconstructing what paths should look like at the receiver at the exact point in the stream.

Important helpers include:

- `iterate_inode_ref()` for `BTRFS_INODE_REF_KEY` and `BTRFS_INODE_EXTREF_KEY`
- `get_first_ref()` and `get_inode_path()`
- `get_cur_inode_state()`, `is_inode_existent()`
- `will_overwrite_ref()`, `did_overwrite_ref()`, `did_overwrite_first_ref()`
- `get_cur_path()`, which resolves receiver-time paths using send progress, parent/send roots, orphan names, pending removals, and waiting directory moves

References are collected into `recorded_ref` lists and RB trees. `process_recorded_refs()` then emits the required rename/link/unlink/rmdir sequence, including special handling for:

- new inodes initially created under generated orphan names
- overwritten first references of unprocessed inodes
- hard links
- directory renames that must be delayed
- directories that cannot be removed until children are processed
- parent directory timestamp updates after ref changes

Directory move ordering is handled by `pending_dir_move`, `waiting_dir_move`, `add_pending_dir_move()`, `wait_for_parent_move()`, `wait_for_dest_dir_move()`, `apply_dir_move()`, and `apply_children_dir_moves()`.

## Data Extent Handling

Regular file data emission supports three modes:

- normal `WRITE` commands from the page cache
- `CLONE` commands from the send root or clone roots when safe
- `UPDATE_EXTENT` commands when `BTRFS_SEND_FLAG_NO_FILE_DATA` is set

Clone selection is driven by:

- `find_extent_clone()`
- `iterate_backrefs()`
- `lookup_backref_cache()` and `store_backref_cache()`
- `clone_range()`
- `send_write_or_clone()`

The code avoids unsafe clone cases, including cloning from future receiver state, overlapping current ranges, unaligned EOF blocks, source extents beyond source i_size, too many extent refs, and clone sources affected by relocation.

For compressed sends, protocol v2+ can emit `BTRFS_SEND_C_ENCODED_WRITE` through:

- `send_encoded_inline_extent()`
- `send_encoded_extent()`

The implementation only sends encoded data when compressed data is not larger than the requested unencoded range. Otherwise it falls back to normal file data reads.

Hole handling uses:

- `need_send_hole()`
- `send_hole()`
- `maybe_send_hole()`
- `range_is_hole_in_parent()`

With protocol support, holes are represented with `FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE`; older streams write zeroes or update extents depending on flags.

## Xattrs, Capabilities, and Verity

Xattrs are processed by walking `BTRFS_XATTR_ITEM_KEY` dir items:

- new xattrs use `send_set_xattr()`
- removed xattrs use `send_remove_xattr()`
- changed xattrs compare data against the parent root

Special cases:

- `security.capability` is skipped during generic xattr processing and emitted later by `send_capabilities()`.
- Empty POSIX ACL xattrs are serialized as a dummy ACL header so receive does not fail on zero-byte ACL data.
- fs-verity is protocol-gated through `BTRFS_SEND_C_ENABLE_VERITY`; `process_verity()` fetches the descriptor and `send_verity()` emits algorithm, block size, salt, and signature data.

## Tree Comparison

Full sends use `full_send_tree()` to iterate the send root as all-new items.

Incremental sends use `btrfs_compare_trees()`, which compares send and parent commit roots. It skips shared subtrees when block pointers and generations match, deep-compares leaf items when keys match, and reports new/deleted/changed/same items to `changed_cb()`.

Important safeguards:

- commit root semaphore is released before callbacks that can write to userspace, avoiding send/receive deadlocks through pipes or files on the same filesystem
- root and leaf extent buffers are cloned where needed so callbacks can safely inspect them outside commit-root locking
- block group relocation is tracked with `last_reloc_trans`; stale paths are restarted through `restart_after_relocation()` and `search_key_again()`
- relocation-sensitive clone decisions fall back to writes if disk bytenr information may be stale

`changed_cb()` dispatches by item type to inode, ref, xattr, extent, and verity handlers. It also treats unchanged refs in changed parent directories as changed and sends holes for unchanged extents when needed.

## Inode Lifecycle

`changed_inode()` initializes current inode state for new, deleted, and changed inode items. It handles:

- orphan inodes with zero link count
- inode generation changes as delete-plus-create reuse of the same inode number
- root directory special case
- creating new inodes under orphan names
- processing all refs, extents, and xattrs for generation-reused inodes

`finish_inode_if_needed()` finalizes pending refs, emits truncates, chown/chmod/fileattr changes, verity, capabilities, child directory moves, and utimes. It delays directory utimes through an LRU cache so non-empty directories receive final timestamps after child entries are added.

## Ioctl Setup and Cleanup

`btrfs_ioctl_send()` enforces:

- `CAP_SYS_ADMIN`
- read-only, non-dead send root
- no active deduplication on send, parent, or clone roots
- valid flags and protocol version
- protocol v2+ for compressed send
- writable `send_fd`
- bounded clone source count and allocation size

It increments `send_in_progress` on all participating roots, copies clone source root IDs from userspace, resolves clone roots, adds the send root as an implicit clone source, sorts clone roots, flushes delalloc, ensures commit roots are up to date, runs `send_subvol()`, flushes delayed directory utimes, and optionally emits `BTRFS_SEND_C_END`.

Cleanup frees pending move/orphan state, decrements root send counters, drops root refs, frees buffers, closes current inode, clears LRUs, releases the output file, and frees the context.

## Dependencies

Internal Btrfs dependencies include tree search/walk APIs, root and transaction handling, backref walking, inode accessors, extent data helpers, xattr lookup, dir item parsing, compression helpers, verity helpers, and the Btrfs LRU cache.

Kernel dependencies include file writes, folio/page-cache reads and readahead, vmalloc/kvmalloc, rbtrees, CRC32C, xattrs, POSIX ACL xattr format, fs-verity descriptors, sorting/bsearch, and capability checks.

## Risk Notes

This file is correctness-critical. Highest-risk areas are incremental rename ordering, orphan name handling, hard-link/reference conflict resolution, delayed directory moves, stale extent handling during relocation, clone safety around EOF and receiver state, and protocol compatibility for v1/v2/v3 streams.

The implementation contains many defensive checks: `WARN_ON`, `ASSERT`, explicit `-EUCLEAN` paths, relocation restarts, root read-only checks, dedupe exclusion, generation checks, and cache invalidation. Any changes here need focused send/receive regression coverage, especially for nested directory swaps, hard links, reflinked extents, compressed extents, holes, inode generation reuse, orphan inodes, and same-filesystem send/receive through a pipe.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/send.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/send.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/send.h

## Purpose

`send.h` defines the public Btrfs send stream format constants used by kernel send generation and userspace receive parsing. It also declares the ioctl entry point:

- `long btrfs_ioctl_send(struct btrfs_root *send_root, const struct btrfs_ioctl_send_args *arg);`

## Protocol Versioning

The stream magic is `btrfs-stream`.

`BTRFS_SEND_STREAM_VERSION` is:

- `3` when `CONFIG_BTRFS_EXPERIMENTAL` is enabled
- `2` otherwise

Buffer sizing is version-dependent:

- v1 commands are bounded by `BTRFS_SEND_BUF_SIZE_V1`, 64 KiB
- v2 uses `BTRFS_SEND_BUF_SIZE_V2`, aligned to fit a command header plus maximum compressed extent payload

## Wire Structures

The header defines packed stream wire structures:

- `struct btrfs_stream_header`: magic plus little-endian stream version
- `struct btrfs_cmd_header`: command payload length, command ID, and CRC
- `struct btrfs_tlv_header`: attribute type and attribute length

`enum btrfs_tlv_type` documents supported value classes: integer widths, binary, string, UUID, and timespec.

## Commands

`enum btrfs_send_cmd` defines stream command IDs.

Version 1 commands include subvolume/snapshot creation, inode creation types, rename/link/unlink/rmdir, xattr set/remove, write, clone, truncate, chmod, chown, utimes, end, and update extent.

Version 2 adds:

- `BTRFS_SEND_C_FALLOCATE`
- `BTRFS_SEND_C_FILEATTR`
- `BTRFS_SEND_C_ENCODED_WRITE`

Version 3 adds:

- `BTRFS_SEND_C_ENABLE_VERITY`

The enum also records max command IDs per protocol version.

## Attributes

The send attribute enum defines TLV attribute IDs.

Version 1 attributes cover UUIDs, transaction IDs, inode metadata, timestamps, xattr name/data, paths, file offsets, write data, and clone source metadata.

Version 2 adds:

- fallocate mode
- Btrfs inode file attributes
- encoded write unencoded length/offset metadata
- compression and encryption fields

`BTRFS_SEND_A_DATA` has special v2 behavior: it must be the final command attribute, its header carries only the type, and its length is implicitly the remaining command length.

Version 3 adds fs-verity attributes:

- hash algorithm
- block size
- salt data
- signature data

## Integration Notes

This header is the format contract consumed by `send.c`. Any changes to command IDs, attribute IDs, packed structures, or max-version constants affect stream compatibility with userspace receive tools and older kernels. New features must be protocol-gated, as `send.c` does for fallocate, file attributes, encoded writes, and verity.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/send.h -->