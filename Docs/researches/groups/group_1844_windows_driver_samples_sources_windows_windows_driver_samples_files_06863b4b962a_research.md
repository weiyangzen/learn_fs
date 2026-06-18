# Group Research: group_1844_windows_driver_samples_sources_windows_windows_driver_samples_files_06863b4b962a

Scope: `Docs/research_subset_a.md`, source tree `sources/windows/windows-driver-samples`.

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/strucsup.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/strucsup.c

## Role

`strucsup.c` is FastFAT’s in-memory structure support layer. It creates, initializes, links, traverses, tears down, and frees the main runtime objects: `VCB`, `FCB`, `DCB`, `CCB`, nonpaged FCB extensions, resources, IRP contexts, close contexts, directory free-entry bitmaps, and volume stream file objects.

## Key Routines

- `FatInitializeVcb`: builds a mounted volume control block, references the target device, queries hotplug/removable state, initializes cache maps, dirty/bad cluster MCBs, notify state, statistics, VPB swap storage, close queues, and the virtual volume file.
- `FatTearDownVcb` / `FatDeleteVcb`: remove internal opens, uninitialize cache maps, delete root/EA structures, free VPBs, MCBs, statistics, tunnel cache, resources, and device references.
- `FatCreateRootDcb`, `FatCreateFcb`, `FatCreateDcb`: allocate and initialize root directory, file, and subdirectory control blocks, including resources, MCBs, timestamps, names, oplocks, locks, parent-child links, and allocation hints.
- `FatDeleteFcb`: validates zero open count, tears down oplocks/file locks/per-stream contexts/MCBs/name buffers/resources/nonpaged state, and unlinks from parent trees.
- `FatCreateCcb`, `FatDeleteCcb`, `FatDeallocateCcbStrings`: manage per-handle context records and query template buffers.
- `FatCreateIrpContext`, `FatDeleteIrpContext_Real`: construct and free request context state, including major/minor operation, target VCB/device, write-through state, recursive-call marking, and optional I/O context cleanup.
- `FatGetNextFcbBottomUp`, `FatGetNextFcbTopDown`: enumerate FCB/DCB trees in lock-order-sensitive ways.
- `FatSwapVpb`, `FatCheckForDismount`: detach a mounted VPB, process dismount eligibility, tear down internal opens, process delayed closes, and delete the volume device when reference counts reach zero.
- `FatConstructNamesInFcb`: builds short, OEM long, or Unicode long name representations and inserts them into parent directory splay trees.
- `FatCheckFreeDirentBitmap`: grows a directory’s free-dirent bitmap as allocation grows.
- `FatAllocateCloseContext`, `FatPreallocateCloseContext`: manage global preallocated close contexts via an interlocked SList.
- `FatEnsureStringBufferEnough`, `FatFreeStringBuffer`: utility allocation/free helpers for string buffers, avoiding freeing stack-backed buffers.
- `FatScanForDataTrack`: reads CD-ROM TOC data and allows FastFAT mounting only when media looks like a single data track, with special fallback for PD media failures.

## Important Mechanics

The file is defensive about partial initialization. Most complex creation paths track unwind resources and use `try/finally` to free partially initialized state on abnormal termination. VCB setup is especially careful because it has to balance global VCB list insertion, target device references, cache-map initialization, close-context preallocation, and VPB fallback allocation.

Directory child ordering is deliberate: DCBs are inserted at the head and FCBs at the tail of `ParentDcbQueue`, allowing child directories to be enumerated before child files for bottom-up locking and teardown.

Name construction contains nuanced FAT long-name handling. ASCII-only long names can be represented in uppercase OEM form and inserted into the OEM prefix tree. Extended Unicode names are kept in the Unicode prefix tree to avoid collisions caused by best-fit OEM mappings.

## Dependencies And Coupling

This file depends heavily on Windows kernel filesystem primitives: `ERESOURCE`, `FsRtl` advanced headers, notify sync, tunnel cache, oplocks, file locks, cache manager callbacks, VPBs, stream file objects, large MCBs, and device I/O controls. It is central to mount, create, close, verify, cleanup, dismount, and prefix lookup behavior across the FastFAT driver.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/strucsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/timesup.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/timesup.c

## Role

`timesup.c` implements FAT/NT timestamp conversion. It bridges Windows system time, local time, FAT date/time bitfields, and FAT creation-time 10-millisecond subsecond storage.

## Key Routines

- `FatNtTimeToFatTime`: converts an NT `LARGE_INTEGER` timestamp to a FAT timestamp, optionally rounding up to the next FAT two-second boundary. It converts system time to local time, validates FAT’s 1980-2107 year range, fills FAT date/time fields, optionally returns 10ms remainder data, then normalizes the input NT time back to the rounded/truncated representable value.
- `FatFatDateToNtTime`: converts a FAT date-only value to an NT system time at local midnight. Invalid FAT date fields produce zero time.
- `FatFatTimeToNtTime`: converts FAT date/time plus optional 10ms creation-time units into NT system time. It handles odd seconds from the 10ms field and clamps impossible second values above 59.
- `FatGetCurrentFatTime`: queries current system time, converts to local time, rounds up by almost two seconds, and returns the current FAT timestamp.

## Important Mechanics

FAT stores ordinary timestamps at two-second resolution, while creation time can include a 10ms field. The conversion logic preserves this distinction: non-rounded conversions retain a 10ms remainder when requested, while rounded conversions report zero remainder because the NT time has effectively been advanced to a FAT boundary.

All NT-to-FAT conversion is local-time based, matching FAT on-disk semantics. FAT-to-NT conversion turns local FAT fields back into system time.

## Dependencies And Coupling

The file uses `RtlTimeToTimeFields`, `RtlTimeFieldsToTime`, `ExSystemTimeToLocalTime`, `ExLocalTimeToSystemTime`, and `KeQuerySystemTime`. It is called by FCB/DCB creation and metadata update paths that need to populate or persist FAT directory timestamps.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/timesup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/verfysup.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/verfysup.c

## Role

`verfysup.c` implements FastFAT volume and file verification support. It handles removable-media verification, stale FCB/DCB validation, dirty/clean volume marking, deferred clean-volume work, write-protection checks, and verify-required recovery flow.

## Key Routines

- `FatMarkFcbCondition`: marks one FCB/DCB or a subtree as `FcbGood`, `FcbBad`, or `FcbNeedsToBeVerified`, updating Fast I/O state and resetting cached allocation/dirent hints when needed.
- `FatMarkDevForVerifyIfVcbMounted`: sets `DO_VERIFY_VOLUME` on the real device only if the VCB’s VPB is still mounted on that device.
- `FatVerifyVcb`: checks `DO_VERIFY_VOLUME`, handles create requests against unmounted volumes, sets hard-error verify device, and delegates state checks to `FatQuickVerifyVcb`.
- `FatVerifyFcb`: rejects dismounted volumes, tolerates deleted-file cleanup edge cases, quick-verifies the VCB, and revalidates `FcbNeedsToBeVerified` objects by walking ancestors.
- `FatDeferredCleanVolume` and `FatCleanVolumeDpc`: schedule and execute delayed clean-volume marking once dirty cached data has drained, with safeguards for racing volume teardown.
- `FatMarkVolume`: writes FAT dirty/clean state to the boot sector, FAT dirty-bit entry, and FAT32 FSInfo sector when applicable.
- `FatFspMarkVolumeDirtyWithRecover`: marks a volume dirty with surface-test request after paging I/O media errors and then completes or signals the original request.
- `FatCheckDirtyBit`: reads the boot sector dirty bit at mount/verify time and updates `VCB_STATE_FLAG_MOUNTED_DIRTY`.
- `FatVerifyOperationIsLegal`: blocks most operations after cleanup has completed, while permitting paging I/O, close, query/set information, and MDL complete cases.
- `FatResetFcb`: clears cached MCB mapping and allocation-size hints, except for real paging files where losing mapping information would be unsafe.
- `FatDetermineAndMarkFcbCondition`: reloads an FCB’s directory entry and compares short name, file size, first cluster, and attributes to decide whether the in-memory object still matches disk.
- `FatQuickVerifyVcb`: raises the right status for verify-required, not-mounted, bad, dismounted, and write-protected states.
- `FatPerformVerify`: invokes `IoVerifyVolume`, reconciles result with VCB state, may dismount stale volumes, reparses absolute creates after remount, and reposts the IRP.

## Important Mechanics

The verification model separates volume validity from file identity. A VCB can be good, not mounted, or bad, while individual FCB/DCB records can require revalidation after media changes or power transitions.

Dirty marking is compatibility-oriented. `FatMarkVolume` updates both the boot-sector dirty bit and FAT dirty-bit entry, and also refreshes FAT32 FSInfo free-cluster hints when marking clean. It bypasses FAT12 and write-protected media.

Paging files receive special treatment. Real paging files on non-removable media are kept good and retain MCB mappings because invalidating those mappings could crash the system. ReadyBoost-style paging files on removable media are allowed to reverify.

## Dependencies And Coupling

This file is tightly coupled to the mount/verify path, cache manager, VPB/device verification flags, boot-sector format, FAT allocation support, directory-entry lookup, FCB tree traversal, and exception-based FastFAT request processing.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/verfysup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/volinfo.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/volinfo.c

## Role

`volinfo.c` implements FastFAT query and set volume information dispatch paths for `IRP_MJ_QUERY_VOLUME_INFORMATION` and `IRP_MJ_SET_VOLUME_INFORMATION`.

## Key Routines

- `FatFsdQueryVolumeInformation`: top-level dispatch wrapper for query volume information. It enters the filesystem, creates an IRP context, calls the common query routine, and routes exceptions through FastFAT exception handling.
- `FatFsdSetVolumeInformation`: equivalent wrapper for set volume information.
- `FatCommonQueryVolumeInfo`: decodes the file object, verifies the root DCB, dispatches by `FS_INFORMATION_CLASS`, acquires the VCB when copying mutable volume label state, and completes the IRP.
- `FatCommonSetVolumeInfo`: requires a `UserVolumeOpen`, acquires the VCB exclusively, verifies the root DCB, and currently supports `FileFsLabelInformation`.
- `FatQueryFsVolumeInfo`: returns serial number, object support flag, and volume label with buffer-overflow-aware truncation.
- `FatQueryFsSizeInfo`: returns total/free clusters and sector/cluster geometry.
- `FatQueryFsDeviceInfo`: returns disk device type and target device characteristics.
- `FatQueryFsAttributeInfo`: returns FAT filesystem attributes, maximum component length, read-only flag, and filesystem name `FAT` or `FAT32`.
- `FatQueryFsFullSizeInfo`: returns caller and actual available allocation units, matching FAT’s global free-space view.
- `FatSetFsLabelInfo`: validates, normalizes, creates, updates, or deletes the root-directory volume label dirent and mirrors the label into the VPB.
- `FatQueryFsSectorSizeInfo`: on supported builds, calls `FsRtlGetSectorSizeInformation` for physical/logical sector size data.

## Important Mechanics

Setting a volume label is write-through and carefully ordered. The code updates the on-disk volume label dirent first, unpins/flushes repinned BCBs to surface I/O errors, and only then changes the VPB label. This avoids a window where the in-memory label claims a change that failed on disk.

Label validation converts Unicode to uppercase OEM, enforces FAT’s 11-character volume label limit, rejects illegal FAT characters and dots, handles DBCS lead bytes, strips trailing spaces, and maps an initial `0xe5` byte to FAT’s special escaped value.

Query paths mostly read stable VCB/BPB/allocation fields, but volume label queries acquire the VCB shared because the VPB label can change.

## Dependencies And Coupling

This file depends on IRP stack decoding, FastFAT file-object decoding, VCB locking, root DCB verification, BPB/allocation support, VPB label fields, directory-entry creation, pinned BCB writeback, and Windows `FILE_FS_*` information structures.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/volinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/workque.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/workque.c

## Role

`workque.c` implements FastFAT request posting to filesystem worker threads. It prepares IRPs that cannot complete synchronously, handles oplock completion reposting, locks user buffers before returning pending, and throttles per-volume worker concurrency with an overflow queue.

## Key Routines

- `FatOplockComplete`: callback from the oplock package. Successful oplock completion queues the request to the FastFAT work queue; failure completes the IRP immediately.
- `FatPrePostIrp`: prepares an IRP before the FSD returns `STATUS_PENDING`. It clears stack-based `FatIoContext` references, probes/locks user buffers for read, write, directory query, EA query/set, and selected FSCTL output buffers, then calls `IoMarkIrpPending`.
- `FatFsdPostRequest`: standard FSD helper that calls `FatPrePostIrp`, queues the request, and returns `STATUS_PENDING`.
- `FatAddToWorkque`: queues an IRP context to `CriticalWorkQueue`, or places it on the volume overflow queue if more than `FSP_PER_DEVICE_THRESHOLD` requests are already posted for that volume.

## Important Mechanics

The file enforces a per-device worker threshold of two posted requests. Additional requests with a file object are stored on the volume device object’s `OverflowQueue` under `OverflowQueueSpinLock`, preventing unbounded worker-thread fan-out for one target device.

User buffers are locked before posting because the original caller’s context may be gone when the worker thread later resumes processing. MDL read/write requests are excluded because there is no ordinary user buffer to lock.

## Dependencies And Coupling

This file is coupled to FastFAT’s FSD/FSP split, oplock callbacks, IRP context lifetime, volume device overflow queues, buffer-locking helpers, and Windows executive work items. It is the async handoff point used when requests cannot wait, need oplock continuation, or must resume in worker-thread context.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/workque.c -->