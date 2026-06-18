<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/init_syscalls.h -->
# sources/distributed-fs/ceph-client/include/linux/init_syscalls.h

Purpose: Declares syscall-like helpers used by kernel init code before userspace exists.

Important APIs/types/functions: Init-only helpers include `init_mount()`, `init_umount()`, `init_chdir()`, `init_chroot()`, `init_chown()`, `init_chmod()`, `init_eaccess()`, `init_stat()`, `init_mknod()`, `init_link()`, `init_symlink()`, `init_unlink()`, `init_mkdir()`, `init_rmdir()`, `init_utimes()`, `init_dup()`, and `init_pivot_root()`.

Control flow: Early init/rootfs code calls these wrappers to build or switch root filesystem state.

State/persistence: Operations mutate VFS namespace, files, directories, modes, ownership, and mounts.

Dependencies/integration: Integrates init, VFS, mount, namespace, and credential behavior.

Risks: These helpers run in privileged init context; errors can prevent boot or corrupt initramfs setup.

Test signals: Initramfs boot, root mount/unmount, namespace setup, file mode/ownership operations, and error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/init_syscalls.h -->
