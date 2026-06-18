# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSFSControl.cpp

## Purpose

`AFSFSControl.cpp` handles IRP major file-system-control requests for the OpenAFS Windows redirector library device. It dispatches user FSCTLs, implements reparse-point query/set/delete behavior for OpenAFS symlinks, mount points, and DFS links, and routes special IPC share FSCTLs to the redirector notification pipe. Most generic volume and oplock FSCTLs are explicitly unsupported or invalid for this redirector layer.

## Important APIs, Types, And State

- `AFSFSControl` is the IRP entry point for `IRP_MN_USER_FS_REQUEST`, `IRP_MN_MOUNT_VOLUME`, and `IRP_MN_VERIFY_VOLUME`.
- `AFSProcessUserFsRequest` handles per-file FSCTL dispatch after extracting `AFSFcb` and `AFSCcb` from the file object contexts.
- `AFSProcessShareFsCtrl` handles FSCTLs issued against `AFS_SPECIAL_SHARE_FCB`, currently `FSCTL_PIPE_TRANSCEIVE`.
- `AFSParseMountPointTarget` parses OpenAFS mount target strings of form `<type>[<cell>:]<volume>`.
- Reparse data structures include Microsoft `REPARSE_DATA_BUFFER`, `REPARSE_GUID_DATA_BUFFER`, OpenAFS `AFSReparseTagInfo`, `GUID_AFS_REPARSE_GUID`, `IO_REPARSE_TAG_OPENAFS_DFS`, and subtags `OPENAFS_SUBTAG_MOUNTPOINT`, `OPENAFS_SUBTAG_SYMLINK`, and `OPENAFS_SUBTAG_UNC`.
- Runtime state comes from `pCcb->DirectoryCB->NameInformation`, `pFcb->ObjectInformation`, directory nonpaged locks, auth groups, object-info trees, and volume metadata.

## Control Flow

`AFSFSControl` obtains the current IRP stack location, switches on the minor function, calls `AFSProcessUserFsRequest` for `IRP_MN_USER_FS_REQUEST`, then completes the IRP with `AFSCompleteRequest`. Exceptions are caught through `AFSExceptionFilter`, traced, and dumped.

`AFSProcessUserFsRequest` validates that the file object has an FCB, CCB, and directory entry. Special share FCBs are delegated to `AFSProcessShareFsCtrl`. Normal requests then switch on `FsControlCode`. Oplock requests, volume lock/unlock/dismount/dirty/mounted queries, and CSC internal requests return not implemented or invalid. `FSCTL_IS_PATHNAME_VALID` succeeds, and `FSCTL_SET_PURGE_FAILURE_MODE` is accepted as a no-op success.

For `FSCTL_GET_REPARSE_POINT`, the code first checks `FILE_ATTRIBUTE_REPARSE_POINT`, verifies that the output buffer can hold the appropriate Microsoft or GUID reparse header, and locks the directory entry. If `TargetName` is not cached, it invalidates data version, sets object verify state, and calls `AFSVerifyEntry` to populate metadata. It then serializes by file type:

- `AFS_FILE_TYPE_SYMLINK` emits `IO_REPARSE_TAG_SYMLINK`. Relative targets use `SYMLINK_FLAG_RELATIVE` with one path string. Absolute targets generate a display name prefixed with `\` and a substitute name prefixed with `\??\UNC`.
- `AFS_FILE_TYPE_MOUNTPOINT` emits an OpenAFS GUID reparse buffer with `IO_REPARSE_TAG_SURROGATE | IO_REPARSE_TAG_OPENAFS_DFS`, copies `GUID_AFS_REPARSE_GUID`, and stores mount-point type, cell length, volume length, and packed cell/volume buffers.
- `AFS_FILE_TYPE_DFSLINK` emits a Microsoft symlink reparse buffer. It treats targets beginning with `\` as relative, drive-letter targets as `\??\` substitute paths, and other targets similarly to UNC-like absolute names.

For `FSCTL_SET_REPARSE_POINT`, the function validates either OpenAFS GUID-tagged data or Microsoft symlink data. OpenAFS symlink and UNC subtags become `uniTargetName`; mount-point setting is rejected as not handled. Microsoft mount points are traced but rejected, while Microsoft symlinks use the substitute name. After validation, the code resolves and references the parent `AFSObjectInfoCB` under the volume object-info tree, then calls `AFSCreateSymlink` with the CCB auth group, parent object, current file name, current object, and target. It decrements the parent object reference afterward.

For `FSCTL_DELETE_REPARSE_POINT`, the code validates that the object is a reparse point and that the input is an OpenAFS GUID reparse tag with the expected GUID. It then returns success without directly changing metadata because the expected caller pattern is delete-on-close after opening the reparse point.

`AFSProcessShareFsCtrl` handles `FSCTL_PIPE_TRANSCEIVE` by passing the CCB, input/output lengths, type-3 input buffer, user output buffer, and returned byte count to `AFSNotifyPipeTransceive`. Unknown share FSCTLs are printed but otherwise leave the default success status unchanged.

## State And Persistence Behavior

This file does not directly persist metadata except through delegated service/object operations. `FSCTL_GET_REPARSE_POINT` can force metadata verification and updates cached `TargetName`/object state through `AFSVerifyEntry`. `FSCTL_SET_REPARSE_POINT` creates or updates symlink metadata through `AFSCreateSymlink`, using parent object references to keep the parent alive during the call. `FSCTL_DELETE_REPARSE_POINT` intentionally does not remove the reparse metadata itself.

IRP-visible output state is written through `Irp->AssociatedIrp.SystemBuffer`, `Irp->UserBuffer` for pipe transceive, and `Irp->IoStatus.Information`. Locking is localized to directory entry locks for target-name access and object-info tree locks for parent lookup/reference.

## Dependencies And Integration Points

- IRP dispatch and completion rely on Windows kernel I/O manager structures and `AFSCompleteRequest`.
- Reparse serialization depends on Windows `REPARSE_DATA_BUFFER`, `REPARSE_GUID_DATA_BUFFER`, `IO_REPARSE_TAG_SYMLINK`, `IO_REPARSE_TAG_MOUNT_POINT`, and OpenAFS GUID/tag definitions.
- `AFSVerifyEntry`, `AFSCreateSymlink`, `AFSIsRelativeName`, `AFSCreateLowIndex`, `AFSLocateHashEntry`, `AFSObjectInfoIncrement/Decrement`, and directory/volume locks connect FSCTL handling to the redirector metadata cache and user-mode service.
- `AFSNotifyPipeTransceive` integrates special `IPC$` share file controls with the notification pipe subsystem.
- `AFSFcbSupport.cpp` provides the FCB/CCB shapes and node type codes used to dispatch normal vs special-share requests.

## Risks And Edge Cases

- Reparse buffer length accounting is security-sensitive because the code writes variable packed paths directly into caller buffers.
- `AFSParseMountPointTarget` assumes the target buffer has at least one character for the type and computes lengths in bytes; malformed short strings can stress boundary conditions.
- Absolute symlink/DFS target conversion manually constructs `\??\UNC` or `\??\` substitute names; path-prefix mistakes can change Windows reparse semantics.
- `FSCTL_SET_REPARSE_POINT` accepts Microsoft symlink substitute names but rejects mount points and OpenAFS mount-point subtags, so callers may see asymmetric get/set behavior.
- Parent object lookup uses the current object's `ParentFileId`; races with rename/delete are mitigated by object references but should be considered around `AFSCreateSymlink`.
- Unknown `AFSProcessShareFsCtrl` operations currently return success unless the callee changes status, which may hide unsupported IPC FSCTL usage.
- The top-level exception path traces and dumps but still returns the current `ntStatus`; callers depend on request completion already happening inside the protected block.

## Test Signals

- FSCTL dispatch tests for invalid FCB/CCB/directory context, special-share delegation, unsupported oplock/volume controls, `FSCTL_IS_PATHNAME_VALID`, and CSC internal behavior.
- Reparse get tests for symlink relative targets, symlink absolute targets, mount points with and without cells, DFS links beginning with slash, DFS drive-letter links, and DFS UNC-like targets.
- Buffer-size tests for all reparse variants, asserting `STATUS_BUFFER_TOO_SMALL` and `IoStatus.Information` values.
- Metadata refresh tests where `TargetName` is empty and `AFSVerifyEntry` succeeds or fails.
- Reparse set tests for OpenAFS GUID mismatch, invalid subtags, truncated variable buffers, Microsoft symlink parsing, rejected Microsoft mount points, parent volume/object lookup failure, and `AFSCreateSymlink` failure.
- Delete-reparse tests for non-reparse objects, tag mismatch, GUID conflict, short input buffer, and success without immediate metadata deletion.
- IPC pipe tests for `FSCTL_PIPE_TRANSCEIVE` input/output byte counts and error propagation from `AFSNotifyPipeTransceive`.
