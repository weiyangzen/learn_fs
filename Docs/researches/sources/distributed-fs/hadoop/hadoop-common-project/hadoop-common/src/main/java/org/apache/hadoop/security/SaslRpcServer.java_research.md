# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SaslRpcServer.java

Purpose: server-side SASL wiring for Hadoop RPC. It maps RPC authentication methods to SASL mechanisms, creates `SaslServer` instances for token and Kerberos flows, and provides callback handlers for DIGEST/TOKEN and GSSAPI negotiation.

Important APIs/types/functions: `QualityOfProtection` exposes SASL QOP strings. `AuthMethod` serializes RPC auth method bytes and maps simple, kerberos, token/digest, and plain to mechanism names. The constructor derives mechanism/protocol/serverId; Kerberos extracts service and host from the current user's principal. `create(Connection, Map, SecretManager)` chooses the callback handler and creates the SASL server, running as current UGI for Kerberos. `encodeIdentifier`, `decodeIdentifier`, `getIdentifier`, and `encodePassword` adapt token identifiers/passwords for SASL.

Control flow: callers initialize static factory via `init`, instantiate per-auth-method server metadata, then call `create`. Token SASL uses `SaslDigestCallbackHandler`: decode token identifier, set `connection.attemptingUser`, retrieve password from `SecretManager.retriableRetrievePassword`, authorize only matching auth/authz IDs, and optionally delegate unknown callbacks to configured `CustomizedCallbackHandler`. Kerberos uses `SaslGssCallbackHandler` and similarly requires auth ID equality.

State/persistence: static `saslFactory`; instance fields hold selected auth method and derived Kerberos protocol/host. No persistence, but token password lookup and connection attempting user mutate RPC authentication state.

Dependencies/integration: `Server.Connection`, `SecretManager`, `TokenIdentifier`, `UserGroupInformation`, `FastSaslServerFactory`, `SaslPlainServer`, and Hadoop security config. Risks: Kerberos principals without host fail late; authorization is strict equality; callback extension must not leak passwords. Test signals include mechanism selection, auth byte serialization, token identifier decoding errors, custom callbacks, and Kerberos host validation.
