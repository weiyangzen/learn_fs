# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/IngressPortBasedResolver.java


Purpose: `IngressPortBasedResolver` customizes SASL quality-of-protection properties by server ingress port, allowing one Hadoop daemon with multiple listeners to require different QOP levels per port.

Important APIs and types: It extends `SaslPropertiesResolver`, defines `ingress.port.sasl.configured.ports` and `ingress.port.sasl.prop.<port>`, and overrides `getServerProperties(InetAddress, int)`.

Control flow and state: `setConf()` first loads default SASL properties, then parses configured ports into a `HashMap<Integer, Map<String,String>>`. Missing per-port QOP defaults to privacy. At lookup, an unconfigured port logs a warning and returns default resolver properties.

Dependencies and integration: It depends on `SaslRpcServer.QualityOfProtection`, Hadoop `Configuration`, and server-side RPC code that passes ingress port to the resolver.

Risks and test signals: Tests should cover multiple ports, malformed port values, missing port-specific config defaulting to privacy, unconfigured port fallback, and immutability assumptions after `setConf()`. Misconfiguration can silently apply default QOP to a listener.
