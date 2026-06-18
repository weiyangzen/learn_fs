# subset-b-006336 AppArmor research

This grouped report covers the requested AppArmor kernel security module files under `sources/distributed-fs/ceph-client/security/apparmor`. Each source file has a marker-delimited section for reconciliation into its source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/Kconfig -->
# sources/distributed-fs/ceph-client/security/apparmor/Kconfig

## Purpose
This Kconfig file controls whether the AppArmor Linux Security Module is built and which optional policy introspection, hashing, raw binary export, paranoid policy-load verification, debug, and KUnit test features are compiled. It is the top-level build-time contract that determines which code paths in this directory are present, especially `crypto.c` and raw policy export support in `apparmorfs.c`.

## Important symbols
- `SECURITY_APPARMOR` depends on `SECURITY` and `NET`, selects `AUDIT`, `SECURITY_PATH`, `SECURITYFS`, and `SECURITY_NETWORK`, and gates the main `apparmor.o` object.
- `SECURITY_APPARMOR_DEBUG`, `SECURITY_APPARMOR_DEBUG_ASSERTS`, and `SECURITY_APPARMOR_DEBUG_MESSAGES` control assertion and diagnostic behavior around `AA_BUG`, `AA_DEBUG`, and the `apparmor.debug` boot/module parameter.
- `SECURITY_APPARMOR_INTROSPECT_POLICY` enables policy introspection through apparmorfs and is a prerequisite for hash and export features.
- `SECURITY_APPARMOR_HASH` selects `CRYPTO_LIB_SHA256` and compiles hash support used by `crypto.c` and hash files in apparmorfs.
- `SECURITY_APPARMOR_EXPORT_BINARY` selects zstd compression/decompression and enables raw binary policy export and related apparmorfs symlinks/files.
- `SECURITY_APPARMOR_PARANOID_LOAD` defaults to full policy verification during load.
- `SECURITY_APPARMOR_KUNIT_TEST` builds the policy unpack KUnit test object.

## Control flow and integration
The options flow into `Makefile` object selection and into `#ifdef CONFIG_SECURITY_APPARMOR_HASH` / `#ifdef CONFIG_SECURITY_APPARMOR_EXPORT_BINARY` conditionals. Enabling AppArmor also requires securityfs and path/network LSM hooks, matching the code's reliance on `/sys/kernel/security/apparmor`, path names, sockets, and kernel audit.

## State and persistence
Kconfig choices are persisted in the kernel build configuration. Runtime state such as loaded profiles, namespace revisions, profile hashes, and raw policy data only exists if the corresponding features are compiled and then enabled at runtime through globals such as `aa_g_hash_policy` and `aa_g_export_binary`.

## Dependencies
The file depends on kernel security, networking, audit, securityfs, crypto SHA-256, zstd, and KUnit subsystems. A mismatch between selected options and code expectations changes exported apparmorfs features and can affect userspace tooling compatibility.

## Risks
Disabling paranoid load verification or policy hashing/export can improve memory or load-time behavior but reduces diagnosability and integrity checking. Introspection and raw export increase memory use because policy data and hashes may be retained. Debug asserts can expose latent kernel warnings in production-like environments if enabled.

## Test signals
Build matrices should cover `SECURITY_APPARMOR=y`, hash on/off, export binary on/off, paranoid load on/off, and `SECURITY_APPARMOR_KUNIT_TEST`. Runtime smoke tests should check expected feature files in securityfs and that policy load/replace/remove behavior matches compiled options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/Makefile -->
# sources/distributed-fs/ceph-client/security/apparmor/Makefile

## Purpose
This Makefile assembles the AppArmor LSM object, conditionally includes hash support, builds the KUnit policy-unpack test, and generates compile-time name tables for capabilities, rlimits, and network families/types. It is the concrete build graph for the AppArmor directory.

## Important build targets
- `obj-$(CONFIG_SECURITY_APPARMOR) += apparmor.o` creates the main linked AppArmor object.
- `apparmor-y` lists core components: apparmorfs, audit, capability, task, ipc, lib, match, path, domain, policy, policy_unpack, procattr, lsm, resource, secid, file, policy_ns, label, mount, net, policy_compat, and af_unix.
- `apparmor-$(CONFIG_SECURITY_APPARMOR_HASH) += crypto.o` adds SHA-256 policy hashing.
- `obj-$(CONFIG_SECURITY_APPARMOR_KUNIT_TEST)` builds `apparmor_policy_unpack_test.o` from `policy_unpack_test.o`.
- Generated headers are `capability_names.h`, `rlim_names.h`, and `net_names.h`.

## Control flow and generated data
The sed pipelines transform UAPI/kernel definitions into lowercase string arrays and securityfs feature masks. Capability names feed `capability.c` audit output and `AA_SFS_CAPS_MASK`; rlimit names feed resource policy output and `AA_SFS_RLIMIT_MASK`; network family/type names feed network policy feature reporting.

## State and persistence
Generated headers are build artifacts, not source state. They are marked in `clean-files`, so normal kernel clean targets remove them. The generated names become compiled-in read-only lookup tables used by audit and apparmorfs feature reporting.

## Dependencies
The generation rules depend on `include/uapi/linux/capability.h`, `include/uapi/asm-generic/resource.h`, `include/linux/socket.h`, and `include/linux/net.h`. They also depend on GNU sed behavior including extended regex and lowercase conversion.

## Risks
Regex drift against upstream header formatting can silently omit names or masks. The network generator intentionally excludes `AF_MAX`, `AF_LOCAL`, and `AF_ROUTE`, so compatibility assumptions must be explicit. Build failures or stale generated headers would directly affect audit readability and userspace feature discovery.

## Test signals
Build with AppArmor enabled and confirm generated headers appear before dependent objects compile. Inspect generated masks for expected capabilities, rlimits, families, and socket types. KUnit builds should include only `policy_unpack_test.o` through the declared test object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/af_unix.c -->
# sources/distributed-fs/ceph-client/security/apparmor/af_unix.c

## Purpose
`af_unix.c` implements fine-grained AppArmor mediation for Unix domain sockets. It handles create, bind, listen, accept, socket option, peer, and file-backed socket revalidation paths, bridging between AppArmor network policy and ordinary path/file mediation for filesystem-backed sockets.

## Important APIs and functions
- `aa_unix_create_perm`, `aa_unix_bind_perm`, `aa_unix_listen_perm`, `aa_unix_accept_perm`, `aa_unix_sock_perm`, `aa_unix_opt_perm`, `aa_unix_peer_perm`, and `aa_unix_file_perm` are the LSM-facing entry points.
- `aa_sunaddr` safely reads `unix_sock->addr` with `smp_load_acquire`.
- `match_to_local`, `match_to_sk`, `match_to_cmd`, `match_to_peer`, and `match_label` walk v9 network DFA states through protocol, address, command selector, peer address, and peer label checks.
- `unix_fs_perm` delegates filesystem-backed socket checks to `aa_path_perm` using inode owner/mode conditions.
- `update_sk_ctx` and `update_peer_ctx` update per-socket cached label/peer contexts.

## Control flow
Create/listen/accept/option/bind operations enter through small public wrappers that capture the current label with `begin_current_label_crit_section`, build audit data, and iterate confined profiles. For v9 network policy, abstract or anonymous sockets are matched in the network DFA; filesystem sockets are usually checked as paths. If v9 is not mediated, the code falls back to older address-family socket mediation via `aa_profile_af_perm` or `aa_profile_af_sk_perm`.

Peer operations are stricter. `aa_unix_peer_perm` requires both socket locks to be held and compares the local socket, peer address/path, and peer label. `aa_unix_file_perm` revalidates open Unix socket files when peer labels or cached labels changed; for non-filesystem sockets it cross-checks both directions with `xcheck`, then updates peer caches after success.

## State and persistence
The file updates per-socket `aa_sk_ctx` fields: current socket label, peer label, and `peer_lastupdate`. These are RCU-protected labels mutated under the Unix socket lock. No persistent disk state is written, but successful checks influence later fast-path decisions through cached labels.

## Dependencies and integration
It depends on Unix socket internals, AppArmor labels, path mediation, net mediation, file permission masks, audit helpers, and policy DFA helpers. Filesystem socket handling intentionally integrates with `file.c` and path rules so Unix socket paths are governed like filesystem objects when appropriate.

## Risks
The code is sensitive to socket lifetime, lock ordering, and RCU label access. Address matching uses special in-band bytes for anonymous, abstract, disconnected, and shutdown addresses; policy compiler/runtime mismatches could misclassify endpoints. The comments note incomplete local label matching and implicit delegation for shutdown/deleted filesystem sockets. Cache update races are handled conservatively, but stale peer information can cause extra revalidation.

## Test signals
Exercise abstract, anonymous, autobind, and filesystem Unix sockets across stream and datagram modes. Test bind/listen/accept, peer send/connect checks, socket option mediation, inherited/open socket revalidation after profile replacement, and filesystem socket fallback to path permissions. Audit records should include operation, class, peer label or path, address failures, and correct allowed/denied outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/af_unix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/apparmorfs.c -->
# sources/distributed-fs/ceph-client/security/apparmor/apparmorfs.c

## Purpose
`apparmorfs.c` implements AppArmor's user-visible filesystem interfaces: securityfs entries under `/sys/kernel/security/apparmor`, a private single-superblock apparmorfs policy tree, policy load/replace/remove files, policy query transactions, profile/namespace introspection, namespace revision polling, and optional raw binary policy export.

## Important APIs and functions
- Filesystem setup and teardown: `aa_create_aafs`, `aa_destroy_aafs`, `apparmorfs_fill_super`, `aafs_create`, `aafs_remove`, and `aa_mk_null_file`.
- Policy writes: `profile_load`, `profile_replace`, `profile_remove`, and shared `policy_update`.
- Namespace/profile tree maintenance: `__aafs_ns_mkdir`, `__aafs_ns_rmdir`, `__aafs_profile_mkdir`, `__aafs_profile_rmdir`, and `__aafs_profile_migrate_dents`.
- Revision signaling: `__aa_bump_ns_revision`, `ns_revision_read`, `ns_revision_poll`.
- Query support: `aa_write_access`, `query_label`, `query_data`, and the `multi_transaction` buffer helpers.
- Raw export, under `CONFIG_SECURITY_APPARMOR_EXPORT_BINARY`: `__aa_fs_create_rawdata`, `__aa_fs_remove_rawdata`, `rawdata_open`, and zstd decompression helpers.

## Control flow
At initialization, `aa_create_aafs` mounts private apparmorfs, creates static securityfs feature files, root `.load/.replace/.remove/revision` files, builds the root policy tree under `.policy`, and exposes a magic `policy` symlink that redirects readers to the current task's policy namespace. Policy write handlers first check `aa_may_manage_policy`, copy complete user writes from offset zero into `aa_loaddata`, and call `aa_replace_profiles` or `aa_remove_profiles`.

The dynamic policy tree mirrors namespaces and profiles with dentries whose inode-private data stores refcounted namespaces, proxies, or raw load data. Namespace directories contain profiles, raw_data, revision, policy-management files, and subnamespace directories. Profile directories expose name, mode, attach string, optional hash, and optional raw data symlinks.

## State and persistence
The visible filesystem is generated kernel state, not persistent storage. It pins dentries and references through `aa_common_ref` and apparmorfs mount counts. Namespace revisions are long counters with wait queues; raw policy data is retained in `aa_loaddata` when export is enabled and linked into `ns->rawdata_list`. The `.null` character device path is stored in global `aa_null` and used when unauthorized inherited files are replaced.

## Dependencies and integration
The file integrates with securityfs, VFS simple filesystem helpers, zstd, policy unpack/load code, policy namespaces, labels/proxies, audit permission checks, resource/cap/net feature tables, and the current task label/namespace helpers. Userspace tools rely on its feature directories and transaction formats for policy discovery and queries.

## Risks
This code has a large VFS and lifetime surface. Inode-private references must match dentry removal and inode eviction exactly. Namespace lock ordering is delicate, especially where inode locks are dropped before namespace operations. Raw policy export can consume memory and requires correct decompression bounds. Query parsing accepts binary strings with embedded NULs, so off-by-one mistakes would be security relevant. Feature reporting is a userspace ABI and changes can break parsers.

## Test signals
Boot with AppArmor enabled and verify securityfs entries, feature files, `.load/.replace/.remove`, `revision`, `profiles`, and `policy` symlink behavior. Load, replace, and remove policies across namespaces and confirm revision polling wakes. Test `.access` label/profile/labelall/data transactions including malformed NUL layouts and oversized writes. With raw export enabled, verify raw_data metadata, hash, compressed size, raw decompression, and profile symlinks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/apparmorfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/audit.c -->
# sources/distributed-fs/ceph-client/security/apparmor/audit.c

## Purpose
`audit.c` centralizes AppArmor audit event formatting, audit-mode decision logic, kill/complain behavior, and audit rule integration. It converts AppArmor-specific `apparmor_audit_data` into Linux audit records via `common_lsm_audit`.

## Important APIs and functions
- `audit_mode_names`, `aa_audit_type`, and `aa_class_names` provide stable string representations.
- `audit_pre` emits common fields: AppArmor audit type, operation, class, info/error, profile/label, namespace, and object name.
- `aa_audit_msg` sends an event with an explicit type.
- `aa_audit` maps `AUDIT_APPARMOR_AUTO` into audit, allowed, denied, or kill based on profile mode and error status.
- `aa_audit_rule_init`, `aa_audit_rule_known`, `aa_audit_rule_match`, and `aa_audit_rule_free` integrate AppArmor labels with kernel audit rules.

## Control flow
Callers populate `apparmor_audit_data` and optional type-specific callback. `aa_audit` suppresses successful events unless `AUDIT_ALL` or explicit audit bits require logging, maps complain-mode denials to `ALLOWED`, suppresses quiet modes, converts kill-mode denials to `KILL`, fills `ad->subj_label`, and invokes `aa_audit_msg`. Kill events send the configured signal to the audited task/current task.

## State and persistence
No durable state is stored. The audit rule helper allocates and retains a parsed `aa_label` in an `aa_audit_rule` object until audit frees it. Audit output enters the kernel audit subsystem and system logs according to external audit configuration.

## Dependencies and integration
The file depends on Linux audit, AppArmor label printing/parsing, profile namespaces, secid/LSM properties, and profile mode macros from policy code. It is called from file, capability, network, domain, mount, IPC, and policy-management mediation paths.

## Risks
Audit suppression can hide expected diagnostics when quiet modes or quiet permission bits apply. Class-name tables must remain aligned with `AA_CLASS_*` constants. Audit rule parsing currently treats rules as root-namespace labels, which can surprise namespaced policy users. Kill-mode side effects must only occur for true `AUDIT_APPARMOR_KILL` records.

## Test signals
Check enforce, complain, kill, quiet, quiet_denied, noquiet, and audit_all modes. Verify audit records contain namespace/profile/label formatting for single and stacked labels. Test audit rules with `AUDIT_SUBJ_ROLE` equality and inequality against AppArmor labels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/audit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/capability.c -->
# sources/distributed-fs/ceph-client/security/apparmor/capability.c

## Purpose
`capability.c` mediates Linux capability checks under AppArmor policy, exposes capability feature metadata, deduplicates noisy capability audit records, and computes the visible capability set for a profile.

## Important APIs and functions
- `aa_sfs_entry_caps` reports capability mask and extended capability support in apparmorfs features.
- `audit_cb` prints `capname` using the generated `capability_names.h` table.
- `audit_caps` handles legacy capability audit mode, quiet/kill bits, complain mode, and one-second per-CPU duplicate suppression.
- `profile_capable` performs the per-profile capability decision using either DFA-based `AA_CLASS_CAP` permissions or legacy `aa_caps` bitsets.
- `aa_capable` iterates confined profiles in a label for LSM capability checks.
- `aa_profile_capget` returns the capability set visible to capability-get style queries.

## Control flow
The public `aa_capable` initializes audit data and checks each confined profile. `profile_capable` first tries the new policydb class path; capabilities are split into 32-bit chunks selected by `cap >> 5`, with the request bit derived from `cap & 0x1f`. If no DFA class mediates capabilities, it falls back to legacy allow/denied/audit/quiet/kill masks.

## State and persistence
The file uses per-CPU `audit_cache` entries keyed by subject cred and capability number with a one-second expiration. It holds a cred reference while cached. Profile capability rules are loaded policy state in `aa_ruleset`.

## Dependencies and integration
It depends on generated capability names, Linux capability constants, timekeeping, AppArmor audit, policydb permissions, profile modes, and label iteration. LSM hooks call `aa_capable` through AppArmor's main LSM integration.

## Risks
Duplicate audit suppression trades visibility for log noise reduction and must correctly release cached credentials. Capability chunk math must match policy compiler encoding. The loop in `aa_profile_capget` is sensitive to `CAP_LAST_CAP` coverage and permission bit shifting, so changes in kernel capability count should be tested.

## Test signals
Test allowed, denied, audited, quiet, kill, and `CAP_OPT_NOAUDIT` cases under both DFA and legacy policy. Verify duplicate audit suppression over repeated checks and expiration after one second. Confirm apparmorfs feature `caps/mask` matches generated capability names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/capability.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/crypto.c -->
# sources/distributed-fs/ceph-client/security/apparmor/crypto.c

## Purpose
`crypto.c` implements optional SHA-256 hashing for loaded AppArmor policy blobs and profiles. The hashes support userspace introspection and integrity comparison between compiled userspace policy and kernel-loaded policy.

## Important APIs and functions
- `aa_hash_size` returns `SHA256_DIGEST_SIZE`.
- `aa_calc_hash` allocates a digest buffer and hashes arbitrary data.
- `aa_calc_profile_hash` hashes the little-endian policy version followed by profile data into `profile->hash`, honoring the runtime `aa_g_hash_policy` switch.
- `init_profile_hash` logs that hashing is enabled after AppArmor initialization.

## Control flow
Policy load code calls `aa_calc_profile_hash` when hash support is compiled. If runtime hashing is disabled, the function returns success without allocating or writing a hash. Otherwise it allocates profile hash storage, initializes a SHA-256 context, includes the policy ABI version in little-endian form, hashes the raw profile byte range, and finalizes into the profile.

## State and persistence
The persistent kernel state is the allocated `profile->hash` field and optional `aa_loaddata->hash` elsewhere. Hashes are exposed through apparmorfs profile and raw_data files but are not written to disk by this code.

## Dependencies and integration
The file depends on `CONFIG_SECURITY_APPARMOR_HASH`, `CRYPTO_LIB_SHA256`, `aa_g_hash_policy`, and AppArmor profile allocation/lifetime. The header provides stubs when the feature is disabled, so callers can be compiled unconditionally.

## Risks
Hash allocation failures fail profile hash computation and can affect policy load behavior depending on caller handling. Runtime toggling of `aa_g_hash_policy` means profiles loaded under different settings may or may not expose hashes. Hashing version plus bytes requires userspace to use the same ABI framing for comparisons.

## Test signals
Build with hash enabled and disabled. With hashing enabled at runtime, load policy and verify apparmorfs `sha256` files are populated and stable for identical input. With runtime hashing disabled, verify load succeeds and hash files are absent or empty as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/domain.c -->
# sources/distributed-fs/ceph-client/security/apparmor/domain.c

## Purpose
`domain.c` implements AppArmor profile attachment and domain transitions: exec transitions, x-table lookups, unconfined attachment, xattr-conditioned attachments, `change_hat`, `change_profile`, `change_onexec`, stacking, ptrace/no_new_privs restrictions, and learning-profile creation in complain mode.

## Important APIs and functions
- Public entry points: `apparmor_bprm_creds_for_exec`, `aa_change_hat`, `aa_change_profile`, and `x_table_lookup`.
- Transition helpers: `profile_transition`, `x_to_label`, `find_attach`, `aa_xattrs_match`, `profile_onexec`, and `handle_onexec`.
- Label matching helpers: `label_compound_match`, `label_components_match`, `label_match`, and `change_profile_perms`.
- Hat helpers: `change_hat` and `build_change_hat`.
- Safety checks: `may_change_ptraced_domain`, no_new_privs subset checks, and secureexec/personality handling.

## Control flow
Exec starts in `apparmor_bprm_creds_for_exec`. It captures the current/newest label, records the label under which no_new_privs began, builds path conditions from executable inode owner/mode, and either processes a pending onexec transition or computes a profile transition for each component of a stacked label. `profile_transition` resolves the executable path, matches file permissions, decodes the exec transition index, finds/creates the target label, audits, and sets secureexec for safe transitions.

Attachment search prefers exact or most-specific xmatch path matches, then considers xattrs; equal specificity and equal xattr count are conflicts. `aa_change_hat` selects hats across the current namespace, supports token-based restore, and kills on brute-force token mismatch. `aa_change_profile` parses target labels, checks change permissions, optionally stores an onexec target, or immediately replaces/merges the current label.

## State and persistence
The file mutates task AppArmor context fields: current credential label, previous hat label, onexec target, change_hat token, and no_new_privs baseline label. It also creates null learning profiles in complain mode and uses policy namespace/profile lists. Exec transition results persist in the new credentials.

## Dependencies and integration
It depends on Linux binprm, ptrace, xattrs, credentials, path naming, labels, file permissions, policy namespaces, audit, task context, and IPC ptrace mediation. It is tightly integrated with policy unpack encoding through `xindex` flags and transition tables.

## Risks
This is a high-risk security boundary. Path lookup failures, xattr matching, conflict fallbacks, and unconfined attachment rules determine whether tasks become confined, remain in-profile, or become unconfined. no_new_privs subset checks must be correct for stacked labels. Ptrace restrictions must use the right tracer credentials and target label. Complain-mode null profile creation changes runtime policy shape and must not leak into enforce behavior.

## Test signals
Test exec transitions for ix/px/cx/nx/ux-style cases, named transition tables, child transitions, stacking targets, missing targets, conflict fallback, and xattr-conditioned attachment. Exercise no_new_privs, ptraced exec, secureexec, personality clearing, change_hat enter/restore/token mismatch, change_profile immediate/onexec/test modes, and unprivileged unconfined stacking restrictions. Audit output should explain fallback/conflict/missing-profile causes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/domain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/file.c -->
# sources/distributed-fs/ceph-client/security/apparmor/file.c

## Purpose
`file.c` implements AppArmor file and open-file mediation: path permission checks, hardlink pair checks, audit formatting for file permissions, conditional owner permissions, per-file context caching, Unix/socket file revalidation, and inherited-file cleanup after domain transitions.

## Important APIs and functions
- `aa_audit_file` emits file-specific audit records.
- `aa_lookup_condperms` and `aa_str_perms` translate DFA states into conditional `aa_perms`.
- `aa_path_perm` and `__aa_path_perm` mediate named paths.
- `aa_path_link` and `profile_path_link` mediate hardlinks and subset constraints.
- `aa_file_perm` revalidates already-open files using `aa_file_ctx`.
- `aa_inherit_files` revalidates inherited descriptors and replaces unauthorized ones with `aa_null`.

## Control flow
Path checks resolve a path name with profile path flags, build a `path_cond` from inode owner/mode, match the file policy DFA, apply permissions, audit, and return errors. Link checks first match the link name, then transition through a NUL-separated pair to match the target; optional subset checks ensure permissions on the link do not exceed target permissions and exec xindex flags are compatible.

Open-file revalidation first checks cached `file_ctx` label and allowed mask under RCU. If the subject label is already cached and requested permissions are covered, the fast path returns. Otherwise it obtains the newest cached file label and revalidates either path-mediated files or sockets, updating `file_ctx` on success. Inherited descriptors are scanned with `iterate_fd`; unauthorized files are replaced with the apparmorfs `.null` device.

## State and persistence
Each `struct file` carries AppArmor blob state `aa_file_ctx` with a spinlock, cached label, and allowed permission mask. The file also relies on global `aa_null` created by apparmorfs. No disk state is written, but cached permissions persist for the lifetime of open file objects.

## Dependencies and integration
The file depends on path naming, policy DFA matching, audit, labels, network/socket mediation, AF_UNIX revalidation, VFS file modes, and kernel fd/tty APIs. Domain transition code calls `aa_inherit_files` to enforce new labels against existing descriptors.

## Risks
Comments explicitly note no revocation on stale profiles and incomplete cached full-permission tracking, so policy replacement may not revoke already-open access immediately. Hardlink subset logic is security sensitive. Deleted/disconnected path handling depends on path flags. In atomic contexts, buffer allocation failures can deny access.

## Test signals
Test read/write/append/create/truncate/open/getattr/setattr/chmod/chown/lock/mmap_exec path permissions; owner conditional rules; hardlink pair and subset failures; profile replacement with open files; inherited fd replacement with `.null`; controlling TTY drop; and socket file revalidation including Unix peer changes. Audit masks should match requested and denied permissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/af_unix.h -->
# sources/distributed-fs/ceph-client/security/apparmor/include/af_unix.h

## Purpose
This header declares the AF_UNIX AppArmor mediation API and small classification macros for Unix socket addresses and socket state. It connects LSM socket hooks and file revalidation code to `af_unix.c`.

## Important APIs and types
The header declares `aa_sunaddr`, `aa_unix_create_perm`, `aa_unix_bind_perm`, `aa_unix_connect_perm`, `aa_unix_listen_perm`, `aa_unix_accept_perm`, `aa_unix_msg_perm`, `aa_unix_opt_perm`, `aa_unix_sock_perm`, `aa_unix_peer_perm`, and `aa_unix_file_perm`. Macros classify abstract, anonymous, filesystem-backed, connected, and peer sockets.

## Control flow and integration
Callers use these prototypes from socket LSM hooks and `file.c` open-file revalidation. Filesystem-vs-abstract address macros determine whether mediation goes through path rules or network DFA rules.

## State and dependencies
It depends on `net/af_unix.h` and AppArmor labels. It does not define state; it exposes access to Unix socket internals through macros.

## Risks
The macro guard is written as `#ifndef __AA_AF_UNIX_H` without a visible `#define`, so repeated inclusion relies on surrounding include behavior and could be fragile. The macros directly dereference Unix socket internals and must only be used with valid socket state and appropriate locks/RCU context.

## Test signals
Compile all users with warnings enabled, especially repeated includes. Exercise address classification for abstract, anonymous, autobind, and filesystem sockets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/af_unix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/apparmor.h -->
# sources/distributed-fs/ceph-client/security/apparmor/include/apparmor.h

## Purpose
`apparmor.h` defines global AppArmor mediation class IDs and runtime configuration globals shared across the LSM implementation.

## Important APIs and symbols
It defines `AA_CLASS_*` constants for file, capability, rlimits, domain, mount, ptrace, signal, net/netv9, label, module, namespace, io_uring, dbus, and related policy classes. It declares runtime globals such as `aa_g_audit`, `aa_g_debug`, `aa_g_hash_policy`, `aa_g_export_binary`, `aa_g_lock_policy`, `aa_g_logsyscall`, `aa_g_paranoid_load`, and `aa_g_path_max`. Compression level macros map to zstd only when raw binary export is compiled.

## Control flow and integration
Class constants index policydb start states, audit class names, label mediation bitmasks, and feature reporting. Runtime globals are read across audit, policy load, apparmorfs, hashing, path handling, and debug code.

## State and persistence
The globals represent runtime module/boot parameter state. Class IDs are ABI-like policy encoding constants and must stay consistent with userspace policy compilers and kernel unpacking code.

## Dependencies
It depends on Linux types and, conditionally, zstd macros through included compilation units. The note that class IDs beyond 63 require label mediation changes matters because `aa_label.mediates` is a 64-bit mask.

## Risks
Changing class values or `AA_CLASS_LAST` can break policy compatibility and label mediation checks. Runtime global changes affect security behavior system-wide.

## Test signals
Build and boot with feature combinations; verify policy classes mediate as expected and apparmorfs/audit class names align with constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/apparmor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/apparmorfs.h -->
# sources/distributed-fs/ceph-client/security/apparmor/include/apparmorfs.h

## Purpose
This header defines apparmorfs/securityfs entry descriptors, namespace/profile dentry index enums, access macros, and exported functions for creating/removing AppArmor filesystem state.

## Important APIs and types
`struct aa_sfs_entry` describes static securityfs files and directories with boolean/string/u64/FOPS values. Macros such as `AA_SFS_FILE_BOOLEAN`, `AA_SFS_FILE_STRING`, `AA_SFS_FILE_U64`, `AA_SFS_FILE_FOPS`, and `AA_SFS_DIR` build entry arrays. The `AAFS_NS_*` and `AAFS_PROF_*` enums index `dents[]` arrays in namespaces and profiles. Functions include `aa_create_aafs`, `aa_destroy_aafs`, `__aa_bump_ns_revision`, profile/ns mkdir/rmdir/migration helpers, and rawdata creation/removal stubs or implementations.

## Control flow and integration
Policy namespace/profile code calls these helpers when policy objects are created, replaced, or removed. Static feature arrays in `apparmorfs.c` use the entry macros to build securityfs. Rawdata functions compile to no-ops unless export binary support is enabled.

## State and persistence
The header standardizes dentry slots used as in-memory references from `aa_ns` and `aa_profile`. `aa_null` is a global path used to replace unauthorized inherited descriptors.

## Dependencies
It depends on VFS dentry/file operations, AppArmor profile and namespace structures, and optional raw policy load data.

## Risks
Dentry index order is a contract with profile/ns allocation and removal code; mismatches can remove or expose the wrong file. Rawdata stubs must preserve caller semantics when export is disabled.

## Test signals
Compile with export binary on/off. Load/replace/remove profiles and namespaces while verifying all dentry slots are created, migrated, and removed without leaks or stale files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/apparmorfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/audit.h -->
# sources/distributed-fs/ceph-client/security/apparmor/include/audit.h

## Purpose
`audit.h` defines AppArmor audit modes, audit event types, operation strings, the `apparmor_audit_data` payload, audit initialization macros, and audit helper prototypes.

## Important APIs and types
Key types are `enum audit_mode`, `enum audit_type`, and `struct apparmor_audit_data`. Operation constants cover filesystem, mount, socket, ptrace, signal, exec, change_hat/profile, procattr, rlimit, user namespace, and io_uring events. `DEFINE_AUDIT_DATA` initializes common LSM audit data. `complain_error` converts access denials to success in complain mode.

## Control flow and integration
Mediation code fills this structure and passes it to `aa_audit` or `aa_audit_msg` with optional callbacks. The nested union carries operation-specific fields for file target/owner, rlimit, signal, network peer, interface, mount, and io_uring data.

## State and persistence
The header defines transient audit payloads. It does not own persistent state, though audit rules can hold parsed labels through functions declared here.

## Dependencies
It depends on Linux audit, LSM audit, scheduler/task types, and AppArmor file and label structures.

## Risks
The union layout requires callbacks to interpret only fields valid for the audited class. Operation strings are part of audit-visible behavior; changing them affects tooling. `complain_error` intentionally hides `-EPERM`/`-EACCES` from callers.

## Test signals
Audit output tests should validate operation strings and class-specific fields for each mediation path. Complain-mode tests should assert access succeeds while audit records still show allowed denials.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/audit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/capability.h -->
# sources/distributed-fs/ceph-client/security/apparmor/include/capability.h

## Purpose
This header defines AppArmor's capability rule representation and public capability mediation API.

## Important APIs and types
`struct aa_caps` stores allow, audit, denied, quiet, kill, and extended capability bitsets. `aa_sfs_entry_caps` exposes feature metadata. `aa_profile_capget` computes a profile's visible capabilities, and `aa_capable` enforces a capability request against a label.

## Control flow and integration
Policy unpack fills `aa_caps` or DFA policydb structures; LSM capability hooks call `aa_capable`; apparmorfs feature reporting references `aa_sfs_entry_caps`.

## State and persistence
Capability policy is stored in per-ruleset `aa_caps`. `aa_free_cap_rules` is currently a no-op because the structure owns no dynamic allocations.

## Dependencies
It depends on Linux capability/sched types, apparmorfs entries, and AppArmor labels/profiles.

## Risks
The header guard end comment has a typo but the macro itself is functional. Any future dynamic fields added to `aa_caps` must update `aa_free_cap_rules`.

## Test signals
Compile capability mediation with policy load/unload cycles and verify no dynamic cleanup is required. Test feature reporting for extended capability support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/capability.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/cred.h -->
# sources/distributed-fs/ceph-client/security/apparmor/include/cred.h

## Purpose
`cred.h` defines helpers for reading, setting, and safely refreshing the AppArmor label stored in Linux credentials, plus a helper for deriving the current AppArmor namespace.

## Important APIs and functions
- `cred_label` and `set_cred_label` access the LSM credential blob.
- `aa_get_newest_cred_label` and `_condref` return current label versions, respecting stale replacements.
- `aa_current_raw_label`, `aa_get_current_label`, `begin_current_label_crit_section`, and related end helpers manage current-task label references.
- `aa_get_current_ns` returns a refcounted namespace for the current label.

## Control flow
The fast critical-section helpers avoid taking references when the cred label is not stale and the current cred cannot change during the section. `begin_current_label_crit_section` may sleep and updates current credentials to the newest label if the old label is stale.

## State and persistence
The state is the AppArmor label pointer in the credential security blob. Refreshing stale labels can replace current task credentials. Namespace references are derived from label components.

## Dependencies
It depends on Linux credentials/scheduler, AppArmor label versioning, policy namespace refs, and task context/blob offsets.

## Risks
Using the sleepable `begin_current_label_crit_section` inside locks is unsafe; the header provides non-sleeping variants for locked contexts. Mispaired put/end calls can leak or underflow label refs. Direct `set_cred_label` transfers ownership expectations to credential lifetime management.

## Test signals
Profile replacement tests should show stale labels update correctly. Lockdep/RCU tests should cover locked critical-section helpers. Credential transition tests should verify label refs are balanced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/cred.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/crypto.h -->
# sources/distributed-fs/ceph-client/security/apparmor/include/crypto.h

## Purpose
This header exposes optional AppArmor SHA-256 policy hash helpers and provides no-op stubs when hash support is not compiled.

## Important APIs
When `CONFIG_SECURITY_APPARMOR_HASH` is enabled, it declares `init_profile_hash`, `aa_hash_size`, `aa_calc_hash`, and `aa_calc_profile_hash`. Otherwise `aa_calc_hash` returns `NULL`, `aa_calc_profile_hash` returns success, and `aa_hash_size` returns zero.

## Control flow and integration
Callers can invoke hash helpers without local `#ifdef`s. AppArmorfs and policy load code use these functions to create or display profile/rawdata hashes only when available.

## State and persistence
The header owns no state. It determines whether callers can allocate and persist hash buffers in profiles/load data.

## Dependencies
It includes `policy.h` for `struct aa_profile` and configuration symbols from Kconfig.

## Risks
The disabled stub for `aa_calc_hash` returning `NULL` must not be mistaken for an allocated digest or ERR_PTR. Callers need to branch on compiled/runtime feature availability before displaying hashes.

## Test signals
Build with hash support disabled and verify callers compile and avoid dereferencing zero-size hashes. Build enabled and verify exported hash sizes are 32 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/crypto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/domain.h -->
# sources/distributed-fs/ceph-client/security/apparmor/include/domain.h

## Purpose
`domain.h` declares AppArmor domain transition flags and public functions for exec-time and self-directed profile changes.

## Important APIs
Flags include `AA_CHANGE_TEST`, `AA_CHANGE_CHILD`, `AA_CHANGE_ONEXEC`, and `AA_CHANGE_STACK`. Public functions are `x_table_lookup`, `apparmor_bprm_creds_for_exec`, `aa_change_hat`, and `aa_change_profile`.

## Control flow and integration
The exec LSM path calls `apparmor_bprm_creds_for_exec`. Procattr or AppArmor task interfaces call `aa_change_hat` and `aa_change_profile`. File policy transition code uses `x_table_lookup` to resolve transition table entries.

## State and persistence
This header owns no state, but the declared functions mutate task credentials and AppArmor task context fields.

## Dependencies
It depends on Linux binprm/types and AppArmor labels.

## Risks
Flag values are part of internal API contracts with procattr parsing and domain code. Misusing `AA_CHANGE_TEST` could accidentally perform a real transition or suppress one.

## Test signals
Compile callers and run change_profile/change_hat test and real modes, including stack and onexec combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/domain.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/file.h -->
# sources/distributed-fs/ceph-client/security/apparmor/include/file.h

## Purpose
`file.h` defines AppArmor file permission masks, file context state, exec transition index encoding, path conditions, and public APIs for path/open-file mediation.

## Important APIs and types
`struct aa_file_ctx` stores a spinlock, cached label, and allowed mask in the file LSM blob. `struct path_cond` carries object uid and mode for owner/conditional permissions. `AA_X_*` constants encode exec transition type, table index, unsafe, child, inherit, and unconfined flags. Public functions include `aa_audit_file`, `aa_lookup_condperms`, `aa_str_perms`, `aa_path_perm`, `aa_path_link`, `aa_file_perm`, and `aa_inherit_files`.

## Control flow and integration
LSM file hooks map open flags with `aa_map_file_to_perms`, then call path or file revalidation functions. Domain transition code interprets `xindex` flags produced by file permission lookups.

## State and persistence
Per-open-file state lives in the file security blob. Permission masks and xindex values are policy/runtime state, not disk persistence.

## Dependencies
It depends on AppArmor domain, match, permissions, labels, and kernel file structures.

## Risks
The same bit ranges encode file permissions and exec transition metadata, so policy unpacking and domain execution must agree. Cached `aa_file_ctx.allow` can become stale with policy replacement, relying on revalidation paths.

## Test signals
Test `aa_map_file_to_perms` for read/write/append/truncate/create combinations. Exercise exec xindex transitions and file cache revalidation after label changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/ipc.h -->
# sources/distributed-fs/ceph-client/security/apparmor/include/ipc.h

## Purpose
This header declares AppArmor IPC signal mediation and defines signal mapping constants used by signal audit/permission code.

## Important APIs
`SIGUNKNOWN` and `MAXMAPPED_SIG` describe signal mapping bounds. `aa_may_signal` checks whether a sender label/cred may signal a target label/cred with a given signal.

## Control flow and integration
Signal LSM hooks call `aa_may_signal`; domain code depends indirectly on IPC/ptrace mediation for transition safety checks.

## State and persistence
No state is defined here. Signal decisions are computed from loaded policy and current credentials.

## Dependencies
It depends on Linux scheduler types and AppArmor labels through function parameters.

## Risks
Signal number mapping must stay aligned with audit strings and policy encoding. Unknown or out-of-range signals need deterministic handling.

## Test signals
Test allowed/denied signal sends across labels, unknown signal mapping, and audit output for mapped/unmapped signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/ipc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/label.h -->
# sources/distributed-fs/ceph-client/security/apparmor/include/label.h

## Purpose
`label.h` defines AppArmor labels: refcounted, RCU-aware sets of one or more profiles that represent confinement. It also defines label sets, proxies for replacement, iteration macros, merge/subset helpers, printing/parsing APIs, and refcount helpers.

## Important APIs and types
Core types are `struct aa_labelset`, `struct aa_proxy`, `struct label_it`, and `struct aa_label`. Label flags include unconfined, null, immutable, in-tree, profile, explicit, stale, renamed, and revoked. Iteration macros cover all profiles, confined profiles, profiles in a namespace, merge differences, and set differences. Public functions cover allocation, insertion/replacement, subset checks, merge, name update, printing, parsing, and profile-label matching.

## Control flow and integration
Most mediation code iterates labels with `fn_for_each_confined` or namespace-scoped variants. Policy replacement marks labels stale and redirects proxies so callers can obtain newest labels. Stacked labels are parsed and split using `stacksplitdfa`.

## State and persistence
Labels are long-lived kernel objects with krefs, RCU cleanup, rbtree membership in namespace label sets, proxy pointers, secids, cached names, mediation bitmasks, and variable profile vectors. Proxies preserve stable object identity across replacement.

## Dependencies
It depends on atomic/kref/RCU/rbtree/audit primitives, AppArmor class constants, and lib helpers. It is foundational for credentials, policy, file, socket, audit, and domain code.

## Risks
Label lifetime and replacement are high risk: stale/proxy handling must avoid use-after-free, refcount leaks, and stale security decisions. Iteration macros hide control flow and rely on labels being NUL-terminated by profile vectors. The `mediates` bitmask only supports class IDs up to 63.

## Test signals
Stress profile replacement/removal while files and sockets hold labels. Test stacked-label parsing, merge/subset operations, namespace-scoped iteration, RCU label acquisition, and audit/seq printing for hidden or subnamespace labels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/label.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/lib.h -->
# sources/distributed-fs/ceph-client/security/apparmor/include/lib.h

## Purpose
`lib.h` gathers shared AppArmor utilities: debug/assert macros, namespace visibility aliases, LSM blob offsets, common refcount type, string tables/counting, policy-list helpers, DFA null transition helper, path mediation predicate, and label-build macros for domain transitions.

## Important APIs and types
Debug constants and macros include `DEBUG_*`, `AA_DEBUG`, `AA_WARN`, `AA_BUG`, and `AA_ERROR`. `struct aa_common_ref` tags refcounted objects embedded in apparmorfs inodes. `struct aa_str_table` and `aa_str_table_ent` store transition/tag strings. `struct aa_policy` is the common name/list/profile-child base for namespaces and profiles. `fn_label_build` and `fn_label_build_in_scope` construct transition labels across stacked profile labels.

## Control flow and integration
`AA_BUG` becomes a runtime WARN when debug asserts are enabled and compile/no_printk validation otherwise. `aa_dfa_null_transition` provides the standard NUL separator step used by link, domain, and network pair matching. `fn_label_build` invokes a transition callback for each profile in a stacked label, flattens/uniques resulting profile vectors, and returns a merged label.

## State and persistence
The header declares global `apparmor_initialized`, `apparmor_blob_sizes`, and `stacksplitdfa`. Counted strings and string tables are refcounted in-memory policy state.

## Dependencies
It depends on slab, fs, LSM hooks, match DFA declarations, labels/profiles through macro call sites, and policy namespace visibility functions.

## Risks
Macro-heavy label building can obscure error paths and cleanup responsibilities. Debug behavior changes significantly with `CONFIG_SECURITY_APPARMOR_DEBUG_ASSERTS`. `path_mediated_fs` excludes `SB_NOUSER` filesystems from path mediation, so filesystem flags directly affect security coverage.

## Test signals
Compile with debug asserts on/off. Exercise stacked-label transitions that produce multiple intermediate labels and allocation failures. Validate string table resizing/destruction and policy lookup under RCU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/match.h -->
# sources/distributed-fs/ceph-client/security/apparmor/include/match.h

## Purpose
`match.h` defines the packed DFA table format and matching API used by AppArmor policy databases for paths, labels, network rules, capabilities, and transition parsing.

## Important APIs and types
Core constants include `DFA_NOMATCH`, `DFA_START`, `YYTH_MAGIC`, table IDs, data-width flags, accept flags, and match flags. `struct table_set_header`, `struct table_header`, and `struct aa_dfa` describe loaded DFA tables. Public functions include `aa_dfa_unpack`, `aa_dfa_match_len`, `aa_dfa_match`, `aa_dfa_next`, `aa_dfa_outofband_transition`, match-until helpers, `aa_dfa_leftmatch`, and refcount helpers.

## Control flow and integration
Policy unpack loads big-endian packed tables, converts to host order with `UNPACK_ARRAY`, and produces refcounted `aa_dfa` objects. Mediation code then starts from class-specific states and consumes strings, bytes, NUL separators, or out-of-band transitions to reach accept table entries that map to permissions.

## State and persistence
DFAs are in-memory policy objects with kref-managed lifetime and pointers to individual table headers. The packed input format is a policy ABI between userspace parser and kernel.

## Dependencies
It depends on kref and AppArmor policy unpack/match implementations. `ACCEPT_TABLE` and related macros require expected table IDs to be present.

## Risks
Malformed DFA tables are security sensitive. Endianness conversion, table sizes, out-of-band transitions, and accept table indexing must be verified during unpack. `aa_state_t` is an unsigned int, so table bounds and state validation matter.

## Test signals
KUnit/fuzz tests should cover DFA unpack validation, invalid magic/flags/table widths, endian conversion, normal matches, leftmost matches, NUL transitions, out-of-band transitions, and refcount cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/match.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/mount.h -->
# sources/distributed-fs/ceph-client/security/apparmor/include/mount.h

## Purpose
`mount.h` defines AppArmor mount permission bits and declares the mount mediation API used by LSM mount hooks.

## Important APIs and types
Permission bits include `AA_MAY_PIVOTROOT`, `AA_MAY_MOUNT`, `AA_MAY_UMOUNT`, and `AA_AUDIT_DATA`/`AA_MNT_CONT_MATCH`. `AA_MS_IGNORE_MASK` lists kernel/internal mount flags ignored by policy. Public functions cover remount, bind mount, mount propagation type changes, old/new move mount paths, new mount, umount, and pivot_root.

## Control flow and integration
LSM mount hooks pass credentials, labels, paths, device/type/data strings, and flags to these functions. Implementations match policy and audit through shared domain/policy/perms infrastructure.

## State and persistence
The header owns no state. Mount decisions use current labels and loaded policy; successful mount operations change VFS state outside AppArmor.

## Dependencies
It depends on Linux fs/path structures, AppArmor domain, and policy definitions.

## Risks
Mount flag normalization via `AA_MS_IGNORE_MASK` must remain aligned with kernel VFS semantics. Move-mount and detached mount behavior is subtle and needs tests across old/new APIs.

## Test signals
Test mount, remount, bind, move, propagation change, umount, and pivot_root permissions with ignored kernel flags and audit data matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/mount.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/net.h -->
# sources/distributed-fs/ceph-client/security/apparmor/include/net.h

## Purpose
`net.h` defines AppArmor network permission masks, socket security context, network audit helpers, secmark structures, apparmorfs feature entries, and public network mediation functions.

## Important APIs and types
Permission aliases map send/receive to write/read and define shutdown, connect, accept, bind, listen, get/set option, network masks, filesystem-socket masks, and peer masks. `struct aa_sk_ctx` stores socket label and peer labels. `DEFINE_AUDIT_NET` and `DEFINE_AUDIT_SK` initialize network audit payloads. Public functions include `aa_do_perms`, `aa_match_to_prot`, `aa_profile_af_perm`, `aa_af_perm`, `aa_sk_perm`, `aa_sock_file_perm`, and `apparmor_secmark_check`.

## Control flow and integration
Socket LSM hooks and AF_UNIX code use these helpers to match address family, socket type, protocol, and operation against policydb DFA states. File revalidation delegates socket files to `aa_sock_file_perm` unless AF_UNIX requires special peer/path handling.

## State and persistence
Per-socket state lives in the socket LSM blob as RCU labels. `aa_secmark` entries are loaded policy state for packet/secmark mediation.

## Dependencies
It depends on net/sock, Linux paths, apparmorfs, labels, permissions, policy, and audit structures.

## Risks
Network v8/v9 compatibility and fallback behavior must match policy compiler output. `aa_sk_ctx.peer_lastupdate` is pointer-comparison-only and must not be dereferenced. AF_UNIX reuses network masks but sometimes delegates to file/path permissions.

## Test signals
Test AF_INET/AF_UNIX create/connect/bind/listen/accept/send/receive/option checks, secmark checks, socket-file mediation, and feature reporting for network_v8/network_v9.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/net.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/path.h -->
# sources/distributed-fs/ceph-client/security/apparmor/include/path.h

## Purpose
`path.h` defines path-name generation flags and buffer helpers used by AppArmor path-based mediation.

## Important APIs
`enum path_flags` includes directory marking, socket condition handling, disconnected path connection, chroot-relative lookup, namespace root connection, deleted-file delegation, and deleted-file mediation. `aa_path_name` converts a kernel `struct path` into an AppArmor policy name. `aa_get_buffer` and `aa_put_buffer` manage temporary path buffers, with `IN_ATOMIC` indicating allocation constraints.

## Control flow and integration
File, domain, mount, and AF_UNIX filesystem socket mediation call `aa_path_name` before DFA matching. The flags are combined from profile path flags and operation-specific conditions.

## State and persistence
The header owns no persistent state. Buffers are temporary kernel allocations or per-CPU resources managed by the implementation.

## Dependencies
It depends on Linux path structures through function parameters and AppArmor profile flags.

## Risks
Path generation is a security boundary: disconnected/deleted/chroot-relative behavior determines the policy string that is matched. Buffer allocation failures can deny operations. Callers must release buffers exactly once.

## Test signals
Test normal, chrooted, disconnected, deleted, directory, and socket paths. Include atomic and sleepable buffer allocation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/path.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/perms.h -->
# sources/distributed-fs/ceph-client/security/apparmor/include/perms.h

## Purpose
`perms.h` defines AppArmor's common permission bit layout, `aa_perms` structure, permission accumulation semantics, cross-check macros, and permission/audit helper prototypes.

## Important APIs and types
It maps read/write/exec/append to VFS bits and defines AppArmor-specific create/delete/open/rename/setattr/getattr/cred/chmod/chown/chgrp/lock/mmap/mprotect/link/snapshot/stack/onexec/change_profile/changehat bits. `struct aa_perms` contains allow, deny, subtree, cond, kill, complain, prompt, audit, quiet, hide, xindex, tag, and label fields. `aa_perms_accum` and `aa_perms_accum_raw` combine permissions across stacked labels. `aa_check_perms` applies decisions and auditing.

## Control flow and integration
Policydb accept entries are converted into `aa_perms`, mode-adjusted, accumulated across profiles, and checked against requested masks. Cross-check macros validate bidirectional or namespace/profile pair permissions, used notably for AF_UNIX peer checks.

## State and persistence
Permission sets are loaded policy state and transient decision state. `nullperms`, `allperms`, and `default_perms` provide standard defaults.

## Dependencies
It depends on Linux fs permission bits and AppArmor labels/audit structures.

## Risks
Permission bit overlays such as `AA_LINK_SUBSET` over `AA_MAY_LOCK` require context-specific interpretation. Accumulation rules are security critical for stacked labels. `AA_MAY_DELEGATE` appears as an empty macro marker, so callers must not treat it as a usable bit.

## Test signals
Unit tests should cover permission accumulation, deny overriding allow, audit/quiet/kill/complain interactions, link subset overlay behavior, xcheck macros, and string/audit formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/perms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/policy.h -->
# sources/distributed-fs/ceph-client/security/apparmor/include/policy.h

## Purpose
`policy.h` defines AppArmor's core policy structures: policy databases, rulesets, attachments, profiles, generic policy data blobs, mode macros, policy management permissions, and profile/policy reference helpers.

## Important APIs and types
Key structures are `aa_policydb`, `aa_data`, `aa_ruleset`, `aa_attachment`, and `aa_profile`. `aa_policydb` wraps DFA, permissions, transition strings, tags, and class start states. `aa_ruleset` combines policy/file policydbs, capabilities, rlimits, and secmarks. `aa_profile` combines policy identity, parent/ns, mode/audit/path flags, attachment data, rawdata/hash/dentries/data, and embedded variable-size label/rules.

Mode macros include `COMPLAIN_MODE`, `USER_MODE`, `KILL_MODE`, `PROFILE_IS_HAT`, and `profile_unconfined`. Public functions cover allocation/free, lookup, profile replacement/removal, learning-profile creation, ruleset allocation, policy management capability checks, and mediation-class computation.

## Control flow and integration
Policy unpack fills these structures. Mediation code retrieves `profile->label.rules[0]`, checks `RULE_MEDIATES` for a class, uses file or policy policydbs for DFA matching, and applies mode/audit behavior. Policy management paths call `aa_replace_profiles` and `aa_remove_profiles`.

## State and persistence
This header defines the in-memory representation of loaded policy. Profiles belong to namespaces, have hierarchy/children, may hold raw policy load data and hashes, expose apparmorfs dentries, and carry label/rules lifetime state.

## Dependencies
It depends on Linux credentials, capabilities, krefs, rhashtable, sockets, AppArmor audit/capability/domain/file/lib/label/net/perms/resource, and apparmorfs dentry indices.

## Risks
Profile structure layout is delicate because `struct aa_label label` is variable-length and last. `aa_get_newest_profile` returns a profile from a label reference and depends on label lifetime rules. Class mediation fallback between NETV9 and NET must match policy ABI. Policy management capability checks are central to load/remove security.

## Test signals
Test policy allocation/free under replacement/removal, profile lookup by namespace/fqname, learning profile creation, rawdata/hash dentries, class mediation bits, v9/v8 network fallback, and policy load/remove permission checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/policy_compat.h -->
# sources/distributed-fs/ceph-client/security/apparmor/include/policy_compat.h

## Purpose
`policy_compat.h` declares compatibility helpers for mapping older AppArmor policy ABI versions into current internal policy formats.

## Important APIs and symbols
It defines `K_ABI_MASK`, `FORCE_COMPLAIN_FLAG`, version comparison macros, version constants `v5` through `v9`, and declarations for `aa_compat_map_xmatch`, `aa_compat_map_policy`, and `aa_compat_map_file`.

## Control flow and integration
Policy unpack/load code calls these mapping helpers after reading older policy blobs. Version comments document semantic changes: v6 per-entry policydb mediation checks, v8 full network masking, and v9 xbits as policydb permission bits.

## State and persistence
No state is defined here. The helpers mutate loaded policydb structures so they can be mediated by the current runtime.

## Dependencies
It depends on `policy.h` and therefore the main policydb/profile structures.

## Risks
ABI mapping errors can silently grant or deny access differently from older policy semantics. Version masks must preserve non-version flags such as force-complain.

## Test signals
Load v5, v6, v7, v8, and v9 policy fixtures and compare expected permission decisions, especially network masks, file xmatch, and force-complain behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/apparmor/include/policy_compat.h -->
