# sources/cloud-native/nydus/contrib/nydusify/pkg/backend/registry.go

## Purpose
This file implements the registry backend for storing Nydus blobs as OCI/distribution blob layers.

## Important APIs, Types, and Functions
`Registry` wraps a `remote.Remote`. Methods implement `Upload`, `Finalize`, `Check`, `Type`, and placeholder `RangeReader`, `Reader`, and `Size` methods that panic.

## Control Flow
`Upload` builds a Nydus blob descriptor, opens the blob file, and pushes it through `remote.Push` by digest. `Finalize` is a no-op. `Check` returns true without remote verification. `newRegistryBackend` creates the wrapper.

## State, Persistence, and Dependencies
Persistent state is the remote registry blob store. Local state is just the remote handle. Dependencies include OCI descriptors, containerd range reader interfaces, local `remote`, and filesystem open.

## Integration Points
This is the default backend for nydusify cache and conversion when storing blobs in registry manifests. It uses the same descriptor annotations as other backends.

## Risks and Test Signals
`Check` returning true can mask missing blobs. Reader methods panic, so callers must avoid using registry backend for direct object reads. `forcePush` is ignored because registries do not allow overwriting existing blobs. Tests cover upload success/failure via monkeypatched remote push, helpers, constructor, and panic behavior.
