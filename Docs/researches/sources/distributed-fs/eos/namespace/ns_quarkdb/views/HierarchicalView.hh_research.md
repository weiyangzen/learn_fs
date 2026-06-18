# sources/distributed-fs/eos/namespace/ns_quarkdb/views/HierarchicalView.hh

## Purpose
`HierarchicalView.hh` declares `QuarkHierarchicalView`, the QuarkDB implementation of the EOS `IView` interface. It presents path-based file/container operations, quota-node APIs, rename APIs, and async metadata lookup surfaces.

## Important APIs, Types, and Functions
The public API overrides service setters/getters, `configure()`, `initialize()` phases, `finalize()`, `getFileFut()`, `getFile()`, `getItem()`, `createFile()`, `createLink()`, `updateFileStore()`, `removeLink()`, `unlinkFile()`, `removeFile()`, `getContainerFut()`, `getContainer()`, `createContainer()`, `updateContainerStore()`, `removeContainer()`, `getUri()` overloads, `getUriFut()` overloads, `getRealPath()`, quota node methods, `getQuotaStats()`, `setQuotaStats()`, `renameContainer()`, `renameFile()`, `inMemory()`, and `getParentContainer()`. Private APIs expose the resumable path and URI lookup machinery used by the implementation.

## Control Flow
The declaration makes clear that the view is both synchronous and asynchronous. Synchronous methods typically wrap future-returning methods and call `.get()`. Private helpers accept current lookup state and pending path chunks so asynchronous operations can resume after service futures complete.

## State and Persistence Behavior
The class stores raw pointers to `qclient::QClient`, `MetadataFlusher`, container service, file service, and quota stats, plus a shared root container and a unique executor. It reports `inMemory() == false`, signaling that operations are backed by persistent QuarkDB state. Store updates are delegated to the configured metadata services.

## Dependencies and Integration Points
The header includes the namespace base, metadata service interfaces, `IView`, and QuarkDB quota stats. It is consumed wherever the QuarkDB namespace view is constructed or manipulated through the generic `IView` interface.

## Risks and Edge Cases
Ownership is mixed: `pQuotaStats` is owned and deleted by the view, while most other pointers are non-owning. `setQuotaStats()` deletes the existing stats object but assumes ownership of the supplied pointer. The comments on `getUri(IFileMD*)` document a deadlock risk if callers lock files before calling URI reconstruction because the implementation also locks or fetches parent containers.

## Test Signals
Public behavior is exercised heavily by `VariousTests.cc`. Constructor/configuration and quota-stats ownership would benefit from additional lifecycle tests.
