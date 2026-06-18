<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/Include/AFSStructs.h -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/Include/AFSStructs.h

## Purpose
`AFSStructs.h` defines the core in-memory control blocks for the OpenAFS Windows redirector kernel library: directory headers, worker contexts, CCBs, object-information records, volume records, directory entries, gather I/O state, I/O run descriptors, name arrays, file-info snapshots, work items, directory snapshots, and byte ranges.

## Important APIs, Types, And Structures
Key structures include `AFSDirHdr` for directory B-tree/list coordination, `AFSWorkQueueContext` for worker thread state, `AFSNonPagedCcb` and `AFSCcb` for open-instance state, `AFSNonPagedObjectInfoCB` and `AFSObjectInfoCB` for file/dir metadata and reference tracking, `AFSNonPagedVolumeCB` and `AFSVolumeCB` for volume-level locks/object trees/root objects, `AFSNameInfoCB` and `AFSDirectoryCB` for directory-entry names and links, `AFSGatherIo` and `AFSIoRun` for scatter/gather cache-file I/O, `AFSNameArrayHdr`/`AFSNameArrayCB` for parsed path traversal, `AFSFileInfoCB` for file metadata transfer, `AFSWorkItem` for worker queues, `AFSSnapshotHdr`/`AFSSnapshotEntry` for directory enumeration snapshots, and `AFSByteRange` for extent range lists.

## Control Flow And Integration
The file is declarative, but the structures directly govern runtime flow. Dispatch paths obtain `AFSFcb`/`AFSCcb` pointers from file objects and use `AFSCcb` fields for auth groups, request IDs, full names, directory snapshots, granted access, and unwind metadata. Object and volume management uses embedded tree/list entries plus nonpaged locks. Worker queues pass `AFSWorkItem` unions to `AFSWorkerThread` and `AFSIOWorkerThread`; each `RequestType` selects a different union member. Read/write paths use `AFSGatherIo` and `AFSIoRun` to fan one master IRP into cache-file child I/O.

## State And Persistence
All structures are in-memory kernel state. `AFSObjectInfoCB` mirrors persistent file metadata from the OpenAFS service, including FIDs, target FIDs, expiration, data version, file type, timestamps, attributes, EOF/allocation, EA size, link count, directory child lists, and FCB pointer. `AFSVolumeCB` stores volume metadata and root object state. `AFSCcb` stores per-open state such as enumeration position, path, name array, request ID, granted access, auth group, and file unwind values. `AFSWorkItem` stores transient queued operations and embedded event/status fields for synchronous worker calls.

## Dependencies And Integration Points
The structures depend on b-tree/list primitives, Windows kernel `ERESOURCE`, `KEVENT`, `PIRP`, `PDEVICE_OBJECT`, `FILE_OBJECT`, `UNICODE_STRING`, `GUID`, `LARGE_INTEGER`, access-mask, and OpenAFS protocol types such as `AFSFileID` and `AFSVolumeInfoCB`. They are consumed by nearly every library module, especially worker, write/read, name, object, FCB, volume, extent, directory-control, cleanup, and service communication code.

## Risks And Edge Cases
Because these are shared control blocks, layout changes have broad blast radius. Nonpaged substructures carry resources used at elevated IRQL or while paged portions may not be safe. Reference-count arrays depend on `AFS_OBJECT_REFERENCE_MAX` and `AFS_VOLUME_REFERENCE_MAX`; mismatches corrupt accounting. The `AFSWorkItem` union relies on callers filling the correct member for each request type. Directory-entry lifetime depends on `DirOpenReferenceCount`, `NameArrayReferenceCount`, list/tree membership flags, and object references staying consistent. Many fields are manipulated under specific locks that are not documented in the struct definitions themselves.

## Test Signals
Test signals include special-pool and pool-tag leak detection for each structure tag, reference-count balance tests for object and volume reasons, worker queue union coverage for all request types, directory tree/list insertion and deletion validation, name-array traversal and free/reset paths, gather I/O completion races, directory snapshot enumeration, FCB/CCB open-close cleanup, PIOCtl/share request IDs, and metadata update propagation from service responses into `AFSObjectInfoCB` and `AFSFileInfoCB`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/Include/AFSStructs.h -->
