# sources/distributed-fs/juicefs/pkg/object/prefix.go

Purpose: provides `WithPrefix`, a transparent `ObjectStorage` decorator that roots all key-based operations under a prefix, plus helpers for deriving parent-directory storage and detecting filesystem-like stores.

Important APIs and types: `withPrefix` wraps an `ObjectStorage`; `WithPrefix` constructs it; `DirStorage` unwraps encryption layers and converts file-like roots to parent directories; `withFile` and `withObj` adapt returned `File`/`Object` instances so `Key()` is relative to the prefix while preserving `Sys()` when available. The wrapper implements normal object methods, multipart, filesystem extension methods (`Chmod`, `Chown`, `Chtimes`), symlink methods, stream upload, restore, and tier support pass-through.

Control flow and state: mutating and lookup methods prepend `p.prefix` before delegating. `Head`, `List`, and `ListAll` call `updateKey` to strip the prefix from returned keys; for known concrete objects it mutates the key, otherwise it wraps the object. `Get` rejects the invalid range combination `off > 0 && limit < 0`. `Copy` delegates without prefixing, while `UploadPartCopy` prefixes both source and destination keys.

Persistence and integration: it changes namespace mapping only; persistence remains in the wrapped backend. It integrates with encryption wrappers, `filestore`, tier, symlink, and filesystem optional interfaces.

Risks and test signals: `Copy` not prefixing differs from most key operations and relies on callers supplying already-correct keys. `ListAll` uses a goroutine and fixed 10240 buffer, so slow consumers retain memory. Tests in `prefix_test.go` cover `DirStorage` directory/file prefix handling and filestore roots.
