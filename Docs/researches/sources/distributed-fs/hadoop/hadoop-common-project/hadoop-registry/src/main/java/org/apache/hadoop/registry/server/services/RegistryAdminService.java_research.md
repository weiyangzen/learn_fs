# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/services/RegistryAdminService.java

Purpose: `RegistryAdminService` extends the ZooKeeper-backed `RegistryOperationsService` with administrative registry setup, user home directory ACL management, asynchronous execution, and recursive purge support. It is the service-level owner of root registry paths such as `PATH_USERS` and `PATH_SYSTEM_SERVICES`.

Important APIs and types: constructors accept a service name and optional `RegistryBindingSource`; `submit()`, `createDirAsync()`, `initUserRegistryAsync()`, and `AsyncPurge` expose async operations through a cached `ExecutorService`; `createRootRegistryPaths()` initializes ZooKeeper nodes; `aclsForUser()` composes client ACLs plus secure-user ACLs; `PurgePolicy` and `NodeSelector` parameterize recursive deletion.

Control flow: service initialization adds a SASL all-permissions ACL for the current user when the registry is secure. Service start creates root paths and expands permission failures with registry diagnostics. Purge performs depth-first traversal: list children, try resolving the current record, ask the selector, handle child-bearing matches according to policy, delete if selected, then recurse into remaining children. It is defensive against concurrently removed paths by returning zero on `PathNotFoundException`.

State and persistence: persistent state lives in ZooKeeper nodes and ACLs; in-memory state is the executor. `stopExecutor()` uses `shutdownNow()` and does not wait for queued purge/create tasks. `initUserRegistry()` waits for the async task but assumes `initUserRegistryAsync()` returns a non-null future, so an already-existing home path can produce a null dereference risk.

Dependencies and integration: integrates with Curator callbacks, ZooKeeper ACL classes, Hadoop service lifecycle, registry security helpers, path utilities, and service record marshalling exceptions. Tests in this subset exercise operations indirectly through `AbstractRegistryTest`, `TestRegistryOperations`, and secure registry fixtures.

Risks and test signals: purge behavior is sensitive to selector correctness, concurrent deletion, and the chosen child policy. Secure startup depends on realm discovery and current-user SASL identity. Test coverage validates root path setup, registry CRUD, ACL/security helpers, and YARN persistence selector logic, but explicit tests for `initUserRegistry()` idempotency and async executor shutdown behavior are not visible here.
