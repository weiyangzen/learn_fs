# sources/cloud-native/containerd/api/services/diff/v1/diff.proto

Protocol definition for the Diff service, which applies archive diffs onto mounts and creates new diff content from mount comparisons.

The service exposes two unary RPCs: `Apply(ApplyRequest) returns (ApplyResponse)` and `Diff(DiffRequest) returns (DiffResponse)`. `ApplyRequest` references the diff blob by `containerd.types.Descriptor`, target mounts, optional `Any` payloads, and a `sync_fs` flag. `DiffRequest` provides left and right mount sets, output media type, content-store ref, labels, and `source_date_epoch` for reproducibility. Responses return descriptors for the applied uncompressed content or generated diff.

Control flow is schema-level. Implementations are expected to fetch content by descriptor, decompress/extract when applying, compare mount trees when diffing, and commit generated content to the content store under the provided ref.

State and persistence are external but implied: content descriptors identify blobs, refs coordinate pre-commit uploads, and labels persist with generated content. Dependencies include protobuf `Any`/`Timestamp` plus containerd `Descriptor` and `Mount` types. Integration points include content service, snapshot mounts, archive apply/diff code, reproducible build tooling, and generated gRPC/ttrpc bindings.

Risks include unsafe mount handling, descriptor/content mismatch, expensive or partial `sync_fs`, reproducibility mismatches around source date epoch and whiteout timestamps, and labels/ref validation gaps. Test signals should include apply of compressed/uncompressed diffs, diff output media type and digest validation, source-date reproducibility, sync behavior, and invalid mount/descriptor errors.
