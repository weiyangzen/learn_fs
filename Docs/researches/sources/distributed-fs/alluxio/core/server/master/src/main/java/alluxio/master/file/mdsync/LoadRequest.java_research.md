# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/LoadRequest.java

Purpose: represents one batch request to load UFS metadata for a path. It carries task identity, load id, batch-set id, continuation token, previous item, descendant type for this specific load, and retry policy.

Important APIs and types: getters expose task info, load path, base task id, load request id, batch set id, previous last item, continuation token, descendant type, and first-load flag. `attempt` uses `CountingRetry(2)`. `compareTo` orders requests differently for single listing, DFS, and BFS/default directory loading.

Control flow: `PathLoaderTask` creates initial and continuation requests. `LoadRequestExecutor` polls requests, performs async UFS listings, and reports errors through `onError`. The constructor increments task load-request stats.

State and persistence behavior: in-memory scheduling state only. Continuation and previous-last fields influence the persisted metadata range processed by `DefaultSyncProcess`.

Dependencies and integration points: integrates `TaskInfo`, `AlluxioURI`, `DescendantType`, `DirectoryLoadType`, retry policy, `PathLoaderTask`, and `LoadRequestExecutor`.

Risks: `equals` delegates to `compareTo` while `hashCode` uses object identity, which is inconsistent for hash collections; currently these objects are primarily queue elements. Retry count semantics must be understood: repeated load errors eventually fail the whole task.

Test signals: tests should cover BFS/DFS/single ordering, retry behavior, stat increments, continuation token propagation, and error callback routing.
