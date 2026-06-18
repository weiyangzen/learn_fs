# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/MiniRPCBenchmark.java

## Purpose
`MiniRPCBenchmark` is a standalone benchmark that measures the time to establish Hadoop RPC sessions under simple, Kerberos, or delegation-token authentication.

## Important APIs, Types, and Functions
The file defines `MiniProtocol`, a protobuf RPC interface annotated with `@KerberosInfo`, `@TokenInfo`, and `@ProtocolInfo`; `MiniServer`, a one-handler RPC server using `ProtobufRpcEngine2`; and `TestDelegationTokenSelector`. Benchmark methods include `connectToServer()`, `connectToServerAndGetDelegationToken()`, `connectToServerUsingDelegationToken()`, `runMiniBenchmark()`, `runMiniBenchmarkWithDelegationToken()`, and `configureSuperUserIPAddresses()`.

## Control Flow
`main()` parses iteration count, optional keytab, principal, token mode, and log level. Non-token mode starts `MiniServer`, warms up one connection, then repeatedly creates and stops RPC proxies while summing elapsed time. Token mode configures proxy-user groups/IPs, starts the server, obtains a delegation token as a proxy user, adds it to `currentUgi`, then times connections under that token identity.

## State and Persistence
Runtime state includes `currentUgi`, benchmark log level, RPC server instance, delegation token secret manager threads, and configuration entries. No benchmark results are persisted; they are printed to standard output.

## Dependencies and Integration Points
It integrates Hadoop RPC, Protobuf services, UGI login/keytab handling, delegation token secret manager/test identifier, impersonation provider configuration, token service binding, network interface enumeration, and Hadoop logging utilities.

## Risks and Edge Cases
Kerberos mode requires valid keytab/principal configuration. Delegation token mode depends on proxy-user IP enumeration and local host naming. `connectToServerUsingDelegationToken()` prints interrupted exceptions instead of failing hard, which can hide interruption. Average connect time includes proxy creation and server-side authentication but not application RPC payload work.

## Test Signals
Signals are successful server startup, proxy creation and shutdown across all iterations, token acquisition and token-authenticated proxy creation, printed average connection time, and absence of authentication/impersonation failures.
