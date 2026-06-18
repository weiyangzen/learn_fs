# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncQuota.java

Purpose: tests `AsyncQuota` read and write operations against a router namespace with storage-type quota support enabled.

Important APIs/types/functions: `MiniRouterDFSCluster`, `RouterConfigBuilder.quota(true)`, `AsyncQuota`, `QuotaUsage`, `StorageType`, `DFS_QUOTA_BY_STORAGETYPE_ENABLED_KEY`, `RouterAsyncRpcClient`, `MockResolver`, `FSDataOutputStream`, and `syncReturn`. The cluster uses one HA nameservice, three DNs, rack configuration, and single async handler/responder counts.

Control flow: setup maps `/` to `ns0`, creates `/testdir`, writes a 1024-byte file, and wires a spy RPC server so `AsyncQuota` uses the async client. `testRouterAsyncGetQuotaUsage()` fetches quota usage for `/testdir` and verifies space consumed is `3 * 1024` with one directory and one file. `testRouterAsyncSetQuotaUsage()` sets a DISK type quota of 8096, waits for completion, reads quota usage back, and verifies the storage-type quota.

State and persistence behavior: quota metadata is persisted in the namenode for `/testdir`; file data and directory are removed after each test. Integration points include quota module routing, storage-type quota enablement, replication accounting, and async completion. Risks include replication-factor assumptions and quota state leakage if cleanup fails. Test signals are exact space consumption, file/directory counts, and type quota values.
