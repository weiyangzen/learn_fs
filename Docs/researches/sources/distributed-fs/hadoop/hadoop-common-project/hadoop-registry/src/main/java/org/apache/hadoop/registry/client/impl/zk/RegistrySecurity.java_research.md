# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/RegistrySecurity.java

## Purpose
`RegistrySecurity` owns registry security policy: reading auth configuration, building ZooKeeper ACLs, setting Curator auth, creating JAAS/SASL client settings, digest helpers, and diagnostics. It is intentionally a Hadoop service so tests and parent services can initialize it independently.

## Important APIs and types
The class extends `AbstractService`. It defines internal `AccessPolicy` values `anon`, `sasl`, `digest`, and `simple`; static ACLs `ALL_READWRITE_ACCESS`, `ALL_READ_ACCESS`, and `WorldReadWriteACL`; ACL collections `systemACLs` and `digestACLs`; Kerberos/JAAS fields; and many helpers. Key methods are `serviceInit`, `initSecurity`, `getClientACLs`, `createSaslACLFromCurrentUser`, `createSaslACL`, `digest`, `toDigestId`, `splitAclPairs`, `parse`, `buildACLs`, `parseACLs`, `createJAASEntry`, `applySecurityEnvironment`, `setZKSaslClientProperties`, `clearZKSaslClientProperties`, `buildSecurityDiagnostics`, and `createACLfromUsername`.

## Control flow
`serviceInit` maps `KEY_REGISTRY_CLIENT_AUTH` to an access policy and calls `initSecurity()`. In secure mode it adds world-read access, derives a Kerberos realm, builds system ACLs from configured principals, builds user ACLs, optionally adds current Kerberos user ACLs, then configures SASL or digest credentials depending on access mode. In insecure mode it grants world read/write. `applySecurityEnvironment()` mutates the Curator builder and JVM ZooKeeper properties according to the selected access policy.

## State and persistence behavior
The persistent impact is ACLs placed on ZooKeeper nodes by callers using `getClientACLs()` or `getSystemACLs()`. Digest credentials are stored in memory as auth bytes for Curator. JAAS and ZooKeeper SASL settings are process-wide JVM state, so multiple clients with different security settings can interfere.

## Dependencies and integration points
It integrates Hadoop `UserGroupInformation`, Hadoop auth `JaasConfiguration` and `KerberosUtil`, Curator builder authorization, ZooKeeper ACL/Id/digest providers, `ZKUtil` ACL parsing, and registry constants. `CuratorService` delegates all security setup to it; `MicroZookeeperService` uses static helpers for server-side SASL context validation and system properties.

## Risks and test signals
Because it sets JVM-wide JAAS/ZooKeeper properties, tests must isolate or clear system properties. Digest ACL strings are partially obfuscated for logs, which should be verified to avoid leaking secrets. Secure SASL mode requires Hadoop security to be enabled or initialization fails. The file as read contains suspicious duplicated code/text in the SASL switch and JAAS template area, so compilation is a primary test signal. Behavioral coverage should include anonymous, simple, digest, and Kerberos paths; realm suffix handling; empty user ACL failure; malformed ACL parsing; and principal/keytab supplied versus pre-existing JAAS configuration.
