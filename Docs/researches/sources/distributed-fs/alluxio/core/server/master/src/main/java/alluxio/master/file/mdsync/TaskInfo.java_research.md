# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/TaskInfo.java

Purpose: immutable descriptor for one metadata sync task, plus mutable task stats and a synchronized set of directories whose direct-children-loaded flag should be updated.

Important APIs and types: fields include UFS base path, Alluxio path, optional startAfter, descendant type, task id, directory load type, sync interval, metadata sync handler, and `TaskStats`. Getters expose these fields, `hasDirLoadTasks` identifies recursive BFS/DFS style tasks, and `addPathToUpdateDirectChildrenLoaded` records directories in a trie.

Control flow: `TaskTracker.launchTaskAsync` creates `TaskInfo` for each new task. `PathLoaderTask`, `DefaultSyncProcess`, `BaseTask`, and report generation repeatedly consult it for path mapping, policy, stats, callbacks, and direct-children-loaded updates.

State and persistence behavior: task info is in-memory. Recorded directories are later journaled as direct-children-loaded updates by `BaseTask.updateDirectChildrenLoaded`.

Dependencies and integration points: depends on `AlluxioURI`, `DescendantType`, `DirectoryLoadType`, `TrieNode`, `TaskStats`, and `MetadataSyncHandler`. It is the common context object across mdsync.

Risks: `startAfter` is package-private and may be null. Direct-children-loaded trie access is synchronized, but returned stream consumers must not assume concurrent modification immunity beyond the synchronized method's creation of the stream.

Test signals: tests should cover descriptor fields, `hasDirLoadTasks`, direct-children-loaded insertion and streaming, and `toString` usefulness for task reports.
