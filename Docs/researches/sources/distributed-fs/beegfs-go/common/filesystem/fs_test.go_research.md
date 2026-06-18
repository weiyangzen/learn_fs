<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/fs_test.go -->
# sources/distributed-fs/beegfs-go/common/filesystem/fs_test.go

Purpose: filesystem-provider tests that do not require an actual BeeGFS mount.

Important APIs/types/functions: `tempPathForTesting`, `TestBeeGFSCreatePreallocatedFile`, and `TestBeeGFSWriteAndReadFileParts`.

Control flow: tests create temp directories under `/tmp`, instantiate `BeeGFS` with that path as `MountPoint`, create a sparse file, write fixed byte ranges through `WriteFilePart`, then read/checksum the full content.

State and persistence: creates and deletes temporary files/directories on local disk.

Dependencies and integration points: depends on `testify` and `BeeGFS` methods from `fs.go`/`common.go`.

Risks: tests do not exercise BeeGFS mount detection, xattrs, ownership/mode/timestamp copying, overwrite, walk behavior, or error paths for range overflow.

Test signals: useful coverage for the ranged I/O helpers and basic file creation semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/fs_test.go -->
