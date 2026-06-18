# sources/distributed-fs/ceph-client/io_uring/xattr.c

Purpose: implements async get/set extended attribute operations for path-based and file-based xattr io_uring opcodes.

Important APIs/types/functions: `struct io_xattr` stores file, `kernel_xattr_ctx`, and optional delayed filename. Entry points are `io_fgetxattr_prep()`, `io_getxattr_prep()`, `io_fgetxattr()`, `io_getxattr()`, `io_fsetxattr_prep()`, `io_setxattr_prep()`, `io_fsetxattr()`, `io_setxattr()`, and `io_xattr_cleanup()`.

Control flow: get prep initializes delayed filename state, imports the xattr name into kernel memory, stores userspace value buffer/size, rejects flags, and forces async. Path get additionally rejects fixed-file mode and delays pathname lookup. Set prep imports name and copies value through `setxattr_copy()`, with path and file variants mirroring get behavior. Issue calls file or filename xattr helpers, then `io_xattr_finish()` clears cleanup, frees name/value/path resources, and posts the result.

State and persistence: transient state includes imported xattr name, optional copied value, delayed path, and userspace value pointer. Successful set operations persist filesystem xattr changes; get operations copy values to userspace.

Dependencies/integration: depends on VFS xattr helpers, delayed filename helpers, `kernel_xattr_ctx`, io_uring cleanup flags, and async issue semantics.

Risks/test signals: risks are cleanup leaks on prep failure/cancel, fixed-file rejection for path variants, flag validation differences between get/set, user buffer faults, and path lookup semantics. Test file/path get/set, remove via zero size where supported, invalid flags, faulted name/value/path pointers, cancellation before issue, and permission/security xattr failures.
