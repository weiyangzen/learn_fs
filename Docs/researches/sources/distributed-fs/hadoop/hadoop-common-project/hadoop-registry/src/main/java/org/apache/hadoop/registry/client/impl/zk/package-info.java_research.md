# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/package-info.java

## Purpose
This package descriptor documents the registry's core ZooKeeper support package.

## Important APIs and types
It points readers to `CuratorService` for service-managed Curator access, `RegistrySecurity` for ACL and security setup, and `ZookeeperConfigOptions` for ZooKeeper system-property definitions.

## Control flow
There is no executable code. It describes the package organization and the requirement that some ZooKeeper system properties be set before object construction or operation invocation.

## State and persistence behavior
No state is stored here. The described package persists registry entries in ZooKeeper and uses JVM-wide security state.

## Dependencies and integration points
The package integrates the public registry operations with Apache Curator/ZooKeeper and Hadoop service lifecycle. It is consumed by higher-level client operations and server-side DNS/admin services.

## Risks and test signals
The package-level warning about system properties is a key test design signal: secure ZooKeeper tests must avoid sharing conflicting clients in the same JVM or must reset properties aggressively.
