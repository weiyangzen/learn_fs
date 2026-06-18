# Group Research: group_1813_winbtrfs_sources_windows_winbtrfs_src_create_c_sources_windows_winb_c91a0fced405

Scope: subset A only, covering the listed WinBtrfs source files under `sources/windows/winbtrfs/src`. Each source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/create.c -->
# File Research: sources/windows/winbtrfs/src/create.c

## Scope

This file implements WinBtrfs `IRP_MJ_CREATE` handling and the supporting object-open/create machinery. It covers FCB and file-reference allocation, path parsing, directory child lookup and caching, inode/xattr/extent loading, named stream handling, new inode creation, existing-file open semantics, reparse handling, oplock handoff, open-by-file-id support, removable-media verification, and volume-open handling.

## Entry Points And Major APIs

- `create_fcb`, `create_fileref`: allocate initialized FCB/file-reference objects.
- `find_file_in_dir`, `split_path`, `open_fileref`, `open_fileref_child`: resolve paths, components, subvolume entries, case sensitivity, and alternate data streams.
- `load_csum`, `load_dir_children`, `open_fcb`, `open_fcb_stream`: load inode metadata, extents, xattrs, directory caches, hardlinks, checksums, and ADS state.
- `add_dir_child`, `inherit_mode`, `file_create_parse_ea`, `file_create2`, `create_stream`, `file_create`: create normal files/directories and named streams.
- `get_reparse_block`, `fcb_load_csums`: build reparse buffers and lazily load extent checksums.
- `open_file3`, `open_file2`, `oplock_complete`: finalize existing-file opens, disposition handling, share access, oplocks, overwrites, CCB setup, paging-file normalization.
- `open_fileref_by_inode`, `open_file`: implement open-by-file-id and top-level file create/open routing.
- `verify_vcb`, `has_manage_volume_privilege`, `drv_create`: removable verification, privilege checks, and exported `IRP_MJ_CREATE` dispatch.

## Core Control Flow

`drv_create` handles master-device and volume-device opens first, rejects unmounted/removing volumes, verifies removable media, then acquires `load_lock`. Empty-name filesystem opens create a CCB on `Vcb->volume_fcb`.

Normal opens acquire `tree_lock` shared unless already held, then `fileref_lock`, and call `open_file` with a rollback list. `open_file` decodes disposition/options, handles `FILE_OPEN_BY_FILE_ID`, resolves names via `open_fileref`, processes reparses, and chooses existing-file open (`open_file2`) or missing-file creation (`file_create`). Failures roll back mutating operations.

Path resolution uses `split_path` plus repeated `open_fileref_child` calls. It handles absolute and related paths, parent-only opens, synthetic `$Root`, dummy hidden subvolume roots, reparse stops, case-sensitive directories, and ADS components.

`open_fcb` loads or reuses an inode FCB. It reads the inode item, guesses type from POSIX mode if needed, scans hardlink refs, xattrs, and extent data, loads directory children for directories, computes allocation sizes, derives attributes/security, and inserts the FCB into per-subvolume/global hash-sorted lists.

`file_create2` initializes a new inode, parent metadata, inherited mode, Btrfs flags, compression state, Windows attributes, security descriptor, EAs, optional allocation, directory child caches, and dirty file/ref state. `create_stream` creates ADS FCBs as `user.<stream>` xattrs with index-0 stream children.

Existing opens go through `open_file2` for access, readonly, delete, reparse, directory/file option, share, and oplock checks. `open_file3` handles overwrite/supersede truncation, EA replacement, stream removal, notifications, CCB creation, `FILE_OBJECT` contexts, and open counters.

## Important State Mutated

- `fcb`: refcount, inode item, type, flags, attributes, SD, EA/reparse/compression/case xattrs, extents, hardlinks, directory children, ADS fields, dirty flags, share access, file sizes.
- `file_ref`: ref/open counts, parent/child links, `dir_child`, created/deleted/dirty state, delete-on-close traversal.
- `dir_child`: key, index, type, UTF-8/UTF-16 names, upcased name, hashes, fileref backpointer, `$Root` marker.
- `root`: FCB buckets, version, last inode, root item transaction/change times.
- `device_extension`: open-file count, loaded roots, root/dummy/volume FCBs, all-FCB list, locks, readonly/mounted/removing state.
- `IRP` / `FILE_OBJECT`: create information, reparse auxiliary buffer, contexts, VPB, section object pointer, cache flags, granted access.

## Dependencies

Uses Windows IFS/kernel APIs for FSRTL headers, file locks, oplocks, wildcard/name matching, share access, security checks, privilege checks, EA validation, volume verification, image-section flushing, resource locks, pool/lookaside allocation, and IRP completion.

Project-local dependencies include tree traversal, name conversion, CRC32C hashing, xattr access, attribute/security helpers, reparse setters, file read/extend/truncate helpers, stream EOF helpers, object lifetime helpers, dirty marking, notifications, rollback, and subvolume helpers.

## Notable Behaviors

- Directory lookup uses index order plus case-sensitive and uppercase hash buckets.
- ADS entries are xattr-backed and appear as index-0 children.
- `$Root` exposes the filesystem tree root when the mounted default subvolume is not `BTRFS_ROOT_FSTREE`.
- Reparse returns store a reparse buffer in `Irp->Tail.Overlay.AuxiliaryBuffer`.
- Atomic-create ECP support honors reparse creation and case-sensitive-directory flags; query-on-create and redirection ECPs are only logged.
- LXSS create-time EAs can alter UID, GID, mode, device number, and special-file type.

## Risks And Edge Cases

- `create_stream` collision handling returns without releasing `dir_children_lock` and assumes `existing_dc->fileref` is non-NULL.
- `file_create2` case-insensitive duplicate checking hashes the upcased name but compares against `dc->name` rather than `dc->name_uc`.
- `load_dir_children` leaks `hash_ptrs` if `hash_ptrs_uc` allocation fails.
- Several create failure paths manually undo parent size changes; correctness depends on rollback and cleanup paths.
- `open_file2` treats some malformed reparse-block failures as non-fatal and continues opening normally.
- ADS lookup has a FIXME for xattr hash collisions.
- `drv_create` waits synchronously for pending oplock completion before returning.

## Summary

`create.c` is the WinBtrfs namespace and open/create hub. It bridges Windows create semantics with Btrfs roots, inodes, directory indexes, xattrs, extents, subvolumes, streams, reparse points, security, share access, and oplocks.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/create.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/devctrl.c -->
# File Research: sources/windows/winbtrfs/src/devctrl.c

## Scope

This file implements WinBtrfs `IRP_MJ_DEVICE_CONTROL` dispatch for filesystem device objects, the control device object, and volume device objects. It handles WinBtrfs-private IOCTLs, selected mount/storage IOCTLs, and pass-through for unhandled filesystem-device controls.

## Entry Points And Major APIs

- `mountdev_query_stable_guid(Vcb, Irp)`: returns the filesystem UUID as `MOUNTDEV_STABLE_GUID`.
- `is_writable(Vcb)`: returns success unless the VCB is readonly.
- `query_filesystems(data, length)`: enumerates loaded VCBs and devices into `btrfs_filesystem` records.
- `probe_volume(data, length, processor_mode)`: validates a `MOUNTDEV_NAME`, checks manage-volume privilege, opens the device, refreshes disk properties, and triggers removal/arrival probing.
- `ioctl_unload(Irp)`: requires load-driver privilege and calls `do_shutdown`.
- `control_ioctl(Irp)`: dispatches private control-device IOCTLs.
- `drv_device_control(DeviceObject, Irp)`: exported device-control dispatch.

## Core Control Flow

`drv_device_control` enters the filesystem, sets top-level IRP state, clears `IoStatus.Information`, and dispatches by VCB type. Control-device requests go to `control_ioctl`; volume-device requests go to `vol_device_control`; filesystem VCBs handle stable GUID and writability queries directly.

Unhandled filesystem-device IOCTLs are passed down to `Vcb->Vpb->RealDevice` with `IoSkipCurrentIrpStackLocation` and `IoCallDriver`, so the lower driver completes the IRP.

`query_filesystems` takes `global_loading_lock`, walks `VcbList`, records each filesystem UUID and device count under `tree_lock`, then records device UUIDs and mountdev names or marks devices missing.

`probe_volume` checks buffer sizes and privilege, opens the named device, gets PnP name and interface GUID, optionally issues `IOCTL_DISK_UPDATE_PROPERTIES`, calls `volume_removal`, then calls `disk_arrival` or `volume_arrival`.

## Important State Mutated

- `Irp->IoStatus.Information` for stable GUID output.
- Caller output buffers for filesystem/device enumeration.
- Global device/volume discovery state through removal and arrival callbacks.
- Driver shutdown path through `do_shutdown`.

## Dependencies

Uses mount manager and storage IOCTLs, `IoGetDeviceObjectPointer`, privilege checks, IRP pass-through APIs, `VcbList`, `global_loading_lock`, `dev_ioctl`, `get_device_pnp_name`, arrival/removal helpers, shutdown helper, and volume-device control delegation.

## Notable Behaviors

- No mounted filesystems returns one zeroed `btrfs_filesystem` record if the buffer is large enough.
- Device names are queried from mountdev into variable-length output entries.
- Private control IOCTLs use `Parameters.FileSystemControl` lengths inside an `IRP_MJ_DEVICE_CONTROL` handler.
- Unknown filesystem-device controls are transparently forwarded to real storage.

## Risks And Edge Cases

- `query_filesystems` may partially populate output before returning `STATUS_BUFFER_OVERFLOW`.
- The second mountdev-name query writes into `&bfd->name_length`, relying on compatible layout with name-length/name fields.
- `probe_volume` continues using the GUID pointer returned by `get_device_pnp_name`; this relies on helper-managed lifetime.
- Pass-through assumes `Vpb` and `RealDevice` are valid for filesystem VCBs.

## Summary

`devctrl.c` is a compact IOCTL router for WinBtrfs control operations, mount/writability queries, volume delegation, and storage-stack pass-through.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/devctrl.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/dirctrl.c -->
# File Research: sources/windows/winbtrfs/src/dirctrl.c

## Scope

This file implements WinBtrfs `IRP_MJ_DIRECTORY_CONTROL`, covering directory enumeration and directory change notification. It formats cached `dir_child` entries into Windows directory information classes, supports wildcard/specific-name queries, emits `.` and `..`, handles reparse tags and EA sizes, and registers notify IRPs with FSRTL.

## Entry Points And Major APIs

- `get_reparse_tag_fcb(fcb)`: extracts a reparse tag from symlink type, directory reparse xattr, or file-backed reparse data.
- `get_reparse_tag(Vcb, subvol, inode, type, atts, lxss, Irp)`: returns symlink/LXSS/saved reparse tags, opening an FCB when needed.
- `get_ea_len(Vcb, subvol, inode, Irp)`: reads and validates the `EA` xattr and computes Windows EA size.
- `query_dir_item(fcb, ccb, buf, len, Irp, de, r)`: formats one entry into the requested directory info structure.
- `next_dir_entry(fileref, offset, de, pdc)`: walks `.` / `..` and index-ordered children.
- `query_directory(Irp)`: implements `IRP_MN_QUERY_DIRECTORY`.
- `notify_change_directory(Vcb, Irp)`: validates and queues directory change notifications.
- `drv_directory_control(DeviceObject, Irp)`: exported directory-control dispatch.

## Core Control Flow

`drv_directory_control` validates the filesystem VCB, clears `IoStatus.Information`, and dispatches by minor function.

`query_directory` validates CCB/FCB/fileref state, checks `FILE_LIST_DIRECTORY` for user-mode callers, handles restart flags, stores the first query string on the CCB, and distinguishes wildcard, specific-file, and sequential enumeration modes. It locks `tree_lock` and the directory child list, maps the caller buffer, finds the first matching entry, writes it with `query_dir_item`, then packs additional aligned entries until the buffer fills or enumeration ends.

`next_dir_entry` returns `.` and `..` for non-root directory references, then scans `dir_children_index` from the saved offset. Synthetic `$Root` is hidden below normal subdirectories to avoid recursive exposure.

`query_dir_item` resolves inode/root metadata for the entry, using an attached child FCB when possible or direct tree lookup otherwise. It fills timestamps, logical/allocation sizes, attributes, EA or reparse values, file IDs, and names for the supported information classes.

`notify_change_directory` checks access and type, materializes the watched path into `ccb->filename` if needed, and calls `FsRtlNotifyFilterChangeDirectory`; pending notify IRPs are not completed immediately.

## Supported Directory Information Classes

- `FileBothDirectoryInformation`
- `FileDirectoryInformation`
- `FileFullDirectoryInformation`
- `FileIdBothDirectoryInformation`
- `FileIdFullDirectoryInformation`
- `FileIdExtdDirectoryInformation`
- `FileIdExtdBothDirectoryInformation`
- `FileNamesInformation`

Short names are not provided. Extended ID classes include a 128-bit ID.

## Important State Mutated

- `ccb->query_dir_offset`, `query_string`, `has_wildcard`, and `specific_file`.
- `ccb->filename` for notify watches.
- `Irp->IoStatus.Information` with bytes returned.
- FSRTL notification state via `Vcb->DirNotifyList` and `Vcb->NotifySync`.

## Dependencies

Uses FSRTL wildcard and notification APIs, EA validation, Unicode upcasing, resource locks, directory information structures, reparse tags, `open_fcb`, `free_fcb`, tree lookup helpers, xattr/file read helpers, attribute helpers, file-id helpers, filename construction, buffer mapping, time conversion, and Btrfs inode/directory item structures.

## Notable Behaviors

- Symlinks report zero EOF/allocation size in directory listings.
- Sparse files report `st_blocks`; other files use sector-aligned logical size.
- Reparse-point entries use `EaSize` as reparse tag for several information classes.
- LXSS special files map to AF_UNIX/FIFO/CHR/BLK reparse tags when `ccb->lxss` is true.
- Initial no-match enumeration returns `STATUS_NO_SUCH_FILE`; later exhaustion returns `STATUS_NO_MORE_FILES` or success after partial output.
- Multi-entry packing aligns to 8 bytes for most classes and 4 bytes for `FileNamesInformation`.

## Risks And Edge Cases

- Extended ID classes fill `FileId` from the containing directory FCB rather than the entry inode/root, so every entry may report the directory's ID.
- Extended ID classes call `get_reparse_tag` even when resolved root `r` can be NULL for dummy/inaccessible entries.
- `get_reparse_tag_fcb` does not verify that file-backed `read_file` returned four bytes.
- Invalid EA xattrs are logged and reported as zero EA length instead of failing enumeration.
- `query_directory` advances `query_dir_offset` before buffer mapping and first-entry formatting succeed, so some failures can consume an entry.
- `notify_change_directory` leaves an allocated `ccb->filename.Buffer` attached if the second filename fetch fails.

## Summary

`dirctrl.c` is the WinBtrfs directory listing and notification layer. It converts cached Btrfs directory children and inode metadata into Windows directory query records, maintains per-handle enumeration state, reports reparse/EA/file-id metadata, and registers change watches through FSRTL.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/dirctrl.c -->