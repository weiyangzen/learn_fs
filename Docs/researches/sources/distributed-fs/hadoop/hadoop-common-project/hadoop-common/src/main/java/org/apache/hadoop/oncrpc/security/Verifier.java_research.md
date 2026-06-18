# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/Verifier.java

Purpose: abstract base and factory for ONC RPC verifier auth blocks.

Important APIs/types/functions: constructor, `readFlavorAndVerifier`, and `writeFlavorAndVerifier`.

Control flow: factory reads flavor, maps `AUTH_NONE` to `VerifierNone`, treats `AUTH_SYS` verifier flavor as `VerifierNone` for compatibility, maps `RPCSEC_GSS` to `VerifierGSS`, then delegates body read. Writer supports `VerifierNone` and `VerifierGSS`.

State and persistence: only inherited flavor; no persistence.

Dependencies and integration: used by `RpcCall`, `RpcReply`, and security handlers.

Risks: unsupported verifier flavors throw. Mapping AUTH_SYS to VerifierNone still calls `VerifierNone.read`, expecting zero length after the AUTH_SYS flavor. Runtime-type dispatch blocks custom verifier subclasses.

Test signals: `TestRpcAuthInfo`, `TestRpcReply`, and call/reply tests cover flavor parsing and writer behavior.
