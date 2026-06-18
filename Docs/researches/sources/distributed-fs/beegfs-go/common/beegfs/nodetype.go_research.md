# sources/distributed-fs/beegfs-go/common/beegfs/nodetype.go

## Purpose
`nodetype.go` defines BeeGFS node type values and conversions between strings, protobuf enums, and user-facing output.

## APIs and Control Flow
`NodeType` variants are invalid, client, meta, storage, and management. `NodeTypeFromString` trims/lowercases input and accepts non-ambiguous prefixes: client, storage, metadata/meta, and management/mgmtd with at least two characters for management. `NodeTypeFromProto` maps protobuf node types to Go values. `ToProto` returns a pointer to a protobuf enum. `String` returns user-facing lower-case names or `<invalid>`.

## State, Dependencies, and Integration
The type is an enum-style integer used by entity parsing, node models, protobuf requests, and pflag wrappers. Dependency is the BeeGFS protobuf package.

## Risks and Test Signals
The parser accepts `m` as metadata because it checks `metadata` after requiring two characters only for management. This is deliberate but creates a compact alias asymmetry. `nodetype_test.go` covers common prefixes and invalid values.
