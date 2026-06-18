# sources/distributed-fs/openafs/src/afs/sysincludes.h

Purpose: centralizes OS/kernel header inclusion for AFS cache-manager code, with extensive platform conditionals and a UKERNEL redirect.

Important APIs/types: no exported functions. It chooses system headers for OpenBSD, NetBSD, Linux, AIX, SGI, Solaris, HPUX, Darwin, FreeBSD, and generic legacy Unix paths. It also defines guard macros to prevent namespace conflicts with Linux Coda/XFS inode headers and declares FreeBSD `M_AFS`.

Control flow: compile-time only. Linux includes modern kernel headers such as `uaccess`, `list`, `dcache`, `mount`, `fs`, `quota`, `sched`, `mm`, `slab`, `proc_fs`, `completion`, and optional `exportfs`. Non-Linux paths include vnode, UFS, socket, mbuf, proc, ioctl, flock, and platform VM headers as needed.

State and persistence: none.

Dependencies and integration points: included before `afsincludes.h` by C files such as `afs_vcache.c`, `afs_volume.c`, and `afs_warn.c`. It provides the kernel type universe for vnodes, credentials, sockets, uio, buffers, and memory APIs consumed by OpenAFS abstractions.

Risks: include-order and macro-conflict risk is high. Some branches intentionally fake or predefine guard macros to avoid conflicting external filesystems. Platform kernel header evolution can break stale conditionals. Duplicate NetBSD includes are harmless but indicate historical accretion.

Test signals: broad compile matrix, especially Linux kernel-version feature probes, Darwin/FreeBSD vnode builds, Solaris 5.10/5.11 branches, and SGI debug header behavior. Also test that `UKERNEL` redirects without pulling kernel headers.
