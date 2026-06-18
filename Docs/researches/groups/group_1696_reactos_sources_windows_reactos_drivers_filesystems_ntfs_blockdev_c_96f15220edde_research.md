# Group Research: ReactOS NTFS driver subset A group 1696

Scope confirmed against `Docs/research_subset_a.md`: `sources/windows/reactos` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/blockdev.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ntfs/blockdev.c

Read status: complete file, 380 lines.

This file provides the NTFS driver's low-level synchronous block-device helpers. It wraps lower storage-device IRPs for reads, writes, sector reads, and device I/O controls.

Key entry points:
- `NtfsReadDisk()` builds an `IRP_MJ_READ` with `IoBuildSynchronousFsdRequest()`, optionally sets `SL_OVERRIDE_VERIFY_VOLUME`, waits on pending I/O, and copies out of a temporary aligned buffer when the caller asks for an unaligned read.
- `NtfsWriteDisk()` builds `IRP_MJ_WRITE`. For unaligned writes it performs read-modify-write: rounds the target range to sector boundaries, reads the old sectors into a temporary buffer, overlays caller data, writes the full aligned buffer, then zeroes and frees it.
- `NtfsReadSectors()` converts sector/count input to byte offset/length and delegates to `NtfsReadDisk()`.
- `NtfsDeviceIoControl()` builds a synchronous device-control IRP, optionally overrides volume verification, waits for completion, and returns `IoStatus.Information` through `OutputBufferSize`.

Important dependencies:
- Kernel I/O manager: `IoBuildSynchronousFsdRequest`, `IoBuildDeviceIoControlRequest`, `IoCallDriver`, IRP stack flags.
- Memory/event helpers: `ExAllocatePoolWithTag`, `KeInitializeEvent`, `KeWaitForSingleObject`.
- NTFS constants/macros: `TAG_NTFS`, `ROUND_DOWN`, `ROUND_UP`.

Notable behavior and risks:
- The write path handles a misaligned start plus rounded length by adding another sector when needed. The read path rounds `Length` independently and allocates `RealLength + SectorSize`, but it only reads `RealLength`; for a misaligned start and sector-sized length, the final copy can require bytes beyond the read range.
- `NtfsWriteDisk()` returns success immediately for zero-length writes.
- Writes do not expose an `Override` parameter, unlike reads and device I/O controls.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/blockdev.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/btree.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ntfs/btree.c

Read status: complete file, 2030 lines.

This file implements an in-memory B-tree abstraction for NTFS filename indexes, plus conversion to and from on-disk `$INDEX_ROOT`, `$INDEX_ALLOCATION`, and `$BITMAP` state. It is central to directory mutation support.

Key entry points:
- `CreateBTreeFromIndex()` parses an index root, optionally recursing into index allocation nodes via `CreateBTreeNodeFromIndexNode()`.
- `CreateEmptyBTree()` creates a root node with a dummy end key for new directories.
- `NtfsInsertKey()` inserts filename keys in sorted order, descends into children, handles child split propagation, and marks nodes dirty.
- `SplitBTreeNode()` splits oversized non-root nodes, creates a right-hand sibling, promotes a median key, and installs dummy end keys.
- `DemoteBTreeRoot()` turns an oversized root into a child of a new root dummy key.
- `UpdateIndexAllocation()` and `UpdateIndexNode()` allocate index records, update child VCN references, create index buffers, and write dirty nodes back to `$INDEX_ALLOCATION`.
- `CreateIndexRootFromBTree()` serializes the root node into a resident index root.
- `AllocateIndexNode()` extends the index allocation and `$I30` bitmap and returns the new node VCN.
- `DestroyBTree*()` and `DumpBTree*()` manage/debug tree memory.

Important dependencies:
- Attribute layer: `FindAttribute`, `ReadAttribute`, `WriteAttribute`, `SetResidentAttributeDataLength`, `SetNonResidentAttributeDataLength`, `AttributeDataLength`.
- File-record mutation: `AddIndexAllocation`, `AddBitmap`, `UpdateFileRecord`.
- NTFS fixup support: `FixupUpdateSequenceArray`, `AddFixupArray`.
- Filename collation uses `RtlCompareUnicodeString`; case sensitivity follows the create/open flags.

Notable behavior and risks:
- Several write paths are explicitly incomplete: attribute lists, creating new nodes in some cases, adding a missing bitmap in `AllocateIndexNode()`, and replacing hardcoded layout math.
- `CreateIndexBufferFromBTreeNode()` uses hardcoded USA offset/count and first-entry offset values.
- `SplitBTreeNode()` uses a hardcoded `HalfSize = 2016`, so split balance assumes common 4096-byte records.
- `CreateBTreeKeyFromFilename()` does not zero the whole key before assigning fields, so `LesserChild` can be uninitialized unless callers overwrite it.
- `CreateIndexBufferFromBTreeNode()` checks size using `CurrentNodeEntry->Length` before copying the current key into that buffer location, which weakens overflow detection.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/btree.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/cleanup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ntfs/cleanup.c

Read status: complete file, 126 lines.

This file handles `IRP_MJ_CLEANUP`, separating per-file cleanup from dispatch-level resource acquisition.

Key entry points:
- `NtfsCleanupFile()` gets the FCB from `FileObject->FsContext`. Volume FCBs only decrement `OpenHandleCount`. Non-volume FCBs acquire `MainResource`, decrement `OpenHandleCount`, call `CcUninitializeCacheMap()`, set `FO_CLEANUP_COMPLETE`, and release the resource.
- `NtfsCleanup()` ignores cleanup against the global filesystem device object, otherwise acquires `DeviceExtension->DirResource`, calls `NtfsCleanupFile()`, releases the directory resource, and queues the IRP context if locking could not wait.

Important dependencies:
- FCB state from create/open paths.
- Cache manager cleanup through `CcUninitializeCacheMap`.
- Dispatch queueing through `NtfsMarkIrpContextForQueue`.

Notable behavior and risks:
- Share-access removal is left as a TODO in both volume and file cases.
- Non-volume cleanup requires both the VCB directory resource and the FCB main resource.
- Volume cleanup decrements the volume FCB open count without taking the FCB main resource.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/cleanup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/close.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ntfs/close.c

Read status: complete file, 123 lines.

This file handles `IRP_MJ_CLOSE` and releases per-open NTFS state.

Key entry points:
- `NtfsCloseFile()` reads the CCB and FCB from the file object, exits early if no CCB is attached, clears `FsContext`, `FsContext2`, and `SectionObjectPointer`, decrements the VCB open handle count, releases the FCB for normal externally-created file objects, frees any directory search pattern, then frees the CCB.
- `NtfsClose()` ignores close on the global filesystem device object, otherwise acquires `DeviceExtension->DirResource`, calls `NtfsCloseFile()`, releases the resource, and queues if needed.

Important dependencies:
- FCB reference management in `fcb.c`.
- Directory enumeration state stored in `Ccb->DirectorySearchPattern`.
- The create path's `NtfsAttachFCBToFileObject()` allocation of CCBs.

Notable behavior and risks:
- Stream file objects created internally have no `FileName.Buffer`, so their FCB is not released through the normal external-object branch.
- `DeviceExt->OpenHandleCount` is decremented only when a CCB is present.
- The `DeviceExt` parameter in `NtfsCloseFile()` is used for handle accounting and FCB release, but close correctness depends on file objects being attached consistently by create/open paths.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/close.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/create.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ntfs/create.c

Read status: complete file, 963 lines.

This file implements `IRP_MJ_CREATE`: volume opens, file opens by name or ID, overwrite handling, reparse handling, and experimental file/directory creation.

Key entry points:
- `NtfsMakeAbsoluteFilename()` converts related-file-object opens into absolute paths.
- `NtfsMoonWalkID()` reconstructs a path from an MFT ID by walking parent filename attributes back to root.
- `NtfsOpenFileById()` opens reserved/system MFT entries by ID using the `MftIdToName` table.
- `NtfsOpenFile()` resolves an absolute path, checks the FCB table, and calls `NtfsGetFCBForFile()` when needed.
- `NtfsCreateFile()` is the main create/open routine. It validates options, denies opens when the volume is locked, handles `FILE_OPEN_BY_FILE_ID`, volume opens, existing-file disposition checks, directory/non-directory constraints, reparse points, overwrite truncation, and new file/directory creation when write support is enabled.
- `NtfsCreate()` queues non-waitable creates, then serializes create/open under `DirResource`.
- `NtfsCreateDirectory()` builds a new directory file record with standard information, filename, and empty `$I30` index root, adds it to the MFT, then inserts its filename into the parent directory index.
- `NtfsCreateEmptyFileRecord()` initializes a blank FILE record with USA metadata and an attribute-end marker.
- `NtfsCreateFileRecord()` builds a normal file record with `$STANDARD_INFORMATION`, `$FILE_NAME`, and `$DATA`, then adds it to the parent directory.

Important dependencies:
- FCB lookup and attach: `NtfsGrabFCBFromTable`, `NtfsGetFCBForFile`, `NtfsAttachFCBToFileObject`.
- MFT/file-record helpers: `ReadFileRecord`, `AddNewMftEntry`, `AddStandardInformation`, `AddFileName`, `AddData`.
- Directory index mutation: `CreateEmptyBTree`, `CreateIndexRootFromBTree`, `AddIndexRoot`, `NtfsAddFilenameToDirectory`.
- Write gate: `NtfsGlobalData->EnableWriteSupport`.

Notable behavior and risks:
- Path canonicalization is still TODO; `.`/`..` and repeated separators are not normalized here.
- New creation and overwrite are denied unless experimental write support is enabled.
- Open-by-ID for user files reconstructs a path, while reserved system IDs use a fixed name table. The diagnostic print for open-by-ID references `FullPath` even when the system-ID path was used.
- Reparse support recognizes mount points and otherwise returns `STATUS_NOT_IMPLEMENTED`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/create.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/devctl.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ntfs/devctl.c

Read status: complete file, 48 lines.

This file implements `IRP_MJ_DEVICE_CONTROL` passthrough.

Key entry point:
- `NtfsDeviceControl()` gets the mounted volume extension, skips the current IRP stack location, clears `IRPCONTEXT_COMPLETE` because the lower driver will complete the IRP, and forwards the IRP to `DeviceExt->StorageDevice`.

Important dependencies:
- Correct mount initialization of `DeviceExt->StorageDevice` in `fsctl.c`.
- Dispatch completion flags in `dispatch.c`.

Notable behavior:
- The NTFS driver does not inspect device-control codes here; all device-control IRPs are forwarded to the underlying storage stack.
- Completion ownership is explicitly transferred to the lower driver.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/devctl.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/dirctl.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ntfs/dirctl.c

Read status: complete file, 622 lines.

This file implements directory enumeration for `IRP_MJ_DIRECTORY_CONTROL`.

Key entry points:
- `NtfsGetFileSize()` finds a `$DATA` stream and returns data and allocated lengths.
- `NtfsGetNamesInformation()`, `NtfsGetDirectoryInformation()`, `NtfsGetFullDirectoryInformation()`, and `NtfsGetBothDirectoryInformation()` format one directory entry into the requested Windows information class.
- `NtfsQueryDirectory()` manages search patterns in the CCB, scan restart/index flags, buffer filling, duplicate short/long-name suppression, and repeated calls to `NtfsFindFileAt()`.
- `NtfsDirectoryControl()` dispatches minor functions. Query directory is implemented; notify-change directory returns `STATUS_NOT_IMPLEMENTED`.

Important dependencies:
- Directory lookup/index traversal: `NtfsFindFileAt`.
- File-record attribute extraction: `GetBestFileNameFromRecord`, `GetFileNameFromRecord`, `GetStandardInformationFromRecord`.
- User-buffer mapping: `NtfsGetUserBuffer`.
- Per-open search state in `NTFS_CCB`.

Notable behavior and risks:
- Compressed directories are rejected with `STATUS_NOT_IMPLEMENTED`.
- Duplicate suppression only ignores immediately adjacent entries with the same MFT record.
- The per-entry helpers support partial first-entry copy semantics and return overflow when the caller buffer cannot hold a complete record.
- `NtfsQueryDirectory()` sets `Irp->IoStatus.Information`, but `NtfsDirectoryControl()` later unconditionally resets `IrpContext->Irp->IoStatus.Information = 0`, which can erase the byte count from successful queries.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/dirctl.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/dispatch.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ntfs/dispatch.c

Read status: complete file, 206 lines.

This file is the central IRP dispatcher and queue bridge for the NTFS FSD.

Key entry points:
- `NtfsFsdDispatch()` allocates an NTFS IRP context and calls `NtfsDispatch()`, completing immediately with insufficient resources if allocation fails.
- `NtfsDispatch()` enters filesystem context, marks top-level IRP state, switches on major function, calls the matching NTFS handler, completes the IRP when `IRPCONTEXT_COMPLETE` is set, queues when `IRPCONTEXT_QUEUE` is set, frees the IRP context otherwise, clears the top-level IRP, and exits filesystem context.
- `NtfsQueueRequest()` marks the IRP pending, sets can-wait, initializes a work item, and queues it to `CriticalWorkQueue`.
- `NtfsDoRequest()` runs queued work and re-enters `NtfsDispatch()`.

Important dependencies:
- All major operation handlers: create, close, cleanup, read, write, query/set file info, query/set volume info, directory control, device control, filesystem control.
- Global write gate for `IRP_MJ_WRITE` and `IRP_MJ_SET_INFORMATION`.
- Lookaside allocation/free for IRP contexts.

Notable behavior:
- Write and set-information requests are denied unless experimental write support is enabled.
- Unsupported major functions fall through with initial `STATUS_UNSUCCESSFUL`.
- The assertion before completion/queueing documents the intended mutually valid flag states.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/dispatch.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/fastio.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ntfs/fastio.c

Read status: complete file, 148 lines.

This file defines NTFS fast-I/O and cache-manager callback stubs.

Key entry points:
- `NtfsAcqLazyWrite()` and `NtfsRelLazyWrite()` are lazy-writer acquire/release callbacks and are unimplemented.
- `NtfsAcqReadAhead()` and `NtfsRelReadAhead()` are read-ahead acquire/release callbacks and are unimplemented.
- `NtfsFastIoCheckIfPossible()`, `NtfsFastIoRead()`, and `NtfsFastIoWrite()` all return `FALSE`, denying fast I/O.

Important dependencies:
- These callbacks are referenced by global cache-manager callback tables used during `CcInitializeCacheMap()`.

Notable behavior:
- Fast I/O is effectively disabled. All read/write paths must fall back to normal IRP handling.
- Lazy-write and read-ahead callbacks return failure or no-op, so cache-manager integration is minimal.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/fastio.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/fcb.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ntfs/fcb.c

Read status: complete file, 784 lines.

This file owns NTFS FCB creation, lookup, reference management, cache-map initialization, path traversal, alternate data stream parsing, and FCB attachment to file objects.

Key entry points:
- `NtfsCreateFCB()` and `NtfsDestroyFCB()` allocate/free FCBs and initialize resources/path/stream fields.
- `NtfsFCBIsDirectory()`, `NtfsFCBIsReparsePoint()`, `NtfsFCBIsCompressed()`, `NtfsFCBIsEncrypted()`, and `NtfsFCBIsRoot()` classify FCBs.
- `NtfsGrabFCB()`, `NtfsReleaseFCB()`, `NtfsAddFCBToTable()`, and `NtfsGrabFCBFromTable()` manage the VCB FCB list under a spin lock.
- `NtfsFCBInitializeCache()` creates a stream file object and initializes the cache map for an FCB.
- `NtfsMakeRootFCB()` and `NtfsOpenRootFCB()` construct/cache the root directory FCB.
- `NtfsMakeFCBFromDirEntry()` builds an FCB from a file record and filename attribute.
- `NtfsAttachFCBToFileObject()` allocates a CCB and attaches FCB/CCB/cache state to a caller file object.
- `NtfsDirFindFile()` resolves one directory element, including `name:stream` and `name:stream:$DATA` handling.
- `NtfsGetFCBForFile()` walks an absolute path component by component.
- `NtfsReadFCBAttribute()` reads a named attribute into a newly allocated buffer.

Important dependencies:
- Directory lookup: `NtfsLookupFileAt`.
- Attribute and record helpers: `ReadFileRecord`, `FindAttribute`, `ReadAttribute`, `GetBestFileNameFromRecord`, `GetStandardInformationFromRecord`.
- Cache manager: `CcInitializeCacheMap`, `CcUninitializeCacheMap`.

Notable behavior and risks:
- Directory FCBs are retained in the FCB table even when refcount reaches zero; non-directory FCBs are destroyed.
- FCB table lookup is case-insensitive and has a FIXME for comparing short names.
- `NtfsDirFindFile()` can return early on missing named stream without freeing the loaded file record.
- Path buffers are fixed at `MAX_PATH`; several paths rely on asserts or manual length checks.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/fcb.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/finfo.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ntfs/finfo.c

Read status: complete file, 786 lines.

This file implements file information query/set operations.

Key query helpers:
- `NtfsGetStandardInformation()` returns allocation size, EOF, link count, delete-pending false, and directory flag.
- `NtfsGetPositionInformation()` returns `FileObject->CurrentByteOffset`.
- `NtfsGetBasicInformation()` returns timestamps and converted file attributes from the FCB filename entry.
- `NtfsGetNameInformation()` returns the FCB path name with overflow handling.
- `NtfsGetInternalInformation()` returns the MFT index.
- `NtfsGetNetworkOpenInformation()` returns timestamps, sizes, and attributes.
- `NtfsGetStreamInformation()` walks data attributes and formats stream entries.
- `NtfsQueryInformation()` dispatches supported query classes and reports unsupported classes.

Key set helpers:
- `NtfsSetEndOfFile()` loads the file record, validates truncation through `MmCanFileBeTruncated()`, finds the selected `$DATA` stream, calls `SetAttributeDataLength()`, then updates the parent directory filename index size fields through `UpdateFileNameRecord()`.
- `NtfsSetInformation()` supports `FileEndOfFileInformation` and a hacky `FileAllocationInformation` path that delegates to EOF handling. Other classes return `STATUS_NOT_IMPLEMENTED`.

Important dependencies:
- FCB/resource locking from `fcb.c`.
- Attribute mutation: `FindAttribute`, `SetAttributeDataLength`, `AttributeDataLength`, `AttributeAllocatedLength`.
- Directory index update: `UpdateFileNameRecord`.

Notable behavior and risks:
- `GetInfoClassName()` indexes a static name table directly with the information class value; unexpected enum values can index out of range.
- Stream enumeration constructs names manually as `:<name>:$DATA`; the memory copy length includes suffix length while copying from the attribute name area, which is risky for named streams.
- Set operations acquire the FCB main resource shared in `NtfsSetInformation()`, while the operation mutates file size and metadata.
- Hardlink support is incomplete: EOF updates only the “best” filename/parent index, with a TODO to update all filename attributes.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/finfo.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/fsctl.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ntfs/fsctl.c

Read status: complete file, 1005 lines.

This file implements filesystem control handling, NTFS volume recognition, mount setup, volume metadata loading, and several user FSCTLs.

Key mount/volume helpers:
- `NtfsHasFileSystem()` queries disk geometry/partition info, reads the boot sector, validates the `"NTFS    "` OEM ID, reserved zero fields, and supported cluster sizes.
- `NtfsQueryMftZoneReservation()` reads the `NtfsMftZoneReservation` registry value.
- `NtfsGetVolumeData()` reads the boot sector into `NtfsInfo`, initializes file-record lookaside storage, reads the MFT record, finds the MFT `$DATA`, reads the `$Volume` record, extracts volume label/version/flags, creates the volume FCB, and stores MFT-zone reservation.
- `NtfsMountVolume()` validates the target, creates the volume device object, initializes the VCB, wires VPB fields, creates the stream file object and cache map, initializes resources/spin locks, sets VPB serial/label, and sends a mount notification.
- `NtfsVerifyVolume()` is a stub returning `STATUS_WRONG_VOLUME`.

Key user FSCTL helpers:
- `GetNfsVolumeData()` fills `NTFS_VOLUME_DATA_BUFFER` and optional extended version data.
- `GetNtfsFileRecord()` returns an in-use file record at or before the requested file reference.
- `GetVolumeBitmap()` validates/probes METHOD_NEITHER buffers, reads `$Bitmap:$DATA`, and returns bitmap bytes starting at an 8-cluster-aligned LCN.
- `LockOrUnlockVolume()` toggles `VCB_VOLUME_LOCKED` only for volume opens and only allows locking when the caller is the only open handle.
- `NtfsUserFsRequest()` dispatches implemented FSCTLs and returns `STATUS_NOT_IMPLEMENTED` for many USN, retrieval, move, and volume resize controls.
- `NtfsFileSystemControl()` dispatches mount, verify, and user filesystem requests by minor function.

Important dependencies:
- Low-level I/O helpers in `blockdev.c`.
- File-record and attribute readers across the NTFS driver.
- Cache manager and VPB/device-object setup.

Notable behavior and risks:
- `GetNtfsFileRecord()` decrements the requested MFT record until it finds an in-use record, with no visible lower bound.
- Several volume-data fields are placeholders: total reserved, MFT zone start, and MFT zone end.
- Many FSCTLs are intentionally unimplemented.
- Failure cleanup in mount/setup paths is partial and depends on which initialization milestones were reached.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ntfs/fsctl.c -->