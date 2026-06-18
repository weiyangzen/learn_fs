# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/WhitelistBasedTrustedChannelResolver.java

Purpose: Implements a trusted-channel resolver that trusts only IP addresses present in configured fixed or variable whitelists. It supports separate server-side peer trust and client-side local trust settings.

Important APIs and configuration: Extends `TrustedChannelResolver`. Config keys define fixed whitelist file paths, variable whitelist enable flags, variable whitelist paths, and cache seconds for server and client. Defaults point to `/etc/hadoop/fixedwhitelist` and `/etc/hadoop/whitelist`. `setConf()` creates `CombinedIPWhiteList` instances. `isTrusted()` checks the local host against the client whitelist. `isTrusted(InetAddress)` checks a peer address against the server whitelist.

Control flow: `setConf()` reads server list configuration, then client list configuration using server values as fallbacks. Variable lists are optional and cache intervals are stored in milliseconds. Trust checks return membership in the whitelist.

State and persistence behavior: Holds server and client `CombinedIPWhiteList` objects that may refresh variable files after cache expiry. Policy persists in Hadoop configuration and external whitelist files.

Dependencies and integration points: Depends on `TrustedChannelResolver`, `CombinedIPWhiteList`, `Configuration`, and `InetAddress`. Used by data-transfer SASL/encryption logic to decide trusted-channel bypass.

Risks: `UnknownHostException` in client local-host lookup returns false, which is fail-closed. Missing whitelist files can force SASL/encryption on all channels. Client fallback paths can unintentionally mirror server whitelist config. Because trust bypasses negotiation, whitelist contents are security-sensitive.

Test signals: Tests should cover fixed/variable whitelist membership, server/client config separation, cache refresh, unknown local host fail-closed behavior, default paths, absent files, and integration with SASL trusted-channel bypass.
