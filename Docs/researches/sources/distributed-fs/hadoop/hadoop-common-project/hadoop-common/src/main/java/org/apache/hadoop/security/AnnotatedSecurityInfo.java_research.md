# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/AnnotatedSecurityInfo.java


Purpose: `AnnotatedSecurityInfo` adapts protocol-interface annotations into Hadoop `SecurityInfo` metadata.

Important APIs and types: It overrides `getKerberosInfo(Class<?>, Configuration)` and `getTokenInfo(Class<?>, Configuration)`, returning the protocol class annotations `@KerberosInfo` and `@TokenInfo`.

Control flow and state: Calls are pure lookups against runtime annotations. The `Configuration` argument is accepted to satisfy the parent contract but is not used.

Dependencies and integration: It integrates with `SecurityUtil` and RPC client/server setup that asks protocols for Kerberos principal keys and token selectors. It depends on Java runtime annotation retention.

Risks and test signals: Protocols missing annotations return null, causing later auth selection to skip Kerberos or token support. Tests should cover annotated and unannotated protocol interfaces and confirm no configuration side effects.
