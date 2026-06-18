# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/DirectoryPathWaiter.java

Purpose: `BaseTask` implementation for recursive directory syncs loaded by directory, where progress is tracked by completed directory roots rather than lexicographic item intervals.

Important APIs and types: maintains a `TrieNode<AlluxioURI>` of completed directories. `waitForSync` blocks until the requested path or its parent is covered by a completed trie entry or until task completion. `nextCompleted` inserts the base load path for non-truncated results.

Control flow: as each directory load finishes without truncation, `nextCompleted` records that directory and notifies waiters. Waiters use `getClosestTerminal` so a completed ancestor can satisfy descendants according to the path/parent check.

State and persistence behavior: in-memory progress coordination only. It does not mutate file-system metadata; mutation happens in `DefaultSyncProcess`.

Dependencies and integration points: depends on `BaseTask`, `TrieNode`, `SyncProcessResult`, `AlluxioURI`, and UFS client supplier construction. It is selected for recursive non-single-listing directory load tasks.

Risks: truncated directory results are not marked complete until a later non-truncated result, so bugs in truncation handling can block waiters. The parent-or-exact check must match traversal semantics for when a listed child is safe to expose.

Test signals: tests should cover completed exact path, completed parent, truncated batches, interruption, and final task success/failure behavior.
