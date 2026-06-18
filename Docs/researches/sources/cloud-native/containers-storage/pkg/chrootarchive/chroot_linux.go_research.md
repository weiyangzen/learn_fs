<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/chroot_linux.go -->
# sources/cloud-native/containers-storage/pkg/chrootarchive/chroot_linux.go

Purpose: Linux root-switch implementation for chrootarchive child processes, preferring `pivot_root` in a private mount namespace and falling back to `chroot`.

Important APIs/types/functions: `chroot` and `realChroot`.

Control flow: loads process capabilities, preloads NSS lookups outside the chroot, uses `realChroot` when only `CAP_SYS_CHROOT` is available, otherwise unshares mount namespace, makes `/` private, bind-mounts the target root if needed, creates `.pivot_root`, calls `unix.PivotRoot`, changes to `/`, makes old root private, unmounts it, and cleans up the pivot dir. `realChroot` calls `unix.Chroot` then `Chdir("/")`.

State/persistence: creates/removes a temporary pivot directory and may add a bind mount/mount namespace state inside the child process. It changes the process root and cwd.

Dependencies/integration: used by reexec children in `archive_unix.go` and `diff_unix.go`. Depends on `mount`, Linux capabilities, NSS preloading, and `x/sys/unix`.

Risks: mount namespace and pivot cleanup are subtle. Failure paths fall back to chroot only after cleanup. If old root is not unmounted, extraction could see host paths. NSS preloading avoids loading attacker-controlled libraries/config from the new root.

Test signals: exercised indirectly by chrootarchive tests and malicious symlink tests on Linux.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/chroot_linux.go -->
