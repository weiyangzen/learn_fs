# subset-b-006348 security SMACK and TOMOYO research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/smack/smack_lsm.c -->
# sources/distributed-fs/ceph-client/security/smack/smack_lsm.c

## Purpose

`smack_lsm.c` is the core Linux Security Module implementation for Smack in this kernel source tree. It registers Smack with the LSM framework, defines Smack blob sizes, initializes built-in labels, and supplies hook implementations for process attributes, inode and superblock labeling, file access, sockets, networking labels, System V IPC, keys, notifications, audit rules, overlayfs copy-up, io_uring, and security context conversion.

## Important APIs, types, and functions

The file exports `smack_blob_sizes`, `smack_initcall()`, and the LSM definition `DEFINE_LSM(smack)`. The central registration table is `smack_hooks[]`, which maps Linux LSM hook names to local functions. Important local helpers include `smk_fetch()` for reading Smack xattrs, `init_inode_smack()` and `init_task_smack()` for blob initialization, `smk_copy_rules()` and `smk_copy_relabel()` for credential duplication, and `smk_ptrace_rule_check()` for ptrace policy. Filesystem setup flows through `smack_sb_alloc_security()`, `smack_fs_context_parse_param()`, `smack_sb_eat_lsm_opts()`, and `smack_set_mnt_opts()`. Inode and xattr hooks include `smack_inode_init_security()`, `smack_d_instantiate()`, `smack_inode_setxattr()`, `smack_inode_post_setxattr()`, `smack_inode_setsecurity()`, and `smack_inode_getsecurity()`. Networking hinges on `socket_smack`, `smack_netlbl_add()`, `smack_netlbl_delete()`, `smack_socket_sock_rcv_skb()`, `smack_from_netlbl()`, `smack_socket_connect()`, and `smack_socket_sendmsg()`.

## Control flow

Boot-time setup starts in `smack_init()`: it creates the rule slab cache, labels the initial task as floor, registers `smack_hooks[]`, marks Smack enabled, initializes the built-in label list, and configures audit secctx support. Later `smack_initcall()` mounts/registers smackfs through `init_smk_fs()` and installs netfilter hooks through `smack_nf_ip_init()`.

Filesystem control flow starts with per-superblock defaults initialized to floor/hat labels. Mount options are parsed from modern `fs_context` parameters or legacy comma-separated LSM options, imported as Smack labels, then applied once in `smack_set_mnt_opts()`. Unprivileged mounts cannot supply Smack options; in non-init user namespaces, most backing stores are treated as untrusted and only root-labeled objects are trusted. `smack_d_instantiate()` lazily finalizes inode labels from special filesystem defaults, current task labels, or xattrs. Creation flows through `smack_inode_alloc_security()` and `smack_inode_init_security()`, including transmute handling when directory flags and rules permit inherited directory labels.

Access checks are mostly direct conversions from kernel operations to Smack permissions. File and inode operations call `smk_curacc()`, `smk_tskacc()`, or `smk_access()` with audit context and optional bringup logging. Exec can change the subjective task label from the file's `SMACK64EXEC` xattr after ptrace and unsafe-exec checks. Sockets are labeled on allocation and post-create; IPv4 uses NetLabel/CIPSO plus secmark fallback, while IPv6 support is selected by build-time labeling modes. Packet receive checks identify a packet label from secmark or NetLabel, then require the sender label to write to the socket input label. IPC and key hooks attach a Smack label to each object and translate operation-specific permissions into read/write/lock/deliver checks.

## State and persistence behavior

Persistent security state is stored in LSM blobs: `task_smack` in credentials, `inode_smack` in inodes, `superblock_smack` in superblocks, a `smack_known *` in files, IPC objects, keys, and messages, and `socket_smack` in sockets. On disk, Smack state persists mainly through xattrs such as `security.SMACK64`, `security.SMACK64EXEC`, `security.SMACK64MMAP`, and `security.SMACK64TRANSMUTE`; IP input/output xattrs are socket-only. Policy labels and rules point into the global `smack_known_list`, which is append-oriented and shared with smackfs. Runtime network state includes socket NetLabel attributes, IPv4/IPv6 host label lists owned elsewhere in smackfs, and optional IPv6 port-label records guarded by `smack_ipv6_lock`.

## Dependencies and integration points

This file depends on the LSM hook framework, VFS xattr and mount APIs, credential APIs, NetLabel/CIPSO, secmark, IPv4/IPv6 networking, audit, keyrings, watch queues, overlayfs copy-up hooks, and io_uring hooks. It uses public helpers and globals from `smack.h`, including `smk_import_entry()`, `smk_access()`, `smk_curacc()`, `smack_log()`, built-in labels, policy lists, xattr names, and smackfs-maintained network/syslog/ptrace configuration. It integrates directly with `smackfs.c` through globals such as `smack_net_ambient`, `smack_syslog_label`, `smack_ptrace_rule`, host-label lists, and `init_smk_fs()`, and with `smack_netfilter.c` through `smack_nf_ip_init()`.

## Risks and test signals

High-risk areas are xattr validation, transmute inheritance, untrusted superblock handling, ptrace policy modes, exec label transitions, NetLabel/secmark precedence, IPv6 port-label lifetime, RCU traversal of policy lists, and mismatched credential copying. Regression tests should exercise mount option parsing, label xattr set/remove/get paths, file and directory transmutation, `SMACK64EXEC` and `SMACK64MMAP`, socket pair and UNIX peer labels, IPv4 CIPSO and secmark receive paths, IPv6 host/port policy when enabled, System V IPC permission checks, key permission checks, `/proc/self/attr/current` and `lsm_getselfattr` behavior, and LSM hook registration under `CONFIG_SECURITY_SMACK`, `CONFIG_AUDIT`, `CONFIG_KEYS`, `CONFIG_NETWORK_SECMARK`, `CONFIG_IPV6`, and `CONFIG_IO_URING`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/smack/smack_lsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/smack/smack_netfilter.c -->
# sources/distributed-fs/ceph-client/security/smack/smack_netfilter.c

## Purpose

`smack_netfilter.c` is the small Smack netfilter integration layer. Its job is to tag locally generated IPv4, and optionally IPv6, packets with the Smack secid stored in the sending socket's outbound label so downstream networking and peer-security code can use `skb->secmark`.

## Important APIs, types, and functions

The main hook is `smack_ip_output()`, registered in `smack_nf_ops[]` for `NF_INET_LOCAL_OUT`. It uses `skb_to_full_sk()` to find the originating socket, `smack_sock()` to access the socket's `socket_smack` blob, and writes `ssp->smk_out->smk_secid` into `skb->secmark`. `smack_nf_register()` and `smack_nf_unregister()` install or remove the hook array per network namespace using `nf_register_net_hooks()` and `nf_unregister_net_hooks()`. `smack_net_ops` wires those into the pernet subsystem, and `smack_nf_ip_init()` conditionally registers the subsystem after Smack has been enabled.

## Control flow

During Smack device init, `smack_initcall()` calls `smack_nf_ip_init()`. If `smack_enabled` is still zero, the function is a no-op. Otherwise it logs that netfilter hooks are being registered and calls `register_pernet_subsys()`. For every network namespace, `smack_nf_register()` installs the output hooks. At packet transmit time, netfilter invokes `smack_ip_output()` before other security hooks at the SELinux-first priority value; if a full socket is available, the hook copies the Smack outbound secid to `skb->secmark`, then always returns `NF_ACCEPT`.

## State and persistence behavior

This file does not own persistent policy state. It derives all labels from the socket security blob initialized and maintained by `smack_lsm.c`. Its only per-packet state mutation is assigning `skb->secmark`. Hook registration is per network namespace and is undone when namespaces exit through `smack_nf_unregister()`.

## Dependencies and integration points

It depends on netfilter IPv4/IPv6 hook APIs, per-network-namespace registration, socket extraction from `sk_buff`, and Smack socket blobs from `smack.h`. It integrates with the receive-side logic in `smack_lsm.c`, where `smack_from_skb()` prefers `skb->secmark` over NetLabel/CIPSO labels when `CONFIG_NETWORK_SECMARK` is enabled. IPv6 registration exists only when `CONFIG_IPV6` is enabled.

## Risks and test signals

The main risks are missing full socket association for some local packets, secmark overwrites interacting with other netfilter users, namespace registration failures, and configuration skew between `CONFIG_SECURITY_SMACK_NETFILTER`, `CONFIG_NETWORK_SECMARK`, and IPv6 support. Useful tests verify that local IPv4 and IPv6 sends carry the expected secmark, unlabeled or socketless packets are accepted unchanged, per-netns registration/unregistration succeeds, and receive-side policy observes the secmark before falling back to NetLabel.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/smack/smack_netfilter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/smack/smackfs.c -->
# sources/distributed-fs/ceph-client/security/smack/smackfs.c

## Purpose

`smackfs.c` implements the `smackfs` pseudo filesystem, the user-space control plane for Smack policy. It exposes files for loading global and task-local access rules, querying access decisions, configuring CIPSO/NetLabel mappings, setting ambient network labels, managing capability/syslog/ptrace restrictions, allowing controlled self-relabeling, and registering the smackfs mount point.

## Important APIs, types, and functions

The file exports mutable Smack policy globals used by `smack_lsm.c`: `smack_net_ambient`, `smack_cipso_direct`, `smack_cipso_mapped`, `smack_syslog_label`, `smack_ptrace_rule`, and network host lists `smk_net4addr_list` and optionally `smk_net6addr_list`. It also exports `smk_destroy_label_list()` and `init_smk_fs()`. `enum smk_inos` maps smackfs pseudo-inodes to file entries. Rule parsing is centered on `struct smack_parsed_rule`, `smk_perm_from_str()`, `smk_fill_rule()`, `smk_parse_rule()`, `smk_parse_long_rule()`, `smk_set_access()`, and `smk_write_rules_list()`. NetLabel/CIPSO configuration flows through `smk_cipso_doi()`, `smk_unlbl_ambient()`, `smk_set_cipso()`, `smk_write_net4addr()`, and `smk_write_net6addr()`. The final filesystem surface is declared in `smk_fill_super()` with `tree_descr` entries and per-file `file_operations`.

## Control flow

Initialization is called from Smack's LSM initcall path. `init_smk_fs()` skips work if Smack was not selected, creates `/sys/fs/smackfs`, registers and kernel-mounts `smackfs`, resets NetLabel defaults, creates the default CIPSO DOI, initializes the unlabeled ambient mapping, and populates NetLabel secattrs for built-in labels.

Most write paths follow a similar sequence: require `CAP_MAC_ADMIN` where the operation changes global policy, reject partial writes by requiring `*ppos == 0`, copy user data into kernel memory, parse labels or numeric controls, then update RCU-protected lists or global pointers under a mutex. Global policy rule writes through `load`, `load2`, and `change-rule` update per-subject rule lists, while `load-self` and `load-self2` update only the current credential's local rules. `access` and `access2` are transaction files: a write parses subject/object/access input, evaluates `smk_access()`, and a following read returns `"1"` or `"0"`. `revoke-subject` zeroes all rules for one subject.

Network control files configure CIPSO DOI, direct/mapped levels, label-to-CIPSO category mappings, IPv4 single-label hosts, IPv6 host labels, and the ambient unlabeled label. IPv4 host entries also update NetLabel static unlabeled mappings. Reads use seq_file traversal under RCU so active readers can observe list state while writers publish changes.

## State and persistence behavior

smackfs state is kernel-resident and persists only for the running boot unless user space reloads policy. Global access rules are stored on each `smack_known` label's `smk_rules` list. Task-local rules and self-relabel allow-lists live in credential `task_smack` blobs and are copied during credential preparation. Network state is held in global ambient/CIPSO variables, built-in label secattrs, and IPv4/IPv6 host lists. The `onlycap` list is swapped with RCU via `smk_list_swap_rcu()`. `relabel-self` updates credentials by preparing new creds and committing them.

## Dependencies and integration points

This file depends on VFS pseudo-filesystem helpers, seq_file, simple transaction files, sysfs mount point creation, NetLabel/CIPSO configuration, audit identity collection, RCU list primitives, credential APIs, and Smack label/rule helpers from `smack.h`. It is the administrative counterpart of `smack_lsm.c`: the LSM hooks consume rule lists, ambient network labels, CIPSO mappings, single-label hosts, ptrace mode, syslog label, onlycap list, and relabel lists that are changed through smackfs.

## Risks and test signals

Risks include parser compatibility between fixed 24-byte and long-label formats, partial-write truncation behavior, permission checks on world-writable task-local files, invalid label clearing semantics for `onlycap` and `unconfined`, RCU publication of replaced lists, NetLabel rollback on DOI changes, IPv4/IPv6 mask parsing bugs, and stale NetLabel cache after CIPSO updates. Tests should cover each smackfs node's read/write contract, privilege failures, malformed rules, long labels, task-local rules, access transaction results, CIPSO category maps, DOI/direct/mapped changes, ambient relabeling, single-label host update/delete behavior, relabel-self credential changes, ptrace/syslog enforcement in `smack_lsm.c`, and mount registration through `/sys/fs/smackfs`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/smack/smackfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/Kconfig -->
# sources/distributed-fs/ceph-client/security/tomoyo/Kconfig

## Purpose

This Kconfig file declares the build-time configuration surface for the TOMOYO Linux security module. It enables TOMOYO itself and exposes defaults controlling learning-mode policy growth, audit log buffering, userspace policy-loader behavior, activation trigger path, and an insecure fuzzing-only built-in setup.

## Important APIs, types, and functions

The primary symbol is `SECURITY_TOMOYO`, a boolean that depends on `SECURITY` and `NET` and selects `SECURITYFS`, `SECURITY_PATH`, and `SECURITY_NETWORK`. Supporting symbols are `SECURITY_TOMOYO_MAX_ACCEPT_ENTRY`, `SECURITY_TOMOYO_MAX_AUDIT_LOG`, `SECURITY_TOMOYO_OMIT_USERSPACE_LOADER`, `SECURITY_TOMOYO_POLICY_LOADER`, `SECURITY_TOMOYO_ACTIVATION_TRIGGER`, and `SECURITY_TOMOYO_INSECURE_BUILTIN_SETTING`.

## Control flow

There is no runtime control flow in this file. Kconfig dependency resolution controls which TOMOYO code is compiled and which constants become available to C sources. If TOMOYO is enabled, securityfs/path/network hooks are selected. If the userspace loader is not omitted, path strings for the loader and activation trigger are configurable and can be overridden later via kernel command line options. The insecure built-in setting selects loader omission and is intended only for fuzzing kernels.

## State and persistence behavior

The file defines persistent kernel configuration state. Integer defaults become compile-time defaults for TOMOYO learning and audit queues. String defaults become built-in fallback paths for policy loading. These settings persist for the built kernel image and influence boot-time TOMOYO behavior before userspace policy is loaded.

## Dependencies and integration points

It integrates with the Linux security subsystem through `SECURITY`, `SECURITYFS`, `SECURITY_PATH`, and `SECURITY_NETWORK`, and with TOMOYO C sources that read the configured maximum learning entries, audit log count, loader path, trigger path, and insecure built-in policy mode. The help text points administrators to TOMOYO userspace tooling and documents kernel command-line overrides.

## Risks and test signals

Risks are configuration skew and unsafe defaults in specialized builds. Disabling the loader changes when policy becomes active; insecure built-in mode deliberately disables important runtime checks and must not appear in production kernels. Test signals are Kconfig dependency tests, build coverage with TOMOYO enabled/disabled, boot tests for loader and omit-loader paths, verification that audit log limits match `SECURITY_TOMOYO_MAX_AUDIT_LOG`, and fuzzing builds that intentionally enable `SECURITY_TOMOYO_INSECURE_BUILTIN_SETTING`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/Makefile -->
# sources/distributed-fs/ceph-client/security/tomoyo/Makefile

## Purpose

This Makefile defines how the TOMOYO security module objects and generated built-in policy header are built. It lists all TOMOYO object files, enables context analysis for the directory, and converts policy `.conf` files into C string arrays included by `common.o`.

## Important APIs, types, and functions

`obj-y` lists the TOMOYO object set: `audit.o`, `common.o`, `condition.o`, `domain.o`, `environ.o`, `file.o`, `gc.o`, `group.o`, `load_policy.o`, `memory.o`, `mount.o`, `network.o`, `realpath.o`, `securityfs_if.o`, `tomoyo.o`, and `util.o`. `targets += builtin-policy.h` declares the generated header. The `cmd_policy` recipe emits `tomoyo_builtin_profile`, `tomoyo_builtin_exception_policy`, `tomoyo_builtin_domain_policy`, `tomoyo_builtin_manager`, and `tomoyo_builtin_stat` arrays from policy config files, escaping backslashes and double quotes and appending newline escapes. `$(obj)/common.o` depends on the generated header unless insecure built-in mode is enabled.

## Control flow

The build system evaluates the wildcard dependency over object-local `policy/*.conf` files and source default `policy/*.conf.default` files. When inputs change, `if_changed,policy` regenerates `builtin-policy.h`. For each known policy name, the recipe picks the first matching real config or default config, falls back to `/dev/null`, and writes a static `__initdata` character array. In normal configurations, `common.o` is rebuilt after the generated header is available.

## State and persistence behavior

Generated state is limited to `$(obj)/builtin-policy.h` in the build output tree. The embedded arrays become init-time kernel data and are not source-controlled. Because the recipe searches both object and source policy paths, a build can override defaults with generated or local object-tree policy files.

## Dependencies and integration points

It depends on Kbuild variables and commands such as `obj-y`, `targets`, `FORCE`, `quiet_cmd_*`, `cmd_*`, `$(call if_changed,...)`, `$(wildcard ...)`, `$(firstword ...)`, and `$(filter ...)`. It integrates with `common.o`, which consumes the built-in policy header, and with `CONFIG_SECURITY_TOMOYO_INSECURE_BUILTIN_SETTING`, which suppresses that dependency for fuzzing-oriented insecure builds.

## Risks and test signals

Risks include incorrect shell escaping of policy lines, stale generated headers when policy files change, unintended object-tree policy override, missing defaults silently becoming empty arrays, and insecure-mode builds not embedding expected policy. Test signals include clean and incremental builds, policy files containing quotes and backslashes, builds with and without object-tree policy overrides, builds under insecure built-in mode, and compile checks that `common.o` sees the generated symbols.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/audit.c -->
# sources/distributed-fs/ceph-client/security/tomoyo/audit.c

## Purpose

`audit.c` implements TOMOYO audit log formatting, filtering, storage, reading, and polling. It turns `tomoyo_request_info` decisions into structured text logs that include timestamps, task credentials, object metadata, exec arguments/environment, symlink targets, domain names, and operation-specific messages, then queues those logs for `/sys/kernel/security/tomoyo/audit`.

## Important APIs, types, and functions

The main exported functions are `tomoyo_init_log()`, `tomoyo_write_log2()`, `tomoyo_write_log()`, `tomoyo_read_log()`, and `tomoyo_poll_log()`. Formatting helpers include `tomoyo_print_bprm()` for `linux_binprm` argv/envp dumps, `tomoyo_filetype()` for mode-to-type keywords, and `tomoyo_print_header()` for the audit header. Queue state is represented by `struct tomoyo_log`, `tomoyo_log` list head, `tomoyo_log_lock`, `tomoyo_log_count`, and `tomoyo_log_wait`. Filtering is centralized in `tomoyo_get_audit()`, which consults policy loaded state, profile preferences, function/category config, default config, and per-ACL grant-log overrides.

## Control flow

Callers first compute the formatted operation-specific length and call `tomoyo_write_log()` or `tomoyo_write_log2()`. `tomoyo_write_log()` performs a sizing `vsnprintf()`, restarts the varargs, and delegates. `tomoyo_write_log2()` asks `tomoyo_get_audit()` whether the granted or rejected request should be logged and whether the profile audit queue is below its configured max. If logging is enabled, it builds the text via `tomoyo_init_log()`, allocates a `tomoyo_log`, accounts memory quota, appends to the queue under `tomoyo_log_lock`, and wakes readers.

`tomoyo_init_log()` first prints the common header. For exec requests it obtains the executable realpath and argv/envp dump; for symlink operations it records the symlink target. It then emits the header, optional exec or symlink block, the current domain name, and the caller-supplied formatted details. `tomoyo_read_log()` supports one queued record per read buffer: it removes the oldest log from the list, decrements audit memory accounting, and hands ownership of the log string to the securityfs read buffer. `tomoyo_poll_log()` reports readable status if the queue is non-empty before or after wait-queue registration.

## State and persistence behavior

Audit logs are in-memory queue entries only. They persist until read from TOMOYO securityfs or dropped due to max audit log count or memory quota. Memory accounting uses `tomoyo_memory_used[TOMOYO_MEMORY_AUDIT]` and `tomoyo_memory_quota[TOMOYO_MEMORY_AUDIT]`; profile count limiting uses `TOMOYO_PREF_MAX_AUDIT_LOG`. `tomoyo_print_bprm()` uses a bounded 8 KiB buffer and truncates argv/envp with an ellipsis marker when near capacity.

## Dependencies and integration points

This file depends on TOMOYO policy/profile structures and helpers from `common.h`, including profile lookup, config arrays, condition grant-log settings, object attribute collection, time conversion, page dumping, realpath resolution, memory accounting, and mode/category keyword tables. It uses kernel wait queues, spinlocks, linked lists, poll flags, process credentials, namespace uid/gid conversion through `init_user_ns`, and `linux_binprm` inspection. It is consumed by the broader TOMOYO permission-checking code whenever a decision needs audit emission.

## Risks and test signals

Risks include log truncation around argv/envp boundaries, allocation failure under `GFP_NOFS`, buffer sizing mistakes from caller-provided format lengths, dropped logs when profile or memory quota is reached, stale object metadata if validation is skipped, and concurrency around queue count and memory accounting. Useful tests cover granted/rejected audit mode selection, per-ACL grant-log overrides, max audit log count, audit memory quota exhaustion, exec log formatting with long argv/envp and page dump failures, symlink target logging, object stat fields for regular files, directories, device nodes, and FIFOs, FIFO ordering on reads, poll wakeups, and behavior before `tomoyo_policy_loaded` becomes true.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/audit.c -->
