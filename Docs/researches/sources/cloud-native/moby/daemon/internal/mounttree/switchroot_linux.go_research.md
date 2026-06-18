<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/mounttree/switchroot_linux.go -->
# sources/cloud-native/moby/daemon/internal/mounttree/switchroot_linux.go

Purpose: switches the current process into a new root mount tree using `pivot_root` when possible, falling back to `chroot`.

Important APIs and types: `SwitchRoot(path string) error` and `realChroot`.

Control flow: if `path` is not already mounted, it tries an rbind mount onto itself and falls back to `chroot` if that fails. It creates a temporary pivot directory under the new root, calls `unix.PivotRoot`, changes directory to `/`, makes the old-root mount private, detach-unmounts it, and removes the temporary directory. On pivot failure it removes the temp dir and falls back to chroot.

State and persistence: mutates the calling process root, cwd, and mount namespace. Temporary pivot directory is removed during cleanup.

Dependencies and integration: depends on `moby/sys/mount`, `mountinfo`, and Linux `unix` syscalls. Used for extraction or daemon operations that need a temporary root tree.

Risks: this is process/mount-namespace destructive and must be called in the correct isolated context. Deferred cleanup writes to the named return `err` pattern imperfectly because `SwitchRoot` does not use a named return; cleanup errors may not propagate in all paths. Propagation mode must be prepared by caller.

Test signals: no direct tests in this subset; requires privileged namespace integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/mounttree/switchroot_linux.go -->
