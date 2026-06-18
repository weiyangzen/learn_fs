# Group Research: group_1705_reactos_sources_windows_reactos_drivers_filesystems_udfs_secursup_c_e5aec281cd00

Scope confirmed against `Docs/research_subset_a.md`. All ten listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/secursup.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/secursup.cpp

## Purpose

`secursup.cpp` implements UDFS security-descriptor support: IRP dispatch handlers for query/set security, ACL assignment/inheritance, security descriptor persistence in UDF named streams, and access/share checks used during open/create.

Most dispatch code is gated by `UDF_ENABLE_SECURITY`; write paths are further gated by `!UDF_READ_ONLY_BUILD`.

## Main Runtime Paths

- `UDFGetSecurity()` is the `IRP_MJ_QUERY_SECURITY` entry point. It enters the filesystem, establishes top-level IRP state, allocates a UDF IRP context, calls `UDFCommonGetSecurity()`, and routes exceptions through the UDF exception filter/handler.
- `UDFCommonGetSecurity()`:
  - extracts `FileObject`, `CCB`, `FCB`, and `NTRequiredFCB`
  - acquires the FCB main resource exclusively
  - obtains the caller buffer and requested query length
  - lazily assigns an ACL with `UDFAssignAcl()` if none is cached
  - calls `SeQuerySecurityDescriptorInfo()` into the caller buffer
  - completes or posts the IRP depending on acquisition/posting state
- `UDFSetSecurity()` and `UDFCommonSetSecurity()` mirror the dispatch structure for `IRP_MJ_SET_SECURITY`.
  - `UDFCommonSetSecurity()` rejects when `Vcb->WriteSecurity` is false.
  - It derives a `DesiredAccess` mask from security-information bits, but the computed mask is not subsequently used in this function.
  - It converts the cached descriptor to self-relative form, calls `SeSetSecurityDescriptorInfo()`, marks `UDF_NTREQ_FCB_SD_MODIFIED`, and sends a `FILE_NOTIFY_CHANGE_SECURITY` notification on success.

## ACL Persistence

- `UDFReadSecurity()` loads a security descriptor from the file’s stream directory:
  - opens the stream directory with `UDFOpenStreamDir__`
  - opens the named ACL stream `UDFGlobalData.AclName`
  - allocates a nonpaged buffer sized to the ACL stream
  - reads the stream and validates it with `RtlValidSecurityDescriptor`
  - maps missing stream directory or ACL stream to `STATUS_NO_SECURITY_ON_OBJECT`
- `UDFWriteSecurity()` writes modified descriptors back:
  - returns success without doing work when security writes are disabled, media is read-only, or the descriptor is not marked modified
  - creates the stream directory and ACL stream if needed
  - unlinks the ACL stream when the descriptor pointer is null
  - writes `RtlLengthSecurityDescriptor()` bytes and clears `UDF_NTREQ_FCB_SD_MODIFIED`

## Descriptor Construction And Ownership

- `UDFConvertToSelfRelative()` clones a descriptor through `SeQuerySecurityDescriptorInfo(FULL_SECURITY_INFORMATION)` into a nonpaged self-relative buffer.
- `UDFInheritAcl()` copies a parent descriptor with the same query API.
- `UDFBuildEmptyAcl()` allocates and initializes a bare security descriptor.
- `UDFBuildFullControlAcl()` creates a world-owned/world-group descriptor with a DACL granting `FILE_ALL_ACCESS` to `SeWorldSid`, then converts it to self-relative form.
- `UDFAssignAcl()` lazily attaches a descriptor to an FCB:
  - stream directories and streams reuse the parent file’s common FCB descriptor
  - volume security inherits from root when possible
  - ordinary files first try persisted ACL stream data, then inherit from parent, or build a full-control ACL for the root
- `UDFDeassignAcl()` either drops auto-inherited pointers without freeing or calls `SeDeassignSecurity()` for owned descriptors.

## Access Enforcement

- `UDFLookUpAcl()` ensures an ACL is assigned and returns `Fcb->NTRequiredFCB->SecurityDesc`.
- `UDFCheckAccessRights()` combines:
  - UDF read-only/media/integrity compatibility checks
  - optional `SeAccessCheck()` against the cached descriptor
  - `ACCESS_SYSTEM_SECURITY` privilege checking through `SeSinglePrivilegeCheck()`
  - Windows share-access checks via `IoCheckShareAccess()` / `IoSetShareAccess()`
- `UDFSetAccessRights()` wraps create/open-time security assignment:
  - without `UDF_ENABLE_SECURITY`, it delegates directly to `UDFCheckAccessRights()`
  - with security enabled, it uses `SeAssignSecurity()` against the parent descriptor and caller `ACCESS_STATE`, converts to self-relative form, then verifies access/share compatibility

## Integration

This file is tightly coupled to:

- FCB/CCB/VCB structures from `struct.h`
- stream-directory/file helpers such as `UDFOpenStreamDir__`, `UDFOpenFile__`, `UDFCreateFile__`, `UDFReadFile__`, `UDFWriteFile__`, and `UDFUnlinkFile__`
- UDF notification, delayed persistence, and descriptor modification flags
- Windows security manager APIs (`SeQuerySecurityDescriptorInfo`, `SeSetSecurityDescriptorInfo`, `SeAssignSecurity`, `SeAccessCheck`)

## Notable Risks

- Security is compile-time optional, so callers must tolerate `STATUS_NO_SECURITY_ON_OBJECT` or no-op persistence depending on build flags.
- Stream/stream-directory descriptors are pointer aliases to parent descriptors; `UDFDeassignAcl(..., AutoInherited=TRUE)` intentionally avoids freeing those aliases.
- `UDFCommonSetSecurity()` computes `DesiredAccess` but does not use it locally; authorization appears to be expected earlier in open/create paths.
- `UDFCheckAccessRights()` treats `Ccb` as optional in the signature, but the `ACCESS_SYSTEM_SECURITY` branch writes through `Ccb` without a local null guard.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/secursup.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/shutdown.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/shutdown.cpp

## Purpose

`shutdown.cpp` implements UDFS shutdown notification handling. On system shutdown it walks mounted UDF volumes, closes delayed/system opens, stops media-eject waiters, performs dismount/flush sequencing, and marks volumes shut down/read-only.

## Main Runtime Paths

- `UDFShutdown()` is the dispatch entry point:
  - enters filesystem context with `FsRtlEnterFileSystem()`
  - sets top-level IRP state
  - allocates a UDF IRP context
  - calls `UDFCommonShutdown()`
  - handles exceptions through the standard UDF exception path
  - completes the IRP on allocation failure
- `UDFCommonShutdown()` performs the actual volume sweep:
  - allocates a `PREVENT_MEDIA_REMOVAL_USER_IN` buffer used by dismount/eject logic
  - acquires `UDFGlobalData.GlobalDataResource`
  - iterates `UDFGlobalData.VCBQueue`
  - for each VCB not already marked `UDF_VCB_FLAGS_SHUTDOWN`:
    - optionally disables delayed close with `UDF_VCB_FLAGS_NO_DELAYED_CLOSE`
    - temporarily releases the global resource to close system delayed files under the root directory
    - closes delayed items when `UDF_DELAYED_CLOSE` is enabled
    - reacquires the global resource
    - stops the eject waiter
    - acquires the VCB resource exclusively
    - calls `UDFDoDismountSequence(Vcb, Buf, FALSE)`
    - delays one second for removable media
    - marks the volume shut down and read-only

## Synchronization

The routine uses `GlobalDataResource` for VCB queue traversal and `VCBResource` for per-volume shutdown mutation. It intentionally releases and reacquires the global resource around delayed-close work because comments indicate delayed-close helpers avoid acquiring `DelayedCloseResource` when the global resource is already held.

## Integration

This file depends on global UDFS mount state (`UDFGlobalData.VCBQueue`), VCB flags, delayed-close helpers, eject-waiter control, and dismount sequencing implemented elsewhere.

## Notable Risks

- The code advances `Link` before doing work on the current VCB because shutdown may delete or mutate the current VCB.
- Resource release/reacquire during traversal means concurrent queue changes are expected; the implementation relies on the pre-captured next link and global locking discipline.
- Shutdown forces `UDF_VCB_FLAGS_VOLUME_READ_ONLY`, preventing later write activity on volumes that remain referenced.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/shutdown.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/struct.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/struct.h

## Purpose

`struct.h` defines the core in-memory UDFS driver structures and flag constants used by dispatch, cache, FCB/CCB lifecycle, VCB integration, delayed close, statistics, and device extensions.

## Main Structures

- `UDFIdentifier`
  - common node signature and size header used by UDFS-owned allocations
- `UDFObjectName`
  - stores absolute pathname metadata for an FCB
- `UDFCCB`
  - per-open context control block
  - links into an FCB’s CCB list
  - stores file object, open/search flags, current directory index, optional search pattern, hashes, tree length, and previously granted access
- `UDFNTRequiredFCB`
  - nonpaged NT-required FCB portion
  - starts with `FSRTL_COMMON_FCB_HEADER`
  - owns section object pointers, file locks, main/paging resources, timestamps, share-access state, security descriptor, lazy-writer tracking, and close-thread state
- `UDFFCB`
  - UDFS logical file control block
  - references `UDFNTRequiredFCB`, `UDF_FILE_INFO`, owning VCB, CCB list, object name, parent FCB, delayed-close context, reference/open counts, and state flags
- `FILTER_DEV_EXTENSION` and `UDFFS_DEV_EXTENSION`
  - small device-extension node-signature structures
- `UDFIrpContext`
  - per-IRP dispatch context used by common FSD/FSP routines
  - carries IRP, major/minor function, target device, saved exception code, work item, transition buffer/MDL, and request flags
- `UDFIrpContextLite`
  - reduced delayed-close queue item
- `UDFEjectWaitContext`
  - state for asynchronous removable-media/eject handling
- `UDFBGWriteContext`
  - background write work item context
- `FILE_SYSTEM_STATISTICS`
  - UDFS statistics wrapper with FAT-compatible statistics payload and cache-line padding
- `UDFFileIDCacheItem`
  - file ID to full-name cache entry

## Flag Groups

The header defines central flag bitmasks for:

- CCB open state, cleanup state, search semantics, wildcard handling, access mode, delete-on-close, and validity
- NT-required FCB descriptor modification/list/deleted/valid state
- FCB file type/state, mapped data, delayed close, deletion, modified/accessed state, and allocation provenance
- IRP context blocking, write-through, exception, async, top-level, popup, flush, read-only, resource-acquired, forced-post, and buffer-lock state
- flush input/output flags and background-writer limits

## Integration

`struct.h` includes `Include/platform.h`, `udf_info/udf_rel.h`, and `Include/udf_common.h`, so it is a bridge between OS-specific driver state and the lower UDF metadata library. Most files in the UDFS driver depend on the FCB/CCB/VCB/IRP structures declared here.

## Notable Details

- The NT-required FCB is allocated separately rather than embedded in `UDFFCB`, with comments pointing to hard-link/symbolic-link complications.
- `UDFNTRequiredFCB.SecurityDesc` is the cached security descriptor manipulated by `secursup.cpp`.
- Several structures are documented as zone/nonpaged aligned, and flags distinguish zone-allocated from non-zone allocations.
- The `FILE_SYSTEM_STATISTICS` padding assumes the payload is no larger than a 64-byte multiple; changes to embedded structures would need care.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/struct.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/sys_spec.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/sys_spec.cpp

## Purpose

`sys_spec.cpp` is a thin compilation wrapper for system-specific UDFS support code.

## Main Contents

- Includes `udffs.h`.
- Defines the file-specific bug-check ID as `UDF_FILE_SYS_SPEC`.
- Includes the implementation file `Include/Sys_spec_lib.cpp` directly.
- Leaves `Include/tools.cpp` commented out.

## Integration

This file exists to compile the shared `Sys_spec_lib.cpp` implementation in the UDFS driver build with the kernel-mode include environment and bug-check ID expected by the rest of the driver.

## Notable Details

There is no independent logic in this file; behavior comes from `Include/Sys_spec_lib.cpp`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/sys_spec.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/sys_spec.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/sys_spec.h

## Purpose

`sys_spec.h` is the public include wrapper for UDFS system-specific support declarations.

## Main Contents

- Uses `_UDF_SYS_SPEC_H_` include guards.
- Includes `Include/Sys_spec_lib.h`.

## Integration

Other UDFS files include this header when they need the system-specific declarations supplied by the shared library header.

## Notable Details

The file contains no declarations of its own; it only wraps the shared system-specific header.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/sys_spec.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_dbg.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_dbg.cpp

## Purpose

`udf_dbg.cpp` implements debug-only support helpers for resource acquisition tracing, reference counter tracing, pool allocation tracking, and guarded wait helpers. It is compiled when `UDF_DBG` or `PRINT_ALWAYS` is defined.

## Resource Debug Wrappers

The file wraps ERESOURCE operations with optional diagnostics:

- `UDFDebugAcquireResourceSharedLite()`
- `UDFDebugAcquireSharedStarveExclusive()`
- `UDFDebugAcquireResourceExclusiveLite()`
- `UDFDebugReleaseResourceForThreadLite()`
- `UDFDebugDeleteResource()`
- `UDFDebugInitializeResourceLite()`
- `UDFDebugConvertExclusiveToSharedLite()`
- `UDFDebugAcquireSharedWaitForExclusive()`

These assert IRQL below `DISPATCH_LEVEL`, optionally print resource/thread/bug-check/line information under `TRACK_RESOURCES`, and maintain `ResCounter` / `AcqCounter`. When `USE_DLD` is enabled, blocking acquisitions are routed through deadlock-detector hooks.

## Reference Counter Debugging

- `UDFDebugInterlockedIncrement()`
- `UDFDebugInterlockedDecrement()`
- `UDFDebugInterlockedExchangeAdd()`

With `TRACK_REF_COUNTERS`, these print thread, source ID, source line, target address, and before/after values. Otherwise they directly call the normal interlocked primitive.

## Pool Tracking

When tracking is enabled, the file uses a static `MemDesc` array of 8192 descriptors:

- `DebugAllocatePool()` records address, requested length, pool type, and optionally source ID/line.
- `DebugFreePool()` finds the descriptor, updates paged/nonpaged byte counters, clears the descriptor, and frees the block.
- `AllocCountPaged`, `AllocCountNPaged`, and `cur_max` summarize tracked state.

If the descriptor table fills, allocations still proceed but are not fully tracked.

## Wait Helpers

- `UDFWaitForSingleObject()` is a simple polling wait over a `LONG` signal variable with delay intervals.
- `DbgWaitForSingleObject_()` repeatedly waits on a kernel object with a bounded timeout slice, printing “No response ?” on repeated timeouts and breaking into the debugger near the end.

## Integration

The matching macros and declarations live in `udf_dbg.h`. In debug builds, driver code can route synchronization and memory allocation through these wrappers using macros that attach bug-check ID and source line information.

## Notable Risks

- The static memory descriptor table is global and not visibly synchronized in this file.
- `UDFWaitForSingleObject()` returns `STATUS_SUCCESS` even if its polling loop exits after timeout without the signal becoming true.
- Resource tracing counters are diagnostic only; they are not enforcement mechanisms.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_dbg.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_dbg.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_dbg.h

## Purpose

`udf_dbg.h` defines the UDFS debug/trace macro layer used across the driver. It controls print routing, breakpoint behavior, protected memory wrappers, debug pool allocation, structure validation, and hex dumping.

## Main Controls

The header exposes compile-time switches such as:

- `UDF_DBG`
- `PRINT_ALWAYS`
- `TRACK_SYS_ALLOCS`
- `TRACK_SYS_ALLOC_CALLERS`
- `USE_DLD`
- `PROTECTED_MEM_RTL`
- `USE_KD_PRINT`
- `USE_MM_PRINT`
- `USE_AD_PRINT`
- `UDF_DUMP_EXTENT`
- `ALWAYS_CHECK_WAIT_TIMEOUT`
- `CHECK_REF_COUNTS`
- `VALIDATE_STRUCTURES`

## Print Macros

When debug printing is enabled:

- `KdPrint`, `MmPrint`, `TmPrint`, `PerfPrint`, `AdPrint`, `ThPrint`, and `ExtPrint` map to `DbgPrint` variants depending on feature macros.
- `AdPrint` and `ThPrint` include the current thread.
- Without debug/always-print, most macros compile to no-ops.

## Allocation And Memory Helpers

- Under `TRACK_SYS_ALLOCS`, `DbgAllocatePool`, `DbgAllocatePoolWithTag`, and `DbgFreePool` route to `DebugAllocatePool()` / `DebugFreePool()`.
- Otherwise they map directly to `ExAllocatePoolWithTag()` / `ExFreePool()`.
- Under `PROTECTED_MEM_RTL`, `DbgMoveMemory`, `DbgCopyMemory`, and `DbgCompareMemory` wrap RTL memory operations in SEH and break on exceptions.

## Breakpoint And Validation

- `UDFBreakPoint()` maps to `int 3` on x86 debug builds or `DbgBreakPoint()` elsewhere.
- `BrutePoint()` breaks only when `BRUTE` is defined.
- `ASSERT_REF()` is controlled by `CHECK_REF_COUNTS`.
- `ValidateFileInfo()` can detect deallocated or malformed `FileInfo` structures when `VALIDATE_STRUCTURES` is enabled.
- `UDFTouch()` forces a read from an address, using x86 inline assembly when available.

## Dumping

`KdDump(a,b)` hex-dumps a memory region when debug output is enabled and becomes a no-op otherwise. `UserPrint` aliases `KdPrint`.

## Integration

This header is included broadly by UDFS driver code and provides the debug abstraction layer used by `udf_dbg.cpp`, `secursup.cpp`, directory parsing, allocation diagnostics, and many support modules.

## Notable Details

- Retail/non-debug builds keep allocation and memory macros direct and remove most diagnostics.
- The protected memory macros intentionally swallow exceptions after breaking, which is useful for diagnostics but can hide the exact failing instruction flow in normal control logic.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_dbg.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_info/alloc.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_info/alloc.cpp

## Purpose

`udf_info/alloc.cpp` implements UDF disk-space and bitmap management: partition address translation, bitmap run scanning, free-space allocation, used/free/bad/zero bitmap mutation, space accounting, write-cache allocation callbacks, and low-level bit operations.

## Address Translation

- `UDFPhysLbaToPart()` converts a physical LBA to a partition-relative logical block number for a requested partition.
- `UDFPartLbaToPhys()` converts `lb_addr` partition-relative addresses to physical LBAs, with compatibility recovery for invalid partition references when `UDF_VCB_IC_INSTANT_COMPAT_ALLOC_DESCS` is set.
- `UDFGetPartNumByPhysLba()` finds the partition containing a physical LBA.
- `UDFPartStart()`, `UDFPartEnd()`, and `UDFPartLen()` return partition boundaries/lengths, including special sentinel values for whole-media or last-partition behavior.

## Bitmap Scanning

- `UDFGetBitmapLen()` returns the length of a same-valued bit run starting at a bit offset and stopping before a limit.
  - It has an x86/MSVC assembly implementation and a generic C implementation.
- `UDFFindMinSuitableExtent()` scans the free-space bitmap for an extent:
  - prefers packet/write-block alignment when useful
  - honors sequential allocation flags
  - caps requests at `UDF_MAX_EXTENT_LENGTH`
  - returns the smallest extent satisfying the request, or the largest available extent if none is large enough
  - falls back from aligned to unaligned search when needed

## Allocation And Marking

- `UDFMarkBadSpaceAsUsed()` masks bad-space bitmap bits out of the free-space bitmap.
- `UDFMarkSpaceAsXXXNoProtect_()` marks all extents in a mapping as used, free, bad, or discarded without acquiring the bitmap resource.
  - updates `BitmapModified` and volume modified state
  - skips unallocated extents
  - clips extents at media boundary
  - updates FSBM, bad-space bitmap, zero-space bitmap, VAT entries, unmap/discard cache state, and mapping records depending on operation flags
- `UDFMarkSpaceAsXXX_()` wraps the no-protect function with exclusive `BitMapResource1` acquisition.
- `UDFAllocFreeExtent_()` allocates one or more extents for a requested byte length:
  - rounds length to logical block boundaries
  - scans within `[SearchStart, SearchLim)`
  - marks allocated blocks zero-filled
  - optionally verifies newly allocated extents with `UDFCheckArea()`
  - builds/merges extent mappings
  - rolls back partial allocation on disk-full or allocation failure

## Space Accounting

- `UDFGetPartFreeSpace()` counts free bits in a partition range using `bit_count_tab`.
- `UDFGetFreeSpace()` sums partition free space for normal media or computes appendable space from `NWA`/`LastLBA` for raw/CD-R style media.
- `UDFGetTotalSpace()` sums partition lengths or derives total media span depending on raw disk/CD-R mode.

## Cache Callback

`UDFIsBlockAllocated()` is a callback for write cache code. It reports `WCACHE_BLOCK_USED` and `WCACHE_BLOCK_ZERO` based on allocation and zero-filled bitmaps unless the VCB assumes all blocks are used.

## Low-Level Bit Operations

For x86 builds, the file supplies optimized bit helpers:

- `UDFGetBit__()`
- `UDFSetBit__()`
- `UDFSetBits__()`
- `UDFClrBit__()`
- `UDFClrBits__()`

Non-MSVC or non-assembly paths use simple C loops or direct shifts.

## Integration

This file is central to allocation code used by extent mapping, file resize/write paths, directory packing, VAT handling, bad-block handling, and write-cache correctness. It depends heavily on VCB partition maps and bitmap fields (`FSBM_Bitmap`, `BSBM_Bitmap`, `ZSBM_Bitmap`, `Vat`).

## Notable Risks

- Bitmap conventions are critical: free-space bits, used bits, bad bits, and zero bits are represented by different helper macros and must stay consistent.
- Several paths assume `BitMapResource1` is already held; misuse of the no-protect variant would corrupt allocation state.
- Assembly-specific implementations have C fallbacks, but behavior must remain bit-for-bit identical across compiler/platform configurations.
- The ReactOS comment in `UDFGetTotalSpace()` notes a fixed undefined shift value, indicating this code has had portability issues.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_info/alloc.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_info/dirtree.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_info/dirtree.cpp

## Purpose

`udf_info/dirtree.cpp` implements UDF directory indexing, name hashing/search, directory packing/retagging, file-entry location caching, and linked/parallel `UDF_FILE_INFO` chain helpers.

## Directory Index Storage

- `UDFDirIndexAlloc()` allocates a frame-based directory index header plus one or more item frames.
- `UDFDirIndexFree()` releases all frames and the header.
- `UDFDirIndexGrow()` extends the last frame or appends a frame.
- `UDFDirIndexTrunc()` shrinks the directory index, preserving residual entries.
- `UDFDirIndex()` returns an item pointer by logical index, with x86 optimized and generic implementations.
- `UDFDirIndexGetFrame()`, `UDFDirIndexInitScan()`, and `UDFDirIndexScan()` support efficient sequential scans across frames.

## Hashing And Names

- `UDFBuildHashEntry()` computes directory lookup hashes:
  - POSIX/case-sensitive hash from the original UTF-16 name
  - uppercase long-name hash
  - DOS 8.3 hash generated through `UDFDOSName()`
- It marks names with `UDF_FI_FLAG_DOS` when the DOS form equals the original name.
- `UDFFindFile()` uses these hashes to search a directory:
  - exact case-sensitive matching when possible
  - fallback case-insensitive long-name matching
  - fallback DOS 8.3 alias matching for names that can be 8.3
  - optional deleted-entry filtering

## Directory Indexing

`UDFIndexDirectory()` builds an in-memory index from a directory extent:

- validates `FileInfo`
- reads the full directory extent into memory
- first scans to count `FILE_IDENT_DESC` entries
- allocates a directory index large enough for entries plus the synthetic self entry
- creates index entry `0` for `.`
- parses each file identifier:
  - computes aligned descriptor length
  - records deleted count
  - creates `..` for `FILE_PARENT`
  - decompresses and normalizes UDF Unicode names for normal entries
  - marks metadata/internal names
  - stores file-entry location, characteristics, offset, length, hashes, and file-info links
- under allocation checking, marks invalid/discarded referenced file-entry blocks as deleted
- stores the finished index in `FileInfo->Dloc->DirIndex`

## Directory Rewrite Helpers

When write support is enabled:

- `UDFPackDirectory__()` removes deleted entries and compacts directory data when `UDF_PACK_DIRS` is enabled.
  - reads valid entries
  - adjusts implementation-use padding so following tags remain block-safe
  - rewrites entries with corrected tags
  - updates `DirIndex` offsets, lengths, and associated `FileInfo` indexes
  - truncates the directory file to the new EOF
- `UDFReTagDirectory()` rewrites descriptor tags for all directory entries when the in-ICB/non-in-ICB data-location state changes.

## File Entry Location Cache

The file manages a VCB-level cache mapping file-entry LBAs to shared `UDF_DATALOC_INFO` objects:

- `UDFFindDloc()` finds a cached Dloc by LBA.
- `UDFFindDlocInMem()` finds the cache slot for a Dloc pointer.
- `UDFFindFreeDloc()` initializes/grows the Dloc cache and returns a free slot.
- `UDFAcquireDloc()` / `UDFReleaseDloc()` set and clear `UDF_FE_FLAG_UNDER_INIT`.
- `UDFStoreDloc()` attaches an existing or newly allocated Dloc to a `UDF_FILE_INFO`.
- `UDFRemoveDloc()` removes and frees a Dloc.
- `UDFUnlinkDloc()` removes a Dloc from the cache without freeing it.
- `UDFFreeDloc()` removes if cached, then frees.
- `UDFRelocateDloc()` updates the cached LBA after relocation.
- `UDFReleaseDlocList()` frees the entire VCB Dloc cache.

## Linked/Parallel FileInfo Helpers

- `UDFGetDirIndexByFileInfo()` returns the parent directory index for a file, excluding stream directories.
- `UDFLocateParallelFI()` finds a linked `FileInfo` with the same parent and directory index.
- `UDFLocateAnyParallelFI()` finds any parallel linked `FileInfo` with the same parent Dloc and index.
- `UDFInsertLinkedFile()` inserts a `FileInfo` into a circular linked chain.

## Integration

This file sits between raw on-disk descriptors from `ecma_167.h`, extent IO helpers, Unicode/name support, FCB/FileInfo lifecycle code, and allocation validation. Its directory index is the basis for path lookup, enumeration, deleted-entry cleanup, and shared hard-link-ish Dloc reuse.

## Notable Risks

- `UDFIndexDirectory()` reads the entire directory extent into memory, so very large directories depend on allocation limits and nonpaged/paged pool availability.
- Recovery from malformed descriptors is limited; utility builds can search for the next plausible file identifier, but normal corruption often returns `STATUS_FILE_CORRUPT_ERROR`.
- Dloc initialization uses a sharing-paused flag; callers must handle `STATUS_SHARING_PAUSED`.
- The code comments note multiply linked objects are not fully supported elsewhere, and this file’s linked/parallel `FileInfo` helpers are a partial cache-sharing mechanism rather than a complete hard-link model.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_info/dirtree.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_info/ecma_167.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_info/ecma_167.h

## Purpose

`ecma_167.h` defines packed C structures and constants for ECMA-167/UDF on-disk descriptors. It is the schema layer used by UDFS parsing, allocation, directory indexing, volume recognition, and file-entry handling.

## Packing And Primitive Types

- Defines `dstring` as `uint8`.
- Defines compression IDs `UDF_COMP_ID_8` and `UDF_COMP_ID_16`.
- Uses `#pragma pack(push, 1)` / `#pragma pack(pop)` so on-disk descriptors match byte layout.

## Common Descriptor Types

The header defines:

- `charspec`
- `timestamp` / `UDF_TIME_STAMP`
- `EntityID` / `regid`
- volume structure descriptors and standard identifiers (`BEA01`, `NSR02`, `NSR03`, `TEA01`, etc.)
- `EXTENT_AD` / `extent_ad` / `EXTENT_MAP`
- descriptor `tag` / `DESC_TAG`
- tag identifiers for volume and file descriptors

## Volume And Partition Descriptors

Structures include:

- `BootDesc`
- `PrimaryVolDesc`
- `AnchorVolDescPtr`
- `VolDescPtr`
- `ImpUseVolDesc`
- `PartitionDesc`
- `LogicalVolDesc`
- generic/type 1/type 2 partition maps
- `UNALLOC_SPACE_DESC`
- `TerminatingDesc`
- `GenericDesc`
- `LogicalVolIntegrityDesc`

Constants cover partition flags, partition contents, access types, partition map types, integrity types, and maximum known VDS partition count.

## File And Allocation Descriptors

The header defines:

- `lb_addr`
- extent interpretation constants:
  - `EXTENT_RECORDED_ALLOCATED`
  - `EXTENT_NOT_RECORDED_ALLOCATED`
  - `EXTENT_NOT_RECORDED_NOT_ALLOCATED`
  - `EXTENT_NEXT_EXTENT_ALLOCDESC`
- `long_ad`, `SHORT_AD`, and `EXT_AD`
- `FILE_SET_DESC`
- `PARTITION_HEADER_DESC`
- `FILE_IDENT_DESC`
- `ALLOC_EXT_DESC`
- `icbtag`
- `IndirectEntry`
- `TerminalEntry`
- `FILE_ENTRY`
- `EXTENDED_FILE_ENTRY`
- `LogicalVolHeaderDesc`
- `PathComponent`

It also defines file characteristics, ICB file types, allocation descriptor type flags, ICB flags, file permissions, record formats, and path component types.

## Extended Attributes And Bitmaps

Structures include:

- `ExtendedAttrHeaderDesc`
- `GenericAttrFormat`
- `CharSetAttrFormat`
- `AlternatePermissionsExtendedAttr`
- `FileTimesExtendedAttr`
- `InfoTimesExtendedAttr`
- `DeviceSpecificationExtendedAttr`
- `ImpUseExtendedAttr`
- `AppUseExtendedAttr`
- `UnallocatedSpaceEntry`
- `SPACE_BITMAP_DESC`
- `PartitionIntegrityEntry`

Constants define known extended attribute type IDs and file-time existence bits.

## Integration

This header is consumed throughout `udf_info` code. For this group specifically:

- `dirtree.cpp` uses `FILE_IDENT_DESC`, `tag`, file characteristics, `lb_addr`, and descriptor lengths.
- `alloc.cpp` uses `EXTENT_AD`, `EXTENT_MAP`, `lb_addr`, and extent type constants.
- higher-level file and volume code use the volume, partition, file set, and file-entry structures to parse UDF media.

## Notable Details

- Flexible trailing arrays are represented as comments rather than C flexible-array members, so callers must do manual pointer arithmetic and length validation.
- All descriptors are packed; using these structures directly on unaligned buffers requires architecture/compiler care.
- The header is schema-only: it does not validate CRCs, tag checksums, descriptor lengths, or media bounds by itself.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_info/ecma_167.h -->