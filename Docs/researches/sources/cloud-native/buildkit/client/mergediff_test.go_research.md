# sources/cloud-native/buildkit/client/mergediff_test.go

## Purpose
This integration-test source builds the merge/diff regression matrix for BuildKit LLB states. `diffOpTestCases` returns `integration.Test` cases that assert `llb.Diff`, `llb.Merge`, file operations, exec-root diffs, exec mount diffs, lazy image blobs, symlinks, hardlinks, opaque whiteouts, and nested merge graphs produce the expected filesystem result and cache behavior.

## Important APIs, Types, and Functions
- `diffOpTestCases() []integration.Test` is the entry point consumed by the broader client integration test suite.
- `verifyContents` implements `integration.Test` and solves an LLB state, exports it locally or as an image, then checks the on-disk content with `fstest` appliers.
- `verifyBlobReuse` asserts that single-layer diff exports reuse an existing layer blob instead of creating a new content blob.
- `contents`, `applyFn`, `contentsOf`, `apply`, `mergeContents`, and `empty` provide a small adapter layer between `llb.State` outputs and `fstest.Applier` assertions.
- `resetState` removes images from the buildkit containerd namespace and calls `checkAllReleasable` so cache and image state do not leak between cases.

## Control Flow
`diffOpTestCases` constructs reusable base states from `alpine` and `busybox`, appends many `verifyContents` and `verifyBlobReuse` values, and returns them to the integration runner. Each `verifyContents.Run` checks feature support, starts a client, obtains a registry, exports the result, optionally imports inline or registry cache, and validates both direct output contents and cache reimport contents. Containerd-backed runs additionally inspect image manifests and layer presence to ensure cache imports do not leave unexpected layer blobs in the worker content store.

## State and Persistence Behavior
The tests intentionally mutate BuildKit daemon state, a temporary registry, the containerd image service, and local output directories. `resetState` is critical persistence hygiene: without it, prior images and blobs could hide cache misses or make content-store reachability checks pass for the wrong reason. The tested persistent artifacts are OCI/Docker image manifests, layer blobs, registry cache exports, and local filesystem outputs.

## Dependencies and Integration Points
The file integrates with `client.Solve`, `llb` graph construction, containerd image/content APIs, the integration sandbox, worker feature gates, `fstest`, registries, and cache import/export options. It depends on Linux behavior for overlay whiteouts, device nodes, hardlinks, symlink traversal, and snapshotter semantics. Some checks require a containerd worker and are skipped for dockerd/rootless cases where the assertions are not meaningful.

## Risks and Edge Cases
The test matrix protects fragile behavior: empty diffs, scratch lower/upper states, file-vs-directory replacement, explicit whiteout conversion, unmatched deletes, deletes after merge, shuffled files that should not create diffs, FIFOs and character devices, symlink override/delete behavior, circular symlinks, hardlink copy-up semantics, diff-of-diff graphs, layered merge deletes, and opaque directory regressions. The risk is mostly environmental flakiness: registry availability, rootless limitations, containerd access, and platform-specific filesystem behavior.

## Test Signals
The file itself is a broad test signal. Passing cases show that `llb.Diff` and `llb.Merge` preserve user-visible filesystem semantics and cache equivalence across direct solves, inline cache, registry cache, and image-content validation. Failures usually indicate a differ, merge-op, exporter, or cache-import regression rather than a narrow client API failure.
