# sources/distributed-fs/eos/namespace/ns_quarkdb/views/HierarchicalView.cc

## Purpose
`HierarchicalView.cc` implements `QuarkHierarchicalView`, the QuarkDB-backed hierarchical namespace view for EOS. It maps path-oriented operations onto file/container metadata services, handles symlink traversal, creates and removes namespace entries, reconstructs paths from IDs, and integrates quota node management.

## Important APIs, Types, and Functions
The implementation defines constructor/destructor, `configure()`, three-phase `initialize()`, `finalize()`, `getItem()`, `getFileFut()`, `getFile()`, `createFile()`, `createLink()`, `unlinkFile()`, `removeFile()`, `getContainerFut()`, `getContainer()`, `createContainer()`, `removeContainer()`, URI reconstruction methods, `getRealPath()`, quota-node methods, rename methods, and `getParentContainer()`. Private helpers include `getPathInternal()`, two `getPathDeferred()` overloads, `getPathExpectContainer()`, URI-building futures, `extractFileMD()`, `extractContainerMD()`, and `UpdateStoreGuard`.

## Control Flow
Path lookup starts at `pRoot`, converts URI chunks with `PathProcessor`, and repeatedly consumes chunks in `getPathInternal()`. Container states handle `"."`, `".."`, and child `findItem()` lookups. File states in the middle of a path are either errors or symlinks; symlink targets are inserted into the pending chunk deque, absolute links reset state to root, relative links resolve from the link's parent. Cache-hit futures are consumed immediately, while cache misses return a Folly future that resumes on the executor. Creation functions resolve parent paths, check conflicts, create metadata through services, attach to parent maps, and update stores. URI reconstruction climbs parent container IDs into a deque, again suspending on metadata cache misses. Quota operations search parent chains for `QUOTA_NODE_FLAG`, register/remove quota nodes, and meld child quota data into parents on removal.

## State and Persistence Behavior
The view owns `QuarkQuotaStats` and an IO thread pool executor, stores non-owning pointers to QuarkDB client, metadata flusher, container service, and file service, and caches the root container. Metadata persistence is delegated to `updateFileStore()` and `updateContainerStore()` on the services. Some operations update one side of a relationship before the other, such as `removeContainer()` deleting metadata then removing the parent map entry. `UpdateStoreGuard` batches container store updates during recursive container creation. `finalize()` deletes quota stats and finalizes services.

## Dependencies and Integration Points
The implementation depends on EOS namespace interfaces, QuarkDB metadata services, `QuarkQuotaStats`, `PathProcessor`, Folly futures/executors, metadata exceptions, and common logging/assertion utilities. It is the central integration point for higher-level namespace APIs using QuarkDB persistence.

## Risks and Edge Cases
Important risks include symlink loop limits, relative symlink semantics, stale service caches, partially persisted create/remove/rename operations, lock ordering for `getUri(IFileMD*)`, root special cases, detached parent containers during URI/quota traversal, and exceptions in asynchronous continuations. `createContainer()` notes eventual consistency and carefully avoids creating a directory over a broken symlink. `getRealPath()` returns a path built from the resolved parent and final chunk but treats the single-chunk case differently. Rename operations update parent maps and object names but rely on callers to hold required locks.

## Test Signals
`VariousTests.cc` directly covers basic create/get behavior, symlink traversal and loops, path normalization, persistence across restart, cache invalidation, URI reconstruction, quota-node corruption handling, locking order, iterators, and missing metadata behavior.
