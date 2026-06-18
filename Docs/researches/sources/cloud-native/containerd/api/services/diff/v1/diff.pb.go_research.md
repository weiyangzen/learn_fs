# sources/cloud-native/containerd/api/services/diff/v1/diff.pb.go

Generated Go protobuf bindings for the Diff service. It defines request/response message structs, nil-safe getters, descriptor metadata, and reflection initialization for filesystem diff apply/create operations.

Important APIs are `ApplyRequest`, `ApplyResponse`, `DiffRequest`, `DiffResponse`, and `File_services_diff_v1_diff_proto`. `ApplyRequest` carries a content `Descriptor`, target `Mount` list, arbitrary `Any` payloads, and `sync_fs`. `DiffRequest` carries left/right mount sets, media type, pre-commit content ref, labels, and `source_date_epoch`. Responses return descriptors for applied or generated diff content.

Control flow is generated message plumbing: `Reset`, `String`, `ProtoReflect`, deprecated descriptors, getters, raw descriptor compression through `sync.Once`, unsafe-disabled exporters, and `protoimpl.TypeBuilder` setup. There is no service execution logic in this file.

State is limited to message fields and package-level descriptor caches. Persistence is external: generated diff content is stored through the content store using refs/descriptors. Dependencies include containerd API `types.Descriptor` and `types.Mount`, protobuf runtime/reflection, `anypb`, `timestamppb`, `reflect`, and `sync`.

Integration points include diff service implementations, content storage, snapshot/mount handling, archive decompression/apply code, reproducible build timestamp handling, and generated transports. Risks include treating request descriptors/mounts as validated, mishandling `sync_fs` cost/semantics, timestamp reproducibility edge cases, and generated descriptor drift. Test signals should cover proto round trips, map payload preservation, descriptor field numbers, apply/diff service validation, and regeneration from `diff.proto`.
