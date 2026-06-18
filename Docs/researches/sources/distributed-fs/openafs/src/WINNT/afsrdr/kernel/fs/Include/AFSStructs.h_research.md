# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/Include/AFSStructs.h

## Purpose
`AFSStructs.h` defines small fs-layer control structures used by library request queuing, process/auth-group tracking, DACL update work, and legacy service-table lookup.

## Important APIs, Control Flow, And State
`AFSLibraryQueueRequestCB` is a singly linked queued-IRP node used while the library is unloaded. `AFSProcessCB` is a process-tree B-tree entry keyed by process ID and contains a resource lock, flags, parent/creator process and thread IDs, active auth-group pointer, process auth-group list, and thread list. `AFSThreadCB` links thread-specific auth-group state by thread ID. `AFSSIDEntryCB` is an auth-group B-tree entry keyed by `(sessionId, SID hash)` and stores a generated GUID. `AFSProcessAuthGroupCB` stores per-process auth group list entries. `AFSSetDaclRequestCB` carries a process pointer, completion status, and event for DACL update work. `AFSSrvcTableEntry` describes the legacy system service table layout used by XP fallback code in `DriverEntry`.

## Dependencies And Integration Points
`AFSLibrarySupport.cpp` allocates and drains `AFSLibraryQueueRequestCB`. `AFSProcessSupport.cpp` allocates and frees process, thread, SID, and process-auth-group CBs. Generic B-tree helpers operate on the embedded `AFSBTreeEntry`. The service-table struct is only relevant to 32-bit XP routine lookup.

## Risks And Test Signals
Several structs store raw `GUID *` pointers rather than owned GUID values; lifetime depends on SID entries, global NoPAG GUID, or process auth lists remaining valid. Linked lists are manually freed at process destruction. Tests should cover process teardown with thread/auth lists, auth-group pointer lifetime, queued IRP node cleanup on cancel and resubmit, and 32-bit legacy build compatibility for `AFSSrvcTableEntry`.
