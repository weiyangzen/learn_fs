# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/ZookeeperConfigOptions.java

## Purpose
`ZookeeperConfigOptions` lists ZooKeeper client/server system-property names and auth scheme names used by the registry security code.

## Important APIs and types
Constants cover SASL client enablement, JAAS login context, SASL client username, server SASL context, failed-SASL downgrade behavior, server realm, kinit path, and ID schemes `sasl` and `digest`. Some values are sourced from ZooKeeper classes such as `ZKClientConfig.LOGIN_CONTEXT_NAME_KEY` and `ZooKeeperSaslServer.LOGIN_CONTEXT_NAME_KEY`.

## Control flow
There are no methods. `RegistrySecurity` reads and writes these JVM properties for client-side auth. `MicroZookeeperService` uses the server-side context and failed-SASL settings when booting an embedded secure ZooKeeper.

## State and persistence behavior
The constants themselves are stateless, but they name JVM-wide system properties. Changes affect all ZooKeeper clients and servers in the same process.

## Dependencies and integration points
It depends on ZooKeeper client/server config classes and is referenced by security and embedded service code. It is package-internal API for coordinating ZooKeeper security setup.

## Risks and test signals
The class comments correctly warn that only one independently configured ZooKeeper client/service can be safe in a JVM. Tests should set and clear the named properties around each case and verify SASL enable/disable behavior does not leak across test methods.
