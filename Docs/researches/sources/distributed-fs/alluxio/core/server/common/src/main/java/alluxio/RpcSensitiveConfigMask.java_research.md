## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/RpcSensitiveConfigMask.java

### Purpose
`RpcSensitiveConfigMask` masks credential-bearing mount properties in RPC messages before logging or exposing them.

### Important APIs, Types, And Functions
The singleton `CREDENTIAL_FIELD_MASKER` implements `SensitiveConfigMask.maskObjects`. It handles `MountPOptions`, `MountPRequest`, `UfsInfo`, `GetUfsInfoPResponse`, and `UpdateMountPRequest`. `copyAndMaskProperties` copies non-credential properties and replaces credential values with `"Masked"`.

### Control Flow
`maskObjects` creates a new object array, pattern-matches each argument type, clones the protobuf builder, clears properties in the relevant nested `MountPOptions`, copies masked properties from the original map, and builds the sanitized message. Unrecognized arguments pass through unchanged.

### State And Persistence
Stateless aside from the singleton. It does not mutate original protobuf messages.

### Dependencies And Integration Points
Integrates with RPC logging/masking infrastructure, protobuf-generated mount messages, `CredentialPropertyKeys`, and `SensitiveConfigMask`.

### Risks
Only known message shapes are masked. New RPC messages that directly or indirectly contain `MountPOptions` require explicit additions or credentials can leak. `copyAndMaskProperties` uses raw `Entry` types, losing generic type safety.

### Test Signals
No direct tests in this subset. Logging tests should verify each supported message type masks all keys in `CredentialPropertyKeys.getCredentials()`.
