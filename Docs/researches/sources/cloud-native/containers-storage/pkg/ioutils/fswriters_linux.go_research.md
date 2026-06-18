# sources/cloud-native/containers-storage/pkg/ioutils/fswriters_linux.go

Purpose: supplies Linux-specific durability hooks for `atomicFileWriter` and write-set file closers.

Important APIs, types, and functions: `dataOrFullSync`, `(*atomicFileWriter).postDataWrittenSync`, and `(*atomicFileWriter).preRenameSync`.

Control flow: `dataOrFullSync` and `postDataWrittenSync` call `unix.Fdatasync` on the file descriptor unless `NoSync` skips the atomic writer's sync. `preRenameSync` is a no-op because Linux can flush data without doing a full file sync before rename.

State and persistence: affects how staged file contents reach stable storage before rename. It does not itself persist metadata beyond what the caller does with chmod, close, and rename.

Dependencies and integration points: depends on `os` and `golang.org/x/sys/unix`. It is selected on Linux and is called from `fswriters.go` during atomic commits and write-set close wrappers.

Risks and edge cases: fdatasync flushes data and required metadata but not every directory-entry guarantee; callers needing directory fsync are not covered here. Errors propagate and abort commit before rename.

Test signals: Linux behavior is indirectly exercised by `fswriters_test.go`; durability itself is not crash-tested, only functional content and mode behavior are verified.
