# Research Report: subset-b-005731

Work item `subset-b-005731` covers NTFS3 core format, mount, runlist, record, name, xattr, and ACL helpers plus `nullfs` and OCFS2 ACL build/config files. Each section below preserves the source path and is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/ntfs.h -->
# sources/distributed-fs/ceph-client/fs/ntfs3/ntfs.h

## Purpose
`ntfs.h` is the NTFS3 on-disk format contract. It defines the little-endian structures, constants, tags, attribute layouts, index records, reparse buffers, EA records, and security-descriptor fragments that other NTFS3 source files parse and mutate. It intentionally keeps layout assertions close to definitions because most consumers use pointer arithmetic against raw disk buffers.

## Important APIs, Types, and Constants
The central scalar type is `CLST`, a cluster number that is normally 32 bit and optionally 64 bit under `CONFIG_NTFS3_64BIT_CLUSTER`. Sentinel LCNs distinguish sparse, resident, compressed, EOF, and delayed-allocation states. `struct MFT_REF`, `struct NTFS_BOOT`, `struct NTFS_RECORD_HEADER`, and `struct MFT_REC` describe boot sectors and MFT records. Attribute handling is represented by `enum ATTR_TYPE`, `struct ATTRIB`, `struct ATTR_RESIDENT`, `struct ATTR_NONRESIDENT`, and helpers such as `attr_size()`, `attr_ondisk_size()`, `resident_data_ex()`, `attr_name()`, and `attr_run()`. Directory and index formats use `struct NTFS_DE`, `struct INDEX_HDR`, `struct INDEX_BUFFER`, and `struct INDEX_ROOT`, with helpers for first/next entries and VBN storage. Later definitions cover `$Secure`, `$ObjId`, `$Reparse`, WOF compression tags, `REPARSE_DATA_BUFFER`, `EA_INFO`, `EA_FULL`, and minimal Windows security descriptor, ACL, ACE, and SID structures.

## Control Flow and Integration
This header has no standalone execution path; it supplies parsing primitives used by `record.c`, `run.c`, `super.c`, `xattr.c`, directory/index code, log replay, security initialization, and inode loading. The inline helpers gate safe traversal by validating sizes, offsets, and flags before callers dereference variable-length data. Consumers depend on the exact ordering and endian encoding of enums, not just symbolic values.

## State and Persistence Behavior
All defined structures map persistent NTFS metadata: boot sectors, MFT records, resident/nonresident attributes, index buffers, reparse records, EAs, and security descriptors. Helpers expose values without owning persistence; callers mark MFT records, indexes, or inodes dirty after mutation. The fixed `static_assert()` checks protect the disk ABI from compiler layout drift.

## Dependencies and Integration Points
The file depends on Linux endian, block, type, string, and kernel helpers plus NTFS3 `debug.h`. It assumes `SECTOR_SHIFT == 9` and uses NTFS3 pointer helpers such as `Add2Ptr()` and `PtrOffset()`. It is included by `ntfs_fs.h` and almost every NTFS3 implementation unit.

## Risks
The risk surface is high because a wrong size, offset, endian conversion, or sentinel interpretation can corrupt metadata or cause out-of-bounds access while parsing untrusted volumes. The optional 64-bit cluster mode changes ABI-sensitive arithmetic. Reparse and EA structures are variable-length and require caller-side length validation.

## Test Signals
Useful tests mount crafted images with resident and nonresident attributes, sparse/compressed data, large indexes, reparse points, EAs, and NTFS 1.x/3.x metadata. Fuzzing record and index buffers should trip helper validation without crashes. Build coverage should include big-endian and `CONFIG_NTFS3_64BIT_CLUSTER` configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/ntfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/ntfs_fs.h -->
# sources/distributed-fs/ceph-client/fs/ntfs3/ntfs_fs.h

## Purpose
`ntfs_fs.h` is the NTFS3 in-memory subsystem interface. It defines mount options, superblock state, NTFS inode extensions, runlist containers, bitmap/index state, locks, feature flags, and function prototypes exported across NTFS3 implementation files.

## Important APIs, Types, and Constants
`struct ntfs_mount_options` captures parsed mount policy including uid/gid, masks, charset, ACLs, discard, sparse, metadata visibility, Windows-name enforcement, case sensitivity, preallocation, and delayed allocation. `struct runs_tree` stores decoded VCN-to-LCN extents. `struct wnd_bitmap` models free-space bitmaps with an extent tree, free counters, zone reservation, and locking. `struct ntfs_index` tracks index allocation and bitmap runs. `struct ntfs_sb_info` is the main mounted-volume state: cluster and record geometry, flags, MFT information, allocation bitmap, cached volume information, `$Secure`, `$Reparse`, `$ObjId`, compression contexts, mount options, ratelimit state, and procfs state. `struct mft_inode` wraps one MFT record and its buffers; `struct ntfs_inode` embeds a Linux inode and adds MFT subrecord trees, attributes, file runs, directory indexes, delayed allocation runs, flags, and locking.

The file declares cross-module APIs from attribute, attrlist, bitmap, directory, file, frecord, fslog, fsntfs, index, inode, name, record, run, super, upcase, xattr, and compression units. Inline helpers cover run allocation/free, bitmap sizing, NTFS time conversion, cluster/block rounding, feature tests, delay-allocation accounting, reference conversion, buffer cleanup, and nested inode locks.

## Control Flow and Integration
Other NTFS3 files include this header to share the same state objects and locking contracts. Mount initializes `ntfs_sb_info`; inode load initializes `ntfs_inode` and `mft_inode`; file and attribute operations mutate `runs_tree` under the relevant locks; sync and teardown walk the same state to flush metadata and release references.

## State and Persistence Behavior
The structures bridge persistent NTFS metadata with Linux VFS state. `ntfs_sb_info` caches volume geometry, dirty state, `$UpCase`, `$AttrDef`, free-space bitmaps, metadata inode references, and delayed allocation counters. `ntfs_inode` tracks dirty MFT records, attribute lists, file run caches, index state, and WSL or NTFS attribute flags. Inline conversions such as `kernel2nt()` and `nt2kernel()` preserve NTFS 100 ns timestamps.

## Dependencies and Integration Points
It depends on Linux VFS, buffer-head, memory-management, rbtree, rwsem, uid/gid, folio, and block APIs. It includes `ntfs.h`, making the on-disk ABI directly available to all NTFS3 modules. POSIX ACL exports are conditional on `CONFIG_NTFS3_FS_POSIX_ACL`.

## Risks
The primary risks are lock-order mistakes, stale run caches, delayed-allocation accounting drift, incorrect dirty propagation, and mismatches between 32-bit and 64-bit cluster builds. Because many helpers are inline, incorrect caller assumptions can spread across the filesystem.

## Test Signals
Compile with ACL, compression, and 64-bit cluster variants. Exercise mount/remount, statfs free-space accounting with delayed allocation, sparse/compressed max-size decisions, nested directory rename locks, metadata inode teardown, and dirty inode writeback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/ntfs_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/record.c -->
# sources/distributed-fs/ceph-client/fs/ntfs3/record.c

## Purpose
`record.c` manages individual NTFS MFT records. It reads records, validates and enumerates attributes, finds attributes by type/name/id, writes dirty records, formats new records, inserts/removes attributes, resizes resident attributes, and repacks nonresident runlists into an MFT attribute.

## Important APIs and Functions
`mi_get()` allocates, initializes, and reads a standalone `mft_inode`; `mi_put()` clears buffers and frees it. `mi_init()` allocates record memory. `mi_read()` reads an MFT record through `$MFT` runs when mounted, retries after loading missing runs, accepts fixup-repaired records by marking them dirty, and validates `rec->total`. `mi_enum_attr()` is the central record parser and validates record bounds, ordered attribute type codes, resident/nonresident sizes, name offsets, VCN ranges, allocation sizes, compression/sparse extension fields, and volume bounds. `mi_find_attr()` filters enumeration by attribute type, name, and id. `mi_write()` writes dirty buffers and flags `$MFTMirr` updates for mirrored records. `mi_format_new()` prepares a reusable record with a fresh sequence. `mi_insert_attr()`, `mi_remove_attr()`, `mi_resize_attr()`, and `mi_pack_runs()` mutate the record body.

## Control Flow
Reads start with MFT run locking when the volume is mounted. If `ntfs_read_bh()` returns `-ENOENT`, the code loads the containing `$MFT` run range and retries. Attribute enumeration begins at `rec->attr_off`, skips records not marked in-use, and advances by validated aligned sizes until `ATTR_END`. Insertions scan sorted attributes using `compare_attr()` and the `$UpCase` table, make room with `memmove()`, assign a new id, and mark the record dirty. `mi_pack_runs()` temporarily opens maximum room at the end of the record, calls `run_pack()`, and rolls back the gap if packing fails.

## State and Persistence Behavior
`mft_inode::mrec` is the in-memory copy of persistent MFT bytes. `mft_inode::nb` holds buffer heads for writeback. `dirty` controls writeback. Insert/remove/resize update `rec->used`, attribute headers, hardlink counts for indexed name removal, and MFT mirror update flags. `mi_format_new()` preserves or increments sequence numbers to keep file handles stale-safe.

## Dependencies and Integration Points
The code depends on `ntfs_read_bh()`, `ntfs_write_bh()`, `ntfs_get_bh()`, `attr_load_runs_vcn()`, `run_pack()`, `ntfs_cmp_names()`, and inode bad-state marking. It is used by higher-level inode, attrlist, xattr, security, and directory operations.

## Risks
This is a high-risk corruption boundary. Off-by-one validation, overlapping `memmove()` mistakes, bad attribute ordering, or wrong `rec->used` updates can corrupt MFT records. Error handling around fixups and run loading must avoid hiding real corruption.

## Test Signals
Use images with full records, many attributes, named streams, resident/nonresident transitions, fragmented `$MFT`, bad fixups, reused records, and mirrored MFT records. Fuzzing MFT attributes should produce `bad_inode` or clean errors without OOB reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/record.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/run.c -->
# sources/distributed-fs/ceph-client/fs/ntfs3/run.c

## Purpose
`run.c` implements NTFS3 runlists: in-memory arrays mapping virtual cluster numbers to logical cluster numbers or sparse holes, plus packing/unpacking of NTFS mapping-pairs arrays stored in nonresident attributes.

## Important APIs and Functions
`struct ntfs_run` stores `vcn`, `len`, and `lcn`. `run_lookup()` binary-searches a VCN. `run_consolidate()` merges or trims adjacent/overlapping entries. Public helpers include `run_lookup_entry()`, `run_is_mapped_full()`, `run_add_entry()`, `run_truncate_head()`, `run_truncate()`, `run_truncate_around()`, `run_collapse_range()`, `run_insert_range()`, `run_insert_range_da()`, `run_get_entry()`, `run_pack()`, `run_unpack()`, `run_unpack_ex()`, `run_get_highest_vcn()`, `run_clone()`, `run_remove_range()`, `run_len()`, and `run_get_max_vcn()`.

## Control Flow
Mutations first locate the affected VCN range, split existing entries where needed, insert or remove array elements with `memmove()`, and then consolidate around the changed index. `run_add_entry()` handles overlap, sparse/non-sparse transitions, contiguous physical runs, and tail reinsertion. Collapse and insert helpers implement fallocate range operations by shifting VCNs and materializing sparse gaps. `run_pack()` verifies complete coverage of the requested range, encodes each run as NTFS mapping pairs using signed LCN deltas, and terminates with zero. `run_unpack()` decodes length and signed LCN deltas, checks VCN/LCN overflow and volume bitmap bounds, optionally frees clusters via `RUN_DEALLOCATE`, and inserts decoded entries. `run_unpack_ex()` additionally verifies decoded allocated runs are marked used in `$Bitmap`, repairs bitmap state when possible, and marks the volume dirty/error on inconsistency.

## State and Persistence Behavior
`runs_tree` is a cache of persistent mapping pairs. Packed run buffers persist inside nonresident attributes; unpacked arrays are in-memory and may be rebuilt from disk. `run_unpack()` can have persistent side effects when called with `RUN_DEALLOCATE` because it marks decoded clusters free. `run_unpack_ex()` can update the allocation bitmap and MFT zone after detecting mismatches.

## Dependencies and Integration Points
The module depends on kernel overflow helpers, allocation APIs, `wnd_bitmap` operations, `mark_as_free_ex()`, `ntfs_set_state()`, and `ntfs_refresh_zone()`. Attribute allocation, truncation, punch-hole, insert/collapse-range, inode loading, and log replay all depend on this runlist layer.

## Risks
Risks include arithmetic overflow, signed LCN delta sign extension, sparse sentinel confusion, large memory growth, incorrect consolidation across holes, and bitmap repair races. Non-64-bit builds must reject volumes whose runs exceed 32-bit cluster limits.

## Test Signals
Exercise fragmented, sparse, backwards-delta, very large, boundary-length, and malformed mapping pairs. Test fallocate collapse/insert, punch-hole removal, delayed-allocation insertion, MFT-specific oversized runlists, and bitmap inconsistency detection under `NTFS3_CHECK_FREE_CLST`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/run.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/super.c -->
# sources/distributed-fs/ceph-client/fs/ntfs3/super.c

## Purpose
`super.c` owns NTFS3 filesystem registration, fs_context parsing, mount/remount, superblock initialization, procfs volume metadata, sync/unmount, export operations, boot-sector parsing, discard, and module init/exit.

## Important APIs and Functions
Logging helpers `ntfs_printk()` and `ntfs_inode_printk()` rate-limit messages and include device/inode context. `ntfs_set_shared()` and `ntfs_put_shared()` share identical `$UpCase` tables across mounts. Mount option parsing is driven by `ntfs_fs_parameters` and `ntfs_fs_parse_param()`. `ntfs_fs_reconfigure()` validates remount state, charset compatibility, journal replay, and dirty-volume policy. Procfs helpers expose `/proc/fs/ntfs3/<dev>/volinfo` and `label`. Super operations include inode allocation/free, `ntfs_put_super()`, `ntfs_statfs()`, `ntfs_show_options()`, `ntfs_shutdown()`, and `ntfs_sync_fs()`. `ntfs_init_from_boot()` parses and validates boot geometry. `ntfs_fill_super()` performs the full mount sequence. `ntfs_unmap_meta()` invalidates block aliases, and `ntfs_discard()` issues aligned discard. `ntfs_init_fs_context()`, `ntfs3_kill_sb()`, `init_ntfs_fs()`, and `exit_ntfs_fs()` integrate with VFS and module lifecycle.

## Control Flow
Mount starts with context allocation and default options, loads NLS, parses the boot sector or alternate boot, and initializes geometry, block size, limits, and a template MFT record. `ntfs_fill_super()` then loads `$Volume`, `$MFTMirr`, `$LogFile` and replays it, enforces dirty-volume read-write policy, loads `$MFT`, initializes `$MFT::$BITMAP`, loads `$Bitmap`, computes the MFT zone, validates `$BadClus`, reads `$AttrDef`, reads and shares `$UpCase`, initializes `$Secure`, `$Extend/$Reparse`, and `$Extend/$ObjId` when available, then loads root and installs procfs. On sync, important metadata inodes are written, volume dirty state is cleared when possible, MFT mirror updates are flushed, and block-device flush is issued when requested.

## State and Persistence Behavior
`ntfs_sb_info` receives persistent geometry, serial number, version, dirty flags, volume label, bitmap state, MFT mirror counts, attribute definitions, EA/reparse limits, and shared upcase table. RW mounts can clear dirty state, update primary boot from a valid alternate boot, write labels via procfs, update `$MFTMirr`, and send discard requests.

## Dependencies and Integration Points
The file integrates with Linux VFS, block devices, fs_context, exportfs, procfs, NLS, slab caches, and NTFS3 modules for log replay, bitmap, security, object id, reparse, inode, index, and label handling.

## Risks
Mount is the trust boundary for untrusted disk images. Geometry validation, fallback boot handling, journal replay policy, dirty-volume gating, shared upcase reference counts, teardown ordering, and MFT bitmap extent merging are sensitive. RW mount after failed replay is explicitly blocked.

## Test Signals
Test clean/dirty volumes, failed and successful journal replay, alternate boot fallback, mismatched sector sizes, huge clusters, unsupported MFT/index sizes, raw-truncated images, bad clusters, remount ro/rw, procfs label writes, statfs delayed-allocation accounting, NFS export handles, discard alignment, and module load/unload with multiple mounts sharing upcase.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/upcase.c -->
# sources/distributed-fs/ceph-client/fs/ntfs3/upcase.c

## Purpose
`upcase.c` provides NTFS name comparison and hashing using the volume's `$UpCase` table. It supports both case-sensitive tie-breaking and case-insensitive ordering required by NTFS directory indexes and dcache operations.

## Important APIs and Functions
`upcase_unicode_char()` maps ASCII lowercase directly to uppercase for a fast path and otherwise indexes the loaded upcase table. `ntfs_cmp_names()` compares two little-endian UTF-16 names. `ntfs_cmp_names_cpu()` compares an in-memory CPU-endian `cpu_str` against a little-endian `le_str`. `ntfs_names_hash()` folds upcased UTF-16 code units into the Linux dcache partial-name hash.

## Control Flow
The comparison helpers first perform direct code-unit comparison unless the caller requested purely case-insensitive comparison. If a direct difference appears while `bothcase` and an upcase table are enabled, control switches to a case-insensitive pass from the current position. If the case-insensitive names compare equal, the saved direct difference becomes the tie-breaker; otherwise the upcased difference decides ordering. This preserves deterministic ordering while avoiding a full second scan in the common case.

## State and Persistence Behavior
The file has no persistent state of its own. It consumes `sbi->upcase`, which is loaded from `$UpCase` during mount and may be shared by `super.c`. Its results affect persistent directory-index ordering and VFS dentry hashing because name lookup, insert, and rename paths rely on these comparisons.

## Dependencies and Integration Points
It depends on `ntfs_fs.h` for NTFS string types and Linux hashing helpers. `record.c` uses `ntfs_cmp_names()` when inserting sorted named attributes. Directory and dentry code use these routines for lookup, case-folded matching, and hash calculation. Mount option `nocase` changes how the dentry operations use the comparison model.

## Risks
The upcase table is indexed by 16-bit code unit; callers must ensure the table is loaded and valid. Incorrect tie-breaking can make directory indexes unsorted or cause duplicate-name behavior differences from Windows. Unicode normalization is not performed here, so tests must match NTFS's code-unit semantics rather than POSIX locale behavior.

## Test Signals
Test ASCII case folding, non-ASCII upcase-table mappings, equal-insensitive but different-sensitive names, prefix ordering, mixed endian inputs, dcache lookup under `nocase`, and directory insertion/search consistency against images created by Windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/upcase.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/xattr.c -->
# sources/distributed-fs/ceph-client/fs/ntfs3/xattr.c

## Purpose
`xattr.c` implements NTFS3 extended attributes, POSIX ACL storage over NTFS EA records, system xattrs for DOS/NTFS attributes and security descriptors, WSL permission xattrs, and VFS xattr handler registration.

## Important APIs and Functions
EA sizing helpers `unpacked_ea_size()` and `packed_ea_size()` interpret NTFS `EA_FULL` entries. `find_ea()` scans an EA list. `ntfs_read_ea()` loads and validates `ATTR_EA_INFO` plus `ATTR_EA`, reading resident data directly or nonresident data through runs. `ntfs_list_ea()`, `ntfs_get_ea()`, and `ntfs_set_ea()` implement EA listing, retrieval, creation, replacement, removal, resizing, and ATTR_EA/ATTR_EA_INFO persistence. Under `CONFIG_NTFS3_FS_POSIX_ACL`, `ntfs_get_acl()`, `ntfs_set_acl()`, and `ntfs_init_acl()` translate POSIX ACLs to named EAs. `ntfs_acl_chmod()` delegates chmod ACL updates. `ntfs_listxattr()`, `ntfs_getxattr()`, and `ntfs_setxattr()` implement VFS xattr entry points. `ntfs_save_wsl_perm()` and `ntfs_get_wsl_perm()` persist Linux uid, gid, mode, and device in `$LXUID`, `$LXGID`, `$LXMOD`, and `$LXDEV`.

## Control Flow
Generic EA operations lock the `ntfs_inode` unless already locked by WSL helpers. `ntfs_set_ea()` reads the existing EA blob with extra capacity, removes an existing matching entry when replacing, appends a new aligned entry when needed, checks packed and unpacked size limits, creates missing EA attributes, resizes `ATTR_EA`, updates resident or nonresident storage, updates `EA_INFO`, toggles `NI_FLAG_EA`, marks parent update when packed size changes, and marks the inode dirty. System xattr dispatch handles `system.dos_attrib`, `system.ntfs_attrib`, `system.ntfs_attrib_be`, and `system.ntfs_security` before falling back to ordinary NTFS EAs.

## State and Persistence Behavior
The code persists EAs in NTFS `ATTR_EA` and summary metadata in `ATTR_EA_INFO`. DOS/NTFS attribute writes update `ni->std_fa` and the standard information attribute. Security xattr writes insert into `$Secure` and update `std_security_id`. WSL permission xattrs can override VFS inode uid/gid/mode on inode load.

## Dependencies and Integration Points
It depends on NTFS attribute lookup/insertion/removal, run loading, VFS ACL/xattr APIs, security descriptor validation, `$Secure` insertion/lookup, and inode dirtying. It is called by VFS inode operations, create paths, setattr/chmod, and inode loading.

## Risks
EA blobs are variable-length untrusted data. Size arithmetic, alignment, packed-size overflow, resident/nonresident transitions, and partial WSL xattr writes are risk points. `ntfs_setxattr()` updates ctime and marks dirty even for some failing paths, so callers should expect metadata churn on attempted writes.

## Test Signals
Test list/get/set/remove xattrs, `XATTR_CREATE` and `XATTR_REPLACE`, large EAs near `$AttrDef` limits, resident to nonresident EA growth, POSIX ACL inheritance and chmod, DOS/NTFS attribute endian variants, security descriptor get/set, WSL permission round trips, forced-shutdown `-EIO`, and corrupted EA list validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nullfs.c -->
# sources/distributed-fs/ceph-client/fs/nullfs.c

## Purpose
`nullfs.c` defines a permanently empty, immutable, kernel-internal filesystem named `nullfs`. It provides a single global superblock instance with an empty root directory and no user mount surface.

## Important APIs and Functions
`nullfs_super_operations` only supplies `simple_statfs`. `nullfs_fs_fill_super()` initializes the superblock geometry, magic, operation tables, xattr/export settings, timestamp granularity, and root inode. `nullfs_fs_get_tree()` returns a singleton tree via `get_tree_single()`. `nullfs_init_fs_context()` marks the context global, not user-mountable, noexec, and nodev. `nullfs_fs_type` exports the filesystem type with `kill_anon_super`.

## Control Flow
The VFS calls `init_fs_context`, which installs `nullfs_fs_context_ops` and flags the filesystem as `SB_NOUSER`. `get_tree` uses the singleton helper and calls `nullfs_fs_fill_super()` on first creation. The fill path allocates one inode, marks it as an empty directory with initialized timestamps, assigns inode number 1, sets `S_IMMUTABLE`, and installs it as `s_root` through `d_make_root()`.

## State and Persistence Behavior
There is no backing store and no persistent metadata. The only filesystem state is the singleton anonymous superblock and immutable empty root inode. There are no xattrs, export operations, write paths, dentries below root, or block-device interactions.

## Dependencies and Integration Points
It depends on Linux fs_context, superblock, simple directory inode, and magic-number helpers. Other kernel code can reference `nullfs_fs_type` as an internal empty filesystem. The `SB_NOUSER`, `SB_I_NOEXEC`, and `SB_I_NODEV` flags keep the instance constrained.

## Risks
The fill path leaks the allocated inode if `d_make_root()` fails only in the normal VFS sense: `d_make_root()` consumes and drops the inode on failure. The main behavioral risk is accidental expansion of a deliberately empty singleton into a mountable or writable filesystem without adding isolation and lifecycle design.

## Test Signals
Build coverage should verify the exported `nullfs_fs_type`. Runtime checks should assert a singleton tree, root inode number 1, directory mode, immutable flag, no xattrs, empty readdir behavior, `simple_statfs`, no user mounts, and correct teardown through `kill_anon_super`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nullfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/Kconfig -->
# sources/distributed-fs/ceph-client/fs/ocfs2/Kconfig

## Purpose
`fs/ocfs2/Kconfig` exposes OCFS2 filesystem build options and their dependencies. It controls whether the shared-disk cluster filesystem, kernel O2CB stack, userspace DLM stack, statistics, mask logging, and expensive debug checks are built.

## Important Options
`OCFS2_FS` is the main tristate and depends on `INET`, `SYSFS`, and `CONFIGFS_FS`; it selects `BUFFER_HEAD`, `JBD2`, `CRC32`, `QUOTA`, `QUOTA_TREE`, `FS_POSIX_ACL`, and `LEGACY_DIRECT_IO`. `OCFS2_FS_O2CB` enables the kernelspace OCFS2 Cluster Base stack and depends on `OCFS2_FS`. `OCFS2_FS_USERSPACE_CLUSTER` enables userspace clustering with the kernel DLM and depends on `OCFS2_FS && DLM`. `OCFS2_FS_STATS` depends on `OCFS2_FS && DEBUG_FS`. `OCFS2_DEBUG_MASKLOG` enables sysfs masklog controls. `OCFS2_DEBUG_FS` enables expensive consistency checks for debugging.

## Control Flow and Integration
These symbols drive `fs/ocfs2/Makefile` object inclusion. The main filesystem object and stack glue are built with `OCFS2_FS`; O2CB and userspace stack modules are conditional; DLM and cluster subdirectories depend on selected clustering options. The selected features also make POSIX ACL and quota code available to source files such as `acl.c`.

## State and Persistence Behavior
Kconfig has no runtime state, but it changes the compiled behavior of persistent OCFS2 mounts. Enabling ACL and quota selections affects interpretation and persistence of inode xattrs and quota metadata. Debug options can expose logging controls and add consistency-check behavior.

## Dependencies and Integration Points
The dependency graph connects OCFS2 to networking, sysfs, configfs, buffer heads, journaling, CRC32, quotas, ACLs, direct I/O compatibility, debugfs, and DLM. User documentation points to ocfs2-tools, the project page, and kernel filesystem documentation.

## Risks
Misconfigured dependencies can produce partial cluster-stack builds or missing runtime tooling expectations. Default-enabled debug mask logging can increase kernel size. Expensive checks are correctly default-off because they can reduce filesystem performance.

## Test Signals
Validate allmodconfig and modular builds for main OCFS2, O2CB, userspace cluster, stats, masklog, and debug combinations. Confirm Makefile object selection matches Kconfig symbols and that ACL/quota code compiles because `OCFS2_FS` selects the required infrastructure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/Makefile -->
# sources/distributed-fs/ceph-client/fs/ocfs2/Makefile

## Purpose
`fs/ocfs2/Makefile` defines how OCFS2 kernel objects are composed from core filesystem, stack glue, clustering backends, DLM, and subdirectories. It maps the Kconfig symbols to concrete object files.

## Important Build Targets
`obj-$(CONFIG_OCFS2_FS)` builds `ocfs2.o` and `ocfs2_stackglue.o`. `obj-$(CONFIG_OCFS2_FS_O2CB)` builds `ocfs2_stack_o2cb.o`. `obj-$(CONFIG_OCFS2_FS_USERSPACE_CLUSTER)` builds `ocfs2_stack_user.o`. `ocfs2-objs` is the main composite object and includes allocation, address-space operations, block checks, buffer-head I/O, dcache, directory, DLM glue, export, extent maps, file, heartbeat, inode, ioctl, journal, local allocation, locks, mmap, namei, refcounting, reservations, extent moving, resize, slot map, suballocation, superblock, symlink, sysfile, uptodate, local/global quota, xattr, ACL, and filecheck support. Subdirectories `dlmfs/`, `cluster/`, and `dlm/` are included based on the same symbols.

## Control Flow and Integration
The Makefile is consumed by kbuild. `ccflags-y := -I$(src)` lets OCFS2 sources include local headers and cluster headers consistently. The composite object list determines link order inside `ocfs2.o`, which is relevant for init/exit sections and symbol resolution. Conditional stack objects provide runtime-selectable clustering methods described by Kconfig.

## State and Persistence Behavior
No runtime state is stored here, but object inclusion controls whether persistent features are available. Including `acl.o`, `xattr.o`, quota objects, journal code, and stack glue enables ACL/xattr persistence, quota metadata, journal transactions, and clustered coordination.

## Dependencies and Integration Points
This file integrates with `fs/ocfs2/Kconfig`, kbuild composite object rules, and subdirectory builds. `acl.c` is always part of the main OCFS2 object when `CONFIG_OCFS2_FS` is enabled, relying on `FS_POSIX_ACL` selected by Kconfig.

## Risks
Omitting an object from `ocfs2-objs` can silently remove a feature or produce unresolved symbols. Adding code that depends on a conditional stack must align with Kconfig and object selection. The cluster directory is always built with OCFS2 for masklog support, so changes there affect more than O2CB-only builds.

## Test Signals
Run kbuild for built-in and module configurations across `OCFS2_FS`, O2CB, userspace cluster, and DLM combinations. Check generated modules and `nm`/modpost output for expected stack, ACL, xattr, quota, and cluster symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/acl.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/acl.c

## Purpose
`acl.c` implements OCFS2 POSIX ACL conversion, retrieval, update, chmod adjustment, and new-inode ACL inheritance. It stores ACLs as OCFS2 xattrs and coordinates changes through OCFS2 inode locks, xattr semaphores, and journal transactions.

## Important APIs and Functions
`ocfs2_acl_from_xattr()` converts little-endian on-disk `ocfs2_acl_entry` values into a `struct posix_acl`. `ocfs2_acl_to_xattr()` serializes a POSIX ACL back to the OCFS2 xattr format. `ocfs2_get_acl_nolock()` maps ACL type to OCFS2 xattr indexes and reads values through `ocfs2_xattr_get_nolock()`. `ocfs2_acl_set_mode()` updates inode mode and ctime in memory and the dinode, starting a transaction if the caller did not provide one. `ocfs2_set_acl()` writes or removes ACL xattrs and updates the ACL cache. Public entry points are `ocfs2_iop_get_acl()`, `ocfs2_iop_set_acl()`, `ocfs2_acl_chmod()`, and `ocfs2_init_acl()`.

## Control Flow
ACL get rejects RCU lookup, checks the mount POSIX ACL option, takes an OCFS2 inode lock, reads under `ip_xattr_sem`, and releases the buffer and lock. ACL set takes an exclusive inode lock; for access ACLs it calls `posix_acl_update_mode()` and persists the resulting mode before writing the xattr. Chmod reads the existing access ACL, transforms it with `__posix_acl_chmod()`, and stores the result. New inode initialization reads the parent's default ACL when enabled; without one it applies the current umask through `ocfs2_acl_set_mode()`. With a default ACL, it stores a default ACL for directories, creates the access ACL/mode pair, and writes the resulting ACL if required.

## State and Persistence Behavior
ACL values persist in OCFS2 xattrs under access/default ACL indexes. Mode and ctime persist in the dinode through journaled writes. The VFS ACL cache is updated after successful set operations. New inode initialization may persist mode changes even when no ACL xattr is created.

## Dependencies and Integration Points
The file depends on OCFS2 xattr, inode locking, journal, allocation context, dinode, masklog, and POSIX ACL APIs. It is compiled into `ocfs2.o` and declared by `acl.h`; inode operations call `ocfs2_iop_get_acl()` and `ocfs2_iop_set_acl()`.

## Risks
The code must keep distributed inode locks, xattr semaphores, buffer heads, and journal handles balanced. ACL conversion uses the initial user namespace, so idmapped mount handling is constrained. Error paths during `ocfs2_init_acl()` must release ACL references and preserve transaction consistency.

## Test Signals
Test ACL get/set/remove on files and directories, symlink rejection, default ACL inheritance, umask fallback, chmod ACL rewriting, no-ACL mount behavior, journal abort paths, clustered concurrent ACL updates, and xattr allocation requiring `meta_ac` or `data_ac`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/acl.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/acl.h

## Purpose
`acl.h` declares OCFS2 ACL on-disk entry format and the ACL functions used by inode and creation paths. It is the narrow interface between OCFS2 ACL implementation, xattr storage, and inode operation wiring.

## Important APIs and Types
`struct ocfs2_acl_entry` is the serialized little-endian ACL entry with `e_tag`, `e_perm`, and `e_id`. The exported functions are `ocfs2_iop_get_acl()`, `ocfs2_iop_set_acl()`, `ocfs2_acl_chmod()`, and `ocfs2_init_acl()`. `ocfs2_init_acl()` accepts a journal handle, child and parent inodes, child and parent dinode buffers, and optional metadata/data allocation contexts needed when ACL xattr creation grows metadata.

## Control Flow and Integration
Inode operation tables use `ocfs2_iop_get_acl()` and `ocfs2_iop_set_acl()` for VFS ACL hooks. Attribute-change paths call `ocfs2_acl_chmod()` after mode changes. Creation paths call `ocfs2_init_acl()` during mknod/create setup to inherit default ACLs or apply umask mode updates. The implementation in `acl.c` performs locking, xattr reads/writes, and journal updates behind this header.

## State and Persistence Behavior
The header itself has no state. It defines the persistent byte layout of ACL xattr entries, so endian fields and size assumptions must remain compatible with existing OCFS2 volumes. The declared functions persist ACL xattrs, inode modes, and ctime through journaled OCFS2 metadata updates.

## Dependencies and Integration Points
It includes `<linux/posix_acl_xattr.h>` for POSIX ACL definitions and references OCFS2 allocation context and buffer-head types via declarations available in including OCFS2 headers. It is included by `acl.c` and by OCFS2 inode/namei code that wires ACL operations.

## Risks
Changing `struct ocfs2_acl_entry` would be an on-disk format break. Prototype changes ripple into VFS inode operations and creation paths. Because id conversion in `acl.c` uses the initial user namespace, future idmapped behavior would need coordinated header and implementation changes.

## Test Signals
Build checks should cover all callers of the declared functions. Runtime tests should verify ACL xattr byte layout compatibility, default ACL inheritance, chmod behavior, and successful creation paths that need allocation contexts for ACL storage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/acl.h -->
