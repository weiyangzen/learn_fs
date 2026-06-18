# sources/distributed-fs/ceph-client/security/selinux grouped research: subset-b-006345

Work item `subset-b-006345` covers SELinux hook implementation, Infiniband P_Key and IMA helpers, and the local headers that define SELinux object-security blobs, class maps, policy capabilities, network-cache interfaces, and audit/AVC entry points.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/hooks.c -->
## sources/distributed-fs/ceph-client/security/selinux/hooks.c

### Purpose
`hooks.c` is the central SELinux LSM integration file. It defines the global `selinux_state`, boot parameter handling, SELinux LSM blob sizes, the `selinux_hooks[]` registration table, early LSM initialization, and hook implementations for process, filesystem, inode, file, socket, IPC, key, Infiniband, BPF, perf, io_uring, audit, and netfilter paths. In this Ceph client source tree it is a mostly upstream SELinux kernel module source, not Ceph-specific logic, but it governs how Ceph or any other client code is mediated by SELinux labels.

### Important APIs, types, and functions
The file registers `DEFINE_LSM(selinux)` with `selinux_init`, `selinux_blob_sizes`, and `selinux_hooks`. It exposes `selinux_complete_init()` and `selinux_nf_ip_init()`, and implements hook families such as `selinux_bprm_creds_for_exec`, `selinux_inode_permission`, `selinux_file_open`, `selinux_socket_bind`, `selinux_socket_sock_rcv_skb`, `selinux_netlink_send`, `selinux_getselfattr`, `selinux_setselfattr`, `selinux_ib_pkey_access`, `selinux_bpf_*`, `selinux_perf_event_*`, and `selinux_uring_*`. Reusable helper flows include `cred_has_capability`, `inode_has_perm`, `file_has_perm`, `may_create`, `may_link`, `may_rename`, `superblock_has_perm`, `socket_type_to_security_class`, `selinux_determine_inode_label`, and the task-local directory AVD cache helpers.

### Control flow
Early boot parses `enforcing=`, `selinux=`, and legacy `checkreqprot=` parameters, initializes credentials for the initial task, initializes AVC/security-server caches, registers hooks, and attaches AVC reset callbacks. Permission paths generally collect source SID, target SID, target class, requested access vector, and audit data, then call `avc_has_perm()` or `avc_has_perm_noaudit()` plus `avc_audit()`. Filesystem mount setup parses SELinux mount options, resolves contexts to SIDs, checks relabel permissions, selects labeling behavior (`XATTR`, `GENFS`, `MNTPOINT`, `NATIVE`, etc.), and initializes delayed inode labels after policy load. Inode and file operations translate VFS operations to class permissions and revalidate when inode SIDs or policy sequence numbers change. Networking maps socket families/protocols to SELinux socket classes, checks bind/connect node and port labels, resolves peer labels from NetLabel/XFRM, applies secmark checks, and registers IPv4/IPv6 netfilter hooks.

### State and persistence
State lives primarily in LSM security blobs described by `selinux_blob_sizes`: credentials, tasks, files, backing files, inodes, IPC objects, keys, messages, sockets, superblocks, TUN devices, Infiniband objects, BPF objects, BPF tokens, and optional perf events. Superblocks retain SID, default SID, mountpoint SID, creator SID, labeling behavior, mount-option flags, locks, and lists of inodes awaiting initialization. File blobs cache the opener SID, inode SID at open, file owner SID, and policy sequence number. Task blobs include a tiny directory AVD cache invalidated by SID or policy sequence changes. Persistent labels are generally stored in `security.selinux` xattrs or produced by genfs/security-server mappings; in-memory labels are revalidated and flushed on policy changes.

### Dependencies and integration points
The file depends on the SELinux AVC and security server (`avc.h`, `security.h`, `avc_ss.h`), object security accessors from `objsec.h`, network caches (`netif.h`, `netnode.h`, `netport.h`), Infiniband P_Key lookup (`ibpkey.h`), XFRM, NetLabel, audit helpers, generated Flask class/permission headers, and kernel subsystems through LSM hook prototypes. It integrates with `selinuxfs` through attr/secctx hooks, with audit through `common_audit_data`, with netfilter through `nf_hook_ops`, with BPF token semantics through bpffs creator SIDs, and with IMA indirectly through policy load paths in the security server.

### Risks
This file has high blast radius. Risks include missing class/permission updates when kernel object families evolve, policy capability conditionals preserving old behavior in surprising ways, mount option compatibility mistakes causing mislabeled filesystems, races around deferred inode initialization, stale file access after policy or label changes, network label inconsistencies between secmark/NetLabel/XFRM, and subtle behavior changes in exec transitions under `no_new_privs` or nosuid. Compile-time guards cover some expansion risks, for example capability count, address family count, read/load enum count, and filesystem behavior count.

### Test signals
Useful signals include SELinux LTP tests, boot with SELinux enforcing/permissive/disabled, policy reload and AVC reset tests, xattr/genfs/mount option labeling tests, exec transition and dynamic transition tests, file-open revalidation tests, NetLabel/XFRM/secmark packet tests, SCTP/MPTCP socket tests, audit-rule invalidation tests, BPF token and fd-passing tests, and kernel builds across configs (`CONFIG_NETLABEL`, `CONFIG_NETFILTER`, `CONFIG_SECURITY_INFINIBAND`, `CONFIG_BPF_SYSCALL`, `CONFIG_KEYS`, `CONFIG_PERF_EVENTS`, `CONFIG_IO_URING`).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/hooks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ibpkey.c -->
## sources/distributed-fs/ceph-client/security/selinux/ibpkey.c

### Purpose
`ibpkey.c` implements SELinux's fast cache from Infiniband subnet prefix plus P_Key number to a policy SID. P_Key labels are policy-managed, but per-operation lookups need a bounded RCU-friendly cache similar to SELinux netif/netnode/netport caches.

### Important APIs, types, and functions
The exported APIs are `sel_ib_pkey_sid(u64 subnet_prefix, u16 pkey_num, u32 *sid)`, `sel_ib_pkey_flush()`, and `sel_ib_pkey_init()`. Internal types are `struct sel_ib_pkey_bkt`, which tracks a bucket list and size, and `struct sel_ib_pkey`, which embeds `struct pkey_security_struct`, a list node, and an RCU head. Helper functions include `sel_ib_pkey_hashfn`, `sel_ib_pkey_find`, `sel_ib_pkey_insert`, and `sel_ib_pkey_sid_slow`.

### Control flow
The fast path takes `rcu_read_lock()`, searches the bucket selected by the P_Key number, and returns the cached SID on hit. On miss, the slow path takes `sel_ib_pkey_lock`, repeats the lookup to avoid duplicate inserts, asks the security server through `security_ib_pkey_sid()`, and inserts a newly allocated cache entry if allocation succeeds. Bucket growth is bounded by `SEL_PKEY_HASH_BKT_LIMIT`; inserting at a full bucket evicts the tail with `list_del_rcu()` and `kfree_rcu()`.

### State and persistence
The cache is in-memory only: a static 256-bucket hash table plus one spinlock. Policy remains authoritative, and cache state is flushed by `sel_ib_pkey_flush()` on policy reset through `hooks.c`'s AVC callback. Allocation failure after a successful policy lookup does not fail the access path; the SID is returned but not cached.

### Dependencies and integration points
This file depends on Linux RCU/list/spinlock primitives, `initcalls.h`, `ibpkey.h`, `objsec.h`, and the security server function `security_ib_pkey_sid()`. It is consumed by `selinux_ib_pkey_access()` in `hooks.c`, which audits and checks `INFINIBAND_PKEY__ACCESS` against the returned P_Key SID.

### Risks
The hash function only uses the P_Key number, so many subnets with the same P_Key can collide. The bounded bucket eviction policy is simple FIFO-by-tail and can churn under adversarial or very large P_Key sets. Correctness depends on policy reset flushing the cache; stale entries would otherwise carry old SID decisions.

### Test signals
Exercise cache hit/miss behavior with repeated P_Key access, policy reload flushing, failure handling with allocation pressure, and multi-subnet same-P_Key collisions. Build coverage requires `CONFIG_SECURITY_INFINIBAND`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ibpkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ima.c -->
## sources/distributed-fs/ceph-client/security/selinux/ima.c

### Purpose
`ima.c` measures SELinux critical state into IMA: initialization state, enforcing mode, checkreqprot value, policy capability booleans, and the loaded policy hash. This lets integrity/audit infrastructure detect policy and state changes relevant to SELinux enforcement.

### Important APIs, types, and functions
The exported functions are `selinux_ima_measure_state()` and `selinux_ima_measure_state_locked()`. The internal helper `selinux_ima_collect_state()` builds a semicolon-delimited state string such as `initialized=1;enforcing=1;...policycap=0;` using `selinux_policycap_names[]` and `selinux_state.policycap[]`.

### Control flow
`selinux_ima_measure_state()` asserts the policy mutex is not already held, locks `selinux_state.policy_mutex`, delegates to the locked variant, and unlocks. The locked variant asserts the mutex is held, builds the state string, measures it as `selinux-state`, frees it, then returns early if SELinux is not initialized. Once initialized, it reads the kernel policy via `security_read_state_kernel()`, measures it as `selinux-policy-hash` with hashing enabled, and frees the vmalloc policy buffer.

### State and persistence
The file does not persist state itself. It snapshots live SELinux state and policy bytes into IMA measurements. Memory ownership is explicit: `kzalloc`/`kfree` for the state string and `security_read_state_kernel()`/`vfree()` for the policy buffer.

### Dependencies and integration points
It depends on IMA (`<linux/ima.h>`), vmalloc freeing, `security.h`, and `ima.h`. `selinuxfs.c` and security-server policy load paths call these functions to measure SELinux state after user-visible state or policy changes.

### Risks
Buffer length calculation must stay aligned with policy capability names and fixed state keys. Missing a new state knob would weaken integrity coverage. Locking discipline matters: policy bytes and policycap state must be read under `policy_mutex` for coherent measurement.

### Test signals
Run with `CONFIG_IMA`, load policy, toggle enforcing/booleans/policy capabilities where possible, and verify IMA contains `selinux-state` and `selinux-policy-hash` records. Also test allocation/read failures for logged errors without leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ima.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/audit.h -->
## sources/distributed-fs/ceph-client/security/selinux/include/audit.h

### Purpose
`audit.h` declares SELinux support routines for Linux audit LSM rules. These routines let audit rules parse SELinux context fields, match task/object LSM properties, free rule-private memory, and update audit rule caches when AVC policy state changes.

### Important APIs, types, and functions
The interface consists of `selinux_audit_rule_avc_callback(u32 event)`, `selinux_audit_rule_init(u32 field, u32 op, char *rulestr, void **rule, gfp_t gfp)`, `selinux_audit_rule_free(void *rule)`, `selinux_audit_rule_match(struct lsm_prop *prop, u32 field, u32 op, void *rule)`, and `selinux_audit_rule_known(struct audit_krule *rule)`.

### Control flow
Audit setup code calls `*_init` to allocate and translate a textual SELinux rule target. Runtime audit matching passes an `lsm_prop` to `*_match`, while rule teardown calls `*_free`. AVC reset events call the callback to invalidate or refresh rule state after policy changes.

### State and persistence
The header owns no state, but documents that rule structures are allocated internally and must be released by the caller. Rule validity depends on the loaded SELinux policy and therefore on AVC reset handling.

### Dependencies and integration points
It includes kernel audit and type headers and is wired into `hooks.c` under `CONFIG_AUDIT` via audit hook registrations and AVC callback registration.

### Risks
Incorrect lifetime handling can leak rule memory or leave stale SIDs after policy reload. Match semantics must remain synchronized with `struct lsm_prop` and audit field/operator definitions.

### Test signals
Build with `CONFIG_AUDIT`; add audit rules using SELinux subject/object fields; reload policy and verify rules still match or are invalidated correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/audit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/avc.h -->
## sources/distributed-fs/ceph-client/security/selinux/include/avc.h

### Purpose
`avc.h` defines the object-manager-facing Access Vector Cache interface. It is the main boundary between SELinux hook implementations and cached security-server decisions, including audit calculation and callback registration.

### Important APIs, types, and functions
Important declarations include `avc_init`, `avc_has_perm_noaudit`, `avc_has_perm`, `avc_has_extended_perms`, `avc_policy_seqno`, `avc_add_callback`, AVC stats helpers, and cache threshold helpers. `struct avc_cache_stats` tracks cache counters. `struct selinux_audit_data` records source SID, target SID, class, requested/audited/denied masks, and result. Inline `avc_audit_required()` computes whether an access decision requires audit; inline `avc_audit()` invokes `slow_avc_audit()` when needed.

### Control flow
Hook code usually calls `avc_has_perm()` for check plus audit or `avc_has_perm_noaudit()` when checks must happen under locks, followed by `avc_audit()` after locks are released. `avc_audit_required()` suppresses audit for `AVD_FLAGS_NEVERAUDIT`, distinguishes denial audit from allow audit, and honors dontaudit-style `auditdeny` filtering.

### State and persistence
The header declares interfaces to global AVC cache state, policy sequence numbers, callback lists, and optional per-CPU stats. It stores no state directly.

### Dependencies and integration points
It depends on generated Flask class and permission headers, SELinux security server types, Linux audit/LSM audit structures, and is included by `hooks.c`, `objsec.h`, NetLabel interfaces, and AVC implementation files.

### Risks
Audit logic is subtle: `auditdeny` filtering is intentionally not a direct denied-permission mask. Callers that skip post-check auditing or pass incomplete audit data can lose important diagnostics. Policy sequence number users must revalidate cached decisions.

### Test signals
Test AVC allow/deny, permissive domain behavior, dontaudit/noaudit cases, extended ioctl/netlink permissions, policy reload sequence changes, cache stats, and callback execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/avc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/avc_ss.h -->
## sources/distributed-fs/ceph-client/security/selinux/include/avc_ss.h

### Purpose
`avc_ss.h` is the security-server-facing AVC interface. It exposes AVC reset support and the class/permission mapping table needed by the security server and generated header tools.

### Important APIs, types, and functions
It declares `avc_ss_reset(u32 seqno)` and `struct security_class_mapping`, whose `name` identifies a class and whose `perms` array contains up to 32 permission names plus a null terminator. It also declares `extern const struct security_class_mapping secclass_map[]`.

### Control flow
The security server calls `avc_ss_reset()` with a policy sequence number when policy state changes. Mapping consumers iterate `secclass_map[]` until the null class entry.

### State and persistence
No state is stored in the header. The mapping table is defined by `classmap.h`, and reset state is maintained by the AVC implementation.

### Dependencies and integration points
This header bridges `classmap.h`, `genheaders.c`, `avc.c`, `services.c`, and `hooks.c` logging paths that need class names.

### Risks
The table shape is ABI-like within the SELinux build. Class ordering and permission ordering must match generated constants and policy expectations.

### Test signals
Regenerate and build SELinux Flask headers; load policy; trigger policy reload and confirm AVC reset and class-name audit formatting continue to work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/avc_ss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/classmap.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/classmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/conditional.h -->
## sources/distributed-fs/ceph-client/security/selinux/include/conditional.h

### Purpose
`conditional.h` declares the security-server interface for SELinux policy booleans. These booleans control conditional policy rules and are exported to selinuxfs.

### Important APIs, types, and functions
The interface includes `security_get_bools(struct selinux_policy *policy, u32 *len, char ***names, int **values)`, `security_set_bools(u32 len, const int *values)`, and `security_get_bool_value(u32 index)`.

### Control flow
Consumers ask for the current policy's boolean list and values, update values by index array, or query one boolean by index. The implementation lives in the security server and is synchronized with active policy state.

### State and persistence
This header stores no state. Boolean names and values live in policy data structures and active SELinux state. Persistence across boot is userspace policy/configuration responsibility, not this header.

### Dependencies and integration points
It includes `security.h` for `struct selinux_policy` and integrates with selinuxfs boolean files and policy conditional evaluation.

### Risks
Boolean index mismatch between userspace and policy can toggle unintended conditional rules. Callers must handle allocation and lifetime of returned names/values according to the implementation contract.

### Test signals
Read and set booleans through selinuxfs, verify conditional allow rules change as expected, reload policy, and test invalid index/value lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/conditional.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/hash.h -->
## sources/distributed-fs/ceph-client/security/selinux/include/hash.h

### Purpose
`hash.h` supplies a small inline hash helper for SELinux access-vector style keys. It is based on MurmurHash3 mixing and returns a bucket index masked by the caller.

### Important APIs, types, and functions
The only API is `static inline u32 av_hash(u32 key1, u32 key2, u32 key3, u32 mask)`. It mixes three 32-bit keys with constants `c1`, `c2`, rotations, final avalanche steps, and returns `hash & mask`.

### Control flow
The function initializes `hash` to zero, applies the `mix` macro to each input, performs Murmur-style finalization, and masks the result. The caller is expected to pass a mask appropriate for a power-of-two-sized hash table.

### State and persistence
The function is stateless and deterministic. There is no allocation or persistence.

### Dependencies and integration points
It depends only on SELinux/kernel availability of `u32`. It is suitable for AVC or policy data structures that need stable in-kernel hashing.

### Risks
Passing a non-power-of-two-minus-one mask gives a biased but still bounded result. Because the seed is fixed at zero, this is not a hash-flooding defense for untrusted high-volume user keys.

### Test signals
Unit-style tests can verify deterministic output, bucket bounds for expected masks, and collision distribution over representative SID/class/permission triples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/ibpkey.h -->
## sources/distributed-fs/ceph-client/security/selinux/include/ibpkey.h

### Purpose
`ibpkey.h` declares the SELinux Infiniband P_Key SID cache interface and provides no-op fallbacks when Infiniband security is not built.

### Important APIs, types, and functions
Under `CONFIG_SECURITY_INFINIBAND`, it declares `sel_ib_pkey_flush()` and `sel_ib_pkey_sid(u64 subnet_prefix, u16 pkey, u32 *sid)`. Without that config, it provides inline fallbacks where flush does nothing and SID lookup returns `SECINITSID_UNLABELED`.

### Control flow
Callers can unconditionally invoke the functions. The preprocessor chooses the real implementation in `ibpkey.c` or the fallback behavior.

### State and persistence
The header has no state. The real implementation caches P_Key mappings in memory; the fallback deliberately has no cache and treats all P_Keys as unlabeled.

### Dependencies and integration points
It includes Linux types and generated Flask initial SID constants. `hooks.c` uses it in Infiniband access checks and in the AVC reset callback.

### Risks
Fallback unlabeled behavior means builds without `CONFIG_SECURITY_INFINIBAND` cannot enforce policy-distinct P_Key labels. Callers must still check return codes in the real build.

### Test signals
Build both with and without `CONFIG_SECURITY_INFINIBAND`; verify hook compilation and runtime P_Key checks or unlabeled fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/ibpkey.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/ima.h -->
## sources/distributed-fs/ceph-client/security/selinux/include/ima.h

### Purpose
`ima.h` declares SELinux IMA measurement entry points and provides empty stubs when IMA is disabled.

### Important APIs, types, and functions
The APIs are `selinux_ima_measure_state()` and `selinux_ima_measure_state_locked()`. With `CONFIG_IMA`, they are external functions implemented in `ima.c`; otherwise, inline stubs compile away calls.

### Control flow
Callers can measure SELinux state without local `#ifdef` logic. The locked variant requires `selinux_state.policy_mutex` to be held; the unlocked variant handles locking internally.

### State and persistence
No header state exists. Measurements are emitted to IMA only in IMA-enabled builds.

### Dependencies and integration points
It includes `security.h` and is used by selinuxfs and security-server policy paths that need to record SELinux state/policy in IMA.

### Risks
Calling the locked variant without holding the policy mutex violates the implementation's lockdep assertions. Stubbed builds provide no integrity measurement signal.

### Test signals
Build with and without `CONFIG_IMA`; in IMA builds, validate measurement records after policy load or SELinux state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/ima.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/initcalls.h -->
## sources/distributed-fs/ceph-client/security/selinux/include/initcalls.h

### Purpose
`initcalls.h` centralizes SELinux initcall declarations so individual SELinux subsystems can be initialized in the correct boot sequence.

### Important APIs, types, and functions
It declares `init_sel_fs`, `sel_netport_init`, `sel_netnode_init`, `sel_netif_init`, `sel_netlink_init`, `sel_ib_pkey_init`, `selinux_nf_ip_init`, and `selinux_initcall`.

### Control flow
SELinux's LSM initialization references `selinux_initcall` through `.initcall_device`; subsystem init implementations can be linked without circular declarations. Individual cache init functions generally check `selinux_enabled_boot` before allocating or initializing state.

### State and persistence
This header stores no state. It coordinates initialization of selinuxfs, network caches, netlink tables, Infiniband P_Key cache, and netfilter hooks.

### Dependencies and integration points
It is included by `hooks.c`, `ibpkey.c`, and other SELinux subsystem sources that participate in boot-time setup.

### Risks
Missing or misordered init declarations can leave caches or hooks uninitialized while hook code assumes they are available.

### Test signals
Boot SELinux-enabled and disabled kernels, inspect init logs, and verify selinuxfs, netfilter hooks, net caches, netlink, and Infiniband cache setup paths execute or skip as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/initcalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/initial_sid_to_string.h -->
## sources/distributed-fs/ceph-client/security/selinux/include/initial_sid_to_string.h

### Purpose
`initial_sid_to_string.h` maps generated SELinux initial SID numbers to their string names. Initial SIDs label kernel/bootstrap objects before full policy-derived labels are available.

### Important APIs, types, and functions
The file defines `static const char *const initial_sid_to_string[]`. Entries include `kernel`, `security`, `unlabeled`, `file`, `init`, `any_socket`, `port`, `netif`, `netmsg`, `node`, and `devnull`, with null placeholders for obsolete or unnamed initial SIDs.

### Control flow
Consumers index the array by initial SID numeric constant. There is no logic other than compile-time data selection for kernel vs host-program include paths.

### State and persistence
The table is static read-only data. It is part of the generated/compiled SELinux policy interface and must align with initial SID constants.

### Dependencies and integration points
It includes `stddef.h` or kernel `linux/stddef.h`. It is used by SELinux tooling/security-server code that needs textual initial SID names.

### Risks
Array ordering must remain synchronized with `SECINITSID_*` constants. Null placeholders are intentional; consumers must tolerate missing names.

### Test signals
Build generated headers and policy tooling, verify initial SID string lookups, and test boot labels before policy load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/initial_sid_to_string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/netif.h -->
## sources/distributed-fs/ceph-client/security/selinux/include/netif.h

### Purpose
`netif.h` declares the SELinux network-interface SID cache API. Network devices do not carry SELinux security blobs, so SELinux maintains a separate namespace/interface-index to SID mapping.

### Important APIs, types, and functions
The interface has `sel_netif_flush()` and `sel_netif_sid(struct net *ns, int ifindex, u32 *sid)`.

### Control flow
Network hook paths call `sel_netif_sid()` during ingress/egress checks to obtain the interface SID and then perform `NETIF__INGRESS` or `NETIF__EGRESS` AVC checks. Policy reset paths call `sel_netif_flush()`.

### State and persistence
The header stores no state. The implementation maintains an in-memory cache derived from policy, keyed by network namespace and ifindex.

### Dependencies and integration points
It includes `net/net_namespace.h` and is used by `hooks.c` netfilter and socket receive paths.

### Risks
Interface rename/reindex and network namespace lifetime handling must be correct in the implementation. Stale entries after policy reload would mislabel network checks.

### Test signals
Exercise packet ingress/egress with labeled interfaces, network namespaces, interface creation/destruction, and policy reload cache flushing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/netif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/netlabel.h -->
## sources/distributed-fs/ceph-client/security/selinux/include/netlabel.h

### Purpose
`netlabel.h` declares SELinux's interface to the NetLabel subsystem and provides no-op fallbacks when NetLabel is disabled. NetLabel carries packet security labels such as CIPSO/CALIPSO across network traffic.

### Important APIs, types, and functions
With `CONFIG_NETLABEL`, the header declares cache invalidation, error reporting, socket security lifecycle helpers, skb SID get/set helpers, SCTP and inet connection setup helpers, socket post-create/connect/setopt helpers, and receive checks. Without NetLabel, inline stubs return neutral values: no label type, null SID, or success.

### Control flow
Socket and netfilter hooks call these helpers while creating sockets, receiving packets, connecting sockets, cloning connections, setting packet labels, and reporting label-related errors. The fallback path lets the rest of SELinux networking compile and execute without NetLabel.

### State and persistence
The header stores no state. Real state is in `sk_security_struct` NetLabel fields and the NetLabel subsystem's own caches/configuration.

### Dependencies and integration points
It includes socket, skb, request_sock, SCTP, AVC, and object-security types. It is tightly integrated with `hooks.c` network receive, connect, SCTP, MPTCP, and netfilter labeling paths.

### Risks
Stub behavior must preserve SELinux semantics when NetLabel is absent. Real builds must avoid stale `nlbl_secattr` data on clone/free/reset and must coordinate NetLabel with XFRM/secmark peer label resolution.

### Test signals
Build with and without `CONFIG_NETLABEL`; test CIPSO/CALIPSO labeling, socket connect and receive checks, SCTP association labeling, packet error handling, and policy/cache invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/netlabel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/netnode.h -->
## sources/distributed-fs/ceph-client/security/selinux/include/netnode.h

### Purpose
`netnode.h` declares the SELinux network-node SID cache API for IP address labels. These lookups are hot in per-packet checks, so implementation-side caching avoids repeated policy lookups.

### Important APIs, types, and functions
The interface has `sel_netnode_flush()` and `sel_netnode_sid(const void *addr, u16 family, u32 *sid)`.

### Control flow
Network receive, bind, and postroute checks call `sel_netnode_sid()` for source or destination addresses, then check node permissions such as `NODE__RECVFROM`, `NODE__SENDTO`, or socket `NODE_BIND`.

### State and persistence
The header has no state. The implementation maintains policy-derived, in-memory address-to-SID cache entries for IPv4/IPv6 families.

### Dependencies and integration points
It depends on Linux scalar types and is consumed by `hooks.c` networking and netfilter paths.

### Risks
Address family parsing and cache invalidation are correctness-sensitive. Unknown or malformed addresses can cause packet drops or unlabeled fallbacks depending on caller behavior.

### Test signals
Test IPv4 and IPv6 node labels, fragmented packet parsing, bind/connect/ingress/egress checks, policy reload flushing, and unknown address family handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/netnode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/netport.h -->
## sources/distributed-fs/ceph-client/security/selinux/include/netport.h

### Purpose
`netport.h` declares the SELinux network-port SID cache API. It maps protocol and port number to a policy SID for socket name-bind/name-connect checks.

### Important APIs, types, and functions
The interface has `sel_netport_flush()` and `sel_netport_sid(u8 protocol, u16 pnum, u32 *sid)`.

### Control flow
`hooks.c` calls `sel_netport_sid()` when binding privileged/out-of-ephemeral-range ports or connecting TCP/SCTP sockets, then checks `SOCKET__NAME_BIND` or `*_SOCKET__NAME_CONNECT` permissions.

### State and persistence
The header has no state. The implementation maintains a bounded in-memory cache derived from policy portcon rules.

### Dependencies and integration points
It includes Linux types and is used by socket bind/connect paths plus AVC reset flushing.

### Risks
Protocol/port mismatches can allow or deny the wrong service label. Ephemeral port range logic lives in callers, so tests must cover both cache and caller thresholds.

### Test signals
Test TCP/UDP/SCTP port label lookups, privileged and non-ephemeral bind checks, name_connect denials, policy reload flushing, and unknown protocol behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/netport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/objsec.h -->
## sources/distributed-fs/ceph-client/security/selinux/include/objsec.h

### Purpose
`objsec.h` defines SELinux security-blob structures for kernel objects and inline accessors that locate SELinux data inside LSM-managed blobs. It is the shared data model used by `hooks.c` and related SELinux subsystems.

### Important APIs, types, and functions
Key structures include `cred_security_struct`, `task_security_struct`, `inode_security_struct`, `file_security_struct`, `backing_file_security_struct`, `superblock_security_struct`, `msg_security_struct`, `ipc_security_struct`, `netif_security_struct`, `netnode_security_struct`, `netport_security_struct`, `sk_security_struct`, `tun_security_struct`, `key_security_struct`, `ib_security_struct`, `pkey_security_struct`, `bpf_security_struct`, and `perf_event_security_struct`. Accessors include `selinux_cred`, `selinux_task`, `selinux_file`, `selinux_inode`, `selinux_superblock`, `selinux_sock`, `selinux_ib`, and BPF/perf/key helpers. `current_sid()` returns the current task's subjective SID.

### Control flow
Hook implementations obtain the relevant blob through these inline accessors, then read or write SIDs, classes, policy sequence numbers, and initialization flags. `task_avdcache_permnoaudit()` is a small inline optimization for permissive/neversaudited directory checks.

### State and persistence
The structures hold in-memory SELinux labels and metadata. They mirror, cache, or derive from persistent policy/xattr state but are not persistent themselves. Some fields are protected by object locks (`inode_security_struct.lock`, superblock mutex/spinlock) or RCU/LSM object lifetime rules.

### Dependencies and integration points
It depends on many kernel object definitions, `flask.h`, `avc.h`, and the externally defined `selinux_blob_sizes` from `hooks.c`. Every major SELinux subsystem relies on these structures for object labeling.

### Risks
Accessor offsets must match `selinux_blob_sizes`. Missing blob size updates for new structures can corrupt memory. Label initialization states (`INVALID`, `PENDING`, `INITIALIZED`) must be respected to avoid using stale or uninitialized SIDs.

### Test signals
Full LSM blob build tests, KASAN/lockdep runs, inode labeling tests, socket clone/free tests, BPF/perf/key object tests, and policy reload/revalidation tests are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/objsec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/policycap.h -->
## sources/distributed-fs/ceph-client/security/selinux/include/policycap.h

### Purpose
`policycap.h` enumerates SELinux policy capabilities: feature flags set by policy that opt into newer kernel SELinux semantics or capabilities.

### Important APIs, types, and functions
The enum includes capabilities for network peer controls, open permission, extended socket classes, always-check-network, cgroup seclabels, NNP/nosuid transitions, genfs symlink labels, ioctl cloexec skip, userspace initial context, netlink extended permissions, netif/genfs wildcards, functionfs seclabels, memfd class, and BPF token permissions. It defines `__POLICYDB_CAP_MAX`, `POLICYDB_CAP_MAX`, and declares `selinux_policycap_names[]`.

### Control flow
Policy load code maps names to enum bits. Runtime code reads `selinux_state.policycap[index]` through helper functions in `security.h` and branches on enabled semantics throughout `hooks.c`.

### State and persistence
This header stores no live state. Policy capability state lives in loaded policy and `selinux_state.policycap[]`.

### Dependencies and integration points
It is included by `policycap_names.h`, `security.h`, `ima.c`, selinuxfs, and security-server policy parsing.

### Risks
Adding a capability requires updating this enum, names, policy parsing/validation, IMA measurement length, and any runtime helper. Ordering must stay aligned with names and policy encoding.

### Test signals
Load policies with each capability, verify selinuxfs policycap entries, IMA state strings, and behavior toggles in hooks such as openperm, extsockclass, memfd, netlink xperm, and BPF token permissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/policycap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/policycap_names.h -->
## sources/distributed-fs/ceph-client/security/selinux/include/policycap_names.h

### Purpose
`policycap_names.h` defines the string names corresponding to the policy capability enum in `policycap.h`.

### Important APIs, types, and functions
The key artifact is `const char *const selinux_policycap_names[__POLICYDB_CAP_MAX]`, with names such as `network_peer_controls`, `open_perms`, `extended_socket_class`, `always_check_network`, `cgroup_seclabel`, `nnp_nosuid_transition`, `genfs_seclabel_symlinks`, `ioctl_skip_cloexec`, `userspace_initial_context`, `netlink_xperm`, `netif_wildcard`, `genfs_seclabel_wildcard`, `functionfs_seclabel`, `memfd_class`, and `bpf_token_perms`.

### Control flow
Consumers index this array by `POLICYDB_CAP_*` enum value. Security-server policy loading uses the strings to identify supported policycap names, selinuxfs exposes them, and IMA state measurement serializes them.

### State and persistence
The array is static compiled data. It represents the stable text interface between policy, selinuxfs, IMA measurement output, and runtime capability bits.

### Dependencies and integration points
It includes `policycap.h` and is included by sources that need the names rather than only enum values.

### Risks
Name ordering must exactly match `policycap.h`. Renaming a string breaks policy compatibility and changes IMA state text. Adding enum values without adding names will break userspace visibility and measurement completeness.

### Test signals
Build checks, policy load with named capabilities, selinuxfs policycap listing, and IMA `selinux-state` measurement contents should all show matching ordered names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/policycap_names.h -->
