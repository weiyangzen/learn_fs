# Research: subset-b-009719

Grouped source-tree-aligned research for NFS-Ganesha OS abstraction, pNFS, SAL, statistics, identity mapping, packaging, and logging files. Each file section is bounded for reconciliation into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/syscalls.h -->
# sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/syscalls.h

## Purpose
This FreeBSD portability header supplies missing Linux-style `*at` and file-handle syscall declarations used by NFS-Ganesha's VFS/FSAL layers. It lets common code compile against older FreeBSD environments that may not expose `openat`, `fstatat`, `getfhat`, file-handle link/readlink helpers, or `AT_*` constants.

## Important APIs, Types, And Control Flow
The file defines fallback `AT_FDCWD`, `AT_SYMLINK_NOFOLLOW`, `AT_SYMLINK_FOLLOW`, and `AT_REMOVEDIR` values, then conditionally declares `getfhat`, `fhlink`, and `fhreadlink` for newer FreeBSD compiler versions. If `SYS_openat` is absent it declares `openat`, `fchownat`, `futimesat`, `fstatat`, `getfhat`, `fhopenat`, `fchmodat`, `faccessat`, `linkat`, `mkdirat`, `mkfifoat`, `mknodat`, `unlinkat`, `readlinkat`, `symlinkat`, `renameat`, `utimensat`, and file-handle helpers.

## State And Persistence
There is no runtime state. The persistent behavior is compile-time ABI exposure: consumers either use system declarations or these prototypes to call platform implementations elsewhere.

## Dependencies And Integration Points
It depends on FreeBSD `<sys/mount.h>` and `<sys/syscall.h>` for `fhandle_t`, syscall numbers, and mount types. It integrates with platform-specific VFS code that needs file-handle-based lookup and relative-directory operations for NFS exports.

## Risks And Test Signals
Prototype drift against newer FreeBSD libc/kernel headers is the main risk, especially `char *` versus `const char *` signatures and `struct fhandle` spelling. Compile tests on supported FreeBSD versions should verify no duplicate/conflicting prototypes, while runtime tests should exercise filehandle open/link/readlink, symlink no-follow behavior, and all `*at` fallbacks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/syscalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/xattr.h -->
# sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/xattr.h

## Purpose
This header normalizes extended attribute APIs on FreeBSD to the Linux-style function names expected by common Ganesha code.

## Important APIs, Types, And Control Flow
It defines `XATTR_CREATE` and `XATTR_REPLACE` flag values and declares `fgetxattr`, `fsetxattr`, `flistxattr`, and `fremovexattr` wrappers operating on file descriptors. There is no control flow in the header; implementation lives in the FreeBSD OS support layer.

## State And Persistence
No in-memory state is defined. The underlying calls persist xattr changes on filesystem objects through `fsetxattr` and `fremovexattr`.

## Dependencies And Integration Points
It includes `<sys/errno.h>` and `<sys/types.h>` and is selected by `include/os/xattr.h` when building for FreeBSD. POSIX ACL conversion, NFSv4 ACL translation, and FSAL metadata paths can use these symbols through the OS abstraction.

## Risks And Test Signals
FreeBSD xattr namespaces and flag semantics do not perfectly match Linux. Tests should cover create-only, replace-only, list buffer sizing, removal of missing attributes, and ACL xattr round-trips on FreeBSD filesystems that support extended attributes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/xattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/linux/acl.h -->
# sources/user-network-fs/nfs-ganesha/src/include/os/linux/acl.h

## Purpose
This Linux compatibility header fills gaps for non-standard POSIX ACL file-descriptor helpers when the platform ACL library lacks them.

## Important APIs, Types, And Control Flow
After including `config.h`, `<limits.h>`, `<sys/types.h>`, and `<sys/acl.h>`, it conditionally declares `acl_get_fd_np(int fd, acl_type_t type)` and `acl_set_fd_np(int fd, acl_t acl, acl_type_t type)` when `HAVE_ACL_GET_FD_NP` or `HAVE_ACL_SET_FD_NP` are absent.

## State And Persistence
The header has no state. The declared functions read and write POSIX ACLs on open file descriptors, which affects filesystem metadata when implemented and called.

## Dependencies And Integration Points
It integrates with POSIX ACL conversion code in `posix_acls.h`/implementation and with build-time feature detection in `config.h`. FSALs use this path to avoid path-based races when translating NFS ACLs.

## Risks And Test Signals
The main risks are mismatched fallback implementations and ACL type support differences between access and default ACLs. Test signals include build matrix coverage with and without native `_np` functions, descriptor ACL get/set round-trips, default ACL handling on directories, and error propagation for unsupported filesystems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/linux/acl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/linux/extended_types.h -->
# sources/user-network-fs/nfs-ganesha/src/include/os/linux/extended_types.h

## Purpose
This is the Linux-specific extended type include. It centralizes standard integer and system type availability for common headers that include `extended_types.h`.

## Important APIs, Types, And Control Flow
It includes `<sys/types.h>` and `<stdint.h>` and declares no additional types or functions. Control flow is limited to the include guard.

## State And Persistence
No runtime state or persistence is involved.

## Dependencies And Integration Points
It is selected by the cross-platform `extended_types.h` wrapper on Linux. It provides the base type vocabulary used by RPC, quota, and OS abstraction headers.

## Risks And Test Signals
Risk is low but build-critical: removing or changing this include can break type visibility for transitive consumers. Test signals are clean Linux builds under strict warning modes and compile checks for headers that rely on `uint64_t`, `uid_t`, `gid_t`, and related scalar types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/linux/extended_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/linux/fsal_handle_syscalls.h -->
# sources/user-network-fs/nfs-ganesha/src/include/os/linux/fsal_handle_syscalls.h

## Purpose
This Linux header abstracts by-handle and `*at` syscalls needed by FSAL/VFS code to operate on objects through persistent handles and special file descriptors.

## Important APIs, Types, And Control Flow
It defines missing `AT_EMPTY_PATH`, `O_PATH`, `AT_EACCESS`, `O_NOACCESS`, `F_OFD_GETLK`, `F_OFD_SETLK`, and `F_OFD_SETLKW` constants. When glibc has not exposed `MAX_HANDLE_SZ`, it defines `struct file_handle`, architecture-specific syscall numbers for aarch64, i386, x86_64, and PPC64, plus inline `name_to_handle_at` and `open_by_handle_at` wrappers around `syscall`. It also defines inline helpers `vfs_stat_by_handle`, `vfs_link_by_handle`, and `vfs_readlink_by_handle`.

## State And Persistence
There is no state in the header. Calls can create directory entries (`linkat`), open files by handle, or inspect handle-backed descriptors, so persistence is delegated to filesystem operations and kernel handle semantics.

## Dependencies And Integration Points
The header assumes `vfs_file_handle_t`, `struct stat`, and syscall prototypes are visible from surrounding includes. It is used by FSAL handle code that overlays Ganesha's handle representation with Linux `struct file_handle`.

## Risks And Test Signals
Architecture syscall-number drift, missing architecture definitions, and mount permission requirements for `open_by_handle_at` are key risks. Tests should cover handle lookup/open/stat/link/readlink on export filesystems, builds on each supported architecture, kernels with and without glibc declarations, and OFD lock constants in lock paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/linux/fsal_handle_syscalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/linux/quota.h -->
# sources/user-network-fs/nfs-ganesha/src/include/os/linux/quota.h

## Purpose
This header maps the common Ganesha quota abstraction to Linux `quotactl`.

## Important APIs, Types, And Control Flow
It includes `<sys/quota.h>` and defines `QUOTACTL(cmd, path, id, addr)` as a direct call to `quotactl((cmd), path, id, addr)`.

## State And Persistence
No header state exists. `quotactl` reads or mutates kernel/filesystem quota state depending on command.

## Dependencies And Integration Points
It is selected by `include/os/quota.h` on Linux and used by rquota service code and FSAL quota paths.

## Risks And Test Signals
Quota command encoding and privilege requirements vary by filesystem. Test signals include `GETQUOTA`/`SETQUOTA` RPC coverage, disabled-quota errors, user/group/project quota variants if supported, and Linux builds against current libc quota headers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/linux/quota.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/linux/sys_resource.h -->
# sources/user-network-fs/nfs-ganesha/src/include/os/linux/sys_resource.h

## Purpose
This Linux OS abstraction exposes a named helper macro for retrieving the process open-file limit.

## Important APIs, Types, And Control Flow
It includes `<sys/resource.h>` and defines `get_open_file_limit(rlim)` as `getrlimit(RLIMIT_NOFILE, (rlim))`.

## State And Persistence
No persistent state is defined. At runtime the macro reads process resource-limit state from the kernel.

## Dependencies And Integration Points
Consumers use it where platform-specific code needs to size descriptor management or report FD usage without hardcoding `RLIMIT_NOFILE`.

## Risks And Test Signals
Risk is small but return-value handling matters. Tests should verify startup behavior when `getrlimit` fails, low file-limit configurations, and FD usage reporting under Linux.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/linux/sys_resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/memstream.h -->
# sources/user-network-fs/nfs-ganesha/src/include/os/memstream.h

## Purpose
This cross-platform wrapper exposes platform-dependent memory-stream APIs. It currently includes the FreeBSD implementation header only when `FREEBSD` is defined.

## Important APIs, Types, And Control Flow
The wrapper itself exports no functions. Its only behavior is conditional inclusion of `<os/freebsd/memstream.h>`.

## State And Persistence
There is no state in this wrapper. Any state belongs to the platform memory-stream implementation selected underneath.

## Dependencies And Integration Points
Common code can include `os/memstream.h` without directly branching on platform. Linux relies on libc's native declarations elsewhere, while FreeBSD gets compatibility declarations.

## Risks And Test Signals
The risk is missing declarations on non-Linux/non-FreeBSD platforms or macro mis-detection. Build tests should include modules using memory streams on FreeBSD and Linux, and functional tests should verify buffer ownership and close semantics where compatibility implementations are used.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/memstream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/mntent.h -->
# sources/user-network-fs/nfs-ganesha/src/include/os/mntent.h

## Purpose
This wrapper normalizes mount table entry APIs for code that reads or writes fstab/mtab-like data.

## Important APIs, Types, And Control Flow
When `LINUX` is set it includes system `<mntent.h>`. When `FREEBSD` is set it includes `<os/freebsd/mntent.h>`. It declares no independent APIs.

## State And Persistence
No state is held in this wrapper. Underlying mount-entry functions read system files or mount databases.

## Dependencies And Integration Points
It insulates common code from Linux/FreeBSD differences in mount table APIs, likely used by export/mount discovery and configuration support.

## Risks And Test Signals
Risks are conditional compilation gaps and semantic differences between `/etc/mtab`, `/proc/mounts`, and FreeBSD mount APIs. Test signals include mount-table parsing on Linux and FreeBSD and builds where only one platform macro is defined.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/mntent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/quota.h -->
# sources/user-network-fs/nfs-ganesha/src/include/os/quota.h

## Purpose
This wrapper selects the platform quota abstraction for Ganesha quota and rquota code.

## Important APIs, Types, And Control Flow
It conditionally includes `<os/linux/quota.h>` for Linux or `<os/freebsd/quota.h>` for FreeBSD. It exports the platform-selected `QUOTACTL` interface through that include.

## State And Persistence
The wrapper has no state. Underlying quota operations read or mutate filesystem quota state.

## Dependencies And Integration Points
It is a stable include point for rquota service handlers and FSAL quota paths.

## Risks And Test Signals
Risk comes from platform macro selection and differing quota command interfaces. Test signals include Linux and FreeBSD builds, rquota RPC behavior, disabled quota behavior, and permission-denied paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/quota.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/subr.h -->
# sources/user-network-fs/nfs-ganesha/src/include/os/subr.h

## Purpose
This OS subroutine header defines common file timestamp, directory-entry, and credential helper interfaces used by Ganesha's portable VFS layer.

## Important APIs, Types, And Control Flow
It defines fallback `UTIME_NOW` and `UTIME_OMIT`, declares `vfs_utimesat`, `vfs_utimes`, `vfs_readents`, `to_vfs_dirent`, `setuser`, `setgroup`, and `set_threadgroups`, and defines `getuser`/`getgroup` aliases to `geteuid`/`getegid`. `struct vfs_dirent` normalizes inode, record length, type, offset, and name fields.

## State And Persistence
The header itself has no state. Implementations change file timestamps, parse directory buffers, and mutate effective user/group/thread group credentials.

## Dependencies And Integration Points
It includes `<stdbool.h>`, `<extended_types.h>`, and `<unistd.h>`. FSAL and protocol code use it to avoid platform-specific directory-entry and credential switching details.

## Risks And Test Signals
Credential-changing helpers are security-sensitive and thread-affinity matters. Directory parsing can be ABI-sensitive across OSes. Tests should cover timestamp special values, directory iteration across file types, privilege drop/restore behavior, supplementary group application, and concurrent request handling under credential changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/subr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/xattr.h -->
# sources/user-network-fs/nfs-ganesha/src/include/os/xattr.h

## Purpose
This wrapper selects the platform extended-attribute API for common Ganesha code.

## Important APIs, Types, And Control Flow
It includes Linux `<sys/xattr.h>` when `LINUX` is set and FreeBSD `<os/freebsd/xattr.h>` when `FREEBSD` is set. It has no functions of its own.

## State And Persistence
No wrapper state exists. Underlying xattr calls persist metadata on filesystem objects.

## Dependencies And Integration Points
The wrapper is used by POSIX ACL xattr conversion, FSAL metadata operations, and any NFS attribute path that needs extended attributes without platform-specific includes.

## Risks And Test Signals
Linux and FreeBSD xattr namespace behavior differs. Test signals include ACL xattr serialization, user/system/security namespace access, create/replace flags, and builds on both platforms.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/os/xattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/pnfs_utils.h -->
# sources/user-network-fs/nfs-ganesha/src/include/pnfs_utils.h

## Purpose
This header provides shared pNFS utility logic for layout range math, XDR encoding of layouts/devices, data-server registry management, and POSIX-to-NFSv4 error conversion.

## Important APIs, Types, And Control Flow
Inline helpers `pnfs_segments_overlap`, `pnfs_segment_contains`, and `pnfs_segment_difference` compare `struct pnfs_segment` ranges while respecting compatible `io_mode` bits and `NFS4_UINT64_MAX` infinite-length segments. Exported encoding APIs include `xdr_fsal_deviceid`, `FSAL_encode_ipv4_netaddr`, `FSAL_encode_file_layout`, `FSAL_encode_v4_multipath`, `FSAL_encode_flex_file_layout`, and `FSAL_encode_ff_device_versions4`. It defines `fsal_multipath_member_t` and declares pNFS data-server lifecycle functions such as `pnfs_ds_alloc`, `pnfs_ds_insert`, `pnfs_ds_get`, `pnfs_ds_put`, `pnfs_ds_remove`, `ReadDataServers`, `remove_all_dss`, and `server_pkginit`.

## State And Persistence
The range helpers are stateless. Data-server functions manage process-global pNFS DS registry state and reference counts; `pnfs_ds_get_ref` increments `ds_refcount` atomically. Persistence is indirect through runtime configuration loaded by `ReadDataServers`, not file writes in this header.

## Dependencies And Integration Points
It depends on `nfs4.h`, `fsal_pnfs.h`, `fsal_api.h`, and `config.h`. It connects FSAL pNFS implementations to NFSv4.1/4.2 layout XDR encoding, data-server discovery, and common error translation.

## Risks And Test Signals
The documented `pnfs_segment_difference` limitation cannot split a middle subtraction, so callers must not assume full interval algebra. Boundary tests are needed for zero-length segments, adjacent ranges, infinite lengths, overflow-prone `offset + length`, mode incompatibility, layout encoding XDR byte streams, DS registry reference balancing, and config parsing failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/pnfs_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/posix_acls.h -->
# sources/user-network-fs/nfs-ganesha/src/include/posix_acls.h

## Purpose
This header declares conversion utilities between Ganesha FSAL/NFSv4 ACLs, POSIX ACLs, and Linux xattr ACL encodings.

## Important APIs, Types, And Control Flow
It defines inheritance/applicability macros for FSAL ACE flags, default permission masks, xattr names `system.posix_acl_access` and `system.posix_acl_default`, and `ACL_FOR_V4`/`ACL_FOR_V3`. It declares `struct acl_ea_entry`, `struct acl_ea_header`, `posix_acl_2_fsal_acl`, `fsal_acl_2_posix_acl`, entry lookup/creation helpers, ACL entry counting, xattr size/count helpers, and xattr serialization/deserialization. Inline `posix_acl_get_uid` and `posix_acl_get_gid` read and free ACL qualifiers.

## State And Persistence
The header has no global state. Its implementations allocate ACL objects and FSAL ACE arrays and serialize to xattr buffers that can be persisted by filesystem xattr calls.

## Dependencies And Integration Points
It depends on `<sys/acl.h>`, `<acl/libacl.h>`, `nfs4_acls.h`, and `fsal_types.h`. It integrates NFSv3/v4 ACL behavior with POSIX ACL storage and FSAL object attributes.

## Risks And Test Signals
ACL mapping is security-sensitive; inheritance flags, owner/group qualifiers, mask entries, and deny/allow conversion must be exact. Tests should cover directory default ACLs, files without ACLs, malformed xattr sizes, qualifier allocation failures, round-trips between FSAL and POSIX ACLs, and permission equivalence for common NFSv4 ACE sets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/posix_acls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/pwnam_wrappers.h -->
# sources/user-network-fs/nfs-ganesha/src/include/pwnam_wrappers.h

## Purpose
This header defines a switchable identity lookup wrapper layer so Ganesha can use libc NSS or direct SSSD-backed implementations for passwd/group resolution.

## Important APIs, Types, And Control Flow
`pwnam_implementation_t` selects `PWNAM_IMPLEMENTATION__NSSWITCH` or `PWNAM_IMPLEMENTATION__SSSD`. Public wrappers include `pwnam_wrappers__set_implementation`, `pwnam_wrappers__getgrouplist`, `pwnam_wrappers__getpwnam_r`, `pwnam_wrappers__getpwuid_r`, `pwnam_wrappers__getgrnam_r`, and `pwnam_wrappers__getgrgid_r`.

## State And Persistence
The selected implementation is process state maintained by the implementation file. Results are caller-provided `passwd`/`group` buffers; no persistence is done.

## Dependencies And Integration Points
It depends on `<grp.h>`, `<pwd.h>`, and system ID types. It feeds idmapper and uid-to-group cache logic, and can route to `sss_nss_idmap.h` when SSSD support is available.

## Risks And Test Signals
Risks include buffer sizing, thread safety, inconsistent NSS/SSSD error codes, and runtime implementation switching. Tests should cover both backends, unknown users/groups, large supplementary group lists, ERANGE retry behavior, and concurrent lookups.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/pwnam_wrappers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/rados_grace.h -->
# sources/user-network-fs/nfs-ganesha/src/include/rados_grace.h

## Purpose
This header declares Ceph RADOS-backed NFS grace-period coordination APIs used by clustered Ganesha instances.

## Important APIs, Types, And Control Flow
It defines default pool/object names `nfs-ganesha` and `grace`. Bulk operations include `rados_grace_create`, `dump`, `epochs`, `enforcing_toggle`, `enforcing_check`, `join_bulk`, `lift_bulk`, `add`, and `member_bulk`. Inline single-node wrappers build a one-element `nodeids` array for enforcing on/off, join, lift, and member checks.

## State And Persistence
Grace state persists in a RADOS object addressed by `rados_ioctx_t` and object id. The APIs track current/recovery epochs, enforcing status, and cluster membership for node ids.

## Dependencies And Integration Points
The header assumes Ceph `rados_ioctx_t` is visible from prior includes and uses `<stdio.h>` for dumping. It integrates with NFSv4 recovery backends and grace enforcement in SAL.

## Risks And Test Signals
Distributed state consistency, partial bulk updates, epoch races, and object creation failures are the key risks. Tests should simulate join/lift/enforcing transitions, multiple nodes, missing RADOS objects, epoch reads, and recovery behavior under RADOS errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/rados_grace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/rbt_node.h -->
# sources/user-network-fs/nfs-ganesha/src/include/rbt_node.h

## Purpose
This header defines the node and tree-head structures for Ganesha's red-black tree macros, adapted from STL red-black tree internals.

## Important APIs, Types, And Control Flow
`struct rbt_head` stores root, leftmost, rightmost, and node count. `rbt_node_t` stores flags, an `anchor` pointer-to-pointer, parent, left child, right child named `next`, sortable `uint64_t rbt_value`, and opaque user pointer `rbt_opaq`. `RBT_NUM` defines allocation batch size and `RBT_RED` marks red nodes.

## State And Persistence
The structures are embedded in caller-managed objects and hold in-memory tree linkage only. No persistence is defined.

## Dependencies And Integration Points
It depends on `<stdint.h>` and is consumed by `rbt_tree.h` macro algorithms and hashtable/cache structures that need ordered nodes.

## Risks And Test Signals
Because callers embed nodes, lifecycle misuse can corrupt arbitrary owner objects. Tests should verify initialization, duplicate values, unlink/reinsert behavior, opaque pointer retrieval, and memory ownership around embedded node containers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/rbt_node.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/rbt_tree.h -->
# sources/user-network-fs/nfs-ganesha/src/include/rbt_tree.h

## Purpose
This macro-only header implements red-black tree operations over `struct rbt_head` and `struct rbt_node` for ordered in-memory indexes.

## Important APIs, Types, And Control Flow
Macros include `RBT_HEAD_INIT`, `RBT_COUNT`, `RBT_RIGHTMOST`, `RBT_LEFTMOST`, `RBT_VALUE`, `RBT_OPAQ`, forward/reverse iteration with `RBT_INCREMENT`, `RBT_DECREMENT`, `RBT_LOOP`, and `RBT_LOOP_REVERSE`, rotations, `RBT_INSERT`, `RBT_UNLINK`, `RBT_FIND`, `RBT_FIND_LEFT`, `RBT_BLACK_COUNT`, and `RBT_VERIFY`. Insert and unlink mutate anchors, parent/child links, leftmost/rightmost cache pointers, count, and red/black flags.

## State And Persistence
All state is caller-owned in-memory tree linkage. The macros perform no allocation, locking, or persistence; callers must provide initialized heads/nodes and external synchronization.

## Dependencies And Integration Points
It relies on `rbt_node.h` definitions being available. The macros are intended for low-level caches/hashtables where function-call overhead or generic containers are avoided.

## Risks And Test Signals
The macro implementation evaluates arguments with side effects, dereferences sibling pointers in unlink fix-up, and has no built-in locking. Duplicate key handling is supported but subtle. Tests should exercise empty trees, ordered and random inserts, duplicate keys, deletion of root/leaf/two-child nodes, iteration after mutations, reverse iteration, `RBT_VERIFY` error detection, and sanitizer runs for pointer misuse.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/rbt_tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/rquota.h -->
# sources/user-network-fs/nfs-ganesha/src/include/rquota.h

## Purpose
This hand-maintained rpcgen-style header defines the RQUOTA RPC protocol data model, client/server stubs, and XDR entry points.

## Important APIs, Types, And Control Flow
It defines quota block structures `sq_dqblk` and `rquota`, argument structures for regular and extended get/set quota calls, result unions `getquota_rslt` and `setquota_rslt`, `qr_status` values `Q_OK`, `Q_NOQUOTA`, and `Q_EPERM`, program/version constants `RQUOTAPROG`, `RQUOTAVERS`, and `EXT_RQUOTAVERS`, procedure numbers, client and `_svc` function prototypes, `rquotaprog_1_freeresult`, `check_handle_lead_slash`, and XDR functions for each protocol type.

## State And Persistence
The header defines RPC wire structures only. Runtime handlers read or mutate filesystem quota state via OS quota APIs; XDR functions serialize transient request/response objects.

## Dependencies And Integration Points
It depends on `gsh_rpc.h` and `extended_types.h`. It connects the RPC dispatch layer to rquota service implementations and the OS quota abstraction.

## Risks And Test Signals
Because this is protocol ABI, field order and integer widths are high-risk. Tests should include XDR encode/decode compatibility with rpcgen clients, procedure dispatch for v1 and extended v2 arguments, path length handling, leading-slash normalization, and quota status mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/rquota.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/sal_data.h -->
# sources/user-network-fs/nfs-ganesha/src/include/sal_data.h

## Purpose
This is the core State Abstraction Layer data model. It defines the in-memory structures for NFSv4/NFSv4.1 client IDs, sessions, stateids, owners, locks, delegations, layouts, recovery records, async state work, per-object state handles, and grace-period events.

## Important APIs, Types, And Control Flow
Major types include `nfs41_session_t` with fore/back channel attributes, slot tables, connection lists, callback state, refcount, and revoked-delegation flags; `state_t` with object/export/owner pointers, typed `union state_data`, stateid sequence/other fields, and refcount; owner structures for NFSv4, NLM, and 9P; `nfs_client_id_t` and `nfs_client_record_t`; `state_lock_entry_t`, `state_block_data_t`, and `state_cookie_entry_t`; `state_file`, `state_dir`, and `state_hdl`; layout segment/recall structures; async queue records; and `nfs_grace_start_t`. It also provides inline `free_state`, stateid compare/copy macros, `obj_is_junction`, and tracepoint macros.

## State And Persistence
This header declares extensive process-global state: pools, hash tables for sessions/state/client IDs/owners, recovery directories, blocked lock lists, debug lists, client-id pools, and delegation counters. Persistent behavior is indirect through recovery directories/backends, revoked delegation records, quota/lock state in FSALs, and client reclaim metadata; the structs themselves are in-memory lifetime anchors.

## Dependencies And Integration Points
It depends on atomic/memory/list/hashtable utilities, FSAL pNFS and object types, config parsing, LTTng trace helpers, NFS protocol data, and optional NLM/9P types. It is consumed by SAL implementation files, NFSv4 protocol operations, export/client managers, FSAL object handles, session transport handling, metrics, and server statistics.

## Risks And Test Signals
Concurrency and lifecycle are dominant risks: documented lock ordering is `STATELOCK` then owner `so_mutex` then state `state_mutex`; client record mutex must not be acquired under `cid_mutex`; references must balance across state, owner, client, session, lock, and object pointers. Tests should stress open/close/lock/delegation/session churn, client expiration and reclaim, layout recall, junction detection, blocked lock grants/cancels, recovery grace transitions, and sanitizer/thread-sanitizer coverage for refcount and lock-order bugs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/sal_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/sal_functions.h -->
# sources/user-network-fs/nfs-ganesha/src/include/sal_functions.h

## Purpose
This header declares the operational API for the State Abstraction Layer: state/error conversion, owner/client/session/stateid management, locks, delegations, layouts, shares, async work, and recovery backends.

## Important APIs, Types, And Control Flow
It exports state error formatting/conversion, owner refcount/display/get/free APIs, `STATELOCK_lock`/`STATELOCK_unlock`, `state_hdl_init`/cleanup, optional 9P and NLM owner/state helpers, NFSv4 client-id lifecycle functions, session table operations, stateid validation and update helpers, state refcount helpers, lease update/reservation, NFSv4 owner seqid replay support, lock test/lock/unlock/cancel/grant APIs, state add/set/delete and safe reference getters, delegation grant/recall/revoke/CB_GETATTR helpers, layout segment operations, NLM share APIs, async scheduling/upcalls/polling, grace/recovery APIs, and `struct nfs4_recovery_backend` function table.

## State And Persistence
The APIs mutate the global SAL data declared in `sal_data.h`: hashes, lists, pools, refcounts, state object lists, lock lists, session connection lists, grace status, and recovery metadata. Persistent state is handled through recovery backends, client stable storage, RADOS or filesystem grace tracking, and FSAL lock/delegation state.

## Dependencies And Integration Points
It depends on `sal_data.h`, `fsal.h`, `gsh_recovery.h`, LTTng traces, and protocol structures. It is the primary contract between NFS protocol handlers, FSAL implementations, recovery modules, statistics/metrics code, and transport/session management.

## Risks And Test Signals
The biggest risks are deadlocks, refcount leaks/use-after-free, replay-cache mistakes for NFSv4.0 seqids, stale stateid handling, lock grant races, and grace-period membership errors. Test signals include NFSv4.0 replay and lease tests, NFSv4.1 session slot reuse, stateid special cases, lock conflict/blocked/async grant flows, delegation recall/revoke, layout return/recall, client restart/reclaim, and recovery backend failover tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/sal_functions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/sal_metrics.h -->
# sources/user-network-fs/nfs-ganesha/src/include/sal_metrics.h

## Purpose
This header declares monitoring hooks for SAL-level client, lease, lock, session, and transport/session association metrics.

## Important APIs, Types, And Control Flow
It defines `sal_metrics__lock_type` with holders, waiters, and count values. Functions record confirmed client totals, lease expiration events, client state-protection type, lock increments/decrements, session connection distributions, denied xprt/session associations, xprt custom data status, xprt session counts, and `sal_metrics__init`.

## State And Persistence
State is owned by the monitoring subsystem initialized by `sal_metrics__init`. The header itself has no storage. Metrics are runtime observability data and may be exported to the configured monitoring backend.

## Dependencies And Integration Points
It includes `monitoring.h`, `nfsv41.h`, and `xprt_handler.h`. It integrates SAL state changes, session connection tracking, and transport custom-data lifecycle with monitoring counters/histograms.

## Risks And Test Signals
Metrics must not perturb SAL locking or allocate in hot paths unexpectedly. Tests should verify init idempotence, enum label coverage, increments/decrements balancing, transport status labels, and that metrics calls remain safe when monitoring is disabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/sal_metrics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/sal_shared.h -->
# sources/user-network-fs/nfs-ganesha/src/include/sal_shared.h

## Purpose
This small shared SAL header defines the common state type enumeration without pulling in the full SAL data model.

## Important APIs, Types, And Control Flow
`enum state_type` includes none, NFSv4 share, delegation, byte-range lock, layout, NLM lock, NLM share, 9P fid, and max sentinel values.

## State And Persistence
There is no runtime state. Values are stored in `state_t` and drive type-specific interpretation of `union state_data`.

## Dependencies And Integration Points
It is included by `sal_data.h` and any code that needs state type labels while avoiding circular dependencies.

## Risks And Test Signals
Changing enum values can break persisted/debug assumptions and switch statements. Test signals include exhaustive switch warnings, state allocation/deletion paths for every type, and metrics/log formatting that maps each state type.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/sal_shared.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/server_stats.h -->
# sources/user-network-fs/nfs-ganesha/src/include/server_stats.h

## Purpose
This public statistics header declares hooks used by request-processing paths to update server, operation, IO, transport, and delegation statistics.

## Important APIs, Types, And Control Flow
It declares `server_stats_nfs_done`, optional `server_stats_9p_done`, `server_stats_io_done`, `server_stats_compound_done`, `server_stats_nfsv4_op_done`, `server_stats_transport_done`, and delegation counters `inc_grants`, `dec_grants`, `inc_revokes`, `inc_recalls`, and `inc_failed_recalls`.

## State And Persistence
The functions update in-memory per-server, per-client, per-export, and protocol-specific statistic structures. Persistence is observability output through DBus/monitoring or log reporting, not this header.

## Dependencies And Integration Points
It references `nfs_request_t`, `gsh_client`, optional 9P request data, and NFS operation/status timing. Protocol dispatchers and FSAL IO paths call these hooks after work completes.

## Risks And Test Signals
Stats hooks run on request hot paths, so locking, null clients, and overflow behavior matter. Tests should cover successful/failed IO, duplicate NFS requests, compound status reporting, per-operation latency, transport byte counters, and delegation grant/recall/revoke accounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/server_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/server_stats_private.h -->
# sources/user-network-fs/nfs-ganesha/src/include/server_stats_private.h

## Purpose
This private statistics header defines internal aggregate structures, DBus reply signatures, reset/export helpers, and initialization/free APIs for Ganesha server statistics.

## Important APIs, Types, And Control Flow
It forward-declares per-protocol stats types, defines `struct gsh_stats`, `struct gsh_clnt_allops_stats`, `struct server_stats` with trailing variable-sized `gsh_client`, `struct export_stats`, and `struct auth_stats`. Under `USE_DBUS` it defines many DBus type/signature macros for exports, clients, IO, layout, auth, all-ops, LRU, and FD usage, declares DBus serialization functions, reset functions, stats timestamps, and optional protocol-specific emitters. It always declares `server_stats_free`, `server_stats_allops_free`, and `server_stats_init`.

## State And Persistence
It manages process runtime statistics and timestamps such as auth/v3/v4 full stats times. DBus functions serialize current in-memory counters; reset functions clear them. No file persistence is performed.

## Dependencies And Integration Points
It includes `sal_data.h` for client/export/state relationships. It integrates with client manager allocation sizing, export manager stats, DBus introspection/serialization, NFS protocol counters, FSAL operation stats, MDCACHE utilization, and FD usage summaries.

## Risks And Test Signals
The trailing `gsh_client` layout requirement in `server_stats` is memory-layout sensitive. DBus signature macros must match serialization code exactly, and compile-time protocol flags change container shape. Tests should cover DBus introspection/signature validation, stats reset, allocation sizing for variable-length clients, disabled/enabled protocol builds, and monotonic counter behavior under concurrent requests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/server_stats_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/sss_nss_idmap.h -->
# sources/user-network-fs/nfs-ganesha/src/include/sss_nss_idmap.h

## Purpose
This header declares direct SSSD-backed passwd/group lookup helpers used as an alternative to libc NSS switching.

## Important APIs, Types, And Control Flow
It exposes `sss_nss_idmap__init`, `sss_nss_idmap__getpwnam`, `getpwuid`, `getgrnam`, `getgrgid`, and `getgrouplist` wrappers using caller-provided `passwd`/`group` buffers and result pointers.

## State And Persistence
Initialization likely sets process state for SSSD idmap access; lookup calls return transient buffer-backed records. No persistence is defined.

## Dependencies And Integration Points
It includes `<grp.h>` and `<pwd.h>` and is selected by `pwnam_wrappers` when SSSD implementation is configured. It feeds idmapper and uid2grp cache population.

## Risks And Test Signals
Risks include optional library availability, initialization failures, buffer sizing, domain-qualified names, and differences from NSS behavior. Tests should cover enabled/disabled SSSD builds, missing SSSD service, large group lists, unknown identities, and concurrent lookup calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/sss_nss_idmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/uid2grp.h -->
# sources/user-network-fs/nfs-ganesha/src/include/uid2grp.h

## Purpose
This header defines the UID/principal-to-group cache contract used by Ganesha's idmapper and credential-building paths.

## Important APIs, Types, And Control Flow
`group_data_t` stores uid, username buffer, primary gid, epoch, supplementary group count, refcount, mutex, and group array. It declares global `uid2grp_user_lock` and `uid2grp_sem`, cache init/add/lookup/remove/reap/clear functions, lookup helpers `uid2grp`, `uname2grp`, and `principal2grp`, plus reference-management APIs `uid2grp_unref`, `uid2grp_hold_group_data`, `uid2grp_release_group_data`, and expiration checks.

## State And Persistence
The cache is process-global in-memory state protected by a rwlock, per-record mutexes, refcounts, and a semaphore. Entries expire by epoch; no persistent storage is declared.

## Dependencies And Integration Points
It depends on pthreads, semaphores, `gsh_types.h`, and identity lookup wrappers. It integrates NFS principal/user resolution with request credential construction and access checks.

## Risks And Test Signals
Risks include stale group membership, refcount leaks, lock contention, semaphore misuse, and principal-to-uid ambiguity. Tests should cover cache hits/misses, expiration removal by uid/name, concurrent readers and reaper, large supplementary groups, principal fallback inputs, and unref/free races.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/uid2grp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/xprt_handler.h -->
# sources/user-network-fs/nfs-ganesha/src/include/xprt_handler.h

## Purpose
This header defines custom transport data used to associate RPC transports with NFSv4.1 sessions and connection-manager state.

## Important APIs, Types, And Control Flow
`nfs41_session_list_entry_t` links a session into a transport list. `nfs41_sessions_holder_t` contains an rwlock, session list, and session count. `xprt_custom_data_status_t` tracks associated, dissociated, and destroyed states. `xprt_custom_data_t` combines the session holder, status, and managed connection. Functions initialize, destroy, dissociate custom data, and add/remove NFSv4.1 sessions for an `SVCXPRT`.

## State And Persistence
Custom data is attached to live transport objects and tracks session associations and managed connection lifecycle. It is volatile in-memory state.

## Dependencies And Integration Points
It depends on `gsh_rpc.h`, `sal_data.h`, and `connection_manager.h`. It integrates the RPC transport layer with SAL session tracking, connection teardown, and `sal_metrics` transport status metrics.

## Risks And Test Signals
Transport teardown races are the main risk: sessions can outlive, dissociate from, or observe destroyed xprts. Tests should cover session add/remove concurrency, transport destruction with active sessions, denied association paths, connection-manager cleanup, and metrics label updates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/xprt_handler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/libganeshaNFS.pc.cmake -->
# sources/user-network-fs/nfs-ganesha/src/libganeshaNFS.pc.cmake

## Purpose
This CMake template generates the `pkg-config` metadata for the `libganeshaNFS` fuselike library.

## Important APIs, Types, And Control Flow
The template sets `prefix`, `exec_prefix`, `libdir`, and `includedir`, then emits package fields `Name`, `Description`, empty `Requires`, version from `@GANESHA_MAJOR_VERSION@@GANESHA_MINOR_VERSION@`, linker flags `-L... -lganeshaNFS`, and include flags from `@INCLUDE_INSTALL_DIR@`.

## State And Persistence
The generated `.pc` file is an installed build artifact. It persists install-time paths and version substitutions.

## Dependencies And Integration Points
It is processed by CMake configure/install logic and consumed by external builds using `pkg-config` to find Ganesha's library and headers.

## Risks And Test Signals
Version concatenation without a separator may be intentional but should be verified. Risks include wrong `LIB_SUFFIX`, wrong include install directory, and missing dependency libraries in `Requires`/`Libs`. Tests should run `pkg-config --cflags --libs libganeshaNFS` from an install tree and compile a small external consumer.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/libganeshaNFS.pc.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/log/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/log/CMakeLists.txt

## Purpose
This CMake file defines the logging object library build for Ganesha's display and log functions.

## Important APIs, Types, And Control Flow
It adds `-D__USE_GNU`, conditionally includes DBus and LTTng include directories, sets `log_STAT_SRCS` to `display.c` and `log_functions.c`, creates `add_library(log OBJECT ...)`, applies sanitizers, sets `-fPIC`, and when LTTng is enabled adds a dependency on generated trace headers and includes generated file properties. It also lists `test_display.c` as test source metadata.

## State And Persistence
Build state is persisted in generated build files and object outputs. No runtime state is defined here.

## Dependencies And Integration Points
It integrates the log object library with top-level CMake, sanitizer configuration, DBus headers for logging/stat output, and LTTng trace generation.

## Risks And Test Signals
Risks include missing generated trace header dependencies, global `add_definitions` leakage, and object library PIC requirements for shared-library consumers. Test signals include CMake configure/build with DBus on/off, LTTng on/off, sanitizer builds, and compilation of `test_display.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/log/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/log/display.c -->
# sources/user-network-fs/nfs-ganesha/src/log/display.c

## Purpose
This source implements `display_buffer`, a bounded string-building helper used by logging and diagnostics to append formatted text, opaque byte strings, and truncated strings safely.

## Important APIs, Types, And Control Flow
Internal `_display_buffer_remain` computes remaining bytes including the null terminator. `display_buffer_remain` validates/reset buffer pointers and marks too-small buffers as overflowed. `_display_complete_overflow` places `...` while avoiding partial UTF-8 truncation. `display_start` prepares append operations and handles already-full buffers. `display_finish` finalizes after writes and applies overflow ellipsis. `display_force_overflow` deliberately marks truncation. `display_vprintf` wraps `vsnprintf`. `display_opaque_bytes_flags` formats bytes in hex with flags for uppercase, `0x`, and invalid input handling. `display_opaque_value_max_impl` prints printable opaque values or hex with length/truncation markers. `display_len_cat` appends length-delimited strings, and `display_cat_trunc` appends a null-terminated string through a sub-buffer for caller-specified truncation.

## State And Persistence
All state is caller-owned in `struct display_buffer` fields `b_start`, `b_current`, and `b_size`. The implementation mutates the current pointer and buffer contents but does not allocate or persist data.

## Dependencies And Integration Points
It includes C runtime headers and `display.h`. Many SAL, stats, ID, state, and logging formatters use display buffers to build bounded diagnostic strings without heap allocation.

## Risks And Test Signals
Critical risks include pointer validation, small-buffer behavior, UTF-8 boundary handling, negative lengths, null opaque values, `vsnprintf` return semantics, and nested sub-buffer truncation. Tests should cover invalid buffers, sizes 0-4, exact fit, overflow, multibyte UTF-8 truncation, printable/non-printable opaque data, `OPAQUE_BYTES_NO_TRUNC`, and repeated appends after overflow.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/log/display.c -->
