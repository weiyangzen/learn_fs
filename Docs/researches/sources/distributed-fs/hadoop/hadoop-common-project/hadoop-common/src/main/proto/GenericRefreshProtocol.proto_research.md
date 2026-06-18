# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/GenericRefreshProtocol.proto

## Purpose
`GenericRefreshProtocol.proto` defines the protobuf RPC contract for Hadoop's generic refresh mechanism, where callers request a named subsystem refresh and receive handler-specific statuses.

## Important APIs, types, and functions
Messages are `GenericRefreshRequestProto` with optional `identifier` and repeated `args`, `GenericRefreshResponseProto` with optional `exitStatus`, `userMessage`, and `senderName`, and `GenericRefreshResponseCollectionProto` with repeated responses. The service `GenericRefreshProtocolService` exposes `refresh`.

## Control flow
RPC clients serialize an identifier and arguments, the server dispatches to matching refresh handlers, and the response collection returns zero or more status records. The proto itself is declarative; generated service stubs implement call dispatch.

## State and persistence
There is no persistent state in the schema. It captures one refresh request and response set. Exit status and messages are optional, so callers must handle missing fields.

## Dependencies and integration points
It generates `org.apache.hadoop.ipc.proto.GenericRefreshProtocolProtos` and integrates with Hadoop IPC, admin CLIs, and refresh handler registries.

## Risks and test signals
Risks include ambiguous identifiers, handlers returning inconsistent exit statuses, and client assumptions about a single response. Test signals include client/server translator tests, refresh commands with no handlers and multiple handlers, argument preservation, and compatibility with older clients.
