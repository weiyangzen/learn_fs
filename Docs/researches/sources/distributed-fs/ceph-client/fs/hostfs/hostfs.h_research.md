# sources/distributed-fs/ceph-client/fs/hostfs/hostfs.h

Purpose: this header defines the ABI between the UML kernel-side hostfs implementation and the user-space syscall wrapper layer.

Important APIs and types: `struct hostfs_timespec`, `struct hostfs_iattr`, and `struct hostfs_stat` are wrapper-safe representations of timestamps, setattr input, and stat results. The prototypes cover stat/access/open/dir iteration/read/write/lseek/fsync/dup-close/create/setattr/symlink/unlink/mkdir/rmdir/mknod/link/readlink/rename/statfs. Attribute validity bits such as `HOSTFS_ATTR_MODE` are included through generated UML offsets.

Control flow role: `hostfs_kern.c` never directly calls libc syscalls; it builds host paths and delegates to these prototypes. `hostfs_user.c` implements the calls with host syscalls and converts errors to negative errno. `hostfs_user_exp.c` exports the symbols for GPL use.

State and persistence: the structs carry host metadata into VFS inode state and requested VFS changes back to host syscalls. Persistent effects happen when implementations call host filesystem operations.

Dependencies and integration: it includes `<os.h>` and `<generated/asm-offsets.h>`, marking it as UML-specific rather than generic kernel filesystem code. It is included by both kernel and user helper sources, so field layout changes affect both sides.

Risks: the header forms a narrow ABI; type or semantic drift can break inode identity, setattr, or statfs conversions. `hostfs_stat` includes both `dev/rdev` and birth time, which kernel code uses to distinguish reused inode numbers; dropping those fields would create aliasing hazards.

Test signals: compile both hostfs halves after struct changes, verify stat data maps correctly for regular files, symlinks, special files, and filesystems with/without birth time, and test setattr bits individually to ensure generated `HOSTFS_ATTR_*` constants match user wrapper behavior.
