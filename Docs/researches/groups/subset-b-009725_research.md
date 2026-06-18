# Research: subset-b-009725

Grouped research for NFS-Ganesha support files under `sources/user-network-fs/nfs-ganesha/src/support`. Each section preserves the source path in its title and is bounded for reconciliation into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/murmur3.c -->
# sources/user-network-fs/nfs-ganesha/src/support/murmur3.c

## Purpose
This file embeds Austin Appleby's public-domain MurmurHash3 implementations used by NFS-Ganesha support code where fast non-cryptographic hashing is needed. It provides the x86 32-bit, x86 128-bit, and x64 128-bit variants and is intentionally platform-light except for endian/alignment assumptions hidden behind `getblock`.

## Important APIs, Types, And Functions
The exported functions are `MurmurHash3_x86_32`, `MurmurHash3_x86_128`, and `MurmurHash3_x64_128`, declared through `murmur3.h`. Internal helpers `rotl32`, `rotl64`, `fmix32`, and `fmix64` implement bit rotations and final avalanche mixing. Macros `ROTL32`, `ROTL64`, `BIG_CONSTANT`, and `getblock` keep the reference algorithm readable. Inputs are raw byte buffers, an `int len`, a `uint32_t seed`, and an output buffer supplied by the caller.

## Control Flow
Each hash routine splits input into fixed-size blocks, mixes full blocks with variant-specific constants, folds remaining tail bytes through fall-through `switch` cases, xors in the total length, applies final avalanche mixing, and writes the result to `out`. The x86 128-bit variant uses four 32-bit lanes, while the x64 variant uses two 64-bit lanes and walks blocks forward.

## State And Persistence
The implementation is stateless and has no persistence. All state is stack-local hash lanes and constants. The only observable side effect is writing the hash value into the caller-provided output buffer.

## Dependencies And Integration Points
It depends on `config.h` and `murmur3.h` for build configuration and prototypes. Callers must provide suitably sized output storage: 4 bytes for x86_32 and 16 bytes for the 128-bit variants. Hash consumers elsewhere in the tree rely on stable algorithm outputs, so changing constants, endian handling, or tail logic would break persisted hash keys if any external store uses the values.

## Risks And Test Signals
Risks are typical for the reference MurmurHash3 C implementation: unaligned reads through `uint32_t *` and `uint64_t *`, little-endian assumptions in `getblock`, signed `int len`, direct casts for output stores, and deliberate fall-through switches that can be broken by warning-driven edits. Test signals should include known MurmurHash3 vectors for empty strings, short tails of every length modulo 16, long multi-block inputs, different seeds, and builds on strict-alignment or big-endian targets if those are supported.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/murmur3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/netgroup_cache.c -->
# sources/user-network-fs/nfs-ganesha/src/support/netgroup_cache.c

## Purpose
This file implements a process-local cache for `innetgr(group, host, NULL, NULL)` lookups. It caches both positive and negative netgroup membership answers to reduce NSS/SSSD lookup cost in export/client matching paths.

## Important APIs, Types, And Functions
`struct ng_cache_info` stores an AVL node, group and host buffer descriptors, and the insertion epoch. Public entry points are `ng_cache_init`, `ng_cache_cleanup`, `ng_innetgr`, and `ng_clear_cache`. Internal helpers include `ng_hash_key`, `buffdesc_comparator`, `ng_comparator`, `ng_expired`, `ng_free`, `ng_remove`, `ng_add`, and `ng_lookup`. A global `pthread_rwlock_t ng_lock` protects the AVL trees.

## Control Flow
Initialization creates separate positive and negative AVL trees and clears a small positive direct-mapped hash array. `ng_innetgr` first takes the read lock, checks the positive tree/cache, then the negative tree. On a double miss, it takes the write lock, calls `innetgr`, stores the result into the positive or negative cache, and returns the result. Expired entries are detected during lookup; lookup temporarily drops the read lock, reacquires the write lock, confirms the node still exists, removes and frees it, then resumes with a read lock and reports a miss.

## State And Persistence
State is in memory only: `pos_ng_tree`, `neg_ng_tree`, `ng_cache[1009]`, and the lock. Entries expire after a hard-coded 30 minutes. There is no disk persistence; cache contents are wiped by `ng_clear_cache` or process shutdown cleanup.

## Dependencies And Integration Points
The code uses Ganesha AVL, buffer, memory, atomic pointer, logging, cleanup, and config support plus libc `innetgr`. It integrates with export access control and idmapping/client matching code that asks whether a client host belongs to a configured netgroup.

## Risks And Test Signals
Risks include stale authorization for up to 30 minutes, no configurable TTL in this file, direct-mapped positive cache collisions replacing `ng_cache` slots, possible duplicate lookups while the read lock is dropped for expiry removal, and reliance on serialized `innetgr` calls because SSSD behavior is noted as unsafe under parallel calls. Tests should exercise positive and negative hits, expiry, duplicate inserts, `ng_clear_cache`, concurrent readers with expiry, hash collision fallback to AVL lookup, and SSSD/NSS failure behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/netgroup_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/nfs4_acls.c -->
# sources/user-network-fs/nfs-ganesha/src/support/nfs4_acls.c

## Purpose
This file manages shared NFSv4 ACL objects. It allocates ACE arrays and ACL containers, interns identical ACL payloads in a hash table, and reference-counts cached ACLs so FSAL objects can share equivalent ACLs without duplicating memory.

## Important APIs, Types, And Functions
Global state includes `pool_t *fsal_acl_pool` and static `hash_table_t *fsal_acl_hash`. Public functions are `nfs4_ace_alloc`, `nfs4_acl_alloc`, `nfs4_ace_free`, `nfs4_acl_free`, `nfs4_acl_entry_inc_ref`, `nfs4_acl_new_entry`, `nfs4_acl_release_entry`, and `nfs4_acls_init`. Internal hashing uses `CityHash64` through `fsal_acl_hash_both`; `compare_fsal_acl` compares raw ACE bytes.

## Control Flow
`nfs4_acls_init` creates the ACL pool and hash table. New ACL data enters through `nfs4_acl_new_entry`, which builds a key over `acldata->aces`, latches the hash table, and either returns an existing ACL after freeing the duplicate ACE array and incrementing the refcount, or creates a new `fsal_acl_t`, owns the ACE array, initializes refcount 1, and inserts it. `nfs4_acl_release_entry` decrements under the ACL lock. If it is the last reference, it latches the hash table, checks the entry again to handle races, deletes the table entry, and frees the ACL and ACE array.

## State And Persistence
All state is process-local. ACL identity is derived from raw ACE array bytes, not from a serialized external key. Persistence is limited to long-lived in-memory pool and hash entries until references are released or the server exits.

## Dependencies And Integration Points
The file depends on Ganesha memory pools, hash table latches, `fsal_types.h`, logging, `city.h`, and `nfs4_acls.h`. It sits between protocol/FSAL ACL conversion code and object metadata, giving FSAL handles a shared `fsal_acl_t` representation.

## Risks And Test Signals
Risks include raw-structure hashing sensitivity to padding or uninitialized ACE fields, refcount races if callers use ACLs after release, missing cleanup for the global hash/pool on shutdown, and asserting `old_value.addr == acl` during final deletion. Test signals should cover interning identical ACLs, distinct ACL byte sequences, release while another thread increments, duplicate insert latch paths, allocation failure paths, and static analysis for padding-sensitive comparisons.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/nfs4_acls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/nfs4_fs_locations.c -->
# sources/user-network-fs/nfs-ganesha/src/support/nfs4_fs_locations.c

## Purpose
This file implements allocation, reference counting, and release for `fsal_fs_locations_t`, the NFSv4 fs_locations data structure used to describe alternate filesystem roots and server locations.

## Important APIs, Types, And Functions
Public functions are `nfs4_fs_locations_new`, `nfs4_fs_locations_free`, `nfs4_fs_locations_get_ref`, and `nfs4_fs_locations_release`. Internal `nfs4_fs_locations_alloc` allocates the structure and optional server array, while `nfs4_fs_locations_put_ref` decrements a reference with the caller holding the write lock.

## Control Flow
`nfs4_fs_locations_new` allocates a zeroed structure, duplicates `fs_root` and `rootpath`, initializes refcount 1, and returns it. Callers increment with `nfs4_fs_locations_get_ref`. Release takes the write lock; if the refcount is greater than one it decrements and returns, otherwise it drops the lock and frees all owned strings, server string values, the server array, the lock, and the object.

## State And Persistence
Each object owns duplicated root strings, an optional `utf8string` server array, a lock, and a reference count. There is no global cache or durable persistence. Lifetime is entirely caller-managed through the reference API.

## Dependencies And Integration Points
The code uses `nfs4_fs_locations.h`, `fsal_types.h`, Ganesha allocation helpers, pthread rwlocks, and NFSv4 logging. It integrates with FSAL and protocol paths that return `fs_locations`/referral style attributes.

## Risks And Test Signals
Risks include no allocation-failure cleanup after `fs_root` or `rootpath` duplication fails, no null check after `server` allocation when `count` is nonzero, and potential races if callers access fields without holding their own reference. Tests should cover zero and nonzero server counts, multiple get/release sequences, release of NULL, allocation failure injection, and server string cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/nfs4_fs_locations.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/nfs_convert.c -->
# sources/user-network-fs/nfs-ganesha/src/support/nfs_convert.c

## Purpose
This file centralizes stringification and status conversion utilities for NFS protocol code. It maps NFS operation numbers, NFS status enums, FSAL status values, file types, request results, auth errors, and 64-bit host/network byte order conversions into protocol-facing representations.

## Important APIs, Types, And Functions
Key exports include `nfsproc3_to_str` when NFSv3 is enabled, `nfsop4_to_str`, `nfsstat3_to_str`, `nfsstat4_to_str`, `nfstype3_to_str`, `nfs_req_result_to_str`, `nfs_htonl64`, `nfs_ntohl64`, `auth_stat2str`, `nfs4_Errno_verbose`, and `nfs3_Errno_verbose` when NFSv3 is enabled. Static `op_names_v3` and `op_names_v4` tables rely on enum-indexed initializers and name prefixes.

## Control Flow
Operation string conversion indexes a static table and strips fixed prefixes (`NFSPROC3_` and `OP_`) after range checks. Status and type conversions are large switch statements returning string literals. FSAL-to-NFS conversion switches on `status.major`, maps each FSAL error to a protocol status, and logs critical diagnostics for non-retryable IO-like cases that are collapsed to protocol IO errors.

## State And Persistence
The file has no mutable state and no persistence. All outputs are string literals, converted integers, or status enum values.

## Dependencies And Integration Points
It includes protocol headers `nfs23.h`, `nfs4.h`, `mount.h`, and `nfs_convert.h`. It is used broadly by request handling, logging, filehandle management, FSAL error handling, duplicate request reporting, and RPC authentication diagnostics.

## Risks And Test Signals
Risks include enum drift when new NFSv4 operations or errors are added without updating tables/switches, unknown values collapsing to `ILLEGAL` or generic strings, and `LITTLEEND` compile-time dependence for 64-bit byte swapping. Since many functions return non-const `char *` despite literals, callers must not mutate the result. Tests should include every known enum value, out-of-range operation numbers, representative FSAL error mappings for v3 and v4, and endian conversion round trips.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/nfs_convert.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/nfs_creds.c -->
# sources/user-network-fs/nfs-ganesha/src/support/nfs_creds.c

## Purpose
This file builds request credentials in `op_ctx`, applies export security policy, performs root/all squash handling, resolves managed groups, compares RPC credentials, and provides a version-independent ACCESS helper.

## Important APIs, Types, And Functions
Global masks `root_op_export_options` and `root_op_export_set` describe root context export permission fields. Public functions include `squash_setattr`, `nfs_compare_clientcred`, `nfs_rpc_req2client_cred`, `nfs_req_creds`, `init_credentials`, `clean_credentials`, `nfs4_export_check_access`, and `nfs_access_op`. Internal helpers `set_extended_groups`, `rpcsec_gss_fetch_managed_groups`, and `squash_creds` coordinate group lookup and credential rewriting.

## Control Flow
`nfs4_export_check_access` refreshes export permissions, validates access mask, NFSv4 protocol enablement, transport, privileged port policy, and security flavor, then calls `nfs_req_creds`. `nfs_req_creds` parses AUTH_NONE, AUTH_SYS, or RPCSEC_GSS credentials, maps GSS principals to uid/gid when enabled, fetches managed groups, calls `set_extended_groups`, then applies anonymous/root squashing in `squash_creds`. `nfs_access_op` translates ACCESS3/ACCESS4 bits into FSAL mode and ACE masks, calls `obj_ops->test_access`, and maps allowed bits back to protocol response masks while honoring read-only exports.

## State And Persistence
Most state is per-request in `op_ctx`: original credentials, active credentials, group data references, copied group arrays, export permission flags, and squash flags. `clean_credentials` releases temporary group references/copies and resets credential state. There is no durable persistence.

## Dependencies And Integration Points
The file integrates with TI-RPC request structures, optional GSSAPI, idmapper/principal mapping, `uid2grp`, export manager/client manager, FSAL export/object operations, LTTng tracepoints, monitoring counters, and NFSv4 protocol access checks.

## Risks And Test Signals
Risks include explicit reliance on TI-RPC private structures, complex flag interactions among `CREDS_LOADED`, `CREDS_ANON`, `MANAGED_GIDS`, and squash flags, fallback behavior controlled by `enable_rpc_cred_fallback`, truncation of long GSS principals to `MAXNAMLEN`, and subtle group-array ownership rules. Tests should cover AUTH_NONE, AUTH_SYS, RPCSEC_GSS success/failure, managed group fallback on/off, all squash/root squash/root-id squash, root group squashing in supplemental groups, read-only export ACCESS filtering, transport/protocol rejection, and `clean_credentials` leak checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/nfs_creds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/nfs_filehandle_mgmt.c -->
# sources/user-network-fs/nfs-ganesha/src/support/nfs_filehandle_mgmt.c

## Purpose
This file converts between FSAL object handles and NFSv3/NFSv4 wire filehandles, validates Ganesha filehandle structure, resolves NFSv3 handles back to FSAL objects, and performs NFSv4 compound current/saved filehandle sanity checks.

## Important APIs, Types, And Functions
Important functions include `nfs3_FhandleToCache` under NFSv3, `nfs4_FSALToFhandle`, `nfs3_FSALToFhandle`, `nfs4_Is_Fh_DSHandle`, `nfs4_Is_Fh_Invalid`, `nfs3_Is_Fh_Invalid`, `nfs4_sanity_check_FH`, and `nfs4_sanity_check_saved_FH`. The implementation manipulates `file_handle_v3_t`, `file_handle_v4_t`, `nfs_fh3`, `nfs_fh4`, `gsh_buffdesc`, `fsal_export`, and `fsal_obj_handle`.

## Control Flow
Outbound conversion allocates or clears the protocol filehandle buffer, points a descriptor at the embedded `fsopaque` area, asks the FSAL object to encode itself with `handle_to_wire`, fills Ganesha version, endian flags, FSAL opaque length, and export id, then sets the final protocol length. Inbound v3 conversion validates the handle, asserts the export id matches the current export, calls export `wire_to_host`, then `create_handle`. Sanity checks validate empty/invalid handles, required object type, and whether pNFS data-server handles are allowed for the operation.

## State And Persistence
The file has no global mutable state. It serializes export id, version, endian flags, and FSAL opaque bytes into wire handles that may persist on clients and return in later requests. That makes handle layout and version compatibility externally visible.

## Dependencies And Integration Points
It depends on NFS protocol headers, FSAL conversion operations, export manager state in `op_ctx`, filehandle layout helpers/macros, logging, and `nfs_convert` for status conversion. It is central to LOOKUP/GETFH/PUTFH style protocol flows.

## Risks And Test Signals
Risks include fixed maximum assumptions for host handles, assert-only export-id checking in v3 inbound conversion, endian flag compatibility, VMware short-handle warning behavior, and precise status mapping for wrong object types. Tests should round-trip FSAL handles through v3/v4 encoders and decoders, validate malformed length/version/fs_len cases, exercise DS-handle rejection, required-type errors for directory/symlink/non-directory operations, and FSAL `handle_to_wire`/`wire_to_host` failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/nfs_filehandle_mgmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/nfs_ip_name.c -->
# sources/user-network-fs/nfs-ganesha/src/support/nfs_ip_name.c

## Purpose
This file implements the IP-address-to-hostname cache used by dispatch/export code for logging, client identity display, and auth statistics. It resolves socket addresses with `getnameinfo`, caches hostnames keyed by `sockaddr_t`, and expires entries after a configurable interval.

## Important APIs, Types, And Functions
Global state is `hash_table_t *ht_ip_name` and `unsigned int expiration_time`. Public functions are `ip_name_value_hash_func`, `ip_name_rbt_hash_func`, `compare_ip_name`, `display_ip_name_key`, `display_ip_name_val`, `nfs_ip_name_add`, `nfs_ip_name_get`, `nfs_ip_name_remove`, and `nfs_Init_ip_name`. The configuration block `nfs_ip_name` exposes `NFS_IP_Name` parameters `Index_Size` and `Expiration_Time`.

## Control Flow
`nfs_ip_name_add` performs DNS lookup into the caller's buffer, falls back to numeric IP text on failure, logs slow lookups, allocates a copied sockaddr key and variable-length hostname value, and inserts into the hash table while tolerating duplicate-key races. `nfs_ip_name_get` looks up the address, evicts expired values, copies the hostname to the caller, and reports miss or success. `nfs_ip_name_remove` deletes a cached entry and frees its value. `nfs_Init_ip_name` initializes the hash table from parsed config.

## State And Persistence
Cache entries are process-local heap allocations with timestamps. They are not persisted. Key memory is allocated on insert, but only value memory is explicitly freed on delete in this file; key cleanup likely depends on hash-table ownership semantics.

## Dependencies And Integration Points
The code depends on Ganesha hash tables, socket hashing/comparison/display helpers, allocation helpers, config parsing, logging, and `gsh_getnameinfo`. It integrates with core config through the exported `config_block` and with dispatch paths needing reverse DNS or address display.

## Risks And Test Signals
Risks include slow or blocking DNS during cache miss, fallback requiring caller buffers at least `SOCK_NAME_MAX`, stale names until expiry, prime-size validation only at config commit, and duplicate insert races that intentionally discard the losing allocation. Tests should cover DNS success/failure, numeric fallback, too-small caller buffers, expiry eviction, duplicate insert, remove miss/hit, IPv4 and IPv6 keys, and non-prime config rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/nfs_ip_name.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/nfs_qosmgr.c -->
# sources/user-network-fs/nfs-ganesha/src/support/nfs_qosmgr.c

## Purpose
This file exposes runtime QoS management over DBus. It lets administrators inspect and update bandwidth, token, and IOPS limits for per-client, per-export, and per-export-per-client QoS modes.

## Important APIs, Types, And Functions
The only non-static exported function is `dbus_qosmgr_init`. Internally, DBus handlers include client setters/getters for bandwidth, tokens, and IOPS; export setters/getters for bandwidth, tokens, and IOPS; per-export-per-client list/set functions; and enable/disable functions for bandwidth and IOPS control. Static `gsh_dbus_method` arrays `qos_methods_pc`, `qos_methods_ps`, and `qos_methods_pepc` define the method surfaces, and `qos_interface` is registered under `org.ganesha.nfsd.qos`.

## Control Flow
Each DBus handler validates argument types, resolves a client or export, takes `g_qos_config_lock`, optionally takes a target `qos_class->lock`, reads or mutates bucket limits/enable flags, writes DBus reply fields, releases references and locks, and returns a boolean DBus status. `dbus_qosmgr_init` selects the method array based on `g_qos_config->qos_type` and registers path `QosMgr` if QoS is globally enabled.

## State And Persistence
The file mutates live `gsh_client`, `gsh_export`, `qos_block`, and `qos_class_t` structures in memory. Changes are runtime state, not persisted back to configuration files. Locks coordinate concurrent DBus calls and NFS request QoS use.

## Dependencies And Integration Points
It depends on DBus support, export/client lookup helpers, global QoS config from `nfs_qos.h`, Ganesha lock conventions, glist iteration, and `gsh_dbus_register_path`. It is the management-plane companion to request-path QoS enforcement.

## Risks And Test Signals
Risks include several apparent iterator/reply mistakes: some getters append output to `args` instead of the reply iterator, `dbus_qos_client_bw_get` duplicates `lookup_client`, some export getters use `iter` before `dbus_message_iter_init_append`, and some setters validate the same current argument twice without advancing. IP rendering in `client_qos_to_dbus` casts `qos_class->gsh_client` rather than the `cl_addrbuf` field after checking its family, which looks unsafe. Tests should use DBus introspection and method calls for every QoS mode, invalid argument type/order checks, missing export/client checks, concurrent set/get calls, and sanitizer coverage for list rendering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/nfs_qosmgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/nfs_read_conf.c -->
# sources/user-network-fs/nfs-ganesha/src/support/nfs_read_conf.c

## Purpose
This file defines the table-driven parser metadata for NFS-specific configuration blocks. It maps configuration tokens to fields in global NFS, QoS, Kerberos, directory services, and NFSv4 parameter structures, and supplies small commit helpers for cluster membership.

## Important APIs, Types, And Functions
Exported `config_block` objects include `nfs_core`, optional `qos_core`, optional `krb5_param`, `directory_services_param`, and `version4_param`. Static token lists define UDP listener modes, root Kerberos principal modes, pwnam backends, enabled protocols, RDMA protocol versions, QoS types, NFSv4 minor versions, and recovery backends. Helper functions are `haproxy_host_adder`, `cluster_members_adder`, `remove_self_cluster_members`, and `core_commit`.

## Control Flow
The parser uses `CONF_ITEM_*` macros to populate global config structures with bounds, defaults, token maps, and destination fields. Host-list parameters call custom adders that build client entries. During core commit, local interface addresses are enumerated and any matching `Cluster_Members` entries are moved into `cluster_self`, then cluster members are logged. Most other blocks use `noop_conf_commit`.

## State And Persistence
This file initializes and mutates process configuration state, not persistent files. The parsed values drive server listeners, protocols, DRC sizing, stats, idmapping, QoS defaults, NFSv4 grace/recovery behavior, and security settings for the lifetime of the daemon or until dynamic config reload paths update them.

## Dependencies And Integration Points
It depends on config parsing macros, NFS core structs, FSAL defaults, protocol feature macros, network interface enumeration, export client parsing, pwnam/idmapping headers, and QoS config. The config blocks are consumed by the global Ganesha parser and DBus config interfaces.

## Risks And Test Signals
Risks include very large macro tables where field/default mismatches are easy, feature-guarded options changing the accepted config surface, fatal failure on `getifaddrs` in cluster self-detection, duplicate `glist_del` in `remove_self_cluster_members`, and apparent duplicated text in the QoS IOPS config area. Tests should parse minimal and maximal configs, invalid bounds, all protocol token aliases, cluster member self-removal with IPv4/IPv6 interfaces, QoS-enabled builds, GSS and NFSIDMAP feature variants, and DBus config introspection names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/nfs_read_conf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/rados_grace.c -->
# sources/user-network-fs/nfs-ganesha/src/support/rados_grace.c

## Purpose
This file manages NFSv4 grace-period cluster coordination state stored in a Ceph RADOS object. It tracks global current/recovery epochs and per-node flags indicating whether a node needs grace and whether it is enforcing grace locally.

## Important APIs, Types, And Functions
Public functions include `rados_grace_create`, `rados_grace_dump`, `rados_grace_epochs`, `rados_grace_enforcing_toggle`, `rados_grace_enforcing_check`, `rados_grace_join_bulk`, `rados_grace_lift_bulk`, `rados_grace_add`, and `rados_grace_member_bulk`. Internal `rados_grace_notify` sends a RADOS notification after successful state changes. Per-node omap values use flag bits `RADOS_GRACE_NEED_GRACE` and `RADOS_GRACE_ENFORCING`.

## Control Flow
The object body stores two little-endian `uint64_t` values: current epoch and recovery epoch. OMAP keys are node ids with one-byte flags. Create writes initial epochs. Dump and epochs read and decode the object. Join/lift/toggle/add functions use read-modify-write loops: read epochs and omap keys, capture object version with `rados_get_last_version`, compute updated flags/epochs, assert the version in a write op, then retry on version races. Lifting grace clears `NEED_GRACE` or removes node keys and sets recovery epoch to zero when all needing nodes are handled.

## State And Persistence
State is durable in RADOS: epochs in the object data and node flags in omap. In-memory arrays are temporary per call. Notifications are best-effort management signals after writes.

## Dependencies And Integration Points
The file depends on `librados`, endian helpers, errno values, and standard allocation. It integrates with NFSv4 recovery backends that need clustered grace coordination and node membership checks.

## Risks And Test Signals
Risks include hard `MAX_ITEMS` pagination limits producing `-ENOTRECOVERABLE` when exceeded, manual allocation cleanup paths, version-race retry behavior, node membership requiring all provided ids to exist, synchronous notify latency, and source anomalies such as duplicated `if (more)` text and suspicious brace structure in read loops that warrant compile/test confirmation. Tests should use a real or mocked RADOS cluster to cover create idempotency, add/member, join start/no-start, lift with remove and non-remove, enforcing toggle/check, concurrent writers causing version retries, more-than-1024 omap entries, malformed object body length, and notification failure tolerance.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/rados_grace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/refstr.c -->
# sources/user-network-fs/nfs-ganesha/src/support/refstr.c

## Purpose
This file provides the allocation and final release functions for Ganesha reference-counted strings (`gsh_refstr`). It supports shared immutable-ish strings whose lifetime is controlled by URCU reference counters.

## Important APIs, Types, And Functions
`gsh_refstr_alloc(size_t len)` allocates `sizeof(struct gsh_refstr) + len` bytes and initializes `gr_ref` with `urcu_ref_init`. `gsh_refstr_release(struct urcu_ref *ref)` is the release callback: it recovers the containing `gsh_refstr`, logs the string value, and frees the allocation.

## Control Flow
Allocation returns an initialized container with room for caller-managed string bytes. Release is called when the URCU refcount reaches zero; it uses `container_of` on the embedded reference member and frees the whole object.

## State And Persistence
There is no global state and no persistence. Each allocation owns one heap object and an embedded reference counter. The caller is responsible for filling `gr_val` and ensuring the requested length includes any required terminator.

## Dependencies And Integration Points
The code depends on `gsh_refstr.h`, URCU refs, Ganesha allocation helpers, list/container macros, and export-component logging. It is used by subsystems that need shared strings without copying on every reference.

## Risks And Test Signals
Risks include no explicit allocation failure check before `urcu_ref_init`, caller mistakes around length and null termination, and logging `%s` on `gr_val` assuming it is a valid C string. Tests should cover allocation length including terminator, ref increment/decrement lifecycle, release callback invocation, allocation failure injection, and sanitizer checks for unterminated `gr_val` use.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/refstr.c -->
