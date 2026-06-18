# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/AbstractZKRegistryTest.java

Purpose: base fixture for tests requiring a transient ZooKeeper server. It owns class-level startup and teardown of `MicroZookeeperService` and produces registry client configurations bound to that instance.

Important APIs and functions: static `createZKServer()` creates `target/zookeeper`, initializes `MicroZookeeperService`, and registers it with an `AddingCompositeService`; `teardownServices()` closes all registered services; `getConnectString()` and `createRegistryConfiguration()` provide client connection settings.

Control flow: static composite service starts before `@BeforeAll` runs, then receives ZooKeeper and any other test services. Each test renames the current thread to `JUnit`, which helps diagnostics. Registry retry and timeout settings are kept low for tests.

State and persistence: ZooKeeper data is stored under `target/zookeeper` and deleted before the server starts. Service state is class-static, so subclasses share one server per test class.

Dependencies and integration: uses Hadoop `Configuration`, registry constants, `RegistryConfiguration`, and the service lifecycle. `AbstractRegistryTest` and `TestCuratorService` depend on it.

Risks and test signals: class-level sharing can hide cross-test leakage if a subclass fails to reset data; however, root deletion in `AbstractRegistryTest` reduces that risk for operation tests. Timeout of 10 seconds catches ZooKeeper startup or client hang regressions.
