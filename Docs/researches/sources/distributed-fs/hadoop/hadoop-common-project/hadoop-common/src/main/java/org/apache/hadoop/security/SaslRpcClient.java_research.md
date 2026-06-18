# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SaslRpcClient.java


Purpose: `SaslRpcClient` performs client-side Hadoop IPC SASL negotiation, selects a compatible authentication method, validates Kerberos principals or token credentials, and wraps RPC streams when negotiated QOP requires it.

Important APIs and types: Construction takes `UserGroupInformation`, protocol class, server address, and configuration. Public APIs include `saslConnect(IpcStreams)`, `getInputStream()`, `getOutputStream()`, `dispose()`, `getAuthMethod()`, and test-visible principal/property helpers. It uses protobuf RPC headers, `RpcSaslProto`, `AuthMethod`, `TokenInfo`, `KerberosInfo`, `SaslPropertiesResolver`, and a static `FastSaslClientFactory`.

Control flow: `saslConnect()` starts with a NEGOTIATE request, then loops over SASL RPC responses. On `NEGOTIATE`, `selectSaslClient()` chooses the first valid server-advertised auth method that the client supports and has credentials for; SIMPLE switches without a SASL client, TOKEN creates a DIGEST client using a selected delegation token, and KERBEROS verifies the real auth method and validates the server principal from protocol annotation/config or pattern. CHALLENGE responses are evaluated with the SASL client; SUCCESS verifies client completion. RPC ERROR/FATAL responses become `RemoteException`; non-SASL responses or malformed packets become `SaslException`.

State and persistence: State is per connection: UGI, protocol, server address, configuration, resolver, selected auth method, and `SaslClient`. There is no persistence. `dispose()` clears SASL resources. `getInputStream()` and `getOutputStream()` wrap streams only when negotiated QOP is not `auth`; wrapped RPC output sends `SaslState.WRAP` messages, and wrapped input rejects non-wrapped responses.

Dependencies and integration: It integrates deeply with Hadoop IPC framing, UGI tokens, `SecurityUtil`, Kerberos principal annotations, token selectors, `RpcWritable`, and SASL providers. It exposes attempted auth method so higher-level clients can decide whether Kerberos relogin may help after connection failure.

Risks and test signals: Tests should cover auth selection ordering, invalid advertised methods, missing tokens, token selector instantiation failures, Kerberos principal pattern and exact-match validation, bad Kerberos config mapped to non-retryable SASL errors, unsolicited challenges, premature server success, malformed packets, SIMPLE fallback, stream wrapping, and non-wrapped response rejection. Security risks include accepting SIMPLE when server offers it and configuration permits it, and relying on exact principal validation correctness.
