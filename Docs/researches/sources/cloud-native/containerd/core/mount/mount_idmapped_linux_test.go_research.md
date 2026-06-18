<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_idmapped_linux_test.go -->
# sources/cloud-native/containerd/core/mount/mount_idmapped_linux_test.go

Purpose: root/kernel-gated tests and benchmarks for Linux idmapped mount support.

Important APIs/types/functions: benchmarks for concurrent `getUsernsFD`; `TestIdmappedMount` with subtests `GetUsernsFD`, `IDMapMount`, and `IDMapMountWithAttrs`; helper `initIDMappedChecker`.

Control flow: tests skip unless root and kernel >= 5.12. They create files owned by container IDs, mount through an idmapped user namespace, then verify host-side uid/gid values at the destination. Read-only attribute tests assert writes fail with `EROFS`.

State and persistence: creates real user namespaces, idmapped mount trees, temp files, and mount targets; cleanup unmounts with `UnmountAll`.

Dependencies and integration points: validates the lower-level functions used by `mount_linux.go` when `uidmap`/`gidmap` options are present.

Risks covered: invalid negative mapping components fail; concurrent namespace FD creation is benchmarked; read-only mount attributes are enforced. Tests are environment-sensitive and skip on unsupported kernels/filesystems.

Test signals: strong integration coverage for kernel idmap behavior; does not explicitly test zero-size mapping or partial syscall failure cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_idmapped_linux_test.go -->
