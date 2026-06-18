# sources/distributed-fs/ceph-client/kernel/audit.h

## Purpose
`audit.h` is the private kernel audit subsystem header. It defines internal audit state structures, especially the per-task `struct audit_context`, and declares cross-file interfaces between core audit logging, syscall auditing, rule filtering, fsnotify watches, tree watches, and audit netlink listing.

## Important APIs, types, and declarations
`enum audit_state` defines whether a task has no audit context, builds one lazily, or records always. `struct audit_entry` wraps `struct audit_krule` for filter lists and RCU freeing. `struct audit_names` stores path lookup/name data collected during audited syscalls, including inode/device, mode, ownership, object LSM properties, and file capabilities. `struct audit_context` is the large per-task syscall/io_uring record with state, timestamp, syscall arguments, return code, priority, names list, current working directory, auxiliary data, socket address, task credentials, target task info, tree references, and unions for IPC, mq, capset, mmap, openat2, execve, module, and time/NTP audit payloads.

The header declares helpers from `audit.c` (`audit_log_session_info`, `auditd_test_task`, `audit_make_reply`, `audit_panic`, `audit_ctl_lock`), from `auditfilter.c` (`audit_match_class`, comparators, path comparison, `audit_filter`, rule list/mutex symbols), and from watch/tree files (`audit_to_watch`, `audit_add_watch`, `audit_remove_watch_rule`, `audit_alloc_mark`, `audit_remove_mark`, `audit_make_tree`, `audit_add_tree_rule`, `audit_tag_tree`, `audit_kill_trees`). It provides disabled stubs when `CONFIG_AUDITSYSCALL` is off.

## Control flow and integration
The declarations encode the audit subsystem layering: core logging calls filters, filters own `audit_entry` lists and may attach watch/tree/exe objects, syscall auditing fills `audit_context`, and fsnotify callbacks update or remove rules asynchronously. Netlink list replies use `struct audit_netlink_list` and `audit_send_list_thread()`.

## State and persistence behavior
The header defines in-memory state only. Its structures determine what data can be persisted into emitted audit records. The `AUDIT_NAMES` preallocation is a performance contract: first path names are stored inline in the task context and overflow names are dynamically allocated and flagged with `should_free`.

## Dependencies and integration points
It depends on VFS path/inode types, `linux/audit.h` UAPI definitions, LSM properties, skbuffs, tty, POSIX mqueue UAPI, and `openat2` structures. It bridges files built under different configs, so its stubs must match real function signatures closely.

## Risks and invariants
`audit_context` layout and lifecycle are sensitive because many syscall audit paths fill it incrementally. `dummy` is required as the first field. Names must be managed through `names_list` rather than direct preallocated array access after setup. Stubs under `!CONFIG_AUDITSYSCALL` must fail safely without leaving callers believing watches or trees are active.

## Test signals
Compile-test audit on/off and auditsyscall on/off configurations. Runtime signals include syscall audit records with many path names, IPC/mqueue/capset/mmap/openat2/execve/time audit records, LSM context output, tree/watch rule addition, and rule-list netlink dumping.
