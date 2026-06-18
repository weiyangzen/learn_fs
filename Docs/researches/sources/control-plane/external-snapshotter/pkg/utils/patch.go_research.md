# sources/control-plane/external-snapshotter/pkg/utils/patch.go

Purpose: centralizes JSON Patch operations for snapshot and group snapshot CRDs, including optional subresources such as `status`.

Important APIs/types/functions: `PatchOp`, `PatchVolumeSnapshotContent`, `PatchVolumeSnapshot`, `PatchVolumeGroupSnapshot`, and `PatchVolumeGroupSnapshotContent`.

Control flow: each function marshals a slice of `PatchOp` to JSON, calls the generated client `Patch` method with `types.JSONPatchType`, passes optional subresources through, and returns either the patched object or the original object on error.

State and persistence: persists metadata/spec/status mutations to the Kubernetes API server through generated clients. It uses `context.TODO()` and does not apply retries itself.

Dependencies and integration: consumed heavily by controllers for finalizer, annotation, and status updates. Depends on generated snapshot clientsets, API machinery patch types, and JSON encoding.

Risks and test signals: risks include invalid JSON pointer escaping at call sites, replacing missing paths, lack of context cancellation, and caller confusion from returning the original object on errors. No direct tests in this subset cover patch helper behavior.
