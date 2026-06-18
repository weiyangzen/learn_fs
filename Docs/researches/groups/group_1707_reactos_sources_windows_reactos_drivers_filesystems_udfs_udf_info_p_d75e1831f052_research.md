# Group Research: group_1707_reactos_sources_windows_reactos_drivers_filesystems_udfs_udf_info_p_d75e1831f052

Scope checked against `Docs/research_subset_a.md`. All five requested files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_info/phys_eject.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_info/phys_eject.cpp

## Purpose

`phys_eject.cpp` implements UDFS removable-media eject monitoring and dismount cleanup. It runs in kernel mode and centers on a background waiter thread that polls/receives device events, performs timed metadata/cache flushes, detects media/device loss, and executes the volume dismount/eject sequence.

## Main Entry Points

- `UDFEjectReqWaiter` at line 30: worker routine for eject/media-change monitoring.
- `UDFStopEjectWaiter` at line 673: asks the waiter to stop and optionally waits for completion.
- `UDFDoDismountSequence` at line 704: flushes, unlocks, resets, optionally ejects, and marks the VCB for unsafe IOCTL after dismount.

## Behavior

`UDFEjectReqWaiter` receives a `PUDFEjectWaitContext`, extracts the `PVCB`, target device object, and event capability state, then drains the drive event queue using `IOCTL_CDRW_GET_EVENT` when event polling is enabled. Unsupported event IOCTLs disable event use.

The main loop waits one second at a time on `Vcb->EjectWaiter->StopReq`. If stop is requested, it takes `VCBResource`, clears `Vcb->EjectWaiter`, releases the resource, signals `WaiterStopped`, frees the wait context, and exits.

On each pass it also handles background filesystem maintenance:

- Recomputes free space periodically for modified writable volumes via `UDFGetFreeSpace`.
- Updates `Vcb->LowFreeSpace` and forces a directory-tree flush when the low-space threshold is crossed.
- Honors `UDF_VCB_SKIP_EJECT_CHECK`, `SkipCountLimit`, and `SkipEjectCountLimit` to temporarily skip eject and/or flush work.
- Avoids eject checks while `UDF_VCB_FLAGS_VOLUME_LOCKED` is set.
- Verifies media/write state with `UDFVVerify`.

The timed flush section is skipped for raw disks and for zero flush periods. For non-CDR mode, it increments `BM_FlushTime` and `Tree_FlushTime`, then:

- Flushes the directory tree with `UDFFlushADirectory`, either full or lite depending on bitmap flush timing.
- Flushes cached allocation state for file entries and directories.
- Updates volume identifiers and both main/reserve VDS copies with `UDFUpdateVolIdent` and `UDFUpdateVDS`.
- Updates the logical volume integrity descriptor when appropriate.
- Copies the free-space bitmap to `FSBM_OldBitmap` after changes.
- Calls `WCacheFlushAll__` and clears modified state through `UDFClrModified` when all relevant state was flushed.

The removable-media path first tests device readiness with `IOCTL_CDRW_TEST_UNIT_READY`. Device loss jumps to the common dismount path; media loss disables actual eject and marks `MediaLoss`. Event handling supports both media event class and external request class:

- Media events detect absent/open media and repair buggy `GET_EVENT` present/door-open reports by confirming with `TEST_UNIT_READY`.
- Media eject-request events set `WC->SoftEjectReq`.
- External request key/request events also set `WC->SoftEjectReq`.

Once eject, media loss, or device failure is detected, the waiter sets `Vcb->SoftEjectReq`, disables delayed-close behavior when compiled with `UDF_DELAYED_CLOSE`, closes system delayed files, acquires `VCBResource`, calls `UDFDoDismountSequence`, clears mount/write-security state on media loss, clears waiter fields, signals `WaiterStopped`, frees the wait context, and returns.

`UDFStopEjectWaiter` is the external stop path. It sets the waiter's `StopReq` event under `VCBResource`, then waits on `Vcb->WaiterStopped` when `UDF_VCB_FLAGS_STOP_WAITER_EVENT` is set. It asserts that `Vcb->EjectWaiter` is gone before returning.

`UDFDoDismountSequence` performs the mechanical dismount work:

- Flushes the logical volume with `UDFFlushLogicalVolume`.
- Waits for `BGWriters` to drain.
- Releases write cache state with `WCacheRelease__`.
- Takes `IoResource`.
- Unlocks removable media repeatedly according to `MediaLockCount`.
- Restores read/write drive speed on non-DVD media.
- Resets the lower CDRW driver when this filesystem owns the device-driver path.
- Stops background formatting for MRW media via `IOCTL_CDRW_CLOSE_TRK_SES`.
- Optionally sends `IOCTL_STORAGE_EJECT_MEDIA`.
- Releases `IoResource`.
- Unregisters shutdown notification.
- Clears `UDF_VCB_FLAGS_MEDIA_LOCKED`.
- Sets `UDF_VCB_FLAGS_UNSAFE_IOCTL`.

## Key Dependencies

This file depends heavily on VCB state and synchronization primitives from `udf.h`/included UDFS headers:

- VCB fields: `EjectWaiter`, `VCBResource`, `IoResource`, `VCBFlags`, `Modified`, `LowFreeSpace`, `BM_FlushTime`, `Tree_FlushTime`, `FastCache`, `RootDirFCB`, `TargetDeviceObject`.
- Device IOCTL helpers: `UDFPhSendIOCTL`, `UDFTSendIOCTL`.
- Cache/flush helpers: `UDFFlushADirectory`, `UDFFlushLogicalVolume`, `WCacheFlushAll__`, `WCacheRelease__`.
- Verification/remap helper: `UDFVVerify`.
- Dismount helpers: `UDFCloseAllSystemDelayedInDir`, `UDFCloseAllDelayed`, `UDFResetDeviceDriver`.

## Concurrency and Safety Notes

The file uses `_SEH2_TRY/_SEH2_FINALLY` to guarantee `VCBResource` release when the loop exits early through `try_return`. `IoResource` protects device control sequences. The stop path and waiter cleanup coordinate through kernel events and `Vcb->EjectWaiter`.

The dismount path intentionally sets `UDF_VCB_FLAGS_UNSAFE_IOCTL` after releasing media and driver state. This flag is later used as a guard that the mounted volume should no longer trust ordinary lower-device operations.

<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_info/phys_eject.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_info/physical.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_info/physical.cpp

## Purpose

`physical.cpp` is a thin compile-unit wrapper for physical device read/write support. It includes `udf.h`, defines this unit's `UDF_BUG_CHECK_ID` as `UDF_FILE_PHYSICAL`, then directly includes `Include/phys_lib.cpp`.

## Behavior

There are no local functions or data structures in this file beyond the bug-check identifier. The actual physical I/O implementation is pulled in textually from `sources/windows/reactos/drivers/filesystems/udfs/udf_info/Include/phys_lib.cpp`.

## Dependencies

- `udf.h` provides the UDFS platform and internal declarations required by the included physical I/O library.
- `Include/phys_lib.cpp` owns the substantive implementation compiled as part of this translation unit.

## Notes

Because this file uses a `.cpp` include rather than linking a separately compiled object, `UDF_BUG_CHECK_ID` and any local preprocessor context apply to the included physical I/O code.

<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_info/physical.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_info/prec_hdr2.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_info/prec_hdr2.cpp

## Purpose

`prec_hdr2.cpp` is a minimal precompiled-header or build helper unit. It contains the copyright banner and includes `udf.h`.

## Behavior

The file defines no functions, classes, macros, or storage. Its only operational effect is to compile the UDFS umbrella header in this build context.

## Dependencies

- `udf.h`, which itself includes platform and UDFS internal headers.

## Notes

This file is likely used by the ReactOS/UDFS build to force or validate header compilation separately from larger implementation units.

<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_info/prec_hdr2.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_info/remap.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_info/remap.cpp

## Purpose

`remap.cpp` implements write verification and bad-sector relocation support for the UDFS driver. It manages an in-memory verify cache of recently written blocks, queues asynchronous verify reads, records blocks that fail write verification, and maps logical sectors through UDF sparing tables or VAT mappings.

## Local Types

- `UDF_VERIFY_ITEM`: one cached block awaiting verification. Stores LBA, CRC, copied block buffer, list link, and queued flag.
- `UDF_VERIFY_REQ_RANGE`: one contiguous verify range.
- `UDF_VERIFY_REQ`: queued work request containing a VCB, temporary buffer, and up to `MAX_VREQ_RANGES` verify ranges.

## Verification Lifecycle

`UDFVInit` initializes `Vcb->VerifyCtx` only when `Vcb->VerifyOnWrite` is enabled and the volume is not in CDR mode. It initializes `VerifyLock`, allocates `StoredBitMap` sized for `LastPossibleLBA`, initializes the list and event, and marks the context initialized.

`UDFVRelease` waits for queued verification to finish, takes `VerifyLock`, removes every cached verify item, clears `VInited`, deletes the resource, frees `StoredBitMap`, and zeroes the context.

`UDFVWaitQueued` waits while `QueuedCount` is nonzero, tracking waiters and pulsing `vrfEvent` when the queue drains.

## Verify Cache Operations

`UDFVStoreBlock` allocates a `UDF_VERIFY_ITEM` plus one block of storage, copies the written block, stores its CRC32, inserts it into the verify list, sets the corresponding `StoredBitMap` bit, and increments `ItemCount`.

`UDFVUpdateBlock` refreshes the stored buffer and CRC for an existing item.

`UDFVRemoveBlock` clears the bitmap bit, unlinks the item, decrements `ItemCount`, and frees the item.

`UDFVWrite` is called after writes. It records the written block range in the verify cache:

- If every block in the range is already cached, it updates each cached item.
- If only some are cached, the active implementation removes those partial overlapping entries and then stores the whole range again.
- If none are cached, it stores every block in the range.
- If the cache exceeds `UDF_MAX_VERIFY_CACHE`, it calls `UDFVVerify` with the lock already held.

`UDFVRead` compares later disk reads against cached write data. For each cached LBA in the read range, it either checks CRC or copies cached data when `PH_READ_VERIFY_CACHE` is requested. On CRC mismatch it restores the cached block into the caller buffer, returns `STATUS_FT_WRITE_RECOVERY`, and marks the bad block in `Vcb->BSBM_Bitmap` when allocation succeeds. Successful reads normally evict verified cache entries unless `PH_KEEP_VERIFY_CACHE` is set; `PH_FORGET_VERIFIED` forces eviction.

`UDFVForget` removes cached verify entries for a range without reading or comparing them.

## Asynchronous Verification

`UDFVVerify` selects cached verify items and groups contiguous LBAs into range requests. It avoids duplicate queueing with each item's `queued` flag, limits each request to `MAX_VREQ_RANGES`, allocates a buffer sized to the largest range, increments `QueuedCount`, and queues `UDFVWorkItem` to `CriticalWorkQueue` outside console builds. With `_CONSOLE`, it executes the work item directly.

`UDFVWorkItem` verifies each queued range. If spare blocks remain, it starts direct-cache mode, calls `UDFTIOVerify` for each range, and ends direct-cache mode. If no spare blocks remain, it logs the exhaustion and falls back to dropping entries from the verify cache by reading cached data with `PH_FORGET_VERIFIED | PH_READ_VERIFY_CACHE`. It frees request memory, decrements `QueuedCount`, and signals `vrfEvent`.

`UDFVFlush` waits for current queued work, forces verification of the remaining cache, then waits again.

## Bad Area and Sparing Support

`UDFCheckArea` reads a candidate area block-by-block or packet-by-packet depending on write-block alignment. Failed reads mark the tested extent as discarded and bad using `UDFMarkSpaceAsXXXNoProtect`.

`UDFRemapPacket` remaps a bad packet through `Vcb->SparingTable`:

- Lazily computes free spare entries when `SparingCountFree == (ULONG)-1`.
- Verifies candidate spare areas with `UDFCheckArea`.
- Marks unusable spare blocks as `SPARING_LOC_CORRUPTED`.
- Aligns the requested LBA to `SparingBlockSize`.
- Detects already remapped packets and can optionally remap a failed spare block when `RemapSpared` is true.
- Assigns the first available spare entry and decrements `SparingCountFree`.

`UDFUnmapRange` releases sparing table entries whose original packet falls fully within a freed range, marking them available again and incrementing `SparingCountFree`.

## Relocation Mapping

`UDFRelocateSector` translates one LBA. With a sparing table, it maps an original packet to the spare packet and preserves intra-packet offset. With VAT, it maps LBAs in the VAT-covered partition through `Vcb->Vat`, returning special sentinel values for next writable address or free entries. Otherwise it returns the original LBA.

`UDFAreSectorsRelocated` checks whether a range intersects a sparing-table remap or requires VAT relocation. For VAT, it treats ranges beyond `NWA` as relocated and scans each VAT entry for non-identity mappings or relevant free entries.

`UDFRelocateSectors` builds an `EXTENT_MAP` for a range whose sectors are relocated. It walks the logical range, calls `UDFRelocateSector` for each block, starts a new extent whenever physical continuity breaks, converts each extent with `UDFExtentToMapping`, and merges them with `UDFMergeMappings`.

## Key Dependencies

This file uses:

- VCB verification state: `Vcb->VerifyCtx`, `VerifyOnWrite`, `CDR_Mode`, `BlockSize`, `BlockSizeBits`, `LastPossibleLBA`.
- Cache/direct I/O helpers: `WCacheStartDirect__`, `WCacheEODirect__`, `UDFTIOVerify`, `UDFTRead`.
- Bitmap helpers: `UDFSetBit`, `UDFClrBit`, `UDFGetBit`, `UDFSetUsedBit`.
- Remap state: `SparingTable`, `SparingCount`, `SparingBlockSize`, `SparingCountFree`, `Vat`, `VatCount`, `NWA`, `Partitions`.
- Extent helpers: `UDFExtentToMapping`, `UDFMergeMappings`, `UDFMarkSpaceAsXXXNoProtect`.

## Risk Notes

The verify cache is protected by `VerifyLock`, but queued items remain in the list with `queued = TRUE` while async work runs. Correctness depends on `QueuedCount`, `vrfEvent`, and the caller-side flush/release protocol waiting before teardown.

`UDFVVerify` marks items queued before allocating all request buffers. If later allocation fails, items can remain marked queued without a work item, which may reduce future verification coverage unless another path clears or removes them.

<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_info/remap.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_info/udf.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_info/udf.h

## Purpose

`udf.h` is the local umbrella header for `udf_info` implementation files. It collects the platform layer and core UDFS internal interfaces used by the source files in this directory.

## Contents

The header includes:

- `Include/platform.h`
- `udffs.h`
- `namesup.h`

It defines no local declarations, macros, functions, or data of its own.

## Role in This Group

All implementation files in this group include `udf.h` directly. Through this header they receive Windows/kernel platform definitions, UDFS VCB/FCB structures, filesystem constants, helper macros, and name-support declarations.

<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_info/udf.h -->