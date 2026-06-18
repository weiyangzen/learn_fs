<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/security.h -->
# sources/distributed-fs/ceph-client/security/selinux/include/security.h

## Purpose
Defines the central SELinux security-server interface used by the LSM hooks, selinuxfs, network labeling code, and policy database services. It declares policy-version bounds, mount-labeling flags, global SELinux state, access-vector decision structures, extended-permission structures, SID/context conversion APIs, filesystem/network/IB lookup APIs, policy load/read APIs, status-page ABI, and cache initialization entry points.

## Important APIs, Types, and Functions
Key types are `struct selinux_state`, `struct selinux_load_state`, `struct av_decision`, `struct extended_perms_data`, `struct extended_perms_decision`, `struct extended_perms`, and `struct selinux_kernel_status`. Important inline APIs expose initialization state, enforcing mode, fixed `checkreqprot`, and policy capabilities such as `selinux_policycap_netpeer()`, `selinux_policycap_netlink_xperm()`, and `selinux_policycap_memfd_class()`. Declared services include `security_compute_av()`, `security_compute_xperms_decision()`, context/SID conversion, transition/member/change SID computation, NetLabel conversion, network SID lookup, genfs lookup, boolean/policy metadata lookup, netlink message lookup, and allocator-cache initialization.

## Control Flow
Callers load a policy through `security_load_policy()`, publish it via `selinux_policy_commit()`, or cancel with `selinux_policy_cancel()`. Permission paths compute `av_decision` and optional extended permissions from subject SID, target SID, class, driver, and base permission. Labeling paths convert between strings and SIDs, compute transition/member/change SIDs, and validate transitions. Network and filesystem hooks call specialized lookup helpers to map ports, nodes, interfaces, genfs paths, and NetLabel security attributes to SIDs.

## State and Persistence
`selinux_state` persists enforcing state when development mode is enabled, initialization state, policy capability bits, the mmap status page, and the RCU-protected active policy under `policy_mutex`. The status-page ABI persists sequence, enforcing, policyload, and deny-unknown values for userspace. Policycap and mount flags influence behavior until the next policy reload or remount.

## Dependencies and Integration Points
Depends on generated SELinux `flask.h` classes/permissions, policy capability definitions, RCU, mutexes, workqueues, VFS dentries/superblocks, NetLabel declarations, and selinuxfs/netlink consumers. It is included by most SELinux implementation files, so ABI-like changes ripple broadly.

## Risks
Policy version constants gate binary policy compatibility and must match readers/writers. `selinux_state.initialized` uses acquire/release ordering; weakening that risks policy visibility races. Extended-permission bit math assumes 256-bit driver windows. Stub NetLabel functions must return errors that callers treat as nonlabel support, not success.

## Test Signals
Validate policy load/read across supported policy versions, enforcing toggles, policycap reporting, SID/context conversion including invalid contexts, extended permissions for ioctls/netlink, NetLabel enabled/disabled builds, status-page mmap updates, and network/filesystem SID lookups after policy reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/security.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/xfrm.h -->
# sources/distributed-fs/ceph-client/security/selinux/include/xfrm.h

## Purpose
Declares SELinux support for XFRM/IPsec policy and state LSM hooks. The header lets the core SELinux network hooks allocate, clone, delete, free, match, and decode XFRM security contexts while compiling to no-op stubs when `CONFIG_SECURITY_NETWORK_XFRM` is disabled.

## Important APIs, Types, and Functions
Always-declared APIs include `selinux_xfrm_policy_alloc()`, `selinux_xfrm_policy_clone()`, `selinux_xfrm_policy_free()`, `selinux_xfrm_policy_delete()`, `selinux_xfrm_state_alloc()`, `selinux_xfrm_state_alloc_acquire()`, `selinux_xfrm_state_free()`, `selinux_xfrm_state_delete()`, `selinux_xfrm_policy_lookup()`, and `selinux_xfrm_state_pol_flow_match()`. With XFRM security enabled, the network packet surface adds `selinux_xfrm_sock_rcv_skb()`, `selinux_xfrm_postroute_last()`, `selinux_xfrm_decode_session()`, and `selinux_xfrm_skb_sid()`. `selinux_xfrm_enabled()` tests the external `selinux_xfrm_refcount`.

## Control Flow
Policy/state management functions are used when XFRM objects are created or destroyed from netlink or acquire paths. Packet hooks decode the session SID from matching XFRM state and check receive/postroute access against socket SIDs. On SELinux policy load, `selinux_xfrm_notify_policyload()` bumps route generation IDs in every network namespace so cached routes observe updated policy.

## State and Persistence
Persistent state is mostly external: XFRM policy/state security contexts and `selinux_xfrm_refcount`. The disabled-build stubs return success or `SECSID_NULL`, preserving normal networking without SELinux XFRM enforcement.

## Dependencies and Integration Points
Depends on `linux/lsm_audit.h`, `net/flow.h`, `net/xfrm.h`, `net_rwsem`, network namespace iteration, and route generation invalidation. It integrates with XFRM netlink, routing cache invalidation, socket receive/postroute hooks, and SELinux policy reload notifications.

## Risks
The enabled/disabled split must preserve identical call signatures. Route generation bumping under `net_rwsem` is broad and must stay synchronized with policy loads. Returning `SECSID_NULL` in disabled stubs is security-sensitive because callers must distinguish "no XFRM SID" from a meaningful label.

## Test Signals
Exercise IPsec policy/state creation with security contexts, policy clone/delete/free paths, receive and postroute checks with matching and mismatching SIDs, policy reload route invalidation, and builds with `CONFIG_SECURITY_NETWORK_XFRM` both enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/include/xfrm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/initcalls.c -->
# sources/distributed-fs/ceph-client/security/selinux/initcalls.c

## Purpose
Provides the device-initcall style SELinux initialization aggregator used by the LSM definition. It centralizes selinuxfs, network label caches, netlink notifications, optional InfiniBand, and optional netfilter setup.

## Important APIs, Types, and Functions
The single exported initialization routine is `selinux_initcall()`. It invokes `init_sel_fs()`, `sel_netport_init()`, `sel_netnode_init()`, `sel_netif_init()`, `sel_netlink_init()`, optional `sel_ib_pkey_init()`, and optional `selinux_nf_ip_init()`.

## Control Flow
Initialization is sequential. Each sub-init return is captured in `rc_tmp`; the first nonzero error is preserved in `rc`, but later init routines still run. Compile-time feature guards include InfiniBand and netfilter only when configured.

## State and Persistence
The file itself owns no state. It causes persistent state to be created in subordinate modules: selinuxfs registration and kernel mount, network SID caches, netdevice notifier registration, netlink socket creation, and feature-specific hook state.

## Dependencies and Integration Points
Depends on `initcalls.h` declarations and Linux initcall ordering. This is the bridge between SELinux LSM registration and the separate subsystems that cannot be initialized solely from policy load.

## Risks
Because initialization continues after failures, later modules may start even if earlier interfaces like selinuxfs failed. There is no rollback for partially initialized subsystems in this file. Panic behavior is delegated to sub-inits such as netlink creation.

## Test Signals
Boot with SELinux enabled and disabled, verify `/sys/fs/selinux` and selinuxfs mount availability, netlink event socket creation, network cache initialization, and configs with InfiniBand or netfilter toggled. Fault-injection tests should confirm the first error is returned while later init attempts still run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/initcalls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/netif.c -->
# sources/distributed-fs/ceph-client/security/selinux/netif.c

## Purpose
Maintains a fast SELinux SID cache for network interfaces because `net_device` does not carry SELinux security state directly. It maps `(network namespace, ifindex)` to interface SID and invalidates entries when devices go down.

## Important APIs, Types, and Functions
The public API is `sel_netif_sid()` and `sel_netif_flush()`, with init through `sel_netif_init()`. Core helpers are `sel_netif_hashfn()`, `sel_netif_find()`, `sel_netif_insert()`, `sel_netif_destroy()`, `sel_netif_sid_slow()`, `sel_netif_kill()`, and `sel_netif_netdev_notifier_handler()`. `struct sel_netif` wraps `struct netif_security_struct` with list and RCU fields.

## Control Flow
Fast lookup runs under `rcu_read_lock()` and returns a cached SID when present. Misses call `sel_netif_sid_slow()`, which gets the device by ifindex, locks the table, rechecks the cache, calls `security_netif_sid(dev->name, sid)`, and inserts a new cache record if memory and global table limits allow. A `NETDEV_DOWN` notifier removes the corresponding entry.

## State and Persistence
State is a 64-bucket RCU hash table, global `sel_netif_total`, and `sel_netif_lock`. The cache persists across packets until device-down invalidation, explicit flush, policy reload flush from other code, or the hard `SEL_NETIF_HASH_MAX` limit preventing more inserts.

## Dependencies and Integration Points
Depends on netdevice lookup/lifetime, network namespaces, SELinux policy lookup via `security_netif_sid()`, object security structures, and the netdevice notifier chain. Packet path hooks use this cache when checking interface labels.

## Risks
`sel_netif_flush()` iterates while deleting entries; list-safe iteration would be less fragile if multiple entries exist in a bucket. The hash combines namespace pointer and ifindex, but comments indicate container labeling is not fully supported. Cache insert failures are intentionally nonfatal, so repeated misses can hurt performance.

## Test Signals
Test lookup hit/miss behavior, policy-defined interface labels, invalid ifindex errors, cache flush after policy reload, `NETDEV_DOWN` invalidation, table-full behavior, and concurrent lookups/removals under RCU with lockdep/KCSAN enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/netif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/netlabel.c -->
# sources/distributed-fs/ceph-client/security/selinux/netlabel.c

## Purpose
Provides SELinux glue for NetLabel/CIPSO-style packet and socket labeling. It maps NetLabel security attributes to SIDs, maps SIDs back to NetLabel attributes, labels sockets and packets, enforces receive permissions, preserves labels across connection setup, and protects established socket labels from userspace option replacement.

## Important APIs, Types, and Functions
Core helpers include `selinux_netlbl_sidlookup_cached()`, `selinux_netlbl_sock_genattr()`, and `selinux_netlbl_sock_getattr()`. Public functions include `selinux_netlbl_cache_invalidate()`, `selinux_netlbl_err()`, `selinux_netlbl_sk_security_free()`, `selinux_netlbl_sk_security_reset()`, `selinux_netlbl_skbuff_getsid()`, `selinux_netlbl_skbuff_setsid()`, SCTP/TCP connection setup helpers, `selinux_netlbl_socket_post_create()`, `selinux_netlbl_sock_rcv_skb()`, `selinux_netlbl_socket_setsockopt()`, and connect helpers.

## Control Flow
Inbound skb SID lookup first checks whether NetLabel is enabled, obtains skb attributes, then calls `security_netlbl_secattr_to_sid()` and caches cacheable mappings. Outbound labeling uses a socket-cached secattr when possible, otherwise converts the requested SID and calls NetLabel skb/socket/connection setters. Socket creation labels INET/INET6 sockets immediately if destination-independent labeling is possible, otherwise marks the socket `NLBL_REQSKB` for per-packet/per-connection labeling. Receive checks map packet attributes to a SID and enforce `RECVFROM` on the receiving socket class.

## State and Persistence
Persistent per-socket state lives in `sk_security_struct`: `nlbl_secattr` and `nlbl_state` (`NLBL_UNSET`, `NLBL_LABELED`, `NLBL_REQSKB`, `NLBL_CONNLABELED`). NetLabel subsystem caches persist mapping results until invalidated. Request sockets and SCTP associations carry labels into accepted/cloned sockets.

## Dependencies and Integration Points
Depends on NetLabel APIs, IPv4/IPv6 headers, sockets, request sockets, SCTP associations, SELinux socket security, AVC permission checks, and NetLabel category import/export from the MLS bitmap layer. It integrates with socket create, connect, receive, setsockopt, SCTP association, and packet send paths.

## Risks
Socket locking is critical: reset/connect helpers assume callers hold locks in some paths and acquire them in others. `setsockopt()` must block removal of real on-the-wire labels without blocking unrelated options. AF_UNSPEC disconnect deliberately deletes connection labels and moves back to request-per-skb mode. Error signaling to NetLabel on denied labeled packets must avoid sending misleading errors for unlabeled traffic.

## Test Signals
Exercise labeled and unlabeled inbound packets, NetLabel disabled builds/runtime, socket post-create with destination-required labels, TCP accept and SCTP association/peeloff label preservation, connect/disconnect relabeling, setsockopt attempts to replace IP options/HBH options, cache invalidation, and AVC denials producing protocol-appropriate NetLabel errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/netlabel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/netlink.c -->
# sources/distributed-fs/ceph-client/security/selinux/netlink.c

## Purpose
Creates the SELinux netlink notification channel and broadcasts SELinux status events to userspace listeners. It handles setenforce and policyload messages for the `NETLINK_SELINUX` family.

## Important APIs, Types, and Functions
Public functions are `selnl_notify_setenforce()`, `selnl_notify_policyload()`, and init `sel_netlink_init()`. Internal helpers are `selnl_msglen()`, `selnl_add_payload()`, and `selnl_notify()`. The static `selnl` socket persists after initialization.

## Control Flow
Event-specific wrappers pass message type and data to `selnl_notify()`. The helper determines payload size, allocates an skb with `nlmsg_new()`, creates the netlink header, fills either `selnl_msg_setenforce` or `selnl_msg_policyload`, sets destination group `SELNLGRP_AVC`, and broadcasts. Unknown message types trigger `BUG()`.

## State and Persistence
The file owns one `struct sock *selnl` marked `__ro_after_init`. Notifications do not store history; delivery depends on active netlink listeners. Payload state is transient per skb.

## Dependencies and Integration Points
Depends on `linux/selinux_netlink.h`, generic netlink socket creation, init namespace, and SELinux status updates from enforcing changes and policy loads. `selinuxfs.c` calls the public notifiers after successful changes.

## Risks
`sel_netlink_init()` panics if the netlink socket cannot be created, making boot failure possible for core allocation/configuration failures. Message-size and payload switches must stay synchronized with the uapi message set. Allocation failures only log and drop notifications.

## Test Signals
Listen on `NETLINK_SELINUX` while toggling enforcing and loading policy, verify payload fields and multicast group, test OOM/drop paths with fault injection, and confirm nonroot receive is allowed by `NL_CFG_F_NONROOT_RECV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/netnode.c -->
# sources/distributed-fs/ceph-client/security/selinux/netnode.c

## Purpose
Caches SELinux node SIDs for IPv4 and IPv6 addresses to avoid repeated policy lookups on packet paths. The cache maps address family plus address to a SID with bounded per-bucket growth.

## Important APIs, Types, and Functions
Public APIs are `sel_netnode_sid()`, `sel_netnode_flush()`, and `sel_netnode_init()`. Helpers include `sel_netnode_hashfn_ipv4()`, `sel_netnode_hashfn_ipv6()`, `sel_netnode_find()`, `sel_netnode_insert()`, and `sel_netnode_sid_slow()`. `struct sel_netnode_bkt` tracks bucket size, and `struct sel_netnode` wraps `netnode_security_struct`.

## Control Flow
Fast path looks up the address under RCU. On miss, `sel_netnode_sid_slow()` locks the hash, rechecks, allocates a node, calls `security_node_sid()` with correct address length, and inserts the result. Insert adds new entries at the head and evicts the RCU-protected tail when the bucket reaches `SEL_NETNODE_HASH_BKT_LIMIT`.

## State and Persistence
Persistent state is a 256-bucket global hash table, bucket sizes, and nodes freed by RCU. Entries survive until eviction or explicit flush, typically after policy changes. There is no namespace key; address labels are policy-global.

## Dependencies and Integration Points
Depends on IPv4/IPv6 address structures, SELinux `security_node_sid()`, object security structures, spinlocks, RCU, and packet hooks needing node labels.

## Risks
Hashing only low address bits is fast but can concentrate some address patterns. Bucket eviction is approximate LRU by insertion order and may churn under scans. Unsupported address families call `BUG()`, so callers must validate family. Memory allocation failure avoids caching but still returns the policy result if lookup succeeds.

## Test Signals
Test IPv4 and IPv6 labels, repeated hit/miss behavior, bucket-limit eviction, flush after policy reload, unsupported-family guard behavior in debug tests, and concurrent readers during flush/eviction under RCU diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/netnode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/netport.c -->
# sources/distributed-fs/ceph-client/security/selinux/netport.c

## Purpose
Caches SELinux SIDs for network ports by protocol and port number. This reduces policy lookup overhead for socket and packet checks involving labeled ports.

## Important APIs, Types, and Functions
Public functions are `sel_netport_sid()`, `sel_netport_flush()`, and `sel_netport_init()`. Helpers include `sel_netport_hashfn()`, `sel_netport_find()`, `sel_netport_insert()`, and `sel_netport_sid_slow()`. `struct sel_netport` stores `netport_security_struct`, list linkage, and RCU callback state.

## Control Flow
The fast path performs an RCU hash lookup by port bucket and protocol. Misses lock the table, recheck, call `security_port_sid(protocol, pnum, sid)`, allocate a cache node, and insert it. Buckets are capped at 16 entries; inserting at a full bucket removes the tail.

## State and Persistence
The cache is a 256-bucket global hash table protected by `sel_netport_lock` for writes and RCU for reads. Entries persist until explicit flush, bucket eviction, or policy reload paths that call the flush function.

## Dependencies and Integration Points
Depends on SELinux policy portcon lookup, object security structures, RCU, spinlocks, and network/socket hooks. It shares the cache design used by `netnode.c`.

## Risks
Heavy use of many ports sharing low bits can cause eviction churn. Protocol is part of equality but not the hash, so TCP/UDP/SCTP collisions for the same low port bits share buckets. Allocation failure makes lookup correct but uncached. Unsupported protocol validation is deferred to `security_port_sid()`.

## Test Signals
Verify TCP/UDP/SCTP policy mappings, cache hits after first lookup, eviction at bucket limit, flush on policy reload, failed policy lookup warnings, and concurrent lookup/flush safety.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/netport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/nlmsgtab.c -->
# sources/distributed-fs/ceph-client/security/selinux/nlmsgtab.c

## Purpose
Maps userspace-generated netlink message types to SELinux permissions for route, tcpdiag/sockdiag, XFRM, and audit netlink socket classes. It provides the policy-facing decision used by SELinux netlink send checks.

## Important APIs, Types, and Functions
The public API is `selinux_nlmsg_lookup()`. `struct nlmsg_perm` stores message type and permission. Static tables cover route messages, tcpdiag/sockdiag messages, XFRM messages, and audit messages. Helper `nlmsg_perm()` linearly searches a table.

## Control Flow
`selinux_nlmsg_lookup()` switches on socket class. If policy capability `netlink_xperm` is enabled, it returns the generic `NLMSG` permission for extended-permission checking. Otherwise it table-lookups fixed message permissions. Audit user-message ranges map to relay permission without table entries. Unknown or unsupported classes return `-ENOENT`; unknown messages in handled classes return `-EINVAL`.

## State and Persistence
State is static read-only mapping tables. Runtime behavior changes when policy capability `POLICYDB_CAP_NETLINK_XPERM` is enabled, shifting checks from coarse fixed table permissions to extended permissions keyed by `nlmsg_type`.

## Dependencies and Integration Points
Depends on kernel netlink uapi constants, generated SELinux class/permission macros, and policycap accessors. Build-time `BUILD_BUG_ON()` checks force table updates when `RTM_MAX` or `XFRM_MSG_MAX` changes.

## Risks
Missing table updates after adding kernel netlink message types can deny legitimate operations or map them incorrectly. Extended permissions cannot be applied blindly to generic netlink because message type values are dynamic. Audit user-message range handling is special and must stay aligned with audit uapi ranges.

## Test Signals
Test each supported netlink class with read/write/relay messages, unknown message denial, policycap `netlink_xperm` enabled/disabled behavior, audit user message ranges, and compile failures when route/XFRM max constants move.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/nlmsgtab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/selinuxfs.c -->
# sources/distributed-fs/ceph-client/security/selinux/selinuxfs.c

## Purpose
Implements the `selinuxfs` pseudo filesystem, the main kernel/userspace control and query surface for SELinux. It exposes policy load/read, enforcing mode, context validation, access/create/relabel/member/validatetrans queries, booleans, status mmap, policy version, MLS status, AVC stats/tuning, initial SID contexts, class/permission indexes, policy capabilities, and the `null` character device.

## Important APIs, Types, and Functions
External entry is `init_sel_fs()` and global `selinux_null`. Filesystem construction uses `sel_fill_super()`, `sel_get_tree()`, `sel_init_fs_context()`, and `sel_kill_sb()`. Policy-load flow is `sel_write_load()` plus `sel_make_policy_nodes()`, `sel_make_bools()`, and `sel_make_classes()`. Query handlers include `sel_write_access()`, `sel_write_create()`, `sel_write_relabel()`, `sel_write_member()`, `sel_write_context()`, and `sel_write_validatetrans()`. State is tracked by `struct selinux_fs_info`; policy reads use `struct policy_load_memory`.

## Control Flow
Mount creation allocates fs-private state, fills root files, creates booleans/class/policycap directories, mounts a kernel instance, and looks up `selinuxfs/null`. Policy writes require `SECURITY__LOAD_POLICY`, copy policy bytes from userspace, call `security_load_policy()`, build replacement boolean/class trees under a hidden `.swapover` directory, atomically exchange dentries, then commit policy. Transaction files parse context strings from a simple transaction buffer and write results back into the same buffer. Boolean writes stage pending values; `commit_pending_bools` applies them through `security_set_bools()`.

## State and Persistence
Persistent filesystem state includes pending boolean names/values, boolean/class dentries, last allocated inode counters, and superblock private data. Global SELinux state is changed through enforcing writes, policy commits, status-page updates, AVC reset, netlink notifications, IMA measurement, and LSM policy-change notifications. Policy read mmap pins a vmalloc snapshot for each open file.

## Dependencies and Integration Points
Depends on VFS/simplefs helpers, fs_context, dentry exchange, SELinux security server, AVC, IMA measurement, audit, generated class/permission metadata, initial SID definitions, mmap/page fault helpers, and sysfs mount point creation. It is the user-visible integration point used by policy loaders, libselinux, setenforce, boolean tools, and policy inspection utilities.

## Risks
Policy-load dentry swapover must keep old and new boolean/class trees consistent on all failure paths. Many write handlers parse whitespace-delimited strings into `size + 1` buffers; overlong contexts are checked against `SIMPLE_TRANSACTION_LIMIT`. Enforcing changes are compiled out except in development builds. Runtime disable and checkreqprot writes are deprecated no-ops but still return success. Policy mmap must remain read-only despite `mprotect()`.

## Test Signals
Test mounting, kernel `null` lookup, policy load success/failure with boolean/class tree replacement, concurrent policy reads during reload, enforcing toggles and notifications, status mmap sequence updates, transaction query outputs, boolean staging/commit, class/perm file indexes, policycap files, AVC stats/tuning, deprecated disable/checkreqprot writes, and unmount cleanup with leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/selinuxfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/avtab.c -->
# sources/distributed-fs/ceph-client/security/selinux/ss/avtab.c

## Purpose
Implements SELinux access vector tables, the hashed policy structures that store type enforcement access vectors, type transition/member/change rules, and extended permission rules. It provides allocation, insertion, search, destruction, policy binary read/write, debug statistics, and slab cache setup.

## Important APIs, Types, and Functions
Public functions include `avtab_init()`, `avtab_alloc()`, `avtab_alloc_dup()`, `avtab_destroy()`, `avtab_insert_nonunique()`, `avtab_search_node()`, `avtab_search_node_next()`, `avtab_read_item()`, `avtab_read()`, `avtab_write_item()`, `avtab_write()`, and `avtab_cache_init()`. Internal helpers include `avtab_hash()`, `avtab_insert_node()`, `avtab_node_cmp()`, `avtab_insert()`, and `avtab_insertf()`.

## Control Flow
Allocation sizes the hash as a power-of-two bucket count based on rule count. Insert walks the sorted bucket chain and rejects duplicate non-extended-permission rules, while conditional-policy callers may use nonunique insertion. Search uses the same ordering to stop early. Policy read supports pre-`POLICYDB_VERSION_AVTAB` legacy encoding and modern 16-bit key encoding, validates type/class values and specifier exclusivity, then inserts decoded data. Write serializes each node with little-endian key and either data word or extended-permission payload.

## State and Persistence
State is `struct avtab` with bucket array, element count, slot count, and mask. Nodes and extended-permission payloads come from dedicated kmem caches. Persisted form is the binary SELinux policy stream read and written through `policy_file`.

## Dependencies and Integration Points
Depends on `policydb` validation, binary policy I/O helpers, `hash.h` `av_hash()`, bitops/hweight, policy version constants, and conditional policy code that stores enabled flags in `specified`.

## Risks
`avtab_node_cmp()` masks conditional enabled bits and treats overlapping specifier masks as equality, so changes can break duplicate detection and search iteration. Policy-version gates for xperms and conditional xperms are compatibility-sensitive. `avtab_write_item()` sizes its local buffer using the xperms union member even for non-xperms nodes, which is currently safe due to compile-time layout but subtle.

## Test Signals
Load policies with AV, type, and xperm rules; reject duplicate nonconditional rules; accept conditional nonunique rules; verify legacy policy decoding; fuzz truncated/overflow/invalid type/class/specifier encodings; dump/reload policies; and inspect hash stats in debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/avtab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/avtab.h -->
# sources/distributed-fs/ceph-client/security/selinux/ss/avtab.h

## Purpose
Defines the access vector table data model and public API for SELinux type enforcement rules. It describes how rules are keyed by source type, target type, target class, and a specified rule kind.

## Important APIs, Types, and Functions
Core types are `struct avtab_key`, `struct avtab_extended_perms`, `struct avtab_datum`, `struct avtab_node`, and `struct avtab`. Rule flags include `AVTAB_ALLOWED`, `AVTAB_AUDITALLOW`, `AVTAB_AUDITDENY`, transition/member/change type rules, xperm rule kinds, and conditional `AVTAB_ENABLED`. APIs cover init, allocation, duplication, destruction, read/write, nonunique insertion, node search, and next-node search.

## Control Flow
Consumers construct an `avtab_key` and search a table to accumulate decisions. Policy load allocates a table, reads items, and inserts nodes. Conditional policy code stores multiple matching nodes and toggles `AVTAB_ENABLED` without removing nodes. Policy write walks the table and serializes each node.

## State and Persistence
The header defines in-memory hash table state and the datum union for either 32-bit permissions/type values or heap-backed extended permissions. The same shapes are serialized by `avtab.c` into binary policies.

## Dependencies and Integration Points
Depends on `security.h` for extended permission bitmaps and policy constants. Integrated by policydb, services decision computation, and conditional policy handling.

## Risks
`specified` mixes rule kind bits and conditional enabled bits; callers must mask correctly. Extended permissions allow multiple entries for a key, unlike regular AV/type rules. Changing `SEL_VEC_MAX` or xperm layout affects decision computation and binary compatibility.

## Test Signals
Compile policydb/services users, load policies with each rule kind, verify conditional enabled toggling, test xperm driver windows, and confirm serialization round trips match the expected rule counts and values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/avtab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/conditional.c -->
# sources/distributed-fs/ceph-client/security/selinux/ss/conditional.c

## Purpose
Implements SELinux conditional policy support: boolean symbol loading/indexing, reverse-polish conditional expression evaluation, conditional AV rule loading/writing, enabled-state updates, conditional decision contribution, and duplication of conditional state during policy operations.

## Important APIs, Types, and Functions
Public APIs include `cond_policydb_init()`, `cond_policydb_destroy()`, `cond_init_bool_indexes()`, `cond_destroy_bool()`, `cond_index_bool()`, `cond_read_bool()`, `cond_read_list()`, `cond_write_bool()`, `cond_write_list()`, `evaluate_cond_nodes()`, `cond_compute_av()`, `cond_compute_xperms()`, `cond_policydb_dup()`, and `cond_policydb_destroy_dup()`. Core internals are `cond_evaluate_expr()`, `evaluate_cond_node()`, `cond_insertf()`, `cond_read_av_list()`, and duplication helpers.

## Control Flow
Boolean records are read into the boolean symbol table and indexed by value. Conditional nodes read a current state, an RPN expression, and true/false AV lists. Each AV rule is inserted into `te_cond_avtab`; type rules are checked against unconditional and conditional conflicts. Evaluation recomputes each expression and toggles `AVTAB_ENABLED` on true/false list nodes. Decision computation searches matching conditional nodes and merges only enabled rules into `av_decision` or xperm decisions.

## State and Persistence
Policydb owns `bool_val_to_struct`, `cond_list`, `cond_list_len`, and `te_cond_avtab`. Conditional rule enabled state is stored in each AV node's key. Binary policy persistence writes boolean records and writes each conditional's AV rules directly, rebuilding the conditional AV table on load.

## Dependencies and Integration Points
Depends on `avtab`, `hashtab`, `symtab`, `policydb`, and services helpers for merging xperm data. It integrates with boolean writes from selinuxfs and security-server decision computation.

## Risks
Expression evaluation has fixed stack depth `COND_EXPR_MAXDEPTH`; malformed expressions become undefined and disable all rules for that node. Conflict checks for conditional type rules are subtle because one matching rule may be shared across true/false branches but additional conflicts are invalid. Duplication must preserve node pointer relationships into the duplicated conditional AV table.

## Test Signals
Load policies with simple and nested booleans, true/false branch rules, conditional xperms, conflicting type rules, invalid operators/boolean indexes, stack-depth overflow, boolean toggles through selinuxfs, policy write/read round trips, and policy duplication failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/conditional.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/conditional.h -->
# sources/distributed-fs/ceph-client/security/selinux/ss/conditional.h

## Purpose
Declares SELinux conditional policy structures and APIs. It models booleans, reverse-polish expressions, true/false rule lists, and conditional nodes embedded in a policy database.

## Important APIs, Types, and Functions
Types include `struct cond_expr_node`, `struct cond_expr`, `struct cond_av_list`, and `struct cond_node`. Expression operators are `COND_BOOL`, `COND_NOT`, `COND_OR`, `COND_AND`, `COND_XOR`, `COND_EQ`, and `COND_NEQ`; `COND_EXPR_MAXDEPTH` caps evaluation stack depth. APIs cover policydb init/destroy/duplication, boolean indexing and I/O, conditional list I/O, evaluation, and decision contribution.

## Control Flow
Policy load uses `cond_read_bool()` and `cond_read_list()` to populate structures. Boolean state changes call `evaluate_cond_nodes()` to update AV node enabled flags. Access decisions call `cond_compute_av()` and `cond_compute_xperms()` after base table lookups.

## State and Persistence
The header defines policy-owned state rather than global state. Conditional AV lists store pointers to nodes in `te_cond_avtab`, so persistence and duplication must rebuild pointer arrays along with the table.

## Dependencies and Integration Points
Depends on `avtab`, `symtab`, `policydb`, and the exported conditional uapi header. Used by policydb parsing/writing, service decision code, and selinuxfs boolean controls.

## Risks
The pointer relationship between `cond_av_list.nodes` and `te_cond_avtab` is invariant-critical. Operator values are serialized in binary policy, so changing them breaks compatibility. Stack depth is a load-time/runtime safety constraint.

## Test Signals
Compile all conditional users, load/write policies with every operator, toggle booleans, verify enabled state and decision changes, and test policy duplication/destruction with memory leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/conditional.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/constraint.h -->
# sources/distributed-fs/ceph-client/security/selinux/ss/constraint.h

## Purpose
Defines SELinux constraint expression structures used to impose restrictions beyond type enforcement and role transitions. Constraints can compare users, roles, types, and MLS levels/categories across source, target, and validatetrans contexts.

## Important APIs, Types, and Functions
Key types are `struct constraint_expr` and `struct constraint_node`. Expression kinds include logical NOT/AND/OR, attribute comparisons, and name-set comparisons. Attribute flags select user/role/type, source versus target, validatetrans extra target, and MLS low/high level pairings. Operators include equality, inequality, dominance, dominated-by, and incomparability. `CEXPR_MAXDEPTH` caps evaluation stack depth.

## Control Flow
This header does not implement evaluation; policydb/services code builds linked lists of `constraint_expr` under `constraint_node`, then decision code evaluates them when permissions are constrained. The linked-list layout supports serialized policy expressions and sequential evaluation.

## State and Persistence
Constraint state is policy-owned and persistent for the life of a loaded policy. Each expression may own an `ebitmap names` set and a `type_set *type_names`, with the next pointer forming the expression stream.

## Dependencies and Integration Points
Depends on `ebitmap` and policydb type-set definitions from including translation units. Integrated with access-decision checks and transition validation in the SELinux security server.

## Risks
Constraint expressions are security-critical because they can deny permissions otherwise allowed by TE/RBAC. MLS attribute flags are numerous and easy to misinterpret. Memory ownership for `names` and `type_names` must be paired with policydb destruction paths.

## Test Signals
Load policies with user/role/type constraints, MLS dominance constraints, validatetrans constraints using extra target context, malformed expression depth/operator cases, and permissions allowed by TE but denied by constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/constraint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/context.c -->
# sources/distributed-fs/ceph-client/security/selinux/ss/context.c

## Purpose
Implements hashing for SELinux security contexts. The hash supports SID table and context lookup paths that need a stable hash over either mapped structured contexts or unmapped invalid context strings.

## Important APIs, Types, and Functions
The single function is `context_compute_hash()`. It hashes invalid/unmapped contexts with `full_name_hash()` over `str` and `len`, and valid contexts with `jhash_3words(user, role, type)` followed by `mls_range_hash()`.

## Control Flow
If `c->len` is nonzero, the function treats the context as an invalid string representation and returns the string hash. Otherwise it hashes structured user, role, type, and MLS range fields. The code assumes contexts from different policies are not mixed for equality/hash comparisons.

## State and Persistence
No state is stored here. The returned hash feeds persistent policy/SID data structures elsewhere. It depends on the invariant that invalid contexts have only `len` and `str` set under a given policy.

## Dependencies and Integration Points
Depends on Linux jhash/name hash helpers, `context.h`, and `mls.h`. Used by SID table or context mapping code to bucket contexts consistently with `context_equal()`.

## Risks
Hash/equality invariants must match: invalid string contexts compare by string while valid contexts compare by fields. Mixing contexts from different policies could make the assumption unsafe. MLS hash changes alter table distribution.

## Test Signals
Hash equal valid contexts with identical MLS ranges, unequal user/role/type/range variants, invalid string contexts, valid versus invalid contexts with similar printed representation, and SID table lookup performance/collision behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/context.h -->
# sources/distributed-fs/ceph-client/security/selinux/ss/context.h

## Purpose
Defines the internal SELinux security context representation and inline helpers for copying, comparing, destroying, and manipulating MLS ranges. A context combines user, role, type, optional invalid string representation, and MLS low/high levels.

## Important APIs, Types, and Functions
The central type is `struct context`. Helpers include `mls_context_init()`, `mls_context_cpy()`, `mls_context_cpy_low()`, `mls_context_cpy_high()`, `mls_context_glblub()`, `mls_context_equal()`, `mls_context_destroy()`, `context_init()`, `context_cpy()`, `context_destroy()`, `context_equal()`, and `context_compute_hash()`.

## Control Flow
Copy helpers duplicate MLS category bitmaps and roll back already-copied levels on failure. Low/high helpers collapse ranges to a single level. `mls_context_glblub()` computes the intersection of two ranges by choosing greatest low sensitivity, least high sensitivity, and category intersections. `context_equal()` compares invalid contexts by string when both have `len`, rejects one-valid/one-invalid pairs, and otherwise compares structured fields.

## State and Persistence
Context state is embedded in policydb, SID table, inode/socket/task security structures, and transition computations. The optional `str` stores contexts that cannot be mapped under the current policy. MLS category bitmaps require explicit destruction.

## Dependencies and Integration Points
Depends on `ebitmap`, `mls_types`, and `security.h`. Used by services, SID table, MLS operations, policy conversion, and label computation paths.

## Risks
Memory ownership is subtle: failed MLS copy must free partial category bitmaps and duplicated strings. `context_cpy()` uses `GFP_ATOMIC`, constraining allocation contexts. The invalid-string convention must remain consistent with hashing and equality.

## Test Signals
Test valid and invalid context equality, copy/destroy with fault injection, low/high/glblub range computations, category bitmap rollback on allocation failure, and SID table operations across policy reload/conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/ebitmap.c -->
# sources/distributed-fs/ceph-client/security/selinux/ss/ebitmap.c

## Purpose
Implements extensible bitmaps used for SELinux type, role, category, and class sets. The representation is a sorted linked list of fixed-size bitmap nodes, allowing sparse arbitrary-size bitsets and binary policy serialization.

## Important APIs, Types, and Functions
Public APIs include `ebitmap_equal()`, `ebitmap_cpy()`, `ebitmap_and()`, `ebitmap_contains()`, `ebitmap_get_bit()`, `ebitmap_set_bit()`, `ebitmap_destroy()`, `ebitmap_read()`, `ebitmap_write()`, `ebitmap_hash()`, `ebitmap_cache_init()`, and optional NetLabel import/export functions. The implementation uses `ebitmap_node_cachep`.

## Control Flow
Set/get operations walk sorted nodes by `startbit`; setting a bit allocates a node aligned to `EBITMAP_SIZE`, and clearing the last bit in a node removes it. Copy duplicates every node. `ebitmap_and()` iterates positive bits in the first bitmap and sets bits present in the second. Policy read validates map unit size, highbit/count consistency, aligned starts, nonempty maps, ordering, and final highbit. Write compacts positive bits into 64-bit serialized maps.

## State and Persistence
State is per-`struct ebitmap` linked nodes plus `highbit`. Nodes are slab allocated. Persisted state is policy-file bitmap records. NetLabel export/import converts between SELinux ebitmap nodes and NetLabel category maps.

## Dependencies and Integration Points
Depends on bit operations, jhash, policy I/O helpers, NetLabel category maps, and callers in MLS, constraints, roles/types, and policydb symbol data.

## Risks
Serialized bitmap validation is critical; accepting out-of-order or empty maps could corrupt policy state. `highbit` is rounded to node boundaries internally but written as last set bit rounded to 64-bit units. NetLabel import copies category maps into both MLS levels elsewhere, so ownership and destruction must be correct on failure.

## Test Signals
Test sparse and dense bitmaps, set/clear node creation and removal, copy/and/contains/equality, policy read rejection for bad mapunit/alignment/empty map/truncation, write/read round trips, NetLabel category import/export, and hash consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/ebitmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/ebitmap.h -->
# sources/distributed-fs/ceph-client/security/selinux/ss/ebitmap.h

## Purpose
Declares the SELinux extensible bitmap representation and iteration helpers. Ebitmaps provide sparse sets for policy symbols and MLS categories without a fixed maximum bit count in the in-memory API.

## Important APIs, Types, and Functions
Types are `struct ebitmap_node` and `struct ebitmap`. Constants derive node size from word size, including `EBITMAP_NODE_SIZE`, `EBITMAP_UNIT_NUMS`, `EBITMAP_UNIT_SIZE`, and `EBITMAP_SIZE`. Inline helpers cover initialization, first/next positive bit iteration, node bit get/set/clear, and `ebitmap_for_each_positive_bit()`. Function declarations cover copy, intersection, containment, bit access, serialization, hashing, destruction, and optional NetLabel conversion.

## Control Flow
Callers initialize an empty bitmap, mutate bits, iterate positive bits using the macro, serialize/deserialize through policy files, and explicitly destroy nodes. Iteration skips empty maps and stops at `highbit`.

## State and Persistence
Each bitmap stores a linked list of nodes and a `highbit` boundary. Node `startbit` anchors the fixed-size map array. Persistence is implemented in `ebitmap.c` but shaped by this header's layout.

## Dependencies and Integration Points
Depends on NetLabel declarations for optional category conversion and Linux bit helpers through implementation users. Used by MLS ranges, constraint name sets, role/type sets, and policy hashing.

## Risks
Macro arithmetic such as `EBITMAP_SHIFT_UNIT_SIZE()` and node index/offset calculations must remain portable across 32-bit and 64-bit builds. Callers must not use node bit helpers on bits outside the node range. Missing `ebitmap_destroy()` leaks slab nodes.

## Test Signals
Build/test on 32-bit and 64-bit configurations, iterate empty and sparse bitmaps, test boundary bits at node edges, validate NetLabel disabled stubs, and run policy load/unload leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/ebitmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/hashtab.c -->
# sources/distributed-fs/ceph-client/security/selinux/ss/hashtab.c

## Purpose
Implements a generic sorted-bucket hash table used by SELinux policy structures such as symbol tables. It provides allocation, insertion node allocation, destruction, mapping, duplication, optional debug statistics, and slab cache initialization.

## Important APIs, Types, and Functions
Public functions are `hashtab_init()`, `__hashtab_insert()`, `hashtab_destroy()`, `hashtab_map()`, `hashtab_duplicate()`, optional `hashtab_stat()`, and `hashtab_cache_init()`. Internal helper `hashtab_compute_size()` rounds element hints to a power-of-two table size.

## Control Flow
Initialization zeroes the table and allocates the bucket array when the hint is nonzero. Inline insertion/search in the header use caller-provided hash/compare functions to maintain sorted chains; `__hashtab_insert()` allocates and links a node at the requested position. Duplication allocates a same-sized table and invokes a caller copy callback for every node, preserving bucket order and cleaning partial copies through a destroy callback on failure.

## State and Persistence
State is `struct hashtab` with bucket array, size, and element count. Nodes are slab allocated from `hashtab_node_cachep`. The table is not serialized directly here, but policydb symbol readers/writers persist data stored in hashtabs.

## Dependencies and Integration Points
Depends on SELinux allocation helpers from `security.h`, slab caches, and caller-supplied key functions declared in `hashtab.h`. Used by policydb and conditional duplication paths.

## Risks
`hashtab_destroy()` frees only nodes and bucket arrays; callers must free keys/data separately where required. Duplication failure cleanup relies on the caller destroy callback matching the copy callback's ownership. Zero-sized tables are valid but reject insert/search as appropriate.

## Test Signals
Test insert/search ordering through header APIs, duplicate with deep and shallow copy callbacks, duplicate failure cleanup, destroy after partial construction, debug statistics, and policy load/unload leak tests for symbol tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/hashtab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/hashtab.h -->
# sources/distributed-fs/ceph-client/security/selinux/ss/hashtab.h

## Purpose
Declares a small generic hash table abstraction for SELinux policy data. It stores opaque key/datum pointers and relies on caller-provided hash and comparison functions.

## Important APIs, Types, and Functions
Types are `struct hashtab_key_params`, `struct hashtab_node`, `struct hashtab`, and `struct hashtab_info`. Inline APIs are `hashtab_insert()` and `hashtab_search()`. External APIs cover init, low-level insertion, destroy, map, duplicate, and optional stats. `HASHTAB_MAX_NODES` caps element count at `U32_MAX`.

## Control Flow
Insertion reschedules if needed, hashes the key, walks the sorted chain using the caller comparison, rejects exact duplicates, and inserts before the first greater key. Search uses the same ordering and stops early if comparison becomes negative.

## State and Persistence
The header defines in-memory table shape only. Keys and data remain caller-owned unless a specific destroy/map callback frees them. The table's sorted chains make deterministic traversal possible within hash buckets.

## Dependencies and Integration Points
Depends on Linux errno/types/scheduler APIs. Used by policy symbol tables, conditional boolean duplication, and other security-server structures that need generic keyed storage.

## Risks
Correctness depends entirely on hash and comparison functions being stable and mutually consistent. Callers must not insert into uninitialized or zero-sized tables. Ownership is not encoded in the type system, making leaks or double-frees possible in map/destroy users.

## Test Signals
Use multiple key types, duplicate insertion, sorted early-stop search, max-node/zero-size errors, callback abort from `hashtab_map()`, and copy/destroy ownership tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/hashtab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/mls.c -->
# sources/distributed-fs/ceph-client/security/selinux/ss/mls.c

## Purpose
Implements SELinux Multi-Level Security operations: context string formatting/parsing, MLS level/range validation, default range setup, policy conversion of levels/categories, MLS range computation during transitions, and optional NetLabel MLS import/export.

## Important APIs, Types, and Functions
Public APIs include `mls_compute_context_len()`, `mls_sid_to_context()`, `mls_level_isvalid()`, `mls_range_isvalid()`, `mls_context_isvalid()`, `mls_context_to_sid()`, `mls_from_string()`, `mls_range_set()`, `mls_setup_user_range()`, `mls_convert_context()`, `mls_compute_sid()`, and NetLabel helpers. It relies on `mls_context_cpy*()` helpers from `context.h` and bitmap operations from `ebitmap`.

## Control Flow
Formatting computes or emits `:sensitivity[:cats][-high[:cats]]`, compacting consecutive categories with ranges. Parsing splits the context string in place into low/high range parts, resolves sensitivities and categories through policy symbol tables, expands category ranges, and defaults high to low when no high range is specified. Validation checks sensitivity existence, category authorization for the level, range dominance, and user authorization. Transition computation honors explicit range transition rules, class default ranges, process/object defaults, or source effective low range depending on AVTAB operation and object class.

## State and Persistence
MLS state is embedded in `struct context` as two `mls_level`s with ebitmap categories. Policydb stores level/category/user range definitions and range transition rules. NetLabel helpers persist only through packet/socket security attributes managed elsewhere.

## Dependencies and Integration Points
Depends on policydb symbols, SID table default-context lookup, services range transition search, NetLabel, ebitmap category conversion, and context helpers. Used by SID/context conversion, policy reload conversion, user context setup, transition labeling, and NetLabel mapping.

## Risks
Parsing mutates the input string and requires callers to pass writable buffers. Category ranges are one-based in policy values but zero-based in bitmaps. `mls_import_netlbl_cat()` shallow-copies the low category bitmap struct to high after import; ownership assumptions are delicate because both levels then describe the same node list. Default range behavior must match class policy semantics or transitions get wrong labels.

## Test Signals
Test non-MLS policies, MLS context formatting/parsing with single categories and ranges, invalid sensitivities/categories/reversed ranges, user range authorization, default SID fallback, range transition rules, every class default range mode, policy conversion with renamed/missing levels/categories, and NetLabel level/category import/export.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/mls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/mls.h -->
# sources/distributed-fs/ceph-client/security/selinux/ss/mls.h

## Purpose
Declares the MLS operation surface for SELinux security-server code. It connects contexts, policydb, SID table, transition computation, and NetLabel category/level conversion.

## Important APIs, Types, and Functions
Declarations cover context length/rendering, context/range/level validation, string-to-context parsing, range assignment, policy conversion, transition SID MLS computation, user range setup, and optional NetLabel import/export. Inline `mls_range_hash()` hashes low/high sensitivities and category ebitmaps.

## Control Flow
Consumers call validation during context lookup/load, rendering during SID-to-context conversion, parsing during context-to-SID conversion, compute during transition/member/change SID calculation, and conversion during policy reload. NetLabel callers use the optional helpers when translating packet labels.

## State and Persistence
The header owns no state, but all functions operate on policy-owned MLS definitions and context-owned ranges. The hash function contributes to persistent SID/context table lookup behavior.

## Dependencies and Integration Points
Depends on jhash, context, ebitmap, policydb, and optional NetLabel declarations. Integrated by services, SID table, NetLabel glue, and policy conversion.

## Risks
Callers must honor allocation and locking requirements, especially policy read locks for default SID lookup during parsing. Hash changes can affect table distribution. Disabled NetLabel stubs return `-ENOMEM` for category conversion, so callers must treat them as unavailable.

## Test Signals
Compile with and without NetLabel, validate MLS enabled/disabled paths, hash equal ranges consistently, and cover callers in context conversion, transition computation, and policy reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/mls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/mls_types.h -->
# sources/distributed-fs/ceph-client/security/selinux/ss/mls_types.h

## Purpose
Defines the basic MLS data structures and dominance predicates used throughout SELinux. It represents a level as sensitivity plus category set, and a range as low/high levels.

## Important APIs, Types, and Functions
Types are `struct mls_level` and `struct mls_range`. Inline predicates are `mls_level_eq()`, `mls_level_dom()`, `mls_level_incomp()`, `mls_level_between()`, and `mls_range_contains()`.

## Control Flow
MLS validation and transition code compare levels by sensitivity ordering plus category containment. Range containment checks that the candidate low dominates the allowed low and the allowed high dominates the candidate high. Between checks combine two dominance tests.

## State and Persistence
The structures are embedded in contexts, user definitions, levels, and range transition data. Category ebitmaps require explicit lifecycle management by the surrounding context or policy object.

## Dependencies and Integration Points
Depends on `security.h` and `ebitmap.h`. Used by `context.h`, `mls.c`, constraint evaluation, user range setup, and label transition logic.

## Risks
Sensitivity values are policy indexes, while categories are zero-based ebitmap positions in many call paths. Dominance semantics are security-critical and must stay consistent with MLS policy language expectations. Macros evaluate arguments more than once only through nested calls, so callers should avoid side-effect expressions.

## Test Signals
Test equality, dominance, incomparability, between, and range containment for empty and populated categories, boundary sensitivities, and category sets that differ only by one bit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/mls_types.h -->
