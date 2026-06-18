<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/auth_info.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/auth_info.h

## Purpose
Defines lightweight authentication metadata passed through libhdfspp connection and RPC layers. It records whether a connection uses simple auth, Kerberos/SASL, token auth, or failure/unknown states and optionally stores a delegation token.

## Important APIs, Types, And Functions
`Token` stores `identifier` and `password`. `AuthInfo` exposes `AuthMethod`, `useSASL()`, `getUser`/`setUser`, `getMethod`/`setMethod`, `getToken`, `setToken`, and `clearToken`. The default method is `kSimple`.

## Control Flow
Callers construct `AuthInfo`, set a user/method/token while negotiating connection options, and then use `useSASL()` to choose simple protocol flow versus SASL-capable authentication.

## State And Persistence
State is per-object and in-memory. Token data is stored as strings in an `std::experimental::optional`; there is no secure wiping or persistence.

## Dependencies And Integration Points
It depends on the local optional wrapper and integrates with RPC/DataTransfer authentication setup, including DIGEST-MD5 and token-based flows.

## Risks
Token strings remain in normal heap memory. `useSASL()` treats all non-simple methods, including unknown/failure markers, as SASL candidates, so callers must validate method transitions explicitly.

## Test Signals
Unit tests should cover default simple auth, token set/clear, user propagation, and method decisions used by RPC and DataNode authentication code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/auth_info.h -->
