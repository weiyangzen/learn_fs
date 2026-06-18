# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/KerberosInfo.java


Purpose: `KerberosInfo` is a runtime-retained protocol annotation that tells Hadoop RPC security which configuration keys contain Kerberos principals.

Important APIs and types: It targets types, has `serverPrincipal()` as a required element and `clientPrincipal()` defaulting to the empty string. It is limited-private and evolving.

Control flow and state: There is no runtime logic in the annotation itself. Consumers such as `AnnotatedSecurityInfo` and `SecurityUtil` read it reflectively.

Dependencies and integration: It integrates with protocol interfaces used by Hadoop IPC. `SaslRpcClient` uses the server principal key to validate the server-advertised Kerberos identity.

Risks and test signals: Tests should cover annotation discovery and missing/empty principal keys. Protocols with incorrect keys can fail SASL negotiation or accept the wrong principal pattern.
