# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/services/MicroZookeeperService.java

## Purpose
`MicroZookeeperService` runs a small embedded localhost ZooKeeper server under Hadoop service lifecycle and supplies registry binding information to clients.

## Important APIs and types
The class extends `AbstractService` and implements `RegistryBindingSource`, `RegistryConstants`, `ZookeeperConfigOptions`, and `MicroZookeeperServiceKeys`. Key methods are `serviceInit`, `setupSecurity`, `serviceStart`, `serviceStop`, `supplyBindingInformation`, `getConnectionString`, `getConnectionAddress`, and `getRandomAvailablePort`.

## Control flow
Initialization reads port, tick time, host, and data directory settings, creates instance/data/conf directories, and deletes explicit configured directories first. Start calls `setupSecurity()`, creates `FileTxnSnapLog` and `ZooKeeperServer`, configures and starts `ServerCnxnFactory`, builds `BindingInformation` with a fixed ensemble provider, records diagnostics, and writes the chosen quorum back into configuration. Stop shuts down the factory and deletes the data directory.

## State and persistence behavior
ZooKeeper transaction/snapshot data lives under the service data directory while running and is deleted on stop. Binding information is valid only after start. JVM system properties may be changed for secure embedded server setup.

## Dependencies and integration points
It integrates embedded ZooKeeper server classes, Curator `FixedEnsembleProvider`, Hadoop `FileUtil`, `RegistrySecurity` static helpers, registry constants, and `RegistryBindingSource`. It is suited for tests and local composite services that need a ZooKeeper-backed registry.

## Risks and test signals
Random-port selection has a bind race between closing the probe socket and ZooKeeper binding. Explicit instance directories are deleted during init. Secure setup mutates JVM-wide SASL properties and validates an existing JAAS context. Tests should cover start-before-binding failure, random and fixed ports, config quorum injection, secure/insecure startup, cleanup on stop, and diagnostics.
