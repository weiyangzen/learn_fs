# sources/distributed-fs/ceph-client/fs/coda/pioctl.c

Purpose: implements the Coda control inode ioctl path, allowing userspace pioctl requests to target a path inside the same Coda mount and be forwarded to Venus.

Important APIs/functions: exports `coda_ioctl_inode_operations` with `.permission` and `.setattr`, plus `coda_ioctl_operations` with `.unlocked_ioctl = coda_pioctl`. `coda_ioctl_permission()` denies execute access but permits non-exec permission checks. `coda_pioctl()` copies `struct PioctlData` from userspace, resolves the embedded path with optional follow semantics, validates the target inode belongs to the same superblock, then calls `venus_pioctl()`.

Control flow: ioctl input arrives on the special pioctl file; the code copies the fixed control block, calls `user_path_at(AT_FDCWD, data.path, ...)`, rejects non-Coda or different-mount targets, extracts the target fid from `ITOC(target_inode)`, performs the Venus upcall, and releases the path.

State and persistence: no persistent local state. Effects are delegated to Venus through `venus_pioctl()`, which may read and write userspace buffers described in `PioctlData`.

Dependencies/integration: integrates VFS ioctl operations, userspace path lookup, `linux/coda.h` pioctl ABI, `coda_inode_info`, and the generic Coda upcall transport. It relies on path lookup to safely copy the user pathname from `data.path`.

Risks: `copy_from_user()` returns `-EINVAL` rather than `-EFAULT`, which is ABI behavior but less precise. The path must remain on the same Coda superblock or foreign inode fids could be sent to the wrong Venus. The command-size rewriting and data-buffer validation happen later in `venus_pioctl()`, so both pieces must stay ABI-compatible.

Test signals: ioctl with bad user pointer, missing path, follow/no-follow symlink cases, path on another filesystem, same Coda mount success, overlarge in/out pioctl buffers via `venus_pioctl()`, and permission checks on the control inode.
