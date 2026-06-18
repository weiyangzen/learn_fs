## sources/distributed-fs/eos/namespace/interface/IView.hh

Purpose: Defines the hierarchical namespace view interface responsible for path lookup, creation, removal, symlink handling, URI reconstruction, quota-node operations, and service wiring.

Important APIs and types: service setters/getters, configure/initialize/finalize, async/sync `getFile` and `getContainer`, `getItem`, store updates, create/remove/unlink file, create/remove link, create/remove/rename container, parent lookup, URI and real-path resolution, quota node lookup/register/remove, quota stats setter/getter, file rename, and `inMemory`.

Control flow: callers use path-based operations through `IView`; implementations translate paths to metadata objects, handle symlink following and link depth, update services/backing stores, and maintain quota/view consistency.

State and persistence: concrete views own hierarchy relationships and coordinate persistent metadata updates through file/container services. The interface itself owns no state.

Dependencies and integration: central contract between MGM operations and namespace storage backends. Depends on file/container services, metadata interfaces, quota stats/nodes, folly futures, and `MDException`.

Risks: comments warn `getUri(IFileMD*)` must not be called with the file already locked because it can lock parent containers and deadlock. Multi-stage initialize methods (`initialize1/2/3`) imply ordering constraints. Symlink following/link-depth handling must prevent cycles.

Test signals: path lookup for files/containers/items, symlink resolution and depth limits, create/remove/unlink/rename flows, URI reconstruction without deadlock, quota-node registration/search, async future behavior, and in-memory no-op expectations in prefetcher.
