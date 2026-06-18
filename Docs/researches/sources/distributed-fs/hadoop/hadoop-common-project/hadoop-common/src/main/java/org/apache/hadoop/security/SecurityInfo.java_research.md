# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SecurityInfo.java

Purpose: a small ServiceLoader extension point used by RPC security code to discover protocol-specific Kerberos and token metadata.

Important APIs/types/functions: abstract `getKerberosInfo(Class<?> protocol, Configuration conf)` returns a `KerberosInfo` annotation or equivalent provider result for a protocol; `getTokenInfo(Class<?> protocol, Configuration conf)` returns `TokenInfo`. Both are public to limited private Hadoop subsystems and evolving.

Control flow: this file defines no concrete behavior. `SecurityUtil.getKerberosInfo` and `SecurityUtil.getTokenInfo` iterate test providers first, then ServiceLoader providers implementing this class, returning the first non-null match.

State/persistence: no fields, no persistence, no caching in this abstraction. State is owned by provider implementations and `SecurityUtil`'s provider arrays/loaders.

Dependencies/integration: used by RPC clients/servers, protocol implementations, and service-provider metadata. It depends only on `Configuration`, `KerberosInfo`, and `TokenInfo`.

Risks: provider ordering controls which metadata wins; a provider returning broad non-null results can shadow later providers. Null returns are part of normal lookup semantics, so tests should cover missing metadata and multiple provider priority.

Test signals: mock `SecurityInfo` providers installed through `SecurityUtil.setSecurityInfoProviders`, protocol classes with/without token and Kerberos metadata, and null-return fallthrough.
