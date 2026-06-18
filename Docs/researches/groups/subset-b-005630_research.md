# Research Group: subset-b-005630

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/volumes.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/volumes.h

## Purpose

`volumes.h` is the central public contract for Btrfs multi-device and chunk-mapping behavior. It defines the in-memory device model, filesystem device set model, RAID profile attributes, chunk-map representation, IO mapping context, device lookup arguments, and exported operations for scanning, opening, resizing, balancing, replacing, mapping, and validating devices and chunks. Other Btrfs subsystems use this header to translate logical filesystem addresses into physical device stripes, track device state, and coordinate allocation policy, including zoned allocation policy through `BTRFS_CHUNK_ALLOC_ZONED`.

## Important APIs, Types, And Functions

Core constants include `BTRFS_STRIPE_LEN`, `BTRFS_MAX_DATA_CHUNK_SIZE`, `BTRFS_MAX_DISCARD_CHUNK_SIZE`, and the `BTRFS_DEV_STATE_*` bit indexes. The `BTRFS_BG_FLAG_TO_INDEX()` conversion and `enum btrfs_raid_types` map on-disk block-group profile bits to compact internal RAID indexes. Static assertions protect this on-disk-to-in-memory mapping.

`struct btrfs_device` represents one member device. Important fields include `devid`, UUID, `bdev_file`, `bdev`, `zone_info`, `dev_state`, size accounting (`total_bytes`, `disk_total_bytes`, `bytes_used`, `commit_*`), flush state, scrub state, dev stats, sysfs kobject state, allocation extent tree, and per-profile temporary accounting. The 64-bit size fields are accessed through generated `btrfs_device_get_*()` and `btrfs_device_set_*()` helpers; on 32-bit SMP they use `seqcount_t`, and on preemptible 32-bit they disable preemption.

`struct btrfs_fs_devices` groups all devices for one filesystem identity. It stores `fsid`, `metadata_uuid`, device counts, open/read-write counts, seed lists, mount/holding counters, sysfs roots, read policy, allocation policy, and per-profile availability estimates protected by `per_profile_lock`.

`struct btrfs_io_context` is the logical-to-physical mapping result used during bio submission. It records the map type, original bio, logical range, mirror number, stripe array, device-replace duplicate stripe data, RAID56 full-stripe metadata, and refcounting. `struct btrfs_chunk_map` is the persistent mapping tree node with logical start, length, stripe size, RAID type, stripe count, and physical stripe array. `btrfs_free_chunk_map()` releases it when refs drop to zero and asserts it is not still in the rb-tree.

Exported APIs include `btrfs_map_block()`, `btrfs_map_repair_block()`, `btrfs_map_discard()`, `btrfs_read_sys_array()`, `btrfs_read_chunk_tree()`, `btrfs_create_chunk()`, `btrfs_open_devices()`, `btrfs_scan_one_device()`, `btrfs_close_devices()`, `btrfs_rm_device()`, `btrfs_grow_device()`, `btrfs_shrink_device()`, `btrfs_init_new_device()`, balance control functions, dev-stat functions, chunk-map lookup/update helpers, superblock IO helpers, device extent verification, per-profile availability helpers, and pending extent helpers.

## Control Flow And Integration

Mount-time code scans devices into `btrfs_fs_devices`, opens them, reads superblocks and chunk trees, and constructs `btrfs_chunk_map` entries. IO submission calls `btrfs_map_block()` or repair/discard variants to translate logical ranges into `btrfs_io_context` stripes. Chunk allocation and deletion paths use the chunk creation/removal prototypes and update device size accounting. Balance, relocation, replace, scrub, sysfs, and zoned code all share the device/chunk objects defined here.

The header also routes bio operations through `btrfs_op()`, where writes and zone appends map to `BTRFS_MAP_WRITE` and reads map to `BTRFS_MAP_READ`. RAID helpers and exported `btrfs_bg_*` routines provide profile names, factors, parity counts, and indexes used by allocation, sysfs reporting, and zoned profile validation.

## State And Persistence Behavior

Device and chunk state spans memory and disk. `struct btrfs_device` tracks in-memory open state, runtime flags, IO stats, sysfs objects, and transaction-local size values, while `disk_total_bytes`, `commit_total_bytes`, and chunk/dev item update APIs connect the state to on-disk metadata. `struct btrfs_fs_devices` keeps global identity and membership state across mount, seed, temp-fsid, and metadata-uuid modes. Device stats are atomic and paired with `dev_stats_ccnt` barriers so `btrfs_run_dev_stats()` can persist coherent changes. Chunk maps mirror on-disk chunk tree items and drive all logical-to-physical persistence semantics.

## Dependencies

This header depends on Linux block, bio, list, mutex, refcount, completion, kobject, rbtree, sort, atomic, and UAPI Btrfs definitions. It includes Btrfs `messages.h`, `extent-io-tree.h`, and `fs.h`, and forward declares transaction, block-group, zoned-device, and space-info structures. It is consumed by volume management, disk IO, bio, scrub, sysfs, zoned, balance, device replace, and allocation code.

## Risks And Edge Cases

The RAID index mapping is tied to on-disk bits; incorrect changes would corrupt profile interpretation. Device size access needs the 32-bit ordering helpers to avoid torn reads. The `dev_state` bit contract is broad and must remain consistent across mount, replace, missing-device, flush, and sysfs paths. `btrfs_io_context` flexible-array sizing and refcounting are sensitive to stripe-count calculations, especially for device replace and RAID56. Device stats require correct memory barriers or transaction persistence can miss increments. UUID and holding counters require `uuid_mutex` as asserted by helper functions.

## Test Signals

High-value tests include mount and remount with single, multi-device, missing-device, seed, temp-fsid, and metadata-uuid configurations; logical-to-physical mapping for all supported RAID profiles; device add/remove/grow/shrink/replace; dev-stat increment/read/reset persistence; chunk-map lookup/removal refcount tests; balance and relocation tests; 32-bit or KCSAN coverage for size accessors; and zoned-mode integration where `zone_info` and zoned allocation policy are populated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/volumes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/xattr.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/xattr.c

## Purpose

`xattr.c` implements Btrfs extended attribute operations and VFS xattr handlers. It stores xattrs as `BTRFS_XATTR_ITEM_KEY` dir-item payloads in the inode root, supports get/set/remove/list operations, wires security/trusted/user/Btrfs-property namespaces into the VFS, and initializes security xattrs during inode creation.

## Important APIs, Types, And Functions

`btrfs_getxattr()` allocates a path, looks up the named xattr with `btrfs_lookup_xattr()`, returns the size for zero-length probes, validates the caller buffer, and reads the packed dir-item data from the leaf.

`btrfs_setxattr()` is the low-level transaction-aware mutation helper. It enforces `BTRFS_MAX_XATTR_SIZE()`, handles remove when `value == NULL`, respects `XATTR_REPLACE` and `XATTR_CREATE`, inserts with `btrfs_insert_xattr_item()`, and performs atomic replacement for existing packed dir-items by extending, truncating, or deleting/re-extending the item as needed. On success it sets `BTRFS_INODE_COPY_EVERYTHING` and clears `BTRFS_INODE_NO_XATTRS`.

`btrfs_setxattr_trans()` wraps `btrfs_setxattr()` in a transaction unless the caller already has `current->journal_info`. The existing-transaction path exists for security hooks such as Smack during directory creation. After a successful mutation it increments inode version, updates ctime, writes the inode item, and aborts the transaction on update failure.

`btrfs_listxattr()` walks all xattr items for the inode with `btrfs_for_each_slot()`, iterates packed `struct btrfs_dir_item` records inside each leaf item, accounts names plus NUL terminators, and copies names to the VFS buffer or returns the required size.

Handler functions translate VFS namespace-relative names through `xattr_full_name()`. Security handlers maintain a negative cache bit for `security.capability` (`BTRFS_INODE_NO_CAP_XATTR`). Property handlers validate and route `btrfs.*` xattrs through `btrfs_validate_prop()`, `btrfs_ignore_prop()`, and `btrfs_set_prop()`. `btrfs_initxattrs()` receives LSM-provided security xattrs, prepends `security.`, and sets each under `memalloc_nofs_save()`. `btrfs_xattr_security_init()` exposes this to inode creation through `security_inode_init_security()`.

## Control Flow And Integration

Reads are path lookup plus leaf-buffer copy. Mutations start from VFS handlers, reject readonly roots, assemble full names, and enter `btrfs_setxattr_trans()` or property-specific transaction code. The low-level set path first resolves remove/replace/create semantics, then either inserts a new dir item or atomically updates an existing record in-place or by replacing only that packed name. Successful mutations update inode metadata and transaction state.

The xattr list path scans from `(ino, BTRFS_XATTR_ITEM_KEY, 0)` forward and stops when objectid or item type leaves the inode's xattr range. Security initialization integrates with LSM inode hooks and uses an existing transaction from create/mkdir code.

## State And Persistence Behavior

Xattrs persist in the Btrfs tree as dir-item records under the inode number and `BTRFS_XATTR_ITEM_KEY`. Multiple xattrs may be packed into a single leaf item, so replacement must preserve visibility of either old or new values and avoid transient missing ACL/security values. Inode ctime and i_version are updated for set/remove operations. Runtime flags cache absence of xattrs or capabilities but are corrected on successful mutations.

## Dependencies

The file depends on Linux VFS xattr, LSM security, POSIX ACL xattr constants, inode versioning, and memory allocation contexts. Btrfs dependencies include tree paths, dir-item helpers, transactions, inode update, root readonly checks, property validation, locking assertions, extent-buffer accessors, and disk IO.

## Risks And Edge Cases

Packed dir-item updates are high risk: item size, name length, data length, and slot position must stay coherent after truncate/extend/delete. `XATTR_REPLACE` relies on inode locking to avoid races with concurrent delete. `value == NULL` means remove, while a zero-length non-NULL value means an empty xattr. Buffer sizing must return `-ERANGE` without partial semantic corruption. Security capability negative caching must be cleared when setting capabilities. Property xattrs have separate validation and may be ignored without persistence.

## Test Signals

Test with `getfattr`/`setfattr` for user, trusted, security, ACL, and `btrfs.*` properties; create-only, replace-only, remove, empty-value, and oversized xattrs; list buffer size probes and small-buffer `-ERANGE`; concurrent set/remove under inode locking; readonly subvolume rejection; LSM security initialization during file and directory creation; capability xattr negative-cache behavior; and fsync/send behavior that depends on `BTRFS_INODE_COPY_EVERYTHING`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/xattr.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/xattr.h

## Purpose

`xattr.h` declares the Btrfs xattr interface shared by inode, VFS, security, and property code. It exposes the handler table installed on Btrfs inodes plus the direct get/set/list/security-init helpers implemented in `xattr.c`.

## Important APIs, Types, And Functions

The header forward declares `dentry`, `inode`, `qstr`, `xattr_handler`, and `btrfs_trans_handle`. `btrfs_xattr_handlers[]` is the VFS namespace handler table. `btrfs_getxattr()`, `btrfs_setxattr()`, `btrfs_setxattr_trans()`, and `btrfs_listxattr()` provide direct xattr operations. `btrfs_xattr_security_init()` initializes security xattrs during inode creation using an existing transaction handle.

## Control Flow And Integration

VFS inode setup references `btrfs_xattr_handlers[]`, while Btrfs create paths can call `btrfs_xattr_security_init()` after inode allocation. Internal callers with an existing transaction can use `btrfs_setxattr()` directly; generic VFS handler paths use `btrfs_setxattr_trans()` so transaction lifetime, inode ctime, and inode item update are handled consistently.

## State And Persistence Behavior

The header itself stores no state, but its API boundary controls whether callers supply a transaction or request transaction management. That distinction matters for persistence ordering, especially during inode creation when security xattrs must be inserted under the same transaction as the new inode.

## Dependencies

It depends only on Linux `types.h` and forward declarations, keeping compile-time coupling low. Implementations require `xattr.c`, transaction handling, dir-item storage, and VFS xattr infrastructure.

## Risks And Edge Cases

The main risk is using the wrong entry point: calling `btrfs_setxattr()` without a valid transaction violates its assertion, while starting a nested transaction during create/security hooks can disturb reserved block state. Prototype changes must remain synchronized with VFS handler expectations and security initialization call sites.

## Test Signals

Build coverage should catch prototype drift. Runtime signals come from security xattr initialization, VFS xattr handler registration, direct transaction callers, and xattr list/get/set/remove tests described for `xattr.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/xattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/zlib.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/zlib.c

## Purpose

`zlib.c` implements the Btrfs zlib compression backend. It allocates zlib workspaces, compresses filemap folios into compressed bios, decompresses compressed bios into target pages, and supports single-sector inline decompression. It also contains a special input-buffer path for s390 zlib hardware acceleration.

## Important APIs, Types, And Functions

`struct workspace` wraps `z_stream`, a scratch buffer, buffer size, list node, and compression level. `zlib_get_workspace()` retrieves a generic Btrfs compression workspace and records the requested level. `zlib_alloc_workspace()` allocates the zlib workspace memory, scratch buffer, and stream workspace. `zlib_free_workspace()` releases all allocations.

`need_special_buffer()` detects s390 DFLTCC hardware acceleration and requests a 4-page buffer when the filesystem folio size is too small. `copy_data_into_buffer()` gathers input filemap data into that buffer so hardware compression receives a larger contiguous input span.

`zlib_compress_bio()` initializes deflate, streams input folios from the file mapping, fills compressed output folios, and appends them to `cb->bbio.bio`. It aborts with `-E2BIG` if compression expands data past useful thresholds or bio append fails, with `-ENOMEM` on allocation failure, and with `-EIO` on zlib failures.

`zlib_decompress_bio()` maps compressed bio folios, optionally skips the zlib header and adler32 path for raw deflate when safe, inflates into the workspace buffer, and feeds output to `btrfs_decompress_buf2page()`. `zlib_decompress()` handles the smaller direct decompression path into a destination folio and zero-fills any short output. `btrfs_zlib_compress` declares supported levels 1 through 9 and the default.

## Control Flow And Integration

Compression starts from the generic Btrfs compression framework with a `compressed_bio`. The backend initializes zlib, obtains input from the inode mapping via `btrfs_compress_filemap_get_folio()`, maps folios with `kmap_local_folio()`, and pushes full or partial compressed folios into the bio. Once all input is consumed it repeatedly calls deflate with `Z_FINISH` until `Z_STREAM_END`.

Bio decompression iterates compressed bio folios using `folio_iter`, inflates into a sector-sized or special workspace buffer, and copies decompressed ranges into the original compressed-bio destination pages. The direct decompression path assumes both compressed input and decompressed output fit within one sector-sized workspace.

## State And Persistence Behavior

The file has no on-disk metadata logic of its own. Its persistent effect is the compressed byte stream stored by higher Btrfs writeback code. Workspace objects are reusable runtime state and keep no cross-call compression history after `zlib_deflateEnd()` or `zlib_inflateEnd()`. Error returns tell the compression framework whether to store data uncompressed (`-E2BIG`) or fail IO (`-EIO`, `-ENOMEM`).

## Dependencies

It depends on Linux zlib/zutil, bio, folio/page mapping, slab/vmalloc allocation, and Btrfs compression helpers (`compression.h`, `btrfs_inode.h`, `fs.h`, `subpage.h`). The implementation relies on `btrfs_min_folio_size()`, `btrfs_alloc_compr_folio()`, `btrfs_free_compr_folio()`, `btrfs_calc_input_length()`, and `btrfs_decompress_buf2page()`.

## Risks And Edge Cases

The main risks are folio lifetime and local mapping balance, output-size accounting, and correctly freeing the last unused output folio. The s390 special buffer path copies across potentially multiple folios and must advance `start` and `avail_in` accurately. Header-skipping logic must only use raw inflate when the input is recognizable deflate without preset dictionary. Short decompression must zero-fill to avoid exposing stale data. Compression expansion detection must be conservative enough to avoid writing compressed extents larger than the original.

## Test Signals

Useful signals include mount/write/read tests with `compress=zlib` at levels 1, default, and 9; incompressible data fallback; compressed reads across multiple folios and subpage sectors; inline/direct decompression; fault injection for workspace and output folio allocation; corrupt compressed extent read errors; fstests compression coverage; and architecture coverage for DFLTCC-enabled s390 systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/zlib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/zoned.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/zoned.c

## Purpose

`zoned.c` implements Btrfs zoned block device support. It discovers device zone geometry, validates zoned mode, manages superblock log zones, computes block-group allocation/write pointers from zone state, tracks active zones, serializes metadata and relocation writes, handles zone append completion rewrites, finishes and resets zones, reserves relocation block groups, and reports zoned runtime statistics.

## Important APIs, Types, And Functions

Zone discovery starts with `btrfs_get_dev_zone_info_all_devices()` and `btrfs_get_dev_zone_info()`. These allocate `struct btrfs_zoned_device_info`, determine zone size and count, allocate `seq_zones`, `empty_zones`, and `active_zones` bitmaps, optionally allocate a zone cache, report or emulate zones, validate active-zone limits, and validate superblock log zone pairs. `btrfs_destroy_dev_zone_info()` and `btrfs_clone_dev_zone_info()` manage lifetime and device-replace cloning.

Superblock log support is built around `sb_write_pointer()`, `sb_log_location()`, `btrfs_sb_log_location_bdev()`, `btrfs_sb_log_location()`, `btrfs_advance_sb_log()`, and `btrfs_reset_sb_log_zones()`. Zoned devices use two sequential zones per mirror as a circular log. When both are full, the latest superblock generation is selected. Write-side location can reset the next full zone before reuse.

Mode validation is handled by `btrfs_check_zoned_mode()` and `btrfs_check_mountopts_zoned()`. They reject host-managed zoned devices without the incompat flag, require equal zone sizes, validate queue limits, require stripe alignment to zone size, disallow mixed block groups, disable async discard, reject space cache v1 and NODATACOW, set `fs_info->zone_size`, `max_zone_append_size`, chunk allocation policy, and max extent size.

Allocation and block-group loading are centered on `btrfs_load_block_group_zone_info()`. It finds the chunk map, loads per-stripe zone state with `btrfs_load_zone_info()`, computes conventional fallback allocation pointers via `calculate_alloc_pointer()`, and dispatches profile-specific logic through `btrfs_load_block_group_by_raid_type()`. Profile helpers handle SINGLE, DUP, RAID1/1C3/1C4, RAID0, and RAID10 write-pointer reconstruction, capacity computation, active-state reconciliation, degraded handling, and raid-stripe-tree requirements for non-single data profiles.

Runtime zone management includes `btrfs_find_allocatable_zones()`, `btrfs_reset_device_zone()`, `btrfs_ensure_empty_zones()`, `btrfs_calc_zone_unusable()`, `btrfs_zone_activate()`, `btrfs_zone_finish()`, `btrfs_can_activate_zone()`, `btrfs_zone_finish_one_bg()`, `btrfs_zoned_activate_one_bg()`, `btrfs_check_active_zone_reservation()`, and `btrfs_reset_unused_block_groups()`.

IO-specific functions include `btrfs_use_zone_append()`, `btrfs_record_physical_zoned()`, `btrfs_finish_ordered_zoned()`, `btrfs_check_meta_write_pointer()`, `btrfs_zoned_issue_zeroout()`, and `btrfs_sync_zone_write_pointer()`.

## Control Flow And Integration

During mount, Btrfs reads or emulates each device's zone information, validates the filesystem's zoned mode, builds per-block-group write pointer state, and registers active block groups. Device zone bitmaps become the source of truth for sequential, empty, and active status. The chunk allocator uses `btrfs_find_allocatable_zones()` and active-zone checks to avoid superblock locations and active-zone exhaustion.

For data writes, `btrfs_use_zone_append()` selects `REQ_OP_ZONE_APPEND` only for regular data in sequential block groups and avoids relocation. Zone append can return a physical address different from the planned one, so `btrfs_record_physical_zoned()` adjusts checksum logicals and `btrfs_finish_ordered_zoned()` splits or rewrites ordered extents when completion sums are not contiguous.

Metadata writes are serialized around `meta_write_pointer`. `btrfs_check_meta_write_pointer()` caches or finds the containing block group, verifies the extent buffer starts at the current metadata write pointer, activates or pivots active metadata/system block groups if active-zone tracking requires it, and returns `-EAGAIN` or `-EBUSY` when holes or writeback ordering prevent immediate write.

Finishing a zone proceeds through `do_zone_finish()`: it verifies active state, waits for reservations, ordered extents, and metadata writeback when needed, marks the block group full/unallocatable, issues `REQ_OP_ZONE_FINISH` on sequential stripes, updates active-zone accounting and reservations, removes the block group from the active list, and wakes waiters on `BTRFS_FS_NEED_ZONE_FINISH`.

Relocation support reserves a dedicated data relocation block group via `btrfs_zoned_reserve_data_reloc_bg()`, migrating an empty data block group to the relocation space-info or allocating a new one. `btrfs_zoned_release_data_reloc_bg()` releases the flag after relocated writes reach the expected end.

## State And Persistence Behavior

Persistent zoned state is partly on disk and partly reconstructed from block device zone write pointers. Superblock mirrors are persisted as log records in two zones per mirror. Block-group `alloc_offset`, `zone_capacity`, `zone_unusable`, `meta_write_pointer`, `physical_map`, and runtime flags are reconstructed at mount and maintained during writes. Device bitmaps track runtime zone classifications and active-zone budget; empty/active bits are updated after reset, allocation, activation, and finish. The chunk tree and extent tree remain the persistent logical metadata, while write pointer reconciliation prevents allocating or writing behind the device's sequential constraints.

## Dependencies

The file depends on Linux zoned block APIs (`blkdev_report_zones_cached`, `blkdev_zone_mgmt`, `blkdev_issue_zeroout`, zone capacity/open/active limits), block queue limits, bitmaps, vmalloc, atomic counters, and memory-allocation scope controls. Btrfs dependencies include chunk maps and mapping (`volumes.h`), block-group and space-info management, transaction and chunk allocation, device replace locking, ordered extents, extent buffers, sysfs, bio mapping, checksum sums, relocation, and mount option handling.

## Risks And Edge Cases

Superblock log state has complex valid/invalid combinations; corruption returns `-EUCLEAN`. Zone sizes must be power-of-two, aligned to stripe length, equal across devices, and within supported min/max. Active-zone accounting is delicate because metadata/system reservations, data allocations, and device limits interact. Mixed conventional/sequential devices require emulated or calculated pointers and validation that no extents exist beyond write pointers. RAID0/RAID10 write-pointer reconstruction must handle partial stripes and stripe ordering. Metadata write pointer holes can deadlock if writeback waits in the wrong context. Device replace must sync target write pointers with zeroout and missing/failing devices can cause degraded-specific behavior. Resetting unused block groups bypasses deletion and must update `bytes_zone_unusable`, free-space control, and device zones coherently.

## Test Signals

Important tests include mounting zoned and non-zoned devices with and without the incompat flag; mixed regular/zoned emulation; invalid zone sizes and active-zone limits; superblock log read/write/reset after wraparound and corruption; allocation skipping superblock zones; block-group loading for SINGLE, DUP, RAID1/1C3/1C4, RAID0, and RAID10; degraded mount scenarios; zone append data writes with checksum logical rewrites and ordered extent splits; metadata writeback ordering and active metadata/system block-group pivoting; zone finish under full, partially written, reserved, relocation, and writeback-heavy cases; data relocation block-group reservation/release; unused block-group reset/reclaim; and sysfs or debugfs stat output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/zoned.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/zoned.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/zoned.h

## Purpose

`zoned.h` declares the Btrfs zoned-mode API and defines the per-device zoned information structure plus inline helpers. It lets the rest of Btrfs compile against zoned functionality whether `CONFIG_BLK_DEV_ZONED` is enabled or not, using real prototypes in zoned builds and conservative stubs otherwise.

## Important APIs, Types, And Functions

`struct btrfs_zoned_device_info` stores zone size, shift, count, maximum active zones, reserved active zones, active-zone budget, bitmaps for sequential/empty/active zones, optional zone cache, and cached superblock log zones. The header declares mount/device discovery, superblock log, allocation, reset, block-group loading, IO, active-zone, relocation, reclaim, and stats functions implemented in `zoned.c`.

When zoned support is disabled, inline stubs mostly return success for no-op functions on non-zoned filesystems, return `-EOPNOTSUPP` for operations that cannot be emulated, and reject a zoned filesystem in `btrfs_check_zoned_mode()`.

Inline helpers include `btrfs_dev_is_sequential()`, `btrfs_dev_is_empty_zone()`, zone empty bit setters, `btrfs_check_device_zone_type()`, `btrfs_check_super_location()`, `btrfs_can_zone_reset()`, metadata IO lock wrappers, tree-log/data-relocation lock and clear helpers, and `btrfs_zoned_bg_is_full()`.

## Control Flow And Integration

Mount and device open paths call the declared discovery and validation APIs. Allocation code uses allocatable-zone and active-zone helpers. Metadata writeback uses the zoned meta IO lock wrappers and write-pointer checks. Data writeback and ordered extent completion use zone append and physical-recording APIs. Relocation and reclaim use the reservation, release, finish, activate, and reset declarations.

The `#ifdef CONFIG_BLK_DEV_ZONED` boundary keeps call sites simple: most code can call zoned helpers unconditionally, and the header resolves them to no-ops or errors in non-zoned builds.

## State And Persistence Behavior

The header defines the in-memory state container for zone geometry, bitmaps, cache, and active-zone budget. Inline helpers mutate empty-zone bits and guard locks but do not persist state directly. Persistence is achieved by `zoned.c` through device write pointers, chunk/block-group metadata, and superblock log zones.

## Dependencies

It depends on Linux block zoned headers, atomic, spinlock, mutex, sequence-file support, and Btrfs `messages.h`, `volumes.h`, `disk-io.h`, `block-group.h`, and `btrfs_inode.h`. This coupling reflects the cross-cutting nature of zoned support across devices, IO, metadata writeback, and block-group allocation.

## Risks And Edge Cases

Stub behavior must match caller expectations in non-zoned builds; returning success for no-op paths is correct only when the filesystem is not zoned. Inline bit helpers assume positions align to the device zone size. `btrfs_check_device_zone_type()` must allow regular devices in zoned filesystems for emulation but reject zoned devices in non-zoned filesystems. Lock wrappers must only lock in zoned mode or they would impose unnecessary ordering constraints on regular filesystems.

## Test Signals

Build both with and without `CONFIG_BLK_DEV_ZONED`. Exercise non-zoned stubs by mounting regular filesystems in a kernel without zoned support and by rejecting zoned filesystems. Runtime zoned tests should validate inline helpers through allocation, reset, metadata writeback, tree-log clearing, data relocation serialization, and full block-group detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/zoned.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/zstd.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/zstd.c

## Purpose

`zstd.c` implements the Btrfs zstd compression backend and its per-filesystem workspace manager. It supports zstd levels -15 through 15, caps the window log to a Btrfs-specific maximum, streams filemap data into compressed bios, decompresses bios and inline extents, and reclaims idle workspaces with an LRU timer while preserving forward progress.

## Important APIs, Types, And Functions

`zstd_get_btrfs_parameters()` obtains zstd parameters for a level and source size, then caps `windowLog` at `ZSTD_BTRFS_MAX_WINDOWLOG` so input remains bounded by `ZSTD_BTRFS_MAX_INPUT`.

`struct workspace` stores allocated zstd memory, workspace size, sector-sized output buffer, actual and requested level, last-used timestamp, idle/LRU list links, zstd input/output buffers, and parameters. `struct zstd_workspace_manager` owns the spinlock, global LRU, idle lists by clipped level, active bitmap, waitqueue, and reclaim timer. `clip_level()` maps zstd's user-facing level range into internal slots.

Workspace lifecycle APIs include `zstd_alloc_workspace_manager()`, `zstd_free_workspace_manager()`, `zstd_alloc_workspace()`, `zstd_free_workspace()`, `zstd_get_workspace()`, and `zstd_put_workspace()`. `zstd_calc_ws_mem_sizes()` precomputes monotonic memory bounds so a higher-level workspace can safely serve a lower level. `zstd_reclaim_timer_fn()` frees idle reclaimable workspaces after `ZSTD_BTRFS_RECLAIM_JIFFIES`.

`zstd_compress_bio()` streams folios from the inode mapping into a zstd compression stream, writes compressed output into Btrfs compressed folios, appends them to the bio, and fails with `-E2BIG` when output grows too large. `zstd_decompress_bio()` streams compressed bio folios through a dstream and copies decompressed output to destination pages via `btrfs_decompress_buf2page()`. `zstd_decompress()` handles direct single-extent decompression into a destination folio. `btrfs_zstd_compress` exposes the level range and default level 3.

## Control Flow And Integration

At filesystem initialization, Btrfs allocates a zstd workspace manager and tries to preallocate a max-level workspace. Compression calls `zstd_get_workspace()`, which first searches idle workspaces at the requested or higher clipped level, then allocates under NOFS context, and finally waits for the protected max-level workspace if allocation fails. Returned workspaces are put back on level idle lists and possibly the LRU.

Compression initializes a zstd cstream with Btrfs-capped parameters, maps input folios one at a time, compresses into a min-folio-sized output buffer, appends full folios to the bio, then calls `zstd_end_stream()` until the frame is complete and appends the final partial folio. Decompression initializes a dstream with the max input bound, iterates bio folios, refills input when exhausted, drains output into a sector-sized workspace buffer, and stops when the destination pages are satisfied or the frame ends.

## State And Persistence Behavior

Persistent data is the zstd frame produced into compressed extents by higher-level writeback. Workspace manager state is runtime-only and scoped to `fs_info->compr_wsm[BTRFS_COMPRESS_ZSTD]`. Idle workspaces may outlive individual IOs until reclaimed by the timer; active_map and idle lists control reuse. Error returns distinguish fallback-worthy expansion (`-E2BIG`) from IO failures or memory pressure.

## Dependencies

The file depends on Linux zstd, bitmap, bio, folio/page mapping, timers, waitqueues, spinlocks, slab/vmalloc allocation, and NOFS allocation control. Btrfs dependencies include `compression.h`, `btrfs_inode.h`, `fs.h`, `misc.h`, and `super.h`, plus helpers for compressed folio allocation, input length calculation, filemap folio lookup, and decompression copyout.

## Risks And Edge Cases

Workspace management is concurrency-sensitive: idle lists, LRU list, active bitmap, `req_level`, and waitqueue wakeups must remain consistent under `spin_lock_bh()`. The max-level workspace is protected to guarantee forward progress under allocation failure. Negative zstd levels are mapped to the level-1 workspace size slot; monotonic sizing must remain valid when zstd parameter behavior changes. Compression must unmap and put input folios on every exit path. Bio size accounting must reject output equal to or larger than input. Decompression must handle truncated input, frame-end conditions, and short output by returning `-EIO` and zero-filling in the direct path.

## Test Signals

Useful tests include reads and writes with `compress=zstd` at negative, default, and high levels; incompressible data fallback; concurrent compression to exercise workspace reuse/waiting/reclaim; forced allocation failures to verify max-workspace forward progress; corrupt or truncated compressed extents; subpage and large-folio configurations; direct inline decompression; and timer-driven idle workspace cleanup during unmount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/zstd.c -->
