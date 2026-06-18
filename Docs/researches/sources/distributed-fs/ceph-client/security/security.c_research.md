# sources/distributed-fs/ceph-client/security/security.c

## Purpose
`security.c` is the Linux Security Module (LSM) framework's central dispatch layer. It exposes the `security_*()` entry points used by VFS, process, IPC, networking, BPF, keyring, block-device, perf, io_uring, and other kernel subsystems, then routes those operations to the active LSM hook implementations. It also owns generic LSM blob allocation for kernel objects and defines shared lockdown reason strings for audit/reporting.

The file is not Ceph-specific despite living under this imported distributed-fs source tree. CephFS and the Ceph client encounter it through normal kernel integration points: inode/file hooks, security xattrs, network sockets, kernel file/data loading, and security context conversion.

## Important APIs, Types, and Data
Key global state:

- `lockdown_reasons[]`: common text labels for `enum lockdown_reason`.
- `lsm_debug`, `lsm_active_cnt`, `lsm_idlist[]`: initialized LSM framework metadata.
- `blob_sizes`: aggregate per-object LSM blob sizes built by LSM registration code.
- `lsm_file_cache`, `lsm_backing_file_cache`, `lsm_inode_cache`: slab caches for high-frequency object blobs.
- `static_calls_table`: per-hook, per-LSM static call slots plus active static keys.

Core helper APIs:

- `lsm_blob_alloc()` allocates zeroed composite blobs or stores `NULL` when the aggregate size is zero.
- `lsm_file_alloc()`, `lsm_backing_file_alloc()`, `lsm_inode_alloc()`, `lsm_cred_alloc()`, `lsm_task_alloc()`, `lsm_ipc_alloc()`, `lsm_key_alloc()`, `lsm_msg_msg_alloc()`, `lsm_bdev_alloc()`, BPF alloc helpers, and `lsm_superblock_alloc()` bind composite storage to object-specific security pointers.
- `lsm_fill_user_ctx()` builds a user-visible `struct lsm_ctx`, supports size-probe calls with `uctx == NULL`, aligns the record length, and returns `-E2BIG`, `-EFAULT`, or `-ENOMEM` as needed.
- `call_void_hook()` invokes all active void hooks.
- `call_int_hook()` invokes active int hooks until one returns a value different from that hook's default from `linux/lsm_hook_defs.h`.
- `lsm_for_each_hook()` iterates active hook slots directly for special aggregation cases.

Major exported security surfaces include binder, ptrace, capabilities, quota/syslog/time, memory overcommit, exec/bprm, filesystem context and superblock operations, path and inode operations, file and mmap operations, task/credential operations, SysV IPC, process attributes, secctx conversion, notifications, network/socket flows, TUN/SCTP/MPTCP/InfiniBand/XFRM, keys, audit rules, BPF objects/tokens, lockdown, block devices, perf events, io_uring, and initramfs notification.

## Control Flow
Most wrappers are intentionally thin:

1. The target subsystem calls a `security_*()` function before or after a kernel operation.
2. The wrapper applies common framework checks, such as `IS_PRIVATE()` bypasses for private inodes, blob allocation, xattr capability prechecks, or user-buffer validation.
3. The wrapper dispatches to one or more LSM hooks through static calls.
4. The first non-default int hook return normally terminates the chain; void hooks fan out to all active LSMs.
5. Allocation wrappers unwind by invoking the corresponding free routine if hook initialization fails.

Special aggregation paths differ from the default `call_int_hook()` behavior:

- `security_vm_enough_memory_mm()` asks every `vm_enough_memory` hook whether `CAP_SYS_ADMIN` should be considered for overcommit accounting, clearing the privilege if any hook returns negative.
- `security_fs_context_parse_param()` treats `-ENOPARAM` as "not consumed" and continues, but returns any other negative error immediately.
- `security_sb_set_mnt_opts()` starts with `-EOPNOTSUPP` when binary mount options exist and stops when a hook returns a non-default value.
- `security_inode_init_security()` allocates an xattr array sized by `blob_sizes.lbs_xattr_count`, lets each LSM fill reserved slots, treats `-EOPNOTSUPP` as non-fatal, then calls the filesystem `initxattrs()` callback once.
- `security_inode_rename()` runs the hook in both directions for `RENAME_EXCHANGE`.
- `security_inode_setxattr()` and `security_inode_removexattr()` optionally perform capability checks unless an LSM's `inode_xattr_skipcap` hook says the LSM will fully mediate that xattr.
- `security_task_prctl()` lets multiple LSMs observe `prctl`; it remembers handled zero returns but stops on non-zero handled results.
- `security_getselfattr()` can aggregate multiple LSM records into a user buffer or select a single LSM via `LSM_FLAG_SINGLE`.
- `security_setselfattr()` validates a copied `struct lsm_ctx` length and dispatches to the hook whose LSM id matches the supplied id.
- `security_getprocattr()` and `security_setprocattr()` return from the first matching LSM id.
- `security_xfrm_state_pol_flow_match()` intentionally uses the first provider because current semantics expect a boolean judgement and only SELinux supplies it.

## State and Persistence Behavior
The file allocates in-memory security blobs attached to kernel object lifetimes. There is no on-disk persistence here; durable state is mediated by downstream LSMs, filesystem xattrs, policy stores, audit records, or subsystem-specific storage.

Important lifetime rules:

- Inode blobs use `call_rcu()` in `security_inode_free()` because path walks may still call `security_inode_permission()` while inode release is in progress. LSMs that retain inode state needed during RCU walks must defer their final release to `inode_free_security_rcu`.
- File, backing-file, task, cred, IPC, key, socket, BPF, block-device, and perf blobs are cleared after hook-specific free notifications.
- Allocation/initialization functions pair `lsm_*_alloc()` with the relevant `*_alloc_security` hook and call the matching `security_*_free()` on failure.
- `security_backing_file_alloc()` warns LSMs not to keep a reference to `user_file`, because stacked-filesystem backing files can otherwise form reference cycles.
- `security_bdev_setintegrity()` explicitly documents that block-device integrity data can change after the bdev blob is allocated and must be refreshed when dm-verity or similar mappings are reloaded.

## Dependencies and Integration Points
`security.c` depends heavily on generated hook definitions in `linux/lsm_hook_defs.h`, static calls/static keys, the LSM initialization code that populates hook slots and blob sizes, slab allocators, RCU, VFS, fs_context, credentials, IPC, sockets, XFRM, BPF, audit, perf, keyrings, and io_uring.

Important outward integrations:

- VFS/file systems: superblock, mount options, path, inode, xattr, ACL, copy-up, kernfs, and file hooks.
- Distributed or network filesystems: security context notification and get/set hooks used by NFS-like servers/clients; CephFS can pass through generic inode/file/xattr mediation.
- Networking: socket lifecycle, packet receive, secmark, TUN, SCTP, MPTCP, AF_UNIX, XFRM/IPsec, and flow secids.
- Userspace ABI: `getselfattr`, `setselfattr`, `/proc/*/attr`, secctx conversion, `SO_GETPEERSEC`, audit rules, and syscall mediation for BPF, perf, keyrings, io_uring, and module/data loading.

## Risks and Edge Cases
- Static-call dispatch depends on hook table setup matching `MAX_LSM_COUNT`; misregistration could silently skip or misroute hooks.
- The "first non-default return wins" policy means hook ordering is security-significant.
- User ABI helpers must maintain strict length, alignment, and overflow checks; `security_setselfattr()` uses `check_add_overflow()` to prevent malformed `lsm_ctx` records.
- `IS_PRIVATE()` bypasses are intentional but dangerous if a filesystem incorrectly marks objects private.
- Inode RCU freeing is subtle; freeing module-private inode state in the early free hook can race permission checks.
- Xattr skip-cap hooks shift responsibility from common capability checks to LSM-specific enforcement.
- `mmap_prot()` changes effective protections under `READ_IMPLIES_EXEC`, except on noexec paths, so hook implementers must inspect both requested and effective protections.
- Several hooks are callable in atomic or interrupt-like contexts, such as socket receive and task/file signal paths; LSM implementations must not sleep when callers forbid it.

## Test Signals
Useful validation signals include kernel LSM selftests, filesystem xattr and mount-option tests, overlayfs copy-up tests, NFS/CephFS label propagation tests, binder and ptrace policy tests, BPF token/object creation tests, network secmark and SO_PEERSEC tests, XFRM labeled IPsec tests, and fault-injection coverage for blob allocation unwind. Build coverage should include configurations with and without `CONFIG_SECURITY_PATH`, `CONFIG_SECURITY_NETWORK`, `CONFIG_KEYS`, `CONFIG_BPF_SYSCALL`, `CONFIG_AUDIT`, `CONFIG_PERF_EVENTS`, and `CONFIG_IO_URING`.
