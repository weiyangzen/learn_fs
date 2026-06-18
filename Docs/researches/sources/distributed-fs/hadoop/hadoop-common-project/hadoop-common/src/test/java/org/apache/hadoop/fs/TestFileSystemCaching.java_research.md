## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileSystemCaching.java

Purpose: comprehensively tests `FileSystem` cache identity, cache disablement, default-URI resolution, UGI/user cache keys, close-all behavior, delete-on-exit on close, URI user-info keying, and semaphore-limited concurrent filesystem construction.

Important APIs/types/functions: `FileSystem.get`, `FileSystem.newInstance`, `FileSystem.Cache`, `FileSystem.Cache.Key`, `FileSystem.closeAllForUGI`, `UserGroupInformation`, `FilterFileSystem`, `LocalFileSystem`, `FS_CREATION_PARALLEL_COUNT`, `BlockingThreadPoolExecutorService`, `SubjectInheritingThread`, and Mockito.

Control flow: early tests compare cached and uncached schemes and default FS URI variants. UGI tests use `doAs` to ensure same subject gives same FS and different subjects/users do not. Delete-on-exit tests mock raw filesystem status/delete behavior across close, missing files, removed files, and cancellation. Concurrent construction tests create a custom cache with one, two, or many semaphores and assert how many surplus instances are discarded while all callers receive the same cached instance.

State and persistence: uses static semaphores in inner filesystem classes, FileSystem global cache behavior, UGI subject/token state, and mocked filesystem close/delete state. Most file operations are mocked except local FS instantiation.

Dependencies/integration points: integrates with Hadoop security, cache configuration keys, URI normalization, thread pools, cache construction throttling, and FilterFileSystem delete forwarding.

Risks and test signals: concurrency tests can expose deadlocks or excessive discarded instances. Cache-key regressions can leak credentials across users or conflate URI user-info. Delete-on-exit tests protect close-time cleanup semantics and avoid deleting paths that no longer exist.
