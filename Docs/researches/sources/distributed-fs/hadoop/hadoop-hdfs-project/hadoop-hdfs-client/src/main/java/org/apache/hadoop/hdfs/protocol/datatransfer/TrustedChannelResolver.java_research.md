# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/TrustedChannelResolver.java

## Purpose
`TrustedChannelResolver` determines whether a data transfer channel should be considered trusted enough to skip SASL/encryption negotiation. The default implementation trusts nothing.

## Important APIs, Types, and Functions
`getInstance(Configuration)` reads `DFS_TRUSTEDCHANNEL_RESOLVER_CLASS`, defaulting to `TrustedChannelResolver`, and instantiates it through `ReflectionUtils`. It implements `Configurable` with `setConf`/`getConf`. `isTrusted()` checks local trust and `isTrusted(InetAddress)` checks remote peer trust; both return false by default.

## Control Flow
`SaslDataTransferClient` calls both local and remote trust checks. If either side is not trusted, it performs SASL/encryption negotiation; only when both are trusted can it skip the handshake.

## State and Persistence Behavior
The resolver stores a `Configuration` reference. Custom subclasses may add their own state, but this base class has no persistence.

## Dependencies and Integration Points
It depends on Hadoop configuration/reflection utilities and Java `InetAddress`. It integrates directly with data transfer SASL client setup and any site-specific trusted network policy.

## Risks and Edge Cases
Custom implementations are security-sensitive: returning true too broadly bypasses SASL/encryption. `getInstance` trusts configuration class loading. Default false is conservative.

## Test Signals
`TestSaslDataTransfer` includes trust-check tests for local and remote trust behavior. Custom resolver tests should verify both local and peer address checks.
