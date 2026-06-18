# Research: subset-b-006344

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/security.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/security.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/Kconfig -->
# sources/distributed-fs/ceph-client/security/selinux/Kconfig

## Purpose
This Kconfig fragment defines the build-time configuration surface for SELinux support in the kernel tree. It controls whether SELinux is built, whether it can be disabled at boot, whether development/permissive support is enabled, whether AVC statistics are exposed, and the sizes of internal SELinux hash/cache structures.

## Important Options
- `SECURITY_SELINUX`: top-level SELinux enable. It depends on `SECURITY_NETWORK`, `AUDIT`, `NET`, and `INET`, selects `NETWORK_SECMARK`, and defaults to off.
- `SECURITY_SELINUX_BOOTPARAM`: adds the `selinux=` boot parameter, allowing `selinux=0` to disable SELinux at boot.
- `SECURITY_SELINUX_DEVELOP`: enables development support, defaults to on, and starts permissive unless `enforcing=1` is passed.
- `SECURITY_SELINUX_AVC_STATS`: enables per-CPU AVC statistics visible through selinuxfs.
- `SECURITY_SELINUX_SIDTAB_HASH_BITS`: controls sidtab bucket count as `2^bits`, range 8..13, default 9.
- `SECURITY_SELINUX_SID2STR_CACHE_SIZE`: sizes the SID-to-context string cache, default 256, with zero disabling it.
- `SECURITY_SELINUX_AVC_HASH_BITS`: controls AVC hash buckets as `2^bits`, range 9..14, default 9.
- `SECURITY_SELINUX_DEBUG`: enables SELinux debug code and is intended for developers, often combined with dynamic debug.

## Control Flow and Build Effects
Kconfig does not execute runtime logic itself. It emits configuration symbols consumed by the SELinux Makefile and C code. `SECURITY_SELINUX` controls whether `selinux.o` is linked. The hash-size symbols compile into sidtab and AVC constants, and `SECURITY_SELINUX_AVC_STATS` toggles stats increments and exported selinuxfs data. `SECURITY_SELINUX_DEVELOP` and boot parameter options influence initialization and runtime enforcement toggles elsewhere in SELinux code.

## State and Persistence Behavior
The file defines compile-time defaults only. Resulting kernel config persists in the kernel build configuration. Runtime SELinux policy, enforcing state, AVC entries, and sidtab contents are handled by other SELinux components and by boot/runtime settings.

## Dependencies and Integration Points
SELinux is made dependent on networking and audit support, reflecting that SELinux hooks include network labeling/secmark behavior and audit logging. `NETWORK_SECMARK` is selected to support packet labeling. Dynamic debug documentation is referenced for debug output control.

## Risks and Edge Cases
- Enabling `SECURITY_SELINUX_BOOTPARAM` permits disabling SELinux via kernel command line, which is useful for distributable kernels but weakens mandatory enablement.
- `SECURITY_SELINUX_DEVELOP=y` defaults to permissive behavior unless overridden, which is appropriate for policy development but risky in production defaults.
- Too-small sidtab or AVC hash settings can increase chain lengths and lookup latency; too-large settings consume more memory.
- `SECURITY_SELINUX_AVC_STATS` adds stats overhead, small but present on hot permission paths.

## Test Signals
Validation includes Kconfig dependency resolution, builds with SELinux on/off, boot tests for `selinux=0` and `enforcing=1`, selinuxfs visibility for `/sys/fs/selinux/avc/cache_stats` and sidtab stats, and performance tests under different `*_HASH_BITS` settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/Makefile -->
# sources/distributed-fs/ceph-client/security/selinux/Makefile

## Purpose
This Makefile describes how SELinux is built inside the kernel tree. It links SELinux objects into `selinux.o`, configures include paths and debug flags, conditionally adds feature objects, and builds/runs the host-side `genheaders` utility that generates `flask.h` and `av_permissions.h`.

## Important Targets and Variables
- `obj-$(CONFIG_SECURITY_SELINUX) := selinux.o`: builds SELinux only when configured.
- `ccflags-y`: adds SELinux source and include directories.
- `ccflags-$(CONFIG_SECURITY_SELINUX_DEBUG) += -DDEBUG`: enables debug preprocessor paths.
- `selinux-y`: core SELinux object list, including `avc.o`, hooks, selinuxfs, netlink, networking tables, status/initcalls, and security-server (`ss/`) policy database objects.
- Conditional objects: `xfrm.o`, `netlabel.o`, `ibpkey.o`, and `ima.o`.
- `genhdrs := flask.h av_permissions.h`: generated header outputs.
- `hostprogs := genheaders`: builds the generator as a host tool.
- `HOST_EXTRACFLAGS`: provides the host tool with SELinux include paths.

## Control Flow
The kernel build system evaluates `selinux-y`, compiles the listed objects, and links them into `selinux.o`. Before SELinux objects are built, the Makefile requires generated headers. Because older make versions lack grouped targets, the dependency is anchored on `$(obj)/flask.h`; invoking that rule runs `genheaders` and writes both `flask.h` and `av_permissions.h`.

The comments document a future simplification once GNU make 4.3 grouped targets are required: all generated headers could be modeled as one grouped target and all object files could depend directly on both outputs.

## State and Persistence Behavior
The Makefile creates generated build artifacts in the object tree, not persistent source files. The generated headers are derived from SELinux class and permission maps. Incremental rebuild correctness depends on kbuild's `if_changed` tracking and the declared target/dependency relationships.

## Dependencies and Integration Points
It integrates with kbuild variables (`obj-*`, `ccflags-*`, `targets`, `hostprogs`, `quiet_cmd_*`, `cmd_*`) and with SELinux source files that include generated `flask.h` and `av_permissions.h`. Conditional object inclusion follows kernel config symbols for XFRM, NetLabel, InfiniBand, and IMA.

## Risks and Edge Cases
- The single-output dependency workaround can be fragile if generated-header dependencies change and kbuild does not notice all consumers.
- `genheaders` must run on the build host, so host compiler flags and include paths must remain valid for non-target compilation.
- Adding new SELinux source files that depend on generated headers requires they be included in `selinux-y` or otherwise covered by the dependency rule.
- Conditional feature objects must stay aligned with Kconfig dependencies and C preprocessor guards.

## Test Signals
Useful checks include clean and incremental kernel builds with `CONFIG_SECURITY_SELINUX=y`, toggling `CONFIG_SECURITY_SELINUX_DEBUG`, building feature combinations for XFRM/NetLabel/InfiniBand/IMA, verifying `flask.h` and `av_permissions.h` regeneration after classmap changes, and checking parallel builds for missing generated-header races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/avc.c -->
# sources/distributed-fs/ceph-client/security/selinux/avc.c

## Purpose
`avc.c` implements SELinux's Access Vector Cache (AVC), the hot-path cache for policy decisions keyed by source SID, target SID, and target class. It avoids repeated security-server lookups, supports extended permissions such as ioctl command sets, audits grants/denials according to policy, and flushes or updates cached decisions when policy changes.

## Important APIs, Types, and Data
Core structures:

- `struct avc_entry`: cache payload: source SID, target SID, class, `struct av_decision`, and optional extended-permission node.
- `struct avc_node`: RCU-protected hlist node wrapping an `avc_entry`.
- `struct avc_xperms_node`: extended permission metadata plus a list of decisions.
- `struct avc_xperms_decision_node`: one extended permission decision, including allowed/auditallow/dontaudit bitmaps.
- `struct avc_cache`: hash slots, per-slot spinlocks for writers, LRU hint, active node count, and latest policy notification sequence.
- `struct selinux_avc`: top-level cache threshold plus `avc_cache`.

Public or externally used functions:

- `selinux_avc_init()`: initializes slots, locks, threshold, and counters.
- `avc_get_cache_threshold()` / `avc_set_cache_threshold()`: expose runtime cache threshold control.
- `avc_init()`: creates slab caches for AVC nodes and extended permission structures.
- `avc_get_hash_stats()`: formats cache occupancy and chain-length stats.
- `avc_add_callback()`: registers policy-change callbacks during init.
- `avc_ss_reset()`: flushes cache, runs reset callbacks, and records latest policy sequence.
- `avc_has_perm_noaudit()`: checks ordinary permissions without audit.
- `avc_has_perm()`: checks ordinary permissions and performs policy-directed audit.
- `avc_has_extended_perms()`: checks base access plus extended permission bitmaps.
- `avc_policy_seqno()`: returns latest policy sequence notification.

## Control Flow
Ordinary permission checking:

1. `avc_has_perm()` calls `avc_has_perm_noaudit()`.
2. `avc_has_perm_noaudit()` looks up `(ssid, tsid, tclass)` under RCU.
3. On hit, it copies `av_decision`, computes denied bits, drops RCU, and calls `avc_denied()` if needed.
4. On miss, it drops RCU and calls `avc_perm_nonode()`, which computes a decision through `security_compute_av()`, inserts it with `avc_insert()`, and evaluates denied bits.
5. `avc_has_perm()` then calls `avc_audit()` to emit audit records when policy says auditallow or auditdeny applies.

Extended permission checking:

1. `avc_has_extended_perms()` looks up or computes the base decision and associated `extended_perms`.
2. If no extended permissions apply, it falls back to the base decision.
3. If a requested driver/base permission decision is absent but the driver and base are known, it computes the extended decision via `security_compute_xperms_decision()`.
4. The computed extended decision is added to the cache with `avc_update_node(AVC_CALLBACK_ADD_XPERMS, ...)`.
5. The requested xperm bit is checked against allowed/dontaudit/auditallow bitmaps before denial and audit.

Cache mutation:

- `avc_insert()` rejects stale decisions with `avc_latest_notif_update()`, allocates a node, deep-copies extended permissions, then inserts or replaces under the per-bucket spinlock.
- `avc_update_node()` allocates a replacement node, finds an existing node with matching seqno, copies the old decision, mutates grant/revoke/audit bits or extended permissions, and replaces the old node with RCU.
- `avc_flush()` walks every bucket under locks and deletes nodes with RCU callbacks.
- `avc_reclaim_node()` scans buckets using `lru_hint` and trylocks, reclaiming up to `AVC_CACHE_RECLAIM` nodes when the active count exceeds the threshold.

Audit flow:

- `avc_xperms_audit_required()` combines requested, allowed, auditallow, auditdeny, dontaudit, result, and extended permission information to decide whether to audit.
- `slow_avc_audit()` builds `selinux_audit_data`, then calls generic `common_lsm_audit()` with SELinux pre/post callbacks.
- Pre-callback prints permission names from `secclass_map`; post-callback translates SIDs to contexts, emits class and permissive status, traces `selinux_audited`, and includes raw invalid contexts when available.

## State and Persistence Behavior
The AVC is a volatile in-kernel cache. It persists only until cache reclaim, policy reset, or system shutdown. Policy sequence numbers prevent old decisions from being inserted after a newer revocation notification. Cache nodes are RCU-freed to allow lockless readers. Extended permission payloads are separately slab-allocated and deep-copied because they can be chained and selectively added after a base AVC entry exists.

The cache threshold defaults to the number of hash slots, `1 << CONFIG_SECURITY_SELINUX_AVC_HASH_BITS`, and can be changed at runtime by SELinux filesystem control paths. When `CONFIG_SECURITY_SELINUX_AVC_STATS` is enabled, per-CPU counters record lookups, misses, allocations, frees, and reclaims.

## Dependencies and Integration Points
`avc.c` depends on SELinux security-server APIs such as `security_compute_av()`, `security_compute_xperms_decision()`, SID-to-context translation, enforcing/permissive state, class/permission maps, and xperm bit helpers. It integrates with generic LSM audit via `common_lsm_audit()`, Linux audit buffers, tracepoints in `trace/events/avc.h`, RCU, hlist, spinlocks, slab caches, and selinuxfs status/stat display paths.

## Risks and Edge Cases
- RCU readers and per-bucket writers require strict copy-replace discipline; in-place mutation of visible nodes would race readers.
- `avc_update_node()` requires a matching decision seqno, so stale update notifications fail with `-ENOENT`.
- Extended permission allocation uses `GFP_NOWAIT`; memory pressure can skip caching or fail xperm update paths.
- `avc_denied()` grants denied permissions into the cache in permissive mode unless `AVC_STRICT` is set, which is intentional but must not leak into enforcing decisions after policy changes.
- Class index use in audit callbacks assumes valid nonzero `tclass`; `slow_avc_audit()` warns and returns `-EINVAL` for invalid classes.
- Reclaim is approximate and trylock-based, so active node count can remain above threshold transiently.

## Test Signals
Validation should cover cache hits and misses, policy reload flushing, revocation sequence ordering, permissive vs enforcing denial results, `AVC_STRICT`, extended ioctl-style permissions, auditallow/auditdeny/dontaudit combinations, selinuxfs cache stats/hash stats, tracepoint emission, and fault injection for slab allocation failures. Concurrency tests should stress RCU readers while policy reloads, grants/revokes, and threshold-driven reclaim occur.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/avc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/genheaders.c -->
# sources/distributed-fs/ceph-client/security/selinux/genheaders.c

## Purpose
`genheaders.c` is a host-side build utility that generates SELinux C headers from static class, permission, and initial SID maps. It writes `flask.h` with security class and initial SID constants plus a socket-class helper, and `av_permissions.h` with per-class permission bit definitions.

## Important APIs, Types, and Functions
The local `struct security_class_mapping` mirrors the class map shape used by `classmap.h`: a class name and up to one machine-word worth of permission strings plus a terminator. The program includes `classmap.h` and `initial_sid_to_string.h` directly so generated values stay aligned with policy maps.

Functions:

- `usage()` prints expected arguments (`flask.h av_permissions.h`) and exits with code 1.
- `stoupperx()` duplicates a string, uppercases it in place, exits with code 3 on allocation failure, and returns caller-owned memory.
- `main()` validates arguments, writes both output headers, checks close errors, and exits with specific error codes for open/close and permission overflow failures.

## Control Flow
The program expects two output paths. It first opens `argv[1]` and writes:

1. generated-file guard text;
2. `SECCLASS_*` constants numbered from 1 in `secclass_map` order;
3. `SECINITSID_*` constants for non-null initial SID strings;
4. `SECINITSID_NUM`;
5. `security_is_socket_class()`, generated by selecting every class whose uppercase name ends with `SOCKET`.

It then closes the first file, opens `argv[2]`, and writes:

1. generated-file guard text;
2. for each class permission, a macro named `<CLASS>__<PERM>`;
3. a 32-bit access-vector bit value `1U << j`.

If a class has permission index `j >= 32`, it reports the offending class/permission and exits because an access vector cannot represent it.

## State and Persistence Behavior
This is a deterministic generator with no persistent state beyond its two output files. It allocates temporary uppercase strings with `strdup()` and frees them after each macro emission. Failed opens or close errors terminate the build with non-zero status. Partial output files can exist if the host process fails mid-write; kbuild's generated-target machinery is responsible for rerunning it.

## Dependencies and Integration Points
The Makefile builds this as a host program, not as target kernel code. It depends on standard C library headers and on SELinux source headers `classmap.h` and `initial_sid_to_string.h`. Generated headers are consumed by SELinux kernel code for class constants, initial SID constants, permission bit masks, and socket class tests.

## Risks and Edge Cases
- `toupper()` is called on `char` values without an unsigned cast; non-ASCII signed chars would be undefined behavior, but SELinux class/permission identifiers are expected to be ASCII.
- Only `argc < 3` is rejected; extra arguments are ignored.
- Header writes are direct `fopen("w")` writes, so interruption can leave partial files until the build regenerates them.
- The permission limit is hard-coded to 32 bits per class, matching access-vector width.
- Socket-class detection is string-suffix based, so class naming conventions must stay stable.

## Test Signals
Useful tests include running the generator on the current maps and comparing output to expected `flask.h` and `av_permissions.h`, adding a synthetic class with more than 32 permissions to confirm failure, checking generated include guards and numbering stability, and verifying that every socket-suffixed class appears in `security_is_socket_class()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/genheaders.c -->
