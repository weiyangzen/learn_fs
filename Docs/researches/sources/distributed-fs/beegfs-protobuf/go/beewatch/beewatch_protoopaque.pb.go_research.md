# sources/distributed-fs/beegfs-protobuf/go/beewatch/beewatch_protoopaque.pb.go

## Purpose

This is generated Go protobuf code for `beewatch.proto` under the `protoopaque` build tag. It represents the same BeeGFS Watch event and subscriber acknowledgement schema as `beewatch.pb.go`, but with the protobuf opaque API: message fields are hidden behind `xxx_hidden_*` members, and callers must use generated accessors, mutators, presence checks, clear methods, and builders.

The file defines the wire/reflection contract for a versioned `Event` envelope, legacy `V1Event`, v8 `V2Event`, and subscriber `Response`. It is intended for builds that opt into protobuf opaque code generation while preserving the same package, descriptors, enum names, field numbers, and service metadata.

## Important APIs, Types, and Functions

- Enums:
  - `V1Event_Type`: `FLUSH`, `TRUNCATE`, `SETATTR`, `CLOSE_WRITE`, `CREATE`, `MKDIR`, `MKNOD`, `SYMLINK`, `RMDIR`, `UNLINK`, `HARDLINK`, `RENAME`, `READ`.
  - `V2Event_Type`: `INVALID`, v1-like file events, and v8-specific open/lock/stripe-pattern events.
- Messages:
  - `Event`: hidden `SeqId`, `MetaId`, optional `MetaMirror`, `EventFlags`, and oneof event data (`event_V1` or `event_V2`). Presence is tracked in `XXX_presence`.
  - `V1Event`: hidden legacy v7 event payload fields.
  - `V2Event`: hidden v8 event payload fields including link count, user ID, and timestamp.
  - `Response`: hidden `CompletedSeq` and `ShuttingDown` fields.
- Generated methods:
  - Standard protobuf `Reset`, `String`, `ProtoMessage`, and `ProtoReflect`.
  - Getter methods for every field.
  - Setter methods for every field; optional `MetaMirror` sets a presence bit.
  - `HasMetaMirror`, `ClearMetaMirror`, `HasEventData`, `HasV1`, `HasV2`, `ClearEventData`, `ClearV1`, `ClearV2`.
  - `WhichEventData` returns `Event_EventData_not_set_case`, `Event_V1_case`, or `Event_V2_case`.
  - Builder types construct opaque messages without direct field writes.
  - Descriptor globals and `file_beewatch_proto_init` build reflection metadata.

## Control Flow

The generated initialization path matches the non-opaque file:

1. `init` invokes `file_beewatch_proto_init`.
2. Oneof wrappers for `Event` are registered as private `event_V1` and `event_V2` wrapper types.
3. `protoimpl.TypeBuilder` builds a descriptor for 2 enums, 4 messages, and 1 service.
4. Raw descriptor and dependency tables are released after construction.

Message-level control flow uses accessors. `SetV1` and `SetV2` replace the oneof branch, and nil clears it. `SetMetaMirror` stores the scalar and marks presence; `ClearMetaMirror` clears the presence bit and resets the stored scalar to zero. Builders use non-atomic presence setters and assign fields in generated order; if both V1 and V2 are supplied, V2 wins.

## State and Persistence Behavior

The file itself persists nothing, but it defines the serialized state used in BeeGFS Watch streams and any stored event data. The main state signals are `SeqId`, metadata node identity (`MetaId`, optional `MetaMirror`), `EventFlags`, versioned payload, and subscriber acknowledgement (`CompletedSeq`, `ShuttingDown`).

Opaque API state has a few important characteristics:

- Optional scalar presence is separated from its value. `GetMetaMirror` returns zero for unset and set-to-zero; only `HasMetaMirror` distinguishes them.
- Event data is held as an interface oneof field and can be unset.
- Unknown fields and size cache are retained by the protobuf runtime for forward compatibility.
- Direct struct field reads/writes are intentionally unavailable to consumers.

## Dependencies and Integration Points

- Imports protobuf reflection/runtime packages and `reflect`.
- Shares the same `beewatch` Go package as `beewatch.pb.go`, but is mutually exclusive by build tags.
- Supplies `Event` and `Response` types consumed by `beewatch_grpc.pb.go`.
- The descriptor includes the `Subscriber.ReceiveEvents` bidirectional stream metadata, with `Event` as input and `Response` as output.
- The generated Go package path in the descriptor is `github.com/thinkparq/protobuf/go/beewatch`.

## Risks and Edge Cases

- Code written for exported fields in `beewatch.pb.go` will not compile in `protoopaque` builds. Accessor-based code is safer across both modes.
- `V1Event_Type` still uses `FLUSH` as the zero value, while `V2Event_Type` uses `INVALID`; consumers should not apply identical zero-value semantics.
- Optional `MetaMirror` presence must be checked explicitly.
- Builders do not reject multiple event data branches; generated assignment order determines the active branch.
- Event flags, sequence monotonicity, timestamp interpretation, path validity, and acknowledgement correctness are not validated by generated code.
- Private oneof wrapper names differ from the non-opaque file (`event_V1`/`event_V2` versus exported `Event_V1`/`Event_V2`), so code should avoid relying on wrapper concrete types where possible.

## Test Signals

- Compile with `-tags protoopaque` to ensure all consumers use accessors/builders rather than exported fields.
- Round-trip serialization tests should compare wire compatibility with the non-opaque build.
- Presence tests should cover unset, set-to-zero, and cleared `MetaMirror`.
- Oneof tests should cover V1, V2, replacement, clear, and `WhichEventData`.
- gRPC tests should confirm `beewatch_grpc.pb.go` works with these opaque message definitions under the `protoopaque` tag.
