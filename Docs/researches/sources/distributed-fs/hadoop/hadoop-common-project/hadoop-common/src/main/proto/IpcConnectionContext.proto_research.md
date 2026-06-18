# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/IpcConnectionContext.proto

## Purpose
`IpcConnectionContext.proto` defines metadata sent when a Hadoop IPC connection is established. It communicates user identity and target protocol before individual RPC calls are processed.

## Important APIs, types, and functions
`UserInformationProto` has optional `effectiveUser` and `realUser`. `IpcConnectionContextProto` has optional `userInfo` and optional `protocol`; field 1 is reserved by omission from older context usage.

## Control flow
During IPC setup, clients serialize the connection context after authentication/handshake framing. Servers use the user information for UGI/proxy-user context and the protocol field to bind the connection to a target RPC protocol.

## State and persistence
The context is per connection. It is not persisted independently, but it influences all calls multiplexed over that connection.

## Dependencies and integration points
It generates `org.apache.hadoop.ipc.protobuf.IpcConnectionContextProtos` and integrates with Hadoop IPC client/server connection setup, security, and proxy-user handling.

## Risks and test signals
Risks include missing user fields under simple/authenticated modes, proxy-user confusion between effective and real user, protocol mismatches, and compatibility around omitted/unknown fields. Test signals include secure and insecure IPC connection tests, proxy user tests, mixed-version context parsing, and protocol mismatch failures.
