# sources/cloud-native/buildkit/solver/pb/ops_vtproto.pb.go lines 12303-15648

## Scope

This chunk is generated `protoc-gen-go-vtproto` code for high-speed protobuf unmarshalling of the latter half of BuildKit's LLB operation schema. It starts inside `ExportCache.UnmarshalVT`, then covers complete `UnmarshalVT` implementations for `ProgressGroup`, `LinuxResources`, `ProxyEnv`, `WorkerConstraints`, `Definition`, `FileOp`, `FileAction`, file action payloads, ownership/user options, merge/diff inputs, `DiffOp`, and `PassthroughOp`.

The source schema for these messages is `sources/cloud-native/buildkit/solver/pb/ops.proto`; the Go type declarations are in `ops.pb.go`. This file is generated and should normally be changed by editing the proto/generation pipeline rather than hand editing the generated decoder.

## Purpose

The code decodes serialized LLB graph and operation messages into Go structs without going through reflective protobuf decoding. These messages sit on the BuildKit solver API boundary: `Definition` carries marshaled `Op` vertices plus metadata, `FileOp` describes filesystem mutation vertices, `MergeOp` and `DiffOp` model snapshot graph operations, `PassthroughOp` exposes external/custom outputs, and metadata helper messages carry cache, progress, resource, proxy, and worker-selection information.

## Important APIs And Types

- `ExportCache.UnmarshalVT` decodes the boolean `Value` field and preserves unknown fields. This is used through `OpMetadata.export_cache`.
- `ProgressGroup.UnmarshalVT` decodes progress grouping fields `id`, `name`, and `weak`, used by `OpMetadata.progress_group`.
- `LinuxResources.UnmarshalVT` decodes cgroup-style limits: memory, memory+swap, CPU shares/period/quota, and CPU/memory node affinity strings. The schema comments state these are per-step metadata constraints that do not affect cache keys.
- `ProxyEnv.UnmarshalVT` decodes the proxy environment tuple `http_proxy`, `https_proxy`, `ftp_proxy`, `no_proxy`, and `all_proxy`. `Meta` references this message outside the chunk.
- `WorkerConstraints.UnmarshalVT` appends repeated containerd-style filter strings. `Op` references this as top-level worker constraints.
- `Definition.UnmarshalVT` decodes repeated raw `def` byte blobs, a `map[string]*OpMetadata`, and optional `Source`. `def` entries are copied into newly allocated byte slices, so they do not alias the input buffer.
- `FileOp.UnmarshalVT` appends repeated `*FileAction` entries.
- `FileAction.UnmarshalVT` decodes numeric input/output indices and the oneof action variants: copy, mkfile, mkdir, rm, and symlink.
- `FileActionCopy.UnmarshalVT` handles copy options including source/destination paths, optional owner, mode/mode string, symlink handling, directory behavior, Docker archive unpack compatibility, destination creation, wildcard behavior, timestamp, include/exclude patterns, replacement behavior, and required paths.
- `FileActionMkFile`, `FileActionSymlink`, `FileActionMkDir`, and `FileActionRm` decode their operation-specific payloads plus optional owner/timestamp fields where applicable.
- `ChownOpt`, `UserOpt`, and `NamedUserOpt` decode ownership overrides. `UserOpt` is a oneof between a named user with an input index and a numeric ID.
- `MergeInput`/`MergeOp`, `LowerDiffInput`/`UpperDiffInput`/`DiffOp`, and `PassthroughOp` decode graph-composition operations. `PassthroughOp.outputs` accepts both packed and unpacked repeated varints.

## Control Flow

Every method follows the same vtprotobuf pattern:

1. Iterate through `dAtA` with `iNdEx < l`.
2. Decode a varint tag into `wire`, split it into `fieldNum` and `wireType`.
3. Reject end-group wire type and non-positive field numbers.
4. Switch on `fieldNum`, validate the expected wire type, decode the field, and advance `iNdEx`.
5. For unknown fields, reset to `preIndex`, call `protohelpers.Skip`, bounds-check the skipped range, append the bytes to `m.unknownFields`, and continue.
6. Return `io.ErrUnexpectedEOF`, `protohelpers.ErrIntOverflow`, or `protohelpers.ErrInvalidLength` on malformed input.

Nested messages are length-delimited, allocated lazily, and decoded by calling their own `UnmarshalVT`. Repeated message fields append new pointers before recursive decode. Repeated string fields append decoded strings. Oneof fields reuse the existing concrete oneof value if it already matches the incoming field, otherwise allocate a fresh payload and replace the oneof.

## State And Persistence Behavior

The decoder mutates the receiver in place. Scalar fields are generally reset to zero before varint accumulation, but repeated fields append to any existing slice. Nested pointer fields are allocated only when the serialized field is present; if a pointer already exists, decoding merges into it. Unknown fields are preserved by appending raw wire bytes to the receiver's protobuf unknown field storage.

`Definition.Def` is deep-copied from the input buffer. `FileActionMkFile.Data` is copied with `append(m.Data[:0], ...)`, which can reuse the receiver's existing capacity but does not retain an alias into `dAtA`. Strings are created from byte slices, so they allocate immutable Go strings. `PassthroughOp.Outputs` preallocates capacity for packed values by counting terminating varint bytes when the output slice is currently empty.

There is no external persistence, I/O, locking, or caching in this chunk. The persistent state is the in-memory protobuf message graph produced from serialized input.

## Dependencies

The chunk depends on:

- `github.com/planetscale/vtprotobuf/protohelpers` for skipping unknown fields and common protobuf decode errors.
- `io` for `io.ErrUnexpectedEOF`.
- `fmt` for malformed-wire error messages.
- Other generated message methods in the same file, such as `OpMetadata.UnmarshalVT` and `Source.UnmarshalVT`, when decoding nested messages.
- Schema/type definitions from `ops.proto` and `ops.pb.go`.

Integration with hand-written code is visible in `json.go`, which customizes JSON encoding for `Op`, `FileAction`, and `UserOpt`, and in `caps.go`, which declares capability IDs for `meta.exportcache`, `exec.meta.linux.resources`, `mergeop`, `diffop`, and `passthroughop`.

## Integration Points

`Definition` is the serialized LLB graph container and appears in `BuildOp` and `SourceInfo`. Any solver path that receives or stores LLB definitions depends on this decoder preserving raw op bytes, metadata map entries, and source mappings correctly.

`FileOp` and `FileAction` are integrated with BuildKit filesystem operations. `FileAction` comments explicitly say changes must be represented in `json.go`, making JSON/protobuf parity an integration contract. The vtprotobuf path supports the symlink oneof, while the current custom JSON helper lists copy, mkfile, mkdir, and rm but not symlink.

`WorkerConstraints`, `ProxyEnv`, `ProgressGroup`, `ExportCache`, and `LinuxResources` are metadata/control-plane types. They influence worker selection, environment propagation, UI/progress grouping, cache export behavior, and runtime resource limits rather than directly describing filesystem snapshots.

`MergeOp`, `DiffOp`, and `PassthroughOp` are graph operation variants selected by the top-level `Op` oneof decoded earlier in the file. They must remain wire-compatible with capability checks in `caps.go` and with clients that may send either packed or unpacked repeated `outputs`.

## Risks

- Because this file is generated, direct edits are fragile and will be overwritten. Schema-level changes must update `ops.proto`, regenerate `ops.pb.go` and `ops_vtproto.pb.go`, and keep `json.go` in sync where comments require it.
- In-place decode semantics mean reusing a non-empty receiver can append repeated fields and unknown fields instead of replacing them. Callers expecting a clean decode should reset or allocate a fresh message first.
- Oneof merge behavior can be subtle: duplicate same-variant oneof fields merge into the existing payload, while a different oneof field replaces the active variant.
- The decoder performs wire-level validation and length checks, but it does not enforce semantic validity such as valid paths, safe wildcard patterns, meaningful resource limits, valid cpuset syntax, or non-empty metadata digest keys.
- Signed integer fields are decoded as plain proto3 varints. Negative values are legal at the wire/type level but expensive on the wire and require downstream semantic handling.
- `Definition.Metadata` assigns `m.Metadata[mapkey] = mapvalue` even if a malformed map entry omits key or value but remains wire-valid. Downstream code should not assume non-empty keys or non-nil values solely because the map exists.
- The hand-written JSON adapter appears to omit `FileAction_Symlink`, so JSON round-trip coverage may lag protobuf/vtprotobuf support for that oneof.

## Test Signals

Direct tests for generated `UnmarshalVT` methods are not present in this chunk. Useful signals are:

- `sources/cloud-native/buildkit/solver/pb/json_test.go` covers JSON round trips for top-level `Op` variants including file, build, merge, and diff; file action variants copy, mkfile, mkdir, and rm; and `UserOpt` by-name/by-ID behavior.
- `json_test.go` does not cover `FileAction_Symlink`, `PassthroughOp`, `LinuxResources`, `ProxyEnv`, `ProgressGroup`, `ExportCache`, `Definition.Metadata`, packed/unpacked `PassthroughOp.Outputs`, malformed wire data, or receiver reuse semantics.
- Regeneration consistency is a key test signal: generated vtprotobuf methods should match `ops.proto` field numbers and `ops.pb.go` types exactly.
- Fuzzing or table tests around malformed varints, truncated length-delimited fields, unknown fields, duplicate oneof fields, map entries missing key/value, and packed/unpacked repeated outputs would exercise the main error and compatibility paths in this chunk.
