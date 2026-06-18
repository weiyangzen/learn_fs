# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSDirControl.cpp

## Purpose

`AFSDirControl.cpp` implements `IRP_MJ_DIRECTORY_CONTROL` for the Windows OpenAFS redirector library. It handles directory enumeration (`IRP_MN_QUERY_DIRECTORY`), change notification registration (`IRP_MN_NOTIFY_CHANGE_DIRECTORY`), snapshot-based enumeration stability, pseudo-entry handling for `"."`, `".."`, and PIOCtl, and FsRtl notification reporting for directory mutations.

## Important APIs, types, and functions

- `AFSDirControl(PDEVICE_OBJECT, PIRP)` dispatches minor functions to `AFSQueryDirectory` or `AFSNotifyChangeDirectory`, completes non-pending IRPs, and catches exceptions.
- `AFSQueryDirectory(PIRP)` validates that the file object references a directory/root FCB, establishes the query mask and restart/index state on the CCB, enumerates or verifies the backing directory, snapshots it, locks the caller buffer, and packs one or more directory information records.
- `AFSNotifyChangeDirectory(PIRP)` validates the directory, rejects deleted/pending-delete state, and registers the notification through `AFSFsRtlNotifyFullChangeDirectory`.
- `AFSLocateNextDirEntry(AFSObjectInfoCB *, AFSCcb *)` advances `Ccb->CurrentDirIndex`, returns dot/dot-dot pseudo-entries, PIOCtl pseudo-entry, or a snapshot-backed directory entry, and returns it with `DirOpenReferenceCount` held.
- `AFSLocateDirEntryByIndex` locates an entry by a stored directory index within the CCB snapshot.
- `AFSSnapshotDirectory(AFSFcb *, AFSCcb *, BOOLEAN)` creates a per-CCB snapshot of directory entry name hashes, skipping deleted and pending-delete entries and avoiding duplicate hashes.
- `AFSFsRtlNotifyFullChangeDirectory` builds a stable notify mask from the parent object's FID and calls `FsRtlNotifyFilterChangeDirectory`.
- `AFSFsRtlNotifyFullReportChange` builds a FID/component name path and calls `FsRtlNotifyFilterReportChange`.
- `AFSNotifyReportChangeCallback` is a framework-safe callback stub for notification filtering.
- `AFSIsNameInSnapshot` detects duplicate hashes while snapshotting.
- `AFSProcessDirectoryQueryDirect` optimizes a non-wildcard query against an unenumerated directory by asking the service to evaluate only the named target.

## Control flow

`AFSQueryDirectory` starts by retrieving `AFSFcb` and `AFSCcb` from the file object. It accepts only directory/root node types and sets an enumeration event on the FCB. Initial queries take the FCB resource exclusively, construct the query mask, and set flags such as `CCB_FLAG_FULL_DIRECTORY_QUERY`, `CCB_FLAG_DIR_OF_DIRS_ONLY`, `CCB_FLAG_MASK_CONTAINS_WILD_CARDS`, and `CCB_FLAG_MASK_PIOCTL_QUERY`. Subsequent queries take the resource shared and respect direct-query completion state.

The directory tree lock is then acquired. If the directory has not been enumerated and the mask is a non-wildcard name, `AFSProcessDirectoryQueryDirect` can query the service for just that entry. Symlink direct queries that need target attributes return `STATUS_REPARSE_OBJECT`, causing the normal enumerate/snapshot path to run. Otherwise, the directory is enumerated with `AFSEnumerateDirectory`; if marked verify, `AFSVerifyEntry` runs and the CCB snapshot is refreshed.

After snapshot setup and optional PIOCtl entry initialization, index/restart flags update `CurrentDirIndex`. The code then computes the base record length for the requested information class and loops through `AFSLocateNextDirEntry`. Each entry is filtered for delete state, mask match, directory-only semantics, and wildcard expression matching. It validates entries marked verify, computes reparse/directory/hidden attributes, fills the requested `FILE_*_DIR_INFORMATION` shape, copies as much of the filename as fits, links `NextEntryOffset`, updates `IoStatus.Information`, and handles `STATUS_BUFFER_OVERFLOW`, `STATUS_NO_SUCH_FILE`, or `STATUS_NO_MORE_FILES`.

Change notify registration builds a synthetic path based on the directory object's FID rather than the user-visible name. Reporting changes similarly uses parent FID plus component name and reports through FsRtl using the CCB as target context.

## State and persistence behavior

Directory enumeration state is stored per CCB: mask name, flags, current directory index, directory snapshot, auth group, full filename/name array, and notify mask. The snapshot persists across query calls for stable enumeration even if the underlying directory tree changes, but entries are resolved back through the live case-sensitive tree when returned.

Directory-level state lives in `AFSObjectInfoCB::Specific.Directory`, including tree locks, node counts, list heads, case-sensitive tree heads, and optional PIOCtl directory CBs. The file also updates `LastAccessCount` on snapshot entries and sets/clears enumeration state through `AFSSetEnumerationEvent` and `AFSClearEnumerationEvent`.

Notification state is held in the control device extension's `NotifySync` and `DirNotifyList`, keyed by FID-derived masks stored in CCBs.

## Dependencies and integration points

The file depends on WDK directory APIs and structures (`FILE_DIRECTORY_INFORMATION`, `FILE_FULL_DIR_INFORMATION`, `FILE_BOTH_DIR_INFORMATION`, `FILE_NAMES_INFORMATION`, `FILE_ID_*` variants, `FsRtlIsNameInExpression`, `FsRtlDoesNameContainWildCards`, `FsRtlNotifyFilterChangeDirectory`, and `FsRtlNotifyFilterReportChange`). It integrates with service/name code through `AFSEnumerateDirectory`, `AFSVerifyEntry`, `AFSValidateEntry`, `AFSRetrieveFileAttributes`, and `AFSEvaluateTargetByName`.

It interacts with `AFSCreate.cpp` through CCB initialization, name-array/full-name storage, PIOCtl directory entry creation, and notification reporting after creates. It uses globals from `AFSData.cpp`: `AFSRDRDeviceObject`, `AFSControlDeviceObject`, `AFSPIOCtlName`, `AFSGlobalDotDirEntry`, and `AFSGlobalDotDotDirEntry`.

## Risks and edge cases

- Buffer packing is sensitive. The first record may be partial with `STATUS_BUFFER_OVERFLOW`; later records must be omitted if they do not fit, with the index backed up so a later query can return them.
- Snapshot entries store hashes, not direct pointers. This avoids stale pointers but depends on hash uniqueness checks and live tree lookup.
- Direct non-wildcard service queries skip full enumeration but cannot fully handle symlink target attributes, so the `STATUS_REPARSE_OBJECT` fallback is important.
- Lock ordering spans FCB resources, directory tree locks, and CCB locks. PIOCtl initialization temporarily drops and reacquires locks, which is a concurrency-sensitive path.
- Dot-name hiding and reparse-point-to-file policy alter returned attributes and can affect user-visible enumeration behavior.
- Notification masks are FID-derived synthetic paths. They must match report paths exactly or notifications will be missed.

## Test signals

Tests should cover all supported information classes, empty directories, dot/dot-dot relative and root enumeration, restart scan, index-specified scan, single-entry scan, wildcard and case-insensitive masks, directory-only masks (`<` and `*.`), PIOCtl mask enumeration, non-wildcard direct query before enumeration, symlink fallback from direct query, small output buffers and overflow behavior, deleted/pending-delete skips, verify/enumerate refresh, hide-dot-names attributes, mountpoint/DFS/symlink reparse attributes, notify registration, notify report delivery, and concurrent enumeration while directory contents change.
