<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-protobuf/cpp/beegfs.pb.h -->
# sources/distributed-fs/beegfs-protobuf/cpp/beegfs.pb.h

## Purpose
This is generated C++ Protocol Buffers code for `proto/beegfs.proto`, produced by protoc 29.2 / Protobuf C++ 5.29.2. It exposes the core BeeGFS identity and classification schema in namespace `beegfs`: common enum domains plus `LegacyId` and `EntityIdSet` message classes. Other generated C++ files, especially management RPC messages, include this header to identify nodes, targets, buddy groups, pools, quota subjects, and network/storage state values in a shared wire-compatible form.

## Important APIs, Types, And Functions
- File-level protobuf metadata: `TableStruct_beegfs_2eproto`, `descriptor_table_beegfs_2eproto`, default-instance externs for `LegacyId` and `EntityIdSet`, and enum descriptor helpers. These are protobuf runtime integration points, not application-owned APIs.
- Enums: `EntityType` (`NODE`, `TARGET`, `BUDDY_GROUP`, `POOL`), `NodeType` (`CLIENT`, `META`, `STORAGE`, `MANAGEMENT`), `ReachabilityState` (`ONLINE`, `POFFLINE`, `OFFLINE`), `ConsistencyState` (`GOOD`, `NEEDS_RESYNC`, `BAD`), `CapacityPool` (`NORMAL`, `LOW`, `EMERGENCY`), `NicType` (`ETHERNET`, `RDMA`), `QuotaIdType` (`QUOTA_ID_TYPE_USER`, `QUOTA_ID_TYPE_GROUP`), and `QuotaType` (`QUOTA_TYPE_SPACE`, `QUOTA_TYPE_INODE`). Each enum has `*_IsValid`, `*_descriptor`, `*_Name`, `*_Parse`, min/max constants, and `google::protobuf::is_proto_enum`/`GetEnumDescriptor` specializations.
- `LegacyId final : google::protobuf::Message` models BeeGFS' legacy numeric identifier pair. Its public field API is `num_id()` / `set_num_id()` / `clear_num_id()` for field 1 and `node_type()` / `set_node_type()` / `clear_node_type()` for field 2. The generated class also exposes standard protobuf lifecycle and reflection APIs: `default_instance`, `descriptor`, `GetReflection`, `New`, `CopyFrom`, `MergeFrom`, `Clear`, `ByteSizeLong`, `_InternalSerialize`, `Swap`, and arena-aware constructors.
- `EntityIdSet final : google::protobuf::Message` groups all identifiers that can refer to an entity. It has explicit-presence optional fields: `uid` field 1 with `has_uid`, `set_uid`, `clear_uid`; `alias` field 2 with `has_alias`, `set_alias`, `mutable_alias`, `release_alias`, `set_allocated_alias`; and `legacy_id` field 3 with `has_legacy_id`, `mutable_legacy_id`, `release_legacy_id`, `set_allocated_legacy_id`, and unsafe arena variants.
- Internal layout matters for generated code compatibility: `EntityIdSet::Impl_` stores a protobuf `HasBits<1>` bitmap, `ArenaStringPtr alias_`, `LegacyId* legacy_id_`, `int64_t uid_`, and cached size. `LegacyId::Impl_` stores `uint32_t num_id_`, an integer-backed `node_type_`, and cached size.

## Control Flow
This header is mostly inline accessors and declarations; parse, serialize, size, merge, and descriptor assignment implementations live in `cpp/beegfs.pb.cc`. Application control flow generally constructs a message, sets identifier fields through the generated accessors, and hands the object to protobuf serialization, gRPC stubs, or another generated message.

For `LegacyId`, scalar setters write directly to `_impl_`; zero is the protobuf default and is also documented by the source proto as invalid application data for `num_id`. For `EntityIdSet`, setters also update the `_has_bits_` bitmap so callers can distinguish "unset" from "set to default value" for proto3 optional fields. `mutable_legacy_id()` lazily allocates the nested `LegacyId` on the owning arena and marks presence. `release_*` and `set_allocated_*` transfer ownership according to protobuf's heap/arena rules, while unsafe arena variants assume matching arena lifetime.

Enum name and parse helpers route through protobuf reflection descriptors. `*_IsValid` only checks whether an integer falls in the generated enum range; it does not validate BeeGFS domain rules such as whether a given `NodeType` is meaningful for a specific `EntityType`.

## State And Persistence
Message state is in-memory protobuf object state plus unknown-field metadata. Serialized bytes are the persistence and RPC compatibility contract: field numbers 1-3 for `EntityIdSet`, 1-2 for `LegacyId`, and the numeric enum values must remain stable. `EntityIdSet` uses explicit presence for all three fields, so serialized messages can preserve whether `uid`, `alias`, or `legacy_id` was intentionally provided even if a value equals the type default.

The source proto documents additional semantic constraints that this generated header does not enforce: `LegacyId.num_id` and `EntityIdSet.uid` treat `0` as invalid, aliases must start with a letter and contain only `[a-zA-Z0-9_-.]`, request messages should usually set one identifier, and response messages should generally fill all known identifiers. Persistence users must enforce those constraints outside this class.

## Dependencies And Integration Points
- Depends on the Protobuf C++ runtime headers and generated-message internals from version 5.29.2; the header has a compile-time `PROTOBUF_VERSION != 5029002` guard.
- Must be compiled and linked with `cpp/beegfs.pb.cc`, where descriptors, parse tables, default instances, class data, constructors, serialization, byte-size, merge, and descriptor initialization are defined.
- Generated from `proto/beegfs.proto` by the repository `Makefile` target `protos`, which also generates Go and Rust outputs. `make test-protos` regenerates artifacts and fails if generated files differ from the checked-in state.
- Used by generated service/domain headers such as `cpp/management.pb.h`, where `EntityIdSet` appears throughout node, target, buddy group, storage pool, quota, and resync request/response messages.
- Cross-language integration is intentional: matching Go and Rust generated files expose the same enum numbers and message fields, so C++ clients must not reinterpret the wire schema independently.

## Risks And Edge Cases
- This is checked-in generated code. Manual edits will be overwritten by regeneration and can desynchronize from `proto/beegfs.proto`, `cpp/beegfs.pb.cc`, Go output, and Rust output.
- The Protobuf C++ version guard is strict. Building against a different protobuf runtime/header version fails at compile time, and generated internals such as `TcParseTable`, `ClassDataFull`, and arena string handling are not stable application APIs.
- Proto3 enum fields are open in generated C++: `LegacyId::set_node_type` accepts a `NodeType`, but unknown integer enum values can still arrive from the wire and should not be treated as fully validated BeeGFS state without `NodeType_IsValid` and domain checks.
- Presence and default values are easy to confuse. `EntityIdSet::has_uid()` can be true while `uid() == 0`, and `has_alias()` can be true with an empty string; both may violate schema comments even though protobuf accepts them.
- Ownership-sensitive APIs (`release_alias`, `set_allocated_alias`, `release_legacy_id`, `set_allocated_legacy_id`, `unsafe_arena_*`) can leak, double-delete, or dangle if callers mix heap and arena ownership incorrectly.
- `LegacyId` is not globally unique by itself; the source schema says the entity type must also be known. Code using only `LegacyId` as a map key or persistent identifier risks collisions across entity types.

## Test Signals
- `make test-protos` in `sources/distributed-fs/beegfs-protobuf` is the primary freshness signal: it runs generation and checks that `cpp/beegfs.pb.h` and sibling generated outputs match the committed `.proto` sources.
- The GitHub Actions `checks` workflow runs `make clean && make test-protos` in a Rust container after installing pinned protoc, Go, gRPC, and `protoc-rs` tool versions.
- Compile/link tests for C++ consumers should include both `beegfs.pb.h` and `beegfs.pb.cc` with protobuf 5.29.2 headers/runtime, because this header intentionally relies on generated definitions in the companion `.cc`.
- Behavioral tests should round-trip `LegacyId` and `EntityIdSet` through binary serialization, verify `has_*` behavior for optional fields set to default values, parse/name all enum values, and assert application-level validation rejects invalid IDs, aliases, and ambiguous identifier combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-protobuf/cpp/beegfs.pb.h -->
