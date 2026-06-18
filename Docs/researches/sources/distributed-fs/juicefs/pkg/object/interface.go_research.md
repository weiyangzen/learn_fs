# sources/distributed-fs/juicefs/pkg/object/interface.go


Purpose: defines the central object-storage interfaces and shared object metadata structs.

Important APIs and flow: `Object` exposes key, size, mtime, directory/symlink flags, storage class, and status. `obj` is the default implementation. `MultipartUpload`, `Part`, `PendingPart`, and `Limits` standardize multipart capabilities. `ObjectStorage` defines idempotent storage operations, all context-first, including create, get, put, copy, delete, head, list, list-all, multipart lifecycle, and restore. `Shutdownable` plus `Shutdown` unwraps encrypted, chunked encrypted, prefix, and sharded wrappers to close underlying stores.

State and persistence: no persistent state itself; it specifies the contract all backends implement.

Dependencies and integration: imports only `context`, `io`, and `time`, but names wrapper types implemented elsewhere (`encrypted`, `chunkedEncrypted`, `withPrefix`, `sharded`) in `Shutdown`.

Risks: changing method signatures affects all providers; `context_cancellation_test.go` guards this. The interface combines simple stores with advanced multipart/restore features, so many implementations rely on `DefaultObjectStorage` unsupported defaults.

Test signals: reflection tests enforce context-first signatures; broad storage tests exercise behavior through this interface.
