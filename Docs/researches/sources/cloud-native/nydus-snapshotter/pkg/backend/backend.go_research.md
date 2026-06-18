# sources/cloud-native/nydus-snapshotter/pkg/backend/backend.go

Purpose: defines the blob storage backend abstraction and factory for nydus converter outputs.

Important APIs and functions: backend type constants `oss`, `s3`, and `localfs`; variable `MultipartChunkSize` defaults to 500 MiB; `Backend` interface defines `Push`, `Check`, `Type`, and `Size`; `NewBackend` dispatches to `newOSSBackend`, `newS3Backend`, or `newLocalFSBackend`.

Control flow: callers pass backend type, raw JSON config, and `forcePush`. Unsupported type returns an error. Implementations upload content-store descriptors and can check/size blobs by digest.

State and persistence: this file has only the multipart-size global. Actual persistence is in local filesystem, OSS, or S3 implementations.

Dependencies and integration points: mirrors the `converter.Backend` interface so converter options can use package backend implementations. Integrates with containerd `content.Store`, OCI descriptors, and digest types.

Risks: `MultipartChunkSize` is mutable package-global, which is convenient for tests/tuning but can affect all backend instances. Factory config is untyped raw JSON; validation is deferred to individual implementations.

Test signals: S3 config has a focused test; localfs and OSS behavior are not directly tested in listed files.
