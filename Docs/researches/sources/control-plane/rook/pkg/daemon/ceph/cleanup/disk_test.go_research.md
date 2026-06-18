<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/disk_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/cleanup/disk_test.go

Purpose: unit tests for disk sanitizer command construction.

Important APIs/types/functions: `TestBuildDataSource` verifies `/dev/zero`; `TestBuildShredCommands` table-tests quick and complete sanitize methods using `DiskSanitizer.buildShredCommands`.

Control flow: tests build a mock `clusterd.Context`, create sanitize specs, and compare resulting `ShredCommand` slices with expected `ceph-volume lvm zap` or `shred` arguments.

State and persistence behavior: no disks are modified. Mock executor stubs unrelated lsblk/sgdisk calls but the tested functions mostly avoid command execution.

Dependencies and integration points: depends on cleanup command builders, Ceph API sanitize enum values, Rook exec test helpers, and testify/assert.

Risks: tests do not cover actual `StartSanitizeDisks`, goroutine behavior, encrypted devices, LVM PV parsing, or command-execution error paths.

Test signals: protects user-visible sanitize method/data-source translation, especially `--random-source=/dev/zero`, `--zero`, iteration count, and quick-mode zap behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/disk_test.go -->
