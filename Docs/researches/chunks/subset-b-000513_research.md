# sources/distributed-fs/beegfs-protobuf/cpp/flex.pb.cc lines 6020-11998

## Scope

This chunk covers generated C++ protobuf runtime code for the middle of `flex.pb.cc`. It starts inside the generated implementation for `flex.WorkRequest` and runs through the beginning of the generated implementation for `flex.RemoteStorageTarget`, ending in that message's parse-table declaration.

The range contains complete generated implementations for:

- `WorkRequest`
- `BuilderJob`
- `MockJob`
- `SyncJob_MetadataEntry_DoNotUse`
- `SyncJob`
- `Work_Status`
- `Work_Part`
- `Work`
- `UpdateConfigRequest`
- `UpdateConfigResponse`
- `BeeRemoteNode`
- `RemoteStorageTarget_Policies`
- `RemoteStorageTarget_S3_StorageClass_Archival`
- `RemoteStorageTarget_S3_StorageClass`
- `RemoteStorageTarget_S3`
- `RemoteStorageTarget_Azure`
- `RemoteStorageTarget_POSIX`

The range also includes the ownership helpers, constructors, destructor, copy constructor, and `clear_type()` start for `RemoteStorageTarget`, plus the start of its `TcParseTable`. The remaining `RemoteStorageTarget` serialization, byte-size, merge, swap, metadata, and other generated methods continue after this chunk.

This file is generated from `proto/flex.proto`; the application semantics come from the `.proto` contract, while this chunk implements C++ object lifetime, parsing tables, wire serialization, merging, swapping, and protobuf reflection metadata.

## Purpose

The purpose of this chunk is to provide C++ protobuf bindings for BeeGFS Flex worker-node and remote-storage configuration messages. These messages are used by Flex services to exchange work requests, work status/results, worker configuration, BeeRemote connection details, and remote storage target definitions.

At a higher level, this chunk covers three related API areas:

- Work submission and execution state: `WorkRequest`, `BuilderJob`, `MockJob`, `SyncJob`, `Work`, `Work_Status`, and `Work_Part`.
- Worker configuration RPC payloads: `UpdateConfigRequest`, `UpdateConfigResponse`, and `BeeRemoteNode`.
- Remote storage target configuration: `RemoteStorageTarget_Policies`, S3 storage classes and archival restore options, S3 endpoint credentials, Azure-over-S3 configuration, POSIX targets, and the beginning of the aggregate `RemoteStorageTarget` oneof wrapper.

There is no handwritten business logic here. The important behavior is generated protobuf behavior: field presence tracking, arena-aware allocation, oneof replacement, UTF-8 verification for string fields, deterministic map serialization for `SyncJob.metadata`, unknown-field preservation, and merge semantics for proto3 scalar/message/repeated fields.

## Important APIs, Types, And Fields

`WorkRequest` is the main message BeeRemote sends to a worker node. It carries `job_id`, `request_id`, `external_id`, `path`, optional `segment`, `remote_storage_target`, `stub_local`, optional `priority`, and a `oneof Type` containing exactly one of `MockJob`, `SyncJob`, or `BuilderJob`. The generated code manages the `Type_` oneof manually: `clear_Type()` deletes or poisons the active submessage depending on arena ownership, resets `_oneof_case_[0]`, and `MergeImpl()` replaces or merges the active branch depending on whether the source and destination oneof cases match.

`BuilderJob` contains optional `JobRequestCfg cfg`, `submitted`, and `errors`. The generated class tracks `cfg` in `_has_bits_[0]` and serializes only non-default counters. It represents job-builder progress rather than a data transfer itself.

`MockJob` supports test and simulation paths. It serializes scalar fields `num_test_segments`, `file_size`, `external_id`, and `should_fail`, plus optional `JobLockedInfo locked_info` and `JobRequestCfg cfg`. The generated merge logic copies non-empty strings and non-zero scalars only, then deep-merges or copy-constructs the optional messages.

`SyncJob` describes upload/download work. Important fields in this chunk are `operation`, `overwrite`, `remote_path`, `flatten`, optional `locked_info`, optional `update`, `metadata`, optional `tagging`, optional `storage_class`, and optional `allow_restore`. The generated table marks `operation` as an open enum and `metadata` as a protobuf map. The map implementation is exposed via `SyncJob_MetadataEntry_DoNotUse` and `GetMapAuxInfo`, with deterministic serialization sorting map entries when the output stream requests deterministic mode.

`Work_Status` stores `Work.State state` and a status `message`. `Work_Part` stores per-part transfer details: `part_number`, `offset_start`, `offset_stop`, `entity_tag`, `checksum_sha256`, and `completed`. `Work` combines `path`, `job_id`, `request_id`, optional `status`, repeated `parts`, and `job_builder`. Generated repeated-field code serializes `parts` in stored order and merges by appending source parts into the destination repeated field.

`UpdateConfigRequest` contains optional `BeeRemoteNode bee_remote` plus repeated `RemoteStorageTarget rsts`. It is the configuration distribution payload for worker nodes; generated merge appends all incoming RSTs and merges or constructs `bee_remote`. `UpdateConfigResponse` carries an open enum `result` and a text `message`.

`BeeRemoteNode` carries BeeRemote identity and connectivity/security material: `id`, `address`, `mgmtd_address`, `mgmtd_tls_cert`, `mgmtd_tls_disable_verification`, `mgmtd_tls_disable`, `auth_secret`, `auth_disable`, and `mgmtd_use_proxy`. `mgmtd_tls_cert` and `auth_secret` are generated as protobuf `bytes` fields and are serialized with `WriteBytesMaybeAliased`; the other textual fields are UTF-8 validated strings.

`RemoteStorageTarget_Policies` currently contains `fast_start_max_size`, a threshold policy used by the remote-storage layer to decide when BeeRemote handles multipart orchestration versus delegating directly to a worker.

`RemoteStorageTarget_S3_StorageClass_Archival` describes archival storage-class restore behavior: `retrieval_tier`, `retention_days`, `check_time`, `recheck_time`, and `auto_restore`. Its parent `RemoteStorageTarget_S3_StorageClass` stores a storage class `name` plus optional `archival`. `RemoteStorageTarget_S3` stores endpoint and credential configuration: `endpoint_url`, `partition_id`, `region`, `bucket`, `access_key`, `secret_key`, and repeated `storage_class`.

`RemoteStorageTarget_Azure` contains optional nested `RemoteStorageTarget_S3 s3` and an `account` string. In the `.proto`, Azure reuses the S3-style configuration shape for compatible object-storage details while adding the Azure account field. `RemoteStorageTarget_POSIX` stores a single filesystem `path`.

The aggregate `RemoteStorageTarget` starts near the end of the chunk. The covered code includes `set_allocated_s3()`, `set_allocated_posix()`, and `set_allocated_azure()`, which clear the current `type` oneof, transfer or copy ownership across arenas with `GetOwnedMessage()`, set the new oneof case, and store the pointer. Its copy constructor deep-copies `policies`, `id`, `name`, and the active `type` oneof branch (`s3`, `posix`, `azure`, or in-place string `mock`). `clear_type()` handles different cleanup paths for pointer-backed message branches and the in-place string-backed `mock` branch.

## Control Flow

The generated classes all follow the protobuf C++ lifecycle pattern:

1. Constructors call `SharedCtor()` to placement-new the internal `Impl_` object and initialize pointer/scalar ranges to zero.
2. Copy constructors merge unknown fields, construct arena-aware string/repeated/map fields, copy has bits, deep-copy present submessages, and copy scalar ranges with `memcpy` where safe.
3. Destructors call `SharedDtor()`, delete unknown-field metadata, assert heap ownership when destructing non-arena messages, destroy arena string pointers, delete heap-owned submessages, clear active oneofs, and destroy the internal implementation object.
4. `Clear()` resets strings, maps, repeated fields, scalar ranges, optional presence bits, unknown fields, and nested messages. Optional message fields are cleared in place rather than deleted.
5. `_InternalSerialize()` writes only fields that are present or non-default under proto3 semantics, then writes unknown fields if any exist.
6. `ByteSizeLong()` computes wire size for present fields and caches it in `_cached_size_` through `MaybeComputeUnknownFieldsSize()`.
7. `MergeImpl()` applies protobuf merge semantics: repeated fields append, message fields merge recursively or are copy-constructed if absent, strings/scalars copy only when source values are non-default, optional fields copy when source has-bits are set, and unknown fields merge.
8. `CopyFrom()` clears the destination and then delegates to `MergeFrom()`.
9. `InternalSwap()` swaps metadata and storage fields, usually requiring equal arenas for string/message ownership safety.

The message-specific control flow is mostly in oneofs and maps:

- `WorkRequest::MergeImpl()` compares source and destination `Type_case()`. If the branch differs, it clears the destination oneof and copy-constructs the source branch; if the branch matches, it merges the nested message.
- `RemoteStorageTarget::set_allocated_*()` always clears the previous `type` branch before adopting the supplied submessage. It preserves arena safety by converting cross-arena pointers through protobuf's ownership helper.
- `RemoteStorageTarget::clear_type()` deletes heap-owned `s3`, `posix`, and `azure` submessages when not on an arena, optionally poisons arena-owned cleared messages under protobuf debug hardening, and explicitly destroys the in-place `mock` string branch.
- `SyncJob::_InternalSerialize()` sorts map entries only when deterministic serialization is requested and there is more than one metadata entry; otherwise it iterates the map's native order.

The parse tables (`TcParseTable`) define fast-path parser dispatch for each message. They map wire tags to parser functions such as `FastUS1` for UTF-8 strings, `FastBS1` for bytes, `FastMtS1` for singular messages, `FastMtR1` for repeated messages, and `SingularVarintNoZag1` for bool/int/enum fields. Auxiliary table entries point to nested message parse tables and map metadata.

## State And Persistence Behavior

The persistent state represented by this generated code is serialized protobuf wire data, not local disk state. The generated classes preserve application state by encoding only present or non-default fields and by keeping unknown fields for forward/backward compatibility.

Presence is important in several places:

- Proto3 scalar fields without `optional` are only serialized when non-default. For example, empty strings, `false`, and numeric zero values are not emitted for most scalar fields in this chunk.
- `optional` scalar and string fields use `_has_bits_`, so an explicit default value can still be distinguished from absence. Examples include `WorkRequest.priority`, `SyncJob.update`, `SyncJob.tagging`, `SyncJob.storage_class`, and `SyncJob.allow_restore`.
- Singular message fields such as `WorkRequest.segment`, `BuilderJob.cfg`, `MockJob.locked_info`, `SyncJob.locked_info`, `Work.status`, `UpdateConfigRequest.bee_remote`, `RemoteStorageTarget_Azure.s3`, and `RemoteStorageTarget.policies` are pointer-backed and presence-tracked.
- Oneof fields persist only the active branch. Setting or merging a different branch discards the previous branch.

Unknown fields are stored through `UnknownFieldSet` metadata and are serialized back out if present. This matters for rolling upgrades where a newer component may send fields that an older C++ component does not understand; the older component can retain the unknown data across parse/serialize cycles if it does not otherwise drop the message.

Repeated and map fields have their own persistence behavior:

- `Work.parts`, `UpdateConfigRequest.rsts`, and `RemoteStorageTarget_S3.storage_class` are repeated message fields. Merge appends source elements, which can duplicate entries if callers use merge where replacement was intended.
- `SyncJob.metadata` is a protobuf map. Deterministic serialization sorts entries by key for stable wire output; normal serialization order is map-implementation dependent.

Sensitive configuration material is present in serialized state. `BeeRemoteNode.auth_secret`, `BeeRemoteNode.mgmtd_tls_cert`, `RemoteStorageTarget_S3.access_key`, and `RemoteStorageTarget_S3.secret_key` are ordinary protobuf fields in this generated code. The code does not redact, encrypt, or zeroize values beyond normal string destruction; confidentiality must be provided by callers, transport security, logging discipline, and storage policy.

## Dependencies And Integration Points

This chunk depends heavily on the Google Protobuf C++ runtime:

- `google::protobuf::Message`, `MessageLite`, `Arena`, `UnknownFieldSet`, `Metadata`, and descriptor/class-data support.
- Internal parser and serializer helpers under `google::protobuf::internal` / `_pbi`, including `TcParser`, `TcParseTable`, `WireFormatLite`, `EpsCopyOutputStream`, `MapEntryFuncs`, `MapSorterPtr`, `ArenaStringPtr`, `MessageCreator`, and `CopyConstruct`.
- Abseil assertions/macros used by generated protobuf code, notably `ABSL_DCHECK`.

The generated code is tied to descriptor data in `descriptor_table_flex_2eproto` and default instances such as `_WorkRequest_default_instance_` and `_RemoteStorageTarget_S3_default_instance_`, which are defined elsewhere in the same generated translation unit.

Application integration points are the Flex protobuf services and cross-language generated bindings:

- `WorkRequest` is the request payload for worker-node submission paths and embeds the job-specific `MockJob`, `SyncJob`, or `BuilderJob` contract.
- `Work` is the generic response/status shape used to return worker state and transfer part details to BeeRemote.
- `UpdateConfigRequest` and `UpdateConfigResponse` correspond to worker configuration updates and include all remote storage targets that should be active on a worker node.
- `BeeRemoteNode` provides the callback/management/auth configuration a worker needs to communicate with BeeRemote and BeeGFS management services.
- `RemoteStorageTarget_*` messages are consumed by worker implementations that support S3-compatible object storage, Azure-compatible configuration, POSIX targets, mock targets, and remote-storage policies.

The C++ output must remain wire-compatible with the Go and Rust outputs generated from the same `flex.proto`. Field numbers, oneof cases, optional-presence semantics, map encoding, and enum values are the shared compatibility contract across those languages.

## Risks And Edge Cases

The largest risk is treating this generated file as the source of truth. Hand-editing `flex.pb.cc` would create drift from `flex.proto`, the generated header, and the Go/Rust bindings. Schema or behavior changes should be made in the `.proto` file and regenerated with the repository's protobuf toolchain.

Proto3 merge semantics can surprise callers. Non-optional scalar defaults do not overwrite existing destination values during `MergeFrom()`, because generated merge code copies only non-default source values. Clearing a scalar in a source message and merging it into a destination will not clear the destination. Callers that want replacement semantics should use `CopyFrom()` or clear fields explicitly.

Repeated-field merge appends rather than replaces. `UpdateConfigRequest.rsts` is especially sensitive because the `.proto` comment says all configured RSTs should be included and missing ones should be deleted by the receiver. If application code merges multiple config requests instead of replacing them, stale or duplicate RST entries can survive.

Oneof transitions destroy prior branch data. `WorkRequest.Type` and `RemoteStorageTarget.type` callers must not keep raw pointers into oneof branches after setting another branch or calling `clear_*()`. The `set_allocated_*()` helpers also take ownership of supplied pointers, potentially copying them to the destination arena; callers must follow protobuf ownership rules.

Arena behavior is subtle. Destructors assert non-arena ownership before deleting fields; arena-owned submessages are not individually deleted. Debug hardening can poison cleared oneof messages on arenas. Tests that inspect cleared arena-backed pointers may fail under hardened builds.

Optional fields require presence-aware checks. For example, `SyncJob.update=false` with presence is semantically different from an absent `update`, and `WorkRequest.priority=0` can be present. Code that only reads scalar values without checking `has_*()` can lose that distinction.

Enum fields are generated as open enum fields in parse tables. Unknown enum values can be stored as numeric values instead of being rejected by this layer. Validation of allowed business-level states, such as meaningful `SyncJob.Operation` or `UpdateConfigResponse.Result`, must happen in application logic.

The generated serializers verify UTF-8 for string fields at serialization time. Invalid string data injected through unsafe APIs or corrupted memory can fail checks or trigger protobuf error behavior during serialization. Bytes fields (`auth_secret`, `mgmtd_tls_cert`) intentionally skip UTF-8 validation.

Secrets are plain fields. Access keys, secret keys, auth secrets, and certificates can be copied by `MergeFrom()`, retained in unknown fields, serialized, and swapped like any other data. Logging whole messages or storing serialized configs without protection can leak credentials.

The chunk ends before the full `RemoteStorageTarget` implementation is visible. Research consumers should not infer its complete serialization, merge, and byte-size behavior solely from this chunk; only the allocation/copy/destruction/parse-table-start behavior is covered here.

## Test Signals

Useful validation for this generated chunk should focus on regeneration, wire compatibility, and representative parse/serialize behavior:

- Regenerate C++ protobuf outputs from `proto/flex.proto` and compare `cpp/flex.pb.cc`/`cpp/flex.pb.h` to the checked-in files to detect manual drift.
- Compile the C++ protobuf target with the repository's expected protobuf runtime version; parse tables and `ClassDataFull` layout are runtime-version sensitive.
- Round-trip serialize/parse `WorkRequest` messages for each `Type` branch (`mock`, `sync`, `builder`) and verify only one branch is active after parse and after branch replacement.
- Exercise `SyncJob.metadata` deterministic serialization with multiple entries and verify stable byte output across runs.
- Verify optional presence survives round trips for `WorkRequest.priority`, `SyncJob.update`, `SyncJob.tagging`, `SyncJob.storage_class`, and `SyncJob.allow_restore`, including explicitly present default values.
- Verify repeated-field behavior for `Work.parts`, `UpdateConfigRequest.rsts`, and `RemoteStorageTarget_S3.storage_class`, especially that merge appends and `CopyFrom()` replaces after clearing.
- Test cross-language compatibility by serializing representative messages in C++ and decoding them with the Go/Rust generated bindings, and vice versa.
- Include negative or edge tests for unknown enum values, unknown fields, empty/default scalar fields, and credential bytes fields to ensure callers understand what protobuf accepts versus what application validation must reject.
- Run sanitizer or arena-focused tests around `set_allocated_s3()`, `set_allocated_posix()`, `set_allocated_azure()`, and oneof clearing to catch ownership mistakes in application code using these generated APIs.
