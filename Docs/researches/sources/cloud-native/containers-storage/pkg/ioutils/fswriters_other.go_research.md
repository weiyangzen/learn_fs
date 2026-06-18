# sources/cloud-native/containers-storage/pkg/ioutils/fswriters_other.go

Purpose: provides non-Linux sync hooks for the atomic file writer.

Important APIs, types, and functions: `dataOrFullSync`, `(*atomicFileWriter).postDataWrittenSync`, and `(*atomicFileWriter).preRenameSync`.

Control flow: `dataOrFullSync` calls `f.Sync`. `postDataWrittenSync` does nothing because platforms such as macOS and Windows may require a full sync instead. `preRenameSync` performs the full sync unless `NoSync` is set.

State and persistence: controls how staged file data is pushed to storage before publishing with rename on non-Linux systems. It does not manage directory-level persistence.

Dependencies and integration points: depends only on `os` and is selected for `!linux`. `fswriters.go` calls these methods through the same `atomicFileWriter` path used on all platforms.

Risks and edge cases: full file sync can be more expensive than Linux fdatasync. Platform differences around rename-after-open are handled by closing in common code before rename. The behavior relies on `os.File.Sync` mapping to the correct platform primitive.

Test signals: cross-platform functional tests in `fswriters_test.go` verify commit semantics and file modes, but not power-loss durability.
