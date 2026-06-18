# Group Research: group_1043_linux_stable_sources_os_linux_linux_stable_fs_ntfs_dir_c_sources_os_6f71db68bb67

Subset scope: `Docs/research_subset_a.md`, which includes `sources/os/linux/linux-stable`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/dir.c

## Scope

Implements NTFS directory operations over the `$I30` filename index: directory lookup, `iterate_shared`/readdir, empty-directory checks, open/release state, and directory fsync.

## APIs And Control Flow

- Defines global little-endian `I30[5]` for `$I30`.
- `ntfs_lookup_inode_by_name()` maps the directory MFT record, searches resident `$INDEX_ROOT`, then descends into `$INDEX_ALLOCATION` blocks when required.
- Lookup performs case-sensitive matching first, keeps one allowed case-insensitive match, and handles DOS short-name matches through `struct ntfs_name` so name lookup can avoid dcache aliasing.
- Index allocation descent reads folios, copies one page, applies MST fixups, validates `INDX` blocks, checks VCN and bounds, and reuses a page buffer when the next child VCN is in the same page.
- `ntfs_filldir()` filters DOS namespace, root self references, hidden/system files by mount options, converts Unicode names with the mounted NLS table, and emits `DT_DIR`, `DT_REG`, or reparse-derived type.
- `ntfs_readdir()` emits dot entries, walks the index with `ntfs_index_ctx_get()`, `ntfs_index_walk_down()`, and `ntfs_index_next()`, and stores a resume key in `file->private_data` when userspace stops early.
- Readdir batches MFT record readahead ranges in an rb-tree and submits `page_cache_sync_readahead()` against `$MFT`.
- `ntfs_check_empty_dir()` treats a directory as empty only when `$INDEX_ROOT` has the minimal empty-root size.
- `ntfs_dir_fsync()` flushes parent directory index allocation inodes, this directory’s data, `$BITMAP`, base inode, MFT bitmap, LCN bitmap, `$MFT`, and the block device.
- `ntfs_dir_ops` wires directory VFS methods: seek, read, iterate, fsync, open, release, ioctl, compat ioctl, and leases.

## State And Dependencies

Depends on MFT mapping/search contexts, NTFS name collation, `index.c` traversal, reparse tag lookup, page-cache folios, rb-trees, writeback, and block-device sync/flush helpers.

Key state includes directory `mrec_lock`, `struct ntfs_index_context`, `struct ntfs_file_private` resume keys, mount case/hidden/system flags, upcase tables, NLS mapping, `$INDEX_ROOT`, `$INDEX_ALLOCATION`, and `$BITMAP`.

## Risks And Invariants

- Index entry bounds, key sizes, VCNs, and `INDX` records are corruption-checked and generally fail as `-EIO`.
- Lookup correctness depends on NTFS collation ordering, including breaking at the first key that sorts after the target.
- Only one case-insensitive match is permitted; a second is treated as corruption.
- The copied page buffer avoids racing writeback MST fixup mutation, but assumes an index block does not cross a page boundary.
- Readdir resume state owns an allocated key buffer and must be freed on release or end-of-iteration.
- Directory fsync reaches parent indexes and volume metadata, so lock nesting and inode references are important.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/dir.h -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/dir.h

## Scope

Declares the NTFS directory helper interface.

## APIs And Data Structures

- `struct ntfs_name` carries lookup results for dcache alias handling:
  - `mref`: target MFT reference.
  - `type`: filename namespace, especially DOS short-name handling.
  - `len` and flexible little-endian Unicode `name[]`.
- Exports global `$I30` name as `extern __le16 I30[5]`.
- Declares `ntfs_lookup_inode_by_name()`.
- Declares `ntfs_check_empty_dir()`.

## Dependencies And Invariants

Includes `inode.h`. `struct ntfs_name` is packed and has a flexible array, so callers must allocate enough storage for non-DOS names. `I30` is a global identity optimization, and code often avoids freeing names equal to this global.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/dir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/ea.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/ea.c

## Scope

Implements NTFS extended attributes, Linux xattr handlers, WSL metadata EAs, DOS/NTFS attribute xattrs, and optional POSIX ACL storage.

## APIs And Control Flow

- `ntfs_write_ea()` writes `$EA` or `$EA_INFORMATION` through fake attribute inodes and optionally truncates the target attribute.
- `ntfs_ea_lookup()` scans packed `struct ea_attr` records with size, alignment, next-offset, name, and value bounds validation.
- `ntfs_get_ea()` reads `$EA_INFORMATION`, verifies `ea_query_length`, reads `$EA`, locates the requested name, and returns or copies its value.
- `ntfs_set_ea()` creates, replaces, appends, or removes EAs while maintaining `ea_length`, `ea_query_length`, and `need_ea_count`.
- WSL metadata helpers read/write `$LXUID`, `$LXGID`, `$LXMOD`, and `$LXDEV`.
- `ntfs_listxattr()` emits the Linux xattr name-list format from NTFS EA records.
- `ntfs_getxattr()` supports synthetic `system.dos_attrib`, `system.ntfs_attrib`, and `system.ntfs_attrib_be`, then falls back to real EAs.
- `ntfs_new_attr_flags()` changes sparse/compressed attribute flags for regular files, including resizing non-resident attribute records when compressed-size fields are required.
- `ntfs_setxattr()` mutates synthetic file attributes or delegates ordinary xattrs to `ntfs_set_ea()`.
- `ntfs_xattr_handlers` registers a catch-all empty-prefix handler.
- Under `CONFIG_NTFS_FS_POSIX_ACL`, ACLs are serialized as EAs and cached through VFS ACL helpers; mode changes are also persisted through `$LXMOD`.

## State And Dependencies

Depends on NTFS attribute add/remove/read/truncate/resize helpers, fake attribute inode I/O, POSIX ACL conversion, VFS xattr contracts, inode mode/uid/gid state, and NTFS file attribute flags.

## Risks And Invariants

- `$EA_INFORMATION.ea_query_length` must not exceed the actual `$EA` size.
- EA walking must respect aligned record sizes and `next_entry_offset` to avoid reading past the buffer.
- `ntfs_set_ea()` may remove or rewrite old records before appending replacements, so lower-level write failures can leave partial EA updates.
- Sparse and compressed are mutually exclusive here; changing them on non-empty non-resident files is rejected.
- Ordinary xattr setting updates ctime and marks the inode dirty even if the EA operation fails.
- ACL writes attempt rollback if persisting `$LXMOD` fails.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/ea.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/ea.h -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/ea.h

## Scope

Declares NTFS EA, xattr, WSL metadata, and optional POSIX ACL entry points.

## APIs And Data Structures

- Defines WSL EA write-selection flags: `NTFS_EA_UID`, `NTFS_EA_GID`, `NTFS_EA_MODE`.
- Exports `ntfs_xattr_handlers`.
- Declares WSL EA helpers: `ntfs_ea_set_wsl_not_symlink()`, `ntfs_ea_get_wsl_inode()`, and `ntfs_ea_set_wsl_inode()`.
- Declares `ntfs_listxattr()`.
- With POSIX ACL support, declares `ntfs_get_acl()`, `ntfs_set_acl()`, and `ntfs_init_acl()`.
- Without POSIX ACL support, maps `ntfs_get_acl` and `ntfs_set_acl` to `NULL`.

## Dependencies And Invariants

The flags are local helper masks, not on-disk NTFS constants. Inode-operation tables can use the ACL names unconditionally because the non-ACL build defines them as `NULL`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/ea.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/file.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/file.c

## Scope

Implements NTFS regular-file VFS operations, inode operations for files/symlinks/special nodes, iomap IO, direct IO, mmap preparation, ioctl handling, and fallocate-style range operations.

## APIs And Control Flow

- `ntfs_file_open()` rejects shutdown volumes, checks 32-bit page-cache limits, enables `FMODE_NOWAIT` and `FMODE_CAN_ODIRECT`, then calls `generic_file_open()`.
- `ntfs_trim_prealloc()` trims trailing preallocated hole runs on last close for uncompressed files.
- `ntfs_file_fsync()` writes file data, base inode, parent directory indexes, dirty non-resident named attributes, MFT/LCN bitmaps, `$MFT`, and the block device, then flushes.
- `ntfs_setattr()` handles size changes, generic attribute copying, ACL chmod, readonly-attribute sync, WSL uid/gid/mode EAs, masks, and dirty-volume marking.
- `ntfs_getattr()` fills stat fields including btime, NTFS compressed/encrypted/immutable/append flags, block accounting, and DIO alignment.
- `ntfs_file_llseek()` implements `SEEK_HOLE` and `SEEK_DATA` via iomap.
- `ntfs_file_read_iter()` supports buffered reads and aligned direct reads; compressed direct reads are rejected.
- `ntfs_file_write_iter()` serializes writes, rejects encrypted writes and compressed direct IO, marks the volume dirty, writes via compressed/iomap/direct paths, and rolls back data/initialized size on errors.
- `ntfs_dio_write_iter()` uses iomap direct IO and falls back to buffered writes for `-ENOTBLK`.
- mmap rejects shutdown and compressed files; writable shared mappings extend initialized size before installing NTFS VM ops.
- `ntfs_ioctl()` handles `FS_IOC_SHUTDOWN`, filesystem label get/set, and `FITRIM`.
- Fallocate supports allocate/keep-size, punch-hole, collapse-range, and insert-range with cluster-alignment and cache invalidation constraints.

## State And Dependencies

Depends on NTFS iomap operations, attribute truncate/fallocate/punch/collapse/insert helpers, LCN bitmap trimming, WSL EA helpers, POSIX ACL helpers, reparse tag lookup, discard/flush APIs, and VFS generic file helpers.

Key state includes `data_size`, `initialized_size`, `allocated_size`, runlists, inode mode/flags, mount masks, volume dirty flags, compression/encryption/sparse bits, and cluster counters.

## Risks And Invariants

- Compressed and encrypted files have deliberately limited write, DIO, mmap, and resize support.
- Direct IO requires block-size alignment and updates inode size in end-IO.
- Write error rollback manually restores initialized and data size.
- Fallocate collapse/insert require cluster alignment and cache invalidation before metadata movement.
- Hole punching zeroes partial clusters and frees only full-cluster interior ranges.
- Release-time preallocation trimming assumes no further writes through that file handle.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/index.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/index.c

## Scope

Implements NTFS index B+tree mechanics: context lifetime, validation, lookup, insertion, deletion, split/reparent operations, index allocation block I/O, index bitmap management, filename index insertion/removal, and ordered traversal.

## APIs And Control Flow

- `ntfs_index_entry_inconsistent()` validates entry key/data boundaries and, with a context, validates placement inside the active root or index block.
- `ntfs_index_entry_mark_dirty()` marks resident `$INDEX_ROOT` dirty or defers index-block writeback through `ib_dirty`.
- Context helpers allocate, free, and reinitialize `struct ntfs_index_context`; release writes dirty index blocks and drops index allocation inodes.
- Index block I/O uses raw attribute pread/pwrite with MST fixups and `INDX`/VCN/header consistency checks.
- Entry helpers compute first/next/previous/last entries, duplicate entries, insert/delete via memmove, and manage child VCNs.
- `ntfs_index_lookup()` searches `$INDEX_ROOT`, follows child VCNs through `$INDEX_ALLOCATION`, records parent positions/VCNs, and returns either a found entry or an insertion position.
- Bitmap helpers create `$BITMAP`, set/clear index allocation bits, and find a free index block VCN.
- `ntfs_ir_reparent()` converts a small resident root into a large index by moving root entries into an allocated index block and leaving a root node pointer.
- `ntfs_ie_add()` inserts entries, growing the root, reparenting, or splitting blocks as needed.
- `ntfs_index_add_filename()` builds a filename index entry for directory `$I30`.
- Deletion handles leaf removal, internal-node successor replacement, empty-block removal, parent END-entry reparenting, root leafification, and bitmap clearing.
- `ntfs_index_remove()` retries structural changes until removal completes.
- `ntfs_index_walk_down()` and `ntfs_index_next()` implement ordered traversal for readdir.

## State And Dependencies

Depends on collation helpers, attribute lookup/add/truncate/record movement, attribute-list updates, fake attribute inode I/O, MFT dirty marking, and MST fixups.

Important state includes `struct ntfs_index_context`, `$INDEX_ROOT`, `$INDEX_ALLOCATION`, `$BITMAP`, parent VCN/position stacks, block size, VCN size bits, collation rule, dirty index-block state, and sync-write mode.

## Risks And Invariants

- Parent stack depth is capped by `MAX_PARENT_VCN`.
- Root growth can require adding an attribute list and moving attributes away before retrying.
- Splits allocate bitmap bits, copy tails, promote medians, update parents, and clear newly allocated bits on failure.
- Internal deletion replaces a removed entry with the leftmost successor from the right subtree; growth during replacement can force split and retry.
- Index block writes apply MST fixups before write; sync failure restores fixups.
- `-EAGAIN` is an internal structural retry signal.
- `$INDEX_ROOT` must be resident and `$INDEX_ALLOCATION` non-resident.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/index.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/index.h -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/index.h

## Scope

Declares the public NTFS index interface and the `struct ntfs_index_context` used by lookup, mutation, and traversal.

## APIs And Data Structures

- `VCN_INDEX_ROOT_PARENT` is the sentinel parent VCN for resident `$INDEX_ROOT`.
- `MAX_PARENT_VCN` caps traversal depth and sizes parent stacks.
- `struct ntfs_index_context` stores target inode/name, current entry/data, collation rule, root/block location, resident search context, index block buffer, index allocation inode, parent stacks, block sizing, dirty state, and sync-write state.
- Declares validation, context lifecycle, lookup/traversal, mutation, index allocation access, raw index remove/add, and sync-write APIs.

## Dependencies And Invariants

Depends on NTFS attribute and MFT structures plus VFS types. Callers must release contexts with `ntfs_index_ctx_put()`. Mutated entries must be marked dirty or sync-written before context release.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/index.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/inode.c

## Scope

Central NTFS inode and attribute-inode implementation. Covers VFS inode lookup/initialization, fake attribute/index inodes, mount-time `$MFT` bootstrap, MFT/attribute parsing, extent attachment, writeback, eviction/deletion, mount option reporting, initialized-size extension, MFT record free-space management, and raw pread/pwrite for attribute inodes.

## APIs And Control Flow

- `ntfs_test_inode()` and `ntfs_init_locked_inode()` implement `iget5_locked()` matching/initialization for normal and fake inodes.
- `ntfs_iget()`, `ntfs_attr_iget()`, and `ntfs_index_iget()` obtain normal, attribute, and index inodes.
- `__ntfs_init_inode()` initializes locks, runlists, extent state, index/compression fields, timestamps, names, flags, and lockdep classes.
- `ntfs_read_locked_inode()` loads base MFT records, standard info, attribute lists, WSL EAs, directory index metadata, regular file data attributes, reparse symlinks, extended system-file view indexes, and VFS operations.
- `ntfs_read_locked_attr_inode()` mirrors base inode metadata onto fake attribute inodes and loads resident/non-resident sizing and compression/sparse/encryption state.
- `ntfs_read_locked_index_inode()` validates `$INDEX_ROOT`, loads `$INDEX_ALLOCATION`, verifies `$BITMAP` coverage, and attaches the base inode.
- `ntfs_read_inode_mount()` bootstraps `$MFT` by direct block-device reads before normal MFT page-cache mapping is available, then loads `$MFT/$DATA` mapping pairs extent by extent.
- `ntfs_evict_big_inode()` truncates page cache, deletes unlinked base inodes, commits dirty linked inodes, frees extents, and releases attribute-list/runlist/name/reparse memory.
- `ntfs_show_options()` prints NTFS mount options including uid/gid, masks, charset, case mode, system/hidden handling, error policy, MFT zone, immutable system files, Windows-name checks, discard, sparse disabling, and ACL mode.
- `ntfs_extend_initialized_size()` maps runlists, zeroes gaps for uncompressed non-resident files, optionally syncs zeroed pages, and updates initialized size.
- `ntfs_truncate_vfs()` wraps NTFS attribute truncation under `mrec_lock`.
- `ntfs_inode_sync_standard_information()` updates timestamps and file attributes in `$STANDARD_INFORMATION` without re-dirtying the inode endlessly.
- `ntfs_inode_sync_filename()` updates all parent directory filename index entries with current flags, sizes, reparse tags, and timestamps.
- `__ntfs_write_inode()` writes dirty base and extent MFT records, updates dirty mapping pairs, syncs standard info and filename entries, and resolves MFT record LCNs.
- `ntfs_inode_attach_all_extents()` and `ntfs_extent_inode_open()` load and attach extent MFT records referenced by an attribute list.
- `ntfs_inode_add_attrlist()` builds an in-memory attribute list, frees base-record space if needed, adds `$ATTRIBUTE_LIST`, updates it, and attempts rollback on failure.
- `ntfs_inode_free_space()` moves movable attributes out of the base MFT record while preserving required base-resident attributes.
- `ntfs_inode_attr_pread()` reads fake attribute data from resident MFT memory or non-resident page-cache folios.
- `ntfs_inode_attr_pwrite()` enlarges attributes if needed, writes resident data into the MFT record/page cache, or writes non-resident folios, with optional synchronous bio writes.
- `ntfs_get_locked_folio()` locks an existing folio or submits readahead and reads it.

## State And Dependencies

Depends on almost every NTFS subsystem: MFT mapping/writeback, attribute search/update/truncate, mapping-pair decompression, runlist merge/free, cluster allocation/free, index mutation, EA/WSL metadata, reparse and object-id indexes, iomap zeroing, bitmap files, and block-device IO.

Important state includes NTFS inode flags, VFS mode/timestamps/link count, sequence numbers, runlists, attribute lists, extent arrays, base/fake inode relationships, `mrec_lock`, `runlist.lock`, `extent_lock`, initialized/data/allocated/compressed sizes, MFT record LCN cache, and volume mount options.

## Risks And Invariants

- Normal inodes, fake attribute inodes, index inodes, and extent inodes share structures but have different lifetime and locking rules; `nr_extents == -1` marks fake/extent-attached behavior.
- `$MFT` bootstrap is circular and relies on discovering enough `$MFT/$DATA` mapping information before normal MFT access.
- Attribute-list handling is delicate: entries may point to extent records, rollback must move attributes back, and `$ATTRIBUTE_LIST` itself cannot be casually moved out of the base record.
- Dirty fake attribute inodes are ignored during writeback because real storage is written through the base inode.
- Filename sync touches parent directory indexes and is skipped when the superblock is not active to avoid unmount deadlocks.
- Deleting unlinked base inodes frees non-resident clusters, extent MFT records, and the base MFT record; failures leave inconsistent metadata and are logged.
- Raw synchronous attribute pwrite constructs bios from runlist mappings, so correctness depends on valid runlists and cluster/page offset calculations.
- Corruption generally marks the volume dirty/error and asks for `chkdsk`; `-ENOMEM` is treated as retryable.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/inode.c -->