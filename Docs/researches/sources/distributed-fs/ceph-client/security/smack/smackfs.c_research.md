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
