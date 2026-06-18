# sources/cloud-native/nydus/contrib/nydusify/pkg/backend/backend.go

## Purpose
This file defines the backend abstraction used by nydusify to upload, check, and read Nydus blob artifacts from registry, OSS, or S3 storage.

## Important APIs, Types, and Functions
`Backend` is the central interface with `Upload`, `Finalize`, `Check`, `Type`, `Reader`, `RangeReader`, and `Size`. Backend type constants are `OssBackend`, `RegistryBackend`, and `S3backend`. `blobDesc` builds OCI descriptors for Nydus blobs. `NewBackend` selects concrete implementations from a backend type string.

## Control Flow
Callers create a backend via `NewBackend`, upload blobs through `Upload`, optionally finalize or cancel pending state, and use checks/readers when validating or building cache. `blobDesc` consistently annotates descriptors with uncompressed digest and Nydus blob marker.

## State, Persistence, and Dependencies
This abstraction has no concrete state. It depends on containerd remote range reader interfaces, OCI descriptors, digest helpers, local remote package, and media annotation constants from `utils`.

## Integration Points
Converter/cache/checker flows depend on this interface to abstract storage. Registry uses OCI distribution; OSS and S3 use object storage and expose remote URLs in descriptors.

## Risks and Test Signals
Concrete backends do not implement all methods equally; registry reader methods panic. The type string switch must stay aligned with CLI validation. Tests cover descriptor creation and constructor dispatch for oss, s3, registry, and unsupported backends.
