# subset-b-000025 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/vertex_test.go -->
## sources/cloud-native/buildkit/solver/llbsolver/vertex_test.go

Purpose: this Go test file exercises llbsolver vertex normalization behavior around BuildKit LLB operation digests. It focuses on digest recomputation for serialized `pb.Op` DAG nodes, backward compatibility with gogoproto-encoded test data, and proxy-network-related vertex digest semantics.

Important APIs and helpers: `TestRecomputeDigests` constructs `pb.Op` source and dependent ops, mutates the source identifier, and verifies `recomputeDigests` rewrites downstream `Input.Digest` values and returns a new digest for the dependent op. `TestIngestDigest` embeds `testdata/gogoproto.data`, unmarshals a `pb.Definition`, and verifies canonical digest recomputation for legacy data. The proxy network tests call `Load`, `loadWithProxyNetwork`, `NormalizeRuntimePlatforms`, and `ValidateEntitlements` and inspect the loaded vertex via `requireVertexOp`. Helper functions `proxyNetworkTestDefinition`, `marshalTestOp`, and `requireVertexOp` build a small source -> exec -> root LLB definition, deterministically marshal operations through `pb.Op.Marshal`, and recover `*pb.Op` from vertex system metadata.

Control flow: the digest tests build old and new serialized source operations, seed an `all` map of digest to internal `op`, seed or inspect a `visited` map, then call `recomputeDigests` from a selected root digest. The proxy tests generate a reusable definition, load it with default options or proxy-network options, then compare the `pb.ExecOp.Network` field and vertex digest. Entitlement coverage deliberately exercises the host-network failure path first, then repeats with `entitlements.EntitlementNetworkHost` allowed.

State and persistence: the file is test-only and persists no runtime state. Its important state is in-memory serialized protobuf bytes, digest maps, and embedded fixture bytes. The fixture represents compatibility input and makes digest behavior reproducible across test runs.

Dependencies and integration points: the tests integrate `github.com/moby/buildkit/solver/pb`, llbsolver loading code, BuildKit entitlements, OpenContainers digest calculation, and `testify` assertions. They are regression tests for the boundary where protobuf serialization, operation digest identity, solver loading, and entitlement validation meet.

Risks and test signals: these tests guard against stale input digests after op mutation, non-canonical digest ingestion from legacy gogoproto data, accidental digest changes from platform normalization, and missing entitlement enforcement when proxy network behavior triggers host network semantics. A notable signal is that host network plus proxy changes the vertex digest and requires entitlement, while explicit none mode is preserved without a digest change.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/vertex_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/memorycachestorage.go -->
## sources/cloud-native/buildkit/solver/memorycachestorage.go

Purpose: this file implements in-memory `CacheKeyStorage` and `CacheResultStorage` backends for BuildKit's solver. The key store tracks cache keys, result associations, dependency links, and backlinks; the result store tracks concrete solver `Result` values by ID. It is suitable for process-local operation and tests, not durable persistence.

Important APIs and types: `NewInMemoryCacheStorage` returns an `inMemoryStore` with `byID` and `byResult` maps. `inMemoryKey` stores `results`, outgoing `links`, reverse `backlinks`, and its `id`. Key-store methods include `Exists`, `Walk`, `WalkResults`, `Load`, `AddResult`, `WalkIDsByResult`, `Release`, `AddLink`, `WalkLinks`, `HasLink`, and `WalkBacklinks`. `NewInMemoryResultStorage` returns an `inMemoryResultStore` backed by `bkmaps.SyncMap[string, Result]`; methods are `Save`, `Load`, `LoadRemotes`, and `Exists`.

Control flow: all key-store mutations hold `mu.Lock`; read paths generally copy IDs, results, or links while holding a read lock and invoke callbacks after unlocking to avoid callback-induced deadlocks. `AddResult` creates a key on demand, stores the `CacheResult`, and maintains the reverse `byResult` index. `Release` removes a result from every key that references it and calls `emptyBranchWithParents` to prune now-empty keys and recursively unlink empty parents. `AddLink` creates both endpoints on demand, records the target in the source's link bucket, and records the source in the target's backlinks. `WalkBacklinks` reconstructs normalized `CacheInfoLink` values from parents, applying `rootKey(l.Digest, l.Output)` for the reported digest.

State and persistence: all cache-key state is volatile maps under a mutex. There is no disk persistence, eviction metadata, remote descriptor persistence, or cross-process sharing. Result storage is similarly process-local and ignores `createdAt` except to return it in `CacheResult`. `LoadRemotes` always returns nil remotes and nil error, so remote cache metadata is not represented.

Dependencies and integration points: the implementation depends on solver package interfaces and types such as `CacheKeyStorage`, `CacheInfoLink`, `CacheResult`, `CacheResultStorage`, `Result`, `Remote`, `ErrNotFound`, and `rootKey`. External dependencies are BuildKit `session`, `bkmaps.SyncMap`, compression config, and `pkg/errors`.

Risks and test signals: recursive pruning in `emptyBranchWithParents` is the highest-risk path because it mutates parent link maps while traversing backlinks. Callback methods intentionally copy under lock first, which lowers lock-order risk but can expose snapshots rather than live views. Because this is in-memory-only, behavior after restart is empty cache state. There are no tests in this file; validation likely comes from solver cache tests elsewhere that assert link traversal, release pruning, and result lookup semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/memorycachestorage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/pb/attr.go -->
## sources/cloud-native/buildkit/solver/pb/attr.go

Purpose: this file defines string constants used as attribute keys and well-known attribute values for `pb.SourceOp.Attrs` and related LLB source behavior. It centralizes the keys that frontend code, solver code, and source implementations use to negotiate source-specific options.

Important APIs and constants: Git-related attributes include `AttrKeepGitDir`, `AttrFullRemoteURL`, authentication secrets, known-hosts and SSH socket keys, checksum, submodule, mtime, fetch-by-commit, bundle, checkout bundle, and signature verification options. Local-source attributes cover session identity, uniqueness, include/follow/exclude patterns, shared cache key hints, metadata transfer, and differ mode values. HTTP attributes cover checksum, filename, permission bits, UID/GID, auth header secret, header prefix, and signature verification. Image attributes cover resolve mode values, record type, layer limit, and checksum. OCI layout and LLB-build attributes are also defined.

Control flow: there is no runtime control flow; these constants are consumed by other packages when constructing or interpreting LLB protobuf messages. The only type alias is `type IsFileAction = isFileAction_Action`, which exposes the generated oneof interface under an exported name for code that needs to type against file-action variants.

State and persistence: no state is stored. The constants become part of serialized `SourceOp.Attrs` maps, so changing a key directly affects cache keys, remote compatibility, and how existing serialized definitions are interpreted.

Dependencies and integration points: the constants pair with `ops.proto`'s `SourceOp.attrs` map and with capabilities in `caps.go`. Source handlers for local, git, HTTP, image, OCI layout, and nested LLB build options depend on the exact strings. The historical external contract matters more than internal Go naming.

Risks and test signals: misspelling or changing a constant is compatibility-sensitive. The broader package already preserves one historical typo in `caps.go`, illustrating that string contracts are immutable once used. There are no direct tests in this file; coverage is indirect through LLB serialization, source resolver behavior, frontend emission, and capability negotiation tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/pb/attr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/pb/caps.go -->
## sources/cloud-native/buildkit/solver/pb/caps.go

Purpose: this file defines BuildKit LLB API capability identifiers and registers them into the package-global `Caps apicaps.CapList`. Capabilities represent backward- or forward-incompatible feature gates for source operations, exec metadata, file operations, cache exporters, policies, history, GC filters, and other solver features.

Important APIs and constants: exported `Cap*` constants are `apicaps.CapID` values. Source capabilities cover image, local, git, HTTP, image blob, OCI layout, and build-op LLB filename support. Exec capabilities cover metadata fields, proxy env, network and proxy network, security modes, device whitelist, ulimit, CDI, Linux resources, mount types and options, cgroups, secret env, and valid exit codes. File capabilities cover base file ops, wildcard removal, copy include/exclude and required paths, symlink behavior, mode string format, and replacement behavior. Other categories include constraints, platform, ignore-cache and descriptions, export cache, remote cache backends, merge/diff/passthrough ops, annotations, attestations, source date epoch, multiple/session exporters, source policy, GC free-space filtering, and history filters.

Control flow: package initialization calls `Caps.Init` once per capability. Most entries are enabled and experimental. `CapFileBase` is prerelease and includes `SupportedHint` entries for Docker and BuildKit versions. `CapSourceDateEpoch` includes a human-readable name. A comment states the policy: every incompatible change needs a new capability row; new capabilities should usually start experimental; merged capability rows are immutable; stable capabilities should not be disabled.

State and persistence: `Caps` is global package state initialized at import time. It is not persisted directly, but it controls compatibility negotiation and can affect whether an LLB definition is accepted or a feature is advertised. Because capability IDs are serialized/communicated strings, their values are persistent protocol contracts.

Dependencies and integration points: the only direct dependency is `github.com/moby/buildkit/util/apicaps`. The capability constants correspond to fields and operation variants in `ops.proto`, source attributes in `attr.go`, frontend feature emission, daemon/client negotiation, and solver validation. The historical typo `CapSourceHTTPUIDGID = "soruce.http.uidgid"` is intentionally preserved for compatibility.

Risks and test signals: the main risk is accidental capability churn: changing an ID, disabling an established capability, or forgetting to add a capability for an incompatible protobuf/behavior change can break mixed-version clients and workers. The file itself has no direct tests; coverage is integration-oriented through LLB capability negotiation and feature-specific tests that require matching caps.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/pb/caps.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/pb/const.go -->
## sources/cloud-native/buildkit/solver/pb/const.go

Purpose: this file defines small typed constants used throughout BuildKit's LLB protobuf model to express input and output indexes and conventional mount/build sentinel values.

Important APIs and constants: `InputIndex` and `OutputIndex` are typed `int64` aliases for referring to input vertices and output slots. `RootMount` is the root filesystem mount point `/`. `SkipOutput` is `OutputIndex(-1)` for disabled outputs. `Empty` is `InputIndex(-1)` for no-content input. `LLBBuilder` is `InputIndex(-1)` for the special nested build builder input. `LLBDefinitionInput` and `LLBDefaultDefinitionFile` both use `buildkit.llb.definition` to identify an LLB definition file used by `BuildOp`.

Control flow: there is no executable control flow. The constants are read by solver, frontend, and operation construction code when building or interpreting LLB graphs.

State and persistence: no local state is stored. These sentinel values appear in serialized LLB definitions and therefore form part of the persisted/cached graph contract. Reusing `-1` for several typed sentinel contexts is intentional because the types and consuming fields disambiguate meaning.

Dependencies and integration points: the constants integrate with `ops.proto` fields such as `Input.index`, `Mount.input`, `Mount.output`, `BuildOp.builder`, and `BuildInput.input`. `RootMount` is used by exec mount creation, and the LLB definition constants connect nested `BuildOp` behavior with filesystem inputs.

Risks and test signals: risks are mostly semantic misuse, such as passing `Empty` where a real input is required or forgetting that `LLBBuilder` and `Empty` share the same raw integer. There are no direct tests in this file; behavior is covered indirectly by solver and frontend tests that construct LLB graphs with root mounts, empty inputs, skipped outputs, and nested build definitions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/pb/const.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/pb/json.go -->
## sources/cloud-native/buildkit/solver/pb/json.go

Purpose: this file provides custom JSON marshaling and unmarshaling for protobuf messages that contain oneof fields: `Op`, `FileAction`, and `UserOpt`. The generated protobuf JSON shape is not used here; instead the package exposes a stable, readable JSON object layout for LLB debugging and round-tripping.

Important APIs and types: `jsonOp` wraps `Op` with `inputs`, an `Op` object containing optional `exec`, `source`, `file`, `build`, `merge`, `diff`, and `passthrough` fields, plus `platform` and `constraints`. `(*Op).MarshalJSON` and `(*Op).UnmarshalJSON` translate between protobuf oneof wrappers and that JSON structure. `jsonFileAction` exposes `input`, `secondaryInput`, `output`, and an `Action` object with optional `copy`, `mkfile`, `mkdir`, and `rm` fields. `(*FileAction).MarshalJSON` and `(*FileAction).UnmarshalJSON` map the file-action oneof. `jsonUserOpt`, `(*UserOpt).MarshalJSON`, and `(*UserOpt).UnmarshalJSON` encode named user vs numeric ID options.

Control flow: each marshal method copies scalar fields into the JSON wrapper, type-switches on the active oneof wrapper, sets the corresponding pointer field, and calls `json.Marshal`. Each unmarshal method decodes into the wrapper, copies scalar fields back, and selects the first non-nil oneof option in a fixed order. `UserOpt.UnmarshalJSON` defaults to `ByID` even when `byId` is absent, which means an empty user object decodes as ID zero.

State and persistence: no package state is stored. The persistent behavior is the JSON representation itself. Because `ops.proto` comments require changes to selected oneof-bearing structures to be reflected in `json.go`, this file is part of the compatibility surface whenever new op, file action, or user option variants are added.

Dependencies and integration points: direct dependency is `encoding/json`; structural dependencies are the generated protobuf types in `ops.pb.go`. It is integrated with `json_test.go`, with LLB debugging/export tooling, and with any code that expects these custom JSON keys rather than default protobuf JSON.

Risks and test signals: a current compatibility gap is that `ops.proto` and `ops.pb.go` include `FileActionSymlink`, but `jsonFileAction` does not include a symlink branch. Symlink file actions therefore cannot round-trip through this custom JSON path. Another risk is silent precedence when JSON contains multiple oneof branches. Tests cover the listed op variants, copy/mkfile/mkdir/rm file actions, and user by-name/by-ID cases, but not symlink or malformed multi-oneof input.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/pb/json.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/pb/json_test.go -->
## sources/cloud-native/buildkit/solver/pb/json_test.go

Purpose: this test file validates the custom JSON round-trip behavior implemented in `json.go` for `Op`, `FileAction`, and `UserOpt` protobuf messages. It ensures the JSON shape is stable and that marshaled JSON can unmarshal back into equivalent Go protobuf structs.

Important APIs and tests: `TestJSON_Op` covers exec, source, file, build, merge, and diff operations. It checks both exact structural JSON equivalence and unmarshal equality. `TestJSON_FileAction` covers copy, mkfile, mkdir, and rm actions, including byte data encoding for `mkfile` as base64 JSON. `TestJSON_UserOpt` covers `UserOpt_ByName` and `UserOpt_ByID`. The tests use `encoding/json` and `testify/require`.

Control flow: each test defines a table of named cases with a protobuf value and an expected JSON string. For each case, it marshals the protobuf value, unmarshals both actual and expected JSON into `any` to avoid formatting/key-order sensitivity, and compares the resulting structures. It then unmarshals the actual bytes into a fresh protobuf object and requires deep equality with the original.

State and persistence: there is no persistent state. The expected JSON strings are the contract under test. They capture omitempty behavior, nested `Op` / `Action` / `User` wrapper object names, default numeric fields that remain visible in custom file-action JSON, and protobuf byte-to-base64 encoding for raw file contents.

Dependencies and integration points: these tests integrate directly with `json.go` and the generated types in `ops.pb.go`. They are important for frontend/debugging compatibility because the custom JSON layout is manually maintained in parallel with `ops.proto`.

Risks and test signals: the tests provide strong signal for currently-covered oneof variants but expose omissions by absence. `PassthroughOp` is handled in `json.go` but not covered here, and `FileActionSymlink` exists in the schema/generated code but is not represented or tested in `json.go`. There is also no test for invalid JSON, JSON containing multiple oneof branches, or empty `UserOpt` behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/pb/json_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/pb/ops.go -->
## sources/cloud-native/buildkit/solver/pb/ops.go

Purpose: this file adds hand-written convenience methods on top of generated protobuf/VTProto types for `Definition` and `Op`. It hides the actual marshaling implementation behind stable methods used by solver code and tests.

Important APIs: `(*Definition).IsNil` treats a nil definition or a definition with nil `Metadata` as logically nil. `(*Definition).Marshal` delegates to `MarshalVT`, and `(*Definition).Unmarshal` delegates to `UnmarshalVT`, using vtprotobuf-generated fast paths. `(*Op).Marshal` uses `proto.MarshalOptions{Deterministic: true}` to produce stable serialized bytes for digest calculation. `(*Op).Unmarshal` delegates to `UnmarshalVT`.

Control flow: all methods are thin wrappers. The only behavioral choice is deterministic marshaling for `Op`, which is critical because BuildKit digests serialized operations and uses those digests as LLB graph identities. `Definition` marshaling does not explicitly request deterministic protobuf marshaling here because it delegates to the vtprotobuf implementation.

State and persistence: no state is stored, but serialized byte output is persistent in cache keys, LLB definitions, and digest references. `Op.Marshal` stability is especially important because `pb.Input.digest` values in the graph refer to digests of marshaled input `Op` messages.

Dependencies and integration points: this file depends on `google.golang.org/protobuf/proto` and generated methods from `ops.pb.go` plus vtprotobuf-generated methods elsewhere in the package. It is used by llbsolver loading, digest recomputation tests, and any frontend or solver path that serializes/deserializes LLB definitions.

Risks and test signals: changing `Op.Marshal` away from deterministic marshaling would destabilize digest identities. `Definition.IsNil` can be surprising because a non-nil `Definition` with nil metadata is considered nil even if other fields are populated. `vertex_test.go` provides direct signal for deterministic op marshaling and digest recomputation behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/pb/ops.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/pb/ops.pb.go -->
## sources/cloud-native/buildkit/solver/pb/ops.pb.go

Purpose: this generated Go file is the protoc output for `solver/pb/ops.proto`. It provides the concrete Go representation of BuildKit's LLB protobuf schema, including enums, message structs, oneof wrapper types, getters, reflection descriptors, dependency indexes, and descriptor initialization.

Important APIs and types: enums include `NetMode`, `SecurityMode`, `MountType`, `MountContentCache`, and `CacheSharingOpt`. Core graph types include `Op`, `Input`, `Definition`, `OpMetadata`, `Platform`, and `WorkerConstraints`. Operation variants are represented by `Op_Exec`, `Op_Source`, `Op_File`, `Op_Build`, `Op_Merge`, `Op_Diff`, and `Op_Passthrough`. Exec-related types include `ExecOp`, `Meta`, `HostIP`, `Ulimit`, `SecretEnv`, `CDIDevice`, `Mount`, `TmpfsOpt`, `CacheOpt`, `SecretOpt`, `SSHOpt`, and `ProxyEnv`. Source and nested build types include `SourceOp`, `BuildOp`, and `BuildInput`. File operation types include `FileOp`, `FileAction`, `FileActionCopy`, `FileActionMkFile`, `FileActionSymlink`, `FileActionMkDir`, `FileActionRm`, `ChownOpt`, `UserOpt`, and `NamedUserOpt`. Merge/diff/passthrough are represented by `MergeInput`, `MergeOp`, `LowerDiffInput`, `UpperDiffInput`, `DiffOp`, and `PassthroughOp`.

Control flow: generated methods follow the standard protobuf runtime pattern: `Reset`, `String`, `ProtoMessage`, `ProtoReflect`, deprecated `Descriptor`, enum descriptor methods, and nil-safe `Get*` accessors. Oneof getters type-assert the active wrapper and return nil/default values otherwise. Package initialization builds the `protoreflect.FileDescriptor` with `protoimpl.TypeBuilder`, registers oneof wrappers for `Op`, `FileAction`, and `UserOpt`, compresses the raw descriptor lazily with `sync.Once`, and releases Go type/dependency slices after building.

State and persistence: message structs hold protobuf state, unknown fields, and size caches. The file-level descriptor variables are initialized once and reused globally. Serialized instances of these types are the durable LLB DAG contract: `Definition.Def` stores marshaled `Op` bytes, `Input.Digest` references marshaled op digests, and `Definition.Metadata` is keyed by op digest string. Unknown fields support forward compatibility at the protobuf layer.

Dependencies and integration points: this file depends on `google.golang.org/protobuf/reflect/protoreflect`, `runtime/protoimpl`, `reflect`, `sync`, and `unsafe`. It is consumed by all BuildKit code that constructs, loads, solves, serializes, inspects, or negotiates LLB operations. Hand-written package files `ops.go`, `json.go`, `attr.go`, `const.go`, and `caps.go` add behavior and constants around these generated structs.

Risks and test signals: this file should not be manually edited; schema changes belong in `ops.proto` followed by regeneration. Important risks include generated/schema drift, missing updates to `json.go` when oneof-bearing messages change, and cache-key incompatibility when field numbers or semantics are changed incorrectly. `json_test.go` covers custom JSON behavior for many generated oneof variants, while `vertex_test.go` exercises deterministic operation serialization and digest identity.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/pb/ops.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/pb/ops.proto -->
## sources/cloud-native/buildkit/solver/pb/ops.proto

Purpose: this protobuf schema defines BuildKit's LLB, the low-level builder instruction graph. `Op` is a DAG vertex, `Input` edges point to other vertices by digest of their marshaled `Op`, and `Definition` packages serialized ops with per-vertex metadata and optional source maps.

Important APIs and messages: `Op` contains repeated `Input`, a oneof operation variant (`ExecOp`, `SourceOp`, `FileOp`, `BuildOp`, `MergeOp`, `DiffOp`, `PassthroughOp`), plus `Platform` and `WorkerConstraints`. `ExecOp` models command execution with `Meta`, mounts, network mode, security mode, secret env, and CDI devices. `Mount` supports bind, secret, SSH, cache, tmpfs, result IDs, and content-cache hints. `SourceOp` identifies sources by URL-like identifier plus an attrs map defined by `attr.go`. `BuildOp` embeds nested build definitions and named inputs. `OpMetadata` carries cache, description, capability, progress-group, export-cache, and Linux resource metadata. `FileOp` contains ordered `FileAction` oneof entries for copy, mkfile, mkdir, rm, and symlink. `MergeOp`, `DiffOp`, and `PassthroughOp` model filesystem composition and pass-through behavior.

Control flow: protobuf schemas do not execute, but this schema defines the data flow for the solver. A `Definition` lists marshaled operations, each `Op.inputs[*].digest` links to the digest of another marshaled op, and op-specific fields describe how the solver should produce outputs. File actions describe transformations over input/output indexes. Metadata is keyed separately by op digest so some runtime metadata can be applied without living directly on the op body.

State and persistence: this is a persistent wire and cache-key contract. Field numbers, enum values, oneof variants, map keys, and sentinel meanings must remain compatible with existing serialized LLB definitions. Comments explicitly note that changes to `Op`, `FileAction`, and `UserOpt` must be represented in `json.go`.

Dependencies and integration points: `go_package` maps the schema to `github.com/moby/buildkit/solver/pb`. Generated Go code appears in `ops.pb.go`, with wrapper methods in `ops.go`, custom JSON in `json.go`, attributes in `attr.go`, and capabilities in `caps.go`. The schema integrates with frontends, solver internals, workers, source resolvers, cache key calculation, exporters, and progress/source-map reporting.

Risks and test signals: schema evolution is high risk because op serialization feeds digest identity and cache reuse. Adding a field or oneof variant may require a new capability in `caps.go`, custom JSON changes in `json.go`, and tests. A visible current drift is `FileActionSymlink`: it exists in the schema and generated code, but the custom JSON wrapper in `json.go` does not handle it. Tests in `json_test.go` and `vertex_test.go` cover JSON round trips and digest semantics for selected paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/pb/ops.proto -->
