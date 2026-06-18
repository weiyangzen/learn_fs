# sources/distributed-fs/ceph-client/kernel/auditfilter.c

## Purpose
`auditfilter.c` implements audit rule parsing, validation, storage, listing, matching, and LSM-rule refresh. It converts userspace `struct audit_rule_data` messages into internal `struct audit_entry`/`audit_krule` objects, maintains RCU-protected filter lists and inode hash lists, and evaluates non-syscall audit filters such as user, exclude, filesystem, subject, and executable filters.

## Important APIs, types, and functions
Global state includes `audit_filter_list[]` for fast RCU filtering, `audit_rules_list[]` for ordered rule listing, and `audit_filter_mutex` for writers/blocking readers. Rule lifetime helpers include `audit_init_entry()`, `audit_free_lsm_field()`, `audit_free_rule()`, `audit_free_rule_rcu()`, and `audit_dupe_rule()`.

Parsing and serialization are handled by `audit_unpack_string()`, `audit_to_entry_common()`, `audit_field_valid()`, `audit_data_to_entry()`, `audit_pack_string()`, and `audit_krule_to_data()`. Rule operations are `audit_add_rule()`, `audit_del_rule()`, `audit_rule_change()`, `audit_list_rules_send()`, and `audit_list_rules()`. Matching helpers include `audit_register_class()`, `audit_match_class()`, `audit_comparator()`, UID/GID comparators, `parent_len()`, `audit_compare_dname_path()`, and `audit_filter()`. LSM policy reload support is in `audit_update_lsm_rules()` and `update_lsm_rule()`.

## Control flow
Netlink rule add/delete from `audit.c` calls `audit_rule_change()`. The payload is parsed by `audit_data_to_entry()`, which validates list/action/field count, expands syscall classes into masks, validates field/operator combinations, translates UID/GID values into kernel IDs, initializes LSM rules, creates watch/tree/exe helper objects, and records string buffer lengths. Add operations take `audit_filter_mutex`, reject duplicates using `audit_find_rule()`, attach watch/tree state if present, assign priority for exit/uring lists, and insert into both listing and filtering lists with RCU-safe list operations. Delete operations find the matching rule, remove watch/tree/exe attachments, update audit rule counters, remove list entries, and RCU-free the old object.

Rule listing takes the mutex, serializes each internal rule back to `audit_rule_data`, queues multipart netlink replies, and sends them from a helper kthread to avoid deadlocking auditctl. `audit_filter()` runs under RCU, evaluates fields against current task state, message type, LSM subject data, and executable mark data, and returns whether the event should be audited.

## State and persistence behavior
Rules live in memory in ordered per-list `audit_rules_list` and RCU-visible filtering lists. Inode/watch rules may live in `audit_inode_hash` buckets rather than the generic list. String fields, LSM opaque rules, watch/tree/exe marks, filter keys, syscall masks, and priorities are part of the rule state. Rule state is not durable across reboot unless userspace reloads it.

## Dependencies and integration points
This file integrates with audit netlink control, `audit.c` logging/replies, syscall audit counters under `CONFIG_AUDITSYSCALL`, LSM audit rule initialization/matching, fsnotify watch/tree/exe helpers, UID/GID namespace conversion, RCU, mutexes, and audit UAPI constants.

## Risks and invariants
Validation is security-sensitive: unsupported field/list/operator combinations must be rejected before insertion. RCU-visible rule structures must never be mutated in place; updates duplicate and replace. Watch/tree/exe setup has cross-file cleanup requirements on parse/add/delete failure. `audit_filter_mutex` synchronizes writers, while RCU readers can run concurrently, so list deletion must use `list_del_rcu()` and delayed freeing. LSM rules may be temporarily invalid across policy changes and are refreshed by duplication.

## Test signals
Use auditctl rule add/delete/list tests across all filter lists, duplicate detection, invalid field/operator/list combinations, UID/GID namespace values, syscall class expansion, filter key serialization, LSM subject/object rules before and after policy reload, watch/tree/exe rules, and concurrent filtering while replacing rules. Fault injection for allocations and LSM rule init should verify cleanup.
