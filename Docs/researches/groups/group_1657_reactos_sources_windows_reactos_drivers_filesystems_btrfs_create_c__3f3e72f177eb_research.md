# Group Research: ReactOS Btrfs create/devctrl/dirctrl

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/create.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/create.c

Implements the WinBtrfs/ReactOS Btrfs create/open path: FCB and fileref allocation, path parsing, directory child lookup/materialization, inode-by-ID opens, file and stream creation, reparse handling, oplock/share-access checks, overwrite/supersede behavior, checksum preloading, removable-media verification, volume opens, and the `IRP_MJ_CREATE` dispatch entry point.

Key entry points:
- `drv_create()` is the IRP dispatcher. It handles opens of the filesystem device object, volume device object, raw volume file object, and normal file objects; verifies mounted/removable media state; acquires `load_lock`, `tree_lock`, and `fileref_lock`; runs `open_file()`; and completes or waits for pending oplock work.
- `open_file()` decodes create disposition/options, validates related file objects, handles `FILE_OPEN_BY_FILE_ID`, resolves paths and reparse stops, dispatches to open-existing or create-new logic, updates granted access, VPB, cache flags, and checksum loading.
- `open_file2()` enforces access checks, readonly/delete rules, reparse returns, directory-vs-file option compatibility, share access, and oplock checks before calling `open_file3()`.
- `open_file3()` finishes an existing-file open, including overwrite/supersede truncation, allocation extension, EA replacement/removal, stream deletion on overwrite, notifications, CCB setup, paging-file extent normalization, and open-count accounting.
- `file_create()` handles create-new requests after parent resolution. It parses final path components and alternate data stream names, processes atomic-create ECPs, performs parent access checks, and calls `file_create2()` or `create_stream()`.
- `file_create2()` creates a new regular file or directory: allocates inode/FCB/fileref, inherits permissions and compression/NOCOW flags, initializes security descriptor and EAs/LXSS metadata, optionally preallocates allocation size, inserts the FCB and directory child, marks dirty state, and sends notifications.
- `create_stream()` maps NTFS alternate data streams to Btrfs `user.*` xattrs, creates ADS FCBs/filerefs, checks reserved stream names, enforces write access on the owning object, and inserts stream entries into the parent FCB’s child list.

Path and object lookup:
- `split_path()` splits NT path components, detects stream syntax, strips `:$DATA`, rejects empty components, and represents each component as `name_bit`.
- `open_fileref()` walks absolute or related paths, strips leading root separators, optionally returns parent refs, tracks parsed offsets for reparses, and switches case sensitivity per directory/stream context.
- `open_fileref_child()` resolves one child component from a parent fileref. Normal entries use directory child hash lists; stream entries scan index-0 stream children and open ADS xattrs through `open_fcb_stream()`.
- `find_file_in_dir()` uses CRC32C hash buckets over original or upcased UTF-16 names to find `dir_child` entries and resolve subvolume root items.
- `open_fileref_by_inode()` supports file-id opens by reconstructing a fileref path from cached hardlinks, `INODE_REF`/`INODE_EXTREF`, `ROOT_BACKREF`, or the synthetic `$Root` directory.

FCB and directory state:
- `create_fcb()` allocates pageable/nonpageable FCB parts, initializes FSRTL headers, resources, locks, oplock state, extent/hardlink/xattr/dir-child lists, and starts the refcount at one.
- `create_fileref()` allocates a `file_ref`, initializes refcount and children list.
- `open_fcb()` loads an inode’s `INODE_ITEM`, infers Btrfs type when needed, reads hardlinks, xattrs, DOS attributes, NT security descriptor, compression/case-sensitive properties, extent data, directory children, file sizes, default attributes, and security descriptor inheritance. It then inserts the FCB into the subvolume cache/hash lists.
- `open_fcb_stream()` opens an ADS FCB backed by a `user.<stream>` xattr and computes the maximum remaining xattr payload room in the leaf.
- `load_dir_children()` materializes `TYPE_DIR_INDEX` entries into sorted/hash-indexed `dir_child` nodes and synthesizes `$Root` under the default subvolume when configured.
- `add_dir_child()` adds a newly created file/directory to the parent’s in-memory child index and hash lists.
- `inherit_mode()` carries parent Unix mode bits while clearing sticky/setuid and, for files, setgid.

Metadata and data helpers:
- `load_csum()` reads checksum items from the checksum tree across one or more `TYPE_EXTENT_CSUM` items.
- `fcb_load_csums()` lazily allocates and loads per-extent checksum buffers for regular extents unless the inode is NODATASUM.
- `file_create_parse_ea()` normalizes create-time EAs, folds duplicates, interprets LXSS `LXUID`, `LXGID`, `LXMOD`, and `LXDEV`, updates Unix inode fields/device type, and stores remaining EAs as the Btrfs EA xattr.
- `get_reparse_block()` converts Btrfs symlink data into a Windows `REPARSE_DATA_BUFFER`, validates file-backed reparse buffers, and copies directory reparse xattr buffers.
- `verify_vcb()` issues `IOCTL_STORAGE_CHECK_VERIFY` to removable backing devices and triggers `IoVerifyVolume()` when media change counts require it.
- `has_manage_volume_privilege()` records `SE_MANAGE_VOLUME_PRIVILEGE` on raw volume opens.

Important invariants:
- Name lookup depends on `dir_children_index`, `dir_children_hash`, `dir_children_hash_uc`, and 256-entry hash pointer arrays remaining sorted and synchronized.
- `tree_lock` protects Btrfs tree reads/mutations around create/open, while `fileref_lock`, per-FCB resources, and per-directory `dir_children_lock` protect object lifetime and directory child state.
- FCBs are cached per subvolume/inode and ADS FCBs are colocated near their owning inode in the FCB list.
- Filerefs represent path instances and carry parent/child links; directory FCBs may cache their primary fileref.
- Newly created objects are marked dirty before they are persisted; rollback lists are used around create/open work that mutates extents or metadata.
- Windows create dispositions must map to Btrfs mutations without violating image-section, share-access, oplock, readonly, subvolume-readonly, verity, and delete-pending constraints.
- Reparse handling must return both `STATUS_REPARSE` and the correct auxiliary buffer/tag so the I/O manager can continue path resolution.
- Alternate data streams are stored as xattrs and use index `0` directory-child entries, distinct from normal directory children whose indexes start at `2`.

Filesystem relevance:
- This file is the core namespace gateway for the driver. It bridges Windows create/open semantics to Btrfs inodes, subvolumes, xattrs, extents, checksums, security descriptors, reparse points, hardlinks, directory indexes, and file-id behavior.

Notable risks:
- `find_file_in_dir()` allocates an upcased string for case-insensitive lookup, then returns immediately on invalid filename without freeing it.
- In `file_create2()`, the case-insensitive duplicate check hashes `fpusuc` but compares `dc->name.Buffer` against `fpusuc.Buffer`; this appears to intend `dc->name_uc` and may miss collisions for differently cased names.
- In `open_fcb()`, an invalid copied NT security descriptor is freed without clearly nulling `fcb->sd`; later fallback security descriptor logic should be audited for stale-pointer assumptions.
- ADS handling notes a FIXME for xattr hash collisions; `open_fileref_child()` treats matching ADS hash as identity when selecting an existing ADS FCB.
- Create/open control flow is highly stateful: rollback, FCB insertion, fileref insertion, dirty marking, parent directory size changes, and share access must all stay paired across many failure paths.
- Reparse failure in `open_file2()` logs an error but converts it to success, which may hide malformed reparse metadata from callers.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/create.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/devctrl.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/devctrl.c

Implements device-control dispatch for the Btrfs driver’s control, filesystem, and volume device objects. It handles a small set of driver/private IOCTLs directly, answers mount-manager/disk writability queries for filesystem devices, delegates volume-device controls, and forwards unknown filesystem-device controls to the underlying real disk device.

Key entry points:
- `drv_device_control()` is the `IRP_MJ_DEVICE_CONTROL` dispatcher. It enters filesystem context, detects top-level IRPs, routes control devices to `control_ioctl()`, volume devices to `vol_device_control()`, filesystem devices to local mount/disk handlers, and forwards unhandled control codes to `Vpb->RealDevice`.
- `control_ioctl()` handles driver control-device IOCTLs: `IOCTL_BTRFS_QUERY_FILESYSTEMS`, `IOCTL_BTRFS_PROBE_VOLUME`, and `IOCTL_BTRFS_UNLOAD`.
- `mountdev_query_stable_guid()` returns the mounted filesystem UUID as the mount manager stable GUID.
- `is_writable()` implements `IOCTL_DISK_IS_WRITABLE` by returning `STATUS_MEDIA_WRITE_PROTECTED` when the VCB is readonly.
- `query_filesystems()` serializes the currently loaded Btrfs filesystems from global `VcbList`, including filesystem UUIDs, device UUIDs, missing-device markers, and mountdev device names.
- `probe_volume()` validates a supplied mountdev name, requires `SE_MANAGE_VOLUME_PRIVILEGE`, opens the target device, refreshes disk properties when applicable, gets the PnP name/interface GUID, runs removal notification, then reannounces the disk or volume.
- `ioctl_unload()` requires `SE_LOAD_DRIVER_PRIVILEGE` and invokes `do_shutdown()`.

Important behavior:
- `query_filesystems()` holds `global_loading_lock` while walking `VcbList`, and each VCB’s `tree_lock` while reading device lists and superblock device counts.
- Variable-length filesystem/device output uses `next_entry` offsets for filesystem records and embeds variable-length device names after each `btrfs_filesystem_device`.
- Missing devices are reported without a mountdev name; present devices are queried through `IOCTL_MOUNTDEV_QUERY_DEVICE_NAME`.
- `probe_volume()` accepts a `MOUNTDEV_NAME` input buffer from the caller, converts it to a `UNICODE_STRING`, opens the named device with `IoGetDeviceObjectPointer()`, and triggers arrival/removal paths to refresh driver discovery.
- `drv_device_control()` completes handled IRPs itself, but skips/completes through the lower driver for forwarded IOCTLs.

Filesystem relevance:
- This file is the administrative/control surface for enumerating loaded Btrfs volumes, rescanning/probing devices, unloading the driver, exposing a stable mount GUID, and preserving Windows disk IOCTL behavior.

Notable risks:
- `query_filesystems()` has complex variable-length packing; callers depend on accurate `itemsize`, `next_entry`, and remaining-length accounting.
- The present-device branch fills name data but does not visibly initialize every per-device output field, so structure layout and caller zeroing expectations are important.
- `control_ioctl()` returns data for `IOCTL_BTRFS_QUERY_FILESYSTEMS` but does not set `Irp->IoStatus.Information` itself; if the API expects bytes-returned semantics, that should be checked against callers.
- `probe_volume()` privilege-gates rescans correctly, but its lifetime/ownership contract for the PnP name returned by `get_device_pnp_name()` should be confirmed with that helper.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/devctrl.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/dirctrl.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/dirctrl.c

Implements directory control for the Btrfs filesystem driver: query-directory enumeration, exact/wildcard name filtering, directory information class formatting, EA/reparse tag reporting, `.`/`..` synthesis, hidden `$Root` handling, and change-notification registration.

Key entry points:
- `drv_directory_control()` dispatches `IRP_MJ_DIRECTORY_CONTROL`, rejects volume/non-filesystem device objects, and routes `IRP_MN_QUERY_DIRECTORY` to `query_directory()` and `IRP_MN_NOTIFY_CHANGE_DIRECTORY` to `notify_change_directory()`.
- `query_directory()` validates FCB/CCB/fileref state and access, processes query flags, stores/reuses query patterns in the CCB, locks the VCB tree and directory child list, locates matching entries, fills one or more records, advances `query_dir_offset`, and returns byte count in `IoStatus.Information`.
- `query_dir_item()` converts one internal `dir_entry` into the requested Windows directory information structure.
- `next_dir_entry()` walks the in-memory `dir_children_index`, synthesizing `.` and `..` for non-root directory opens and hiding the synthetic `$Root` entry except at the apparent root.
- `notify_change_directory()` validates access and directory type, computes the watched path name if needed, and registers the IRP with `FsRtlNotifyFilterChangeDirectory()`.

Directory information support:
- Supports `FileBothDirectoryInformation`, `FileDirectoryInformation`, `FileFullDirectoryInformation`, `FileIdBothDirectoryInformation`, `FileIdFullDirectoryInformation`, `FileNamesInformation`, and Vista-style `FileIdExtdDirectoryInformation` / `FileIdExtdBothDirectoryInformation`.
- Populates timestamps from Btrfs `INODE_ITEM` fields, translating Unix/Btrfs time to Windows time.
- Reports `EndOfFile` as zero for symlinks and `st_size` otherwise.
- Reports allocation size as zero for symlinks, `st_blocks` for sparse files, or sector-aligned logical size otherwise.
- Reports file attributes from cached FCBs when available or by calling `get_file_attributes()` from inode metadata.
- Reports EA size from cached/fetched EA xattrs, but substitutes reparse tags for information classes whose `EaSize` field doubles as reparse tag reporting.
- Reports short-name lengths as zero because Btrfs has no DOS 8.3 short-name namespace.

Reparse and EA helpers:
- `get_reparse_tag_fcb()` returns symlink tags directly, extracts directory reparse tags from the reparse xattr, or reads a file-backed reparse buffer tag from file contents.
- `get_reparse_tag()` maps Btrfs symlinks and LXSS socket/FIFO/char/block device types to Windows reparse tags; for normal files/directories it opens the target FCB when the reparse attribute is present.
- `get_ea_len()` fetches the Btrfs EA xattr, validates it with `IoCheckEaBufferValidity()`, and computes the packed Windows EA length.

Filtering and enumeration:
- Query patterns are stored on the CCB. `SL_RESTART_SCAN` clears stored state and resets offset.
- A single `*` or absent filename means full enumeration; non-wildcard names become exact lookups; wildcard names are upcased for case-insensitive `FsRtlIsNameInExpression()`.
- Exact lookup uses the directory child hash tables, choosing case-sensitive or upcased hash buckets based on `ccb->case_sensitive`.
- Multi-entry output aligns each next record to 8 bytes for most directory classes and 4 bytes for `FileNamesInformation`.
- `SL_RETURN_SINGLE_ENTRY` and exact-file queries stop after the first successful entry.

Locking and state:
- Directory enumeration holds `Vcb->tree_lock` shared and the directory FCB’s `dir_children_lock` shared while reading child lists and formatting returned records.
- Change notification holds `tree_lock` shared and the target FCB resource exclusive while validating/registering the watch.
- Query state persists in `ccb->query_dir_offset`, `ccb->query_string`, `ccb->has_wildcard`, and `ccb->specific_file`.

Filesystem relevance:
- This file is the Windows directory enumeration facade over Btrfs directory index metadata cached by `create.c`. It is responsible for making Btrfs inode/subvolume/xattr/reparse state look like standard Windows directory query records.

Notable risks:
- In the extended file ID information cases, `FileId.Identifier` is filled from the queried directory FCB (`fcb->inode`, `fcb->subvol->id`) rather than the child entry’s `inode`/`r`; this looks wrong for directory listings where each returned row should identify the listed child.
- `query_dir_item()` may open child FCBs and read reparse/file data while enumeration locks are held; this is functional but increases deadlock and latency sensitivity.
- `get_reparse_tag()` opens an FCB to inspect reparse data for listed entries, so malformed or expensive reparse metadata can affect ordinary directory listings.
- The exact-match path allocates an upcased string for case-insensitive matching and frees it correctly, but the surrounding enumeration state is updated before exact lookup, making restart/specific-file behavior worth regression testing.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/dirctrl.c -->