# sources/distributed-fs/beegfs-go/common/beegfs/consistencystate.go

## Purpose
This file defines BeeGFS target consistency states and conversions among user strings, protobuf enums, and Go string output.

## APIs and Control Flow
`ConsistencyState` has variants `ConsistencyStateUnspecified`, `Good`, `NeedsResync`, and `Bad`. `ConsistencyStateFromString` trims/lowercases input and recognizes `good`, `needs_resync`, and `bad`. `ConsistencyStateFromProto` maps protobuf values to Go constants. `ToProto` returns a pointer to the corresponding protobuf enum. `String` returns user-friendly lower-case names or `<unspecified>`.

## State, Dependencies, and Integration
The type is immutable enum-style state. It depends on `github.com/thinkparq/protobuf/go/beegfs` and is used by parsers and command/UI layers that display or submit target consistency state.

## Risks and Test Signals
The parser does not accept hyphenated or spaced variants such as `needs-resync`. Unknown protobuf values collapse to unspecified, which is safe but lossy. No direct test file is listed, though the parser wrapper may be tested elsewhere.
