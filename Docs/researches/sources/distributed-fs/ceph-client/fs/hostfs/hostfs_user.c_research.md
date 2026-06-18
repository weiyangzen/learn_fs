# sources/distributed-fs/ceph-client/fs/hostfs/hostfs_user.c

Purpose: this file is the UML user-space syscall wrapper implementation behind hostfs. It converts host libc/syscall results into the negative errno interface used by `hostfs_kern.c`.

Important APIs and functions: `stat_file()` uses `statx()` with `AT_SYMLINK_NOFOLLOW` and optional `AT_EMPTY_PATH`, then `statx_to_hostfs()` fills `struct hostfs_stat`. File operations wrap `open64`, `pread64`, `pwrite64`, `lseek64`, `fsync`/`fdatasync`, `dup2`, and `close`. Directory operations wrap `opendir`, `seekdir`, `readdir`, and `closedir`. Metadata and namespace functions wrap `chmod/fchmod`, `chown/fchown`, `truncate/ftruncate`, `utimes/futimes`, `symlink`, `unlink`, `mkdir`, `rmdir`, `mknod`, `link`, `readlink`, `rename`, `renameat2`, and `statfs64`.

Control flow: each wrapper performs a host syscall, returns `-errno` on failure, and otherwise normalizes return values for kernel-side callers. `set_attr()` applies mode, ownership, size, and time changes in ordered blocks. For explicit atime/mtime setting, it stats current times first, modifies only requested fields, then calls `futimes()` or `utimes()`.

State and persistence: all persistent state lives in the host filesystem. This file performs direct host mutations for hostfs VFS operations. It also advances read/write offsets passed by pointer after successful pread/pwrite.

Dependencies and integration: it depends on libc/POSIX headers, UML `os_makedev()`, and `hostfs.h` struct definitions. `rename2_file()` conditionally defines syscall numbers for x86 and falls back to `-EINVAL` when unsupported or unavailable.

Risks: `open_file()` panics on impossible mode combinations, relying on kernel-side callers to pass valid read/write booleans. `set_attr()` comments that ctime is not handled; caller-visible ctime comes from later stat refreshes. The time-setting block reads `attrs->ia_atime` and `ia_mtime` only when corresponding `*_SET` bits are present. `rename2_file()` portability depends on syscall number availability.

Test signals: wrapper-level tests should cover negative errno mapping, symlink stat behavior, birth-time fallback when `STATX_BTIME` is absent, partial reads/writes, append-mode open effects, individual setattr fields, `renameat2` unsupported kernels, special-device creation, and statfs field conversion.
