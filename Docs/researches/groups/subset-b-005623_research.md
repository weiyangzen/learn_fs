# subset-b-005623 Research

Grouped source research for Btrfs send stream implementation and protocol declarations. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/send.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/send.c

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/send.c` implements the kernel side of `BTRFS_IOC_SEND`: it serializes a read-only Btrfs subvolume or snapshot into the userspace Btrfs send stream consumed by `btrfs receive`. The file covers full sends, incremental sends against a parent root, clone-source optimization, metadata and xattr changes, fs-verity enablement, encoded/compressed writes, sparse range handling, and the ordering rules needed to replay renames, links, unlinks, and directory removals without breaking receiver path resolution. The source was read as a complete 8326-line file for this report.

## Important APIs, Types, and Functions

The exported entry point is `btrfs_ioctl_send(struct btrfs_root *send_root, const struct btrfs_ioctl_send_args *arg)`. It validates privileges, send flags, protocol version, read-only/dead/dedupe state, send file descriptor access, parent and clone roots, buffer allocation, delalloc flushing, commit-root freshness, then drives `send_subvol()` and final cleanup.

Core state is held in `struct send_ctx`. It stores the output file and offset, command buffer and protocol version, send/parent/clone roots, compare-tree paths, relocation generation, current inode metadata, reference lists, path/name caches, backref cache, directory-created and delayed-utimes caches, pending directory move trees, waiting move trees, orphan-directory metadata, current inode page-cache state, and the cached current inode path.

Important helper types include `struct fs_path` for dynamically building normal and reversed paths, `struct clone_root` for allowed clone sources, `struct backref_cache_entry` for leaf-to-root clone backref memoization, `struct pending_dir_move` and `struct waiting_dir_move` for delayed directory renames, `struct orphan_dir_info` for directories that cannot yet be removed, `struct name_cache_entry` for path component lookups, `struct btrfs_inode_info` for extracted inode item fields, `struct recorded_ref` for new/deleted references, and `enum btrfs_compare_tree_result` for tree diff callback results.

Stream construction is centered on `send_header()`, `begin_cmd()`, `tlv_put*()` helpers, `put_data_header()`, `send_cmd()`, and command-specific emitters such as `send_subvol_begin()`, `send_rename()`, `send_link()`, `send_unlink()`, `send_rmdir()`, `send_create_inode()`, `send_truncate()`, `send_chmod()`, `send_chown()`, `send_utimes()`, `send_fileattr()`, `send_set_xattr()`, `send_remove_xattr()`, `send_write()`, `send_clone()`, `send_update_extent()`, `send_fallocate()`, `send_hole()`, `send_encoded_inline_extent()`, `send_encoded_extent()`, and `send_verity()`.

Tree and metadata diffing relies on `full_send_tree()` for parentless sends, `btrfs_compare_trees()` for incremental sends, and `changed_cb()` as the central dispatcher. `changed_inode()`, `changed_ref()`, `changed_xattr()`, `changed_extent()`, and `changed_verity()` translate item-level compare results into stream actions. `finish_inode_if_needed()` closes out pending refs, data ranges, metadata updates, capabilities, fs-verity state, child directory moves, and utimes.

Path and reference resolution are handled by `iterate_inode_ref()`, `iterate_dir_item()`, `get_inode_info()`, `get_first_ref()`, `get_inode_path()`, `get_cur_inode_state()`, `get_cur_path()`, `will_overwrite_ref()`, `did_overwrite_ref()`, `orphanize_inode()`, `process_recorded_refs()`, and the delayed directory move helpers `wait_for_dest_dir_move()`, `wait_for_parent_move()`, `apply_dir_move()`, and `apply_children_dir_moves()`.

Extent data handling uses `find_extent_clone()`, `iterate_backrefs()`, `clone_range()`, `send_write_or_clone()`, `is_extent_unchanged()`, `maybe_send_hole()`, `process_extent()`, and `process_all_extents()`. These paths choose between no-data updates, regular writes, clone commands, fallocate hole punching, zero writes for protocol v1, and encoded writes for compressed extents when allowed.

## Control Flow

`btrfs_ioctl_send()` is the outer control path. It first requires `CAP_SYS_ADMIN`, refuses non-read-only/dead/deduplicating send roots, increments `send_in_progress`, validates clone-source count and flags, initializes `send_ctx`, chooses protocol v1 by default or a requested protocol when `BTRFS_SEND_FLAG_VERSION` is set, opens the destination file, allocates a v1 or v2/v3 send buffer, loads clone-source roots from userspace, optionally loads a parent root, adds the send root as an implicit clone source, sorts clone roots for bsearch, flushes delalloc for all roots used by send, commits stale roots when commit roots lag current roots, then calls `send_subvol()`.

`send_subvol()` optionally emits the stream header, emits a `SUBVOL` or `SNAPSHOT` command with UUID and ctransid metadata, then selects the traversal mode. Without a parent root, `full_send_tree()` walks the send root from `BTRFS_FIRST_FREE_OBJECTID` and treats every item as new. With a parent root, `btrfs_compare_trees()` walks both commit roots in key order, skips shared subtrees by comparing block pointers/generations at internal levels, deep-compares equal leaf items, and calls `changed_cb()` for new, deleted, changed, or same-but-contextually-relevant items.

`changed_cb()` deliberately drops `commit_root_sem` before writing to the output file to avoid deadlock when send and receive operate through a pipe or the output file is on the same filesystem. It first finishes the previous inode if needed, ignores internal free-space/free-inode objects, then dispatches inode items to `changed_inode()`, refs to `changed_ref()`, xattrs to `changed_xattr()`, data extents to `changed_extent()`, and verity descriptor item creation to `changed_verity()`.

Inode processing is stateful across multiple tree items with the same objectid. `changed_inode()` resets current inode state, handles orphan nlink-zero cases, distinguishes new, deleted, changed, and generation-reused inodes, creates new inodes under temporary orphan names, and, for generation reuse, explicitly processes all old refs as deleted and all new refs/xattrs/extents as newly created. `finish_inode_if_needed()` later processes recorded refs, emits remaining holes/data/truncate/chown/chmod/fileattr/verity/capability/utimes commands, updates `send_progress`, and applies child directory moves that were blocked by parent moves.

Reference processing is two-phase. Compare callbacks record new and deleted refs into RB-tree-backed lists so that new refs can be processed before deletions. `process_recorded_refs()` computes the current receiver-visible path, orphanizes colliding inodes when a new ref would overwrite an unprocessed first ref, creates parent directories out of inode order when required, sends link or rename commands, delays directory renames when parent/destination ordering would create loops or path conflicts, sends unlinks for deleted non-directory refs, sends or delays `RMDIR`, and queues parent directory utimes.

Data extent processing first skips symlink extents. Incremental sends call `is_extent_unchanged()` to detect extents equivalent to the parent snapshot even when splits or holes exist. Changed extents try `find_extent_clone()` to find a valid clone source among user-supplied roots plus the send root; if no acceptable clone exists, `send_write_or_clone()` sends regular data or encoded compressed data. `maybe_send_hole()` and `send_hole()` preserve sparse ranges that changed from data to holes, using v2 `FALLOCATE` hole punching when possible or v1 zero writes/update-extent fallback.

The compare algorithm in `btrfs_compare_trees()` holds `commit_root_sem` while walking internal nodes but clones root nodes and leaves so `changed_cb()` can safely run without the semaphore. It periodically releases the semaphore for rescheduling or contention. If block-group relocation commits during traversal, `restart_after_relocation()` reacquires fresh commit-root paths and reclones leaves/root nodes so file extent disk bytenrs and metadata buffers are not stale.

## State and Persistence Behavior

The persistent output of this file is the byte stream written to `arg->send_fd`. Commands are serialized as a stream header followed by `struct btrfs_cmd_header` records with CRC32C over the command buffer and little-endian TLV attributes. Protocol v2 changes `BTRFS_SEND_A_DATA` so its data attribute has no explicit length and must be the final attribute in a command; `send_ctx.put_data` enforces this locally.

No durable kernel metadata is meant to be changed by send, but the implementation temporarily affects in-memory root state through `send_in_progress` counters and may force delalloc flushing and transaction commits before traversal. Root commit freshness matters because send walks commit roots but some operations, such as inode lookup for data reads or verity descriptors, consult current roots.

`send_ctx` contains substantial transient ordering state. `send_progress` models the receiver's replay point and decides whether paths should be resolved from the send root or parent root. `cur_inode_path` caches the receiver-visible path of the current inode. `name_cache`, `backref_cache`, `dir_created_cache`, and `dir_utimes_cache` are bounded or explicitly trimmed LRU caches. RB trees store pending moves, waiting moves, orphan directories, and recorded refs. These structures are fully cleaned in the ioctl exit path, including WARN_ON checks for unexpected remaining directory-move/orphan state after a successful send.

Data reads may instantiate page-cache pages for the current inode. `send_extent_data()` records whether the mapping was initially empty and later truncates page-cache ranges after sending to avoid polluting the cache with send-only reads. `close_current_inode()` finishes any remaining page-cache cleanup and drops the inode reference.

## Dependencies and Integration Points

This file depends on Btrfs core tree, inode, extent, dir-item, file-item, transaction, backref, compression, ioctl, verity, and LRU-cache helpers: `"ctree.h"`, `"backref.h"`, `"locking.h"`, `"disk-io.h"`, `"btrfs_inode.h"`, `"transaction.h"`, `"compression.h"`, `"print-tree.h"`, `"accessors.h"`, `"dir-item.h"`, `"file-item.h"`, `"ioctl.h"`, `"verity.h"`, and `"lru_cache.h"`. Kernel dependencies include file I/O, xattrs, ACL encoding, compat helpers, crc32c, vmalloc, radix tree, fallocate flags, and fs-verity.

The userspace ABI integration point is `struct btrfs_ioctl_send_args` from the Btrfs ioctl layer and the send stream protocol constants declared in `send.h`. Receivers must interpret emitted command IDs and attributes exactly as defined by the protocol version. Clone integration depends on Btrfs backref walking through `iterate_extent_inodes()` and clone-source root UUID/ctransid metadata. Encoded-write integration depends on Btrfs compression mapping and encoded read helpers. Verity integration depends on `btrfs_get_verity_descriptor()` and protocol v3 command support.

The implementation also integrates with filesystem concurrency controls: `root_item_lock` protects root flags and `send_in_progress`, `commit_root_sem` protects commit-root traversal, dedupe activity is rejected to keep readonly roots stable, relocation generation is checked to avoid stale bytenrs, and delalloc/ordered extents are flushed before traversal.

## Risks and Edge Cases

Directory replay ordering is the highest complexity area. Parent-child rename reversals, destination-name conflicts with unrelated delayed moves, overwritten first refs, hard links, deleted-but-nonempty directories, and out-of-order parent creation all rely on `send_progress`, orphan names, and pending/waiting RB trees staying consistent. Regressions here usually produce invalid streams that fail on receive or produce wrong paths.

Clone selection is correctness-sensitive. The code must not clone from data that the receiver has not created yet, from a source range past EOF, from stale relocated bytenrs, from a source whose extent layout diverges inside the requested range, or from an unaligned EOF block that a receiver cannot clone safely. It intentionally falls back to writes in many ambiguous cases.

Protocol-version branching affects receiver compatibility. v1 has a 64 KiB command buffer and lacks fallocate, file attributes, encoded writes, and verity. v2 uses larger buffers and special DATA TLV layout. v3 is conditional on `CONFIG_BTRFS_EXPERIMENTAL` and adds fs-verity. Incorrect `proto_cmd_ok()` checks or buffer sizing can create streams older receivers cannot parse.

The compare traversal must handle block-group relocation and snapshot root-node COW safely while not holding `commit_root_sem` across blocking output writes. Mistakes can deadlock, read stale metadata, or miss changes. The comments explicitly call out dedupe and relocation as reasons for conservative restarts and send exclusion.

Memory and allocation risk is nontrivial: path buffers grow up to `PATH_MAX`, xattr iteration may use `kvmalloc`, v2 buffers are vmalloc-backed and mapped into `send_buf_pages`, clone-source arrays are capped but can still be large, and optional caches must degrade safely on allocation failure. TLV size checks return `-EOVERFLOW` when a command would exceed its buffer.

Rare filesystem states are handled but risky: nlink-zero orphan inodes in readonly snapshots, empty symlink inodes from crash windows, symlink extents that are not inline/uncompressed, parent directories deleted and recreated with the same inode number, clone roots with `received_uuid`, and extents beyond i_size from fallocate.

## Test Signals

Strong test coverage should include full sends and incremental sends with file creates, deletes, hard links, renames, directory parent-child move inversions, overwritten names, delayed `RMDIR`, xattr additions/removals/changes, POSIX ACL zero-length normalization, capabilities, chmod/chown/utimes/fileattr changes, sparse file hole punching, `BTRFS_SEND_FLAG_NO_FILE_DATA`, and omitted stream header/end flags.

Extent tests should cover unchanged split extents, shared extents cloned from parent/user clone roots/send root, compressed encoded writes, inline compressed extents, prealloc extents, holes under `NO_HOLES`, unaligned EOF clone cases, clone-source ranges beyond source i_size, and fallback from clone to write when backref counts are large.

Concurrency and filesystem-state tests should exercise sends while relocation can occur, rejection during dedupe, read-only/dead root checks, delalloc flushing after a subvolume is made read-only, generation reuse of an inode number, orphan nlink-zero inodes, send-to-pipe receive on the same filesystem, and cleanup of `send_in_progress` on all error paths.

Protocol tests should validate v1, v2, and, when built, v3 stream parsing; CRC correctness; the v2 trailing DATA attribute layout; receiver compatibility for `FALLOCATE`, `FILEATTR`, `ENCODED_WRITE`, and `ENABLE_VERITY`; and buffer overflow handling for large compressed extents or xattrs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/send.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/send.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/send.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/send.h` declares the Btrfs send stream wire-format constants and the `btrfs_ioctl_send()` prototype used by the Btrfs ioctl layer. It defines stream magic/version selection, command-buffer size rules, packed stream/TLV header structures, command IDs, attribute IDs, and protocol-version maxima. The source was read as a complete 187-line file for this report.

## Important APIs, Types, and Functions

The only function prototype is `long btrfs_ioctl_send(struct btrfs_root *send_root, const struct btrfs_ioctl_send_args *arg);`, implemented in `send.c`.

Important constants are `BTRFS_SEND_STREAM_MAGIC`, `BTRFS_SEND_STREAM_VERSION`, `BTRFS_SEND_BUF_SIZE_V1`, and `BTRFS_SEND_BUF_SIZE_V2`. `BTRFS_SEND_STREAM_VERSION` is `3` only under `CONFIG_BTRFS_EXPERIMENTAL`; otherwise it is `2`. v1 commands are bounded by a 64 KiB command buffer, while v2 uses an aligned buffer sized for a command header plus compressed extent data.

Packed wire-format structures are `struct btrfs_stream_header` (`magic`, little-endian `version`), `struct btrfs_cmd_header` (`len`, `cmd`, `crc`), and `struct btrfs_tlv_header` (`tlv_type`, `tlv_len`). They are declared packed because their exact byte layout is part of the send-stream ABI.

`enum btrfs_tlv_type` defines local type categories for TLV interpretation: integer widths, binary, string, UUID, and timespec. `enum btrfs_send_cmd` assigns stable numeric command IDs. v1 includes subvolume/snapshot, create, rename/link/unlink/rmdir, xattr, write/clone, truncate/chmod/chown/utimes/end/update-extent. v2 adds fallocate, fileattr, and encoded write. v3 adds enable-verity. The anonymous attribute enum assigns stable IDs for UUIDs, ctransids, inode metadata, xattrs, paths, write data, clone metadata, fallocate mode, file attributes, encoded-write metadata, compression/encryption, and fs-verity descriptor fields.

## Control Flow

This header has no executable control flow. It controls compile-time and ABI flow by constraining which command and attribute IDs are valid for each protocol version. `send.c` uses the version maxima in `proto_cmd_ok()`, uses buffer-size macros while allocating `send_ctx.send_buf`, emits `btrfs_stream_header` through `send_header()`, emits `btrfs_cmd_header` through `begin_cmd()`/`send_cmd()`, and emits `btrfs_tlv_header` through `tlv_put()` and v1 data headers.

The protocol-version boundary also affects runtime feature selection: v1 streams cannot emit fallocate, fileattr, encoded write, or verity commands; v2 can emit encoded compressed data and fallocate hole punching; v3 can emit `BTRFS_SEND_C_ENABLE_VERITY` when experimental support is built.

## State and Persistence Behavior

The file owns no runtime storage. Its packed structures and numeric enums define the persistent byte format written into send streams and later consumed by receivers. Changing command IDs, attribute IDs, field sizes, packing, endianness, or version maxima changes the on-disk/on-pipe ABI for send streams.

`BTRFS_SEND_A_DATA` has special persistence semantics starting with protocol v2: the header includes only the attribute type and the data length is implied by the remaining command length. This is why `send.c` must place DATA last and prevent further TLVs after it.

## Dependencies and Integration Points

The header includes `<linux/types.h>`, `<linux/sizes.h>`, and `<linux/align.h>`, and depends on `BTRFS_MAX_COMPRESSED` and `PAGE_SIZE` being available through the wider Btrfs/kernel include context. It forward declares `struct btrfs_root` and `struct btrfs_ioctl_send_args` to avoid pulling in heavier Btrfs internals.

The primary integration points are the kernel send implementation in `send.c`, the ioctl declarations that define `btrfs_ioctl_send_args` and send flags, and userspace/kernel receive implementations that parse this exact stream format. The command and attribute enums are a cross-version compatibility contract between senders and receivers.

## Risks and Edge Cases

The command and attribute numbers are ABI-stable; reordering or renumbering would break all existing receivers. Adding a new command requires updating version-specific maxima and ensuring `send.c` gates emission through protocol checks. Adding attributes requires receiver compatibility rules, especially if the attribute is mandatory for interpreting command payloads.

Packed structure layout and little-endian fields are critical. Any compiler/layout drift or accidental padding would corrupt stream parsing. The v2 `BTRFS_SEND_A_DATA` exception is easy to mishandle because it does not use the ordinary `struct btrfs_tlv_header` length field.

Buffer-size macros are tied to protocol behavior. v1 assumes no command is larger than 64 KiB. v2 must be large enough for a header plus compressed extent data and page-aligned vmalloc/page mapping used by encoded reads. If `BTRFS_MAX_COMPRESSED` or compression behavior changes, send buffer assumptions need review.

`CONFIG_BTRFS_EXPERIMENTAL` changes the advertised maximum stream version. Builds without it must not emit v3 fs-verity commands even if the code paths compile, and userspace requesting a higher version should be rejected.

## Test Signals

Compile tests should cover builds with and without `CONFIG_BTRFS_EXPERIMENTAL` so `BTRFS_SEND_STREAM_VERSION` and v3 maxima are correct. ABI tests should assert packed structure sizes and command/attribute numeric values. Stream round-trip tests should parse v1 and v2 streams, including v2 DATA attributes without explicit lengths. Feature tests should request unsupported versions and verify `btrfs_ioctl_send()` rejects them, and should verify that fallocate/fileattr/encoded-write/verity commands only appear in compatible stream versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/send.h -->
