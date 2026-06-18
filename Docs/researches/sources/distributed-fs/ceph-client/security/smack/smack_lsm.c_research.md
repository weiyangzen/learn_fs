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
