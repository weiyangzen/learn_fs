# sources/control-plane/juicefs-csi-driver/pkg/dashboard/utils.go

## Purpose
This package-level utility file provides sorting adapters, mount-pod label selectors, job owner references, secret-name parsing, PVC selector checks, YAML/debug file writing, zipping, and safe-ish path component normalization for dashboard handlers.

## Important APIs, Types, And Functions
It defines `ReverseSort`, `Reverse`, `LabelSelectorOfMount`, `isShareMount`, `SetJobAsConfigMapOwner`, `getUniqueIdFromSecretName`, `IsPVCSelectorEmpty`, `DownloadYaml`, `ZipDir`, and `StripDir`.

## Control Flow
Sorting wraps another `sort.Interface` with inverted `Less`. Mount selectors match `common.PodUniqueIdLabelKey` against PV volume handle and optionally storage class. Download helpers restrict target paths to `/tmp`, marshal YAML, and write through buffered IO. `ZipDir` walks a source directory and writes a deflated zip to a `/tmp` target. `StripDir` replaces path separators and `..` with dashes.

## State And Persistence
`DownloadYaml` and `ZipDir` write local files under `/tmp`; other helpers are stateless. `SetJobAsConfigMapOwner` mutates the provided ConfigMap object in memory before the caller updates Kubernetes.

## Dependencies And Integration Points
Used by PV/pod/batch handlers for sorting, relationship lookup, debug bundle generation, and upgrade ConfigMap ownership. It depends on Kubernetes core/batch/meta types and `sigs.k8s.io/yaml`.

## Risks
The `/tmp` prefix check uses string prefix rather than cleaned path boundary, so paths like `/tmpx` would pass even though they are outside `/tmp` semantically. `isShareMount` assumes at least one container. `ZipDir` can include the root directory entry as `./` and follows `filepath.Walk` behavior without symlink-specific controls.

## Test Signals
`utils_test.go` covers reverse sorting, empty PVC selector detection for an empty struct, and `StripDir` replacement behavior.
