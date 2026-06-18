# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/MetadataFetcher.cc

## Purpose
This file implements stateless, no-cache metadata retrieval helpers for QuarkDB. It fetches file/container protobufs, parent maps, id lookups, fsview membership, full-path resolution, reverse path resolution, and directory content counts. Higher-level services and inspectors use it as the direct backend access layer.

## Important APIs, Types, and Functions
Reply validators `ensureStringReply()`, `ensureBoolReply()`, and `ensureUInt64Reply()` normalize Redis reply errors into `MDStatus`. `MapFetcher<Trait>` is a self-deleting qclient callback that HSCANs a container file map or container map in batches (`COUNT 250000`) and fulfills a `folly::Promise` with `IContainerMD::FileMap` or `ContainerMap`.

`getFileFromId()` and `getContainerFromId()` fetch protobufs and deserialize them. `doesFileMdExist()` and `doesContainerMdExist()` distinguish ENOENT from backend/deserialization errors. `getFileMap()` and `getContainerMap()` create map fetchers. `getFilesFromFilemap()` and `getContainersFromContainerMap()` sort by name before issuing metadata fetches. `getFileIDFromName()` and `getContainerIDFromName()` read parent hashes and deserialize ids. Name-based protobuf fetchers chain id lookup and id fetch. `locationExistsInFsView()` checks `SISMEMBER` in `fsview:<location>:files` or `fsview:<location>:unlinked`. `resolveFullPath()` uses `FullPathResolver`; `resolvePathToID()` uses `ReversePathResolver`; `countContents()` issues two `HLEN` calls.

## Control Flow
Most methods return futures by chaining `qcl.follyExec()` with parsing callbacks. `MapFetcher` starts an HSCAN, validates the two-element cursor/result reply, inserts filename/id pairs into a sparse-hash-style map, recursively issues the next HSCAN until cursor `0`, then sets the promise and deletes itself. Its comments correctly note that members must not be accessed after `execCB()` because the callback may already have completed and deleted the object.

`FullPathResolver` walks parent containers by repeatedly reading container protobufs and pushing names to the front of a deque until parent id 1, then emits a slash-terminated path. It short-circuits container id 1 to `/`. `ReversePathResolver` tokenizes a path, starts at container id 1, resolves each component as a container, and if resolving the final component as a container fails it tries a file lookup. It self-deletes after setting a value or exception.

## State and Persistence Behavior
The fetcher does not mutate persistent state. It reads protobuf keys, parent map hashes, fsview sets, and hash lengths. It constructs transient protobufs, maps, and futures. Its returned map contents represent persistent parent index state at scan time, not an atomic snapshot across multiple HSCAN batches or chained fetches.

## Dependencies and Integration Points
It depends on namespace interfaces, QuarkDB services, serialization, request builders, path processing, qclient async APIs, folly futures/promises, Redis reply types, and QuarkDB constants. It is used by `MetadataProviderShard` for cache misses, by `Inspector` for direct checks/repairs, and by scanner/explorer code for path and child metadata resolution.

## Risks and Test Signals
The self-deleting callback/resolver pattern is fragile: every error and success path must set exactly one promise outcome and then delete once. HSCAN does not provide an atomic view if parent maps change mid-scan. `FullPathResolver` does not guard against cycles or parent id 0 beyond eventual fetch failure, so detached/cyclic containers can hang or fail late. `ReversePathResolver` intentionally lacks symlink support. Tests should cover nil, empty, wrong-type, and malformed Redis replies; multi-batch HSCAN; deserialization errors; missing final path component as file vs container; root path resolution; detached parent errors; fsview boolean validation; and count reply validation.
