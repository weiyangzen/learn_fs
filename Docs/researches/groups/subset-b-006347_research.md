# subset-b-006347 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/policydb.c -->
# sources/distributed-fs/ceph-client/security/selinux/ss/policydb.c

## Purpose
`policydb.c` implements the SELinux binary policy database reader, writer, validator, index builder, and destructor. It turns a policy image into the in-kernel `struct policydb` model used by `services.c`: symbol tables, access vectors, conditional rules, class defaults, role transitions, filename transitions, object contexts, genfs rules, MLS ranges, policy capabilities, permissive domains, neveraudit domains, and type-attribute maps.

## Important APIs, Types, and Functions
The public entry points are `policydb_read()`, `policydb_write()`, `policydb_destroy()`, `policydb_load_isids()`, `policydb_context_isvalid()`, `policydb_*_isvalid()`, `policydb_filenametr_search()`, `policydb_rangetr_search()`, `policydb_roletr_search()`, `string_to_security_class()`, `string_to_av_perm()`, and `str_read()`. Major helpers include `policydb_init()`, `policydb_index()`, symbol read/write callbacks, `ocontext_read()/ocontext_write()`, `genfs_read()/genfs_write()`, `filename_trans_read()/filename_trans_write()`, and boundary sanity checks.

## Control Flow
`policydb_read()` validates magic, string, policy version, config flags, and compatibility table sizes; initializes symbol tables; reads symbols through `read_f[]`; requires the `process` class and transition permissions; loads AV tables and conditionals; reads role transitions/allows, filename transitions, indexed symbol arrays, object contexts, genfs entries, range transitions, type-attribute maps, and boundary checks. Read-side helpers validate references as they parse, so most malformed policies fail before publication. `policydb_write()` reverses this order into a bounded `policy_file`, refusing very old policy versions that the writer cannot safely encode.

## State and Persistence
State is entirely in memory after load but mirrors the binary policy layout for `security_read_policy()`. `next_entry()` and `put_entry()` advance the policy buffer and enforce length/overflow checks. `policydb_destroy()` is comprehensive: it maps over symbol tables, conditional policy, AV tables, role/filename/range hash tables, object contexts, genfs lists, and ebitmaps.

## Dependencies and Integration Points
This file depends on SELinux core structures from `avtab`, `conditional`, `mls`, `context`, `ebitmap`, `sidtab`, and `services`. `services.c` consumes policy lookup functions for class/permission mapping, SID computation, filename transitions, role transitions, range transitions, policycaps, and object-context SID lookup.

## Risks
The critical risks are binary parser regressions, version compatibility mistakes, missing cleanup on partial load failure, invalid symbol indexes, duplicate transition keys, and off-by-one errors in policy value arrays. Filename transition compatibility paths are especially sensitive because old policies are expanded into the newer compressed shape. MLS/category reads must destroy partially initialized bitmaps on failure.

## Test Signals
Useful signals include SELinux policy load/unload tests across supported policy versions; malformed/truncated policy images; duplicate genfs, role, and filename transition entries; MLS and non-MLS policy round trips through `policydb_write()`; boundary violation policies; policies with unknown classes/permissions under allow/reject modes; and KASAN/KMEMLEAK checks around failed reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/policydb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/policydb.h -->
# sources/distributed-fs/ceph-client/security/selinux/ss/policydb.h

## Purpose
`policydb.h` defines the in-kernel shape of an SELinux policy database and the serialized policy buffer helpers. It is the contract between the parser/writer in `policydb.c`, the security server in `services.c`, MLS code, conditional policy code, and SID conversion code.

## Important APIs, Types, and Functions
Key datum types include `perm_datum`, `common_datum`, `class_datum`, `role_datum`, `type_datum`, `user_datum`, `level_datum`, `cat_datum`, `cond_bool_datum`, `type_set`, `ocontext`, and `genfs`. Lookup keys include `role_trans_key`, `filename_trans_key`, and `range_trans`. `struct policydb` owns symbol tables, value-to-name arrays, value-to-struct arrays, TE/conditional AV tables, role/filename/range transition hash tables, role allows, object contexts, genfs contexts, type-attribute maps, policycaps, permissive and neveraudit maps, policy version, unknown handling flags, and process transition permission masks. `struct policy_file` is a moving buffer cursor for binary policy data.

## Control Flow
The header establishes numeric indices for symbol classes (`SYM_*`) and object contexts (`OCON_*`) that drive loop-based parser/destructor code. Inline `next_entry()` and `put_entry()` are the central policy stream operations: they bound-copy from/to the buffer and advance the cursor.

## State and Persistence
The declarations encode both persistent policy concepts and transient indexes. Arrays such as `sym_val_to_name` and `class_val_to_struct` are derived from symbol tables after parsing. `policydb.len` records the binary policy length for later readback.

## Dependencies and Integration Points
It includes `symtab`, `avtab`, `sidtab`, `ebitmap`, `mls_types`, `context`, and `constraint`, making it a central SELinux SS header. External callers use the validity, lookup, read, write, and destroy prototypes rather than reaching into parser internals.

## Risks
Any layout change must be synchronized with parser version compatibility and all destroy paths. The symbol and object-context enum counts are baked into compatibility checks. `put_entry()` relies on multiplication overflow detection; callers must pass correct element sizes and counts.

## Test Signals
Compilation across SELinux MLS, NetLabel, Infiniband, and conditional policy configurations is a baseline. Policy load/readback tests should cover every `OCON_*` and `SYM_*` kind and confirm unknown-class flags and policycaps survive a round trip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/policydb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/services.c -->
# sources/distributed-fs/ceph-client/security/selinux/ss/services.c

## Purpose
`services.c` implements the SELinux security server: access-vector decisions, context/SID translation, SID computation for transitions and object creation, policy load/commit/cancel, boolean updates, network/object-context SID lookup, audit rule support, NetLabel conversion, and policy readback.

## Important APIs, Types, and Functions
Central exported functions include `security_compute_av()`, `security_compute_xperms_decision()`, `security_transition_sid()`, `security_member_sid()`, `security_change_sid()`, `security_validate_transition()`, `security_bounded_transition()`, `security_sid_to_context*()`, `security_context_to_sid*()`, `security_load_policy()`, `selinux_policy_commit()`, `selinux_policy_cancel()`, `security_port_sid()`, `security_netif_sid()`, `security_node_sid()`, `security_genfs_sid()`, `security_fs_use()`, `security_set_bools()`, `security_sid_mls_copy()`, audit-rule helpers, NetLabel helpers, and policy readback helpers. The file owns class/permission mapping via `struct selinux_map` and context conversion via `services_convert_context()`.

## Control Flow
Access decisions map kernel class IDs to policy class IDs, find source/target contexts in the active RCU-protected sidtab, evaluate TE and conditional AV table entries across source/target type-attribute bitmaps, merge extended permissions, apply constraints/MLS, role transition restrictions, type bounds, permissive and neveraudit flags, then map results back to kernel permission bits. SID computation selects user/role/type defaults, transition/change/member AV rules, filename transitions, role transitions, MLS values, validates the new context, and inserts or reuses a SID. Policy load reads a new `policydb`, builds the kernel mapping, loads initial SIDs, preserves booleans, converts the live SID table, and publishes via RCU only at commit.

## State and Persistence
The active policy is `selinux_state.policy` under RCU plus `policy_mutex` for updates. `latest_granting` is the policy sequence for AVC and audit invalidation. Boolean changes create a shallow policy copy plus duplicated conditional portions, reevaluate conditionals, then publish a new policy object.

## Dependencies and Integration Points
This file integrates with AVC (`avc_ss_reset`), netlink policyload notifications, status page updates, NetLabel cache invalidation, XFRM policyload notification, IMA state measurement, audit, LSM blobs, filesystem superblock security, policycap globals, and the SID table conversion machinery.

## Risks
The highest risks are RCU lifetime mistakes, `-ESTALE` retry omissions during sidtab conversion, mismatched kernel/policy class mapping, invalid-context handling under permissive versus enforcing mode, boolean update shallow-copy mistakes, and incorrect network fallback labels. Permission mapping must handle unknown policy entries consistently with `allow_unknown` and `reject_unknown`.

## Test Signals
Exercise policy reload under concurrent context-to-SID insertions, AVC checks before and after boolean flips, unknown class/permission modes, filename transitions with object names, validatetrans denials, bounded transition denials, NetLabel and XFRM peer SID resolution, genfs/fs_use lookup, audit-rule stale detection, and policy readback length consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/services.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/services.h -->
# sources/distributed-fs/ceph-client/security/selinux/ss/services.h

## Purpose
`services.h` declares the compact shared types used by the SELinux security server and SID conversion code. It avoids exposing most `services.c` internals while giving policy load, sidtab conversion, and extended permission code a common contract.

## Important APIs, Types, and Functions
`struct selinux_mapping` maps one kernel security class to a policy class value and policy permission bits. `struct selinux_map` stores the mapping array and size. `struct selinux_policy` bundles the active `sidtab`, `policydb`, class/permission map, and `latest_granting` sequence. `struct convert_context_args` carries old/new policydb pointers for context conversion. Prototypes cover extended permission driver discovery/decision computation and `services_convert_context()`.

## Control Flow
The mapping types are populated during `security_load_policy()` and consumed by access computation to translate kernel class/permission numbering into policy numbering and back. Conversion args are passed by `sidtab_convert()` into `services_convert_context()` for every existing SID context during policy reload.

## State and Persistence
`struct selinux_policy` is the RCU-published unit of SELinux policy state. Its `latest_granting` value persists as the sequence used to invalidate AVC/audit users after policy changes.

## Dependencies and Integration Points
The header depends on `policydb.h` and is consumed by `services.c`, `sidtab.c`, and other SELinux files that need active policy or conversion interfaces. It is part of the boundary between parsed policy state and runtime decision services.

## Risks
Changing these structures affects RCU-published policy lifetime and sidtab conversion. Mapping array bounds and permission bit widths must stay aligned with `secclass_map` and `u32` access vectors.

## Test Signals
Compile-time coverage should include extended permissions and policy reload. Runtime signals include AVC decisions after policy load, policy reload with existing SIDs, and ioctl/netlink extended permission checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/services.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/sidtab.c -->
# sources/distributed-fs/ceph-client/security/selinux/ss/sidtab.c

## Purpose
`sidtab.c` implements SELinux SID-to-context and context-to-SID storage. It supports fast lock-free SID lookup, reverse context lookup, initial SID storage, dynamic SID allocation, optional SID-to-string caching, and live SID table conversion during policy reload.

## Important APIs, Types, and Functions
Main APIs are `sidtab_init()`, `sidtab_set_initial()`, `sidtab_search_entry()`, `sidtab_search_entry_force()`, `sidtab_context_to_sid()`, `sidtab_convert()`, `sidtab_cancel_convert()`, `sidtab_freeze_begin()`, `sidtab_freeze_end()`, `sidtab_destroy()`, `sidtab_hash_stats()`, and optional `sidtab_sid2str_get()/put()`. Internal helpers implement the tree allocator/lookup (`sidtab_do_lookup()`), reverse hash lookup (`context_to_sid()`), conversion traversal, and cache eviction.

## Control Flow
Initial SIDs are copied into fixed `isids[]` entries and optionally entered into the reverse hash. Dynamic SIDs are indexed after `SECINITSID_NUM`; lookup reads `count` with acquire semantics before walking the tree. `sidtab_context_to_sid()` first tries an RCU reverse-hash lookup, then locks, retries, rejects inserts if frozen, allocates the next tree entry, copies the context, mirrors it into a conversion target if a policy load is active, publishes `count` with release semantics, and inserts into the reverse hash. `sidtab_convert()` freezes the conversion snapshot count, enables live conversion for newly inserted entries, converts existing tree entries outside the lock, then builds the target reverse hash.

## State and Persistence
The sidtab is in-memory runtime state, not directly serialized. It persists across policy reloads by converting contexts from the old policy to the new policy. Invalid/unmapped contexts can be retained as strings in `struct context`, and force lookups can return them.

## Dependencies and Integration Points
It depends on `context` helpers for equality, copy, destroy, and hashing; `services_convert_context()` for policy reload conversion; SELinux initial SID constants; RCU hash/list APIs; and spinlocks for writers. `services.c` performs all high-level SID/context operations through this table.

## Risks
Key risks are publish-order races around `count`, stale inserts during policy switch, conversion target consistency, hash duplicates, and cache lifetime under RCU. `sidtab_convert()` assumes no concurrent policy loads and needs correct rollback through `sidtab_cancel_convert()` on failure.

## Test Signals
Stress tests should perform concurrent `security_context_to_sid()` while reloading policy, validate `-ESTALE` retry paths, check duplicate initial SID contexts, verify fallback to unlabeled for missing SIDs, run SID-to-context cache LRU tests when enabled, and monitor hash stats under large label sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/sidtab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/sidtab.h -->
# sources/distributed-fs/ceph-client/security/selinux/ss/sidtab.h

## Purpose
`sidtab.h` defines the SID table data structures and public APIs for SELinux runtime SID management. It captures the allocation geometry, initial SID handling, reverse hash, conversion metadata, locking, and optional string cache contract used by `sidtab.c` and `services.c`.

## Important APIs, Types, and Functions
`struct sidtab_entry` stores SID, context hash, `struct context`, optional cached string, and reverse-hash node. `union sidtab_entry_inner`, `sidtab_node_leaf`, and `sidtab_node_inner` define page-sized tree nodes. `struct sidtab_isid_entry` stores fixed initial SIDs. `struct sidtab_convert_params` connects old-to-new conversion args with a target sidtab. `struct sidtab` owns roots, count, conversion pointer, frozen flag, lock, optional cache state, initial SID entries, and `context_to_sid` hash. Inline `sidtab_search()` and `sidtab_search_force()` expose context pointers from entries.

## Control Flow
The constants derive node capacities from page size and structure size, allowing a multi-level tree up to `U32_MAX` dynamic SIDs. Callers search by SID, insert by context, and coordinate policy reload through conversion/freeze helpers.

## State and Persistence
The header separates fixed initial SID state from dynamically allocated SIDs. `count` is explicitly documented as atomically read/written, while `convert` and `frozen` are lock-protected writer state.

## Dependencies and Integration Points
It includes Linux spinlock/log2/hashtable APIs and `context.h`. It is consumed by `policydb.h`, `services.h`, and all code that needs SID-to-context resolution.

## Risks
The allocation geometry is sensitive to structure-size changes. Any new fields in `sidtab_entry` can reduce leaf capacity and should be evaluated against `SIDTAB_MAX_LEVEL`. Callers must respect that returned context pointers are protected by the surrounding RCU/policy lifetime.

## Test Signals
Build tests with different page sizes and `CONFIG_SECURITY_SELINUX_SID2STR_CACHE_SIZE` values are useful. Runtime tests should validate initial SID setup, dynamic SID overflow behavior, conversion freeze semantics, and cache enable/disable compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/sidtab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/symtab.c -->
# sources/distributed-fs/ceph-client/security/selinux/ss/symtab.c

## Purpose
`symtab.c` implements the simple string-keyed symbol table used throughout SELinux policy parsing for classes, permissions, roles, types, users, booleans, sensitivities, and categories.

## Important APIs, Types, and Functions
The file exports `symtab_init()`, `symtab_insert()`, and `symtab_search()`. It defines private key operations `symhash()` and `symcmp()` and packages them into `symtab_key_params`. The hash function is djb2a over unsigned bytes; comparison is `strcmp()`.

## Control Flow
`symtab_init()` resets `nprim` and initializes the underlying `hashtab`. Insert/search forward the supplied string key and datum to `hashtab_insert()` and `hashtab_search()` with the symbol key parameters. Ownership of inserted keys/data is handled by policydb-specific destructors, not by this file.

## State and Persistence
The symtab holds in-memory policy symbols during and after policy load. `nprim` is a caller-maintained count of primary symbols and is later used by `policydb_index()` to allocate value-to-name/value-to-struct arrays.

## Dependencies and Integration Points
It depends on Linux string/kernel/errno headers and the local `hashtab` abstraction. `policydb.c` is the primary consumer and uses one `struct symtab` per SELinux symbol kind.

## Risks
Duplicate-key behavior is delegated to `hashtab_insert()`. Since keys are raw `char *`, callers must ensure stable allocated storage and matching destruction. Hash collision behavior affects policy load/search performance.

## Test Signals
Policy load tests with many symbols and collision-heavy names provide coverage. Unit-level signals would include insert/search success, duplicate rejection from the underlying hash table, and `nprim` preservation across initialization and policy parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/symtab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/symtab.h -->
# sources/distributed-fs/ceph-client/security/selinux/ss/symtab.h

## Purpose
`symtab.h` declares the SELinux symbol table wrapper around the generic `hashtab` implementation. It gives policy code a concise type for string-to-datum mappings plus a primary-symbol count.

## Important APIs, Types, and Functions
`struct symtab` contains `struct hashtab table` and `u32 nprim`. Public prototypes are `symtab_init()`, `symtab_insert()`, and `symtab_search()`.

## Control Flow
The header is intentionally minimal: policy readers allocate/populate datums, call `symtab_insert()`, then later call `symtab_search()` for references and mapping. `nprim` is filled by parser code according to policy metadata.

## State and Persistence
The symbol table persists inside `struct policydb` for the lifetime of the loaded policy. It is also used to construct derived indexes for fast value-to-name and value-to-struct access.

## Dependencies and Integration Points
It includes `hashtab.h` and is included by `policydb.h`. Every SELinux policy symbol kind is represented by this type.

## Risks
Because the API does not encode ownership, callers must pair inserted keys/data with the right destructors. Changes to `struct symtab` affect `policydb` layout and initialization/destruction loops.

## Test Signals
Compiler coverage plus policy load/search tests are enough for this small wrapper. Debug hash evaluation in `policydb.c` can expose pathological table sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/symtab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/status.c -->
# sources/distributed-fs/ceph-client/security/selinux/status.c

## Purpose
`status.c` implements the mmap-visible SELinux status page used by userspace to observe enforcing-mode and policy-load changes without a syscall on every access check.

## Important APIs, Types, and Functions
The exported functions are `selinux_kernel_status_page()`, `selinux_status_update_setenforce()`, and `selinux_status_update_policyload()`. They update a `struct selinux_kernel_status` located at the head of a lazily allocated page.

## Control Flow
`selinux_kernel_status_page()` takes `selinux_state.status_lock`, allocates and zeroes the page if needed, initializes version, sequence, enforcing, policyload, and deny_unknown, then returns the page reference. Update functions lock, check whether the page exists, increment `sequence` to an odd value, issue a write memory barrier, update fields, issue another barrier, and increment `sequence` again to an even value.

## State and Persistence
The status page is kernel memory owned by `selinux_state.status_page` and exposed through the SELinux status filesystem interface. It is not durable storage; it mirrors current kernel SELinux state. The sequence field implements seqlock-style observation for userspace readers.

## Dependencies and Integration Points
It depends on `selinux_state.status_lock`, `enforcing_enabled()`, and `security_get_allow_unknown()`. `services.c` calls `selinux_status_update_policyload()` after policy commit, and setenforce paths call `selinux_status_update_setenforce()`.

## Risks
Memory ordering is the main risk: userspace relies on odd/even sequence transitions and barriers. Updates are skipped if userspace has not yet requested the page. The initial `deny_unknown` value depends on active policy unknown-permission handling.

## Test Signals
Tests should mmap `/selinux/status`, verify initial fields, toggle enforcing mode, load policy, and ensure userspace sees even sequence changes with matching field updates. Race tests should poll while setenforce/policyload loops run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/status.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/xfrm.c -->
# sources/distributed-fs/ceph-client/security/selinux/xfrm.c

## Purpose
`xfrm.c` implements SELinux hooks for labeled IPsec/XFRM policies and states. It allocates, clones, frees, authorizes, and matches SELinux security contexts on XFRM policy/state objects and extracts peer SIDs from packet transform paths.

## Important APIs, Types, and Functions
Important functions include `selinux_xfrm_policy_alloc()`, `selinux_xfrm_policy_clone()`, `selinux_xfrm_policy_free()`, `selinux_xfrm_policy_delete()`, `selinux_xfrm_policy_lookup()`, `selinux_xfrm_state_alloc()`, `selinux_xfrm_state_alloc_acquire()`, `selinux_xfrm_state_free()`, `selinux_xfrm_state_delete()`, `selinux_xfrm_state_pol_flow_match()`, `selinux_xfrm_decode_session()`, `selinux_xfrm_skb_sid()`, `selinux_xfrm_sock_rcv_skb()`, and `selinux_xfrm_postroute_last()`. `selinux_xfrm_refcount` tracks labeled XFRM objects.

## Control Flow
User-provided XFRM contexts are validated for LSM/SELinux DOI and algorithm, copied into `xfrm_sec_ctx`, converted to a SID, and authorized with `ASSOCIATION__SETCONTEXT`. Policy lookup checks `ASSOCIATION__POLMATCH`; EACCES is mapped to ESRCH so the XFRM layer treats it as no policy match. State/policy/flow matching rejects label mismatches and requires `ASSOCIATION__SENDTO`. Packet SID extraction scans ingress `sec_path` or egress destination transforms. Receive/postroute hooks enforce `RECVFROM`/`SENDTO` against labeled or unlabeled association SIDs.

## State and Persistence
Security contexts are stored on XFRM policy/state objects and freed with those objects. The global refcount records active labeled XFRM usage. Packet-derived SIDs are transient.

## Dependencies and Integration Points
This file integrates SELinux AVC checks with the Linux XFRM/IPsec stack, skb security paths, destination transforms, socket receive/send paths, and `security_context_to_sid()`/`security_sid_to_context()`.

## Risks
Risks include accepting malformed user contexts, inconsistent ingress transform labels, incorrect unlabeled fallback enforcement, refcount imbalance, and lifetime bugs when cloning variable-length contexts. The `-EACCES` to `-ESRCH` conversion is behaviorally important for XFRM policy search.

## Test Signals
Exercise labeled and unlabeled IPsec policies, mismatched SA/policy/flow labels, deletion authorization, acquire-state allocation from secid, ingress stacks with multiple labels, postroute unlabeled checks, and refcount balance under clone/free/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/xfrm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/smack/Kconfig -->
# sources/distributed-fs/ceph-client/security/smack/Kconfig

## Purpose
`security/smack/Kconfig` defines build-time configuration for the Smack LSM and its optional policy/audit/network behaviors.

## Important APIs, Types, and Functions
The symbols are `SECURITY_SMACK`, `SECURITY_SMACK_BRINGUP`, `SECURITY_SMACK_NETFILTER`, and `SECURITY_SMACK_APPEND_SIGNALS`. `SECURITY_SMACK` depends on `NET`, `INET`, and `SECURITY`, selects `NETLABEL` and `SECURITY_NETWORK`, and defaults off.

## Control Flow
Kconfig selection controls which source files and conditional code are compiled. `BRINGUP` enables rule mode `b` reporting for granted accesses. `NETFILTER` enables packet marking with secmarks and pulls in netfilter/secmark dependencies. `APPEND_SIGNALS` changes signal-delivery authorization from write-style access to append-style access.

## State and Persistence
This file has no runtime state but controls compiled policy behavior. User-visible semantics can change significantly based on selected options, especially signal permissions and bringup-mode logging.

## Dependencies and Integration Points
The options feed `security/smack/Makefile`, `smack.h` feature macros, and conditional code in Smack access/network paths. They also require kernel security, networking, NetLabel, and optionally netfilter secmark support.

## Risks
Configuration combinations can subtly change access decisions. `SECURITY_SMACK_NETFILTER` alters IPv6 labeling mode in `smack.h`; `SECURITY_SMACK_APPEND_SIGNALS` changes what rules authorize signal delivery. Defaults are conservative, but distro configs need explicit review.

## Test Signals
Build all option combinations that are dependency-valid. Runtime tests should cover bringup logging, packet labeling with and without netfilter, and signal delivery authorization under write versus append mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/smack/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/smack/Makefile -->
# sources/distributed-fs/ceph-client/security/smack/Makefile

## Purpose
`security/smack/Makefile` defines how the Smack LSM object is built from its component source files.

## Important APIs, Types, and Functions
`obj-$(CONFIG_SECURITY_SMACK) := smack.o` builds Smack only when the main Kconfig symbol is enabled. `smack-y` includes `smack_lsm.o`, `smack_access.o`, and `smackfs.o`; `smack-$(CONFIG_SECURITY_SMACK_NETFILTER)` conditionally adds `smack_netfilter.o`.

## Control Flow
Kbuild aggregates the listed objects into `smack.o`. The netfilter object is linked only for secmark/netfilter mode, matching Kconfig dependencies and feature macros.

## State and Persistence
No runtime state is stored here. The file controls which compiled code is present in the kernel image/module.

## Dependencies and Integration Points
It is directly driven by `security/smack/Kconfig` and integrates with kernel Kbuild. The listed objects divide Smack into LSM hooks, access/label logic, smackfs policy interface, and optional netfilter integration.

## Risks
Adding source files without updating this Makefile causes missing symbols or dead code. Incorrect conditional linkage can break builds for configurations without netfilter support.

## Test Signals
Build Smack enabled/disabled and Smack netfilter enabled/disabled. Linker errors and missing hook behavior are the main regression signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/smack/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/smack/smack.h -->
# sources/distributed-fs/ceph-client/security/smack/smack.h

## Purpose
`smack.h` is the central Smack LSM header. It defines labels, per-object security blobs, access rule structures, network label structures, mount options, access mode flags, audit wrappers, global state declarations, and helper accessors for kernel object blobs.

## Important APIs, Types, and Functions
Core types include `smack_known`, `superblock_smack`, `socket_smack`, `inode_smack`, `task_smack`, `smack_rule`, IPv4/IPv6 network label entries, optional port labels, and audit structs. It declares access APIs from `smack_access.c`: `smk_access_entry()`, `smk_access()`, `smk_tskacc()`, `smk_curacc()`, label import/parse functions, secid lookup, NetLabel population, and privilege helpers. Inline accessors map LSM blob offsets to typed Smack structures for creds, files, inodes, IPC, superblocks, sockets, keys, and tasks.

## Control Flow
Feature macros select IPv6 port labeling versus secmark labeling. `MAY_DELIVER` depends on `CONFIG_SECURITY_SMACK_APPEND_SIGNALS`. Access flags and special labels drive the access algorithm in `smack_access.c` and hooks in `smack_lsm.c`. Audit helpers either initialize `common_audit_data` or compile away when audit is disabled.

## State and Persistence
Smack labels are represented by permanent `smack_known` entries that are added but not deleted. Per-object blobs store pointers to those shared labels and rule lists. Shared globals include known special labels, network lists, onlycap labels, hash slots, and rule cache.

## Dependencies and Integration Points
It integrates with Linux capabilities, LSM hooks/blobs, NetLabel, sockets, IPv6, audit, SysV IPC, keys, superblocks, inodes, tasks, and Smack filesystem configuration.

## Risks
Blob offset helpers must stay synchronized with `smack_blob_sizes`. Label lifetime is intentionally permanent, so import paths must validate labels and avoid unbounded abuse. Configuration-dependent access semantics need tests across option sets.

## Test Signals
Compile with audit, IPv6, netfilter, keys, and append-signal combinations. Runtime tests should cover label import, task/inode/socket blob access, transmute flags, onlycap enforcement, network label paths, and audit-data initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/smack/smack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/smack/smack_access.c -->
# sources/distributed-fs/ceph-client/security/smack/smack_access.c

## Purpose
`smack_access.c` implements Smack label repository management, core rule lookup and access decisions, audit logging, label parsing/import, NetLabel secattr population, secid-to-label translation, and MAC override privilege checks.

## Important APIs, Types, and Functions
It defines special labels `?`, `^`, `*`, `_`, and `@`, the global `smack_known_list`, `smack_known_hash`, `smack_known_lock`, `smack_onlycap_list`, and `smack_onlycap_lock`. Public functions include `smk_access_entry()`, `smk_access()`, `smk_tskacc()`, `smk_curacc()`, `smack_str_from_perm()`, `smack_log()`, `smk_insert_entry()`, `smk_find_entry()`, `smk_parse_label_len()`, `smk_parse_smack()`, `smk_netlbl_mls()`, `smack_populate_secattr()`, `smk_import_entry()`, `smk_import_valid_label()`, `smack_from_secid()`, `smack_privileged_cred()`, and `smack_privileged()`.

## Control Flow
`smk_access()` first applies hardcoded Smack rules: star subject denied, web subject/object allowed, star object allowed, equal labels allowed, hat/floor read-or-lock allowances. Otherwise it RCU-searches the subject label's rule list with `smk_access_entry()` and checks requested bits against allowed bits, with write implying lock. Task/current access wrappers add task-local restrictions and `CAP_MAC_OVERRIDE` onlycap handling. Label import parses a valid leading label, locks the global repository, reuses an existing entry or allocates/populates a new `smack_known`, assigns a secid, initializes rules, and publishes via RCU list/hash insertion.

## State and Persistence
Known labels are permanent in-memory objects and are shared by pointer. Secids monotonically increase from above the built-in labels. NetLabel attributes are cached inside each label. onlycap state restricts which labels may use MAC override capability.

## Dependencies and Integration Points
The file depends on Linux capability checks, RCU lists, NetLabel category maps/cache, audit, task creds, and constants from `smack.h`. LSM hooks call these helpers for file, task, IPC, network, and policy-interface decisions.

## Risks
Pointer/string identity assumptions require labels to come from the known-label repository. Label parsing must reject separators and options safely. Permanent label allocation can grow without deletion. Audit behavior differs under bringup mode. onlycap checks combine capability state with label membership and can affect administrative recovery.

## Test Signals
Tests should cover all built-in label shortcuts, explicit rule grants/denials, write-implies-lock, task-local restriction, `CAP_MAC_OVERRIDE` with empty and populated onlycap lists, invalid label strings, duplicate label imports, secid lookup misses, NetLabel direct versus mapped labeling, and audit logging filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/smack/smack_access.c -->
