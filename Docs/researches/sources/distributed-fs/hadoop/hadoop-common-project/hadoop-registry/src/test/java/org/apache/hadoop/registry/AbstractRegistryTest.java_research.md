# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/AbstractRegistryTest.java

Purpose: common base fixture for ZooKeeper-backed registry operation tests. It creates a fresh `RegistryAdminService`, resets the registry tree, recreates root paths, and exposes helper assertions and record bind helpers.

Important APIs and functions: `setupRegistry()` initializes and starts the admin service with `createRegistryConfiguration()` from `AbstractZKRegistryTest`; `putExampleServiceEntry()` builds and binds a sample `ServiceRecord`; `assertPathExists()`, `assertPathNotFound()`, and `assertResolves()` wrap registry calls in test-friendly assertions.

Control flow: each test starts with an initialized in-memory ZooKeeper from the superclass. The fixture deletes `/` recursively, then calls `createRootRegistryPaths()` to isolate tests. Binding helpers ensure the parent path exists before calling `operations.bind()`.

State and persistence: persists test data in the shared `MicroZookeeperService` instance, then cleans through service teardown registration. The `registry` and `operations` fields share the same object.

Dependencies and integration: integrates registry admin services, `RegistryOperations`, path utilities, persistence policies, and JUnit lifecycle annotations.

Risks and test signals: deleting `/` and recreating root paths is a broad reset, so tests depend on `RegistryAdminService` being robust after full tree deletion. This fixture is a strong signal for normal registry CRUD behavior but not for multi-client or secure ACL behavior.
