# sources/distributed-fs/openafs/src/WINNT/afsrdr/common/AFSRedirCommonStructs.h

## Purpose
Defines internal kernel/library redirector structures for trees, queues, FCBs, extents, device extensions, provider connections, callbacks, and library initialization. It is the in-memory schema for afsredir and its service library.

## Important APIs, Types, And Functions
Core structures are `AFSBTreeEntry`, `AFSListEntry`, `AFSTreeHdr`, `AFSCommSrvcCB`, `AFSPoolEntry`, `AFSNonPagedFcb`, `AFSExtent`, `AFSFcb`, `AFSDeviceExt`, and packed `AFSProviderConnectionCB`. Callback typedefs cover request processing, logging, provider connection creation, pool allocation/free, authgroup retrieval, and trace dumps. `AFSLibraryInitCB` passes device objects, names, debug flags, global root FID, cache callbacks, cache mapping, and framework callbacks to the library.

## Control Flow
Request/result pools queue IRP work to the service. FCB/NPFCB locks serialize file, paging, section, extent, dirty-list, and CCB state. Device extensions split control, redirector, and library roles. Worker queues process async work. Provider lists support network-provider enumeration. Library init wires callbacks from framework to loaded library.

## State And Persistence
Fields track live kernel state: open/share counts, object information, dirty extents, locks, purge points, section-create file object, queued flushes, cache file mapping, volume/root-cell trees, provider lists, sysname lists, process/authgroup trees, library state, service request counts, memory pressure, and worker queues.

## Dependencies And Integration Points
Depends on Windows kernel primitives and user ABI structs such as `AFSFileID`, `AFSRequestExtentsCB`, and `AFSFileExtentCB`. Integrates redirector driver, service communication, library module, network provider, cache manager, and authgroups.

## Risks
Concurrency density is high. Lock ranking must be honored. Intrusive lists/trees need strict lifetime discipline. `AFSDeviceExt` union fields must match device role. Extent counters/events can leak or hang if updated incorrectly.

## Test Signals
Driver Verifier, checked-lock assertions, open/close stress, byte-range locks, extent request/release/dirty flush cycles, provider enumeration, library load/unload, network transitions, and memory-pressure simulations validate behavior.
