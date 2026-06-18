# sources/cloud-native/containerd/internal/cri/nri/nri_api_other.go

## Purpose

This non-Linux file provides a no-op NRI API implementation for unsupported platforms while preserving the same CRI integration surface.

## Important APIs, Types, and Functions

`API` is an empty struct. `NewAPI` returns nil, while methods on nil/empty API values provide disabled behavior where callers keep a typed field. `Register` returns nil and `IsEnabled` returns false. All lifecycle hooks return nil or no adjustment. `WithContainerAdjustment` and `WithContainerExit` return no-op containerd options. `PluginSyncBlock` has a no-op `Unblock`, and `BlockPluginSync` returns nil. Domain methods return the Kubernetes containerd domain name plus empty lists/lookups or nil update/evict errors.

## Control Flow

All methods immediately return without side effects. `UpdateContainerResources` returns the request resources unchanged.

## State and Persistence Behavior

No state is stored or persisted. No CRI stores are read or mutated.

## Dependencies and Integration Points

It is selected by `//go:build !linux` and lets platform-independent CRI code call `c.nri.*` without build-tag conditionals.

## Risks and Edge Cases

Feature parity differs by platform: NRI plugins are effectively unavailable outside Linux. Callers must not assume `BlockPluginSync` returns a non-nil block or that NRI lifecycle failures can occur.

## Test Signals

Non-Linux builds should compile and tests should verify NRI calls are no-ops, especially container creation options and resource update pass-through.
