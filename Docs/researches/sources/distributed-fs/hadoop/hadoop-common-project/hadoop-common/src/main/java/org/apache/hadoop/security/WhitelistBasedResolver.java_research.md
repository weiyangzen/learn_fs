# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/WhitelistBasedResolver.java

Purpose: `SaslPropertiesResolver` implementation that applies different RPC SASL QOP properties depending on whether a client IP is in a configured whitelist.

Important APIs/types/functions: configuration keys define fixed whitelist file, variable whitelist enable/file/cache, and non-whitelist RPC protection. `setConf` builds a `CombinedIPWhiteList` and precomputes non-whitelist SASL properties. `getServerProperties(InetAddress)` and `getServerProperties(String)` choose default properties for whitelisted clients and restricted properties for others. `getSaslProperties` defaults non-whitelisted clients to privacy.

Control flow: when configured, fixed file is always used; variable file/cache are used only when enabled. At request time, null client addresses get non-whitelist properties, otherwise the IP string is checked against the combined whitelist.

State/persistence: in-memory `CombinedIPWhiteList` and SASL property map. Whitelist files are read by the helper; this class does not write them.

Dependencies/integration: Hadoop RPC SASL resolver configuration, `CombinedIPWhiteList`, `SaslRpcServer.QualityOfProtection`, and `SaslPropertiesResolver`.

Risks: null client addresses take stricter non-whitelist path; bad whitelist file paths may silently reduce whitelist coverage depending on helper behavior; variable whitelist refresh cadence controls runtime policy changes; IP string matching must account for IPv4/IPv6 formats. Test signals include fixed-only, variable-enabled, cache expiry, null address, unknown host string path, and QOP parsing defaults.
