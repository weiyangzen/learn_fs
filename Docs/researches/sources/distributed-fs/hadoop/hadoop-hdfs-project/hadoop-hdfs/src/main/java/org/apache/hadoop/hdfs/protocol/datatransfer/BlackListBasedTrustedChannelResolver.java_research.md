# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/BlackListBasedTrustedChannelResolver.java

Purpose: Implements a trusted-channel resolver that trusts peers unless their IP address appears in configured fixed or variable blacklists. It can apply separate server-side and client-side blacklist settings.

Important APIs and configuration: Extends `TrustedChannelResolver`. Config keys define fixed blacklist file paths, variable blacklist enable flags, variable file paths, and cache refresh seconds for server and client. Defaults point to `/etc/hadoop/fixedBlackList` and `/etc/hadoop/blackList`. `setConf()` builds `CombinedIPList` instances. `isTrusted()` checks the local host against the client blacklist. `isTrusted(InetAddress)` checks a peer address against the server blacklist.

Control flow: `setConf()` loads server fixed/variable settings first, then uses the server fixed/variable defaults as client fallbacks unless client keys override them. Variable lists are enabled only when the corresponding boolean is true; cache seconds are converted to milliseconds. Trust checks invert membership in the blacklist.

State and persistence behavior: Holds two in-memory `CombinedIPList` objects that may reload variable files according to cache expiry. Trust policy is persisted externally in configured list files and Hadoop configuration.

Dependencies and integration points: Depends on `TrustedChannelResolver`, `CombinedIPList`, `Configuration`, and `InetAddress`. Used by data-transfer SASL code to skip handshakes for trusted channels when configured.

Risks: `UnknownHostException` in client-side local-host lookup returns trusted, which is permissive. Missing or stale blacklist files can unintentionally trust peers. Client fallback behavior may reuse server file paths if client keys are absent. Trusting blacklisted logic directly affects whether SASL/encryption wrapping is skipped.

Test signals: Tests should cover fixed and variable blacklist membership, server/client separate config, cache refresh, disabled variable lists, unknown local host behavior, default paths, and integration with SASL trusted-channel bypass.
