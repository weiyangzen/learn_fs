# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/DataNodeTestUtils.java

Purpose: this utility exposes package-private or operational DataNode behavior to tests while deliberately avoiding Mockito imports so downstream projects can still start MiniDFSCluster with limited dependencies.

Important APIs and types: `DataNode`, `MiniDFSCluster`, `BPOfferService`, `FsDatasetSpi`, `FsVolumeSpi`, `FsVolumeImpl`, `FsDatasetTestUtil`, `DatanodeRegistration`, `InterDatanodeProtocol`, `StorageLocation`, and `GenericTestUtils.waitFor`.

Control flow: simple helpers get a DataNode registration, toggle heartbeat/cache-report/IBR test flags, trigger deletion reports, heartbeats, and block reports across all block-pool offer services, create inter-DataNode protocol proxies with hostname-setting assertions, expose the DataNode dataset, and fetch replica info. Disk-failure helpers rename data directories to `.origin`, create files in their place, and restore the original directories later. Reconfiguration builds a comma-separated data-dir list and calls `reconfigurePropertyImpl`, swallowing `ReconfigurationException` for tests that intentionally hit failed volumes. Volume helpers locate an `FsVolumeImpl` by base URI and wait for async disk-error checks to complete.

State and persistence: several methods mutate real filesystem directories and DataNode runtime flags. `injectDataDirFailure` and `restoreDataDirFromFailure` are persistent on disk until restored, so callers must use cleanup reliably.

Dependencies and integration points: this is a shared white-box bridge for tests of DataNode heartbeats, block reports, volume failures, dynamic volume reconfiguration, and dataset internals. It integrates with production DataNode APIs but remains in test scope.

Risks: directory failure injection is destructive if restore is skipped or if `.origin` already exists. Reconfiguration intentionally hides some exceptions, which is useful for tests but can obscure unexpected failures. The "no Mockito" constraint is important and documented in the source.

Test signals: no local tests exist; downstream tests using this helper signal whether DataNode internals remain reachable and controllable for test scenarios.
