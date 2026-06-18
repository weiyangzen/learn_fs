<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/chroot_unix.go -->
# sources/cloud-native/containers-storage/pkg/chrootarchive/chroot_unix.go

Purpose: non-Linux/non-Darwin Unix chroot implementation.

Important APIs/types/functions: `realChroot` and `chroot`.

Control flow: `realChroot` calls `unix.Chroot(path)` then `unix.Chdir("/")`; `chroot` delegates to `realChroot`.

State/persistence: changes process root and current working directory in the reexec child.

Dependencies/integration: used by `archive_unix.go` and `diff_unix.go` on supported Unix platforms without Linux pivot_root implementation.

Risks/test signal: weaker than Linux pivot_root because the old root is not explicitly unmounted. Correctness depends on OS chroot behavior and child process isolation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/chroot_unix.go -->
