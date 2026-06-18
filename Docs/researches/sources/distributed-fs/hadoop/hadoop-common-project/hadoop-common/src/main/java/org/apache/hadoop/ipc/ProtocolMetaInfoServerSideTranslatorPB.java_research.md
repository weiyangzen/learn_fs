# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtocolMetaInfoServerSideTranslatorPB.java

## Purpose
This translator implements the `ProtocolMetaInfoPB` service by reading the server's registered protocol/version map and returning supported versions or method signatures.

## Important APIs, Types, and Functions
`getProtocolVersions` iterates all `RPC.RpcKind` values and emits version lists. `getProtocolSignature` returns method fingerprints for each version of a requested protocol/rpc kind. `getProtocolVersionForRpcKind` loads the protocol class, resolves annotated protocol name, and asks `RPC.Server.getSupportedProtocolVersions`.

## Control Flow
Requests contain class names and rpc kind strings. The translator reflects the class, converts rpc kind names through `RPC.RpcKind.valueOf`, collects versions, and builds protobuf responses. Missing registrations produce empty responses; class loading failures become `ServiceException`.

## State and Persistence Behavior
It stores only a reference to the live `RPC.Server`. No state is persisted.

## Dependencies and Integration Points
It depends on generated `ProtocolInfoProtos`, `ProtocolSignature`, `RPC.Server.VerProtocolImpl`, and shaded protobuf service exception handling. It is registered automatically by `RPC.Server`.

## Risks and Test Signals
Risks include accepting arbitrary class names for reflection, enum value errors, and stale protocol maps after dynamic registration. Tests should cover missing protocol, version lists across rpc kinds, class-not-found, and signature contents.
