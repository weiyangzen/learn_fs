# Group Research: group_1049_linux_stable_sources_os_linux_linux_stable_fs_ntfs3_ntfs_h_sources__ba2bc04fb0ae

Scope: `Docs/research_subset_a.md`  
Files read completely: yes

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/ntfs.h -->
# File Research: sources/os/linux/linux-stable/fs/ntfs3/ntfs.h

Purpose: Defines NTFS3 on-disk ABI structures, constants, little-endian enums, and small layout/access helpers used across the driver.

Key contents:
- NTFS core constants: name length/link limits, LZNT compression unit sizes, special LCN markers, predefined MFT record numbers, attribute type values, and DOS/NTFS file attribute flags.
- Packed on-disk structures for the boot sector, MFT record header/body, resident and nonresident attributes, standard information, attribute-list entries, file-name attributes, directory index entries, index headers/buffers/roots, `$Volume`, `$AttrDef`, object-id, quota, security, reparse, EA, ACL, SID, and relative security descriptor data.
- Reparse-point constants and structures for mount points, symlinks, WOF/system compression, cloud tags, and generic reparse buffers.
- Inline helpers for MFT references, record state, attribute size/name/data pointers, directory-entry VBN access, index-entry traversal, and small filename/index utilities.

Important invariants:
- This file is layout sensitive; it uses `static_assert()` heavily to pin exact sizes and offsets for structures consumed from disk.
- `CLST` is 32-bit by default and 64-bit only with `CONFIG_NTFS3_64BIT_CLUSTER`; sparse/resident/compressed/EOF/delalloc sentinel LCNs depend on that type.
- Attribute flags and type enums are stored as little-endian values, so helpers generally convert before arithmetic and comparisons.
- Resident data helpers validate size/offset only in `resident_data_ex()`; raw `resident_data()` and `attr_run()` assume prior validation.
- Index-entry helpers trust the entry-size field except where `hdr_first_de()` and `hdr_next_de()` check header bounds.

Dependencies:
- Included by almost every NTFS3 implementation file through `ntfs_fs.h`.
- Relies on Linux endian/types/build assertions and local pointer helpers from `debug.h`.

Risk notes:
- Any change to fields, packing, or constants can break disk compatibility.
- The `le_cmp()` helper appears intended to compare attribute-list entry names with attributes, but its current `memcmp()` is gated by `!le->name_len`; callers should be checked carefully before relying on it for non-empty names.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/ntfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/ntfs_fs.h -->
# File Research: sources/os/linux/linux-stable/fs/ntfs3/ntfs_fs.h

Purpose: Central NTFS3 in-memory interface. It defines mount/inode/run/index state and declares the cross-file API surface for NTFS3 implementation modules.

Key contents:
- Mount options for ownership, masks, character conversion, sparse/prealloc/discard behavior, case sensitivity, hidden/meta visibility, Windows-name validation, delayed allocation, and forced dirty mounts.
- In-memory extent/run representation with `struct runs_tree` and `RUN_DEALLOCATE`.
- `struct wnd_bitmap` for free-space bitmaps, including window-level free counts, rb-tree extent indexes, zone tracking, and synchronization state.
- `struct ntfs_sb_info` with cluster/block geometry, record/index sizing, MFT state, global cluster bitmap, volume metadata, `$Secure`, `$Reparse`, `$ObjId`, compression contexts, mount options, proc entry, and ratelimited logging state.
- `struct mft_inode` and `struct ntfs_inode`, which embed the base MFT record, VFS inode, valid size, creation time, standard attributes, subrecord tree, directory or file run state, attribute-list state, and NTFS-specific flags.
- Function prototypes for attribute handling, attrlist handling, bit operations, directory/name/file operations, frecord/inode logic, log replay, low-level NTFS I/O/security/reparse/object-id helpers, index handling, runlist handling, superblock helpers, bitmap handling, upcase comparisons, xattrs/ACLs, and compression.

Important invariants:
- `ntfs_inode::ni_lock` has explicit nested lock classes for normal, parent, security, object-id, reparse, and dirty contexts.
- File run state uses `run_lock`; directory index state uses per-index run locks and version counters.
- Delayed allocation is tracked per file and globally through atomic `sbi->used.da`.
- Time conversion uses NTFS 100 ns units with signed arithmetic on decode to support pre-1970 timestamps.
- `is_ntfs3()` gates NTFS 3.x metadata features such as `$Secure`, `$Extend`, `$Reparse`, and `$ObjId`.

Dependencies:
- Includes `ntfs.h` for all on-disk layouts.
- Declares interfaces implemented by `attrib.c`, `attrlist.c`, `bitmap.c`, `dir.c`, `file.c`, `frecord.c`, `fslog.c`, `fsntfs.c`, `index.c`, `inode.c`, `namei.c`, `record.c`, `run.c`, `super.c`, `upcase.c`, `xattr.c`, and compression modules.

Risk notes:
- This header is a high-coupling point; changing structures affects most NTFS3 files.
- Many declared APIs rely on caller-held inode/run/index locks that are not encoded in types.
- The run tree is array-backed with a TODO to use rb-trees; memory growth and fragmentation are controlled by implementation policy in `run.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/ntfs_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/record.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs3/record.c

Purpose: Handles individual MFT record lifecycle, attribute enumeration/validation, attribute insertion/removal/resizing, and repacking of nonresident runlists inside a record.

Key responsibilities:
- Allocates, initializes, reads, writes, formats, and frees `struct mft_inode` through `mi_get()`, `mi_put()`, `mi_init()`, `mi_read()`, `mi_write()`, and `mi_format_new()`.
- Enumerates and validates attributes in an MFT record with `mi_enum_attr()`.
- Finds attributes by type, name, and optional id via `mi_find_attr()`.
- Inserts ordered attributes with `mi_insert_attr()`, assigning ids through `mi_new_attt_id()`.
- Removes attributes with `mi_remove_attr()`, including hard-link decrement handling for indexed file-name attributes.
- Resizes resident attributes and shifts record tail data with `mi_resize_attr()`.
- Rebuilds packed mapping pairs in-place with `mi_pack_runs()`.

Important invariants:
- `mi_read()` accepts fixup failures by marking the record dirty, but rejects wrong `rec->total`.
- `mi_enum_attr()` is the key corruption boundary for record contents: it checks used/total bounds, alignment, ordered attribute types, resident/nonresident header sizes, name/data/run offsets, VCN ordering, valid/data/allocated sizes, compression/sparse total size, cluster alignment, and volume bounds.
- Attribute order is by type and then name collation using the volume upcase table.
- Duplicate non-indexed attributes of the same type/name are rejected during insertion.
- Writes to records below `sbi->mft.recs_mirr` set `NTFS_FLAGS_MFTMIRR` so the mirror can be updated.

Dependencies:
- Uses low-level metadata I/O helpers from `fsntfs.c`.
- Uses run packing from `run.c`.
- Uses name collation from `upcase.c`.
- Uses NTFS inode dirty/error helpers declared in `ntfs_fs.h`.

Risk notes:
- Corruption detected during enumeration calls `_ntfs_bad_inode()` and returns `NULL`, which can look like normal end-of-enumeration to some callers unless they also check inode state.
- `mi_pack_runs()` temporarily opens a maximum gap in the record and must restore tail data on failure.
- `mi_resize_attr()` adjusts `res.data_size` for resident attributes only; nonresident size changes are handled elsewhere.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/record.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/run.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs3/run.c

Purpose: Maintains NTFS runlists, mapping virtual cluster numbers to logical cluster numbers or sparse regions, and converts between in-memory arrays and NTFS packed mapping pairs.

Key responsibilities:
- Binary-searches run arrays with `run_lookup()` and exposes lookup through `run_lookup_entry()`.
- Adds or replaces mapped ranges with `run_add_entry()`, including overlap handling, splitting, tail reinsertion, sparse/real run separation, allocation growth, and consolidation.
- Truncates, trims, removes, collapses, and inserts ranges through `run_truncate()`, `run_truncate_head()`, `run_truncate_around()`, `run_remove_range()`, `run_collapse_range()`, `run_insert_range()`, and `run_insert_range_da()`.
- Reports mapping state with `run_get_entry()`, `run_is_mapped_full()`, `run_len()`, and `run_get_max_vcn()`.
- Packs in-memory runs into NTFS mapping-pair bytes with `run_pack()`.
- Unpacks and validates mapping-pair bytes with `run_unpack()`, optionally checking cluster allocation bitmap consistency with `run_unpack_ex()`.
- Provides `run_get_highest_vcn()` for log replay and `run_clone()` for copying run trees.

Important invariants:
- Runs are sorted by VCN and normalized by `run_consolidate()` after insertion.
- Adjacent sparse runs can merge; adjacent real runs merge only when both VCNs and LCNs are contiguous.
- `run_unpack()` rejects malformed encodings: zero lengths, oversized length/offset fields, truncated buffers, zero LCN deltas for non-sparse runs, VCN overflow, `evcn` overrun, unsupported 64-bit cluster references in 32-bit mode, and LCN ranges outside the volume bitmap.
- `RUN_DEALLOCATE` is a special mode where unpacked real clusters are freed without storing them in a run tree.
- Normal run-tree memory is capped by policy warnings around `NTFS3_RUN_MAX_BYTES`; MFT runs are allowed to exceed that warning path.

Dependencies:
- Uses allocation bitmap APIs to mark/free/check clusters.
- Uses `mark_as_free_ex()`, `ntfs_set_state()`, and MFT-zone refresh logic from other NTFS3 modules.

Risk notes:
- The array-backed run tree can require memmove-heavy operations; comments call this a bottleneck.
- `run_unpack_ex()` can repair bitmap mismatches by marking clusters used and setting the volume error state, so it has both validation and recovery side effects.
- Range insert/collapse operations assume caller-level attribute-size and on-disk persistence handling.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/run.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/super.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs3/super.c

Purpose: Implements NTFS3 filesystem registration, fs_context mount option parsing, superblock initialization/teardown, boot-sector validation, sync/statfs/export operations, procfs volume reporting, discard, and module init/exit.

Key responsibilities:
- Provides ratelimited NTFS3 logging helpers under `CONFIG_PRINTK`.
- Shares identical `$UpCase` tables across mounts using a small global reference-counted table.
- Parses mount options including uid/gid/masks, immutable system files, discard, force, sparse, hidden/meta behavior, Windows-name rules, ACL, iocharset, prealloc, nocase, and delayed allocation.
- Handles remount/reconfigure constraints, including refusing rw remount when journal replay is needed or dirty volume is not forced, and disallowing iocharset changes.
- Creates `/proc/fs/ntfs3/<dev>/volinfo` and writable `label` entries when procfs is enabled.
- Allocates/frees NTFS inodes from `ntfs_inode_cachep`.
- Implements super operations: inode allocation/free, eviction, put_super, statfs, show_options, shutdown, sync_fs, and write_inode.
- Implements NFS export helpers through file handles and parent lookup.
- Validates boot-sector geometry and initializes core sizing in `ntfs_init_from_boot()`, including fallback to the alternative boot sector.
- Mounts in `ntfs_fill_super()` by loading `$Volume`, `$MFTMirr`, `$LogFile`, `$MFT`, `$Bitmap`, `$BadClus`, `$AttrDef`, `$UpCase`, optional NTFS 3.x metadata files, and root.
- Unmaps metadata buffer aliases and issues aligned discard requests.
- Registers/unregisters the `ntfs3` filesystem and initializes bitmap/inode caches.

Important invariants:
- Boot validation checks NTFS signature, sector/cluster sizing, MFT/MFTMirr LCNs, record/index size limits, cluster/media sector compatibility, raw-volume size, 32-bit cluster build limits, and derived maximum file sizes.
- Mount rw is blocked when log replay is required but failed, or when the volume is dirty without `force`.
- `$MFT` bitmap runs from extent records are merged before initializing the MFT bitmap window.
- `$Bitmap` size must cover all volume clusters.
- `$BadClus` real runs are counted and, on rw mounts, forced used in the allocation bitmap.
- `$AttrDef` must start with `ATTR_STD` and is parsed in increasing type order to cache EA and reparse maximum sizes.
- `$UpCase` must be exactly 0x10000 UTF-16 entries and is endian-swapped on big-endian builds.

Dependencies:
- Uses VFS fs_context, block-device, exportfs, NLS, procfs, seq_file, statfs, and module infrastructure.
- Drives initialization of nearly every NTFS3 subsystem declared in `ntfs_fs.h`.

Risk notes:
- Error cleanup is split between `ntfs3_put_sbi()`, `ntfs3_free_sbi()`, `ntfs_put_super()`, fs_context free, and kill_sb; ownership transfer in successful mount paths must remain exact.
- If the alternate boot sector is accepted on rw mount, primary boot may be rewritten after root creation.
- `ntfs_sync_fs()` clears the dirty flag only if metadata writes succeed, then updates MFTMirr and optionally flushes the block device.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/upcase.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs3/upcase.c

Purpose: Provides NTFS Unicode case-folded comparison and hashing helpers using the mounted volume's `$UpCase` table.

Key responsibilities:
- `upcase_unicode_char()` uppercases ASCII `a`-`z` directly and otherwise indexes the `$UpCase` table.
- `ntfs_cmp_names()` compares two little-endian UTF-16 names, supporting case-sensitive, case-insensitive, and `bothcase` tie-breaking behavior.
- `ntfs_cmp_names_cpu()` compares a CPU-endian `struct cpu_str` to a little-endian `struct le_str`.
- `ntfs_names_hash()` feeds upcased UTF-16 code units into Linux `partial_name_hash()`.

Important invariants:
- When `bothcase` and an upcase table are supplied, exact-case differences are remembered as `diff1`, but case-insensitive comparison decides primary ordering; exact-case difference breaks ties.
- With no upcase table, comparisons are raw code-unit comparisons.
- Length difference is returned when common prefixes match.

Dependencies:
- Uses `$UpCase` loaded and possibly shared by `super.c`.
- Used by record/attribute collation, directory lookup, and case-insensitive dentry operations.

Risk notes:
- The helpers operate on UTF-16 code units, not full Unicode scalar/canonical equivalence.
- `upcase_unicode_char()` assumes the upcase table covers all 16-bit input values.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/upcase.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/xattr.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs3/xattr.c

Purpose: Implements NTFS3 extended attributes, special system xattrs, POSIX ACL storage via EAs, and WSL permission/device metadata.

Key responsibilities:
- Defines supported special xattr names: `system.dos_attrib`, `system.ntfs_attrib`, `system.ntfs_attrib_be`, and `system.ntfs_security`.
- Reads and validates packed NTFS EA data through `ntfs_read_ea()`, including EA_INFO/EA pairing, size limits from `$AttrDef`, resident/nonresident reads, and per-entry consistency checks.
- Lists, gets, sets, replaces, and removes NTFS EAs with `ntfs_list_ea()`, `ntfs_get_ea()`, and `ntfs_set_ea()`.
- Creates/deletes `ATTR_EA_INFO` and `ATTR_EA`, resizes EA storage, writes resident or nonresident content, updates EA flags, parent-update flags, and inode dirty state.
- Under `CONFIG_NTFS3_FS_POSIX_ACL`, maps POSIX ACLs to xattrs and implements get/set/init/chmod helpers.
- Implements generic `listxattr`, getxattr, and setxattr dispatch.
- Gets/sets NTFS DOS attributes and full NTFS attributes, preserving directory-bit consistency and invoking `ni_new_attr_flags()` for sparse/compressed regular-file transitions.
- Gets/sets NTFS security descriptors through `$Secure` by security id on NTFS 3.x volumes.
- Saves and restores WSL metadata EAs `$LXUID`, `$LXGID`, `$LXMOD`, and `$LXDEV`.

Important invariants:
- EA names are limited to 255 bytes.
- EA packed size must fit 16 bits and total EA size must not exceed `sbi->ea_max_size`.
- Setting the final EA removes both `ATTR_EA_INFO` and `ATTR_EA` and clears `NI_FLAG_EA`.
- Changes in packed EA size set `NI_FLAG_UPDATE_PARENT`, because parent directory duplicate information may need updating.
- POSIX ACLs are not applied to symlinks; default ACLs are only valid on directories.
- `system.ntfs_security` requires NTFS 3.x and valid relative security descriptors.

Dependencies:
- Uses attribute and run APIs from `attrib.c`/`run.c`, inode and record helpers, `$Secure` helpers, POSIX ACL helpers, and VFS xattr infrastructure.

Risk notes:
- `ntfs_read_ea()` marks the volume dirty on malformed EA data.
- Some getxattr undersized-buffer cases return `-ENODATA` rather than the more typical `-ERANGE`, matching this driver's current behavior.
- `ntfs_setxattr()` updates ctime and marks the inode dirty even when the final operation returns an error.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nullfs.c -->
# File Research: sources/os/linux/linux-stable/fs/nullfs.c

Purpose: Defines a minimal internal `nullfs` filesystem that provides one permanently empty, immutable root directory.

Key responsibilities:
- Supplies `nullfs_super_operations` with `simple_statfs`.
- Fills a single anonymous superblock in `nullfs_fs_fill_super()`, setting maxbytes, block size, magic, super operations, time granularity, and no xattrs/export operations.
- Allocates root inode, initializes it as an empty directory, sets inode number 1, timestamps, and `S_IMMUTABLE`.
- Uses `get_tree_single()` to provide one global instance.
- Initializes fs_context with `fc->global = true`, `SB_NOUSER`, and internal noexec/nodev flags.
- Exposes `struct file_system_type nullfs_fs_type`.

Important invariants:
- The filesystem is not user-mountable (`SB_NOUSER`) and is intended as a single global internal instance.
- Root is empty and immutable by construction.
- `kill_anon_super` tears down the anonymous superblock.

Dependencies:
- Uses simple VFS helpers: `new_inode()`, `make_empty_dir_inode()`, `simple_inode_init_ts()`, `d_make_root()`, `get_tree_single()`, and `kill_anon_super()`.

Risk notes:
- If `d_make_root()` fails, the function returns `-ENOMEM`; `d_make_root()` consumes the inode, so this path relies on VFS ownership semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nullfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/Kconfig

Purpose: Kconfig definitions for building OCFS2 and its clustering/debug options.

Key contents:
- `OCFS2_FS`: tristate main OCFS2 filesystem, depending on `INET`, `SYSFS`, and `CONFIGFS_FS`; selects buffer heads, JBD2, CRC32, quota support, POSIX ACLs, and legacy direct I/O.
- `OCFS2_FS_O2CB`: kernelspace O2CB clustering support, depending on `OCFS2_FS`, default enabled.
- `OCFS2_FS_USERSPACE_CLUSTER`: userspace clustering via fs/dlm, depending on `OCFS2_FS && DLM`, default enabled.
- `OCFS2_FS_STATS`: optional debugfs-backed statistics, depending on `OCFS2_FS && DEBUG_FS`, default enabled.
- `OCFS2_DEBUG_MASKLOG`: optional extensive logging/masklog support, depending on `OCFS2_FS`, default enabled.
- `OCFS2_DEBUG_FS`: optional expensive consistency checks for debugging, default disabled.

Important invariants:
- POSIX ACL support is selected unconditionally by `OCFS2_FS`.
- Both clustering stacks are build-time selectable but described as runtime selectable.
- Expensive debug checks are intentionally opt-in.

Dependencies:
- Coordinates build inclusion with the Makefile and broader kernel options for configfs/sysfs/networking/DLM/debugfs/quota/JBD2.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/Makefile

Purpose: Build rules for OCFS2 core objects, stack glue, optional clustering stacks, and subdirectories.

Key contents:
- Adds local include path with `ccflags-y := -I$(src)`.
- Builds `ocfs2.o` and `ocfs2_stackglue.o` when `CONFIG_OCFS2_FS` is enabled.
- Builds `ocfs2_stack_o2cb.o` under `CONFIG_OCFS2_FS_O2CB`.
- Builds `ocfs2_stack_user.o` under `CONFIG_OCFS2_FS_USERSPACE_CLUSTER`.
- Defines the large `ocfs2-objs` aggregate, including allocation, aops, block checks, buffer I/O, dcache, directories, DLM glue, export, extent map, file, heartbeat, inode, ioctl, journal, localalloc, locks, mmap, namei, refcount tree, reservations, move extents, resize, slot map, suballoc, super, symlink, sysfile, uptodate, local/global quota, xattr, ACL, and filecheck objects.
- Descends into `dlmfs/` and `cluster/` for `CONFIG_OCFS2_FS`; descends into `dlm/` for O2CB.

Important invariants:
- `cluster/` is always built with OCFS2 for masklog support.
- `acl.o` and `xattr.o` are part of the main OCFS2 object when the filesystem is enabled.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/acl.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/acl.c

Purpose: Implements OCFS2 POSIX ACL conversion, get/set inode operations, chmod ACL updates, and new-inode ACL initialization.

Key responsibilities:
- Converts OCFS2 on-disk ACL xattr entries to/from Linux `struct posix_acl` with `ocfs2_acl_from_xattr()` and `ocfs2_acl_to_xattr()`.
- Reads ACL xattrs without taking inode cluster locks in `ocfs2_get_acl_nolock()`, using OCFS2 xattr indexes for access/default ACLs.
- Updates inode mode in memory and on disk through `ocfs2_acl_set_mode()`, optionally starting its own journal transaction and journaling dinode writes.
- Sets ACL xattrs with `ocfs2_set_acl()`, optionally using an existing journal handle and allocation contexts.
- Provides VFS inode operations `ocfs2_iop_get_acl()` and `ocfs2_iop_set_acl()`, taking OCFS2 inode locks and xattr semaphores as needed.
- Updates access ACL after chmod with `ocfs2_acl_chmod()`.
- Initializes ACLs for new inodes in `ocfs2_init_acl()`, inheriting a parent default ACL when present or applying current umask otherwise.

Important invariants:
- Symlinks do not support ACL mutation.
- Default ACLs apply only to directories; setting a default ACL on a non-directory returns `-EACCES` if one is supplied.
- `ocfs2_iop_get_acl()` refuses RCU mode with `-ECHILD`.
- ACL support is gated at runtime by `OCFS2_MOUNT_POSIX_ACL`.
- Mode updates must be journaled to the dinode and update ctime.
- Cached ACLs are updated after successful set operations.

Dependencies:
- Uses OCFS2 xattr APIs, inode locking, journaling, allocation contexts, dinode layout, and masklog error reporting.
- Uses generic POSIX ACL helpers for mode calculation, ACL creation, chmod, and xattr conversion semantics.

Risk notes:
- On-disk ACL entry count is `size / sizeof(struct posix_acl_entry)` without checking for trailing bytes, matching existing code but worth noting for validation expectations.
- `ocfs2_acl_set_mode()` may create and commit its own transaction when callers do not provide one, so callers must understand journaling context and lock state.
- Error paths log with `mlog_errno()` in some mode-update cases but not every ACL/xattr failure.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/acl.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/acl.h

Purpose: Header for OCFS2 ACL on-disk entry layout and ACL operation prototypes.

Key contents:
- Defines `struct ocfs2_acl_entry` with little-endian tag, permission, and id fields.
- Declares VFS-facing ACL operations: `ocfs2_iop_get_acl()` and `ocfs2_iop_set_acl()`.
- Declares internal helpers: `ocfs2_acl_chmod()` and `ocfs2_init_acl()`.

Important invariants:
- On-disk ACL entries are little-endian and converted explicitly in `acl.c`.
- `ocfs2_init_acl()` requires caller-supplied journal handle, inode/parent inode, dinode buffers, and metadata/data allocation contexts.

Dependencies:
- Includes `linux/posix_acl_xattr.h`.
- Function signatures depend on OCFS2 buffer heads and allocation-context types from other OCFS2 headers included by users.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/acl.h -->