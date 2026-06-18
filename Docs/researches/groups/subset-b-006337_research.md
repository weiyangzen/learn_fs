# subset-b-006337 AppArmor research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/policy_ns.h -->
# sources/distributed-fs/ceph-client/security/apparmor/include/policy_ns.h

Purpose: declares AppArmor policy namespaces, the containers that own profile visibility, per-namespace labels, raw policy data, apparmorfs dentries, and the namespace-local unconfined profile.

Important APIs/types: `struct aa_ns_acct` tracks maximum and current namespace policy size/count. `struct aa_ns` embeds `aa_policy`, parent linkage, `mutex lock`, accounting, `unconfined`, `sub_ns`, revision/wait state, `aa_labelset labels`, `rawdata_list`, and apparmorfs dentries. `MAX_NS_DEPTH`, `root_ns`, `kernel_t`, `ns_unconfined()`, `aa_ns_visible()`, `aa_ns_name()`, namespace lookup/create/remove helpers, and `aa_get_ns()`/`aa_put_ns()` are the main interface.

Control flow: callers prepare or find namespaces through `aa_prepare_ns()`/lookup helpers, then mutate policy under the namespace lock. Reference management is intentionally tied to the namespace's unconfined profile rather than an independent namespace kref.

State and persistence: namespace lifetime pins the unconfined profile; namespace revisions and wait queues signal policy changes; `rawdata_list` preserves loaded binary policy blobs when export is enabled. Dependencies include `apparmorfs`, `label`, and `policy`. Integration is broad: policy load/removal, label sets, secctx display, and LSM init all depend on the root namespace.

Risks and test signals: stale locks or unbalanced profile refs can leak whole namespaces. Visibility rules are security-sensitive for nested namespaces and user namespaces. Test by loading/removing nested namespaces, verifying apparmorfs entries, checking hidden namespace rendering, and exercising policy admin/view capability paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/policy_ns.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/policy_unpack.h -->
# sources/distributed-fs/ceph-client/security/apparmor/include/policy_unpack.h

Purpose: defines the binary policy-load interface used to convert serialized AppArmor policy blobs into in-kernel profiles and raw-load metadata.

Important APIs/types: `struct aa_load_ent` binds a new profile to old/rename targets and namespace names during atomic replacement. Packed flags/modes encode profile hats and runtime modes. `enum aa_code` defines the typed stream format. `struct aa_ext` is the unpack cursor. `struct aa_loaddata` holds raw policy payload, compression metadata, hash, ABI, revision, namespace, apparmorfs dentries, and two lifetimes: inode/fs users via `count` and profile users via `pcount`.

Control flow: apparmorfs receives a blob, wraps it in `aa_loaddata`, calls `aa_unpack()` into a load-entry list, then policy replacement deduplicates rawdata and attaches profile refs. KUnit-only unpack helpers expose primitive cursor reads for parser tests.

State and persistence: raw payload can remain compressed or uncompressed and may be exported under apparmorfs. `__aa_loaddata_update()` stamps policy revision, while `aa_rawdata_eq()` supports deduplication.

Dependencies and integration: integrates with `policy.c`, apparmorfs rawdata directories, hash/compression settings, profile replacement, and delayed work cleanup. Risks are malformed stream bounds, refcount split-brain between dentries and profiles, and ABI/version drift. Test signals include KUnit unpack primitive tests, invalid blob fuzzing, duplicate rawdata loads, compressed export reads, and failed atomic policy-load cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/policy_unpack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/procattr.h -->
# sources/distributed-fs/ceph-client/security/apparmor/include/procattr.h

Purpose: declares the AppArmor `/proc/<pid>/attr/` and LSM self-attribute helpers.

Important APIs: `aa_getprocattr()` renders a label into a process attribute string with optional newline. `aa_setprocattr_changehat()` parses changehat/permhat requests from procattr writes.

Control flow and integration: `lsm.c` maps `current`, `prev`, and `exec` procattr/getselfattr requests to task labels, calls `aa_getprocattr()`, and dispatches setprocattr commands such as `changehat`, `permhat`, `changeprofile`, `stack`, and on-exec variants. `aa_setprocattr_changehat()` bridges user text commands into task context label transitions.

State and persistence: no state is stored in this header; state lives in `aa_task_ctx` (`previous`, `onexec`, token) and current credentials. Dependencies are AppArmor label rendering, domain transition code, and LSM procattr hooks.

Risks and test signals: parsing must reject unterminated or empty buffers and audit invalid commands. Changehat is token-sensitive, so tests should cover successful hat change, permission-only checks, restore failure, invalid command auditing, newline rendering, and concurrent reads of stale/replaced labels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/procattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/resource.h -->
# sources/distributed-fs/ceph-client/security/apparmor/include/resource.h

Purpose: declares AppArmor mediation and transition handling for POSIX resource limits.

Important APIs/types: `struct aa_rlimit` contains a mask of controlled hard limits and `limits[RLIM_NLIMITS]`. `aa_map_resource()` maps kernel resource indices to AppArmor policy indices. `aa_task_setrlimit()` mediates `setrlimit` against a subject label and target task. `__aa_transition_rlimits()` applies profile rlimit changes across exec/profile transitions. `aa_sfs_entry_rlimit[]` exports supported rlimit names to apparmorfs.

Control flow: LSM `task_setrlimit` obtains the current label and calls `aa_task_setrlimit()` for confined labels. Exec commit invokes `__aa_transition_rlimits(old, new)` after label change is committed to reset soft limits and enforce new hard limits.

State and persistence: rules live in profile rulesets; the running process state is the kernel rlimit table. `aa_free_rlimit_rules()` is a no-op because this structure has no dynamic allocations.

Dependencies and integration: depends on Linux `resource.h`, task credentials, profile rulesets, and apparmorfs feature reporting. Risks include inconsistent resource index mapping and surprise persistence because removing policy does not restore earlier rlimits. Test with profile transitions, per-resource allow/deny, inherited limits after exec, and policy removal after confinement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/secid.h -->
# sources/distributed-fs/ceph-client/security/apparmor/include/secid.h

Purpose: declares AppArmor security identifier allocation and conversion between numeric secids, labels, and LSM security contexts.

Important APIs/constants: `AA_SECID_INVALID` is never allocated, `AA_SECID_WILDCARD` matches any secid for secmark policy, and `apparmor_display_secid_mode` controls whether mode is included in rendered secctx. The public functions are `aa_secid_to_label()`, `apparmor_secid_to_secctx()`, `apparmor_lsmprop_to_secctx()`, `apparmor_secctx_to_secid()`, `apparmor_release_secctx()`, `aa_alloc_secid()`, and `aa_free_secid()`.

Control flow: labels receive secids during label initialization; network secmark and LSM secctx hooks convert between secids and AppArmor label names. Release frees allocated security context memory through the LSM context wrapper.

State and persistence: secids pin labels while active; freeing a label releases its secid. The wildcard value is policy semantics, not an allocated object.

Dependencies and integration: integrates with label lifecycle, socket/secmark checks, audit, LSM hooks, and sysctl control in `lsm.c`. Risks include stale secid-to-label references after label replacement and ambiguous string-to-secid parsing. Test with label replacement, secmark wildcard rules, getpeersec/secctx hooks, display-mode toggles, and invalid secctx inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/secid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/sig_names.h -->
# sources/distributed-fs/ceph-client/security/apparmor/include/sig_names.h

Purpose: provides architecture-aware signal-number normalization and audit names for AppArmor signal mediation.

Important data: `sig_map[MAXMAPPED_SIG]` maps Linux signal numbers to stable AppArmor internal signal IDs, folding aliases such as `SIGPOLL`/`SIGIO` and optional architecture signals behind `#ifdef`s. `sig_names[MAXMAPPED_SIGNAME]` maps those internal IDs to policy/audit names, with `"exists"` reserved as the final existence-test entry.

Control flow: `ipc.c` includes this file and calls `map_signal_num()` to map `sig` into a DFA input symbol. Audit code then renders `sig_names[ad->signal]` or an `rtmin+N` form for realtime signals.

State and persistence: static read-only tables only.

Dependencies and integration: depends on `<linux/signal.h>` and `include/signal.h`; integrates with `AA_SFS_SIG_MASK`, signal DFA policy, and audit records. Risks are architecture-specific alias drift and table-size mismatch with `MAXMAPPED_SIG`. Test by compiling on architectures with optional `SIGEMT`, `SIGSTKFLT`, `SIGLOST`, and `SIGUNUSED`, and by mediating standard, unknown, zero, and realtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/sig_names.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/signal.h -->
# sources/distributed-fs/ceph-client/security/apparmor/include/signal.h

Purpose: defines the stable numeric range AppArmor uses for signal mediation.

Important constants: `SIGUNKNOWN` is the fallback signal class, `MAXMAPPED_SIG` bounds normal signal mapping, `MAXMAPPED_SIGNAME` adds the synthetic existence-test name, and `SIGRT_BASE` is the offset used for realtime signal policy symbols.

Control flow and integration: `sig_names.h` sizes its mapping/name tables with these constants, `ipc.c` maps kernel signal numbers into these IDs, and `task.h` publishes the supported signal names through `AA_SFS_SIG_MASK`.

State and persistence: none; this is compile-time policy ABI. Dependencies are minimal, but semantic consumers include the signal DFA, audit formatting, and apparmorfs feature reporting.

Risks and test signals: changing constants is ABI-sensitive because loaded policy and user tools expect stable signal IDs. Tests should ensure realtime signals map to `SIGRT_BASE + offset`, unknown values map to `SIGUNKNOWN`, `sig_names` remains one longer than `MAXMAPPED_SIG`, and apparmorfs feature strings remain aligned with policy compiler expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/task.h -->
# sources/distributed-fs/ceph-client/security/apparmor/include/task.h

Purpose: declares per-task AppArmor state, task label transition helpers, ptrace mediation constants, signal feature strings, and user-namespace mediation entry points.

Important APIs/types: `task_ctx()` locates AppArmor's task blob. `struct aa_task_ctx` stores `nnp`, `onexec`, `previous`, and `token` for no-new-privs and procattr transitions. Helpers include `aa_replace_current_label()`, `aa_set_current_onexec()`, `aa_set_current_hat()`, `aa_restore_previous_label()`, `aa_get_task_label()`, `aa_free_task_ctx()`, `aa_dup_task_ctx()`, and `aa_clear_task_ctx_trans()`. Permission masks define ptrace, signal, and user-namespace create mediation.

Control flow: task allocation duplicates current transition state with label refs; task free drops refs; exec commit clears transitional fields; procattr and domain code modify `previous`/`onexec`/token.

State and persistence: task context persists for task lifetime and is copied on fork. Label refs are explicitly managed to survive RCU profile replacement.

Dependencies and integration: depends on LSM blob sizing, label refs, domain transition, ptrace hooks, signal hooks, and userns hooks. Risks include token mishandling, leaked labels on clone/free, and stale onexec transitions after exec. Test fork/exec, changehat restore, ptrace permissions, signal send/receive, no-new-privs interactions, and user namespace creation policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/task.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/ipc.c -->
# sources/distributed-fs/ceph-client/security/apparmor/ipc.c

Purpose: implements AppArmor signal IPC mediation between sender and target labels.

Important functions: `map_signal_num()` converts kernel signal numbers to AppArmor DFA symbols, including realtime offsets and unknown fallback. `audit_signal_mask()` and `audit_signal_cb()` render send/receive masks, signal names, unmapped values, and peer labels. `profile_signal_perm()` performs one profile-side DFA check. `aa_may_signal()` performs bidirectional sender-write and target-read checks with `xcheck_labels()`.

Control flow: the LSM `task_kill` hook collects sender and target credentials/labels, then calls `aa_may_signal()`. For each relevant label/profile pairing, policy starts at `AA_CLASS_SIGNAL`, transitions on the mapped signal, matches the peer label, applies profile modes, and audits denied or forced-audit permissions.

State and persistence: no persistent state; all decisions derive from current labels, rulesets, and audit data. Dependencies include signal mapping tables, label matching, policy DFA, credentials, and audit.

Risks and test signals: signal aliases, realtime ranges, and signal zero existence checks are subtle. Bidirectional checks must use the correct subject credentials for send and receive. Test confined sender/receiver combinations, unconfined bypass, unknown signals, realtime signals, audit peer rendering, and policy with peer-label conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/ipc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/label.c -->
# sources/distributed-fs/ceph-client/security/apparmor/label.c

Purpose: implements AppArmor labels: canonical ordered profile sets, labelset insertion/replacement, stale-label update, proxy redirection, label parsing, label matching, and label name/audit rendering.

Important APIs/functions: proxy lifecycle (`aa_alloc_proxy()`, `__aa_proxy_redirect()`), vector canonicalization (`aa_vec_unique()`), label lifecycle (`aa_label_init()`, `aa_label_alloc()`, `aa_label_destroy()`, `aa_label_kref()`), set operations (`aa_label_insert()`, `aa_label_remove()`, `aa_label_replace()`), subset/merge operations (`aa_label_is_subset()`, `aa_label_merge()`), policy matching (`aa_label_match()`), printing (`aa_label_snxprint()`, `aa_label_asxprint()`, `aa_label_xaudit()`), parsing (`aa_label_strn_parse()`), and stale refresh (`__aa_labelset_update_subtree()`).

Control flow: labels are sorted by namespace depth/name and profile hname, then interned in a namespace `aa_labelset` red-black tree. Replacement marks old labels stale, redirects their proxy to the new label, and later RCU frees unused labels. Compound label policy first tries a full `A//&B` DFA match, then per-component accumulation if needed.

State and persistence: labels hold profile refs, secids, optional cached names, proxies, tree nodes, flags, and mediates bitmasks. Proxies let tasks and objects follow policy replacement without immediate mutation.

Dependencies and integration: used by credentials, files, sockets, policy replacement, secid, audit, procattr, IPC, network, and mount mediation. Risks include lock ordering across namespace labelsets, proxy cycles, duplicate profile refs, stale component updates, hidden namespace rendering, and allocation failure during replacement. Test label parse/print round trips, stacking, namespace visibility, concurrent replacement under RCU, secid free, merge/subset behavior, and audit strings containing control characters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/label.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/lib.c -->
# sources/distributed-fs/ceph-client/security/apparmor/lib.c

Purpose: provides common AppArmor helpers for debug parsing, string tables, counted strings, policy names, permission printing, and permission/audit mode evaluation.

Important APIs/functions: `aa_parse_debug_params()` and `aa_print_debug_params()` map sysfs debug strings. `aa_resize_str_table()`/`aa_destroy_str_table()` manage unpacked string tables. `skipn_spaces()` and `aa_splitn_fqname()` parse policy namespace/profile names. `aa_info_message()` logs status. `aa_str_alloc()`/`aa_str_kref()` implement counted strings. `aa_perm_mask_to_str()`, `aa_audit_perm_names()`, and `aa_audit_perm_mask()` format permission masks. `aa_apply_modes_to_perms()` applies audit/complain/kill/user modes. `aa_check_perms()` centralizes allow/deny/audit return semantics. `aa_policy_init()`/`aa_policy_destroy()` manage hierarchical policy names.

Control flow: mediation code computes `aa_perms`, applies modes, then calls `aa_check_perms()` to decide error and audit type. Name parsing supports both `:ns:profile` and policy hierarchy forms.

State and persistence: `nullperms`, `allperms`, file permission names, and counted policy strings are shared infrastructure. Dependencies include audit, profile modes, and policy structures.

Risks and test signals: incorrect mode application can silently allow complain-mode denials or suppress audit. Name parsing is security-sensitive for namespace boundaries. Test debug sysfs parsing, permission mask formatting, `hide` returning `-ENOENT`, complain/kill/user modes, and fqname parsing edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/lsm.c -->
# sources/distributed-fs/ceph-client/security/apparmor/lsm.c

Purpose: registers AppArmor as an LSM and implements the kernel hook glue for credentials, paths, files, mmap, mounts, procattrs, exec, task controls, sockets, secctx, io_uring, sysctl, netfilter secmark, buffer caching, and module parameters.

Important APIs/functions: credential hooks manage `cred_label`; file/path hooks call `aa_path_perm()`, `aa_file_perm()`, and mount helpers; procattr hooks dispatch profile/hat transitions; task hooks mediate rlimits, ptrace, signals, and user namespace creation; socket hooks label sockets, mediate AF/Unix/secmark operations, and serve peer secctx; `aa_get_buffer()`/`aa_put_buffer()` provide reusable pathname buffers; `apparmor_init()` initializes DFA engines, root namespace, sysctls, buffers, init label, hooks, and audit LSM config.

Control flow: hooks usually enter a current-label critical section, bypass unconfined labels, call the subsystem-specific mediator, then release refs. Exec commit inherits file permissions, clears death signal, transitions rlimits, and later clears task transition context. Init unpacks `nulldfa.in` and `stacksplitdfa.in`, allocates `nullpdb`, creates apparmorfs, then registers hooks via `DEFINE_LSM`.

State and persistence: global knobs include mode, audit, debug, lock_policy, path_max, rawdata export/compression, initialized/enabled flags, root namespace, DFA globals, per-CPU/global buffer pools, LSM blob sizes, sysctls, and socket/file/task blobs.

Dependencies and integration: this is the integration hub for all AppArmor modules plus Linux LSM, audit, netfilter, sysfs, sysctl, zstd, and apparmorfs. Risks include refcount mistakes in blobs, sleeping/allocation in atomic contexts, parameter permission bypass, policy lock semantics, hook ordering, and secmark drop behavior. Test boot enable/disable, init failure cleanup, all hook classes, module parameter permissions, buffer exhaustion, netfilter secmark, io_uring, and policy replacement during active task/file/socket use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/lsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/match.c -->
# sources/distributed-fs/ceph-client/security/apparmor/match.c

Purpose: implements AppArmor's serialized DFA unpacker, verifier, matcher, out-of-band transitions, accept-until matching, and leftmatch fallback.

Important APIs/functions: `aa_dfa_unpack()` parses table-set headers and tables; `verify_table_headers()` and `verify_dfa()` validate sizes, bounds, diff-encoding chains, and OOB transition flags; `aa_dfa_free_kref()` frees tables; `aa_dfa_match_len()`, `aa_dfa_match()`, `aa_dfa_next()`, `aa_dfa_outofband_transition()`, `aa_dfa_match_until()`, `aa_dfa_matchn_until()`, and `aa_dfa_leftmatch()` perform runtime matching.

Control flow: unpack reads big-endian table metadata, validates accepted table data widths, remaps 16-bit transition tables to 32-bit, optionally verifies all transitions, then exposes compact default/base/next/check tables. Matching uses optional equivalence classes and a default-chain loop to transition for each byte.

State and persistence: a DFA owns kvallocated tables and a kref. Loaded profile policy DBs, `nulldfa`, and `stacksplitdfa` hold references.

Dependencies and integration: all policy classes use this engine through policy DB start states and permission lookup. Risks include malformed policy blobs, integer bounds around `base_idx + 255`, diff-encoding loops, OOB `-1` transition indexing, vmalloc alias synchronization, and accepting unverified states. Test with valid/invalid packed DFAs, 16-bit remap, EC tables, diff encoded chains, OOB transitions, null transitions, and policy fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/mount.c -->
# sources/distributed-fs/ceph-client/security/apparmor/mount.c

Purpose: mediates mount, remount, bind, move, propagation-change, unmount, and pivotroot operations against AppArmor mount policy.

Important functions: `audit_mnt_flags()`, `audit_mount()`, `match_mnt_flags()`, `do_match_mnt()`, `match_mnt_path_str()`, `match_mnt()`, `aa_remount()`, `aa_bind_mount()`, `aa_mount_change_type()`, `aa_move_mount()`, `aa_move_mount_old()`, `aa_new_mount()`, `aa_umount()`, `build_pivotroot()`, and `aa_pivotroot()`.

Control flow: LSM mount hooks normalize mount flags and select an operation helper. Helpers allocate pathname buffers, resolve mountpoint/source paths where needed, determine binary mount-data handling from filesystem flags, and run each confined profile through a DFA sequence: mountpoint, null, source, null, type, null, ordered flags, optional data, then permission lookup. Pivotroot can build and install a replacement label after successful policy match.

State and persistence: no standalone persistent state; decisions use profile rules, path flags, global path buffers, current labels, and VFS path refs. Pivotroot may persistently change the current label.

Dependencies and integration: depends on path lookup, DFA matching, file system type lookup, audit, domain label replacement, and LSM mount hooks. Risks include path lookup failure semantics, binary data non-matching, flag normalization, source path resolution for detached mounts, and pivotroot transition auditing gaps. Test all mount modes, missing device on `FS_REQUIRES_DEV`, bind/move with disconnected paths, binary mount data, propagation flags, unmount auditing, and pivotroot label transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/mount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/net.c -->
# sources/distributed-fs/ceph-client/security/apparmor/net.c

Purpose: implements generic network-family mediation, Unix audit formatting helpers, socket-file permission bridging, and optional secmark checks.

Important APIs/functions: `aa_sfs_entry_network[]` and `aa_sfs_entry_networkv9[]` report network features. `audit_net_cb()` emits family/type/protocol, net permission masks, Unix addresses, and peer labels. `aa_do_perms()` applies modes and checks permissions. `aa_match_to_prot()` matches AF/type/protocol triples. `aa_profile_af_perm()`, `aa_af_perm()`, `aa_sk_perm()`, and `aa_sock_file_perm()` mediate create/socket operations. With secmark enabled, `apparmor_secmark_init()`, `aa_secmark_perm()`, and `apparmor_secmark_check()` map label strings to secids and enforce packet labels.

Control flow: socket hooks in `lsm.c` pass current label and socket metadata. Policy starts at network class, matches big-endian family/type/protocol, optionally uses early permissions when `AA_CONT_MATCH` is not required, then audits via `audit_net_cb()`.

State and persistence: secmark entries cache resolved secids in rulesets. Socket labels live in `aa_sk_ctx`, not here.

Dependencies and integration: depends on AF/Unix helpers, labels, policy DBs, secid conversion, audit, and apparmorfs feature reporting. Risks include family/type bounds, protocol matching differences, lazy secmark initialization in atomic contexts, wildcard secids, and Unix abstract address audit escaping. Test AF create/connect/listen/bind paths, Unix peer audit, socket file receive, secmark allow/deny/audit/wildcard, and unconfined bypass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/nulldfa.in -->
# sources/distributed-fs/ceph-client/security/apparmor/nulldfa.in

Purpose: provides a compiled binary DFA byte array included by `lsm.c` as the built-in null policy automaton.

Important content: the file is a comma-separated hexadecimal byte stream, 8-byte aligned by the including C declaration. It begins with the AppArmor DFA table-set magic/header and includes serialized accept/default/base/next/check data for a minimal "notflex" DFA.

Control flow: `aa_setup_dfa_engine()` includes this file into `nulldfa_src[]`, unpacks it with `aa_dfa_unpack()` accepting 32-bit accept tables, assigns it to `nulldfa`, and attaches it to `nullpdb`. Null profiles and placeholder ancestors use `nullpdb` for file and policy rules, making this blob the default no-permission/learning placeholder engine.

State and persistence: static built-in data only; runtime state is the unpacked `aa_dfa` and `aa_policydb` references created during LSM init.

Dependencies and integration: tightly coupled to `match.c`'s serialized DFA format and `policy.c` null profile creation. Risks include silent corruption of a binary source file that is hard to review, mismatch with expected table flags, and boot failure if unpack verification rejects it. Test by boot/init of AppArmor, null profile allocation, DFA unpack validation, and comparing regenerated null DFA bytes from the policy compiler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/nulldfa.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/path.c -->
# sources/distributed-fs/ceph-client/security/apparmor/path.c

Purpose: resolves VFS paths into AppArmor mediation names while handling chroot-relative lookup, disconnected paths, deleted dentries, internal mounts, directory suffixes, and audit diagnostics.

Important functions: `prepend()` safely prepends text into the backwards path buffer. `disconnect()` handles paths not connected to the expected root and optional disconnected prefixes. `d_namespace_path()` performs the main lookup using `dentry_path()`, `__d_path()`, `d_absolute_path()`, or `dentry_path_raw()`. `aa_path_name()` wraps lookup and maps errors to human-readable info.

Control flow: callers provide a buffer sized by `aa_g_path_max` and path flags. Internal mounts use dentry paths and special-case proc sysctl paths. Chroot-relative lookup uses current fs root; otherwise absolute path lookup is used. Disconnected paths may be denied or prefixed depending on policy flags. Directories get a trailing slash except root.

State and persistence: no persistent state; consumes global `aa_g_path_max`, current fs root, mount namespace membership, and profile path flags.

Dependencies and integration: used by file, mount, link/rename, and audit mediation. Risks include off-by-one buffer handling, name-too-long behavior, deleted dentry mediation flags, chroot escape/connect semantics, and internal proc/sys rewriting. Test deleted files, disconnected bind mounts, chroot-relative paths, directories, root, long paths, internal proc/sys paths, and `PATH_CONNECT_PATH`/`PATH_CHROOT_NSCONNECT` combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/path.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/policy.c -->
# sources/distributed-fs/ceph-client/security/apparmor/policy.c

Purpose: implements AppArmor profile/policy object lifecycle, hierarchical lookup, null and learning profiles, policy admin checks, atomic profile replacement/load, and policy removal.

Important APIs/functions: policy DB lifecycle (`aa_alloc_pdb()`, `aa_pdb_free_kref()`), profile/ruleset lifecycle (`aa_alloc_ruleset()`, `aa_alloc_profile()`, `aa_free_profile()`), profile list mutation (`__add_profile()`, `__remove_profile()`), lookup (`aa_find_child()`, `aa_lookupn_profile()`, `aa_fqlookupn_profile()`), null/learning profile creation (`aa_alloc_null()`, `aa_new_learning_profile()`), capability checks (`aa_policy_view_capable()`, `aa_policy_admin_capable()`, `aa_may_manage_policy()`), replacement (`aa_replace_profiles()`), and removal (`aa_remove_profiles()`).

Control flow: `aa_replace_profiles()` unpacks a load blob, enforces a single namespace, prepares/locks the namespace, deduplicates rawdata, resolves old/rename/parent entries, creates apparmorfs nodes, bumps namespace revision, then atomically replaces or adds profiles and updates stale labels across the subtree. Failure audits the causative entry and marks the rest of the atomic set as failed. Removal resolves a namespace/profile, bumps revision, removes profile trees or namespaces, and updates labels.

State and persistence: profiles own labels, rulesets, attachments, rawdata refs, children, parent refs, hashes, data tables, and apparmorfs dentries. Namespace revisions and rawdata exports persist policy load history while refs remain.

Dependencies and integration: depends on policy unpack, namespaces, label replacement, apparmorfs, capability, resource, file, IPC, and path modules. Risks include atomicity across profile sets, namespace lock ordering, missing ancestor placeholder semantics, rawdata/profile ref cycles, immutable/noreplace handling, user namespace policy admin checks, and rlimit persistence after removal. Test atomic multi-profile load failure, replacement with children/hats, missing parent creation, rename, same-rawdata dedup, policy lock, unprivileged user namespace controls, namespace removal, and active task label refresh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/policy.c -->
