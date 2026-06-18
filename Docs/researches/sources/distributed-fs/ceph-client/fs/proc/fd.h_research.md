# sources/distributed-fs/ceph-client/fs/proc/fd.h

Purpose: Declares the proc fd/fdinfo operations used by the per-pid entry tables.

Important APIs and types: Exposes `proc_fd_operations`, `proc_fd_inode_operations`, `proc_fdinfo_operations`, `proc_fdinfo_inode_operations`, `proc_fd_permission()`, and inline `proc_fd()` which returns `PROC_I(inode)->fd`.

Control flow: The header has no complex runtime flow. Its inline helper maps a proc inode to the descriptor number stored by fd/fdinfo instantiation.

State and persistence: State is the `fd` field embedded in `struct proc_inode`; the header only provides access to it.

Dependencies and integration points: Includes `linux/fs.h` and relies on proc internal definitions available to includers. It is included by `base.c` for entry tables and by `fd.c` for implementation.

Risks: `proc_fd()` assumes the inode is a proc inode instantiated by fd handling. Using it on the wrong inode would read unrelated proc inode state. Operation declarations must stay synchronized with `fd.c`.

Test signals: Compile coverage through `base.c` and `fd.c`, lookup/read of fd and fdinfo entries, and permission tests that call `proc_fd_permission()`.
