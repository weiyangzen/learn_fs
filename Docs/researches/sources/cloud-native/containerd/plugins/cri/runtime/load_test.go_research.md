# sources/cloud-native/containerd/plugins/cri/runtime/load_test.go

## Purpose
Validates preloading of base OCI runtime specs referenced from CRI runtime configuration.

## Important APIs, Types, And Functions
`TestLoadBaseOCISpec` writes a JSON `oci.Spec`, configures a runtime with `BaseRuntimeSpec`, calls `loadBaseOCISpecs`, and asserts the spec map contains the loaded version and hostname.

## Control Flow
The test creates a temporary file, JSON-encodes a minimal spec, builds `criconfig.Config.Runtimes`, loads specs, then checks the returned map by filename.

## State And Persistence
Uses a temporary file only. It verifies file-backed config input becomes an in-memory cache for `runtime.LoadOCISpec`.

## Dependencies And Integration Points
Depends on `criconfig`, `pkg/oci`, JSON encoding, and `testify`. It directly exercises helpers from `runtime/plugin.go`.

## Risks
It does not cover duplicate spec paths, malformed JSON, missing files, or `runtime.LoadOCISpec` not-found behavior.

## Test Signals
Provides a focused startup-cache regression for the base OCI spec loading path.
