# Group Research: group_1828_winbtrfs_sources_windows_winbtrfs_src_treefuncs_c_sources_windows_w_14a60d20c8e5

Scope verified against `Docs/research_subset_a.md`: `sources/windows/winbtrfs` is included in subset A. All six listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/treefuncs.c -->
# File Research: sources/windows/winbtrfs/src/treefuncs.c

## Purpose

`treefuncs.c` implements WinBtrfs' in-memory Btrfs tree node lifecycle and mutation machinery. It loads tree blocks from disk into cached `tree` / `tree_data` structures, traverses B-tree leaves and internal nodes, inserts and deletes metadata items, maintains rollback records for failed filesystem updates, and commits batched metadata changes into dirty in-memory tree nodes.

This file is a core metadata layer used by directory, inode, extent, free-space, root, and chunk management code. It does not write serialized tree blocks by itself; instead it marks tree nodes dirty (`write = true`) and updates generation/size/item counters so later flush code can split/rewrite trees.

## Tree Loading and Cache Management

`load_tree` constructs a `tree` object from a raw tree block buffer already read from disk. It copies the `tree_header`, initializes internal-node locking state, builds the `itemlist`, and inserts the tree into both `Vcb->trees` and the sorted hash list `Vcb->trees_hash`.

Leaf nodes become `tree_data` entries pointing into the backing `buf` payload. Internal nodes become `tree_data` entries with `treeholder.address`, `treeholder.generation`, and a lazily populated child `tree` pointer. The loader validates that item arrays fit within `Vcb->superblock.node_size` and rejects oversized leaf items.

`do_load_tree` allocates a node-sized buffer, calls `read_data` with metadata verification and expected generation, and then serializes child/root installation under either the parent tree mutex or the root `load_tree_lock`. `do_load_tree2` avoids duplicate loads if another thread populated the holder first.

`free_tree`, `free_trees_root`, and `free_trees` tear down cached tree objects. They clear parent/root back-pointers, remove hash/list entries, free inserted leaf data separately from buffer-backed leaf data, and release node buffers/nonpaged locks. `free_trees` also reaps cached file references and FCBs after tree teardown.

## Traversal

The small helpers `first_item`, `prev_item`, `next_item`, and `last_item` wrap list navigation for a `tree`. `find_item_in_tree` performs the main B-tree descent: it finds the last key less than or equal to the search key, lazily loads child blocks, honors the `ignore` flag for logically deleted entries, and can stop at an arbitrary tree level for callers that need an internal node.

Public traversal APIs include:

- `find_item`: finds a leaf-level item at or before the requested key.
- `find_item_to_level`: like `find_item`, but may stop at a caller-specified internal level.
- `find_next_item`: walks to the next leaf item, loading right-side child paths as needed and optionally skipping ignored entries.
- `find_prev_item`: walks to the previous leaf item, loading left-side child paths as needed.
- `skip_to_difference`: advances two traversal pointers until their paths diverge or one side ends; this supports comparing related tree versions.

Important caveat: `find_prev_item` has a FIXME noting that it does not support an ignore flag. Callers relying on visible-only reverse traversal must account for this.

## Direct Item Mutation

`insert_tree_item` inserts one metadata item into a root. It loads the root if needed, rejects duplicate non-ignored keys, allocates a `tree_data`, inserts it in sorted order, updates parent separator keys when inserting before the first key, increments item/size counters, marks the leaf dirty, sets `Vcb->need_write`, and bumps generation on the modified leaf and ancestors.

`delete_tree_item` implements logical deletion by setting `tree_data.ignore`, decrementing the containing tree's visible item count and serialized size, marking the node dirty, and propagating the current superblock generation up the ancestor chain. It does not immediately unlink/free the item.

These direct mutation helpers require the global tree lock to be held exclusively.

## Rollback Support

`add_rollback` appends rollback records to a caller-owned list. `clear_rollback` frees rollback payloads without applying them. `do_rollback` walks the rollback list in reverse order and undoes space-list and extent-list mutations after failed higher-level operations.

Rollback cases cover:

- `ROLLBACK_INSERT_EXTENT`: re-ignores an inserted extent and decrements extent references/st_blocks.
- `ROLLBACK_DELETE_EXTENT`: restores a deleted extent and increments references/st_blocks.
- `ROLLBACK_ADD_SPACE` and `ROLLBACK_SUBTRACT_SPACE`: reverse free-space list and chunk-used accounting changes, coalescing same-chunk rollback records while holding the chunk lock.

Rollback interacts with chunk lookup, changed extent refs, inode `st_blocks`, and free-space list helpers. Error paths mostly log failures from reference updates and continue unwinding.

## Batched Metadata Changes

`clear_batch_list` frees uncommitted batch roots, index buckets, and batch items. `commit_batch_list` drains a list of `batch_root` entries and calls `commit_batch_list_root` for each root.

`commit_batch_list_root` flattens indexed batch sublists into one sorted list, then applies operations into tree leaves. It supports broad delete operations (`Batch_DeleteInode`, `Batch_DeleteExtentData`, `Batch_DeleteFreeSpace`) and point operations such as insert, delete, directory item update, inode ref update, extended inode ref update, xattr set/delete, and free-space item changes.

The function tries to batch consecutive operations that fall before the current leaf's tree-end key, reducing repeated full tree searches. It keeps inserted items sorted, updates counts/sizes, marks touched trees dirty, restores ignored parent separator entries when a child becomes visible again, and propagates the superblock generation upward.

## Collision Handling

`handle_batch_collision` resolves batch operations that target an existing visible item. It has specialized logic for packed Btrfs item types:

- `Batch_SetXattr`: replaces an existing xattr with the same name or appends a new one inside a `DIR_ITEM` payload, truncating to the node max length when needed.
- `Batch_DirItem`, `Batch_InodeRef`, `Batch_InodeExtRef`: appends another packed entry to the existing item payload.
- `Batch_InodeRef`: when an `INODE_REF` would overflow and extended inode refs are enabled, converts the operation into a `Batch_InodeExtRef`.
- `Batch_DeleteDirItem`, `Batch_DeleteInodeRef`, `Batch_DeleteInodeExtRef`, `Batch_DeleteXattr`: removes one packed subrecord, either deleting the whole item or inserting a replacement item with the remaining packed records.
- `Batch_DeleteInodeRef`: if a matching normal inode ref is not found and extended refs are enabled, adds a synthesized `Batch_DeleteInodeExtRef`.

After collision-specific processing, the old item is marked ignored and any replacement `tree_data` is inserted before it.

## Dependencies and Cross-File Interactions

This file depends on structures and helpers from `btrfs_drv.h`, checksum hashing from `crc32c.h`, and the block read path through `read_data`. It is called by metadata update code across the driver, including create/delete, extent-tree updates, free-space management, root updates, directory/xattr updates, and flush logic.

It assumes synchronization from `Vcb->tree_lock` for most public mutation/traversal entry points, uses per-tree fast mutexes during lazy child loading, and uses root load resources for root-node loading.

## Error Handling and Safety Notes

The code consistently returns `STATUS_INSUFFICIENT_RESOURCES` for allocation failures and logs structural corruption or unexpected duplicate keys. Many mutations rely on logical deletion via `ignore`; correct item counts and sizes depend on every collision/delete path decrementing only visible items.

Memory ownership is subtle: original leaf item data points into `tree->buf`, while inserted or replacement item data is separately allocated and freed only when `inserted` is true. Batch collision code transfers `bi->data` ownership into `tree_data` for successful inserts/replacements, while some delete-operation payloads are freed at batch cleanup.

Research follow-up should pair this file with the tree flush/split code, because this file prepares dirty in-memory metadata but does not show how overfull leaves/internal nodes are later serialized.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/treefuncs.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/ubtrfs/resource.h -->
# File Research: sources/windows/winbtrfs/src/ubtrfs/resource.h

## Purpose

`ubtrfs/resource.h` is the Visual Studio resource-editor header for the user-mode `ubtrfs` utility DLL resources. It contains no runtime filesystem logic.

## Contents

The file has the standard `//{{NO_DEPENDENCIES}}` generated header comments and AP Studio default ID definitions guarded by `APSTUDIO_INVOKED` and `APSTUDIO_READONLY_SYMBOLS`.

Defined defaults:

- `_APS_NEXT_RESOURCE_VALUE` = `101`
- `_APS_NEXT_COMMAND_VALUE` = `40001`
- `_APS_NEXT_CONTROL_VALUE` = `1001`
- `_APS_NEXT_SYMED_VALUE` = `101`

## Dependencies and Cross-File Interactions

`ubtrfs.rc.in` includes this header through the CMake-substituted path `@CMAKE_CURRENT_SOURCE_DIR@/src/ubtrfs/resource.h`. The current resource script only uses it as a conventional resource include; no symbolic resource IDs from this header are referenced elsewhere in the read file.

## Research Notes

This file is build/resource metadata only. Changes here matter for resource-editor generated IDs, not Btrfs format behavior.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/ubtrfs/resource.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/ubtrfs/ubtrfs.c -->
# File Research: sources/windows/winbtrfs/src/ubtrfs/ubtrfs.c

## Purpose

`ubtrfs.c` implements the user-mode WinBtrfs formatting DLL. It exposes FMIFS-style entry points used by Windows formatting tools, builds an initial single-device Btrfs filesystem image, writes root/chunk/extent/free-space metadata trees, writes superblocks, and asks the loaded kernel driver to probe the newly formatted volume.

The file also includes a stub `ChkdskEx`, configuration exports for sector/node size and feature flags, and support for multiple checksum algorithms.

## Local Formatting Model

The formatter builds a minimal in-memory representation rather than reusing the kernel driver's tree code:

- `btrfs_item`: one sorted key/data item.
- `used_space_extent`: tracks allocated regions inside a chunk.
- `btrfs_chunk`: chunk offset, `CHUNK_ITEM`, allocation cursor, used bytes, and used-space list.
- `btrfs_root`: one root tree, its eventual tree header/address/chunk, and sorted item list.
- `btrfs_dev`: one device item plus the next physical allocation offset.

Helper list functions implement the subset of Windows list behavior needed in user mode.

## Formatting Layout Construction

`write_btrfs` is the main filesystem creation routine. It creates roots for root, chunk, extent, device, checksum, filesystem, data relocation, and optional free-space/block-group trees. It initializes one device, detects SSD rotation status, allocates a system chunk and metadata/mixed chunk, inserts the device item, creates the default subvolume, initializes filesystem and relocation roots, assigns tree block addresses, adds block-group/free-space records, writes all roots, clears the first megabyte, and writes superblocks.

Chunk and device placement is handled by:

- `init_device`: initializes `DEV_ITEM`, UUIDs, IO alignment, and skips the first MiB for allocations.
- `add_chunk`: chooses system/metadata chunk sizes, DUP vs single-stripe layout, stripe length, and device extents.
- `find_chunk_offset`: allocates physical space for chunk stripes and adds `DEV_EXTENT` records.
- `superblock_collision` and `get_next_address`: avoid placing tree blocks in stripes overlapping well-known superblock mirror locations.

The formatter creates DUP system metadata on non-SSD devices, uses DUP metadata unless mixed groups are requested, and supports optional free-space cache and block-group tree feature flags.

## Tree and Metadata Writing

`assign_addresses` gives each root a tree block address in the system or metadata chunk, records used space, and creates either skinny metadata (`TYPE_METADATA_ITEM`) or full extent items (`TYPE_EXTENT_ITEM`) in the extent tree. It also inserts `ROOT_ITEM` records for non-root/chunk roots.

`write_roots` serializes every root as a single leaf tree block. It emits leaf node headers from sorted `btrfs_item` lists, packs item payloads from the end of the node, fills the tree header, computes the selected checksum, and writes the block through `write_data`.

`write_data` writes the same tree block to every stripe in the target chunk, which implements DUP-style mirroring for chunks with two stripes.

`write_superblocks` builds the `superblock`, computes bytes used from extent metadata, validates/converts the volume label to UTF-8, embeds the system chunk array, computes the selected checksum, and writes superblock copies at the standard `superblock_addrs` that fit on the device.

Checksum support covers CRC32C, XXHASH, SHA256, and BLAKE2 for both tree blocks and superblocks. `check_cpu` switches CRC32C to a hardware implementation on x86/x64 when SSE4.2 is available.

## Initial Filesystem Contents

The created filesystem includes a default subvolume layout:

- `set_default_subvol` creates the root-tree directory inode and a directory item named `default` pointing to `BTRFS_ROOT_FSTREE`.
- `init_fs_tree` creates the subvolume root inode and a `..` inode ref.
- `add_inode_ref` and `add_dir_item` build packed Btrfs inode-reference and directory-item records.
- `add_block_group_items` records block group usage either in the block group tree or extent tree.
- `populate_free_space_root` emits free-space extents and `FREE_SPACE_INFO` records for each chunk when the free-space cache compat-ro flag is enabled.

Timestamps are converted from Windows file time to Btrfs seconds/nanoseconds by `win_time_to_unix`.

## Format Entry Points

`FormatEx2` performs the actual format operation. It enables `SeManageVolumePrivilege`, selects hardware CRC support, validates checksum type, opens the target volume for read/write, queries length and geometry, derives sector and node sizes, sends initial progress, locks the volume, refuses to format one member of a mounted multi-device Btrfs filesystem, sends a whole-device TRIM request, sets required incompat flags, calls `write_btrfs`, dismounts/unlocks/closes the volume, and asks `\\Btrfs` to probe the volume with `IOCTL_BTRFS_PROBE_VOLUME` after success.

`FormatEx` adapts undocumented `format.exe`/FMIFS-style arguments (`DSTRING`, `STREAM_MESSAGE`, `options`) to `FormatEx2` and returns a Win32 `BOOL`.

Other exports:

- `SetSizes`: sets default sector and node size overrides.
- `SetIncompatFlags`: sets default Btrfs incompat feature flags.
- `SetCompatROFlags`: sets default compat-ro feature flags.
- `SetCsumType`: sets default checksum type.
- `GetFilesystemInformation`: stub returning true.
- `DllMain`: records the module handle on process attach.

`ChkdskEx` is also a stub; when given a callback it reports a one-line "stub, not implemented" output and returns success.

## Mounted Multi-Device Protection

`is_mounted_multi_device` reads and verifies the target superblock, extracts filesystem and device UUIDs, opens `\\Btrfs`, queries mounted filesystems with `IOCTL_BTRFS_QUERY_FILESYSTEMS`, and checks whether the target device belongs to a currently mounted multi-device filesystem. `FormatEx2` denies formatting in that case.

`look_for_device` walks variable-length `btrfs_filesystem_device` records to match the device UUID. `check_superblock_checksum` verifies the on-disk superblock checksum before trusting UUIDs.

## Dependencies and Cross-File Interactions

This file includes shared Btrfs format definitions from `../btrfs.h`, public IOCTL definitions from `../btrfsioctl.h`, CRC32C from `../crc32c.h`, and XXHASH from the bundled ZSTD library. It declares SHA256 and BLAKE2 helpers provided elsewhere in the WinBtrfs build.

At runtime it uses NT native file APIs (`NtReadFile`, `NtWriteFile`, `NtFsControlFile`, `NtDeviceIoControlFile`, `NtOpenFile`), Windows disk/storage IOCTLs, mountdev structures, ATA identify data for SSD detection, and Windows privilege APIs.

## Error Handling and Safety Notes

The formatter returns NTSTATUS failures for privilege, open, geometry, invalid parameter, label validation, allocation/IO, and mounted multi-device protections. Many internal allocations use `malloc` without exhaustive null checks in helper paths, so the code assumes formatter memory pressure is uncommon compared with kernel-mode paths.

The formatter only creates a single-device filesystem. Multi-device awareness is protective, not constructive. The entire tree model assumes each root fits in one leaf at format time.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/ubtrfs/ubtrfs.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/ubtrfs/ubtrfs.rc.in -->
# File Research: sources/windows/winbtrfs/src/ubtrfs/ubtrfs.rc.in

## Purpose

`ubtrfs.rc.in` is the CMake-templated Windows resource script for `ubtrfs.dll`. It supplies version metadata embedded in the user-mode Btrfs utility DLL.

## Contents

The script includes `src/ubtrfs/resource.h` via `@CMAKE_CURRENT_SOURCE_DIR@`, includes `winresrc.h`, sets English (United Kingdom) resources with code page 1252, and defines AP Studio `TEXTINCLUDE` blocks for resource-editor compatibility.

The `VS_VERSION_INFO` block uses CMake substitutions for:

- `FILEVERSION @PROJECT_VERSION_MAJOR@,@PROJECT_VERSION_MINOR@,@PROJECT_VERSION_PATCH@,0`
- `PRODUCTVERSION @PROJECT_VERSION_MAJOR@,@PROJECT_VERSION_MINOR@,@PROJECT_VERSION_PATCH@,0`
- string `FileVersion`
- string `ProductVersion`

String metadata identifies the file as:

- `FileDescription`: `Btrfs utility DLL`
- `InternalName`: `ubtrfs`
- `OriginalFilename`: `ubtrfs.dll`
- `ProductName`: `WinBtrfs`
- `LegalCopyright`: `Copyright (c) Mark Harmstone 2016-24`

Debug builds set `FILEFLAGS 0x1L`; non-debug builds set `0x0L`. The resource declares `FILEOS 0x4L`, `FILETYPE 0x2L`, and translation `0x809, 1200`.

## Dependencies and Cross-File Interactions

This template is consumed by the build system to generate a `.rc` file with project version numbers substituted. It complements `ubtrfs.c` by branding/versioning the DLL but has no direct code dependency on formatting behavior.

## Research Notes

This is build metadata. Functional changes to filesystem formatting happen in `ubtrfs.c`; changes here affect Windows file properties and resource/version output.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/ubtrfs/ubtrfs.rc.in -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/volume.c -->
# File Research: sources/windows/winbtrfs/src/volume.c

## Purpose

`volume.c` implements WinBtrfs' volume device wrapper and physical-device aggregation for Btrfs filesystems. It creates logical volume devices over one or more child block devices, forwards raw reads and selected writes, answers mount manager/storage IOCTLs, registers PnP removal notifications, handles drive-letter cleanup, and adds discovered Btrfs devices to the driver's PDO list.

The code bridges Windows volume/mount-manager expectations with Btrfs' multi-device model.

## Volume Lifetime

`vol_create` rejects opens during removal, increments `open_count`, and reports `FILE_OPENED`. `vol_close` decrements `open_count` under `pdo_list_lock` and the PDO child lock; if the volume is marked removing and the last handle closes, it calls `free_vol`.

`free_vol` marks the volume dead, detaches it from any mounted VCB, frees its name, deletes child locks, detaches/deletes device objects, unregisters child PnP notifications, frees child PnP names, and handles the `no_pnp` PDO allocation mode.

## Raw Read/Write Forwarding

`vol_read` forwards an IRP read to the first child device. It allocates a new lower IRP because the child is not in the same device stack, maps buffered/direct/neither I/O according to the child device flags, installs `vol_read_completion`, waits synchronously if pending, copies completion information back to the original IRP, and completes the original request.

`vol_write` mirrors this flow for writes but only permits writes when there is exactly one child device. Multi-device raw volume writes return `STATUS_ACCESS_DENIED`, preventing a caller from writing arbitrary bytes to just the first member of a Btrfs multi-device filesystem.

The shared completion context stores an `IO_STATUS_BLOCK` and event.

## IOCTL Handling

`vol_device_control` handles mountdev, disk, storage, and volume IOCTLs:

- `IOCTL_MOUNTDEV_QUERY_DEVICE_NAME`: returns the logical volume name.
- `IOCTL_MOUNTDEV_QUERY_UNIQUE_ID`: returns the filesystem UUID from the PDO extension.
- `IOCTL_STORAGE_GET_DEVICE_NUMBER`: returns the child disk/partition number for single-device volumes.
- `IOCTL_MOUNTDEV_QUERY_STABLE_GUID`: returns the filesystem UUID as a stable GUID.
- `IOCTL_VOLUME_GET_GPT_ATTRIBUTES`: returns zero attributes.
- `IOCTL_VOLUME_IS_DYNAMIC`: returns a one-byte true value.
- `IOCTL_VOLUME_ONLINE` and `IOCTL_VOLUME_POST_ONLINE`: succeed without work.
- `IOCTL_DISK_GET_DRIVE_GEOMETRY`: synthesizes geometry from aggregate child size and sector size.
- `IOCTL_DISK_IS_WRITABLE`: checks whether any child accepts `IOCTL_DISK_IS_WRITABLE`.
- `IOCTL_DISK_GET_LENGTH_INFO`: returns aggregate child size.
- `IOCTL_STORAGE_CHECK_VERIFY` and `IOCTL_DISK_CHECK_VERIFY`: checks all children.
- `IOCTL_VOLUME_GET_VOLUME_DISK_EXTENTS`: aggregates disk extents from all children.

Unknown IOCTLs are passed through only when the logical volume has one child (`vol_ioctl_passthrough`). The passthrough routine creates a lower IRP, mirrors the caller's IOCTL parameters and buffers, waits for completion, copies the lower status/information, and frees the lower IRP.

Note: `vol_is_writable` computes `STATUS_MEDIA_WRITE_PROTECTED` when no child is writable but returns `STATUS_SUCCESS` unconditionally at the end. That may be intentional compatibility behavior or a latent bug; the local `Status` value is otherwise unused on return.

## Mount Manager and Drive Letters

`mountmgr_add_drive_letter` asks MountMgr for the next drive letter for a given device path with `IOCTL_MOUNTMGR_NEXT_DRIVE_LETTER`.

`drive_letter_callback` opens `MOUNTMGR_DEVICE_NAME` and calls `drive_letter_callback2`. The latter builds `\\??`-prefixed names for all child PnP paths, removes their existing drive letters, then reacquires the child lock and records whether each child previously had a drive letter. This supports replacing per-device letters with the logical Btrfs volume letter.

## PnP Removal and Degraded Mount Policy

`pnp_removal` listens for `GUID_TARGET_DEVICE_QUERY_REMOVE` and forwards query-remove handling to the mounted filesystem device when present.

`allow_degraded_mount` reads the global `mount_allow_degraded` default and then checks the per-volume registry key `<registry_path>\<filesystem-uuid>` for a DWORD `AllowDegraded` override. `add_volume_device` uses this to decide whether a partially discovered filesystem may be surfaced.

## Adding Discovered Devices

`add_volume_device` is called when a Btrfs superblock/device is discovered. It:

- Finds or creates a PDO extension keyed by filesystem UUID.
- Opens the physical device path and stores the file/device object.
- Initializes child list state and sector size for new PDOs.
- Rejects duplicate device UUIDs.
- Allocates a `volume_child` with device UUID, device id, generation, size, disk/partition numbers, seeding flag, and normalized PnP path.
- Registers target-device-change notifications.
- Inserts the child ordered by generation, updating expected child count when newer metadata appears.
- If the filesystem is already mounted, attaches the physical device to the matching missing Btrfs `device` record and calls `init_device`.
- Propagates removable-media characteristics.
- Enables the device interface once all children are loaded, or once one child is loaded and degraded mount is allowed.
- Processes drive-letter cleanup, inserts new PDOs into `pdo_list`, and triggers boot/no-PnP/bus relation handling as appropriate.

Failure paths dereference the opened file object. Some new-PDO failure branches return after allocation/open failures without central cleanup, so ownership must be read carefully when modifying this function.

## Dependencies and Cross-File Interactions

This file depends on driver globals (`drvobj`, `master_devobj`, `busobj`, `pdo_list_lock`, `pdo_list`, `registry_path`), PnP helpers (`pnp_query_remove_device`, `boot_add_device`, `AddDevice`), IOCTL helper `dev_ioctl`, drive-letter helper `remove_drive_letter`, Btrfs device initialization `init_device`, and registry option state (`mount_allow_degraded`).

It shares major data structures with the rest of the driver: `volume_device_extension`, `pdo_device_extension`, `volume_child`, `device_extension`, `device`, `superblock`, and Btrfs UUID/device item fields.

## Error Handling and Safety Notes

The file uses ERESOURCE locking around global PDO and per-PDO child state. Raw lower IRP forwarding is synchronous and carefully separates the logical volume stack from child device stacks.

The most important behavioral safety boundaries are multi-device write denial, single-child IOCTL passthrough only, duplicate child UUID rejection, and query-remove propagation to mounted filesystems.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/volume.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/worker-thread.c -->
# File Research: sources/windows/winbtrfs/src/worker-thread.c

## Purpose

`worker-thread.c` provides deferred worker-queue execution for WinBtrfs read and write IRPs. It lets dispatch paths queue work that cannot complete immediately, then performs the actual read/write on a system worker thread and completes the IRP.

## Main Data Structure

`job_info` stores the target `device_extension`, queued `PIRP`, and embedded `WORK_QUEUE_ITEM`.

## Deferred Read Path

`do_read_job` runs a queued read. It detects top-level IRP state, obtains the file object's FCB, clears `IoStatus.Information`, acquires the FCB resource shared if the current thread does not already hold it, calls `do_read(Irp, true, &bytes_read)` inside structured exception handling, releases the resource if acquired, logs failures, sets `Irp->IoStatus.Status`, completes the IRP, clears top-level IRP state if needed, and returns the status.

## Deferred Write Path

`do_write_job` runs a queued write. It detects top-level IRP state, calls `write_file(Vcb, Irp, true, true)` inside structured exception handling, logs failures, sets IRP status, completes the IRP, clears top-level IRP state if needed, and returns the status.

## Worker Dispatch and Queuing

`do_job` is the `WORKER_THREAD_ROUTINE`. It inspects the queued IRP major function and dispatches to `do_read_job` for `IRP_MJ_READ` or `do_write_job` for `IRP_MJ_WRITE`, then frees `job_info`.

`add_thread_job` allocates `job_info`, stores the VCB and IRP, and ensures the IRP has an MDL. If no MDL is present it allocates one over `Irp->UserBuffer` and probes/locks pages with `IoWriteAccess` for reads or `IoReadAccess` for writes. It then initializes and queues the work item to `DelayedWorkQueue`.

## Dependencies and Cross-File Interactions

This file calls `do_read` from the read path and `write_file` from the write path, uses FCB resources from `btrfs_drv.h`, and relies on Windows work queue, MDL, probe/lock, exception, and IRP completion APIs.

It is used by dispatch code that marks an IRP pending and needs the operation continued outside the caller's original context.

## Error Handling and Safety Notes

Allocation failures and page-probe exceptions cause `add_thread_job` to clean up and return false so the caller can fail or complete the IRP. The read job acquires the FCB resource only if needed, avoiding recursive acquisition when already held.

`do_job` computes `IrpSp` as nullable but then dereferences it without a null check. In current use `job_info->Irp` is always set by `add_thread_job`, so this is an internal invariant rather than a general-purpose worker routine.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/worker-thread.c -->