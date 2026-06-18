<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/ZookeeperClient.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/ZookeeperClient.java

## Purpose
Builds configured Curator `CuratorFramework` clients for ZooKeeper connections, including optional SASL/Kerberos ACLs and SSL/TLS client settings.

## Important APIs, types, and functions
The fluent builder methods set connection string, namespace, auth type, keytab, principal, JAAS login entry, timeouts, retry policy, ZooKeeper factory, SSL enablement, and keystore/truststore paths/passwords. `create()` validates mandatory state and builds a Curator framework. `aclProvider()` configures open ACLs for `none` auth or installs a global JAAS configuration and SASL owner ACLs for `sasl`. `zkClientConfig()` fills ZooKeeper SSL client properties. `SASLOwnerACLProvider` returns all-permission SASL ACLs for one principal short name.

## Control flow
`create()` composes Curator builder state in one pass. SASL mode requires non-empty keytab, principal, and login entry, installs JVM-wide ZooKeeper auth properties, and creates a restricted ACL provider. SSL mode requires keystore and truststore locations and sets the Netty secure client socket.

## State and persistence
Builder state is held in instance fields until `create()`. It mutates JVM-global JAAS and ZooKeeper system properties in SASL mode. No ZooKeeper data is persisted by this class directly.

## Dependencies and integration points
Used by `ZKSignerSecretProvider` and Hadoop common ZooKeeper delegation-token code. Depends on Curator, ZooKeeper client config/X509 utilities, `JaasConfiguration`, and Hadoop classification/testing annotations.

## Risks and test signals
Global JAAS/system-property changes can affect all ZooKeeper clients in the JVM. Principal ACL uses `principal.split("[/@]")[0]`, which may not match server-side SASL identities in every deployment. Passwords are passed as strings. Tests should cover auth-type validation, missing SASL inputs, SSL missing store paths, namespace/timeouts/retry propagation, ACL principal derivation, and interaction between multiple clients with different JAAS entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/ZookeeperClient.java -->
