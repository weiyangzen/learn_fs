# sources/distributed-fs/glusterfs/libglusterfs/src/compat.c

## Purpose
This file contains operating-system compatibility shims used by libglusterfs. Most code is Solaris-specific extended attribute support for platforms where xattrs are represented through attribute directories and where symlinks or device files need a mapped regular file. It also provides fallback implementations for missing libc helpers and a portable lazy unmount wrapper.

## Important APIs, types, and functions
Solaris exports include `solaris_fsetxattr`, `solaris_fgetxattr`, `solaris_setxattr`, `solaris_getxattr`, `solaris_listxattr`, `solaris_flistxattr`, `solaris_removexattr`, `solaris_unlink`, `solaris_rename`, `make_export_path`, and `solaris_xattr_resolve_path`. Generic or conditional helpers include `strsep`, `vasprintf`, `asprintf`, `mkdtemp`, `gf_extattr_list_reshape`, `strnlen`, and `gf_umount_lazy`.

## Control flow
Solaris path xattr operations first call `solaris_xattr_resolve_path()`. Regular files and directories use native attribute operations. Special files are redirected to a mapped file under `GF_SOLARIS_XATTR_DIR` below the export root discovered by walking GFID xattrs with `make_export_path()`. Set/get/list/remove operations then use `attropen`, `openat`, `read`, `write`, `unlinkat`, and directory iteration. `gf_umount_lazy()` builds a `runner_t`, invokes Linux `umount -l` or the platform `umountd`, and optionally removes the mount directory on Linux.

## State and persistence behavior
Compatibility calls persist data only through filesystem xattrs and the Solaris mapped-xattr files. The mapped files are keyed by inode number beneath the export's hidden xattr directory. `solaris_unlink()` removes the mapped file when the source has a single link; `solaris_rename()` removes a mapped destination before rename. No process-global cache is maintained.

## Dependencies and integration points
The file integrates with GlusterFS allocation/logging (`GF_CALLOC`, `GF_FREE`, `gf_msg`), path/stat conversion (`iatt_from_stat`), GFID helpers, syscall wrappers, and command execution via `runner_t`. Higher layers call these through compatibility macros from `glusterfs/compat.h` and `glusterfs/syscall.h`.

## Risks and edge cases
`make_export_path()` and related Solaris functions use repeated `strcat()` into `PATH_MAX` buffers and assume path lengths fit. Error handling around `dup`, `fdopendir`, and `close` can leak or double-close if platform semantics differ. `mkdtemp()` appears to treat `mkstemp()` as returning a string, which is only safe if a platform macro changes that interface; otherwise it is suspicious. The Solaris mapped-xattr scheme relies on inode stability and cleanup paths being consistently used.

## Test signals
Tests should cover Solaris xattrs on regular files, symlinks, device files, ENOENT-to-ENODATA translation, zero-size get/list calls, too-small list buffers returning `ERANGE`, unlink and rename cleanup of mapped xattr files, BSD extattr list reshaping, missing `strnlen`, and `gf_umount_lazy()` command construction on Linux and non-Linux builds.
