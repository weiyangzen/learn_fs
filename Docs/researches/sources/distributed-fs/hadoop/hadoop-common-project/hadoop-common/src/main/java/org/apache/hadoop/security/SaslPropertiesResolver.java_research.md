# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SaslPropertiesResolver.java


Purpose: `SaslPropertiesResolver` supplies SASL property maps for Hadoop RPC client and server connections, defaulting to QOP values from configuration.

Important APIs and types: It implements `Configurable`, has static `getInstance(Configuration)` for configurable subclass selection, `setConf()`, `getDefaultProperties()`, server/client property lookup overloads, and static `getSaslProperties()` for subclasses.

Control flow and state: `setConf()` reads `hadoop.rpc.protection`, maps configured `QualityOfProtection` names to SASL QOP strings, joins them, and sets `Sasl.SERVER_AUTH` to true. Default client and server lookup methods return the same stored property map; port-aware overloads delegate to address-only methods.

Dependencies and integration: It depends on Hadoop configuration keys, `SaslRpcServer.QualityOfProtection`, Java SASL constants, and `ReflectionUtils`. `SaslRpcClient`, RPC servers, and `IngressPortBasedResolver` use it.

Risks and test signals: Tests should cover QOP list mapping, invalid QOP names, custom resolver instantiation, and returned map contents. The stored map is mutable if exposed directly, so callers could accidentally alter resolver state.
