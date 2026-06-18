# sources/distributed-fs/beegfs-protobuf/cpp/beeremote.pb.cc lines 6010-7691

## Scope

This chunk is the tail of the generated C++ implementation for `beeremote.proto`. It starts inside `beeremote.GetJobsRequest` serialization/size logic and continues through EOF, covering generated implementations for:

- `GetJobsRequest` tail methods for the query `oneof` and include/update flags.
- `GetJobsResponse`.
- `UpdateWorkRequest`.
- `UpdateWorkResponse`.
- `GetRSTConfigRequest`.
- `GetRSTConfigResponse`.
- `GetStubContentsRequest`.
- `GetStubContentsResponse`.
- Namespace/global descriptor registration epilogue.

The file is protobuf compiler output, so the direct code is mostly lifecycle, parsing-table, serialization, merge, copy, swap, and descriptor glue. The protocol contract is better understood with the adjacent source schema in `sources/distributed-fs/beegfs-protobuf/proto/beeremote.proto`: these messages back the `BeeRemote` service RPCs `GetJobs`, `UpdateWork`, `GetRSTConfig`, and `GetStubContents`.

## Purpose

This range implements the wire-format behavior for the BeeRemote query/update/config APIs at the end of `beeremote.proto`.

`GetJobsRequest` and `GetJobsResponse` model job lookup. The request supports one active query selector at a time: `by_job_id_and_path`, `by_exact_path`, or `by_path_prefix`. The proto comments explain that the limited query surface maps to key/value store indexes, where jobs are stored by keys and secondary indexes can be represented through metadata references. The request also has flags controlling whether work request details are included, whether work result details are included, and whether BeeRemote should actively refresh work results from worker nodes while serving the query. The response carries one `path` and repeated `JobResult` records; the service RPC returns a stream of these responses.

`UpdateWorkRequest` and `UpdateWorkResponse` implement the worker-node callback path for reporting work progress/results back to BeeRemote. The request wraps one `flex.Work` message. The response intentionally has no fields, using a project-owned empty message rather than `google.protobuf.Empty` so fields can be added later without changing the RPC message type.

`GetRSTConfigRequest` and `GetRSTConfigResponse` expose remote storage target configuration to callers. The request is empty. The response is repeated `flex.RemoteStorageTarget`, letting BeeRemote provide all currently configured RST definitions in one protobuf response.

`GetStubContentsRequest` and `GetStubContentsResponse` let clients ask BeeRemote what remote content a stub path points at. The request is a path string. The response has optional `rst_id` and optional `url`, preserving presence bits so the response can distinguish absent values from `rst_id == 0` or `url == ""`.

## Important APIs, Types, And Functions

### `GetJobsRequest` tail

The visible portion of `GetJobsRequest` contains:

- `_InternalSerialize()`: writes the active `query` oneof member, then writes non-default bool flags `include_work_requests` field 4, `include_work_results` field 5, and `update_work_results` field 6.
- `ByteSizeLong()`: adds two bytes for each non-default bool, then adds the size of whichever oneof member is active.
- `MergeImpl()`: copies true bool flags from `from`, merges or replaces the active oneof field, and merges unknown fields.
- `CopyFrom()`: clears this message and delegates to `MergeFrom()`.
- `InternalSwap()`: swaps metadata, bool flag storage, the oneof union, and the oneof case value.
- `GetMetadata()`: returns protobuf reflection metadata through `GetClassData()`.

The generated merge behavior matters: scalar bool fields in proto3 do not track presence here, so a false value in `from` does not overwrite a true value in `to` during `MergeFrom()`. Full replacement callers must use `CopyFrom()` or `Clear()` first. The oneof does track which query variant is active and will clear the old query if the incoming oneof case differs.

### `GetJobsResponse`

`GetJobsResponse` is a regular `google::protobuf::Message` with:

- `string path = 1`.
- `repeated beeremote.JobResult results = 2`.

The generated class owns an `ArenaStringPtr` for `path_` and a repeated pointer field for `results_`. `ClassDataFull` and `TcParseTable<1, 2, 1, 38, 2>` bind the generated parser to field 1 as UTF-8 string and field 2 as repeated message using the `JobResult` parse table.

Important methods:

- `SharedCtor()` placement-constructs the `Impl_`.
- `SharedDtor()` deletes unknown fields, destroys `path_`, and destroys the implementation object when not arena-owned.
- `_InternalSerialize()` verifies `path` UTF-8 before writing field 1 and serializes each `JobResult` as field 2 with cached sizes.
- `ByteSizeLong()` accumulates tag and message sizes for all repeated results and the optional non-empty path.
- `MergeImpl()` appends/merges repeated results and sets `path` only if the source path is non-empty.
- `InternalSwap()` requires both messages to share the same arena and swaps metadata, repeated results, and the arena string.

### `UpdateWorkRequest`

`UpdateWorkRequest` is a regular message with one optional message field:

- `flex.Work work = 1`.

Although proto3 message fields have implicit presence, the generated code stores explicit has-bits for `work_`. `_Internal::kHasBitsOffset` points table-driven parsing at `_impl_._has_bits_`.

Important methods:

- `clear_work()` clears the nested `flex.Work` object if allocated and clears has-bit `0x00000001`.
- The copy constructor uses `Message::CopyConstruct<flex::Work>()` only when the source has the `work` bit set.
- `SharedDtor()` deletes `work_` for heap-owned messages.
- `TcParseTable<0, 1, 1, 0, 2>` maps field 1 to `FastMtS1`, a singular message parser using the `flex::Work` table.
- `Clear()` clears the nested work message without necessarily freeing the object, then clears has-bits and unknown fields.
- `_InternalSerialize()` writes field 1 only when the has-bit is set.
- `MergeImpl()` copy-constructs `work_` when the destination lacks it, otherwise merges into the existing nested `flex.Work`.
- `InternalSwap()` swaps metadata, the has-bit word, and the raw `work_` pointer.

This message is the integration point between the BeeRemote protocol and the `flex` worker protocol. `flex.Work` includes path, job ID, request ID, work status, and worker-side state. The proto comments in `beeremote.proto` state that `BeeRemote.UpdateWork` is intended to be called by worker nodes so they can send results back as they become available, avoiding long-lived result streams.

### `UpdateWorkResponse`

`UpdateWorkResponse` is generated as a `ZeroFieldsBase` message. It has no field entries, no aux entries, no has-bits, and a mini parse fallback table. It still has protobuf metadata, copy construction of unknown fields, and descriptor methods.

Its important behavior is the absence of application fields. Success/failure semantics must therefore be represented by RPC status or by future fields added to the message. Because it is a project-owned message type, future additions can be wire-compatible with existing clients that preserve or ignore unknown fields.

### `GetRSTConfigRequest`

`GetRSTConfigRequest` is also generated as a `ZeroFieldsBase` message with no application fields. It participates in descriptor registration and has the same generic empty-message parse behavior as `UpdateWorkResponse`.

The request being empty means the API currently has no filtering, pagination, or version request parameters. Any caller invoking `GetRSTConfig` receives the server's full response set.

### `GetRSTConfigResponse`

`GetRSTConfigResponse` is a regular message with:

- `repeated flex.RemoteStorageTarget rsts = 1`.

The generated parser table maps field 1 to a repeated message using the `flex::RemoteStorageTarget` table. `clear_rsts()` and `Clear()` both clear the repeated field. `_InternalSerialize()` emits every RST as field 1. `ByteSizeLong()` sums one tag byte per item plus each nested message size. `MergeImpl()` appends/merges source RST entries into the destination repeated field. `InternalSwap()` swaps metadata and repeated-field storage.

The dependency on `flex.RemoteStorageTarget` is important because the RST schema is defined outside `beeremote.proto` in `flex.proto`. The comments there indicate RST configuration can be relatively large and includes all remote storage targets that should be configured. This response is the BeeRemote-facing endpoint for distributing that configuration.

### `GetStubContentsRequest`

`GetStubContentsRequest` is a regular message with:

- `string path = 1`.

It uses an `ArenaStringPtr` for `path_` and a table entry marking field 1 as singular UTF-8 string. `_InternalSerialize()` writes `path` only when non-empty and verifies UTF-8. `ByteSizeLong()` accounts for the string only when non-empty. `MergeImpl()` sets the destination path only when the source path is non-empty. `InternalSwap()` requires the same arena and swaps metadata plus the path string.

Because `path` is a non-optional proto3 string, generated code cannot distinguish unset from explicitly set empty string. Server-side validation must reject or define behavior for an empty path if empty paths are invalid.

### `GetStubContentsResponse`

`GetStubContentsResponse` is a regular message with explicit optional scalar/string presence:

- `optional uint32 rst_id = 1`.
- `optional string url = 2`.

The generated has-bit layout uses `0x00000002` for `rst_id` and `0x00000001` for `url`. The parse table maps field 1 to a no-zigzag `uint32` varint parser and field 2 to a UTF-8 string parser.

Important methods:

- The constructors initialize `url_` and set `rst_id_` to zero.
- `Clear()` clears `url_` only when its has-bit is set, resets `rst_id_` to `0u`, clears all has-bits, and clears unknown fields.
- `_InternalSerialize()` writes `rst_id` if the `0x00000002` bit is set and writes `url` if the `0x00000001` bit is set.
- `ByteSizeLong()` separately accounts for optional URL and optional RST ID.
- `MergeImpl()` sets URL and/or RST ID when the source has the corresponding bit, then ORs the source has-bits into the destination.
- `InternalSwap()` swaps metadata, has-bits, URL storage, and RST ID.

Optional presence is the key semantic detail. A response can represent "no stub target/content available" by omitting both fields, "target known but URL unavailable" by setting only `rst_id`, or "URL known without an explicit target" by setting only `url`, depending on server policy.

## Control Flow

The runtime control flow is protobuf and RPC driven:

1. A client or worker constructs one of these generated message types through the public C++ API in `beeremote.pb.h`.
2. Setters mutate private `_impl_` fields, oneof case storage, has-bits, arena strings, repeated fields, or nested message pointers.
3. gRPC/protobuf serialization calls `_InternalSerialize()` to emit only present or non-default fields, followed by any unknown fields.
4. Receivers use the table-driven parser definitions (`TcParseTable`) to reconstruct the generated message instances.
5. Service implementation code outside this generated file inspects the resulting messages and performs application behavior: job lookup, work status update, RST config lookup, or stub-content lookup.
6. When application code combines messages, `MergeImpl()` applies protobuf merge semantics. For repeated fields, entries are appended/merged. For message fields, nested messages are merged. For proto3 non-presence scalars/strings, only non-default source values overwrite. For optional scalar/string fields and oneofs, presence is preserved.
7. Response messages are serialized back through the same generated write paths.

For `BeeRemote.GetJobs`, the application flow implied by the proto is: the request chooses one key/value-store query shape, the server streams one or more `GetJobsResponse` messages keyed by path, and the inclusion/update flags determine how much nested work detail and freshness work the server performs before returning results.

For `BeeRemote.UpdateWork`, the flow is worker-to-BeeRemote: the worker sends a `flex.Work` update, BeeRemote records or reconciles the work status, and an empty `UpdateWorkResponse` confirms the unary RPC completed successfully at the protobuf level.

For `BeeRemote.GetRSTConfig`, the empty request triggers a full remote storage target configuration response.

For `BeeRemote.GetStubContents`, the path request maps to optional target and URL response data.

## State And Persistence Behavior

This generated file does not directly persist state to disk. It defines the in-memory and wire representation used by higher-level BeeRemote components that do persist job and work state.

The proto comments around `GetJobsRequest` describe the persistence model: BeeRemote stores jobs in key/value stores where keys serve as indexes, and `MapStore` over BadgerDB can use metadata to reference data stored in other maps instead of duplicating complete records for every query dimension. The `GetJobsRequest` oneof mirrors that persistence model by limiting server queries to the indexes that exist: job ID plus path, exact path, and path prefix.

State semantics inside this generated code are:

- Unknown fields are preserved in `_internal_metadata_`, serialized back out, merged, swapped, and cleared with the message. This supports forward compatibility across schema versions.
- Cached serialized sizes are stored in each message's `_cached_size_` and updated by protobuf internals.
- `GetJobsRequest` oneof state is stored in `_oneof_case_[0]`; switching query variants clears the prior variant.
- `UpdateWorkRequest` stores `work_` as a lazily allocated nested message pointer with a has-bit.
- `GetJobsResponse` and `GetRSTConfigResponse` store repeated nested messages in protobuf repeated pointer fields; merge appends rather than replaces.
- `GetStubContentsResponse` uses has-bits for optional scalar/string presence, so presence survives serialization, merge, clear, and copy operations.
- Empty request/response messages still preserve unknown fields, so future fields can pass through older binaries subject to normal protobuf unknown-field handling.

Application-level persistence happens outside this file: job records, work results, RST configuration, and stub metadata are read from or written to BeeRemote's stores by service handlers that consume these generated types.

## Dependencies And Integration Points

Primary dependencies are the C++ protobuf runtime and the generated code for related schemas:

- `google::protobuf::Message`, `ZeroFieldsBase`, `Arena`, `UnknownFieldSet`, `Metadata`, `WireFormatLite`, `EpsCopyOutputStream`, `RepeatedPtrField`, `ArenaStringPtr`, `TcParser`, and `TcParseTable`.
- `beeremote.JobResult`, implemented earlier in the same generated file and used by `GetJobsResponse`.
- `flex.Work`, used by `UpdateWorkRequest`.
- `flex.RemoteStorageTarget`, used by `GetRSTConfigResponse`.
- `descriptor_table_beeremote_2eproto`, class data, default instances, and generated descriptor methods built earlier in the file.

Service-level integration points from `beeremote.proto` are:

- `rpc GetJobs(GetJobsRequest) returns (stream GetJobsResponse)`.
- `rpc UpdateWork(UpdateWorkRequest) returns (UpdateWorkResponse)`.
- `rpc GetRSTConfig(GetRSTConfigRequest) returns (GetRSTConfigResponse)`.
- `rpc GetStubContents(GetStubContentsRequest) returns (GetStubContentsResponse)`.

The final file epilogue closes the `beeremote` namespace, leaves empty `google::protobuf` namespace insertion hooks, and registers descriptors through a static `_static_init2_` initializer that calls `_pbi::AddDescriptors(&descriptor_table_beeremote_2eproto)`. This is necessary for reflection, descriptors, text/debug formatting, and gRPC/protobuf runtime integration.

## Risks And Edge Cases

Generated protobuf code should generally not be patched by hand. Contract changes belong in `beeremote.proto` or imported proto files followed by regeneration. Manual edits here are at high risk of being overwritten or diverging from the generated header and descriptors.

`GetJobsRequest` merge semantics can surprise callers. The three bool flags are proto3 scalar fields without explicit presence, so merging a request with `include_work_results=false` into a request that already has it true will not clear the destination. Use `CopyFrom()` or `Clear()` before merge when replacement semantics are required.

The `GetJobsRequest` oneof enforces exactly one query variant at the message level, but it does not enforce that any query is set. A default request has `QUERY_NOT_SET`. Service code must reject or define behavior for a missing query; otherwise it could accidentally scan all jobs or return nothing depending on handler implementation.

Path strings are UTF-8 protobuf strings, not byte paths. Serialization verifies UTF-8 for `GetJobsRequest` string variants, `GetJobsResponse.path`, `GetStubContentsRequest.path`, and `GetStubContentsResponse.url`. Non-UTF-8 filesystem paths or opaque URLs cannot be represented safely as these string fields.

`GetJobsRequest.by_path_prefix="/"` is documented as a way to return all jobs. Combined with `include_work_requests`, `include_work_results`, or especially `update_work_results`, this can trigger large responses and expensive worker-node refresh work. Streaming mitigates response size for `GetJobs`, but server-side locking, store scans, and worker RPC fan-out remain risks.

`GetJobsResponse.MergeImpl()` appends results rather than replacing them. Code that reuses response objects across paths or pages must call `Clear()` before reuse to avoid mixing result sets.

`UpdateWorkRequest` accepts absence of `work` at the protobuf layer. Service code must check `has_work()` and reject empty updates; otherwise an empty update could be interpreted as a default `flex.Work` with empty IDs/status.

`UpdateWorkResponse` has no fields, so all current failure detail must be expressed as the gRPC status. If callers need partial-acceptance details later, adding fields is wire-compatible but requires careful client/server rollout.

`GetRSTConfigRequest` has no filters or pagination. Large RST configuration sets are returned in one response, and changes to RST visibility or partial config retrieval require future fields.

`GetStubContentsRequest.path` is a non-optional string, so absence and empty string are the same. Service validation must handle empty paths explicitly. `GetStubContentsResponse` uses optional fields, so clients should call `has_rst_id()` and `has_url()` instead of treating `0` or empty string as absent.

Arena-sensitive swaps require matching arenas in several message types. Generated `InternalSwap()` uses `ABSL_DCHECK_EQ(arena, other->GetArena())`; debug builds catch mismatches, while callers should still use public swap APIs appropriately.

Static descriptor initialization order is managed by protobuf macros, but embedding this generated file into unusual build systems can expose initialization/linking issues if descriptor symbols or imported `flex` generated code are missing.

## Test Signals

High-signal tests should focus on the generated contract through public APIs and RPC behavior rather than editing generated internals.

Static/generated-code checks:

- Regenerate `beeremote.pb.cc` and `beeremote.pb.h` from `beeremote.proto` and verify this tail does not drift.
- Compile a target that links `beeremote.pb.cc` with the generated `flex` protobuf objects to catch missing descriptor/table symbols.
- Run protobuf reflection checks for `beeremote.GetJobsResponse`, `beeremote.UpdateWorkRequest`, `beeremote.GetRSTConfigResponse`, and `beeremote.GetStubContentsResponse`.

Serialization and merge tests:

- Round-trip `GetJobsRequest` for each query oneof variant and verify `query_case()` and field values survive.
- Verify setting `by_exact_path` then `by_path_prefix` clears the old oneof variant.
- Verify `GetJobsRequest.MergeFrom()` does not clear true bool flags when the source has default false, and document that `CopyFrom()` is needed for replacement.
- Round-trip `GetJobsResponse` with multiple `JobResult` entries and confirm repeated result order and path are preserved.
- Verify `GetJobsResponse.MergeFrom()` appends results and only overwrites path when the source path is non-empty.
- Round-trip `UpdateWorkRequest` with and without `work`; verify `has_work()` controls serialization.
- Verify `GetStubContentsResponse` presence semantics: unset fields, `rst_id=0` with presence, empty `url` with presence, and both fields set should remain distinguishable after serialization.
- Verify unknown fields survive parse/serialize and merge for both empty and non-empty messages.

Service-level tests:

- `BeeRemote.GetJobs` should reject missing query, return at most one job for `by_job_id_and_path`, return all jobs for an exact path, and stream all matching paths for prefix queries.
- `GetJobs` with `include_work_requests=false/include_work_results=false` should omit heavy details according to service policy; true flags should include the expected nested data.
- `GetJobs` with `update_work_results=true` should exercise worker refresh and status-update paths, including failures communicating with worker nodes.
- `BeeRemote.UpdateWork` should reject requests without `work`, accept valid worker-owned `flex.Work` updates, persist them, and return success through an empty response plus OK RPC status.
- `BeeRemote.GetRSTConfig` should return all configured `flex.RemoteStorageTarget` entries and handle an empty configuration deterministically.
- `BeeRemote.GetStubContents` should validate empty and malformed paths and should return optional `rst_id`/`url` presence according to whether the path is a stub with known remote content.
