# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/underfs/AbstractUfsManager.java

## Purpose
`AbstractUfsManager` is a shared base implementation of `UfsManager`. It caches `UnderFileSystem` instances by scheme, authority, and mount-specific properties, tracks mount-id to client mappings, and lazily initializes root and journal UFS clients.

## Important APIs, Types, and Functions
Important pieces include nested `Key`, `getOrAddWithRecorder()`, abstract `connectUfs(UnderFileSystem)`, `addMount()`, `addMountWithRecorder()`, `removeMount()`, `get(long)`, `getRoot()`, `getJournal(URI)`, `close()`, and `hasMount(long)`. It uses `UfsClient`, `UnderFileSystemConfiguration`, `ManagedBlockingUfsForwarder`, `Recorder`, `IdUtils`, `Closer`, and Alluxio configuration keys for root and UFS managed-blocking behavior.

## Control Flow, State, and Persistence
Mount registration stores a lazy `UfsClient` supplier that calls `getOrAddWithRecorder()`. On cache miss, UFS creation is synchronized, creates an `UnderFileSystem`, optionally wraps object stores or configured UFSes with `ManagedBlockingUfsForwarder`, registers the UFS with `Closer`, calls subclass-specific `connectUfs()`, probes availability with `exists(path)`, and stores the instance in the cache. `getRoot()` lazily creates the root mount from global configuration; `getJournal()` lazily creates the journal mount using `UfsJournal.getJournalUfsConf()`.

## Dependencies and Integration Points
It depends on Alluxio URI/configuration, UFS factories, mount ids, recorder diagnostics, and subclasses that decide master versus worker connection calls. It is used by master and worker components needing mount-backed UFS access.

## Risks and Test Signals
Risks include no reference counting for cached UFS instances, cache keys ignoring path and depending on property-map equality, runtime wrapping of initial connection failures, object-store managed-blocking behavior, and lazy singleton root/journal clients not updating after config changes. Signals are cache reuse by scheme/authority/properties, mount-not-found errors, root/journal lazy initialization, close closing all registered UFSes, and recorder output for cache hits/misses.
