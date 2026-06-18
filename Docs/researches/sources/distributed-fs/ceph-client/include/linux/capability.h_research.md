## sources/distributed-fs/ceph-client/include/linux/capability.h

**Purpose:** This header defines the in-kernel capability representation and authorization helpers around user namespaces, files, and inode ownership.

**Important APIs/types/functions:** `kernel_cap_t` wraps a `u64`. `struct cpu_vfs_cap_data` stores xattr capability data in CPU endian form. Macros define kernel capability version, FS/NFSD masks, empty/full sets, and operations such as `cap_clear`, `cap_raise`, `cap_lower`, `cap_raised`, `cap_combine`, `cap_intersect`, `cap_drop`, `cap_isclear`, `cap_isidentical`, and `cap_issubset`. Capability check APIs include `capable()`, `ns_capable()`, no-audit variants, inode-aware helpers, `file_ns_capable()`, `ptracer_capable()`, and specialized `perfmon_capable()`, `bpf_capable()`, and checkpoint/restore helpers. File-capability APIs parse/convert disk xattrs.

**Control flow, state, persistence:** Capability sets are bitmasks in credentials and file xattrs. With `CONFIG_MULTIUSER=n`, checks stub to true. File capability xattrs persist on disk and are converted through VFS/idmap helpers.

**Dependencies/integration:** Depends on UAPI capabilities, UID/GID types, user namespaces, mount idmaps, VFS dentries/inodes/files, and LSM/audit implementation.

**Risks and test signals:** Risks include fallback to `CAP_SYS_ADMIN`, namespace confusion, idmapped mount conversion mistakes, and config-off assumptions. Test signals include LTP capability tests, filecap xattr round trips, user namespace tests, BPF/perf permission tests, and `CONFIG_MULTIUSER=n` compile behavior.
