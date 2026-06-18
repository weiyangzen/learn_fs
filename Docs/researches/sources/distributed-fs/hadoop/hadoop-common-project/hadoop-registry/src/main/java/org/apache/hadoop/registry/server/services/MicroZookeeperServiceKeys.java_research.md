# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/services/MicroZookeeperServiceKeys.java

## Purpose
`MicroZookeeperServiceKeys` defines configuration keys specific to the embedded `MicroZookeeperService`.

## Important APIs and types
The prefix is `RegistryConstants.REGISTRY_PREFIX + "zk.service."`. Keys include service JAAS context, tick time, host, port, data directory, and failed-SASL-client behavior. The default host is `localhost`.

## Control flow
There are no methods. `MicroZookeeperService` reads these constants during init and secure setup.

## State and persistence behavior
Values affect embedded ZooKeeper runtime state and data directory placement. They are not used by ordinary registry clients.

## Dependencies and integration points
The interface depends on `RegistryConstants` and is implemented by `MicroZookeeperService`.

## Risks and test signals
Misconfigured directories can be deleted by the service, and SASL keys affect JVM/server security behavior. Tests should cover defaults, custom host/port/dir, and secure server options.
