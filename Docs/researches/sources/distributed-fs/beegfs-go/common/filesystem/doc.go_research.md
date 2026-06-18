<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/doc.go -->
# sources/distributed-fs/beegfs-go/common/filesystem/doc.go

Purpose: package documentation for the filesystem abstraction.

Important APIs/types/functions: no executable APIs; documents `filesystem.Provider`, `New`/mount initialization pattern, and optional singleton-style usage by applications.

Control flow: none.

State and persistence: none.

Dependencies and integration points: explains how applications initialize BeeGFS or mock providers and references logger behavior in example text.

Risks: documentation mentions a `New()` function and `MountPoint` global, while this subset shows `NewFromMountPoint`/`NewFromPath`; doc drift should be checked against the rest of the package.

Test signals: no tests; documentation only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/doc.go -->
