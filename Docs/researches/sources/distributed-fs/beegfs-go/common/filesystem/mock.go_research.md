<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/mock.go -->
# sources/distributed-fs/beegfs-go/common/filesystem/mock.go

Purpose: in-memory/mock implementation of `Provider` for tests that need basic file operations without a mounted BeeGFS filesystem.

Important APIs/types/functions: `NewMockFS`, `MockFS`, and implementations for mount path, relative path, stat, create/write/read/remove/open/ranged I/O. Many advanced provider methods return `"not implemented"`.

Control flow: uses `afero.NewMemMapFs`; implemented methods delegate to Afero and shared ranged I/O helpers. `Lstat`, directory creation/walking, metadata copy, overwrite, and readlink are placeholders.

State and persistence: stores files in an in-memory Afero filesystem. No durable persistence.

Dependencies and integration points: depends on `github.com/spf13/afero` and the `Provider` interface. Useful for callers that only need simple file reads/writes in tests.

Risks: incomplete `Provider` implementation can fail when tests use newer filesystem features. `CreatePreallocatedFile` ignores `overwrite` semantics and uses `Create`, so behavior differs from real BeeGFS. `Lstat` is not implemented, which prevents filter/walk flows using this mock.

Test signals: indirectly used by external tests if any; no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/mock.go -->
