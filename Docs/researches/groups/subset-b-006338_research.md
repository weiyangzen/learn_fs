# subset-b-006338 Research

Grouped source-tree-aligned research for the requested security, AppArmor, BPF LSM, common capability, device cgroup, securityfs, integrity, and EVM files.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/policy_compat.c -->
# sources/distributed-fs/ceph-client/security/apparmor/policy_compat.c

Purpose: converts older AppArmor packed policy DFA permission encodings into the current `struct aa_perms` table model used by the policy engine. It supports legacy file permission layouts, generic policydb versions, and xmatch DFAs so older userspace policy compilers can still load policy into newer kernels.

Important APIs, types, and functions: exported entry points are `aa_compat_map_xmatch()`, `aa_compat_map_policy()`, and `aa_compat_map_file()`. They allocate `policy->perms`, set `policy->size`, and rewrite DFA accept tables through `remap_dfa_accept()`. Internal helpers include `dfa_map_xindex()`, `map_old_perms()`, `compute_fperms_*()`, `compute_xmatch_perms()`, `compute_perms_entry()`, `map_other()`, and `map_xbits()`. The code depends on `struct aa_policydb`, `struct aa_dfa`, `struct aa_perms`, `ACCEPT_TABLE()`, `ACCEPT_TABLE2()`, and version predicates such as `VERSION_LE(version, v8)`.

Control flow: each public mapper allocates a permission table from DFA state count, fills it state-by-state from embedded accept bits, then rewrites accept1/accept2 to permission-table indexes. File DFAs get two entries per DFA state for user/other owner-condition variants. Generic policydb mapping treats accept1 as base user permissions and accept2 as extension bits/audit/quiet, with version-specific handling around v8/v9 xbits.

State and persistence: it mutates in-memory policydb state only: `policy->perms`, `policy->size`, and the DFA accept tables. No filesystem state is changed. Allocation uses `kvzalloc_objs()` and failures leave callers with `-ENOMEM`.

Dependencies and integration: called from `policy_unpack.c` when loaded policy lacks an explicit `perms` table. Its output is later verified by `verify_profile()` and consumed by rule lookup paths. It integrates with AppArmor permission constants, xtransition encodings, DFA table layouts, and debug logging.

Risks and test signals: compatibility bit layouts are historical and easy to mis-map; errors can grant, deny, or audit the wrong operation. The owner split and xindex remapping are especially sensitive because accept2 becomes an owner flag for file DFAs. There is no direct KUnit file for this mapper; practical tests are successful loads of legacy v5-v9 policy, accept index verification, and permission behavior regression tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/policy_compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/policy_ns.c -->
# sources/distributed-fs/ceph-client/security/apparmor/policy_ns.c

Purpose: manages AppArmor policy namespaces, including root namespace allocation, namespace visibility/name virtualization, lookup, creation, recursive teardown, and the special unconfined labels for root and kernel contexts.

Important APIs, types, and functions: global state is `root_ns`, `kernel_t`, and `aa_hidden_ns_name`. Public helpers include `aa_ns_visible()`, `aa_ns_name()`, `aa_free_ns()`, `__aa_lookupn_ns()`, `aa_lookupn_ns()`, `__aa_find_or_create_ns()`, `aa_prepare_ns()`, `__aa_remove_ns()`, `aa_alloc_root_ns()`, and `aa_free_root_ns()`. Allocation flows through `alloc_ns()` and `alloc_unconfined()`; teardown flows through `destroy_ns()` and `__ns_list_release()`.

Control flow: namespace lookup walks hierarchical names split on `"//"` under RCU. Creation requires the parent namespace lock, allocates initialized namespace state, creates AppArmorFS namespace directories, links the namespace into the parent `sub_ns` list with RCU, and returns a counted reference. Removal unlinks from the parent, destroys profiles and child namespaces recursively, redirects unconfined proxy labels to the parent, removes AppArmorFS nodes, and drops list refs.

State and persistence: namespace objects hold profile lists, child namespace lists, raw load data, labels, wait queues, locks, parent refs, and an unconfined profile. Persistent user-visible state is exposed through AppArmorFS directories, but this file itself only creates/removes those nodes via `__aafs_ns_mkdir()` and `__aafs_ns_rmdir()`.

Dependencies and integration: depends on AppArmor policy/list primitives, labelsets, AppArmorFS namespace layout, RCU list traversal, mutex nesting by namespace level, and profile allocation/freeing. It is used by policy load/unload and label display logic.

Risks and test signals: refcount/list ownership is subtle: `ns->unconfined` shares namespace lifetime assumptions, and RCU readers require correct lock/ref rules. Namespace visibility affects procattr/secctx disclosure. Test signals include namespace creation depth enforcement, duplicate namespace rejection, recursive unload, visible/hidden namespace names, and AppArmorFS cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/policy_ns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/policy_unpack.c -->
# sources/distributed-fs/ceph-client/security/apparmor/policy_unpack.c

Purpose: implements AppArmor's binary policy loader. It parses user-provided packed policy streams, validates the ABI/version, allocates profiles and policy databases, remaps legacy permission formats, verifies internal consistency, optionally hashes/compresses raw policy data, and returns `aa_load_ent` records for policy replacement.

Important APIs, types, and functions: exported/high-value functions include `aa_loaddata_alloc()`, `aa_rawdata_eq()`, `__aa_loaddata_update()`, `aa_loaddata_kref()`, `aa_ploaddata_kref()`, `aa_load_ent_alloc()`, `aa_load_ent_free()`, and `aa_unpack()`. KUnit-visible primitives include `aa_inbounds()`, `aa_unpack_u16_chunk()`, `aa_unpack_X()`, `aa_unpack_nameX()`, `aa_unpack_u32()`, `aa_unpack_u64()`, `aa_unpack_array()`, `aa_unpack_blob()`, `aa_unpack_str()`, and `aa_unpack_strdup()`. Core internal stages are `unpack_dfa()`, `unpack_strs_table()`, `unpack_xattrs()`, `unpack_secmark()`, `unpack_rlimits()`, `unpack_tags()`, `unpack_perms_table()`, `unpack_pdb()`, `unpack_profile()`, `verify_header()`, `verify_profile()`, and `compress_loaddata()`.

Control flow: `aa_unpack()` initializes an `aa_ext` cursor over `udata->data`, repeatedly verifies an optional/required stream header, unpacks one profile, verifies it, hashes it if enabled, wraps it in an `aa_load_ent`, and appends to the output list. Profile unpacking checks structure tags, handles namespace-qualified names, flags/modes/caps, attachment/xmatch, rlimits, secmark, policydb, file rules, and arbitrary profile data. Policydb unpacking optionally reads tags and a permission table, unpacks a DFA, computes class start states, unpacks transition tables, and leaves legacy permission conversion to the caller.

State and persistence: mutates allocated profile/policydb/load-entry objects and `aa_loaddata` metadata (`abi`, `hash`, `compressed_size`, `data`). It can update AppArmorFS loaddata inode timestamps in `__aa_loaddata_update()` and schedules deferred rawdata fs removal via workqueue in `aa_ploaddata_kref()`.

Dependencies and integration: depends on AppArmor audit, credential, DFA, policy, label, crypto, file/path, signal, resource, and compatibility-mapping helpers. It also uses kernel rhashtable for profile data blobs and zstd when binary export compression is configured.

Risks and test signals: this is a parser for privileged policy input, so cursor rollback, bounds checking, integer sizes, null-terminated strings, DFA alignment, version gates, and cleanup paths are critical. Verification checks permission conflicts, accept indexes, tags, transition indexes, and label indexes. KUnit tests cover primitive unpackers and out-of-bounds rollback; broader signals require policy load tests for valid/invalid ABI versions, malformed DFAs, optional tables, legacy compatibility, compression/hash modes, and failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/policy_unpack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/policy_unpack_test.c -->
# sources/distributed-fs/ceph-client/security/apparmor/policy_unpack_test.c

Purpose: KUnit coverage for the low-level AppArmor binary unpack primitives exported under `EXPORTED_FOR_KUNIT_TESTING`.

Important APIs, types, and functions: defines `struct policy_unpack_fixture`, `build_aa_ext_struct()`, `policy_unpack_test_init()`, and KUnit cases for `aa_inbounds()`, `aa_unpack_array()`, `aa_unpack_blob()`, `aa_unpack_str()`, `aa_unpack_strdup()`, `aa_unpack_nameX()`, `aa_unpack_u16_chunk()`, `aa_unpack_u32()`, `aa_unpack_u64()`, and `aa_unpack_X()`. Test data is built with typed tags, named elements, little-endian integer encodings, and offsets derived from string sizes.

Control flow: each test starts from a fixture buffer with serialized AppArmor elements, adjusts `e->pos` and sometimes `e->end`, invokes one unpack helper, and asserts returned data plus cursor position. Negative tests verify that helpers fail cleanly and reset `e->pos` when a name/code/bounds check fails.

State and persistence: no persistent state; all allocations are KUnit-managed except strings returned by `aa_unpack_strdup()`, which tests free explicitly. Some tests intentionally extend `e->end` beyond allocated data only for pointer arithmetic comparisons.

Dependencies and integration: included by KUnit when AppArmor policy unpack testing is enabled; imports the KUnit export namespace and validates functions in `policy_unpack.c`.

Risks and test signals: coverage is strong for primitive cursor behavior but does not exercise full profile unpacking, DFA parsing, tag verification, or compatibility mapping. Important signals are preserving cursor rollback, rejecting out-of-bounds reads, ensuring duplicated strings are outside the source buffer, and matching little-endian integer values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/policy_unpack_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/procattr.c -->
# sources/distributed-fs/ceph-client/security/apparmor/procattr.c

Purpose: implements AppArmor's `/proc/<pid>/attr/` label display and `change_hat` write parsing.

Important APIs, types, and functions: public functions are `aa_getprocattr()` and `aa_setprocattr_changehat()`. Internal `split_token_from_name()` parses the `<hex-token>^<hat-name>` procattr format.

Control flow: `aa_getprocattr()` gets the current AppArmor namespace, checks whether the target label namespace is visible, measures formatted label length with `aa_label_snxprint()`, allocates a buffer, prints label mode/name with subnamespace visibility and hidden-unconfined flags, appends an optional newline, and returns the length. `aa_setprocattr_changehat()` parses the token, builds a vector of up to 16 NUL-separated hat names, then calls `aa_change_hat()`.

State and persistence: reads current namespace/label state and allocates a returned string for procfs callers. It does not directly mutate policy; mutation is delegated to domain transition code through `aa_change_hat()`.

Dependencies and integration: integrates with procattr LSM hooks, AppArmor namespace visibility, label rendering, domain transitions, and AppArmor debug/error logging.

Risks and test signals: namespace visibility failures must not leak label names. The parser must reject malformed tokens, empty token/name combinations, and overlong hat vectors. Test signals include procattr reads from same/sub/hidden namespaces and writes for single hat, multi-hat, restore-token, malformed delimiter, and zero-token cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/procattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/resource.c -->
# sources/distributed-fs/ceph-client/security/apparmor/resource.c

Purpose: mediates `setrlimit()` operations under AppArmor profiles and applies profile-defined resource limits during label transitions.

Important APIs, types, and functions: exports `aa_sfs_entry_rlimit`, `aa_map_resource()`, `aa_task_setrlimit()`, and `__aa_transition_rlimits()`. Internal helpers are `audit_cb()`, `audit_resource()`, and `profile_setrlimit()`. It uses generated `rlim_names.h` and architecture-specific `rlim_map[]`.

Control flow: `aa_task_setrlimit()` obtains the target task label, requires `CAP_SYS_RESOURCE` when setting another differently labeled task's limit, otherwise iterates confined profiles and denies hard-limit raises above policy maxima. `__aa_transition_rlimits()` first relaxes soft limits controlled by the old label back toward init-task soft limits, then clamps current hard/soft limits to the new label's maxima and updates CPU timers when needed.

State and persistence: mutates `current->signal->rlim[]` during profile transitions and emits audit records. Policy rlimit settings are read from `rules->rlimits`.

Dependencies and integration: tied to AppArmor rulesets, label iteration, capability checks, audit callbacks, Linux `struct rlimit`, and POSIX CPU timer update code.

Risks and test signals: architecture resource-number mapping must match the compiler's flattened policy order. Cross-label setrlimit behavior depends on a capability fallback. Test signals include hard-limit denial, peer-label audit output, transition clamping, old-policy soft-limit reset, and RLIMIT_CPU timer updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/secid.c -->
# sources/distributed-fs/ceph-client/security/apparmor/secid.c

Purpose: maps AppArmor labels to numeric secids and converts secids/LSM properties to printable security contexts.

Important APIs, types, and functions: global state is `aa_secids` xarray and `apparmor_display_secid_mode`. Public functions include `aa_secid_to_label()`, `apparmor_secid_to_secctx()`, `apparmor_lsmprop_to_secctx()`, `apparmor_secctx_to_secid()`, `apparmor_release_secctx()`, `aa_alloc_secid()`, and `aa_free_secid()`. Internal `apparmor_label_to_secctx()` formats labels from `root_ns`.

Control flow: secid allocation locks the xarray with IRQ-save, allocates an ID from `AA_FIRST_SECID` upward, stores the label pointer, and writes `label->secid`. Conversion from secctx parses a label string relative to root unconfined label and returns its secid. Release frees only AppArmor-owned contexts.

State and persistence: secids are in-memory xarray entries and intentionally do not pin labels; label replacement/freeing must keep mappings coherent. Context conversion allocates strings for callers.

Dependencies and integration: used by LSM secctx hooks, audit/netlabel-facing code, label parsing/rendering, root namespace state, and LSM context IDs.

Risks and test signals: because secids do not hold label refs, stale mapping prevention depends on label lifecycle code outside this file. Test signals include secid allocation/free reuse, invalid label parse errors, display mode inclusion, and release behavior for non-AppArmor contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/secid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/stacksplitdfa.in -->
# sources/distributed-fs/ceph-client/security/apparmor/stacksplitdfa.in

Purpose: static serialized AppArmor DFA input used for stack-splitting/name parsing behavior, with the leading comment documenting the source pattern `0x1 [^\000]*[^/\000]//&`.

Important APIs, types, and functions: no C APIs or functions. The file is a byte table consumed by AppArmor build-time or generated-DFA include machinery alongside other `.in` DFA blobs.

Control flow: none at runtime in this file; consumers treat the bytes as a compiled DFA. The encoded automaton appears to detect hierarchical namespace/profile split markers involving `"//"` after non-slash content.

State and persistence: immutable source artifact. Runtime state is whatever DFA object the build/include path creates from these bytes.

Dependencies and integration: integrates with AppArmor DFA unpack/match code and build rules that embed generated DFA data. It is related to name parsing, stack splitting, and namespace/profile separators.

Risks and test signals: hand-maintained byte blobs are opaque; corruption may not be obvious until matching behavior changes. Test signals are successful DFA unpacking and policy-name parsing cases around empty components, slash boundaries, and `"//"` split markers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/stacksplitdfa.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/task.c -->
# sources/distributed-fs/ceph-client/security/apparmor/task.c

Purpose: handles AppArmor task label access/replacement, hat/on-exec context state, ptrace mediation, and user namespace creation mediation.

Important APIs, types, and functions: public functions are `aa_get_task_label()`, `aa_replace_current_label()`, `aa_set_current_onexec()`, `aa_set_current_hat()`, `aa_restore_previous_label()`, `aa_may_ptrace()`, and `aa_profile_ns_perm()`. Internal mediation helpers include `profile_ptrace_perm()`, `profile_tracee_perm()`, `profile_tracer_perm()`, `audit_ptrace_cb()`, `get_current_exe_path()`, and `audit_ns_cb()`.

Control flow: label replacement prepares new credentials, updates stale NNP labels, clears task transition state when moving unconfined or across namespaces, then commits the new label. Hat switching stores/restores prior labels guarded by a token. Ptrace mediation checks both tracer and tracee label views through `xcheck_labels()`, falling back to `CAP_SYS_PTRACE` for old-style profiles. User namespace mediation looks up class policy state and checks `AA_USERNS_CREATE`.

State and persistence: mutates current task credentials and `aa_task_ctx` fields (`previous`, `onexec`, `token`, `nnp`). It reads peer task creds under RCU and emits audit records, including executable path when available.

Dependencies and integration: tied to Linux credential commit flow, AppArmor label/ruleset APIs, ptrace LSM hooks, namespace creation hooks, path rendering, and audit logging.

Risks and test signals: credential replacement must preserve label refs correctly while racing label replacement. Hat token checks are security-critical. `get_current_exe_path()` has an error path that must release acquired file/path refs. Test signals include self/peer ptrace allow/deny, stale label replacement, change_hat/restore token behavior, on-exec clearing, and userns audit output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/task.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/bpf/Makefile -->
# sources/distributed-fs/ceph-client/security/bpf/Makefile

Purpose: builds the BPF LSM support object when `CONFIG_BPF_LSM` is enabled.

Important APIs, types, and functions: the only build rule is `obj-$(CONFIG_BPF_LSM) := hooks.o`.

Control flow: Kbuild includes `hooks.o` in the security/bpf object list conditionally on the config symbol.

State and persistence: no runtime state.

Dependencies and integration: depends on the kernel Kbuild system and the BPF LSM Kconfig symbol. It directly controls whether `hooks.c` participates in the build.

Risks and test signals: risk is limited to build inclusion. Test signals are successful builds with `CONFIG_BPF_LSM=y/m` and absence of BPF LSM hooks when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/bpf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/bpf/hooks.c -->
# sources/distributed-fs/ceph-client/security/bpf/hooks.c

Purpose: registers BPF LSM hook trampolines for all LSM hooks and reserves inode security blob storage for BPF local storage.

Important APIs, types, and functions: defines `bpf_lsm_hooks[]`, `bpf_lsmid`, `bpf_lsm_init()`, `bpf_lsm_blob_sizes`, and `DEFINE_LSM(bpf)`. Macro expansion over `linux/lsm_hook_defs.h` maps every hook name to `bpf_lsm_<hook>()`; it also registers `inode_free_security` to `bpf_inode_storage_free()`.

Control flow: at LSM initialization, `bpf_lsm_init()` calls `security_add_hooks()` and logs activation. The LSM descriptor advertises blob sizes so inode security storage includes `struct bpf_storage_blob`.

State and persistence: persistent kernel state is the registered LSM hook list and allocated inode blob space. Per-inode BPF storage is cleaned on inode security free.

Dependencies and integration: depends on BPF LSM generated hook functions, LSM infrastructure, UAPI LSM IDs, and BPF local storage.

Risks and test signals: macro-generated all-hook registration can break if hook signatures or generated BPF hook names drift. Test signals include BPF LSM boot registration, BPF LSM program attachment/execution for representative hooks, and inode storage cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/bpf/hooks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/commoncap.c -->
# sources/distributed-fs/ceph-client/security/commoncap.c

Purpose: implements the common Linux capability LSM: namespace-aware capability checks, ptrace checks, capability set mutation, file capability xattr conversion, exec-time credential derivation, setuid/fsgid capability fixups, scheduler/nice/ioprio checks, prctl capability operations, low-mmap checks, and LSM registration.

Important APIs, types, and functions: major exports include `cap_capable()`, `cap_settime()`, `cap_ptrace_access_check()`, `cap_ptrace_traceme()`, `cap_capget()`, `cap_capset()`, `cap_inode_need_killpriv()`, `cap_inode_killpriv()`, `cap_inode_getsecurity()`, `cap_convert_nscap()`, `get_vfs_caps_from_disk()`, `cap_bprm_creds_from_file()`, `cap_inode_setxattr()`, `cap_inode_removexattr()`, `cap_task_fix_setuid()`, `cap_task_setscheduler()`, `cap_task_setioprio()`, `cap_task_setnice()`, `cap_task_prctl()`, `cap_vm_enough_memory()`, and `cap_mmap_addr()`. It registers `capability_hooks` with `DEFINE_LSM(capability)` at `LSM_ORDER_FIRST`.

Control flow: capability checks climb target user namespaces, accepting same-namespace effective caps or namespace owner privileges. File capability reads validate v1/v2/v3 xattr formats, map idmapped mounts and rootids, and convert v2/v3 data for callers. Exec handling clears/derives file capabilities, applies privileged-root compatibility, handles unsafe/no-new-privs downgrade, clears ambient caps on setid/fcap, computes permitted/effective sets, audits non-root effective gains, and sets secureexec. Prctl handling gates bounding set, securebits, keepcaps, and ambient operations.

State and persistence: mutates proposed or current credentials, file capability xattr values passed to VFS, task flags (`PF_SUPERPRIV`), and `bprm` secureexec/personality-clear fields. It can remove `security.capability` xattrs via killpriv.

Dependencies and integration: central LSM hooks, user namespaces, idmapped mounts, xattr/VFS, exec binprm, securebits, ptrace, audit, tracepoints, and memory management policy.

Risks and test signals: high-risk areas are user-namespace root mapping, idmapped mount conversion, ambient/permitted invariant preservation, setuid-root plus fcaps behavior, no-new-privs downgrade, and security xattr permission checks. KUnit coverage targets namespace-root helpers; broader tests should cover filecap xattr v2/v3 conversion, exec transitions, prctl securebits/ambient paths, ptrace, and low mmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/commoncap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/commoncap_test.c -->
# sources/distributed-fs/ceph-client/security/commoncap_test.c

Purpose: KUnit tests for namespace-root helper behavior in `commoncap.c`, included in the same compilation unit under `CONFIG_SECURITY_COMMONCAP_KUNIT_TEST` so static helpers can be exercised.

Important APIs, types, and functions: tests cover `vfsuid_root_in_currentns()` and `kuid_root_in_ns()`. `create_test_user_ns_with_mapping()` builds minimal mock user namespaces with custom uid/gid maps for test cases.

Control flow: cases construct `kuid_t`, `vfsuid_t`, and mock namespaces, then assert whether each helper recognizes UID 0 or mapped namespace root. Multi-namespace tests ensure different mapped root kuids are distinguished while init UID 0 remains root through parent traversal.

State and persistence: all namespace objects are KUnit allocations. No persistent kernel state is intended.

Dependencies and integration: depends on KUnit, user namespace map structures, refcount initialization, and static inclusion by `commoncap.c`.

Risks and test signals: mock namespaces are minimal and may miss invariants expected by full namespace code, but they directly test the mapping logic used by file capability visibility/conversion. Passing tests signal correct handling for invalid vfsuids, nonzero UIDs, init namespace root, and custom mapped roots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/commoncap_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/device_cgroup.c -->
# sources/distributed-fs/ceph-client/security/device_cgroup.c

Purpose: implements legacy device cgroup access control and bridges it with cgroup BPF device programs through `devcgroup_check_permission()`.

Important APIs, types, and functions: key types are `enum devcg_behavior`, `struct dev_exception_item`, and `struct dev_cgroup`. It defines cgroup subsystem callbacks `devcgroup_css_alloc()`, `devcgroup_css_free()`, `devcgroup_online()`, `devcgroup_offline()`, files `allow`, `deny`, `list`, and exported `devcgroup_check_permission()`. Internal rule helpers include `match_exception()`, `match_exception_partial()`, `verify_new_ex()`, `revalidate_active_exceptions()`, `propagate_exception()`, and `devcgroup_update_access()`.

Control flow: cgroups inherit parent behavior/exceptions at online time. Writes to `allow`/`deny` parse `a`, `b`, or `c` device rules with major/minor wildcards and access bits, require `CAP_SYS_ADMIN`, enforce parent constraints, update exception lists, and propagate new restrictions down the hierarchy. Permission checks first run BPF cgroup device programs, then legacy list checks under RCU if enabled.

State and persistence: per-cgroup state is `behavior` plus an RCU-protected exception list. Updates are serialized by `devcgroup_mutex`; frees use `kfree_rcu()`. User-visible state is the cgroup v1 devices control files.

Dependencies and integration: integrates with cgroup core, kernfs control files, BPF cgroup device hooks, RCU, capability checks, and device inode permission paths.

Risks and test signals: hierarchy propagation and default-allow/default-deny semantics are subtle. Parser edge cases around wildcards, access bits, and numeric overflow can change containment guarantees. Test signals include parent cannot grant unavailable access, deny propagation to descendants, BPF denial precedence, RCU-safe list reads, and cgroup list output compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/device_cgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/inode.c -->
# sources/distributed-fs/ceph-client/security/inode.c

Purpose: implements `securityfs`, the kernel pseudo-filesystem used by security modules, and exposes a read-only `lsm` file listing active LSM names when security support is enabled.

Important APIs, types, and functions: exported functions are `securityfs_create_file()`, `securityfs_create_dir()`, `securityfs_create_symlink()`, and `securityfs_remove()`. Internal filesystem functions include `securityfs_fill_super()`, `securityfs_get_tree()`, `securityfs_init_fs_context()`, `securityfs_create_dentry()`, `remove_one()`, `lsm_read()`, and `securityfs_init()`.

Control flow: creation pins the singleton filesystem if no parent is supplied, allocates an inode, starts simplefs dentry creation, initializes file/dir/symlink operations and private data, makes the dentry persistent, and returns it. Removal recursively removes a dentry subtree while managing the pin count. `securityfs_init()` creates `/sys/kernel/security`, registers the filesystem, and creates `lsm`.

State and persistence: global `mount` and `mount_count` track singleton mount pins. Created dentries/inodes persist until explicit `securityfs_remove()`. `lsm_read()` lazily builds and caches a comma-separated active LSM string.

Dependencies and integration: depends on simplefs helpers, sysfs mount point creation, VFS/fs_context APIs, LSM active ID list, and module-exported securityfs consumers such as AppArmor, IMA, EVM, and other LSMs.

Risks and test signals: callers must remove created entries; no automatic module cleanup exists. Symlink targets stored in `i_link` require correct free handling. Test signals include creating/removing root and nested entries, symlink cleanup, mount pin balancing, and correct `/sys/kernel/security/lsm` content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/Kconfig -->
# sources/distributed-fs/ceph-client/security/integrity/Kconfig

Purpose: defines configuration for the Linux integrity subsystem, including IMA, EVM, signature verification, asymmetric keys, trusted/platform/machine keyrings, platform key loading, and integrity audit.

Important APIs, types, and functions: Kconfig symbols include `INTEGRITY`, `INTEGRITY_SIGNATURE`, `INTEGRITY_ASYMMETRIC_KEYS`, `INTEGRITY_TRUSTED_KEYRING`, `INTEGRITY_PLATFORM_KEYRING`, `INTEGRITY_MACHINE_KEYRING`, `INTEGRITY_CA_MACHINE_KEYRING`, `INTEGRITY_CA_MACHINE_KEYRING_MAX`, `LOAD_UEFI_KEYS`, `LOAD_IPL_KEYS`, `LOAD_PPC_KEYS`, and `INTEGRITY_AUDIT`. It sources `ima/Kconfig` and `evm/Kconfig`.

Control flow: config dependencies/selects determine which keyrings, parsers, crypto algorithms, platform loaders, and audit support are compiled. `INTEGRITY` gates the whole subtree.

State and persistence: no runtime state directly; it controls compiled-in runtime state such as keyrings and LSM components.

Dependencies and integration: integrates with `SECURITY`, `KEYS`, `SIGNATURE`, asymmetric key infrastructure, system trusted/blacklist/secondary keyrings, EFI/S390/PPC platform support, and audit.

Risks and test signals: dependency errors can produce missing verification paths or overly broad trust. Test signals are config matrix builds for IMA/EVM/signature/keyring combinations and boot-time keyring availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/Makefile -->
# sources/distributed-fs/ceph-client/security/integrity/Makefile

Purpose: composes integrity subsystem objects based on Kconfig and establishes the relative build order of IMA and EVM.

Important APIs, types, and functions: builds `integrity.o` from `iint.o` plus conditional objects: `integrity_audit.o`, `digsig.o`, `digsig_asymmetric.o`, platform/machine keyring loaders, EFI/S390/PPC platform certificate handlers, and `efi_secureboot.o`. It descends into `ima/` and `evm/`.

Control flow: Kbuild appends objects according to `CONFIG_*` symbols. The comment notes IMA/EVM LSM relative order depends on the listed order.

State and persistence: no runtime state directly.

Dependencies and integration: tied to Kconfig symbols from integrity, platform certs, IMA, EVM, and EFI.

Risks and test signals: build order can affect LSM ordering and therefore integrity behavior. Test signals are successful builds across config matrices and expected object inclusion/exclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/digsig.c -->
# sources/distributed-fs/ceph-client/security/integrity/digsig.c

Purpose: manages integrity keyrings and dispatches IMA/EVM/module digital signature verification.

Important APIs, types, and functions: static state includes `keyring[INTEGRITY_KEYRING_MAX]` and `keyring_name[]`. Public functions are `integrity_digsig_verify()`, `integrity_modsig_verify()`, `integrity_init_keyring()`, `integrity_load_x509()`, and `integrity_load_cert()`. Internal helpers are `integrity_keyring_from_id()`, `__integrity_init_keyring()`, and `integrity_add_key()`.

Control flow: verification resolves a keyring ID, examines signature version byte, and dispatches to legacy `digsig_verify()`, `asymmetric_verify()`, or `asymmetric_verify_v3()`. Keyring initialization chooses permissions/restrictions based on keyring type and trusted keyring config, sets platform/machine trust hooks, and may load module certs. Certificate loading reads DER files or accepts built-in buffers and inserts asymmetric keys.

State and persistence: keyring pointers persist globally. Loaded certificates persist in kernel keyrings. Keyring restrictions may prevent later user key insertion.

Dependencies and integration: integrates with key retention service, system trusted keyrings, IMA module signatures, platform/machine trusted key setup, kernel file reading, and asymmetric signature code.

Risks and test signals: wrong keyring restrictions can admit untrusted keys or block boot-time trust anchors. Signature version dispatch must reject short/unknown formats. Test signals include keyring allocation, trusted restriction enforcement, v1/v2/v3 signature verification, module signature verification, X.509 load success/failure, and blacklist interactions through asymmetric code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/digsig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/digsig_asymmetric.c -->
# sources/distributed-fs/ceph-client/security/integrity/digsig_asymmetric.c

Purpose: verifies integrity signatures using asymmetric keys and supports IMA/EVM signature version 3 by hashing file-identity metadata before verification.

Important APIs, types, and functions: public functions are `asymmetric_verify()` and `asymmetric_verify_v3()`. Internal helpers are `request_asymmetric_key()` and `calc_file_id_hash()`. It uses `struct signature_v2_hdr`, `struct public_key_signature`, `struct ima_file_id`, and `struct ima_max_digest_data`.

Control flow: key lookup first checks the IMA blacklist keyring for the key ID, then searches a specific keyring or global asymmetric keys. `asymmetric_verify()` validates signature length, hash algorithm, key ID, public key algorithm, selects encoding (`pkcs1`, `x962`, or `raw`), and calls `verify_signature()`. v3 verification hashes the typed file ID structure and verifies that derived digest.

State and persistence: no persistent state; it acquires and releases key references.

Dependencies and integration: depends on asymmetric key type, public key crypto, hash algorithm tables, IMA blacklist keyring, and integrity xattr signature formats.

Risks and test signals: key lookup errors are intentionally normalized for some cases, while blacklisted keys must reject. Algorithm/encoding selection must match key type. Test signals include unknown key, blacklisted key, unsupported hash/pkey algorithm, malformed signature size, valid RSA/ECDSA/ECRDSA signatures, and v3 hash type validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/digsig_asymmetric.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/efi_secureboot.c -->
# sources/distributed-fs/ceph-client/security/integrity/efi_secureboot.c

Purpose: exposes architecture secure-boot status to the integrity subsystem by querying EFI secure boot mode safely after EFI runtime support is available.

Important APIs, types, and functions: key functions are `get_sb_mode()` and `arch_get_secureboot()`. It uses `arch_efi_boot_mode` when provided, `efi_get_secureboot_mode()`, `efi_rt_services_supported()`, and `efi_enabled(EFI_BOOT)`.

Control flow: `arch_get_secureboot()` lazily initializes static state once. If EFI boot is active, it uses an architecture-provided mode or queries EFI variables; it returns true only for `efi_secureboot_mode_enabled`.

State and persistence: caches `sb_mode` and `initialized` statically for subsequent calls. It logs mode status.

Dependencies and integration: integrates with EFI runtime services, architecture EFI hooks, and integrity policy decisions that depend on secure boot.

Risks and test signals: calling too early can hang, which the comment explicitly warns against. Test signals include EFI-disabled, runtime-variable unsupported, arch-provided enabled/disabled, and queried enabled/disabled/unknown modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/efi_secureboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/evm/Kconfig -->
# sources/distributed-fs/ceph-client/security/integrity/evm/Kconfig

Purpose: defines Extended Verification Module configuration for protecting file security xattrs with HMACs or signatures.

Important APIs, types, and functions: symbols include `EVM`, `EVM_ATTR_FSUUID`, `EVM_EXTRA_SMACK_XATTRS`, `EVM_ADD_XATTRS`, `EVM_LOAD_X509`, and `EVM_X509_PATH`.

Control flow: enabling `EVM` selects key, encrypted-key, HMAC, SHA1, hash-info, and security path dependencies. Optional symbols alter HMAC material, allow runtime protected-xattr extension, and load an X.509 cert into `.evm`.

State and persistence: no direct runtime state, but options affect persistent EVM labels: changing FSUUID or extra xattr participation requires relabeling existing filesystems.

Dependencies and integration: integrates with integrity keyrings, encrypted keys, crypto, security xattrs, Smack, and securityfs.

Risks and test signals: HMAC input changes are backward-incompatible with existing labels. Test signals are config builds and EVM validation across FSUUID, Smack extra xattrs, runtime xattr list, and X.509 load configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/evm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/evm/Makefile -->
# sources/distributed-fs/ceph-client/security/integrity/evm/Makefile

Purpose: builds the EVM object from core, crypto, securityfs, and optional POSIX ACL support.

Important APIs, types, and functions: Kbuild rules create `evm.o` from `evm_main.o`, `evm_crypto.o`, `evm_secfs.o`, and conditionally `evm_posix_acl.o`.

Control flow: object inclusion is controlled by `CONFIG_EVM` and `CONFIG_FS_POSIX_ACL`.

State and persistence: no runtime state directly.

Dependencies and integration: ties EVM build output into the integrity Makefile and optional ACL xattr handling.

Risks and test signals: missing optional ACL object can alter protected metadata coverage when POSIX ACLs are configured. Test signals are build inclusion and EVM ACL behavior under `CONFIG_FS_POSIX_ACL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/evm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/evm/evm.h -->
# sources/distributed-fs/ceph-client/security/integrity/evm/evm.h

Purpose: internal EVM header defining initialization flags, inode-cache metadata, protected xattr list entries, digest layout, globals, and crypto/securityfs function prototypes.

Important APIs, types, and functions: defines `EVM_INIT_HMAC`, `EVM_INIT_X509`, `EVM_ALLOW_METADATA_WRITES`, `EVM_SIGV3_REQUIRED`, `EVM_SETUP_COMPLETE`, `EVM_KEY_MASK`, `EVM_INIT_MASK`, `struct xattr_list`, `struct evm_iint_cache`, `struct evm_digest`, `evm_iint_inode()`, and prototypes for `evm_protected_xattr()`, `evm_init_key()`, `evm_update_evmxattr()`, `evm_calc_hmac()`, `evm_calc_hash()`, `evm_init_hmac()`, and `evm_init_secfs()`.

Control flow: the inline `evm_iint_inode()` returns the EVM portion of an inode security blob using `evm_blob_sizes.lbs_inode`, or NULL when no security blob exists.

State and persistence: declares global initialization state, HMAC attributes, and configured protected xattr names. `evm_iint_cache` stores per-inode EVM status and metadata attributes.

Dependencies and integration: included by EVM implementation files and depends on the integrity header, LSM blob sizing, inode security blobs, and xattr APIs.

Risks and test signals: blob offset correctness is critical because the inline pointer arithmetic assumes LSM blob layout. Test signals include inode blob allocation with EVM enabled, EVM status caching, and protected xattr list behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/evm/evm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/evm/evm_crypto.c -->
# sources/distributed-fs/ceph-client/security/integrity/evm/evm_crypto.c

Purpose: calculates and updates EVM HMAC/hash values over protected security xattrs plus inode metadata, initializes the EVM HMAC key, and manages crypto hash transforms.

Important APIs, types, and functions: public functions are `evm_set_key()`, `evm_calc_hmac()`, `evm_calc_hash()`, `evm_update_evmxattr()`, `evm_init_hmac()`, and `evm_init_key()`. Internal helpers include `init_desc()`, `hmac_add_misc()`, `dump_security_xattr*()`, `evm_calc_hmac_or_hash()`, and `evm_is_immutable()`. Static state includes `evmkey`, `hmac_tfm`, `evm_tfm[]`, `mutex`, and `evm_set_key_flags`.

Control flow: `init_desc()` selects HMAC or hash algorithm, lazily allocates a crypto shash transform, sets the HMAC key when needed, and returns an initialized descriptor. `evm_calc_hmac_or_hash()` iterates configured protected xattrs, uses the requested xattr value when supplied, fetches other xattrs from VFS, feeds all values into the hash, adds inode metadata and optionally FS UUID, then finalizes. Portable signatures require an IMA xattr. `evm_update_evmxattr()` rejects immutable portable signatures, computes a SHA1 HMAC, writes `security.evm`, or removes it when no data remains. `evm_init_key()` requests the encrypted `evm-key`, passes decrypted data to `evm_set_key()`, and zeroes the original decrypted payload.

State and persistence: stores global HMAC key bytes and initialized crypto transforms. Persists calculated HMACs by setting/removing `security.evm` xattrs. Updates per-inode metadata cache for overlay/metadata inode cases. Key initialization sets `evm_initialized`.

Dependencies and integration: depends on encrypted keys, crypto shash API, EVM config xattr list, VFS xattr APIs, inode metadata, init user namespace UID/GID encoding, and EVM main/status code.

Risks and test signals: key length handling copies shorter keys but always sets a 128-byte HMAC key length, making zero padding part of the key material. HMAC input ordering and metadata encoding are compatibility-critical; changing FSUUID or protected xattrs requires relabeling. Test signals include missing key, immutable signature rejection, portable signature without IMA hash, xattr update/removal, overlay metadata cache behavior, and encrypted-key zeroization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/evm/evm_crypto.c -->
