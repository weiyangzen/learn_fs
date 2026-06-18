# sources/distributed-fs/beegfs-go/common/beegfs/entity.go

## Purpose
This file defines common BeeGFS entity identity types: legacy node-type plus numeric ID, globally unique UID, alias, invalid ID, and full `EntityIdSet` values.

## APIs and Control Flow
`EntityId` requires `fmt.Stringer` and `ToProto`. `IdFromString` trims and parses unsigned decimal IDs with a caller-provided bit size and minimum one. `LegacyId` formats short and long node-type IDs and converts to protobuf. `Uid` and `Alias` format and convert to protobuf. `AliasFromString` enforces aliases beginning with a letter and containing letters, digits, dash, underscore, or dot. `EntityIdSetFromProto` converts a protobuf set into Go fields, and `EntityIdSet.ToProto` converts back.

## State, Dependencies, and Integration
These are value types used across CLI parsing, node stores, and protobuf APIs. Dependencies include regex, string/number parsing, and BeeGFS protobuf entity types.

## Risks and Test Signals
`EntityIdSetFromProto` only checks nil input or nil `LegacyId`, but dereferences `input.Uid` and `input.Alias`, so partial protobufs can panic. `LegacyId.ToProto` casts `NumId` to `uint32` without range enforcement at conversion time. Tests cover ID parsing ranges and entity parser outputs, not full `EntityIdSetFromProto` nil-field behavior.
