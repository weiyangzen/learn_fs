# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncRpcServer.java

Purpose: tests async helper methods on `RouterRpcServer` itself rather than on higher-level protocol modules.

Important APIs/types/functions: `RouterRpcServer`, `RemoteMethod`, `RemoteLocation`, `BlockStoragePolicy`, `DatanodeInfo`, `DatanodeStorageReport`, `HdfsConstants.DatanodeReportType`, and `syncReturn`. It inherits async RPC server setup and `/testdir` creation from `RouterAsyncProtocolTestBase`.

Control flow: `testInvokeAtAvailableNsAsync()` invokes remote `getStoragePolicies` at an available namespace and expects the standard eight storage policies. `testGetCreateLocationAsync()` gets locations for `/testdir`, invokes async create-location selection, and verifies the returned nameservice is `ns0`. `testGetDatanodeReportAsync()` fetches datanode reports, namespace-to-storage-report maps, and slow datanode reports asynchronously, comparing the slow report with the synchronous version.

State and persistence behavior: mostly read-only cluster state; create-location selection depends on resolver mappings and `/testdir`. Integration points include low-level async invocation, location selection, datanode report fan-out, and slow-datanode report handling. Risks include hard-coded expected policy/DN counts and type-erased map retrieval from `syncReturn(Map.class)`. Test signals are storage policy count, selected nameservice, datanode report sizes, map size, and array equality.
