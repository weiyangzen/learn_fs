# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/client/impl/TestMicroZookeeperService.java

Purpose: smoke test for the embedded `MicroZookeeperService` default temporary directory support.

Important APIs and functions: `testTempDirSupport()` creates, initializes, starts, and stops a `MicroZookeeperService` using a `RegistryConfiguration`; `destroyZKServer()` stops the service after each test.

Control flow: service lifecycle is exercised without explicit ZooKeeper path operations.

State and persistence: any storage is managed internally by `MicroZookeeperService` default configuration. The field is stopped through `ServiceOperations.stop()`.

Dependencies and integration: integrates registry configuration, Hadoop service operations, and JUnit timeout.

Risks and test signals: this is a basic lifecycle signal only. It does not validate connection strings, directory cleanup, port binding, or client connectivity.
