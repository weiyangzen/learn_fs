# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/RegistryInternalConstants.java

## Purpose
`RegistryInternalConstants` centralizes implementation-only constants for registry path validation and ZooKeeper ACL/security wiring.

## Important APIs and types
The constants include `VALID_PATH_ENTRY_PATTERN`, permission masks for readers, system services, and user roots, `SASLAUTHENTICATION_PROVIDER`, `ZOOKEEPER_AUTH_PROVIDER`, and `HADOOP_USER_NAME`. Permission masks are defined using `ZooDefs.Perms`.

## Control flow
There are no functions. Consumers import these values when validating registry path components or configuring ZooKeeper server SASL support. `MicroZookeeperService.setupSecurity()` uses the auth-provider constants to install SASL ACL support into the embedded server.

## State and persistence behavior
No runtime state is stored. The constants affect persistent ZooKeeper ACLs when used to create nodes and affect JVM/server security properties when configuring SASL.

## Dependencies and integration points
The interface depends on ZooKeeper `ZooDefs`. It is internal to the `impl.zk` package and complements the public `RegistryConstants`.

## Risks and test signals
The path-entry regex allows unlimited segment length and lowercase alphanumeric/hyphen names only; tests should verify this matches registry path rules wherever enforced. ACL permission constants should be tested indirectly through secure registry node creation, especially user root permissions that intentionally omit ACL administration.
