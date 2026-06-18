# Group Research: group_1255_netbsd_src_sources_os_bsd_netbsd_src_sys_fs_udf_udf_subr_c_sources__7560042f26ee

Scope: `Docs/research_subset_a.md`, specifically NetBSD UDF filesystem sources under `sources/os/bsd/netbsd-src/sys/fs/udf/`.

Files read completely:
- `sources/os/bsd/netbsd-src/sys/fs/udf/udf_subr.c`
- `sources/os/bsd/netbsd-src/sys/fs/udf/udf_subr.h`
- `sources/os/bsd/netbsd-src/sys/fs/udf/udf_vfsops.c`

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_subr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf_subr.c

## Purpose

`udf_subr.c` is the large support implementation for NetBSD’s in-kernel UDF filesystem. It handles most mount-time UDF format interpretation and much of the common vnode support machinery used by `udf_vfsops.c` and vnode operations.

Major responsibilities include:
- Device/media and MMC track discovery.
- Descriptor tag validation, CRC maintenance, and descriptor sizing.
- Anchor, VDS, logical volume integrity, VAT, sparable partition, metadata partition, and root directory discovery.
- Logical volume open/close sequencing for writable media.
- Node loading, descriptor lifecycle, dirty/writeout handling, and genfs integration.
- Directory FID parsing, dirhash population, lookup, attach, detach, and parent update.
- UDF/Unix name, permission, ownership, and timestamp conversion.
- File-buffer read/write translation handoff to lower UDF mapping and disc strategy code.

## Key Flows

### Media and Track Discovery

The file starts with debug dump helpers for `mmc_discinfo` and `mmc_trackinfo`, then implements:
- `udf_update_discinfo()`: asks the device for MMC disc info, or synthesizes disc-like information for ordinary disk partitions via `getdisksize()`.
- `udf_update_trackinfo()`: reads MMC track info, or synthesizes a single closed track for partition-backed mounts.
- `udf_setup_writeparams()`: prepares MMC write parameters for recordable media.
- `udf_mmc_synchronise_caches()`: issues MMC cache synchronization for writable non-partition media.
- `udf_search_tracks()`: maps requested session number to first/last track.
- `udf_search_writing_tracks()`: identifies writable data and metadata tracks, attempts damaged-track repair, and rejects media without writable data/metadata tracks.

This is the media abstraction layer that lets UDF mount on both optical MMC devices and regular block devices.

### Descriptor Validation

Descriptor helpers include:
- `udf_check_tag()`: validates 16-byte UDF descriptor tag checksum.
- `udf_check_tag_payload()`: validates descriptor payload CRC.
- `udf_validate_tag_sum()` and `udf_validate_tag_and_crc_sums()`: recompute tag checksum and payload CRC before writing.
- `udf_tagsize()`: computes descriptor size for known descriptor types, usually rounded to logical block size.
- `udf_fidsize()`: computes exact FID length without sector rounding.

These routines are central to safely reading and rewriting on-disc UDF structures.

### Anchor and Volume Descriptor Processing

Mount-time discovery proceeds through:
- `udf_read_anchor()` and `udf_read_anchors()`: locate AVDPs around track start/end positions.
- `udf_read_vds_extent()` and `udf_read_vds_space()`: read the main/reserve Volume Descriptor Sequence.
- `udf_process_vds_descriptor()`: records primary volume, logical volume, partition, implementation, and unallocated-space descriptors.
- `udf_process_vds()`: validates descriptor completeness, checks OSTA UDF compliance, retrieves logical volume integrity, decodes partition maps, determines virtual-to-physical mapping types, selects allocation strategies, and selects the disc strategy implementation.

Important partition-map handling:
- Physical mappings become space-map allocations.
- Virtual mappings enable VAT and sequential allocation.
- Sparable mappings load sparing tables and use remap-on-error behavior.
- Metadata mappings identify metadata files and metadata bitmap behavior.

The code also contains compatibility handling for malformed/random physical partition numbers through `udf_find_raw_phys()`.

### Logical Volume Integrity

Logical volume integrity support is implemented through:
- `udf_retrieve_lvint()`: reads the logical volume integrity sequence, including chained extents, and records trace positions.
- `udf_loose_lvint_history()`: rewrites/reduces old integrity history when space runs out.
- `udf_writeout_lvint()`: updates timestamp and implementation ID, writes the current integrity descriptor, and appends a terminator if possible.

This is used by both mount/open and unmount/close paths to mark a writable volume open or closed.

### Space Tables and Metadata Partition Bitmap

Space table support includes:
- `udf_read_physical_partition_spacetables()`: reads unallocated and freed space bitmaps; explicitly rejects table-based unallocated/freed space descriptors as unsupported.
- `udf_write_physical_partition_spacetables()`: writes physical partition bitmaps synchronously.
- `udf_read_metadata_partition_spacetable()`: reads metadata bitmap file through the vnode layer.
- `udf_write_metadata_partition_spacetable()`: resizes and writes metadata bitmap contents.

Notes:
- Bitmap page backing is marked TODO.
- Physical unallocated/freed “space tables” are not supported and force read-write mount failure.
- Metadata write support is constrained; `udf_read_metadata_nodes()` explicitly notes metadata writing is disabled/not working in some paths.

### VAT and Sequential Media

VAT handling is substantial:
- `udf_vat_read()` and `udf_vat_write()` access and grow the in-memory VAT table.
- `udf_check_for_vat()` validates old UDF 1.50 VAT tails or UDF VAT file headers, loads the full VAT file, and updates logical volume info.
- `udf_search_vat()` scans likely VAT locations near the end of the session and retains the last accepted VAT node.
- `udf_update_vat_descriptor()` updates old/new VAT metadata before writeout.
- `udf_writeout_vat()` writes the VAT table file and fsyncs the VAT node.
- VAT LVExtension extended attributes are synchronized by `udf_update_lvid_from_vat_extattr()` and `udf_update_vat_extattr_from_lvid()`.

For sequential media close, `udf_close_logvol()` writes repeated VAT descriptors for Windows compatibility and optionally closes tracks/sessions/finalizes media.

### Sparable and Metadata Partition Support

Partition-specific mount helpers:
- `udf_read_sparables()`: loads one valid sparing table from the partition map.
- `udf_read_metadata_nodes()`: loads metadata main, mirror, and bitmap files as system vnodes.
- `udf_read_vds_tables()`: dispatches to VAT, sparing table, metadata node, and bitmap readers after partition maps are known.

System files are marked using `UDF_SET_SYSTEMFILE`, which sets `VV_SYSTEM`, takes an extra ref, and releases the lock.

### Root Directory Discovery

`udf_read_rootdirs()`:
- Translates and reads the File Set Descriptor sequence.
- Keeps the last valid FSD encountered.
- Updates stored logical volume names.
- Loads the root directory node.
- Optionally attempts to load the system stream directory, but currently ignores it.

### Logical Volume Open/Close

Writable mount open:
- `udf_open_logvol()` checks integrity state, write parameters, writable tracks, optional session-start validation, optional VAT writeout, marks integrity open, and writes LVID if required.

Unmount close:
- `udf_close_logvol()` writes VATs, closes session/tracks if requested, writes partition bitmaps, writes metadata partition descriptors/mirror, marks integrity closed, writes LVID, and synchronizes caches.

`udf_validate_session_start()` handles writing or copying the ISO/UDF VRS and initial anchor when opening a new sequential session.

### Genfs Integration and Buffer I/O

The file defines UDF genfs hooks:
- `udf_gop_alloc()`: reserves logical blocks before writes.
- `udf_gop_markupdate()`: maps genfs update flags to UDF inode flags.
- `udf_genfsops`: uses `genfs_gop_write_rwmap`.

Buffer helpers:
- `udf_read_filebuf()`: translates file logical blocks, handles internal/zero/unmapped cases, creates nested I/O buffers for mapped runs, and queues them to the selected disc strategy.
- `udf_write_filebuf()`: translates/late-allocates write runs through nested buffers and increments outstanding buffer accounting.
- `udf_read_internal()` and `udf_write_internal()` handle files stored inside FE/EFE descriptors.

Translation and allocation helpers such as `udf_translate_file_extent()`, `udf_reserve_space()`, `udf_allocate_space()`, `udf_grow_node()`, and `udf_shrink_node()` are called here but implemented elsewhere.

### Node Lifecycle

Node helpers include:
- `udf_get_node_id()` and `udf_compare_icb()` for identity/rbtree ordering.
- `udf_init_nodes_tree()` initializes the sync rbtree.
- `udf_loadvnode()` loads a vnode from an ICB address, follows indirect entries, accepts FE/EFE descriptors, loads allocation extension descriptors, sets vnode type, and initializes genfs state.
- `udf_get_node()` uses `vcache_get()` and locks the vnode.
- `udf_writeout_node()` writes dirty node descriptors and allocation extension descriptors.
- `udf_dispose_node()` tears down genfs state, dirhash, locks, allocation extension descriptors, FE/EFE memory, and returns the node to `udf_node_pool`.
- `udf_newvnode()` allocates one logical block for a new FE/EFE and initializes vnode/node state.
- `udf_create_node()` creates and attaches a new node into a directory, rolling back allocated descriptor space on failure.
- `udf_delete_node()` shrinks a file to zero, marks it clean/deleted, adjusts file counts, and frees descriptor space.
- `udf_resize_node()` dispatches grow/shrink.

Special file creation for block devices, char devices, FIFOs, and sockets returns `ENOTSUP`; comments note missing specfs/fifofs integration.

### Directory Operations

Directory support includes:
- `udf_read_fid_stream()`: reads one FID descriptor from a directory stream, validates tag and payload CRC, converts the UDF name to a `dirent`, synthesizes `".."` for parent FIDs, and advances the offset.
- `udf_dirhash_fill()`: builds a NetBSD `dirhash`, recording deleted FIDs as reusable free entries.
- `udf_lookup_name_in_dir()`: canonicalizes a Unix name through UDF name conversion, searches dirhash hits, rereads matching FIDs, and returns the target ICB.
- `udf_dir_attach()`: chooses a deleted FID slot or appends a new one, handles tag-split padding, writes the FID, updates link counts, and updates dirhash.
- `udf_dir_detach()`: marks a directory FID deleted, writes it back, optionally adjusts link counts, and removes dirhash entry.
- `udf_dir_update_rootentry()`: updates a directory’s `".."` FID after parent changes.

One conditional branch under `#ifndef UDF_COMPLETE_DELETE` appears to call `udf_read_fid_stream(vp, ...)` where the local directory vnode variable is `dvp`; this path depends on compile-time configuration and should be checked if `UDF_COMPLETE_DELETE` is ever disabled.

### Attributes, Names, Permissions, and Time

Conversion helpers:
- `udf_osta_charset()`, `udf_to_unix_name()`, and `unix_to_udf_name()` convert OSTA Compressed Unicode and UTF-8 names.
- `udf_perm_to_unix_mode()`, `unix_mode_to_udf_perm()`, and `udf_icb_to_unix_filetype()` translate UDF permissions/types.
- `udf_getaccessmode()` and `udf_setaccessmode()` read/write mode bits.
- `udf_getownership()` and `udf_setownership()` translate anonymous/nobody UID/GID conventions.
- `udf_timestamp_to_timespec()` and `udf_timespec_to_timestamp()` convert UDF timestamps.
- `udf_itimes()` applies access/change/update/modify/birth times.
- `udf_update()` updates timestamps, implementation ID, descriptor CRCs, and optionally fsyncs dirty nodes.

Extended attribute support:
- Searches internal FE/EFE EA space.
- Checks/calculates UDF implementation EA checksums.
- Can insert internal EAs while creating descriptors.
- Uses file-times EAs for FE creation time support.

### Synchronization

`udf_do_sync()`:
- Skips lazy sync.
- Iterates mount vnodes, selects dirty non-system UDF vnodes, inserts them into an rbtree, and runs three sync passes.
- Pass 1 fsyncs data only.
- Pass 2 fsyncs completed nodes.
- Pass 3 counts pending device/node I/O and waits for `MNT_WAIT`.
- Cleans the rbtree and releases vnode references.

This complements `udf_vfsops.c`’s `udf_sync()` wrapper.

## Dependencies

Includes and depends on:
- NetBSD kernel VFS, vnode, genfs, buf, dirhash, mount, kauth, device, disklabel, and clock APIs.
- UDF structure definitions from `ecma167-udf.h`, `udf_mount.h`, `udf.h`, and `udf_bswap.h`.
- Unicode helpers from `<fs/unicode.h>`.
- Disc strategy modules through `udf_discstrat_*()` and strategy globals.
- Allocation/readwrite helpers declared in `udf_subr.h` but implemented in other UDF files.

## Notable Constraints and Risks

- Sector sizes `>= 8192` are rejected by mount logic in `udf_vfsops.c`; this file assumes logical block and descriptor sizes fit current limits.
- Many descriptor and allocation paths rely on `KASSERT()`/`assert()` for invariants.
- Physical unallocated/freed space tables are unsupported; only bitmaps are handled.
- Metadata partition writing has comments indicating incomplete or disabled support.
- NFS file handles and `vget` support are not implemented in `udf_vfsops.c`, limiting export-style use.
- Directory corruption recovery is TODO; `udf_read_fid_stream()` reports broken entries but does not resynchronize.
- Internal allocation read/write paths note missing bounds checks for malicious `l_ea`/`inf_len` values.
- VAT and sequential media close handling is highly media-specific and intentionally compatibility-driven.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_subr.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf_subr.h

## Purpose

`udf_subr.h` is the internal UDF support header. It declares the shared helper API used across NetBSD’s UDF filesystem implementation and provides the `VFSTOUDF(mp)` mount-data conversion macro.

It is not limited to declarations implemented in `udf_subr.c`; it also exposes functions implemented across sibling UDF source files such as allocation, read/write, vnode operations, rename, and disc strategy modules.

## API Groups

### Mount and Device Helpers

Declared functions include:
- Disc and track inspection: `udf_update_discinfo()`, `udf_update_trackinfo()`.
- Track search and writable track setup: `udf_search_tracks()`, `udf_search_writing_tracks()`.
- MMC write setup and cache synchronization: `udf_setup_writeparams()`, `udf_mmc_synchronise_caches()`, `udf_synchronise_caches()`.

### Descriptor Helpers

The header exposes:
- Tag/FID sizing: `udf_fidsize()`, `udf_tagsize()`.
- Tag validation and CRC recomputation: `udf_check_tag()`, `udf_check_tag_payload()`, `udf_validate_tag_sum()`, `udf_validate_tag_and_crc_sums()`.
- Physical descriptor read/write: `udf_read_phys_sectors()`, `udf_write_phys_sectors()`, `udf_read_phys_dscr()`, `udf_write_phys_dscr_sync()`, `udf_write_phys_dscr_async()`.
- Logical-volume descriptor handling: `udf_create_logvol_dscr()`, `udf_free_logvol_dscr()`, `udf_read_logvol_dscr()`, `udf_write_logvol_dscr()`.

### Volume Discovery and Lifecycle

Declared mount-time helpers:
- `udf_read_anchors()`
- `udf_read_vds_space()`
- `udf_process_vds()`
- `udf_read_vds_tables()`
- `udf_read_rootdirs()`

Declared writable-volume helpers:
- `udf_open_logvol()`
- `udf_close_logvol()`
- `udf_writeout_vat()`
- `udf_write_physical_partition_spacetables()`
- `udf_write_metadata_partition_spacetable()`
- `udf_do_sync()`
- `udf_synchronise_metadatamirror_node()`

### Translation and Allocation

The header declares the mapping and allocation contract:
- Logical-to-physical translation: `udf_translate_vtop()`, `udf_translate_vtop_list()`, `udf_translate_file_extent()`.
- Allocation descriptor access: `udf_get_adslot()`, `udf_append_adslot()`.
- VAT access: `udf_vat_read()`, `udf_vat_write()`.
- Reservation/allocation/free: `udf_reserve_space()`, `udf_allocate_space()`, `udf_free_allocated_space()`, `udf_cleanup_reservation()`.
- Late allocation and resize: `udf_late_allocate_buf()`, `udf_grow_node()`, `udf_shrink_node()`, `udf_resize_node()`.
- Free-space calculation: `udf_calc_freespace()`.

### Node Lifecycle

Node-related declarations include:
- Unique ID advancement: `udf_advance_uniqueid()`.
- Lock wrappers: `UDF_LOCK_NODE()` and `UDF_UNLOCK_NODE()` record source file/line for lock debugging.
- Node locking functions: `udf_lock_node()`, `udf_unlock_node()`.
- Node lookup/write/dispose: `udf_get_node()`, `udf_writeout_node()`, `udf_dispose_node()`.
- Node tree and ICB helpers: `udf_init_nodes_tree()`, `udf_get_node_id()`, `udf_compare_icb()`.

### File Buffer I/O and Disc Strategy

The header declares:
- File buffer read/write entry points: `udf_read_filebuf()`, `udf_write_filebuf()`.
- Descriptor fixup helpers: `udf_fixup_fid_block()`, `udf_fixup_internal_extattr()`, `udf_fixup_node_internals()`.
- Disc strategy lifecycle and queueing: `udf_discstrat_init()`, `udf_discstrat_finish()`, `udf_discstrat_queuebuf()`.

### Descriptor Creation and Identity

Shared creators include:
- `udf_write_terminator()`
- `udf_inittag()`
- `udf_set_regid()`
- `udf_add_domain_regid()`
- `udf_add_udf_regid()`
- `udf_add_impl_regid()`
- `udf_add_app_regid()`

### Directory and Name Handling

Directory helpers:
- `udf_osta_charset()`
- `udf_read_fid_stream()`
- `udf_lookup_name_in_dir()`
- `udf_create_node()`
- `udf_delete_node()`
- `udf_chsize()`
- `udf_dir_detach()`
- `udf_dir_attach()`
- `udf_dir_update_rootentry()`
- `udf_dirhash_fill()`

Name conversion:
- `udf_to_unix_name()`
- `unix_to_udf_name()`

### Times, Modes, Ownership

The header exposes:
- Dirty list helpers: `udf_add_to_dirtylist()`, `udf_remove_from_dirtylist()`.
- Timestamp update: `udf_itimes()`, `udf_update()`.
- Access mode and ownership conversion: `udf_getaccessmode()`, `udf_setaccessmode()`, `udf_getownership()`, `udf_setownership()`.
- UDF timestamp conversion: `udf_timestamp_to_timespec()`, `udf_timespec_to_timestamp()`.

### Vnode Operations

The header declares UDF vnode operation entry points:
- Lifecycle: `udf_inactive()`, `udf_reclaim()`.
- Attribute/path/access: `udf_getattr()`, `udf_setattr()`, `udf_pathconf()`, `udf_access()`.
- Open/close/read/write: `udf_open()`, `udf_close()`, `udf_read()`, `udf_write()`.
- Lookup and creation/removal: `udf_lookup()`, `udf_create()`, `udf_mknod()`, `udf_link()`, `udf_symlink()`, `udf_rename()`, `udf_remove()`, `udf_mkdir()`, `udf_rmdir()`.
- Directory/symlink: `udf_readdir()`, `udf_readlink()`.
- Strategy/fsync/locking: `udf_trivial_bmap()`, `udf_vfsstrategy()`, `udf_fsync()`, `udf_advlock()`.

## Design Role

This header is the internal coupling point for the UDF implementation. It makes the filesystem’s mount, vnode, allocation, descriptor, directory, and media-strategy layers visible to one another. The API is broad and exposes many concrete on-disc UDF concepts directly, which matches the implementation style of this filesystem: explicit descriptor manipulation rather than a narrow abstraction boundary.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_subr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_vfsops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf_vfsops.c

## Purpose

`udf_vfsops.c` implements NetBSD VFS operations for the UDF filesystem. It is the mount-level entry point that registers the filesystem, allocates/frees mount state, opens and closes the backing block device, performs mount-time UDF discovery through `udf_subr.c`, exposes root/stat/sync operations, and rejects unsupported VFS features.

## Module and VFS Registration

The file defines:
- `MODULE(MODULE_CLASS_VFS, udf, NULL)`.
- Global `udf_verbose` debug mask.
- UDF malloc types: `M_UDFMNT`, `M_UDFVOLD`, `M_UDFTEMP`.
- Global `udf_node_pool`.
- `udf_vnodeopv_descs`.
- `struct vfsops udf_vfsops`.

The `udf_vfsops` table wires:
- Mount lifecycle: `udf_mount`, `udf_start`, `udf_unmount`, `udf_mountroot`.
- Accessors: `udf_root`, `udf_statvfs`.
- Sync: `udf_sync`.
- Vnode cache integration: `udf_vget`, `udf_loadvnode`, `udf_newvnode`.
- File handle operations: `udf_fhtovp`, `udf_vptofh`.
- Init/reinit/done: `udf_init`, `udf_reinit`, `udf_done`.
- Snapshot/extattr/suspend/rename lock hooks.

Unsupported or stubbed operations include quotas, fs-level fsync, root mount, NFS-style vget/file handles, and snapshots.

## Initialization and Teardown

`udf_init()`:
- Attaches malloc types.
- Initializes `udf_node_pool` sized for `struct udf_node`.

`udf_reinit()`:
- No-op.

`udf_done()`:
- Destroys `udf_node_pool`.
- Detaches malloc types.

`udf_modcmd()`:
- Attaches or detaches `udf_vfsops` on module init/fini.
- Returns `ENOTTY` for unknown module commands.

The file also creates a debug sysctl node under `vfs.udf`; when `UDF_DEBUG` is enabled, it exposes writable `verbose`.

## Mount State Freeing

`free_udf_mountinfo()` frees:
- Anchors.
- Primary/logical/unallocated/implementation/logical-integrity descriptors.
- Partition descriptors and unallocated/freed descriptors.
- Metadata unallocated descriptor.
- Fileset descriptor and sparing table.
- Late-allocation mapping buffers.
- VAT table.
- Mount mutexes.
- The `struct udf_mount`.

`udf_release_system_nodes()` releases retained system vnodes:
- VAT node.
- Metadata node.
- Metadata mirror node.
- Metadata bitmap node.

## Mount Flow

`udf_mount()` handles:
- Argument validation and `MNT_GETARGS`.
- Rejects `MNT_UPDATE` with `EOPNOTSUPP`.
- Verifies mount argument version.
- Resolves the device path with `namei_simple_user()`.
- Requires a block device with a valid bdev switch.
- Authorizes read/write mount access via kauth.
- Opens the device with `VOP_OPEN()`.
- Calls `udf_mountfs()` to read and validate the filesystem.
- On failure, releases system nodes, finishes disc strategy, frees mount state, closes the device, and releases the vnode.
- Registers the mount on the special device with `spec_node_setmountedfs()`.
- Sets statvfs metadata.
- For writable mounts, calls `udf_open_logvol()`. If logical volume open fails, it downgrades to read-only rather than failing the already-mounted filesystem.

The writable-open downgrade is explicitly marked with a FIXME because the mount has progressed too far to return the open error cleanly.

## Actual Filesystem Mounting

`udf_mountfs()` performs the real UDF discovery:
1. Invalidates stale device buffers with `vinvalbuf()`.
2. Initializes mount stat fields, fsid, name length, and `MNT_LOCAL`.
3. Allocates and initializes `struct udf_mount`.
4. Initializes `logvol_mutex`, `allocate_mutex`, and `sync_lock`.
5. Initializes the node rbtree.
6. Stores mount args and device vnode.
7. Calls `udf_update_discinfo()`.
8. Validates sector size:
   - Must be a power of two.
   - Sector sizes `>= 8192` are rejected as an implementation limit.
9. For writable mounts:
   - Requires recordable media.
   - Rejects full sequential media.
   - Rejects updating previous sessions.
10. Starts bootstrap disc strategy.
11. Reads anchors using `udf_read_anchors()`.
12. Reads VDS space with `udf_read_vds_space()`.
13. Stops bootstrap strategy.
14. Processes VDS with `udf_process_vds()`.
15. Starts selected final disc strategy.
16. Allocates late-allocation mapping buffers and node allocation descriptor copy space.
17. Sets mount block-size shifts.
18. Reads VDS support tables through `udf_read_vds_tables()`.
19. Requires logical volume integrity to be closed; otherwise asks for fsck and returns `EPERM`.
20. Reads root directories with `udf_read_rootdirs()`.

This function is the bridge between generic NetBSD VFS mount setup and UDF-specific format interpretation in `udf_subr.c`.

## Unmount Flow

`udf_unmount()`:
- Gets `struct udf_mount`.
- Optionally performs debug sanity checks.
- Flushes non-system vnodes with `vflush(..., SKIPSYSTEM)`.
- Calls `udf_sync(..., FSYNC_WAIT, ...)`.
- Flushes again to ensure no busy non-system vnodes remain.
- Calls `udf_close_logvol()` to close writable logical volume/session.
- Releases retained system nodes.
- Flushes all remaining vnodes; failure is considered panic-worthy for system vnodes.
- Finishes disc strategy.
- Synchronizes caches.
- Closes the backing device.
- Clears mountedfs association on the special vnode.
- Releases the device vnode with `vput()`.
- Frees UDF mount info.
- Clears `mp->mnt_data` and `MNT_LOCAL`.

## Root and Statvfs

`udf_root()`:
- Uses `fileset_desc->rootdir_icb`.
- Calls `udf_get_node()` to get the root node.
- Verifies `VV_ROOT`.
- Returns the root vnode.

`udf_statvfs()`:
- Fills block size, fragment size, I/O size, flags.
- Locks `allocate_mutex`.
- Calls `udf_calc_freespace()`.
- Reads file/directory counts from logical volume integrity implementation data.
- Sets available/reserved counts mostly to zero.
- Calls `copy_statvfs_info()`.

The comment notes read-only behavior around available block reporting.

## Sync

`udf_sync_writeout_system_files()`:
- Writes VAT if requested.
- Writes metadata and physical partition bitmaps if requested.
- Clears bitmap write flags when successful and requested.

`udf_sync()`:
- Returns immediately on read-only mounts.
- Skips autosync if another sync is already in progress.
- Sets `ump->syncing`.
- Calls `udf_do_sync()` for vnode/data sync.
- On `MNT_WAIT`, writes system files/bitmaps synchronously.
- Clears `ump->syncing`.

`udf_do_sync()` itself is implemented in `udf_subr.c`.

## Unsupported VFS Features

The file returns `EOPNOTSUPP` for:
- `udf_mountroot()`
- `udf_vget()`
- `udf_fhtovp()`
- `udf_vptofh()`
- `udf_snapshot()`

This means:
- UDF cannot be used as NetBSD root filesystem through this path.
- NFS/export-style stable file handle lookup is not implemented.
- Filesystem snapshots are not implemented.

## Dependencies

This file depends on:
- NetBSD VFS, vnode, mount, module, sysctl, kauth, specfs, genfs, buf, and block device APIs.
- UDF mount and descriptor structures from `ecma167-udf.h`, `udf_mount.h`, `udf.h`, `udf_subr.h`, and `udf_bswap.h`.
- UDF support functions implemented mostly in `udf_subr.c` and sibling UDF files.

## Notable Constraints and Risks

- `MNT_UPDATE` is not supported.
- Mount arguments have only basic validation beyond version.
- Writable mounts on unsupported media are rejected early, but failure to open the logical volume after mount discovery downgrades to read-only.
- Sector size support is capped below 8192 bytes.
- Dirty logical volume integrity blocks mount and requires fsck.
- File handle and snapshot operations are stubs.
- Unmount can panic if system vnodes fail to flush after system-node release.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_vfsops.c -->