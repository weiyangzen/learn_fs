# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/CuratorService.java

## Purpose
`CuratorService` is the low-level Hadoop service wrapper around Apache Curator and ZooKeeper. It does not expose the public registry API directly; it supplies lifecycle-managed Curator access, registry-root path resolution, ZooKeeper CRUD helpers, ACL-aware creation, path watching, and diagnostics for higher-level services such as `RegistryOperationsService` and `RegistryDNSServer`.

## Important APIs and types
The class extends `CompositeService` and implements `RegistryConstants` plus `RegistryBindingSource`. Key fields are `CuratorFramework curator`, `registryRoot`, `RegistrySecurity registrySecurity`, `EnsembleProvider ensembleProvider`, and `CuratorCacheBridge curatorCacheBridge`. Lifecycle methods `serviceInit`, `serviceStart`, and `serviceStop` initialize security, build and start Curator, and close Curator/cache resources. Registry helpers include `zkStat`, `zkGetACLS`, `zkPathExists`, `zkMkPath`, `zkCreate`, `zkUpdate`, `zkSet`, `zkDelete`, `zkList`, `zkRead`, `dumpPath`, `registerPathListener`, `instantiateCacheForRegistry`, and `startCache`.

## Control flow
Initialization reads `KEY_REGISTRY_ZK_ROOT`, adds the `RegistrySecurity` child service, and defers Curator construction until start. `createCurator()` builds a binding from `RegistryBindingSource`, reads timeout/retry options, applies security under a class-level synchronized block because ZooKeeper security state is JVM-wide, then starts Curator. All ZooKeeper operations call `checkServiceLive()`, convert logical registry paths with `createFullPath()`, call Curator, and route failures through `operationFailure()`, which maps Keeper exceptions to Hadoop registry/filesystem exceptions.

## State and persistence behavior
The persistent state is ZooKeeper znodes below the configured registry root. `zkMkPath` and `zkCreate` create persistent or caller-supplied mode nodes with explicit ACLs; `zkSet` is create-or-update and treats overwrite flags at the caller boundary; `zkDelete` can delete recursively and may run in background when passed a callback. The service itself owns only transient Curator connection state and an optional cache watching the registry root.

## Dependencies and integration points
It integrates Curator, ZooKeeper `CreateMode`/`ACL`/`Stat`, Hadoop service lifecycle, `RegistrySecurity`, `RegistryPathUtils`, and registry exception classes. `RegistryOperationsService` uses the CRUD wrappers to implement the public API. `RegistryDNSServer` uses `instantiateCacheForRegistry` and `registerPathListener` to turn Curator cache events into DNS updates. `MicroZookeeperService` can provide its binding information through the same `RegistryBindingSource` abstraction.

## Risks and test signals
The create-if-absent flow is documented as check-then-create and is therefore race-prone when multiple clients create the same path; callers must tolerate `NodeExistsException` mapping. ACL lists are rejected when empty for `zkMkPath`, so tests should cover secure and insecure ACL creation. Path-listener callbacks convert `IOException` to `UncheckedIOException`, which can affect Curator listener threads. The file as read contains suspicious syntax duplication around `isSecure()` and should be covered by compilation. Behavioral tests should use an in-process ZooKeeper, verify exception translation, recursive delete, overwrite semantics, cache listener add/delete events, and SASL/digest configuration diagnostics.
