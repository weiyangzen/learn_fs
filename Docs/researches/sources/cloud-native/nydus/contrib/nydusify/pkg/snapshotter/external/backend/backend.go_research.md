# sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/backend/backend.go

Purpose: defines shared data contracts for external snapshotter backend generation and file/chunk metadata.

Important APIs/types/functions: `Backend`, `Config`, `Blob`, `BlobConfig`, `Result`, `FileAttribute`, `File`, `Handler`, `RemoteHanlder`, `Chunk`, and `SplitObjectOffsets`.

Control flow: handlers return backend configuration and chunks for files. Remote handlers return backend configuration plus file attributes. `SplitObjectOffsets` computes zero-based offsets for fixed-size chunks, returning empty for non-positive chunk size or zero total size, and including a final partial offset when needed.

State and persistence: structs are JSON-serializable where tagged and are used as metadata records; no persistence is implemented here.

Dependencies and integration points: modctl local/remote handlers, snapshotter external generator/walker code elsewhere, and external backend metadata layout.

Risks and test signals: `RemoteHanlder` is misspelled in the type name but part of the package API. `FileAttribute` lacks JSON tags, so encoding relies on default field names if used directly.
