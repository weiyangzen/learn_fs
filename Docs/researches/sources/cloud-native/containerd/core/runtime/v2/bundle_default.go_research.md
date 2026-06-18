# sources/cloud-native/containerd/core/runtime/v2/bundle_default.go

## Purpose
Provides the non-Linux implementation of `prepareBundleDirectoryPermissions`, making bundle permission adjustment a no-op on platforms without Linux user namespace GID remapping behavior.

## APIs, Flow, State, Dependencies, Risks, And Tests
The only API is `prepareBundleDirectoryPermissions(path string, spec []byte) error`, compiled with `//go:build !linux`. It returns nil without inspecting the path or spec. There is no control flow beyond the return, no state mutation, and no persistence.

The file exists so `bundle.go` can call the same function on every platform while Linux-specific ownership/chmod logic lives in `bundle_linux.go`. It has no imports and integrates through Go build tags.

The main risk is assuming Linux-style access fixes happen on other platforms; this file deliberately does nothing, so platform-specific user namespace support would need its own implementation. Test signals are cross-platform compilation and bundle tests that import shared test utilities on all platforms.
