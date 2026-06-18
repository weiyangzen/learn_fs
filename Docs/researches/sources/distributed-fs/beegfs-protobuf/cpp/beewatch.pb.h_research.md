<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-protobuf/cpp/beewatch.pb.h -->
# sources/distributed-fs/beegfs-protobuf/cpp/beewatch.pb.h

## Purpose
Declares the generated C++ Protocol Buffers API for BeeGFS Watch events from `beewatch.proto`, using Protobuf C++ 5.29.2. It exposes message classes and enums in namespace `beewatch` so C++ producers/consumers can construct, inspect, serialize, parse, reflect on, and stream Watch events and acknowledgements in the same wire format used by the Go and Rust generated outputs.

## Important APIs, Types, And Functions
- File-level integration points: `TableStruct_beewatch_2eproto`, `descriptor_table_beewatch_2eproto`, and default-instance externs for `Event`, `V1Event`, `V2Event`, and `Response`.
- `V1Event_Type` models the BeeGFS v7 legacy event set: `FLUSH`, `TRUNCATE`, `SETATTR`, `CLOSE_WRITE`, `CREATE`, `MKDIR`, `MKNOD`, `SYMLINK`, `RMDIR`, `UNLINK`, `HARDLINK`, `RENAME`, and `READ`.
- `V2Event_Type` models the BeeGFS v8 event set: `INVALID`, the common filesystem mutation events, plus `OPEN_READ`, `OPEN_WRITE`, `OPEN_READ_WRITE`, `LAST_WRITER_CLOSED`, `OPEN_BLOCKED`, `STRIPE_PATTERN_CHANGED`, and `INODE_LOCKED`.
- Both enums provide generated `*_IsValid`, `*_descriptor`, `*_Name`, and `*_Parse` helpers.
- `V1Event` fields: `type`, `dropped_seq`, `missed_seq`, `path`, `entry_id`, `parent_entry_id`, `target_path`, and `target_parent_id`.
- `V2Event` fields: `type`, `num_links`, `path`, `entry_id`, `parent_entry_id`, `target_path`, `target_parent_id`, `msg_user_id`, and `timestamp`.
- `Event` fields: common metadata `seq_id`, `meta_id`, optional `meta_mirror`, `event_flags`, and a `oneof event_data` containing either `v1` field 11 or `v2` field 12.
- `Response` fields: subscriber acknowledgement `completed_seq` and shutdown signal `shutting_down`.

## Control Flow
Application code usually includes this header, creates a message, populates fields through generated accessors, and hands the object to protobuf serialization, parsing, reflection, or gRPC layers. Inline scalar setters write directly to `_impl_` with ThreadSanitizer instrumentation. String setters use `ArenaStringPtr::Set`, `Mutable`, `Release`, and `SetAllocated` with arena-aware ownership.

`Event.mutable_v1()` and `Event.mutable_v2()` lazily clear any previous oneof member, mark the selected case, and allocate the submessage on the owning arena. `release_v1()` and `release_v2()` detach the active oneof member, duplicating from an arena when needed. Unsafe arena variants skip ownership migration and assume caller-managed arena compatibility. `has_meta_mirror()` checks the generated has-bit, while `event_data_case()`, `has_v1()`, and `has_v2()` check the oneof case discriminator.

## State And Persistence
The classes hold in-memory protobuf state and cached serialized sizes; durable state is the binary protobuf encoding defined by field numbers and enum numeric values. `Event::Impl_` stores `HasBits<1>` for `meta_mirror` presence, scalars for `seq_id`, `meta_id`, `meta_mirror`, and `event_flags`, a union of `V1Event*`/`V2Event*`, and oneof case storage. `V1Event::Impl_` stores five arena-aware strings plus `dropped_seq`, `missed_seq`, and integer-backed `type`. `V2Event::Impl_` stores five arena-aware strings plus `num_links`, integer-backed `type`, `msg_user_id`, and `timestamp`. `Response::Impl_` stores `completed_seq` and `shutting_down`.

Except for `meta_mirror` and the oneof, fields follow proto3 default semantics: absent and default values read the same through accessors. `meta_mirror` is explicitly optional, so callers can distinguish absent mirror information from an explicitly set zero value. `Event.event_data` can be unset, `v1`, or `v2`; callers must inspect the case before using version-specific payload fields.

## Dependencies And Integration Points
- Depends on Protobuf C++ runtime headers and has a strict `PROTOBUF_VERSION != 5029002` compile-time guard.
- Must be compiled with `cpp/beewatch.pb.cc`, which defines descriptors, class data, default instances, parse tables, and non-inline methods.
- Generated from `sources/distributed-fs/beegfs-protobuf/proto/beewatch.proto`, whose comments define `Event` as the stable Watch envelope for minor additive changes and describe `V1Event` as BeeGFS v7 legacy format and `V2Event` as BeeGFS v8 format.
- The descriptor includes a `Subscriber.ReceiveEvents(stream Event) returns (stream Response)` service, so these messages are the payload contract for Watch subscribers acknowledging processed sequence IDs and graceful shutdown requests.
- Integrates with sibling Go and Rust generated outputs that share the same field numbers, enum values, and service schema.

## Risks And Edge Cases
- The file is generated and should be treated as a build artifact checked in for consumers; manual edits risk divergence from the proto source and sibling Go/Rust/C++ generated files.
- Public-looking internals such as `_impl_`, `_table_`, `ClassDataFull`, `TcParseTable`, and default-instance structs are protobuf implementation details, not stable application extension points.
- Because `V1Event.Type` starts at `FLUSH = 0`, a default-constructed v1 event has a valid-looking event type even when the application may not have intentionally set it. `V2Event` avoids that by using `INVALID = 0`.
- `Event` can carry neither version or exactly one version, so callers must check `event_data_case()` before reading version-specific fields.
- `event_flags` is only a raw bitmask; constants live outside this generated file.
- Ownership APIs for strings and oneof submessages require normal protobuf arena discipline to avoid leaks, dangling pointers, or copies that callers did not expect.

## Test Signals
- `make test-protos` under `sources/distributed-fs/beegfs-protobuf` is the primary generated-code drift check.
- Compile tests should include this header with Protobuf C++ 5.29.2 and link the companion `.cc`.
- Unit tests should cover default construction, setting/clearing every scalar and string field, `has_meta_mirror()` for explicit zero and nonzero values, `event_data_case()` transitions between `v1`, `v2`, and unset, `release_*`/`set_allocated_*` ownership behavior when relevant, enum `Name`/`Parse`/`IsValid`, and binary round-trips that preserve sequence IDs, mirror presence, event flags, versioned payloads, and response acknowledgements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-protobuf/cpp/beewatch.pb.h -->
