# Group Research: group_1665_reactos_sources_windows_reactos_drivers_filesystems_btrfs_volume_c__9ed53e51c27e

Scope: `Docs/research_subset_a.md` only. Files read completely: `sources/windows/reactos/drivers/filesystems/btrfs/volume.c`, `sources/windows/reactos/drivers/filesystems/btrfs/worker-thread.c`, `sources/windows/reactos/drivers/filesystems/btrfs/write.c`, `sources/windows/reactos/drivers/filesystems/btrfs/xor.S`, and `sources/windows/reactos/drivers/filesystems/btrfs/xxhash.c`.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/volume.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/volume.c

## Role

This file implements the WinBtrfs/ReactOS Btrfs volume-device layer: create/close dispatch for volume device objects, raw volume read/write forwarding, mountdev and volume IOCTL handling, mount manager drive-letter coordination, PnP removal notification, degraded-mount policy lookup, and discovery/registration of physical devices that belong to a Btrfs filesystem UUID.

It sits between Windows volume/mount-manager interfaces and the filesystem VCB/device model. It aggregates one or more `volume_child` devices under a `pdo_device_extension`, exposes a volume device extension to the rest of the driver, and forwards certain operations to child disk devices when safe.

## Major Responsibilities

- Maintain open/close lifetime for `volume_device_extension` objects.
- Tear down volume/PDO state in `free_vol()`, including children, PnP notifications, names, resources, detach/delete operations, and mounted-device back references.
- Forward raw volume reads and writes to the first child device, while rejecting raw writes when the Btrfs volume has more than one child device.
- Serve mountdev identifiers: device name, unique ID, stable GUID.
- Serve volume/disk/storage IOCTLs for dynamic volume status, writable checks, length, geometry, disk extents, GPT attributes, online notifications, media verification, and child passthrough.
- Ask mount manager to assign or remove drive letters.
- React to target-device query-remove notifications by asking the mounted filesystem device to query-remove.
- Check registry policy for degraded mounting, globally and per filesystem UUID.
- Add discovered physical devices to the global PDO list, create a PDO when first seeing a filesystem UUID, insert child devices in generation order, attach newly available child devices to an already mounted VCB, enable the volume interface when enough devices are present, and trigger bus relation updates or no-PnP attachment paths.

## Volume Lifetime

`vol_create()` rejects opens while `vde->removing` is set, otherwise reports `FILE_OPENED` and increments `open_count`.

`vol_close()` decrements `open_count` under `pdo_list_lock` and the PDO child lock. If the last handle closes after removal was requested, it calls `free_vol()`. It also guards against `vde->dead` before and after acquiring the global lock.

`free_vol()` marks the volume dead, disconnects `Vcb->vde` from any mounted device, frees the symbolic name buffer, deletes `pdode->child_lock`, detaches from an attached device if present, unregisters every child PnP notification, frees child PnP names and child records, frees a manually allocated PDO extension in `no_pnp` mode, deletes the volume FDO, and deletes the PDO when normal PnP is in use.

## Raw Read And Write Forwarding

`vol_read()` and `vol_write()` allocate a new IRP targeted at a child device because the target device is not in this driver's stack. Both hold `pdode->child_lock` while choosing the child and waiting for completion.

Read forwarding:

- Requires at least one child.
- Uses the first child.
- Builds an IRP with `IRP_MJ_READ` and the child file object.
- Handles buffered I/O by allocating a system buffer and setting `IRP_BUFFERED_IO | IRP_DEALLOCATE_BUFFER | IRP_INPUT_OPERATION`; direct I/O reuses the caller MDL; neither-buffered/direct maps the caller MDL to a system address.
- Copies read length and byte offset, waits for completion, copies `Information` back, completes the original IRP.

Write forwarding:

- Requires at least one child.
- Rejects writes when more than one child is present, returning `STATUS_ACCESS_DENIED`.
- Builds an `IRP_MJ_WRITE` similarly to read forwarding.
- For buffered I/O it points the child IRP system buffer and user buffer at the mapped caller buffer, without allocating a new copy.
- Waits synchronously, propagates status and byte count, completes the original IRP.

## IOCTL Handling

`vol_device_control()` dispatches known control codes directly and otherwise tries `vol_ioctl_passthrough()` when the volume has exactly one child.

Direct handlers include:

- `IOCTL_MOUNTDEV_QUERY_DEVICE_NAME`: returns `vde->name` as `MOUNTDEV_NAME`.
- `IOCTL_MOUNTDEV_QUERY_UNIQUE_ID`: returns the filesystem UUID from `pdode->uuid`.
- `IOCTL_STORAGE_GET_DEVICE_NUMBER`: returns the child disk and partition number only for a single child with a valid disk number.
- `IOCTL_MOUNTDEV_QUERY_STABLE_GUID`: returns the filesystem UUID as the stable GUID.
- `IOCTL_VOLUME_GET_GPT_ATTRIBUTES`: returns zero GPT attributes.
- `IOCTL_VOLUME_IS_DYNAMIC`: writes one byte set to `1`.
- `IOCTL_VOLUME_ONLINE` and `IOCTL_VOLUME_POST_ONLINE`: no-op success.
- `IOCTL_DISK_GET_DRIVE_GEOMETRY`: synthesizes CHS geometry from total child size and device sector size.
- `IOCTL_DISK_IS_WRITABLE`: probes children with `IOCTL_DISK_IS_WRITABLE`.
- `IOCTL_DISK_GET_LENGTH_INFO`: sums child `vc->size`.
- `IOCTL_STORAGE_CHECK_VERIFY` and `IOCTL_DISK_CHECK_VERIFY`: checks every child with `IOCTL_STORAGE_CHECK_VERIFY`.
- `IOCTL_VOLUME_GET_VOLUME_DISK_EXTENTS`: aggregates disk extents from every child.

`vol_ioctl_passthrough()` rejects zero-child and multi-child volumes, allocates a child IRP, copies major/minor function, IOCTL parameters, buffers, MDL, user buffer, and flags, waits for completion, copies status and information back, then frees the IRP.

## Disk Extents, Length, Geometry, Writability

`vol_get_disk_extents()` first counts the extents returned by every child, tracks the largest child response needed, then either reports `STATUS_BUFFER_OVERFLOW` with the required count or re-queries each child and concatenates all `DISK_EXTENT` entries into the caller buffer.

`vol_get_length()` sums `volume_child.size` across all children.

`vol_get_drive_geometry()` sums child sizes and reports a synthetic geometry with sector size from `DeviceObject->SectorSize` or 512 bytes, 63 sectors per track, 255 tracks per cylinder, and removable/fixed media based on device characteristics.

`vol_is_writable()` checks whether any child accepts `IOCTL_DISK_IS_WRITABLE` and tracks `STATUS_MEDIA_WRITE_PROTECTED` versus other errors. The function computes a `Status`, but currently returns `STATUS_SUCCESS` unconditionally after releasing the child lock, which weakens write-protection reporting.

## Mount Manager And Drive Letters

`mountmgr_add_drive_letter()` sends `IOCTL_MOUNTMGR_NEXT_DRIVE_LETTER` for a device path and logs whether a drive letter was assigned.

`drive_letter_callback2()` snapshots child PnP names into a temporary list, removes existing drive-letter links through mount manager, records whether each child previously had a letter in `vc->had_drive_letter`, and frees temporary records. It deliberately drops `child_lock` while calling mount manager, then reacquires it to update matching children by device UUID.

`drive_letter_callback()` obtains the mount manager device object and invokes `drive_letter_callback2()`.

## PnP And Degraded Mounts

`pnp_removal()` handles `GUID_TARGET_DEVICE_QUERY_REMOVE` by delegating query-remove to the mounted filesystem device when present.

`allow_degraded_mount()` builds a registry subkey path under the driver registry path using the filesystem UUID string. It defaults to global `mount_allow_degraded`, opens the per-UUID key if present, reads a `REG_DWORD` value named `AllowDegraded`, and returns the resulting boolean value.

## Device Discovery And PDO Aggregation

`add_volume_device()` is the core discovery path for a device containing a Btrfs superblock:

- Ignores empty device paths.
- Acquires the global `pdo_list_lock` and searches for an existing `pdo_device_extension` by filesystem UUID.
- Opens the target device with `IoGetDeviceObjectPointer`.
- If this is the first device for the filesystem UUID, creates a PDO using either `IoReportDetectedDevice` plus manual extension allocation in `no_pnp` mode or `IoCreateDevice` with `FILE_AUTOGENERATED_DEVICE_NAME | FILE_DEVICE_SECURE_OPEN` in normal PnP mode.
- Initializes the PDO extension, child list, child count, sector size, and resources.
- For existing PDOs, rejects duplicate child device UUIDs.
- Allocates and populates a `volume_child` with device UUID, devid, generation, PnP notification handle, device/file objects, normalized PnP name, size, seeding flag, disk/partition numbers, and drive-letter state.
- Inserts the child ordered by generation, updating `pdode->num_children` from the newest superblock when appropriate.
- If the filesystem is already mounted, finds a matching missing `device` entry in the VCB and initializes it.
- Propagates removable-media characteristics.
- Enables the volume interface and processes drive letters when all expected children are loaded or one child is loaded and degraded mounting is allowed.
- Inserts new PDOs into the global list after child setup, then notifies boot/no-PnP/bus paths.

The `fail:` path dereferences the opened `FileObject`. Several earlier failure branches return without reaching `fail`, so this function relies on the exact branch structure for object lifetime.

## Dependencies And Integration Points

This file depends on driver globals (`drvobj`, `master_devobj`, `busobj`, `pdo_list_lock`, `pdo_list`, `registry_path`), volume/PDO structures from `btrfs_drv.h`, mount manager APIs, raw child-device `dev_ioctl()`, filesystem removal logic (`pnp_query_remove_device()`), device initialization (`init_device()`), boot attach (`boot_add_device()`), `AddDevice()`, drive-letter removal helpers, and global options such as `no_pnp`, `mount_allow_degraded`, and `boot_uuid`.

## Risk Notes

- `vol_is_writable()` ignores its computed failure status and always returns success.
- `vol_read()` allocates a child IRP and may allocate a buffered I/O system buffer, but the visible code does not free `Irp2` on all completion paths; correctness depends on IRP flags/completion behavior outside this file.
- Raw writes are intentionally limited to single-child volumes; multi-device Btrfs raw volume writes are denied.
- `vol_ioctl_passthrough()` copies the original IRP flags and buffer pointers to a separate IRP, so passthrough correctness depends on the target driver's interpretation of borrowed buffers and the synchronous wait.
- `add_volume_device()` mixes global PDO locking, child locking, device-object references, and no-PnP special handling; error-path lifetime is subtle.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/volume.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/worker-thread.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/worker-thread.c

## Role

This file provides a small delayed-work-queue wrapper for Btrfs read and write IRPs that cannot complete immediately. It packages an IRP and optional VCB pointer into a `WORK_QUEUE_ITEM`, queues it to `DelayedWorkQueue`, and completes the IRP from the worker routine after running the normal read or write path synchronously.

## Major Responsibilities

- Execute deferred read work through `do_read_job()`.
- Execute deferred write work through `do_write_job()`.
- Allocate and initialize `job_info` records.
- Ensure user buffers have an MDL and locked pages before a job leaves the caller context.
- Queue the worker item and free the `job_info` after execution.

## Read Job

`do_read_job()`:

- Determines whether this IRP was set as top-level via `is_top_level()`.
- Gets the `FILE_OBJECT` and FCB.
- Initializes `IoStatus.Information` to zero.
- Acquires the FCB main resource shared if the current thread does not already hold it shared.
- Calls `do_read(Irp, true, &bytes_read)` inside an SEH guard.
- Releases the FCB resource if it acquired it.
- Stores the resulting status, logs failures, completes the IRP, clears top-level IRP state if needed, and returns the status.

The `bytes_read` local is passed to `do_read()` but this wrapper relies on `Irp->IoStatus.Information` for the completed byte count.

## Write Job

`do_write_job()`:

- Captures top-level IRP state.
- Calls `write_file(Vcb, Irp, true, true)` inside an SEH guard, forcing wait/deferred-write behavior appropriate for queued execution.
- Stores the status, logs failures, completes the IRP, clears top-level IRP state if needed, and returns the status.

## Worker Dispatch

`do_job()` gets the current IRP stack location and dispatches by `MajorFunction`:

- `IRP_MJ_READ` -> `do_read_job()`
- `IRP_MJ_WRITE` -> `do_write_job()`

It frees the `job_info` after dispatch. The code assumes `ji->Irp` is non-null before dereferencing `IrpSp`; the ternary assignment allows null but the subsequent `IrpSp->MajorFunction` does not.

## Queue Setup And MDL Preparation

`add_thread_job()` allocates a nonpaged `job_info`, stores the VCB and IRP, and ensures `Irp->MdlAddress` exists:

- For read IRPs, it probes with `IoWriteAccess` because the device will write into the user buffer.
- For write IRPs, it probes with `IoReadAccess` because the device will read from the user buffer.
- It derives length from the read/write parameters.
- It rejects unexpected major functions.
- It allocates an MDL over `Irp->UserBuffer`, attaches it to the IRP, and probes/locks pages under SEH.
- On probe failure, it frees the MDL, clears `Irp->MdlAddress`, frees the job record, and returns false.

If MDL setup succeeds or an MDL was already present, the function initializes the work item and queues it.

## Dependencies And Integration Points

This file depends on `btrfs_drv.h`, `do_read()`, `write_file()`, `is_top_level()`, FCB resource state, Windows MDL probing/locking APIs, and the delayed work queue. It is called by dispatch paths such as `drv_write()` when `write_file()` returns `STATUS_PENDING`.

## Risk Notes

- `do_job()` does not guard against `ji->Irp == NULL` after assigning `IrpSp`.
- MDLs allocated here are not freed in this file; freeing is expected later in normal IRP completion/cleanup paths.
- Queued read jobs acquire the FCB resource shared only if not already held shared; they do not check exclusive ownership separately.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/worker-thread.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/write.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/write.c

## Role

This is the central WinBtrfs write path. It handles Btrfs chunk allocation, data-stripe preparation for single/mirrored/striped/parity profiles, physical child-device write IRPs, extent-list mutation, copy-on-write and no-COW/prealloc writes, file growth/truncation, cached and noncached write dispatch, alternate data stream writes, timestamps/notifications, rollback, and IRP completion for `IRP_MJ_WRITE`.

The file bridges Windows write semantics and Btrfs on-disk allocation semantics. It turns file writes into Btrfs extents and checksums, updates chunk free-space and reference tracking, sends data to the correct device stripes, and keeps the in-memory FCB/VCB state dirty for later metadata commit.

## Major Responsibilities

- Find free logical addresses inside existing chunks.
- Allocate new chunks for DATA, METADATA, SYSTEM, DUP, RAID0, RAID1, RAID10, RAID5, RAID6, RAID1C3, and RAID1C4 profiles.
- Select stripe devices based on free-space holes and approximate device usage.
- Prepare write MDLs for RAID0 and RAID10 striped writes.
- Buffer partial RAID5/6 stripes and flush them once complete.
- Generate RAID5 XOR parity and RAID6 P/Q parity.
- Send parallel write IRPs to child devices and wait for completion.
- Track missing-device tolerances by profile.
- Split, remove, insert, and roll back file extents.
- Allocate checksums unless `BTRFS_INODE_NODATASUM` is set.
- Convert inline extents to regular extents and regular extents back to inline where applicable.
- Extend/truncate file sizes and preallocate physical space.
- Handle cached writes through Cache Manager and noncached writes through direct Btrfs extent writes.
- Update inode times, sequence, subvolume root timestamps, file sizes, cache file sizes, disk counters, and directory notifications.
- Dispatch and complete write IRPs, including volume-FDO raw writes and MDL write completion.

## Chunk Free-Space Lookup

`find_data_address_in_chunk()` verifies the requested length fits remaining chunk capacity, loads the chunk cache if needed, and searches `c->space_size` for a hole:

- Exact hole size is preferred.
- If the list reaches a hole smaller than requested, it chooses the previous larger hole.
- If all listed holes are larger and the tail hole is large enough, it chooses the tail.

`get_chunk_from_address()` scans `Vcb->chunks` under `chunk_lock` and returns the chunk whose logical address range contains the requested address.

`find_new_chunk_address()` picks a logical chunk offset by scanning existing chunks from `0xc00000` and returning the first gap large enough for the new chunk.

## Chunk Allocation

`alloc_chunk()` chooses chunk and stripe sizes, selects devices/holes, builds a `CHUNK_ITEM`, creates the in-memory `chunk`, initializes locks/lists/events, subtracts device space, protects superblock-reserved areas, inserts the chunk in logical order, marks it created/changed, and returns it.

Profile policy:

- DATA chunks use up to 1 GiB per stripe and up to 10 GiB per chunk.
- METADATA chunks use 1 GiB per stripe above 50 GiB total device size, otherwise 256 MiB.
- SYSTEM chunks use 32 MiB stripes and 64 MiB max chunk size.
- Max chunk size and stripe size are capped to roughly 10 percent of total device size.
- RAID5/6 set the RAID56 incompat flag.

Stripe selection:

- `find_new_stripe()` chooses a hole on a writable, non-relocating, present device, avoiding devices already selected for the same chunk. It favors the least-used device and a hole that fits `max_stripe_size`; if allowed and not full-size, it falls back to the largest available hole.
- `find_new_dup_stripes()` finds two holes on one device for DUP, again favoring least-used devices, and can split a single large hole into two DUP stripes.
- Degraded allocation can add missing-device stripes when `Vcb->options.allow_degraded` permits it and the profile has allowed missing stripes.

The function initializes `c->space` and `c->space_size` with one free logical range, creates `range_locks`, `partial_stripes`, `changed_extents`, and chunk resources, and updates each selected device's `bytes_used`.

## Stripe Write Preparation

`write_data()` is the profile dispatcher. It finds the target chunk, allocates a `write_stripe` array, calls the appropriate preparation routine, checks whether missing devices exceed profile tolerance, creates per-stripe `write_data_stripe` records and IRPs, and records total physical bytes for disk counters.

Profile behavior:

- Single/DUP/RAID1/RAID1C3/RAID1C4 write the same logical data to every present stripe and allow all but one stripe to be missing.
- RAID0 uses `prepare_raid0_write()` and allows no missing devices.
- RAID10 uses `prepare_raid10_write()` and allows one missing device.
- RAID5 uses `prepare_raid5_write()` and allows one missing device.
- RAID6 uses `prepare_raid6_write()` and allows two missing devices.

`prepare_raid0_write()` and `prepare_raid10_write()` compute per-stripe logical ranges, build partial MDLs over the caller or scratch buffer, and split page frame numbers by stripe. RAID10 mirrors each logical stripe across `sub_stripes`.

For non-file writes or unaligned buffers, these routines may allocate a nonpaged scratch copy or probe/lock an MDL over the kernel buffer.

## RAID5/6 Partial Stripes And Parity

`add_partial_stripe()` stores partial RAID5/6 full-stripe writes in `c->partial_stripes`. It uses a bitmap where set bits mean missing sectors. When the bitmap becomes fully clear, it calls `flush_partial_stripe()`, removes the partial-stripe record, and frees its bitmap/data.

`prepare_raid5_write()`:

- Moves unaligned head/tail fragments into partial-stripe storage.
- Computes per-data-stripe ranges and parity range.
- Allocates log-stripe MDLs for data used to calculate parity.
- Allocates `wtc->parity1` and its MDL.
- Builds stripe MDLs, copies PFNs into data and parity stripes, maps log MDLs, and XORs all data stripes into `parity1`.

`prepare_raid6_write()` follows the same shape but reserves two parity stripes, allocates `parity1` and `parity2`, and computes RAID6 parity by XORing data for P and repeatedly applying `galois_double()` plus XOR for Q.

`get_raid56_lock_range()` maps a logical write to the full RAID5/6 stripe range that must be serialized. `write_data_complete()` uses this to lock parity ranges around `write_data()` and child-IRP completion.

## Physical Child Writes

`write_data_complete()` initializes a `write_data_context`, optionally locks RAID5/6 stripe ranges, calls `write_data()` under SEH, launches all non-ignored child write IRPs with `IoCallDriver()`, waits on a context event, checks each stripe status, logs device write errors, frees all stripe/MDL/parity/scratch resources, unlocks RAID5/6 ranges, and returns status.

`write_data_completion()` copies child IRP status, marks the stripe success/error/cancelled, cancels sibling pending IRPs on error, decrements `stripes_left`, and signals when the final stripe completes. A source comment says a lock is needed here; list and status updates are currently unsynchronized.

`free_write_data_stripes()` releases parity MDLs, scratch MDLs, parity buffers, scratch buffer, stripe MDLs, IRPs, and stripe records. It tracks `last_mdl` to avoid freeing the same MDL multiple times for RAID10 mirrored stripes.

## Extent Mutation

`add_extent()` inserts an extent into an FCB's extent list sorted by logical file offset.

`remove_fcb_extent()` marks an extent ignored and records a rollback entry.

`add_extent_to_fcb()` allocates a new `extent`, copies `EXTENT_DATA`, attaches checksum ownership, inserts it sorted by offset, and records an insert rollback.

`excise_extents()` removes or splits existing extents overlapping a byte range. It handles:

- Whole inline extent removal.
- Whole regular/prealloc extent removal, including changed extent reference decrement.
- Removing the beginning of an extent.
- Removing the end of an extent.
- Removing the middle, creating two replacement extents and increasing changed extent references as needed.

Checksum slices are copied for uncompressed extents. Compressed extents keep checksum buffers covering the whole compressed physical extent. Inline extents cannot be split; attempting to split one returns an internal error. The function marks extents and inode items changed and dirties the FCB.

## New Extent Insertion

`insert_extent_chunk()` assumes the caller holds `c->lock`; on success it releases the chunk lock. It finds free space in the chunk, allocates `EXTENT_DATA`/`EXTENT_DATA2`, calculates checksums when data is present and checksums are enabled, inserts the extent into the FCB, subtracts logical free space, increments inode blocks, marks dirty state, records a changed extent reference, releases the chunk lock, and writes data to the physical address if data was supplied.

`try_extend_data()` tries to append a write to the physical free space immediately after the previous file extent, when the chunk is writable/non-relocating and has the same data profile. It still creates a new extent record for the appended range.

`insert_extent()` breaks a write into `MAX_EXTENT_SIZE` pieces, tries to reuse existing chunks, allocates new chunks if necessary, falls back to fragmented insertion when allocation cannot provide a large enough contiguous region, and uses `insert_extent_chunk()` for each physical allocation.

`insert_chunk_fragmented()` allocates as many chunks as it can, then walks every writable data chunk and consumes holes in size order until the requested logical range is covered or disk space runs out.

`insert_prealloc_extent()` creates prealloc extents for file allocation. It tries existing chunks, then new chunks, then fragmented allocation, and avoids prealloc marking for paging files.

## File Truncation And Extension

`truncate_file()`:

- If truncating an inline file to a nonzero size, reads the remaining data, removes old extents, then either writes it as regular sector-aligned data or creates a shorter inline extent.
- Otherwise excises extents beyond the aligned new EOF.
- Updates inode size, allocation size, file size, and valid data length.
- Notes a FIXME to notify Cache Manager for the non-inline path.

`extend_file()`:

- Handles alternate data streams by delegating to `stream_set_end_of_file_information()`.
- Finds the last non-ignored extent and current allocation.
- Converts inline files to regular extents when the new size exceeds `max_inline`.
- Extends inline data in place by replacing the inline extent with a larger zero-padded inline extent.
- Optionally inserts prealloc extents for regular files.
- Creates either regular allocation or inline zero-filled data when extending a previously empty file.
- Updates inode size, blocks, FCB file sizes, dirty flags, and allocation size.

## Preallocated And No-COW Writes

`do_write_file_prealloc()` converts a prealloc extent, or a slice of one, into regular written extents:

- Replaces whole prealloc extents with a regular extent and writes the full range in place.
- Replaces beginning, end, or middle portions by splitting into regular and remaining prealloc extents.
- Calculates checksums for newly written regular portions when required.
- Updates changed extent references for split cases.
- Marks the underlying chunk changed.

`do_write_file()` is the core noncached logical write function:

- Walks file extents overlapping the write range.
- For unique no-COW regular extents, writes in place directly to the existing physical address.
- For unique prealloc extents, calls `do_write_file_prealloc()`.
- For gaps or copy-on-write ranges, excises existing extents and calls `insert_extent()`.
- Updates checksums in place for unexpected NODATACOW-with-checksums cases.
- Validates extent ordering in `DEBUG_PARANOID`.
- Marks extents changed and dirties the FCB.

## Top-Level Write Flow

`write_file2()` implements Windows file write semantics around the Btrfs write engine:

- Rejects zero-length writes as success.
- Validates the `FILE_OBJECT`, FCB type, and append-to-EOF sentinel.
- Uses `CcCanIWrite()` for cached throttling and rejects async noncached writes by returning `STATUS_PENDING`.
- For noncached nonpaging writes with cached sections, flushes and purges Cache Manager data under the paging resource.
- Acquires paging, tree, and FCB resources according to paging/pagefile mode.
- Extends file size when writes pass EOF, except paging writes past EOF are clipped or ignored.
- Initializes or resizes Cache Manager file sizes for cached writes.
- Handles MDL cached writes with `CcPrepareMdlWrite()`.
- Handles normal cached writes with `CcCopyWriteEx()` when available, otherwise `CcCopyWrite()`, always waiting to avoid flush-before-worker races.
- Handles alternate data stream growth and buffer writes in-memory.
- Handles noncached regular writes by choosing inline, compressed, or normal sector-aligned write ranges, reading partial old data when needed, then calling `add_extent_to_fcb()`, `write_compressed()`, or `do_write_file()`.
- Updates inode timestamps, sequence, size, dirty flags, subvolume root time, Cache Manager file sizes, current byte offset, and notifications.

`write_file()` maps the caller buffer from `SystemBuffer` or MDL/user buffer, checks byte-range locks, initializes rollback, calls `write_file2()`, updates disk counters for noncached writes, and either clears or applies rollback depending on status.

`drv_write()` is the `IRP_MJ_WRITE` dispatch routine:

- Enters filesystem context and top-level IRP handling.
- Routes volume-device writes to `vol_write()`.
- Validates VCB, FCB, CCB, user access, volume-lock state, readonly subvolume, and readonly volume state.
- Passes locked-volume raw writes to `Vpb->RealDevice`.
- Handles `IRP_MN_COMPLETE` by calling `CcMdlWriteComplete()`.
- Checks oplocks for nonpaging writes.
- Forces synchronous handling for paging I/O to avoid Cache Manager deadlocks.
- Calls `write_file()`.
- Completes nonpending IRPs; for `STATUS_PENDING`, marks pending and queues a worker job with `add_thread_job()`, falling back to immediate `do_write_job()` if queueing fails.

## Dependencies And Integration Points

This file depends on the rest of the WinBtrfs driver for chunk locking, changed extent references, free-space list operations, checksum calculation, compressed writes, file reads, rollback, notifications, stream metadata, cache initialization, volume raw writes, PnP volume state, and device error logging. It also depends on Windows kernel APIs for IRPs, MDLs, Cache Manager, FsRtl resources/oplocks/locks, disk counters, SEH, and paging-file priorities.

Key external helpers include `load_cache_chunk()`, `space_list_subtract()`, `space_list_subtract2()`, `protect_superblocks()`, `acquire_chunk_lock()`, `release_chunk_lock()`, `chunk_lock_range()`, `chunk_unlock_range()`, `flush_partial_stripe()`, `do_xor()`, `galois_double()`, `do_calc_job()`, `update_changed_extent_ref()`, `add_changed_extent_ref()`, `write_compressed()`, `read_file()`, `stream_set_end_of_file_information()`, `mark_fcb_dirty()`, `mark_fileref_dirty()`, and rollback helpers.

## Risk Notes

- `write_data_completion()` explicitly lacks locking while changing stripe states and cancelling sibling IRPs.
- The RAID preparation code performs low-level PFN copying and partial MDL construction; it assumes page-aligned lengths and offsets in several paths.
- `insert_extent_chunk()` releases `c->lock` internally only after a successful insertion, making its lock ownership contract unusual and easy to misuse.
- Many extent split paths allocate multiple replacement extents and checksum buffers before removing the original; rollback coverage is essential for correctness.
- `truncate_file()` notes that Cache Manager should be informed for one truncation path.
- `drv_write()` may queue pending writes to a worker; paging I/O is forced to wait to avoid deadlocks.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/write.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/xor.S -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/xor.S

## Role

This assembly file implements optimized in-place XOR routines for WinBtrfs parity calculations. It provides SSE2 and AVX2 versions for both x86-64 and 32-bit x86 builds.

The C-side contract is:

- `do_xor_sse2(uint8_t* buf1, uint8_t* buf2, uint32_t len)`
- `do_xor_avx2(uint8_t* buf1, uint8_t* buf2, uint32_t len)`

Both compute `buf1[i] ^= buf2[i]` for `len` bytes.

## x86-64 Implementation

Under `__x86_64__`, the file emits `.code64` routines using the Windows x64 calling convention:

- `rcx`: destination/source buffer `buf1`
- `rdx`: source buffer `buf2`
- `r8d`: byte length

`do_xor_sse2()`:

- Checks both pointers for 16-byte alignment.
- If both are aligned, processes 16-byte chunks with `movdqa`, `pxor`, and `movdqa`.
- Falls back to 8-byte scalar XOR chunks.
- Finishes with byte-by-byte XOR.

`do_xor_avx2()`:

- Checks both pointers for 32-byte alignment.
- If aligned, processes 32-byte chunks with `vmovdqa`, `vpxor`, and `vmovdqa`.
- Falls back to 8-byte scalar XOR chunks.
- Finishes with byte-by-byte XOR.

## 32-Bit x86 Implementation

For non-x86-64 builds, the file emits `.code` routines using stdcall-decorated names:

- `_do_xor_sse2@12`
- `_do_xor_avx2@12`

Arguments are read from the stack into:

- `edi`: `buf1`
- `edx`: `buf2`
- `esi`: length

Both routines save and restore `esi` and `edi`, use `ebp` as a frame pointer, and return with `ret 12`.

The SSE2 path uses 16-byte aligned vector chunks, then 4-byte scalar chunks, then byte chunks. The AVX2 path uses 32-byte aligned vector chunks, then 4-byte scalar chunks, then byte chunks.

## Dependencies And Integration Points

The file includes `asm.inc` and exports symbols consumed by the Btrfs XOR/parity layer, especially RAID5/6 write parity generation in `write.c`. Higher-level C code is responsible for selecting an available SIMD implementation and for providing valid buffers and lengths.

## Risk Notes

- The aligned vector paths use aligned loads/stores (`movdqa`/`vmovdqa`) only after checking both pointers. If either pointer is unaligned, the routine drops entirely to scalar chunks rather than using unaligned vector operations.
- The AVX2 routines do not issue `vzeroupper`; if mixed with legacy SSE code on affected processors this can have performance implications, though not a functional issue.
- The routines assume non-overlapping or safely overlapping buffers for in-place XOR semantics; no overlap handling beyond simple forward iteration is provided.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/xor.S -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/xxhash.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/xxhash.c

## Role

This file embeds Yann Collet's xxHash implementation, adapted for WinBtrfs/ReactOS build environments. It provides one-shot and streaming XXH32/XXH64 hashing plus canonical big-endian serialization helpers. In the Btrfs driver, xxHash is used as a checksum algorithm option where configured by the filesystem.

## Build And Allocation Adaptation

The file includes standard C headers and conditionally includes Windows kernel headers. Allocation is adapted by target:

- Kernel/non-`_USRDLL` builds allocate from `PagedPool` with tag `"XXH "` via `ExAllocatePoolWithTag()` and free with `ExFreePool()`.
- Non-ReactOS user DLL builds use `malloc()` and `free()`.
- ReactOS user DLL builds use `RtlAllocateHeap()` and `RtlFreeHeap()` from the process heap.

It includes `xxhash.h` with `XXH_STATIC_LINKING_ONLY` enabled so internal state structures and canonical helpers are available.

## Tuning And Portability Controls

The file preserves upstream tuning macros:

- `XXH_FORCE_MEMORY_ACCESS`: controls unaligned memory reads through `memcpy`, packed access, or direct casts.
- `XXH_ACCEPT_NULL_INPUT_POINTER`: optional null-input behavior, disabled by default.
- `XXH_FORCE_NATIVE_FORMAT`: optional native-endian mode, disabled by default so hashes are endian-independent.
- `XXH_FORCE_ALIGN_CHECK`: enabled by default on non-x86 architectures and disabled on x86/x64.

It defines compiler inline attributes, rotation helpers, byte-swap helpers, endian detection through `XXH_CPU_LITTLE_ENDIAN`, unaligned/aligned read helpers, and basic fixed-width types when needed.

## XXH32

XXH32 uses 32-bit primes and the standard four-lane accumulator for inputs at least 16 bytes. Core routines include:

- `XXH32_round()`: mixes one 32-bit input word into an accumulator.
- `XXH32_endian_align()`: one-shot hashing over aligned or unaligned input and selected endian mode.
- `XXH32()`: public one-shot API choosing aligned/unaligned and endian mode.
- `XXH32_createState()` / `XXH32_freeState()`: heap state lifecycle.
- `XXH32_reset()`: initializes accumulators from a seed.
- `XXH32_update_endian()` / `XXH32_update()`: streaming update with a 16-byte temporary buffer.
- `XXH32_digest_endian()` / `XXH32_digest()`: finalizes the streaming hash without mutating the state.
- `XXH32_copyState()`: copies streaming state.

Finalization mixes remaining 4-byte and 1-byte tails, then applies avalanche shifts and prime multiplications.

## XXH64

XXH64 mirrors the same structure with 64-bit primes and a 32-byte lane block:

- `XXH64_round()` and `XXH64_mergeRound()` implement accumulator mixing.
- `XXH64_endian_align()` performs one-shot hashing.
- `XXH64()` is the public one-shot API.
- `XXH64_createState()` / `XXH64_freeState()` allocate and free streaming state.
- `XXH64_reset()` initializes state from the seed.
- `XXH64_update_endian()` / `XXH64_update()` process streaming input with a 32-byte temporary buffer.
- `XXH64_digest_endian()` / `XXH64_digest()` finalize from streaming state.
- `XXH64_copyState()` copies state.

Finalization processes 8-byte, 4-byte, and byte tails before applying the XXH64 avalanche.

## Canonical Representation

The file implements canonical conversion helpers:

- `XXH32_canonicalFromHash()`
- `XXH64_canonicalFromHash()`
- `XXH32_hashFromCanonical()`
- `XXH64_hashFromCanonical()`

Canonical form is big-endian, so little-endian hosts byte-swap before writing canonical bytes and use big-endian reads when decoding.

## Dependencies And Integration Points

This file depends on `xxhash.h` for public types, state layouts, version constants, and public API decoration. It is self-contained otherwise, with local wrappers for allocation and memory reads. Driver checksum code can use either one-shot APIs or streaming state APIs depending on how data is buffered.

## Risk Notes

- Null input is not accepted unless `XXH_ACCEPT_NULL_INPUT_POINTER` is defined; default behavior will dereference invalid input.
- Direct or packed memory-access modes are platform/compiler dependent. The default `memcpy` path is the safest.
- Kernel builds allocate streaming state from paged pool, so callers must not use state allocation/free paths at IRQL levels where paged pool access is invalid.
- The code is an embedded third-party implementation; updates should be compared against upstream xxHash behavior and local ReactOS/WinBtrfs allocation changes.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/xxhash.c -->