# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/FileMDSvc.hh

## Purpose
This header declares the QuarkDB implementation of `IFileMDSvc`. It is the service facade used by EOS namespace code to access file metadata while hiding QuarkDB persistence and cache-provider details.

## Important APIs, Types, and Functions
`QuarkFileMDSvc` overrides lifecycle, asynchronous and blocking file retrieval, existence checks, cache dropping, creation, update, deletion, counting, listener notification, container-service wiring, quota stats wiring, visitor hook, id retrieval, cache stats, id blacklist, and provider access. `sFlushInterval` is declared as the backend flush interval. Private `SafetyCheck()` verifies recorded max file id consistency at startup.

Private state includes listener list, quota stats pointer, container service pointer, metadata flusher pointer, qclient pointer, metainfo hash, atomic file count, owning `MetadataProvider`, and `UnifiedInodeProvider`.

## Control Flow
Clients must set the container service before configuration creates the provider and before initialization. After setup, interface calls use the metadata provider for cached reads and the flusher/request builder for persistence.

## State and Persistence Behavior
The class is the service-level owner of file metadata cache/provider state and unified inode allocation state. It does not store file metadata itself except through provider caches; durable state remains in QuarkDB.

## Dependencies and Integration Points
It includes `IFileMDSvc`, inode providers, qclient hash structures, and forward declarations for quota, flusher, and metadata provider. It integrates with `QuarkContainerMDSvc`, metadata listeners, and namespace accounting/quota views.

## Risks and Test Signals
Raw non-owning pointers make lifecycle tests important. `visit()` is a no-op, so callers expecting visitor traversal need separate coverage. Tests should verify that `getMetadataProvider()` is null before configuration and valid after configuration, and that all interface methods fail predictably when called too early.
