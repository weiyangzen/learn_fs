## sources/distributed-fs/eos/namespace/Prefetcher.cc

Purpose: Implements asynchronous metadata prefetching to populate namespace caches before callers perform synchronous metadata operations, reducing QuarkDB/cache latency in path, inode, directory, and filesystem-list workflows.

Important APIs and functions: staging methods add file, container, item, and URI futures; `wait` blocks on staged futures. Static convenience methods prefetch by path/id/inode, with parents, with children, filesystem file lists, unlinked lists, and parent URIs.

Control flow: all methods return immediately for in-memory views. Stage methods request futures from `IView`, `IFileMDSvc`, or `IContainerMDSvc`; parent prefetch chains metadata futures into URI futures. Child prefetch fetches the container, checks a ten-minute `lastPrefetch` throttle, iterates subcontainers/files with optional limits, stages each child, waits, and updates `lastPrefetch`.

State and persistence: `Prefetcher` owns vectors of futures only for its lifetime. Persistent metadata is not changed except for the in-memory `IContainerMD::lastPrefetch` timestamp used to throttle child prefetches.

Dependencies and integration: integrates `IView`, `IFsView`, file/container services, `ContainerMapIterator`, `FileMapIterator`, `FileId` inode helpers, folly futures, and EOS logging. MGM callers use it before locking or xattr operations.

Risks: staged item futures in `mItems` are never waited in `wait`, so `stageItem` may not provide the same synchronization guarantee as file/container/URI staging. Exceptions during path staging are logged as benign races. Child prefetch can be expensive without limits, and limit defaults use `uint64_t(-1)`.

Test signals: verify in-memory no-op behavior, future waiting for files/containers/URIs, item prefetch synchronization expectation, child prefetch throttling, limit handling, inode file/container detection, unlinked filesystem list prefetch, and race handling on deleted paths.
