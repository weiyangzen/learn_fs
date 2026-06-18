# sources/distributed-fs/ceph-client/include/uapi/linux/landlock.h

Purpose: defines the Landlock sandboxing userspace API: ruleset attributes, rule types, filesystem and network access-right bits, scoping bits, ruleset creation flags, and self-restriction logging/thread-synchronization flags.

Important APIs and types: `struct landlock_ruleset_attr` declares handled filesystem rights, handled network rights, and domain scopes. `LANDLOCK_CREATE_RULESET_VERSION` and `LANDLOCK_CREATE_RULESET_ERRATA` query ABI version and fixed errata. `LANDLOCK_RESTRICT_SELF_LOG_*` and `LANDLOCK_RESTRICT_SELF_TSYNC` tune audit logging and multithreaded enforcement. `enum landlock_rule_type`, `struct landlock_path_beneath_attr`, and `struct landlock_net_port_attr` describe path hierarchy and TCP-port rules. Access masks include `LANDLOCK_ACCESS_FS_*`, `LANDLOCK_ACCESS_NET_BIND_TCP`, `LANDLOCK_ACCESS_NET_CONNECT_TCP`, and `LANDLOCK_SCOPE_*`.

Control flow: userspace creates a ruleset with a declared set of handled rights, adds path or port rules, then restricts the current process or thread group. Later filesystem, TCP bind/connect, UNIX socket resolution, abstract socket, and signal checks are mediated by the resulting Landlock domain.

State and persistence: the header has no storage. Runtime policy is held by kernel Landlock domains attached to tasks and inherited across fork/exec according to Landlock rules. Policies are process state, not filesystem persistence.

Dependencies and integration points: depends on `linux/types.h`; integrates with Landlock syscalls, LSM hooks, audit logging, pathname resolution, TCP socket operations, UNIX sockets, signal delivery, `no_new_privs`, and thread synchronization.

Risks and test signals: risks include ABI-version mismatch, forgetting to set handled rights, special `LANDLOCK_ACCESS_FS_REFER` deny-by-default semantics, packed path rule layout, port 0 ephemeral behavior, and over/under-auditing. Test all ABI versions, unknown flag rejection, packed struct size, path rule inheritance, rename/link constraints, TCP bind/connect per port, scope denials, TSYNC behavior, and audit logging toggles.
