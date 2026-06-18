# sources/distributed-fs/openafs/src/WINNT/afsrdr/tools/objstatus/ObjectStatus.cpp

## Purpose

`sources/distributed-fs/openafs/src/WINNT/afsrdr/tools/objstatus/ObjectStatus.cpp` implements `AFSObjectStatus`, a diagnostic tool for retrieving redirector object metadata by FID or path and for invalidating a cached object by FID. The complete 523-line file was read.

## Important APIs, Types, and Functions

`main` parses `/f`, `/n`, and `/i`. `ParseFID` splits a `Cell.Volume.VNode.Unique` string into an `AFSFileID` using hex parsing. `GetAFSFileType` maps `AFS_FILE_TYPE_FILE`, `AFS_FILE_TYPE_DIRECTORY`, `AFS_FILE_TYPE_SYMLINK`, `AFS_FILE_TYPE_MOUNTPOINT`, and `AFS_FILE_TYPE_DFSLINK` to display strings. The tool uses `AFSGetStatusInfoCB`, `AFSStatusInfoCB`, `AFSInvalidateCacheCB`, `IOCTL_AFS_GET_OBJECT_INFORMATION`, and `IOCTL_AFS_INVALIDATE_CACHE`.

## Control Flow

The program requires either a FID or a filename. If `/i` is present, it requires `/f`, builds an `AFSInvalidateCacheCB` with reason `AFS_INVALIDATE_FLUSHED`, and sends `IOCTL_AFS_INVALIDATE_CACHE`. Otherwise it builds an `AFSGetStatusInfoCB` using either the parsed FID or a wide filename. For UNC-like names it skips the first leading backslash before copying. It sends `IOCTL_AFS_GET_OBJECT_INFORMATION` with a 1024-byte in/out buffer and prints the returned FID, target FID, expiration, data version, file type, object flags, timestamps, attributes, EOF, allocation size, EA size, and link count.

## State and Persistence Behavior

Status lookup is read-only from the tool perspective. Invalidation mutates redirector cache state for the specified FID, potentially forcing subsequent metadata or data refresh from AFS. No local files or registry values are written.

## Dependencies and Integration Points

The utility opens `AFS_SYMLINK` and depends on OpenAFS user structures from `AFSUserStructs.h`. Kernel-side object status retrieval is visible in `kernel/lib/AFSGeneric.cpp` through `AFSGetObjectStatus`, with IOCTL validation in `kernel/lib/AFSDevControl.cpp` and dispatch from `kernel/fs/AFSCommSupport.cpp`.

## Risks and Edge Cases

`ParseFID` mutates the input `argv` string by replacing dots with nulls. It appends user-provided segments into a 50-byte buffer with `strcat_s`; overly long segments fail safely but are only detected during parsing. Path mode uses a fixed 256-wide-character filename buffer and a fixed 1024-byte IOCTL buffer, so long names or larger future `AFSStatusInfoCB` payloads are not handled dynamically. The `/n` path path can be omitted without validation, leaving `wchFileName` uninitialized if no FID is used. The unused `dwIOControl` local suggests an older refactor left dead state.

## Test Signals

Useful tests include FID parsing with valid and malformed four-part values, path lookup for local AFS and UNC-style names, object status of file, directory, symlink, mount point, and DFS link objects, invalidation by FID followed by a lookup that confirms cache refresh behavior, and access/error tests against nonexistent FIDs or disconnected redirector state.
