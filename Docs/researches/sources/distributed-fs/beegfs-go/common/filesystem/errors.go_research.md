<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/errors.go -->
# sources/distributed-fs/beegfs-go/common/filesystem/errors.go

Purpose: sentinel errors for filesystem provider operations.

Important APIs/types/functions: `ErrNoSpaceForWrite`, `ErrUnmounted`, `ErrInitFSClient`, and `ErrUnsupportedFileSystem`.

Control flow: no flow; other package files wrap or return these errors.

State and persistence: none.

Dependencies and integration points: used by `limitedFileWriter`, `UnmountedFS`, `NewFromMountPoint`, and `NewFromPath`.

Risks: `ErrNoSpaceForWrite` includes a trailing space in its string, which can affect exact-message tests or UI output. Callers should use `errors.Is`.

Test signals: indirectly exercised by filesystem tests; no dedicated sentinel test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/errors.go -->
