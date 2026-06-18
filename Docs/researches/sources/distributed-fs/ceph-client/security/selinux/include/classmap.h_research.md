## sources/distributed-fs/ceph-client/security/selinux/include/classmap.h

### Purpose
`classmap.h` defines the canonical SELinux security class to permission-name mapping used to generate class and permission constants and to map kernel object managers to policy classes.

### Important APIs, types, and functions
The key artifact is `const struct security_class_mapping secclass_map[]`. It uses common permission macros such as `COMMON_FILE_PERMS`, `COMMON_SOCK_PERMS`, `COMMON_IPC_PERMS`, `COMMON_CAP_PERMS`, and `COMMON_CAP2_PERMS`. Classes include process, filesystem, file-like classes, sockets and netlink variants, packet/node/netif, key, binder, Infiniband, BPF, perf_event, anon_inode, io_uring, user_namespace, and memfd_file.

### Control flow
There is no runtime control flow besides consumers iterating the null-terminated mapping. Build-time tooling uses it to produce generated constants. Runtime audit code uses it to print class and permission names.

### State and persistence
The mapping is static kernel data. It is effectively a contract with policy and generated headers; changing ordering changes generated numeric identifiers.

### Dependencies and integration points
It depends on `struct security_class_mapping` from `avc_ss.h`. Compile-time guards require updates when Linux capabilities or protocol families grow beyond represented values.

### Risks
Adding a kernel object class, socket family, capability, or permission without updating this file can cause missing enforcement or build failures. Reordering existing entries can break policy compatibility.

### Test signals
Run SELinux header generation, full kernel build, policy load tests, audit log class/permission formatting tests, and targeted tests for newly added classes such as BPF token, memfd, io_uring, or user namespace.
