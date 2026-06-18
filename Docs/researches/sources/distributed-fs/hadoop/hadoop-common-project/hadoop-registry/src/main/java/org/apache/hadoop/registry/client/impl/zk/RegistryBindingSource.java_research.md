# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/RegistryBindingSource.java

## Purpose
`RegistryBindingSource` abstracts where ZooKeeper connection binding information comes from. It lets clients use configuration-backed fixed quorums, embedded ZooKeeper services, or future dynamic providers.

## Important APIs and types
The single method `supplyBindingInformation()` returns `BindingInformation`, which carries an `EnsembleProvider` and textual description. `CuratorService` implements this interface by building a fixed Curator ensemble from `KEY_REGISTRY_ZK_QUORUM`, while `MicroZookeeperService` implements it after starting its local server.

## Control flow
`CuratorService.createEnsembleProvider()` invokes this method immediately before Curator construction. The returned provider becomes the source of Curator's ZooKeeper ensemble, and the description is copied into diagnostics.

## State and persistence behavior
The interface owns no state. Implementers may expose transient runtime state, such as an embedded server's chosen port, or static configuration state.

## Dependencies and integration points
It is a public evolving interface in the ZooKeeper implementation package. Its key integration point is Curator builder setup, and it allows a registry client and an embedded ZooKeeper service to be composed under one service lifecycle.

## Risks and test signals
Implementers must not return incomplete binding data. `MicroZookeeperService.supplyBindingInformation()` explicitly fails before the service has started. Tests should validate that `CuratorService` can consume both self-supplied fixed bindings and externally supplied bindings, and that diagnostics preserve the source description.
