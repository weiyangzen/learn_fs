<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-protobuf/cpp/beewatch.pb.cc -->
# sources/distributed-fs/beegfs-protobuf/cpp/beewatch.pb.cc

## Purpose
Implements the generated C++ Protocol Buffers runtime for `beewatch.proto`, produced by protoc 29.2 / Protobuf C++ 5.29.2. It supplies descriptors, default instances, parse tables, constructors/destructors, serialization, byte-size calculation, merge/copy, swap, and metadata wiring for the BeeGFS Watch messages `Event`, `V1Event`, `V2Event`, and `Response` in namespace `beewatch`.

## Important APIs, Types, And Functions
- Generated default instances: `_Event_default_instance_`, `_V1Event_default_instance_`, `_V2Event_default_instance_`, and `_Response_default_instance_`.
- File descriptor machinery: `descriptor_table_beewatch_2eproto`, `descriptor_table_protodef_beewatch_2eproto`, `TableStruct_beewatch_2eproto::offsets`, generated `MigrationSchema` rows, `file_default_instances`, and static `AddDescriptors` initialization.
- Enum helpers: `V1Event_Type_descriptor`, `V1Event_Type_IsValid`, `V2Event_Type_descriptor`, and `V2Event_Type_IsValid`. Both validation helpers only check whether the integer is within the known generated range.
- Message implementations: each class defines arena constructors, copy constructors, `SharedCtor`, `SharedDtor`, `Clear`, `_InternalSerialize`, `ByteSizeLong`, `MergeImpl`, `CopyFrom`, `InternalSwap`, `GetClassData`, and `GetMetadata`.
- `Event` additionally implements the oneof-specific ownership paths `set_allocated_v1`, `set_allocated_v2`, and `clear_event_data`.

## Control Flow
Static initialization registers the descriptor table through `AddDescriptors`. Descriptor lookup lazily calls `AssignDescriptors` before returning enum descriptors. Message construction initializes scalar storage to zero/defaults, initializes arena-aware strings, and leaves `Event.event_data` unset.

Parse behavior is table-driven through `TcParseTable` instances. `Event` has fast varint entries for `seq_id`, `meta_id`, `meta_mirror`, and `event_flags`, with oneof message entries for fields 11 and 12. `V1Event` and `V2Event` use fast UTF-8 string parsers for paths and entry IDs. `Response` parses `completed_seq` and `shutting_down` as varints.

Serialization writes only non-default scalar/string values, writes `Event.meta_mirror` when its explicit presence bit is set, writes exactly the active `Event` oneof member, verifies UTF-8 before serializing string fields, and appends unknown fields when present. Merge copies non-default scalars and non-empty strings, preserves unknown fields, and for `Event` either merges into the same active oneof case or clears/replaces the previous case when the source oneof differs.

## State And Persistence
Runtime state is protobuf object memory plus unknown-field metadata. The embedded descriptor preserves the wire contract from `beewatch.proto`: `Event` fields 1-4 plus oneof fields 11/12, `V1Event` fields 1-8, `V2Event` fields 1-9, and `Response` fields 1-2. `Event.meta_mirror` uses a has-bit, so it can serialize an explicit zero; most other proto3 scalars and strings have no explicit presence and are omitted when default.

`Event.event_data` is a pointer union with `_oneof_case_[0]`; clearing deletes heap-owned submessages or optionally poisons arena-owned messages in debug-hardening mode. `V1Event` and `V2Event` own five `ArenaStringPtr` fields each. `Response` stores only `completed_seq` and `shutting_down`. Persistence compatibility depends on stable field numbers and enum numeric values, not on generated C++ layout.

## Dependencies And Integration Points
- Depends on the companion generated header `beewatch.pb.h`.
- Uses Protobuf C++ runtime internals including `TcParser`, `TcParseTable`, `ClassDataFull`, `WireFormatLite`, `WireFormat`, `ArenaStringPtr`, descriptor assignment, reflection, unknown fields, and arena allocation.
- The embedded descriptor declares the `Subscriber.ReceiveEvents` bidirectional streaming RPC with `stream Event` input and `stream Response` output. Service stubs live in other generated files, but this descriptor is the schema source for reflection.
- Integrates with cross-language generated outputs under the same `beegfs-protobuf` tree and with `make protos` / `make test-protos`, which regenerate and check generated artifacts for drift.

## Risks And Edge Cases
- This is checked-in generated code and should not be manually edited; regeneration from `proto/beewatch.proto` will overwrite hand changes.
- It is tightly coupled to Protobuf C++ 5.29.2 and generated runtime internals, so building with mismatched protobuf headers/runtime can fail or violate generated-code assumptions.
- Enum fields are treated as open protobuf enums in the table entries; `*_IsValid` only confirms known numeric ranges and does not validate BeeGFS semantic combinations.
- Merge semantics skip default values for most fields, so merging a message cannot clear a destination scalar/string by supplying a default value; callers needing replacement must use `CopyFrom` or `Clear` first.
- Ownership-sensitive oneof APIs can leak or dangle if heap and arena lifetimes are mixed incorrectly.
- UTF-8 verification is performed for path and ID strings, which can surface serialization failures or debug checks if callers treat these fields as arbitrary bytes.

## Test Signals
- `make test-protos` in `sources/distributed-fs/beegfs-protobuf` is the strongest freshness signal because it regenerates protobuf outputs and fails if generated files differ from checked-in sources.
- C++ build tests should compile and link `beewatch.pb.cc` with `beewatch.pb.h` against Protobuf 5.29.2.
- Behavioral tests should round-trip `Event` carrying both `v1` and `v2`, verify oneof replacement/clearing, verify `meta_mirror` presence when set to zero, verify unknown fields survive parse/serialize/merge, exercise enum name/parse helpers, and validate that `Response.completed_seq` and `shutting_down` serialize only when non-default.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-protobuf/cpp/beewatch.pb.cc -->
