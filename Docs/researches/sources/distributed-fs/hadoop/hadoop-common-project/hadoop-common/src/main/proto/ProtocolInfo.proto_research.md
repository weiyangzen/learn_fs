# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/ProtocolInfo.proto

## Purpose
`ProtocolInfo.proto` defines Hadoop's RPC meta-protocol for querying protocol versions and method signatures. It lets clients determine server capabilities across RPC kinds.

## Important APIs, types, and functions
Messages include `GetProtocolVersionsRequestProto`, `ProtocolVersionProto`, `GetProtocolVersionsResponseProto`, `GetProtocolSignatureRequestProto`, `GetProtocolSignatureResponseProto`, and `ProtocolSignatureProto`. The service `ProtocolInfoService` exposes `getProtocolVersions` and `getProtocolSignature`.

## Control flow
Clients ask for versions supported by a protocol or for method signature hashes for a specific protocol/rpc-kind pair. Servers return repeated version records or per-version method hash lists. This can be invoked as a meta-protocol over an existing RPC connection.

## State and persistence
The schema represents server capability metadata at request time. Version lists and method hashes are not persisted by the proto, though implementations may cache reflection results.

## Dependencies and integration points
It generates `org.apache.hadoop.ipc.protobuf.ProtocolInfoProtos` and integrates with `ProtocolMetaInfoPB`, RPC compatibility negotiation, and protocol translator support checks.

## Risks and test signals
Risks include stale method hash calculations, wrong `rpcKind` strings, incomplete version lists, and incompatibility if required fields change. Test signals include `isMethodSupported` tests, mixed-version protocol negotiation, meta-protocol calls over regular service connections, and reflection/signature regression tests.
