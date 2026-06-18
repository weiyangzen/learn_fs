# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/Credentials.java

Purpose: abstract base and factory for ONC RPC credential auth blocks.

Important APIs/types/functions: `readFlavorAndCredentials`, `writeFlavorAndCredentials`, constructor, `mCredentialsLength`, and test-only `getCredentialLength`.

Control flow: factory reads an auth flavor integer and instantiates `CredentialsNone`, `CredentialsSys`, or `CredentialsGSS`, then delegates body parsing. Writer emits the flavor matching the runtime type and delegates body writing.

State and persistence: subclass instances track credential-body length; no persistence.

Dependencies and integration: used by `RpcCall` for request header parsing/writing and by security handlers.

Risks: unsupported flavors throw. Runtime-type dispatch means custom credential subclasses are not serializable without modifying this base. Error message for unrecognized credential says verifier.

Test signals: `TestCredentialsSys`, `TestRpcAuthInfo`, and `TestRpcCall` cover auth flavor parsing and writing.
