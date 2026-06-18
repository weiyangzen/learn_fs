# sources/distributed-fs/ceph-client/fs/fhandle.c

## Purpose

`sources/distributed-fs/ceph-client/fs/fhandle.c` implements the VFS file-handle syscalls `name_to_handle_at()` and `open_by_handle_at()`. It bridges path lookup, filesystem export operations, mount identity reporting, and permission-gated decoding of persistent file handles back into `struct path` and `struct file` objects. The complete 462-line file was read for this report.

## Important APIs, Types, and Functions

Key entry points are `SYSCALL_DEFINE5(name_to_handle_at)`, `SYSCALL_DEFINE3(open_by_handle_at)`, and the compat `open_by_handle_at` variant. Internal helpers include `do_sys_name_to_handle()`, `get_path_anchor()`, `vfs_dentry_acceptable()`, `may_decode_fh()`, `handle_to_path()`, `do_handle_to_path()`, `file_open_handle()`, and `do_handle_open()`. The code depends on `struct file_handle`, `struct path`, `struct export_operations`, and `struct handle_to_path_ctx` from VFS internals.

## Control Flow

`name_to_handle_at()` validates user flags, performs `filename_lookup()`, then calls `exportfs_encode_fh()` through `do_sys_name_to_handle()`. It returns mount IDs in either legacy integer or unique `u64` form, copies the variable-size handle back to userspace, and maps handle overflow to `-EOVERFLOW`. `open_by_handle_at()` reads and validates the userspace handle, anchors decoding to an fd, cwd, pidfs root, or nsfs root, checks export permission hooks or generic capability policy, decodes through `exportfs_decode_fh_raw()`, and opens the resulting path through filesystem `->open` or `file_open_root()`.

## State and Persistence Behavior

The persistent state is external: file handles are stable filesystem export identifiers, not state owned by this file. Runtime state is stack/local allocation plus path and mount references. Permission state is derived from capabilities, mount namespaces, idmapped mounts, and encoded handle flags such as connectable and directory-only.

## Dependencies and Integration Points

This code integrates with exportfs, namei lookup, namespace roots, mount internals, idmapping checks, file opening, `FD_ADD`, and user-copy APIs. Filesystems expose behavior through `s_export_op`, optionally overriding generic decode permission or open handling.

## Risks and Edge Cases

Risk concentrates around permission regressions for handle decoding, disconnected dentries, connectable handle subtree checks, user namespace id mappings, and malformed handle sizes/types. `vfs_dentry_acceptable()` deliberately performs racy path ancestry checks without `rename_lock`; that is acceptable for the documented approximation but sensitive to policy changes.

## Test Signals

Useful tests include xfstests/exportfs coverage for handle encode/decode, capability matrix tests for `CAP_DAC_READ_SEARCH` and `CAP_SYS_ADMIN`, malformed userspace handle tests, AT flag validation, idmapped mount cases, connectable directory-only decoding, and filesystem-specific NFS-export handle round trips.
