# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/RpcAuthInfo.java

Purpose: abstract base for ONC RPC auth credential and verifier objects.

Important APIs/types/functions: `AuthFlavor` enum, `fromValue`, constructor, abstract `read`/`write`, `getFlavor`, and `toString`.

Control flow: `AuthFlavor.fromValue` scans enum constants by protocol value and throws for unknown values.

State and persistence: immutable auth flavor; no persistence.

Dependencies and integration: parent of `Credentials` and `Verifier`; used by RPC call/reply serialization.

Risks: supported enum includes flavors that not all subclasses implement. Protocol numeric values are explicit and must remain stable.

Test signals: `TestRpcAuthInfo` covers flavor value mapping and invalid flavor handling.
