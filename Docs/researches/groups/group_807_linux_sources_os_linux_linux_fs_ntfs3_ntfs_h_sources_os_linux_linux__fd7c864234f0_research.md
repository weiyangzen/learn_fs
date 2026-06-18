# Group Research: group_807_linux_sources_os_linux_linux_fs_ntfs3_ntfs_h_sources_os_linux_linux__fd7c864234f0

Scope checked against `Docs/research_subset_a.md`: all requested files are under `sources/os/linux/linux`, which is included in subset A. I read each listed file completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/ntfs.h -->
# File Research: sources/os/linux/linux/fs/ntfs3/ntfs.h

## Role

Defines NTFS3's on-disk format model: magic values, record layouts, attribute layouts, index records, reparse buffers, EA/security structures, and small helpers for interpreting those packed structures. This header is the low-level contract between NTFS disk bytes and the rest of the Linux `ntfs3` driver.

## Major Contents

- Core constants:
  - `NTFS_NAME_LEN`, `NTFS_LINK_MAX`, LZNT constants, cluster sentinel values such as `SPARSE_LCN`, `RESIDENT_LCN`, `COMPRESSED_LCN`, `DELALLOC_LCN`.
  - MFT record numbers for NTFS metadata files, including `$MFT`, `$MFTMirr`, `$LogFile`, `$Volume`, `$Bitmap`, `$Secure`, `$UpCase`, and `$Extend`.
- On-disk identifiers:
  - `enum ATTR_TYPE` defines NTFS attribute type codes.
  - `enum FILE_ATTRIBUTE` defines Windows/NTFS file attribute bits.
  - `enum NTFS_SIGNATURE` defines record signatures like `FILE`, `INDX`, `BAAD`.
- Fundamental record formats:
  - `struct NTFS_BOOT` is the packed 512-byte boot sector.
  - `struct NTFS_RECORD_HEADER` is the shared fixup-header prefix for FILE/INDX/log records.
  - `struct MFT_REC` models one MFT record.
  - `struct MFT_REF` stores record number plus sequence.
- Attribute formats:
  - `struct ATTRIB` wraps resident and nonresident attribute headers.
  - `struct ATTR_RESIDENT` and `struct ATTR_NONRESIDENT` define the resident/nonresident payload metadata.
  - Helpers include `attr_size`, `attr_ondisk_size`, `attr_name`, `attr_run`, `resident_data_ex`, and flag predicates for sparse/compressed/encrypted/indexed attributes.
- Named NTFS metadata structures:
  - Standard information: `ATTR_STD_INFO`, `ATTR_STD_INFO5`.
  - Attribute list entries: `ATTR_LIST_ENTRY`.
  - File names: `ATTR_FILE_NAME`, `NTFS_DUP_INFO`.
  - Index structures: `NTFS_DE`, `INDEX_HDR`, `INDEX_BUFFER`, `INDEX_ROOT`.
  - Volume info and attribute definition table: `VOLUME_INFO`, `ATTR_DEF_ENTRY`.
  - Object ID, quota, security, reparse, WOF compression, EA, ACL, SID structures.

## Important Invariants

- The file is full of `static_assert`s locking exact structure sizes and offsets. These are essential because most structs directly overlay on-disk bytes.
- NTFS record fixups are expected at either legacy or modern MFT offsets, with `MFTRECORD_FIXUP_OFFSET` currently selecting the older `0x2A` layout.
- Attribute records must distinguish resident and nonresident storage, with nonresident attributes carrying VCN ranges, runlist offsets, allocated/data/valid sizes, and optional total size for sparse/compressed streams.
- Directory/index entries rely on variable-size entries and optional trailing VBN fields, so helpers compute offsets rather than exposing fixed trailing members.
- NTFS time/security/reparse/EA structs are little-endian and intentionally mirror Windows NTFS layouts.

## Dependencies

- Uses Linux kernel endian and type APIs.
- Relies on helper pointer macros from `debug.h`.
- Exposes data structures consumed by nearly every NTFS3 implementation file, especially `record.c`, `run.c`, `super.c`, `xattr.c`, inode, index, and attribute code.

## Notes For Future Work

- This file is schema-critical. Any change must be validated against on-disk compatibility, not just C type safety.
- Several helpers operate on caller-validated buffers. Callers must prove size and bounds before using them.
- `le_cmp()` appears worth extra attention in future review: the name comparison arm uses `!le->name_len` before `memcmp`, which means non-empty names are not compared there. It may be intentional due other ordering checks, but it is surprising.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/ntfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/ntfs_fs.h -->
# File Research: sources/os/linux/linux/fs/ntfs3/ntfs_fs.h

## Role

Central private header for the NTFS3 driver. It defines in-memory superblock/inode/run/index state and declares the cross-file API surface for attributes, records, directories, indexes, bitmaps, security, xattrs, compression, logging, and mount helpers.

## Major Contents

- NTFS3-specific error codes:
  - `E_NTFS_FIXUP`, `E_NTFS_NONRESIDENT`, `E_NTFS_NOTALIGNED`, `E_NTFS_CORRUPT`.
- Mount and runtime flags:
  - Superblock flags include discard shutdown, log replay, MFT mirror update, and journal-replay-needed states.
  - Inode flags include external compression format bits, deduplication, EA presence, directory/resident state, and parent-update requirements.
- Mount options:
  - `struct ntfs_mount_options` stores NLS, uid/gid, masks, ACL/name/display/hidden/sparse/prealloc/nocase/delalloc settings.
- Core in-memory structures:
  - `struct runs_tree`: array-backed VCN-to-LCN run map.
  - `struct wnd_bitmap`: free-space bitmap window/tree state.
  - `struct ntfs_index`: per-index runlists, locking, and block geometry.
  - `struct ntfs_sb_info`: NTFS3 superblock state, including cluster geometry, MFT state, volume info, security/reparse/object-id indexes, compression contexts, options, and procfs entry.
  - `struct mft_inode`: one loaded MFT record with buffers.
  - `struct ntfs_inode`: Linux inode extension, including MFT record tree, resident/file/dir union, attribute list, valid size, flags, and locking.
  - `struct ntfs_fnd`: index-search path state.
- Declarations:
  - Attribute manipulation from `attrib.c`.
  - Attribute-list handling from `attrlist.c`.
  - Directory/name conversion/search.
  - File operations, inode operations, MFT record operations.
  - Runlist operations from `run.c`.
  - Bitmap, superblock, security, reparse, objid, index, xattr, ACL, and compression functions.
- Inline helpers:
  - Run initialization/free/close.
  - NTFS timestamp conversion.
  - Superblock and inode container helpers.
  - Delayed-allocation counters.
  - Cluster/block alignment conversions.
  - Inode state predicates for compressed/sparse/dedup/encrypted/resident.
  - Buffer release and lock helpers.

## Important Invariants

- `struct ntfs_inode` embeds `struct inode` as `vfs_inode`; `ntfs_i()` is the canonical container conversion.
- NTFS inodes may span multiple MFT records; `mi_tree` and attribute lists represent overflow/subrecord state.
- File and directory state share a union, so callers must honor inode kind flags before accessing `ni->dir` or `ni->file`.
- Runlists are protected by `run_lock` in paths that may load or mutate mappings concurrently.
- MFT, security, reparse, and object-id metadata have nested lock classes to satisfy lockdep ordering.
- Delayed allocation counters are atomic and adapt to 32-bit vs 64-bit cluster builds.

## Dependencies

- Pulls in most kernel filesystem, buffer, page, rwsem, mutex, rbtree, and ID-mapping APIs.
- Depends on `ntfs.h` for on-disk format definitions.
- Acts as the compile-time coupling point for the NTFS3 implementation files.

## Notes For Future Work

- The header is broad and monolithic by design; changes here have large blast radius.
- `runs_tree` still has a TODO to use an rb-tree instead of an array. `run.c` also comments on array/memmove costs.
- Any new operation should respect the existing lock nesting helpers and avoid bypassing `ni_lock`, `run_lock`, and bitmap locks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/ntfs_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/record.c -->
# File Research: sources/os/linux/linux/fs/ntfs3/record.c

## Role

Implements low-level MFT record lifecycle and in-record attribute manipulation. It allocates, reads, validates, formats, writes, inserts, removes, resizes, and repacks attributes inside one `struct mft_inode`.

## Major Functions

- `compare_attr()`: orders attributes by type and name using the upcase table.
- `mi_new_attt_id()`: allocates an unused attribute ID, reusing gaps when the record's next ID reaches high values.
- `mi_get()` / `mi_put()` / `mi_init()` / `mi_clear()`:
  - Allocate, initialize, read, and free `mft_inode` instances.
- `mi_read()`:
  - Reads one MFT record through `$MFT` run mappings.
  - Handles missing loaded runs by loading more `$MFT` runs and retrying.
  - Treats fixup failure specially by marking the record dirty but allowing continuation.
  - Verifies `rec->total` matches `sbi->record_size`.
- `mi_enum_attr()`:
  - Enumerates attributes in an MFT record and performs extensive bounds/format validation.
  - Validates used/total boundaries, alignment, attribute ordering, resident/nonresident sizes, VCN ranges, run offsets, names, alloc/data/valid/total sizes, compression/sparse rules, and volume bounds.
  - Marks the inode bad if corruption is detected.
- `mi_find_attr()`:
  - Finds an attribute by type, name, and optional ID.
- `mi_write()`:
  - Writes dirty MFT record buffers and flags `$MFTMirr` updates for mirrored records.
- `mi_format_new()`:
  - Initializes a new/reused MFT record from `sbi->new_rec`, preserving or generating sequence numbers.
- `mi_insert_attr()`:
  - Inserts a new attribute in sorted position, assigns an ID, shifts the record tail, and marks dirty.
- `mi_remove_attr()`:
  - Removes an attribute, shifts the tail, updates hard-link count for indexed file-name attributes, and marks dirty.
- `mi_resize_attr()`:
  - Grows or shrinks an attribute in-place by aligned bytes, shifting trailing attributes.
- `mi_pack_runs()`:
  - Re-packs a nonresident attribute's mapping pairs into available record space, preserving the record if packing fails.

## Important Invariants

- MFT records must have `rec->total == sbi->record_size` after reading.
- Attribute enumeration enforces increasing attribute type order.
- Attribute sizes and offsets must be 8-byte aligned and contained within `rec->used`.
- Resident data must fit between `data_off` and attribute size.
- Nonresident attributes must have valid `svcn <= evcn + 1`, `valid_size <= data_size <= alloc_size`, cluster-aligned allocation sizes, and acceptable `total_size` rules for sparse/compressed streams.
- Insertion/removal/resizing depends on `memmove` over validated in-record boundaries.

## Dependencies

- Uses `ntfs_read_bh`, `ntfs_write_bh`, `ntfs_get_bh`, `attr_load_runs_vcn`, and `run_pack`.
- Consumes on-disk structures from `ntfs.h` and in-memory state from `ntfs_fs.h`.
- Cooperates with `$MFT` run locking during reads and formatting.

## Notes For Future Work

- `mi_enum_attr()` is a central corruption boundary. Bugs here can turn malformed disk bytes into unsafe pointer arithmetic elsewhere.
- `mi_read()` allows `-E_NTFS_FIXUP` to proceed with `mi->dirty = true`; this behavior should remain paired with a clear understanding of NTFS fixup recovery semantics.
- Attribute insertion rejects duplicate non-indexed attributes with same type/name, but allows indexed duplicates.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/record.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/run.c -->
# File Research: sources/os/linux/linux/fs/ntfs3/run.c

## Role

Implements NTFS runlist management. A runlist maps virtual clusters in a file to logical clusters on disk, including sparse extents. This file handles lookup, insertion, consolidation, truncation, collapse/insert range, packing into NTFS mapping-pair format, unpacking from disk, cloning, and range removal.

## Major Functions

- Internal helpers:
  - `run_lookup()`: binary-searches the run array for a VCN and returns either containing index or insertion index.
  - `run_consolidate()`: merges adjacent or overlapping compatible runs.
  - `run_packed_size()`, `run_pack_s64()`, `run_unpack_s64()`: endian-aware mapping-pair integer encoding helpers.
- Lookup and coverage:
  - `run_lookup_entry()`: returns LCN/length/index for a VCN.
  - `run_get_entry()`: returns the Nth run.
  - `run_is_mapped_full()`: checks whether a VCN range is continuously mapped.
  - `run_len()` and `run_get_max_vcn()`: summarize run coverage.
- Mutations:
  - `run_add_entry()`: inserts or overlays a run, splitting existing runs when sparse/non-sparse or LCN continuity differs.
  - `run_truncate_head()`, `run_truncate()`, `run_truncate_around()`: drop mappings before/after positions and manage memory.
  - `run_collapse_range()`: removes a logical VCN range for fallocate collapse.
  - `run_insert_range()` and `run_insert_range_da()`: inserts sparse VCN space for fallocate insert, including delayed-allocation variant.
  - `run_remove_range()`: removes a range and reports removed length.
  - `run_clone()`: copies a run tree.
- NTFS mapping-pair encoding:
  - `run_pack()`: serializes a contiguous run coverage range into NTFS packed mapping pairs.
  - `run_unpack()`: parses packed mapping pairs, checks overflows, sparse encodings, 32-bit cluster build limits, and volume bounds.
  - `run_unpack_ex()`: optionally validates unpacked allocated clusters against the volume bitmap and repairs/marks dirty when mismatches are detected.
  - `run_get_highest_vcn()`: parses mapping pairs enough to compute highest VCN, used during log replay.

## Important Invariants

- `runs_tree` is sorted by VCN and represented as a contiguous array.
- Adjacent extents are consolidated when sparse status and physical LCN continuity match.
- Sparse runs use `SPARSE_LCN`; physical runs must stay within the volume bitmap range.
- On 32-bit cluster builds, VCN/LCN ranges beyond 2^32 clusters are rejected.
- Mapping-pair unpacking treats length as unsigned and LCN delta as signed, matching NTFS disk format.
- `run_unpack()` can also be called in validation-only mode with `run == NULL`, or cluster-freeing mode with `RUN_DEALLOCATE`.

## Dependencies

- Uses kernel allocation, overflow, endian, log2 helpers, and block APIs.
- Calls bitmap/free-space helpers through `mark_as_free_ex`, `wnd_is_used`, `wnd_set_used_safe`, `wnd_zone_set`, and `ntfs_refresh_zone`.
- Relies on NTFS constants and `runs_tree` definitions from `ntfs.h` and `ntfs_fs.h`.

## Notes For Future Work

- The file explicitly notes array/memmove costs and a future extents-tree direction.
- `run_add_entry()` is complex because it overlays arbitrary ranges and may recursively add tails. It is a key area for edge-case tests.
- `run_remove_range()` splitting a middle physical run adds the tail with the original `r->lcn`; future review should verify whether that should include the removed offset when used for physical mappings.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/run.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/super.c -->
# File Research: sources/os/linux/linux/fs/ntfs3/super.c

## Role

Implements NTFS3 filesystem registration, mount/remount context handling, boot-sector parsing, superblock initialization/teardown, procfs exposure, statfs/show-options/sync/shutdown, NFS export hooks, metadata cache cleanup, discard, and module init/exit.

## Major Areas

- Logging:
  - `ntfs_printk()` and `ntfs_inode_printk()` provide rate-limited filesystem/inode diagnostics.
- Shared upcase table:
  - `ntfs_set_shared()` and `ntfs_put_shared()` deduplicate identical `$UpCase` tables across mounted volumes.
- Mount options:
  - `ntfs_fs_parameters[]` accepts uid/gid/masks, immutable, discard, force, sparse, nohidden, hide-dot-files, Windows names, showmeta, ACL, iocharset, prealloc, nocase, and delalloc.
  - `ntfs_fs_parse_param()` parses and validates parameters.
  - `ntfs_fs_reconfigure()` handles remount, with checks for unreplayed journal, dirty volume, and iocharset consistency.
- Procfs:
  - Creates `/proc/fs/ntfs3/<dev>/volinfo` and `label`.
  - Allows label writes through `ntfs_set_label()` on writable mounts.
- Inode cache and super operations:
  - `ntfs_alloc_inode()`, `ntfs_free_inode()`, `init_once()`.
  - `ntfs_sops` wires allocation, eviction, put_super, statfs, show_options, shutdown, sync, and write_inode.
- Teardown:
  - `ntfs3_put_sbi()` closes bitmaps, drops metadata inodes, updates MFT mirror, clears indexes.
  - `ntfs3_free_sbi()` frees allocated tables, compression contexts, shared upcase, and superblock state.
  - `ntfs_put_super()` clears dirty state when possible and releases options.
- Sync/stat/export:
  - `ntfs_statfs()` reports cluster counts adjusted for delayed allocation.
  - `ntfs_sync_fs()` writes metadata inodes, clears dirty state if successful, updates MFT mirror, and flushes block device.
  - NFS export hooks reconstruct inodes from MFT reference/generation.
- Boot parsing:
  - `ntfs_init_from_boot()` reads primary boot sector, falls back to alternative boot, validates NTFS signature, sector/cluster sizes, MFT locations, MFT/index record sizes, volume size, 32-bit cluster limits, and initializes geometry/maxbytes/MFT-zone/new-record template.
- Mount body:
  - `ntfs_fill_super()` loads `$Volume`, `$MFTMirr`, `$LogFile`, replays log, enforces dirty-volume policy, loads `$MFT`, initializes MFT bitmap and volume bitmap, handles `$BadClus`, reads `$AttrDef`, reads and shares `$UpCase`, initializes `$Secure`, `$Extend`, `$Reparse`, `$ObjId`, then loads root.
  - Updates primary boot from valid alternative boot when appropriate.
- Discard and metadata unmap:
  - `ntfs_unmap_meta()` cleans block-device aliases over metadata ranges.
  - `ntfs_discard()` aligns to device discard granularity and issues trim when enabled.
- Module registration:
  - `ntfs_init_fs_context()`, `ntfs3_kill_sb()`, `ntfs_fs_type`, `init_ntfs_fs()`, `exit_ntfs_fs()`.

## Important Invariants

- RW mount is denied if log replay is required but cannot be completed.
- Dirty volumes require `force` for RW mount.
- Boot-derived cluster size must be at least media sector size.
- MFT and index record sizes must be power-of-two, sector-sized or larger, and no more than 4096 bytes.
- `$Bitmap` must be large enough for all volume clusters.
- `$UpCase` must be exactly 65536 UTF-16 entries.
- The root inode must load and have inode operations before `s_root` is installed.
- `fc->s_fs_info` ownership is transferred through fs context and kill-super paths; option pointers are swapped on reconfigure.

## Dependencies

- Linux fs context, block device, procfs, seq_file, exportfs, NLS, module, statfs, buffer-head APIs.
- NTFS3 internal metadata loaders from inode, fsntfs, index, bitmap, security, objid, reparse, xattr, and logging code.

## Notes For Future Work

- Mount sequencing is critical: `$Volume` before `$LogFile`, `$MFT` before bitmaps, `$UpCase` before case-sensitive operations, and security/extend metadata before normal root use.
- The alternative boot repair path writes block 0 after successful root load; tests around read-only, fake boot sectors, and partial failure would be valuable.
- `ntfs_discard()` caches `-EOPNOTSUPP` by setting `NTFS_FLAGS_NODISCARD`, avoiding repeated unsupported trim attempts.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/upcase.c -->
# File Research: sources/os/linux/linux/fs/ntfs3/upcase.c

## Role

Provides NTFS name comparison and hashing using the volume `$UpCase` table. This supports NTFS case-insensitive matching and dentry hashing.

## Major Functions

- `upcase_unicode_char()`:
  - Fast-paths ASCII lowercase to uppercase.
  - Uses the loaded NTFS upcase table for other code units.
- `ntfs_cmp_names()`:
  - Compares two little-endian UTF-16 names.
  - Supports case-sensitive first comparison with case-insensitive fallback when `bothcase` is set.
  - Supports fully case-insensitive comparison when requested.
- `ntfs_cmp_names_cpu()`:
  - Same logic, but compares a CPU-endian `cpu_str` against a little-endian `le_str`.
- `ntfs_names_hash()`:
  - Applies upcase conversion before feeding characters into Linux `partial_name_hash()`.

## Important Invariants

- Callers must provide a valid upcase table when case-insensitive behavior is needed.
- `bothcase` preserves deterministic ordering by returning the original case-sensitive difference when names are equal case-insensitively.
- Length difference breaks ties after common-prefix comparison.

## Dependencies

- Uses `ntfs_fs.h` for NTFS string types and declarations.
- Uses Linux name hashing helpers.

## Notes For Future Work

- The function label/comment spells `case_insentive`; harmless but repeated.
- This code works at UTF-16 code-unit level, not full Unicode normalization. That matches NTFS upcase-table behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/upcase.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/xattr.c -->
# File Research: sources/os/linux/linux/fs/ntfs3/xattr.c

## Role

Implements NTFS3 extended attributes and xattr handlers, including NTFS EA storage, system xattrs for DOS/NTFS/security attributes, optional POSIX ACL support through EAs, and WSL permission EA compatibility.

## Major Areas

- EA sizing and lookup:
  - `unpacked_ea_size()` and `packed_ea_size()` compute NTFS EA layout sizes.
  - `find_ea()` scans an EA buffer by name.
- EA read/list/get:
  - `ntfs_read_ea()` loads `ATTR_EA_INFO` and `ATTR_EA`, reads resident or nonresident EA data, validates all entries, enforces `$AttrDef` maximums, and marks the volume dirty on inconsistencies.
  - `ntfs_list_ea()` emits xattr names or computes required size.
  - `ntfs_get_ea()` returns a named EA value, supporting size-query semantics and optional external locking.
- EA set/remove:
  - `ntfs_set_ea()` adds, replaces, removes, or no-ops identical EA values.
  - Creates `ATTR_EA_INFO` and `ATTR_EA` if needed.
  - Resizes the EA attribute through `attr_set_size()`.
  - Writes nonresident EA data through run mappings or resident data directly.
  - Updates `NI_FLAG_EA`, parent-update flag, dirty inode state, and optional EA size output.
- POSIX ACL support under `CONFIG_NTFS3_FS_POSIX_ACL`:
  - `ntfs_get_acl()` reads ACL xattrs and caches translated POSIX ACLs.
  - `ntfs_set_acl_ex()` validates symlink/default ACL rules, updates mode for access ACLs, writes ACL xattrs, saves WSL permissions when mode changes, and caches ACLs.
  - `ntfs_set_acl()` and `ntfs_init_acl()` wire VFS ACL operations.
- chmod/list handlers:
  - `ntfs_acl_chmod()` delegates to POSIX ACL chmod when ACLs are enabled.
  - `ntfs_listxattr()` lists NTFS EAs.
- System xattrs:
  - `system.dos_attrib`: one-byte DOS attributes.
  - `system.ntfs_attrib`: little/native u32 file attributes.
  - `system.ntfs_attrib_be`: big-endian u32 file attributes.
  - `system.ntfs_security`: raw NTFS security descriptor by security ID.
- `ntfs_getxattr()`:
  - Handles system xattrs or falls back to NTFS EA lookup.
- `ntfs_setxattr()`:
  - Handles file attribute updates, security descriptor insertion, or generic EA setting.
  - Keeps directory attribute bit consistent with inode mode.
  - For regular files, routes sparse/compressed changes through `ni_new_attr_flags()`.
- WSL compatibility:
  - `ntfs_save_wsl_perm()` writes `$LXUID`, `$LXGID`, `$LXMOD`, and `$LXDEV` for device nodes.
  - `ntfs_get_wsl_perm()` reads those EAs to restore uid/gid/mode/rdev.
- Xattr registration:
  - Exposes a single catch-all xattr handler with empty prefix.

## Important Invariants

- EA names are limited to 255 bytes.
- Packed EA size must fit in 16 bits and total EA size must not exceed `sbi->ea_max_size`.
- `ATTR_EA_INFO` and `ATTR_EA` are managed as a pair.
- EA mutation requires `ni_lock()` unless the caller passes `locked=true`.
- ACL xattrs are not supported on symlinks; default ACLs are only meaningful on directories.
- System NTFS security xattr is only supported for NTFS 3.x-style `$Secure` security IDs.
- Every `ntfs_setxattr()` path updates ctime and marks the inode dirty, even when the specific operation returns an error.

## Dependencies

- Uses NTFS attribute APIs, run APIs, inode dirtying, security descriptor helpers, and POSIX ACL APIs.
- Depends on structures from `ntfs.h` and shared declarations from `ntfs_fs.h`.

## Notes For Future Work

- `ntfs_read_ea()` treats malformed EA metadata as a dirty-volume condition; this is an important fsck/chkdsk signal.
- The catch-all xattr handler means name dispatch security must remain strict inside `ntfs_getxattr()` and `ntfs_setxattr()`.
- WSL permission restore trusts internal `$LX*` EA values if all required entries are present.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nullfs.c -->
# File Research: sources/os/linux/linux/fs/nullfs.c

## Role

Defines a minimal internal Linux filesystem named `nullfs`. It creates a single global, non-user-mountable, permanently empty, immutable directory superblock.

## Major Contents

- `nullfs_super_operations`:
  - Only provides `.statfs = simple_statfs`.
- `nullfs_fs_fill_super()`:
  - Initializes superblock limits, block size, magic, operations, time granularity, and flags.
  - Allocates one inode, converts it to an empty directory, initializes timestamps, assigns inode number 1, marks it immutable, and installs it as root.
- `nullfs_fs_get_tree()`:
  - Uses `get_tree_single()` to enforce a single global instance.
- `nullfs_init_fs_context()`:
  - Sets fs context operations.
  - Marks the context global.
  - Sets `SB_NOUSER`.
  - Sets internal flags `SB_I_NOEXEC | SB_I_NODEV`.
- `nullfs_fs_type`:
  - Registers name `nullfs`, init context, and `kill_anon_super`.

## Important Invariants

- The filesystem is intentionally empty and immutable.
- It is not mountable by userspace due `SB_NOUSER`.
- It is currently single-instance/global.
- Root inode allocation failure returns `-ENOMEM`.

## Dependencies

- Linux superblock/fs_context APIs.
- `NULL_FS_MAGIC`.
- Simple directory/statfs helpers.

## Notes For Future Work

- Comments note it could become userspace-mountable and multi-instance later.
- In `nullfs_fs_fill_super()`, if `d_make_root()` fails it returns `-ENOMEM`; `d_make_root()` consumes the inode on failure, so the usual ownership pattern is preserved.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nullfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/Kconfig -->
# File Research: sources/os/linux/linux/fs/ocfs2/Kconfig

## Role

Declares build-time configuration options for the OCFS2 clustered filesystem and its clustering/debug/statistics features.

## Major Options

- `OCFS2_FS`:
  - Main OCFS2 filesystem support.
  - Depends on `INET`, `SYSFS`, and `CONFIGFS_FS`.
  - Selects buffer heads, JBD2, CRC32, quota support, POSIX ACL filesystem support, and legacy direct I/O.
  - Help text describes OCFS2 as a general-purpose extent-based shared-disk cluster filesystem, with 64-bit inode numbers and extending metadata groups.
- `OCFS2_FS_O2CB`:
  - Kernelspace O2CB clustering support.
  - Depends on `OCFS2_FS`.
  - Defaults to `y`.
  - Runtime selectable.
- `OCFS2_FS_USERSPACE_CLUSTER`:
  - Userspace clustering with fs/dlm.
  - Depends on `OCFS2_FS && DLM`.
  - Defaults to `y`.
  - Runtime selectable.
- `OCFS2_FS_STATS`:
  - Debugfs-backed statistics.
  - Depends on `OCFS2_FS && DEBUG_FS`.
  - Defaults to `y`.
- `OCFS2_DEBUG_MASKLOG`:
  - Extensive masklog logging.
  - Depends on `OCFS2_FS`.
  - Defaults to `y`.
- `OCFS2_DEBUG_FS`:
  - Expensive consistency checks.
  - Depends on `OCFS2_FS`.
  - Defaults to `n`.

## Important Invariants

- POSIX ACL support is selected by the main OCFS2 option, so OCFS2 ACL code is expected to be available when the filesystem is enabled.
- Clustering backend choice is compiled separately but runtime selectable.
- Expensive debug checks are intentionally opt-in.

## Dependencies

- Kernel Kconfig system.
- OCFS2 tooling and docs are referenced in help text.

## Notes For Future Work

- Because `OCFS2_FS_O2CB` and `OCFS2_FS_USERSPACE_CLUSTER` both default to enabled, builds may include both cluster stacks unless downstream configs trim them.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/Makefile -->
# File Research: sources/os/linux/linux/fs/ocfs2/Makefile

## Role

Defines how OCFS2 and its cluster stack components are built.

## Major Contents

- Adds `-I$(src)` to compile flags.
- Builds main objects when `CONFIG_OCFS2_FS` is enabled:
  - `ocfs2.o`
  - `ocfs2_stackglue.o`
- Builds cluster stack modules conditionally:
  - `ocfs2_stack_o2cb.o` for `CONFIG_OCFS2_FS_O2CB`
  - `ocfs2_stack_user.o` for `CONFIG_OCFS2_FS_USERSPACE_CLUSTER`
- `ocfs2-objs` aggregates the main filesystem implementation:
  - Allocation, address-space ops, block checks, buffer-head I/O, dcache, directory, DLM glue, export, extent map, file, heartbeat, inode, ioctl, journal, localalloc, locks, mmap, namei, refcount tree, reservations, move extents, resize, slot map, suballoc, super, symlink, sysfile, uptodate, quota, xattr, ACL, and filecheck objects.
- Adds subdirectories:
  - `dlmfs/`
  - `cluster/`
  - `dlm/` when O2CB is enabled.

## Important Invariants

- `acl.o` is part of the main `ocfs2.o` object list.
- `cluster/` is always built with OCFS2 for masklog support.
- `dlm/` is tied to O2CB kernelspace clustering.

## Dependencies

- Linux kernel kbuild.
- The listed `.o` files correspond to OCFS2 source modules in the same directory and subdirectories.

## Notes For Future Work

- The object list makes clear that ACL support is not isolated as an optional object once OCFS2 is enabled.
- Formatting is legacy kbuild style with tabs/backslash continuations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/acl.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/acl.c

## Role

Implements OCFS2 POSIX ACL conversion, retrieval, setting, chmod updates, and new-inode ACL initialization. ACLs are stored as OCFS2 xattrs and coordinated with OCFS2 inode locks, xattr semaphores, and journal transactions.

## Major Functions

- ACL serialization:
  - `ocfs2_acl_from_xattr()` converts little-endian OCFS2 ACL xattr entries to `struct posix_acl`.
  - `ocfs2_acl_to_xattr()` converts `struct posix_acl` back to OCFS2 xattr format.
- ACL lookup:
  - `ocfs2_get_acl_nolock()` maps ACL type to OCFS2 xattr index, queries xattr size, reads value, and converts it to a POSIX ACL.
- Mode update:
  - `ocfs2_acl_set_mode()` updates inode mode both in memory and on disk.
  - It can read its own inode block and start its own transaction if the caller does not provide them.
  - Journals dinode access, updates ctime, marks fsync transaction state, and dirties the buffer.
- ACL setting:
  - `ocfs2_set_acl()` validates symlink/default ACL rules, serializes ACLs, and writes/removes ACL xattrs either through an existing journal handle or the generic xattr setter.
  - Updates the VFS ACL cache on success.
- VFS inode operations:
  - `ocfs2_iop_set_acl()` obtains an inode lock, updates mode for access ACLs with `posix_acl_update_mode()`, writes the mode to disk, then writes the ACL xattr.
  - `ocfs2_iop_get_acl()` rejects RCU lookup, checks mount ACL option, locks inode, takes `ip_xattr_sem`, reads ACL, and releases locks.
- chmod handling:
  - `ocfs2_acl_chmod()` reads access ACL, applies mode changes with `__posix_acl_chmod()`, then writes the updated ACL.
- New inode initialization:
  - `ocfs2_init_acl()` reads parent default ACL if ACL mount option is enabled.
  - If no inherited ACL exists, applies current umask to mode.
  - If inherited ACL exists, writes default ACL for directories, derives access ACL/mode with `__posix_acl_create()`, persists mode, and writes access ACL when needed.

## Important Invariants

- Symlinks do not support ACL setting/chmod ACL updates.
- Default ACLs only apply to directories; non-directory default ACL removal is a no-op, but setting one returns `-EACCES`.
- ACL xattr names are represented by OCFS2 xattr indexes with empty names.
- Disk mode and in-memory mode are kept synchronized through journaling.
- ACL access paths must coordinate inode cluster locks and `ip_xattr_sem`.
- RCU ACL lookup is unsupported and returns `-ECHILD`.

## Dependencies

- OCFS2 internals: inode locks, dinode buffers, journal access, xattr get/set, allocation contexts, masklog, superblock mount options.
- Linux POSIX ACL helpers and ID mapping through `init_user_ns` / `nop_mnt_idmap`.
- `acl.h` for `struct ocfs2_acl_entry` and prototypes.

## Notes For Future Work

- The file credits ext3 ACL code lineage, so behavior tracks older filesystem ACL conventions.
- The conversion functions use `sizeof(struct posix_acl_entry)` for on-disk entry sizing while casting to `struct ocfs2_acl_entry`; these sizes match the local OCFS2 entry layout expectation.
- `ocfs2_iop_set_acl()` uses `nop_mnt_idmap` in `posix_acl_update_mode()`, so idmapped mount behavior should be considered if OCFS2 idmap support changes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/acl.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/acl.h

## Role

Declares OCFS2 ACL on-disk entry format and ACL helper APIs used by OCFS2 inode/xattr/create/chmod paths.

## Major Contents

- Header guard `OCFS2_ACL_H`.
- Includes `linux/posix_acl_xattr.h`.
- `struct ocfs2_acl_entry`:
  - Little-endian tag, permission, and ID fields.
- Function prototypes:
  - `ocfs2_iop_get_acl()`
  - `ocfs2_iop_set_acl()`
  - `ocfs2_acl_chmod()`
  - `ocfs2_init_acl()`

## Important Invariants

- OCFS2 ACL xattr entries are little-endian on disk.
- Callers pass OCFS2 transaction/buffer/allocation context to `ocfs2_init_acl()` so ACL inheritance can participate in inode creation journaling.

## Dependencies

- Requires POSIX ACL xattr definitions and OCFS2 types declared elsewhere, such as `handle_t`, `ocfs2_alloc_context`, `inode`, and `buffer_head`.

## Notes For Future Work

- This is a small interface header; behavior lives in `acl.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/acl.h -->