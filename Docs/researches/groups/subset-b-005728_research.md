# subset-b-005728 Research Group

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/super.c -->
# sources/distributed-fs/ceph-client/fs/ntfs/super.c

Implements the legacy `ntfs` filesystem module's superblock lifecycle: mount option parsing, boot-sector validation, mount-time volume bootstrap, system-file loading, free-space accounting, sync/unmount behavior, error policy, sysctl/slab/workqueue setup, and filesystem registration. Key APIs include `ntfs_parse_param()`, `ntfs_reconfigure()`, `ntfs_handle_error()`, `ntfs_write_volume_flags()`, `ntfs_write_volume_label()`, `ntfs_fill_super()`, `load_system_files()`, `ntfs_put_super()`, `ntfs_sync_fs()`, `get_nr_free_clusters()`, and module init/exit.

Mount starts with `ntfs_init_fs_context()`, then `ntfs_fill_super()` validates device geometry, reads/parses the boot sector, initializes allocator cursors and VFS superblock fields, constructs `$MFT`, loads required metadata files, creates the root dentry, and queues free-cluster precalculation. Persistent writes include `$Volume` flags, labels, logfile emptying, quota state, inode commits, dirty-bit clearing, and block-device flushes. State includes shared `default_upcase`, volume flags, system inode references, free counters, dirty reservations, and bitmap page counters. Integration spans VFS, block devices, NLS, errseq, NTFS inode/attribute/index/logfile/quota code, sysctl, slabs, and workqueues. Main risks are complex mount unwind paths, dirty/hibernation safety, `$MFTMirr` validation, free-space wait ordering, and clean-bit handling after writeback errors. Test with clean/dirty/hibernated images, remount transitions, bad geometry, logfile/quota failures, volume label writes, statfs, shutdown, and init failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/sysctl.c -->
# sources/distributed-fs/ceph-client/fs/ntfs/sysctl.c

Provides optional debug sysctl registration for the legacy `ntfs` driver when both `DEBUG` and `CONFIG_SYSCTL` are enabled. It defines `ntfs_sysctls[]` for `fs/ntfs/ntfs-debug`, stores the registration handle in `sysctls_root_table`, and exposes `ntfs_sysctl(int add)` to register or unregister the table. It is called by module init/exit in `super.c`. No disk state is touched; runtime state is the sysctl handle and the `debug_msgs` integer. Dependencies are procfs/sysctl and `debug.h`. Risks are lifecycle misuse such as unregistering the wrong handle, though normal module sequencing avoids that. Test debug and non-debug builds, proc visibility, writable debug value behavior, and registration failure unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/sysctl.h -->
# sources/distributed-fs/ceph-client/fs/ntfs/sysctl.h

Declares `ntfs_sysctl(int add)` when `DEBUG && CONFIG_SYSCTL` is active and otherwise supplies an inline success stub. This lets module lifecycle code call sysctl setup unconditionally. It owns no persistent state and only affects compile-time linkage. It integrates `super.c` with the optional implementation in `sysctl.c`. The main risk is assuming a proc entry exists in builds where the stub is selected. Test by compiling both feature branches and confirming link behavior without sysctl dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/sysctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/time.h -->
# sources/distributed-fs/ceph-client/fs/ntfs/time.h

Defines inline conversion between Linux `timespec64` UTC and NTFS little-endian 64-bit 100 ns timestamps since 1601-01-01. `utc2ntfs()` adds `NTFS_TIME_OFFSET`, scales seconds/nanoseconds, and endian-converts. `get_current_ntfs_time()` samples coarse real time. `ntfs2utc()` subtracts the epoch offset and splits seconds/remainder with `div_s64_rem()`. It stores no state, but converted values persist when callers write NTFS metadata timestamps. It integrates with inode metadata and the superblock's `s_time_gran = 100`. Risks include truncation to 100 ns, pre-1970 signed times, and endian correctness. Test known epoch round trips, sub-100 ns truncation, negative times, and big-endian builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/unistr.c -->
# sources/distributed-fs/ceph-client/fs/ntfs/unistr.c

Implements legacy NTFS Unicode comparison, collation, duplication, and NLS/UTF-16 conversion. Important functions are `ntfs_are_names_equal()`, `ntfs_names_are_equal()`, `ntfs_collate_names()`, `ntfs_ucsncmp()`, `ntfs_ucsncasecmp()`, `ntfs_file_compare_values()`, `ntfs_nlstoucs()`, `ntfs_ucstonls()`, and `ntfs_ucsndup()`. Comparisons endian-convert UTF-16 and optionally upcase via the volume table. Conversion uses UTF helpers for UTF-8 or per-character NLS callbacks otherwise. State comes from `vol->nls_map`, `vol->nls_utf8`, `vol->upcase`, and allocated output buffers. It integrates with directory lookup, index collation, volume labels, and file-name attributes. Risks include allocator ownership, invalid character semantics, overlong names, unconvertible characters, and argument ordering for collation validation. Test case sensitivity, invalid characters, max-length names, UTF-8/NLS conversion, embedded NULs, and big-endian behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/unistr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/upcase.c -->
# sources/distributed-fs/ceph-client/fs/ntfs/upcase.c

Generates the default NTFS Unicode upcase table. `generate_default_upcase()` allocates `default_upcase_len` little-endian entries, initializes identity mappings, then applies range delta, duplicate-pair, and explicit-word mapping tables. It is called during mount when the global default table is absent and is later compared with a volume `$UpCase` table for sharing. It writes no disk state; memory is reference-counted by superblock code. Dependencies are endian helpers and NTFS constants. Risks are allocation failure and mapping-table correctness, since wrong mappings break case-insensitive lookup compatibility. Test representative ASCII, Greek, Cyrillic, fullwidth, explicit mappings, identity entries, and fallback when allocation fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/upcase.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/volume.h -->
# sources/distributed-fs/ceph-client/fs/ntfs/volume.h

Defines `struct ntfs_volume`, the legacy driver's in-memory superblock state, plus inline volume flag and accounting helpers. The structure stores mount options, geometry, allocator cursors, system-file inodes, version/flags/label, NLS/upcase state, free counters, dirty cluster reservations, bitmap page counters, and background work. `DEFINE_NVOL_BIT_OPS()` emits flag test/set/clear helpers; other inlines adjust free clusters, MFT records, per-page empty bits, and dirty reservations. State mirrors persistent NTFS metadata but is runtime-owned. It integrates with mount, allocation, statfs, inode, directory, and teardown code. Risks include waiters blocking on `NVolFreeClusterKnown`, accounting underflow masking, and initialization coupling between free-cluster and MFT counters. Test mount defaults, flag toggles, wait/wakeup, statfs with dirty reservations, MFT counter updates, shutdown, and teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/volume.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/Kconfig -->
# sources/distributed-fs/ceph-client/fs/ntfs3/Kconfig

Defines kernel config for `ntfs3`. `NTFS3_FS` is the tristate read-write driver option and selects buffer heads, NLS, and legacy direct I/O. `NTFS3_64BIT_CLUSTER` enables 64-bit cluster numbers on 64-bit builds. `NTFS3_LZX_XPRESS` enables external Windows compression formats. `NTFS3_FS_POSIX_ACL` selects POSIX ACL support. It owns no runtime state but changes compatibility and compiled behavior. It integrates with the Kbuild Makefile and VFS/compression/ACL code. Risks are Windows incompatibility for 64-bit clusters, missing external compression support when disabled, and Linux-only ACL semantics. Test build matrices and mount/runtime behavior for each option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/Makefile -->
# sources/distributed-fs/ceph-client/fs/ntfs3/Makefile

Builds `ntfs3.o`, lists core driver objects, conditionally adds LZX/XPRESS decompression objects, and applies a strict warning subset with compiler-option probing. It owns no runtime state; it controls which source files and feature objects become part of the module or built-in driver. Dependencies are Kbuild, compiler support, `CONFIG_NTFS3_FS`, and `CONFIG_NTFS3_LZX_XPRESS`. Risks are compiler-version warning breakage or missing object list entries causing link/functionality failures. Test GCC/Clang builds, module and built-in configurations, optional compression, and warning-enabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/attrib.c -->
# sources/distributed-fs/ceph-client/fs/ntfs3/attrib.c

Implements NTFS3 attribute mutation: runlist loading, cluster allocation/deallocation, resident-to-nonresident conversion, size changes, block mapping, delayed allocation, sparse/compressed frame allocation, WOF frame metadata reads, hole punching, range collapse/insert, and forced nonresident data. Key APIs include `attr_load_runs()`, `run_deallocate_ex()`, `attr_allocate_clusters()`, `attr_make_nonresident()`, `attr_set_size_ex()`, `attr_data_get_block()`, `attr_data_get_block_locked()`, `attr_load_runs_vcn()`, `attr_load_runs_range()`, `attr_is_frame_compressed()`, `attr_allocate_frame()`, `attr_collapse_range()`, `attr_punch_hole()`, `attr_insert_range()`, and `attr_force_nonresident()`.

Control flow typically finds the base attribute, loads runlist segments, edits runs, repacks runs into MFT records, updates attribute lists when records split/merge, updates sizes and inode bytes, then marks metadata dirty. Persistent state includes runlists, allocation/data/valid/total sizes, resident payloads, attribute-list entries, sparse/compression layout, and allocation bitmap changes. Dependencies include run, bitmap, inode, MFT record, attrlist, compression, block I/O, and folios. Risks are high: partial rollback, ENOSPC during deep attribute-list expansion, compressed-frame alignment, delayed allocation crossing real clusters, MFT self-extension, stale pointers after layout changes, and a suspicious `attr_allocate_frame()` valid-size assignment that appears not to store `new_valid`. Test with truncate, sparse writes, ENOSPC/fault injection, compression, WOF, hole/collapse/insert range, resident boundary crossing, and consistency checks after remount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/attrib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/attrlist.c -->
# sources/distributed-fs/ceph-client/fs/ntfs3/attrlist.c

Manages NTFS attribute lists for attributes spanning multiple MFT records. It loads resident/nonresident lists, enumerates entries, finds matching entries by type/name/VCN, inserts sorted entries, removes entries, writes dirty lists, and destroys list state. Important functions are `ntfs_load_attr_list()`, `al_enumerate()`, `al_find_le()`, `al_find_ex()`, `al_add_le()`, `al_remove_le()`, `al_update()`, and `al_destroy()`. Runtime state is `ni->attr_list` buffer, size, runlist, and dirty flag; persistent state is `$ATTRIBUTE_LIST`. It integrates with `attrib.c` and MFT segment loading. Risks include sorted lookup correctness, malformed entry bounds, zero-size/nonresident invalid states, and partial persistence failure after in-memory insertion. Test fragmented files, list growth to nonresident, removal during truncation, ENOMEM insertion, sorted order, and remount validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/attrlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/bitfunc.c -->
# sources/distributed-fs/ceph-client/fs/ntfs3/bitfunc.c

Provides low-level bitmap predicates `are_bits_clear()` and `are_bits_set()`. They handle partial leading bytes, align to `size_t`, scan words and trailing bytes, and handle partial tails using `fill_mask[]` and `zero_mask[]`. They own no state and are used by `bitmap.c` to verify ranges in persistent allocation bitmap buffers. Risks are off-by-one errors around unaligned ranges and architecture assumptions around word loads; zero-length ranges intentionally return true. Test sub-byte, cross-byte, word-aligned, unaligned, all-clear, all-set, mixed, and big-endian cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/bitfunc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/bitmap.c -->
# sources/distributed-fs/ceph-client/fs/ntfs3/bitmap.c

Implements NTFS3 bitmap-window allocation support using per-window free counters plus red-black trees by start and by length. Important APIs include `wnd_init()`, `wnd_rescan()`, `wnd_find()`, `wnd_set_free()`, `wnd_set_used()`, `wnd_set_used_safe()`, `wnd_is_free()`, `wnd_is_used()`, `wnd_extend()`, `wnd_zone_set()`, `ntfs_trim_fs()`, and little-endian bitmap helpers. Initialization scans on-disk bitmap blocks through runlists, builds extents, and caps cache size. Allocation uses aggregate zero counts, hints, largest extents, or fallback bitmap scans, optionally marking bits used. Persistent state is `$Bitmap` or `$MFT/$BITMAP`; runtime state is `free_bits`, extent trees, `total_zeroes`, zone, and cache validity. Dependencies include runlists, buffer heads, discard, block mapping, and `bitfunc.c`. Risks are cache/disk divergence, approximate trees under extent caps, zone exclusion bugs, map/read errors, and dirty-buffer persistence. Test allocation hints, full/partial requests, zones, cache invalidation, boundary transitions, extension, trim, and bitmap primitive correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/bitmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/debug.h -->
# sources/distributed-fs/ceph-client/fs/ntfs3/debug.h

Provides `Add2Ptr()`/`PtrOffset()` packed-record pointer helpers and logging macros around `ntfs_printk()`/`ntfs_inode_printk()`. With `CONFIG_PRINTK` disabled, inline stubs preserve call sites and format annotations without output. It owns no persistent state. It is included broadly across NTFS3 for record parsing and diagnostics. Risks are misuse of pointer-offset macros outside one mapped object and losing diagnostics in no-printk builds. Test compile format checking, printk/no-printk builds, and corrupted-record paths under sanitizers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/dir.c -->
# sources/distributed-fs/ceph-client/fs/ntfs3/dir.c

Implements NTFS3 directory name conversion, lookup, iteration, counting, empty checks, and directory file operations. Key functions are `ntfs_utf16_to_nls()`, `_utf8s_to_utf16s()`, `ntfs_nls_to_utf16()`, `dir_search_u()`, `ntfs_dir_emit()`, `ntfs_read_hdr()`, `ntfs_readdir()`, `ntfs_dir_count()`, `dir_is_empty()`, and `ntfs_dir_operations`. Lookup searches NTFS indexes and opens referenced inodes. Readdir emits dots, walks root and allocation index blocks by used bitmap bits, filters DOS/meta/hidden entries, converts names, and restarts after directory modification at end-of-stream to support common readdir/unlink loops. Persistent state is directory index data; runtime state includes index nodes, search contexts, conversion buffers, and `file->private_data` version tracking. Dependencies include index, inode, NLS, VFS dir_context, ioctl/fsync/open, and mount options. Risks are malformed index bounds, conversion truncation or replacement, unreliable duplicated dtype, and undefined semantics during mutation. Test conversion, lookup, large directories, filters, corruption, readdir mutation, empty checks, and dtype behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/dir.c -->
