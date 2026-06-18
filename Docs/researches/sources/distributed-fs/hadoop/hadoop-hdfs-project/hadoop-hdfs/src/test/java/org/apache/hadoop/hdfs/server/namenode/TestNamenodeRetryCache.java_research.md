# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNamenodeRetryCache.java

Purpose: Verifies NameNode retry cache correctness for non-idempotent RPCs by manually controlling RPC call ids and client ids, and verifies retry cache rebuild from edit logs after restart.

Important APIs and types: `DummyCall` extends `Server.Call` to install controlled call metadata via `Server.getCurCall`. Tests call `NamenodeProtocols` methods: `concat`, `delete`, `createSymlink`, `create`, `append`, deprecated `rename`, `rename2`, `updatePipeline`, snapshot methods, and `FSNamesystem.initRetryCache`. `testRetryCacheRebuild` inspects `LightWeightCache<CacheEntry, CacheEntry>`.

Control flow: Setup enables retry cache and starts a cluster with enough DataNodes for the default erasure coding policy. `newCall` increments a shared call id to represent a new RPC; reusing the same call id simulates retries. Each operation first succeeds, then repeated same-call invocations must replay the cached result, while a new call id should fail or return false because the namespace already changed. HA update pipeline verifies a retry after standby failure does not hang. Rebuild test runs a standard operation set, snapshots cache entries, restarts NameNode, and verifies the same 39 entries are rebuilt.

State and persistence behavior: Retry cache entries are persisted in edit log records for reconstructable operations and rebuilt on NameNode restart. Namespace mutations from create/delete/rename/snapshot operations are intentionally used to distinguish retry replay from fresh duplicate requests.

Dependencies and integration points: Integrates IPC server call context, NameNode RPC implementation, retry cache serialization, edit log replay, snapshots, append/create semantics, HA standby exceptions, ACL config, and erasure coding policy sizing.

Risks: The hard-coded expected cache size of 39 is sensitive to `DFSTestUtil.runOperations`. Static call id/client state must be reset carefully. Directly setting thread-local server calls is test-only and can leak if future code uses async execution.

Test signals: Passing means repeated same-call RPCs replay success, new-call duplicates fail naturally, standby retry does not deadlock, disabling retry cache returns null, and restart rebuilds all expected cache entries.
