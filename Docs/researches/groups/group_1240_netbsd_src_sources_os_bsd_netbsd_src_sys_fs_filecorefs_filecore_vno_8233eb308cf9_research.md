# Group Research: group_1240_netbsd_src_sources_os_bsd_netbsd_src_sys_fs_filecorefs_filecore_vno_8233eb308cf9

Scope verified against `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_vnops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_vnops.c

## Purpose
Implements vnode operations for NetBSD FilecoreFS, a read-only Acorn FileCore filesystem implementation. It adapts FileCore nodes to the NetBSD vnode interface for access checks, attributes, reads, directory iteration, block strategy, and path configuration.

## Main Entry Points
- `filecore_access()` rejects writes to regular files, directories, and symlinks, then delegates authorization through kauth and `genfs_can_access()`.
- `filecore_getattr()` fills `vattr` from `filecore_node` metadata and mount defaults for uid, gid, mode, timestamps, size, block size, and file id.
- `filecore_read()` reads regular files through UBC and directory/non-regular content through `filecore_dbread()` or `bread()`.
- `filecore_readdir()` emits synthetic `.` and `..` entries, walks FileCore directory entries, converts names with `filecore_fn2unix()`, and optionally records cookies.
- `filecore_readlink()` is present but returns `EINVAL`; symlink target reads are not implemented.
- `filecore_strategy()` maps logical blocks with `VOP_BMAP()` and dispatches I/O to the underlying device vnode.
- `filecore_pathconf()` reports read-only filesystem limits such as link max 1, path max 256, no truncation, and 32 file size bits.
- `filecore_vnodeop_entries` wires vnode operations, using `genfs_eopnotsupp` or read-only helpers for mutation operations.

## Dependencies
Uses NetBSD vnode, UBC, buffer cache, kauth, genfs, specfs, and Filecore-specific helpers from `filecore.h`, `filecore_extern.h`, and `filecore_node.h`.

## Risks and Notes
The implementation is explicitly read-only. `filecore_readlink()` makes symlink support effectively absent even though symlink types are considered in access checks. `filecore_readdir()` advances the local `cookies` pointer before assigning `*a_cookies`, so the returned pointer appears to reference the advanced position rather than the allocation base. Directory parsing relies on `filecore_fn2unix()` to signal invalid entries or end of directory, and an in-source warning notes an old `d_namlen` type mismatch.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/hfs/Makefile -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/hfs/Makefile

## Purpose
Installs public HFS kernel headers into the system include tree.

## Main Contents
Sets `INCSDIR` to `/usr/include/fs/hfs`, installs `hfs.h` and `libhfs.h`, and includes `bsd.kinc.mk`.

## Dependencies
Part of NetBSD kernel include installation infrastructure.

## Risks and Notes
Only `hfs.h` and `libhfs.h` are exported. Internal helpers such as `unicode.h` are not installed by this Makefile.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/hfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/hfs/hfs.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/hfs/hfs.h

## Purpose
Defines the kernel-facing HFS/HFS+ mount, vnode, callback, macro, and function interfaces.

## Main Contents
- `struct hfs_args` carries the block special device path used for mounting.
- `struct hfsmount` connects the NetBSD mount, device vnode/device id, and parsed `hfs_volume`.
- `struct hfsnode_key` identifies vcache entries by CNID and fork type.
- `struct hfsnode` stores vnode state, mount/device references, the cached catalog record, cached parent CNID, and selected fork.
- Callback argument structs pass credentials, lwp pointers, and device vnodes to the `libhfs` callback layer.
- Convenience macros convert between mount/vnode/HFS node pointers, obtain allocation block size, and convert HFS raw device numbers.
- Declares vnode operation descriptors, VFS prototypes, vnode loading helpers, callback wrappers, endian cursor helpers, HFS time conversion, and catalog record type mapping.

## Dependencies
Includes NetBSD vnode/mount/genfs headers and `fs/hfs/libhfs.h`.

## Risks and Notes
Default uid, gid, file mode, and directory mode are compile-time constants rather than mount options. The cached parent CNID would require maintenance if write/rename support were added. Comments mark debug and permission behavior as development-era or incomplete.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/hfs/hfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/hfs/hfs_subr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/hfs/hfs_subr.c

## Purpose
Provides HFS vnode initialization, kernel callback adapters for `libhfs`, physical block reads, HFS time conversion, endian cursor helpers, and catalog-record-to-vnode-type mapping.

## Main Entry Points
- `hfs_vinit()` derives vnode type from the catalog record, switches special and fifo vnodes to their operation vectors, initializes special devices, and marks root vnodes.
- `hfs_libcb_error()`, `hfs_libcb_malloc()`, `hfs_libcb_realloc()`, and `hfs_libcb_free()` adapt `libhfs` diagnostics and memory allocation to the kernel.
- `hfs_libcb_opendev()` opens the already-resolved block device vnode, invalidates stale buffers, records device block size, and stores per-volume callback data.
- `hfs_libcb_closedev()` closes the callback device and frees callback data.
- `hfs_libcb_read()` translates volume-relative reads to physical device reads through `hfs_pread()`.
- `hfs_pread()` performs sector-aligned `bread()` calls and copies only the requested byte range to the caller.
- `hfs_time_to_timespec()` converts HFS+ seconds since 1904 to Unix `timespec`, clamping pre-1970 dates to epoch.
- `be16tohp()`, `be32tohp()`, and `be64tohp()` decode big-endian values and advance a pointer.
- `hfs_catalog_keyed_record_vtype()` maps HFS catalog records to NetBSD vnode types.

## Dependencies
Uses NetBSD vnode, buffer cache, kauth, specfs, device-size helpers, and HFS structures from `hfs.h`.

## Risks and Notes
The callback allocator still uses `M_TEMP` in places marked as needing pools. `hfs_pread()` has an in-source comment questioning correctness when the aligned start differs from the requested offset. Non-file catalog records are treated as directories by `hfs_catalog_keyed_record_vtype()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/hfs/hfs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/hfs/hfs_vfsops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/hfs/hfs_vfsops.c

## Purpose
Implements NetBSD VFS operations for the HFS/HFS+ filesystem: module attach, mount, unmount, root lookup, statvfs, vnode cache loading, and filesystem lifecycle.

## Main Entry Points
- `MODULE()` and `hfs_modcmd()` attach and detach the VFS module.
- `hfs_vfsops` defines mount, unmount, root, statvfs, sync, vget, loadvnode, file-handle, init, reinit, and done hooks.
- `hfs_mount()` validates mount arguments, resolves the block device, authorizes access, rejects live update remounts, and calls `hfs_mountfs()`.
- `hfs_mountfs()` allocates `hfsmount`, initializes callback arguments, opens the volume through `hfslib_open_volume()`, rejects dirty journaled volumes, and sets mount block shifts.
- `hfs_unmount()` flushes vnodes, closes the `libhfs` volume, releases the device vnode, and frees mount state.
- `hfs_root()` resolves `HFS_CNID_ROOT_FOLDER`.
- `hfs_statvfs()` reports block size, total/free blocks, and file counts from the HFS+ volume header.
- `hfs_vget()` and `hfs_vget_internal()` resolve CNID plus fork type through vcache.
- `hfs_loadvnode()` allocates an `hfsnode`, reads the catalog record by CNID, stores parent CNID, initializes vnode/genfs state, selects fork size, and returns the stable key.
- `hfs_init()` creates pools, attaches malloc types, registers `libhfs` callbacks, and initializes global library state.
- `hfs_done()` tears down malloc, pools, and `libhfs` state.

## Dependencies
Uses NetBSD VFS, vnode cache, module framework, genfs, specfs, pool allocator, kauth mount authorization, and `libhfs`.

## Risks and Notes
Live remount/update support is disabled. File handles are unsupported: `hfs_fhtovp()` and `hfs_vptofh()` return `EOPNOTSUPP`. Dirty journaled volumes are rejected; no replay is attempted. In the mount failure path, allocated `hfsmount` is freed but `mp->mnt_data` is not explicitly cleared there. Vnode write operations are not implemented, so the filesystem is effectively read-only.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/hfs/hfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/hfs/hfs_vnops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/hfs/hfs_vnops.c

## Purpose
Implements HFS/HFS+ vnode operations for path lookup, access checks, attributes, reads, directory iteration, block mapping, reclaim, and operation-vector registration. Mutation operations are mostly unsupported.

## Main Entry Points
- `hfs_vnodeop_entries`, `hfs_specop_entries`, and `hfs_fifoop_entries` define regular, special-device, and fifo vnode operation tables.
- `hfs_vop_parsepath()` extends generic parsing to consume a `/rsrc` suffix, although the regular vnode table currently wires `vop_parsepath` to `genfs_parsepath`.
- `hfs_vop_lookup()` checks directory execute permission, handles `.` and `..`, converts names from UTF-8 to UTF-16, maps `:` to `/`, searches the catalog, resolves HFS+ hardlink metadata, and chooses data or resource fork vnode.
- `hfs_vop_access()` rejects writes to regular files, directories, and symlinks, then authorizes against `VOP_GETATTR()` results.
- `hfs_vop_getattr()` maps file/folder catalog records to `vattr`, including fork size, block usage, BSD mode/uid/gid, timestamps, special-device numbers, and fallback defaults.
- `hfs_vop_setattr()` rejects unsupported or read-only attribute changes.
- `hfs_vop_bmap()` obtains file extents from `libhfs`, maps logical allocation blocks to physical device blocks, and reports run length.
- `hfs_vop_read()` reads regular files and symlinks through UBC up to the selected fork logical size.
- `hfs_vop_readdir()` loads directory children with `hfslib_get_directory_contents()`, converts UTF-16 names to UTF-8, maps `/` to `:`, emits `dirent` records, and frees temporary arrays.
- `hfs_vop_readlink()` reads symlink contents via `VOP_READ()`.
- `hfs_vop_reclaim()` releases the device vnode, destroys genfs state, returns the node to the pool, and clears vnode data.

## Dependencies
Uses NetBSD vnode/genfs/specfs/fifofs/UBC interfaces, HFS node structures, `libhfs`, and local Unicode conversion helpers from `unicode.h`.

## Risks and Notes
The custom `/rsrc` parser is not active in the regular vnode table. `..` lookup requests `HFS_RSRCFORK`, which is surprising for parent directory lookup. `hfs_vop_bmap()` returns `EBADF` when no extents are found, which may mishandle zero-length files. `hfs_vop_readdir()` does not emit synthetic `.`/`..`, does not update `uio_offset` explicitly, and treats a too-small buffer as EOF. A debug print references `curchildname`, which is not defined unless hidden by debug configuration.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/hfs/hfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/hfs/libhfs.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/hfs/libhfs.c

## Purpose
Implements the core HFS+/HFSX on-disk parser used by the NetBSD HFS filesystem. It handles volume opening, HFS wrapper detection, journal metadata, catalog and extent B-tree traversal, directory listing, hardlink resolution, structure decoding, extent reads, key comparison, callbacks, and case-folding table creation.

## Main Entry Points
- `hfslib_init()` stores global callbacks and constructs reusable catalog keys for HFS+ private objects.
- `hfslib_done()` frees the global case-folding table.
- `hfslib_open_volume()` opens the device through callbacks, reads the HFS+ volume header or embedded HFS wrapper, reads catalog and extents header nodes, selects key comparison mode, reads journal metadata, initializes case-folding when needed, and stores the volume name.
- `hfslib_close_volume()` closes the callback device.
- `hfslib_path_to_cnid()` reconstructs a Unicode absolute path by walking parent thread records.
- `hfslib_find_parent_thread()` resolves a CNID to its parent thread record.
- `hfslib_find_catalog_record_with_cnid()` resolves CNID to catalog key and catalog record.
- `hfslib_find_catalog_record_with_key()` traverses catalog B-tree index and leaf nodes using the selected key comparator.
- `hfslib_find_extent_record_with_key()` traverses the extents overflow B-tree.
- `hfslib_get_file_extents()` combines inline fork extents with overflow records until all file blocks are described.
- `hfslib_get_directory_contents()` locates children by parent CNID, walks chained leaf nodes, filters private objects, and optionally returns child records and names.
- `hfslib_is_journal_clean()` treats unjournaled volumes as clean and journaled volumes as clean only when journal start equals end.
- `hfslib_read_*()` functions decode big-endian volume headers, HFS wrapper MDBs, B-tree nodes, catalog records, extent records, fork descriptors, Unicode strings, BSD metadata, Finder info placeholders, and journal structures.
- `hfslib_readd_with_extents()` reads file ranges by intersecting requested byte ranges with extents.
- Callback wrappers centralize error, allocation, device open/close, and read calls.
- `hfslib_make_catalog_key()` and `hfslib_make_extent_key()` construct B-tree keys.
- `hfslib_compare_catalog_keys_cf()`, `hfslib_compare_catalog_keys_bc()`, and `hfslib_compare_extent_keys()` implement B-tree ordering.
- `hfslib_create_casefolding_table()` lazily allocates and populates the HFS+ case-folding table.
- `hfslib_get_hardlink()` resolves HFS+ hardlink records under the private metadata directory.

## Dependencies
Depends on `libhfs.h` data structures and callback functions supplied by kernel glue in `hfs_subr.c`. Uses HFS+/HFSX catalog, extent, journal, wrapper, and B-tree formats.

## Risks and Notes
This file is parser-heavy and trusts many disk-provided sizes, offsets, node links, and record counts. Comments identify incomplete or suspect behavior: extent index records are described as bogus, Finder info readers are placeholders, binary catalog comparison is byte-oriented despite the HFS spec requiring 16-bit chunks, and casefolding has endian caveats. `hfslib_read_unistr255()` clamps excessive name length to 255 but then advances only across the clamped length, which can desynchronize parsing on malformed input. B-tree traversal assumes consistent node ordering and valid record offsets. `hfslib_readd_with_extents()` reads covered intersections but does not zero gaps for sparse or missing coverage. Callback and case-folding state is process-global, so initialization order and concurrent use matter.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/hfs/libhfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/hfs/libhfs.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/hfs/libhfs.h

## Purpose
Defines the HFS/HFS+ on-disk data model, constants, callbacks, global state, and parser APIs used by `libhfs.c` and the kernel HFS wrapper.

## Main Contents
- Volume signatures, volume attribute bits, B-tree node kinds, B-tree header flags, special CNIDs, catalog record kinds, journal flags, journal magic values, fork types, key comparison types, key length limits, and hardlink magic values.
- HFS+ on-disk types for Unicode strings, CNIDs, extent records, forks, volume headers, B-tree nodes, catalog keys, extent keys, BSD metadata, file/folder records, thread records, and journal structures.
- Plain HFS master directory block structures used to locate embedded HFS+ volumes inside HFS wrappers.
- `hfs_volume` stores parsed volume header, catalog/extents headers, key-size fields, volume name, key comparator, journal metadata, embedded volume offset, readonly flag, and callback data.
- `hfs_catalog_keyed_record_t` represents catalog leaf records or index child pointers.
- `hfs_callback_args` and `hfs_callbacks` define host-provided allocation, I/O, open, close, and error hooks.
- Declares global callbacks and global case-folding table.
- Declares high-level lookup/listing/journal/hardlink APIs, low-level structure readers, key constructors, extent readers, comparators, and callback wrappers.

## Dependencies
Includes NetBSD endian, param, mount, and types headers. Outside the kernel, it includes libc and iconv-related headers.

## Risks and Notes
The header defines `max` and `min` macros unconditionally, which can collide with other definitions. Many structures mirror packed disk formats but are decoded through explicit readers rather than direct casting. The callback interface is global while `hfs_volume.cbdata` carries per-volume data. Return conventions vary: some APIs return 0 on success, others return counts, CNIDs, byte counts, or negative/not-found values.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/hfs/libhfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/hfs/unicode.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/hfs/unicode.c

## Purpose
Provides local UTF-8 to UTF-16 and UTF-16 to UTF-8 conversion helpers for HFS path lookup and directory name handling.

## Main Entry Points
- `utf8_to_utf16()` decodes UTF-8 into UTF-16 code units, optionally falling back to Latin-1 for invalid high bytes, rejects several malformed encodings, emits surrogate pairs for four-byte UTF-8, counts errors, and returns output code-unit count.
- `utf16_to_utf8()` encodes UTF-16 code units into UTF-8 bytes, attempts surrogate-pair handling, counts errors, and returns output byte count.

## Dependencies
Uses `sys/null.h` and declarations from `unicode.h`.

## Risks and Notes
The implementation is compact but fragile. Some bounds checks use expressions that can still permit out-of-range lookahead on truncated input. `utf16_to_utf8()` uses `uint8_t` positions for source and destination indices, which can overflow for lengths above 255. The surrogate-pair path appears to validate the first surrogate twice rather than validating the second code unit, and the computed pair indexes are suspicious after incrementing `spos`. Callers often ignore the reported error count.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/hfs/unicode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/hfs/unicode.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/hfs/unicode.h

## Purpose
Declares HFS-local Unicode conversion helpers and conversion flags.

## Main Contents
Defines `UNICODE_DECOMPOSE`, `UNICODE_PRECOMPOSE`, and `UNICODE_UTF8_LATIN1_FALLBACK`, then declares `utf8_to_utf16()` and `utf16_to_utf8()`.

## Dependencies
Includes `sys/types.h` for fixed-width and size types.

## Risks and Notes
The flags are declared but the implementation only meaningfully uses the Latin-1 fallback flag; decomposition/precomposition are not implemented in `unicode.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/hfs/unicode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/Makefile -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/Makefile

## Purpose
Installs public msdosfs kernel headers into the system include tree.

## Main Contents
Sets `INCSDIR` to `/usr/include/msdosfs`, installs `bootsect.h`, `bpb.h`, `denode.h`, `direntry.h`, `fat.h`, and `msdosfsmount.h`, then includes `bsd.kinc.mk`.

## Dependencies
Part of NetBSD kernel include installation infrastructure.

## Risks and Notes
This exports both on-disk format headers and internal-ish denode/FAT interfaces used by kernel and `makefs` builds.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/bootsect.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/bootsect.h

## Purpose
Defines DOS/FAT boot sector layout structures for several historical FAT variants.

## Main Contents
- `struct bootsector33` models a DOS 3.3 style 512-byte boot sector with jump, OEM name, 19-byte BPB, drive number, boot code, and 0x55/0xaa signature bytes.
- `struct extboot` describes the extended boot signature, volume ID, label, and filesystem type fields.
- `struct bootsector50` models a DOS 5.0 boot sector with 25-byte BPB and extension.
- `struct bootsector710` models a FAT32-era boot sector with 53-byte BPB and extension.
- Atari/GEMDOS alternate boot sector definition is retained under disabled code.
- `union bootsector` overlays the supported variants.
- Disabled shorthand macros map boot-sector fields to BPB members.

## Dependencies
Uses fixed-width integer types expected from surrounding includes.

## Risks and Notes
The BPB fields are represented as byte arrays inside boot sector structs to avoid alignment assumptions. Signature macros are repeated for multiple structs. Atari support is documented but inactive in this header.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/bootsect.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/bpb.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/bpb.h

## Purpose
Defines BIOS Parameter Block layouts and FAT32 FSInfo layout for FAT12/FAT16/FAT32 media.

## Main Contents
- `struct bpb33`, `struct bpb50`, and `struct bpb710` describe host-aligned DOS 3.3, DOS 5.0, and FAT32 BPB fields.
- FAT32 flags define active FAT number, mirroring bit, and supported filesystem version.
- Atari/GEMDOS BPB definition is retained under disabled code.
- `getushort()`, `getulong()`, `putushort()`, and `putulong()` wrap little-endian decode/encode helpers.
- `struct byte_bpb33`, `struct byte_bpb50`, and `struct byte_bpb710` describe exact on-disk byte-array forms that avoid compiler alignment concerns.
- `struct fsinfo` defines the FAT32 FSInfo sector layout, including signatures, free-count hint, and next-free hint.

## Dependencies
Includes `sys/endian.h` for little-endian encoding and decoding helpers.

## Risks and Notes
The file intentionally separates host-aligned and byte-packed forms. Consumers must use byte forms or endian helpers when reading disk data directly. Several BPB fields are only meaningful for specific FAT generations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/bpb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/denode.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/denode.h

## Purpose
Defines the in-memory msdosfs denode, denode keys, FAT cache, directory lookup result storage, file-handle structure, conversion macros between disk direntries and denodes, and vnode/internal service prototypes.

## Main Contents
- Detailed comments explain FAT directory identity quirks: root directory specialness, cluster 0 meanings, missing Unix link counts, immutable directory sizes, and `.`/`..` behavior.
- `MSDOSFSROOT_OFS` defines the synthetic root directory entry offset.
- `struct fatcache` and cache slot macros remember recent file-relative to filesystem-relative cluster mappings.
- `struct msdosfs_lookup_results` stores lookup offsets and slot counts.
- `struct denode_key` identifies vcache entries by containing directory cluster, directory offset, and a unique generation pointer for unlinked nodes.
- `struct denode` stores genfs node state, vnode/device refs, mount pointer, flags, directory entry identity, DOS name/attributes/timestamps, start cluster, file size, and FAT cache.
- `DE_UPDATE`, `DE_CREATE`, `DE_ACCESS`, `DE_MODIFIED`, and `DE_RENAME` flag pending state changes.
- `WIN_MAXLEN` and `MSDOSFS_FILESIZE_MAX` define FAT filename and file size limits.
- `DE_INTERNALIZE*` and `DE_EXTERNALIZE*` convert between on-disk `struct direntry` and in-memory `struct denode`, including FAT32 high cluster bits.
- `DETIMES()` drains pending timestamp updates through `msdosfs_detimes()`.
- `struct defid` overlays filesystem file handles.
- Declares msdosfs vnode operations and internal routines for create, extend, truncate, update, directory entry IO, name generation, file handles, and genfs operations.

## Dependencies
Includes genfs node definitions in kernel builds, or stubs for `MAKEFS`. Relies on `direntry.h`, `bpb.h`, and `fat.h` macros/types in consumers.

## Risks and Notes
Directory and root identity are intentionally non-Unix-like. `fc_setcache` is a multi-statement macro without a `do { } while (0)` wrapper. Conversion macros assume callers have a valid `de_pmp` so FAT32 detection is meaningful. Directory sizes are synthesized by following cluster chains rather than trusting directory entry size.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/denode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/direntry.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/direntry.h

## Purpose
Defines FAT short directory entries, Win95 long-name entries, directory attribute bits, date/time bit layouts, and filename/time conversion prototypes.

## Main Contents
- `struct direntry` models the 32-byte FAT short directory entry: 8.3 name, attributes, timestamps, high/low start cluster, and file size.
- Slot constants distinguish empty, deleted, and escaped `0xe5` first-name bytes.
- Attribute constants define readonly, hidden, system, volume label, directory, archive, normal, and Win95 long-name values.
- `msdos_dirchar()` provides indexed access across name and extension fields.
- `struct winentry` models a Win95 long filename slot with sequence count, checksum, and three UTF-16 name fragments.
- Date and time masks/shifts describe FAT packed timestamp fields.
- Declares time conversion, short-name conversion, Win95 long-name conversion/checking, checksum, and slot-count helpers for kernel or `MAKEFS`.

## Dependencies
Uses fixed-width integer types and references `struct dirent` for long-name reconstruction.

## Risks and Notes
The on-disk name fields are raw byte arrays, not C strings. Long-name entries store UTF-16 fragments split across non-contiguous fields. FAT timestamps have two-second granularity plus optional hundredths for creation time.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/direntry.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/fat.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/fat.h

## Purpose
Defines FAT cluster constants, FAT type masks, EOF detection, FAT operation flags, allocation flags, and FAT service routine prototypes.

## Main Contents
- Defines special cluster values for root, free clusters, first valid cluster, reserved range, bad cluster, EOF range, and end marker.
- Defines FAT12/FAT16/FAT32 masks and type-test macros against `pm_fatmask`.
- `MSDOSFSEOF()` tests whether a masked cluster number lies in the FAT EOF range.
- Defines `FAT_GET`, `FAT_SET`, and `FAT_GET_AND_SET` operation flags for FAT entry updates.
- Defines `DE_CLEAR` for zeroing newly allocated file blocks.
- Declares FAT mapping, allocation, extension, free-chain, in-use map, and FAT-cache helpers.

## Dependencies
Relies on `struct msdosfsmount` and `struct denode` definitions from msdosfs mount/denode headers in consumers.

## Risks and Notes
FAT type detection is based on a mount-computed mask rather than rechecking disk layout. EOF matching follows Microsoft’s broad EOF-marker range semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/fat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_conv.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_conv.c

## Purpose
Implements FAT timestamp conversion, DOS 8.3 filename conversion, Win95 long filename conversion, UTF-8/UCS-2 conversion helpers, and case-insensitive name matching for msdosfs.

## Main Entry Points
- `msdosfs_unix2dostime()` converts Unix `timespec` to packed DOS date/time/hundredths fields with timezone adjustment, two-second granularity, and range clamping.
- `msdosfs_dos2unixtime()` converts packed DOS date/time/hundredths fields back to Unix `timespec`.
- `msdosfs_dos2unixfn()` converts an 11-byte DOS 8.3 name to a Unix filename, handling `SLOT_E5`, optional lowercasing, trailing blanks, and extensions.
- `msdosfs_unix2dosfn()` converts a Unix filename to an 8.3 DOS name, handles `.` and `..`, rejects names made only of blanks/dots, inserts generation suffixes, and reports whether a long-name entry is needed.
- `msdosfs_unix2winfn()` creates one Win95 long-name directory slot from a Unix name, using UTF-8 or 8-bit-to-UCS-2 conversion and padding with null/0xffff.
- `msdosfs_winChkName()` verifies a Win95 long-name slot against a Unix name and checksum.
- `msdosfs_win2unixfn()` prepends a Win95 long-name segment to a `dirent`, rejects slash-containing names, converts UCS-2 to UTF-8 or 8-bit, and tracks total name length.
- `msdosfs_winChksum()` computes the short-name checksum for Win95 long entries.
- `msdosfs_winSlotCnt()` computes the number of Win95 slots required for a name.
- Static helpers implement invalid slash detection, UCS-2/UTF-8 conversion, UCS-2/8-bit conversion, UCS-2 padding, Unicode fold lookup, and case-insensitive comparisons.

## Dependencies
Uses NetBSD time/clock helpers, endian helpers, dirent definitions, `direntry.h`, `denode.h`, and the external `msdosfs_unicode_foldmap` table.

## Risks and Notes
The file uses fixed translation tables for DOS/Unix character conversion and upper/lower folding. UTF-8 decoding accepts only up to three-byte sequences for UCS-2 and does not validate continuation-byte bit patterns beyond length classes. `ucs2utf8str()` and related routines use pointer subtraction on possibly null output pointers when called in length-only mode, which is a delicate convention. `msdosfs_win2unixfn()` documents that long UCS-2 names can be silently truncated to fit `dirent.d_name`, potentially causing ambiguous displayed names.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_conv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_denode.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_denode.c

## Purpose
Implements msdosfs denode lifecycle, vnode cache loading, file truncation/extension, inactive/reclaim behavior, genfs hooks, and synthetic file-handle generation tracking.

## Main Entry Points
- `msdosfs_init()` attaches msdosfs malloc types, initializes denode and file-handle pools, initializes the file-handle red-black tree, and creates the file-handle mutex.
- `msdosfs_done()` destroys pools/mutexes and detaches malloc types.
- `msdosfs_deget()` normalizes FAT32 root cluster lookups and obtains vnodes from vcache by `denode_key`.
- `msdosfs_loadvnode()` allocates a denode, manufactures the root denode or reads a directory entry with `msdosfs_readep()`, internalizes disk metadata, determines vnode type, synthesizes directory size by following FAT chains, initializes genfs state, and sets UVM vnode size.
- `msdosfs_deupdat()` delegates pending denode updates to `msdosfs_update()`.
- `msdosfs_detrunc()` truncates files, rejects fixed FAT12/FAT16 root truncation, zeroes partial cluster tails, updates directory entry state, frees cluster chains, and purges FAT cache.
- `msdosfs_deextend()` extends regular files by allocating clusters, zero-filling new UBC ranges, updating file size/write size, and writing metadata.
- `msdosfs_reclaim()` releases device vnode refs, destroys genfs state, clears vnode data under interlock, and returns the denode to the pool.
- `msdosfs_inactive()` truncates and marks deleted files when reference count drops on writable mounts, removes file-handle records, updates metadata, and requests recycling for deleted denodes.
- `msdosfs_gop_alloc()` is a no-op allocation hook; `msdosfs_gop_markupdate()` maps genfs accessed/modified notifications to denode flags.
- `msdosfs_fh_enter()`, `msdosfs_fh_remove()`, `msdosfs_fh_lookup()`, and `msdosfs_fh_destroy()` maintain a mount-scoped red-black tree of directory-entry file-handle generations.

## Dependencies
Uses NetBSD vnode, mount, buffer cache, pools, UVM, genfs, kauth, red-black trees, and msdosfs headers `bpb.h`, `msdosfsmount.h`, `direntry.h`, `denode.h`, and `fat.h`.

## Risks and Notes
Root handling differs for FAT32 versus fixed-root FAT variants. Directory sizes are synthesized by `msdosfs_pcbmap()` rather than on-disk file size. `msdosfs_detrunc()` sets UVM size before some error paths, so callers rely on later consistency handling. File-handle generation is global and protected by a mutex; generation wraparound is not addressed. `msdosfs_gop_alloc()` returning success without allocation is intentional only if allocation is handled elsewhere.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_denode.c -->