# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSNameSupport.cpp

## Purpose

`AFSNameSupport.cpp` is the Windows AFS redirector name-resolution and directory-entry mutation layer. It turns incoming NT file-object names into OpenAFS volume and directory control blocks, walks cached directory trees, evaluates special AFS objects such as symlinks, mount points, DFS links, and `@SYS`, and maintains the per-directory indexing structures used by later create, cleanup, query, and enumeration code.

The file also owns helper paths for related opens, dynamic cell/share discovery under the global root, mount-point target volume construction, DFS reparse-name construction, and fully qualified `\server\share\path` name synthesis for file information queries.

## Important APIs, Types, and Functions

- `AFSLocateNameEntry(...)` is the main path walker. Given a parsed path, current `AFSVolumeCB`, parent `AFSDirectoryCB`, and `AFSNameArrayHdr`, it returns referenced output volume, parent directory, final directory entry, optional missing component, and optional DFS target name. It honors `AFS_LOCATE_FLAGS_NO_MP_TARGET_EVAL`, `AFS_LOCATE_FLAGS_NO_SL_TARGET_EVAL`, and `AFS_LOCATE_FLAGS_NO_DFS_LINK_EVAL`.
- `AFSCreateDirEntry(...)` asks the user-mode/service side to create an object via `AFSNotifyFileCreate`, handles races against already inserted entries, verifies stale parents, and inserts the new `AFSDirectoryCB` into the parent indexes.
- `AFSInsertDirectoryNode(...)`, `AFSDeleteDirEntry(...)`, and `AFSRemoveDirNodeFromParent(...)` maintain the parent directory's case-sensitive tree, case-insensitive tree/list, optional short-name tree, and enumeration list.
- `AFSFixupTargetName(...)` splits an in-place path into parent path and final target component by scanning backward for `\`.
- `AFSParseRelatedName(...)` handles relative opens against `FileObject->RelatedFileObject`, cloning or populating the related CCB's `AFSNameArrayHdr` and building a combined full name buffer.
- `AFSParseName(...)` parses root, UNC, drive-mapped, global-root, special-share, pioctl, and ordinary share/cell paths. It validates server names, root volume readiness, wildcard rejection, dynamic cell lookup, parse flags, volume references, and parent directory references.
- `AFSCheckCellName(...)` filters Windows administrative shares, asks the service whether a global-root component is a valid AFS target, and either builds a root volume or inserts a new global-root directory entry.
- `AFSBuildMountPointTarget(...)` evaluates a mount point into a target `AFSFileID`, locates or initializes the target volume, initializes the volume root FCB if needed, and returns a volume reference held for mount-point traversal.
- `AFSBuildRootVolume(...)` is the same volume lookup/initialization path for root cell/share discovery.
- `AFSProcessDFSLink(...)` ensures a DFS link has a target name, constructs a `\Device\MUP\...` or `\??\X:\...` reparse target plus remaining path, then either stores it in the `FILE_OBJECT` and returns `STATUS_REPARSE` or returns it through `TargetName`.
- `AFSGetFullFileName(...)` writes a fully qualified `\AFSServerName + Ccb->FullFileName` string into a caller buffer, adding a trailing slash for share-root directory/mount-point names and reporting `STATUS_BUFFER_OVERFLOW` on truncation.

Core structures come from `Include/AFSStructs.h`: `AFSDirectoryCB` contains name info, object back pointer, tree/list entries, flags, nonpaged lock, and reference counts; `AFSNameInfoCB` contains long name, target name, and DOS short name; `AFSNameArrayHdr` tracks walked components, current entry, link count, and max element count. Public prototypes and flags are declared in `Include/AFSCommon.h` and `Include/AFSDefines.h`.

## Control Flow

`AFSParseName` is usually the first stage for create/open paths. It rejects wildcard and too-short names, consumes the server component, accepts drive-letter mapped forms only when `AFSIsDriveMapped` approves, checks `AFSGlobalRoot` online/verify state, enumerates the global root if needed, then handles root/global-root/pioctl/special-share cases before resolving the first share/cell component. It performs case-sensitive lookup, case-insensitive lookup with collision detection, short-name lookup, and finally service-backed `AFSCheckCellName`. On success it returns the residual path as both `FileName` and `ParsedFileName`, an initialized name array, a referenced volume, and a referenced parent directory if the open is not pure root access.

`AFSParseRelatedName` follows the same ownership pattern for relative opens. It starts from the related FCB/CCB directory, checks volume offline/invalid and verify states, allocates a combined full path buffer, appends the requested relative name with a separator when needed, populates a new name array from the related array when available, and returns a referenced parent and parse-name volume reference.

`AFSLocateNameEntry` walks the residual path after parsing. Each loop validates current references, enforces `MaxLinkCount`, updates last access, rejects deleted or pending-delete parents, verifies or evaluates stale/current objects, evaluates special object types, enumerates directories before descending, and stops when the final object or missing terminal component is reached. Component lookup dissects with `FsRtlDissectName`, ignores `.`, backs up through `AFSNameArray` on `..`, expands `@SYS` with `AFSSubstituteSysName` and `AFSSubstituteNameInPath`, then searches the parent trees in case-sensitive, case-insensitive, short-name, and dynamic-cell order. Symlink traversal rewrites the current full path for relative or absolute targets and resets/backtracks the name array appropriately. Mount-point traversal switches to the target volume root and records the target in the name array. DFS links return a Windows reparse path.

Directory mutation flows are lock-centric. `AFSCreateDirEntry` creates/evaluates externally first, then takes the parent `DirectoryNodeHdr.TreeLock` exclusively, verifies if required, handles duplicate FID races or conflicting stale names, and calls `AFSInsertDirectoryNode`. Deletion requires the parent tree lock to be exclusive, removes all name-tree links and optionally the enumeration list, releases owned buffers, decrements the object reference under the volume object tree lock, destroys the nonpaged lock, and frees the directory entry.

## State and Persistence Behavior

The persistent in-memory state is the redirector cache: volume tree entries, object info blocks, directory entries, name arrays, and full-path buffers. This file does not write disk state directly, but it invokes service/provider operations that can populate or refresh cache state: `AFSNotifyFileCreate`, `AFSEvaluateNode`, `AFSVerifyEntry`, `AFSVerifyVolume`, `AFSEnumerateDirectory`, `AFSEnumerateGlobalRoot`, `AFSEvaluateTargetByName`, `AFSEvaluateTargetByID`, `AFSInitVolume`, and `AFSInitRootFcb`.

Reference ownership is central. `AFSParseName` and `AFSParseRelatedName` return volume references with reason `AFS_VOLUME_REFERENCE_PARSE_NAME`; `AFSLocateNameEntry` returns a current volume reference with reason `AFS_VOLUME_REFERENCE_LOCATE_NAME` or `AFS_VOLUME_REFERENCE_MOUNTPT`; mount/root builders return references with `AFS_VOLUME_REFERENCE_MOUNTPT` or `AFS_VOLUME_REFERENCE_BUILD_ROOT`. Directory entries use `DirOpenReferenceCount`, while name arrays separately hold `NameArrayReferenceCount` through `AFSNameArray.cpp` helpers.

Buffer ownership is encoded with flags and path-local booleans. `AFS_PARSE_FLAG_FREE_FILE_BUFFER` tells create/open cleanup that a related-open full-name buffer was allocated. Directory flags `AFS_DIR_RELEASE_NAME_BUFFER` and `AFS_DIR_RELEASE_TARGET_NAME_BUFFER` drive delete-time frees. `AFSLocateNameEntry` may replace `RootPathName->Buffer` for symlink or `@SYS` expansion and frees superseded buffers only when it allocated/substituted them.

## Dependencies and Integration Points

This file depends on Windows kernel APIs and FSRTL helpers including `UNICODE_STRING`, `PIRP`, `PFILE_OBJECT`, `FsRtlDissectName`, `FsRtlDoesNameContainWildCards`, `FsRtlIsNameInExpression`, `RtlCompareUnicodeString`, `RtlIsNameLegalDOS8Dot3`, `ERESOURCE`, and interlocked counters.

OpenAFS dependencies include:

- B-tree helpers from `AFSBTreeSupport.cpp`: case-sensitive, case-insensitive, and short-name locate/insert/remove routines.
- Name-array helpers from `AFSNameArray.cpp`: initialization, population, insertion, backup, parent lookup, reset, and free.
- Generic/evaluation helpers from `AFSGeneric.cpp`: object lookup, verification, evaluation, target-name updates, invalidation cleanup, absolute-name checks, share-name checks, and sys-name substitution.
- Create/open integration in `AFSCreate.cpp`, which calls `AFSParseName` and `AFSLocateNameEntry` with create-option-specific locate flags and then releases returned volume/directory references.
- Query/file-info integration in `AFSFileInfo.cpp`, which calls `AFSGetFullFileName`.
- Directory enumeration and callback integration through `AFSDirControl.cpp`, `AFSCommSupport.cpp`, and cleanup/close paths that set `AFS_OBJECT_FLAGS_VERIFY`, `AFS_DIR_ENTRY_DELETED`, and related flags consumed here.

## Risks and Edge Cases

- Reference leaks or premature frees are the largest risk. Most paths manually transfer `pDirEntry`, `pParentDirEntry`, and `pCurrentVolume` into output pointers and null local variables to avoid cleanup decrements; small changes can break ownership.
- Lock ordering is delicate. Directory tree locks, directory nonpaged locks, volume locks, the global volume tree lock, and object-info tree locks are acquired in specific modes. Comments around mount-point processing explicitly avoid lock inversion.
- Path-buffer ownership is nontrivial for symlink and `@SYS` rewrites, especially when a related open already allocated the full-name buffer. Incorrect boolean propagation can double-free or leak `UNICODE_STRING.Buffer`.
- Case-insensitive lookup returns `STATUS_OBJECT_NAME_COLLISION` when multiple case variants map to the same insensitive key. Callers must not treat that like a simple not-found result.
- `AFSLocateNameEntry` maps some semantically precise errors to compatibility-oriented statuses, such as returning `STATUS_OBJECT_PATH_NOT_FOUND` instead of `STATUS_OBJECT_PATH_INVALID` for file-in-path behavior and invalid absolute symlink targets.
- DFS processing has a strict contract: exactly one of `FileObject` or `TargetName` must be supplied. Passing both or neither returns `STATUS_INVALID_PARAMETER`.
- Link traversal is bounded only by `Specific.RDR.MaxLinkCount` and `NameArray->LinkCount`; name-array resets during absolute symlink traversal intentionally preserve link count.
- Dynamic cell creation under the global root races with other lookups and callback invalidation. `AFSCreateDirEntry` and `AFSCheckCellName` both contain race handling, but stale entries can be marked deleted instead of immediately freed when counts are held.
- Short-name lookup can be disabled globally with `AFS_DEVICE_FLAG_DISABLE_SHORTNAMES`; tests must cover both configurations because lookup order changes.

## Test Signals

- Parse coverage: UNC `\\server\share\path`, drive-mapped paths, `\\server`, `\\server\all`, `\\server\all\_._AFS_IOCTL_._`, trailing slash trimming, wildcard rejection, invalid server names, unmapped drive letters, and related-file-object opens.
- Lookup coverage: exact case match, case-insensitive unique match, case-insensitive collision, DOS 8.3 short-name lookup enabled/disabled, missing terminal component vs missing intermediate component, and global-root dynamic cell discovery.
- Traversal coverage: `.`, `..`, relative symlink target, absolute AFS symlink target, invalid absolute symlink server name, symlink no-evaluate flag, mount point no-evaluate flag, mount point into cached volume, mount point into newly initialized volume, DFS no-evaluate flag, and DFS reparse target construction with and without remaining path.
- Cache validation coverage: parent/object `AFS_OBJECT_FLAGS_VERIFY`, deleted/pending-delete directory entries, stale deleted child cleanup when parent verification is pending, offline/invalid volume handling, and directory enumeration before descent.
- Ownership coverage: every successful parse/locate caller releases volume references with the returned reason, releases returned parent/final directory references, frees `AFS_PARSE_FLAG_FREE_FILE_BUFFER` buffers, and frees DFS `TargetName` buffers when using the out-parameter mode.
- Stress coverage: concurrent create/lookup of the same component, create racing with callback invalidation, link-count exhaustion, low-memory failures on name/reparse buffer allocation, and buffer-overflow behavior in `AFSGetFullFileName`.
