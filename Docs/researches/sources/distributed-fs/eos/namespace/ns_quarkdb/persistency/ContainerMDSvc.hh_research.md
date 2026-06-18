# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/ContainerMDSvc.hh

## Purpose
This header declares the QuarkDB implementation of the EOS container metadata service. It adapts `IContainerMDSvc` to QuarkDB persistence, cache-backed retrieval, inode allocation, quota integration, and listener notification.

## Important APIs, Types, and Functions
`QuarkContainerMDSvc` overrides lifecycle, retrieval, creation, update, deletion, counting, listener, lost+found, cache-stat, and id-blacklist methods. It exposes setters for file metadata service, metadata provider, inode provider, and quota stats. `getContainerMDFut()` is the asynchronous API; `getContainerMD()` is the blocking interface-compatible wrapper. `createInParent()` and `getLostFoundContainer()` are higher-level convenience methods.

Private state includes listener list, quota stats pointer, file service pointer, qclient pointer, flusher pointer, metadata hash, provider pointer, unified inode provider pointer, atomic container count, and delayed cache-size string. `SafetyCheck()` and `notifyListeners()` are private implementation hooks.

## Control Flow
Callers must wire `setFileMDService()`, `setMetadataProvider()`, and `setInodeProvider()` before `initialize()`. The file metadata service is responsible for creating and sharing the metadata provider and inode provider. After initialization, normal interface calls use the provider and flusher.

## State and Persistence Behavior
The class represents persistent container metadata but stores only service-local counters and pointers. QuarkDB persistence is performed by implementation methods using request builders and flusher. Cache capacity configuration can be received before the provider pointer exists and applied later from `mCacheNum`.

## Dependencies and Integration Points
It includes container interfaces, QuarkDB constants, quota stats, metadata flusher, inode providers, and qclient hash structures. It is a friend of `QuarkContainerMD`, allowing metadata objects to call service internals as needed.

## Risks and Test Signals
The class relies on non-owning raw pointers, so initialization order and lifetime are critical. Tests should verify failures when dependencies are missing, delayed cache configuration, listener notification ordering, and that service methods do not dereference unset provider/inode pointers.
