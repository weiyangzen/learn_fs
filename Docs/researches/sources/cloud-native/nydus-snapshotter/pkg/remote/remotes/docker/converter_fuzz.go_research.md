# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/converter_fuzz.go

## Purpose
Provides a go-fuzz entry point for `ConvertManifest`.

## Important APIs, Types, And Functions
`FuzzConvertManifest(data []byte) int` generates an OCI descriptor from fuzz input and invokes `ConvertManifest` against a local content store.

## Control Flow
The fuzzer suppresses warning logs, generates a descriptor, creates a temp directory, opens a containerd local store, calls `ConvertManifest`, ignores the result, and returns `1` if execution reached the converter.

## State And Persistence
Creates temporary local content store state. The code does not explicitly remove the temp directory, so fuzz runs may rely on the harness/environment for cleanup.

## Dependencies And Integration Points
Uses `go-fuzz-headers`, containerd local content store, OCI descriptors, and logrus log-level control.

## Risks And Edge Cases
The target mostly checks converter robustness for arbitrary descriptors and missing blobs. It does not validate semantic correctness of rewritten manifests.

## Test Signals
Useful for panic resistance around content reads, JSON unmarshalling, digest recalculation, and label generation paths.
