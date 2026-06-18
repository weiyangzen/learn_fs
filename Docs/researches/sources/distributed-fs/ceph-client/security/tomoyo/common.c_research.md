# sources/distributed-fs/ceph-client/security/tomoyo/common.c

## Purpose

`common.c` is the central TOMOYO securityfs policy interface and policy-mode engine. It defines the user-visible keyword tables, profile configuration parser/printer, policy manager authorization, domain and exception policy read/write dispatch, supervisor query handling for enforcing-mode violations, statistics/quota interfaces, and built-in policy loading. It sits between the LSM hook-facing enforcement files and the `/sys/kernel/security/tomoyo/` control files created elsewhere.

## Important APIs, types, and functions

The file exports global keyword tables such as `tomoyo_mode`, `tomoyo_mac_keywords`, `tomoyo_condition_keyword`, `tomoyo_path_keyword`, `tomoyo_socket_keyword`, and `tomoyo_dif`; these tables are used both for parsing policy and rendering audit/securityfs output. `tomoyo_init_policy_namespace()` initializes namespace policy lists and registers namespaces. `tomoyo_profile()` and the internal `tomoyo_assign_profile()` manage per-namespace profiles. `tomoyo_open_control()`, `tomoyo_read_control()`, `tomoyo_write_control()`, `tomoyo_poll_control()`, and `tomoyo_close_control()` implement the generic control-file state machine. `tomoyo_supervisor()` is the common decision point for audit, learning, permissive, enforcing, and interactive query behavior. `tomoyo_update_stat()`, `tomoyo_check_profile()`, and `tomoyo_load_builtin_policy()` expose statistics and boot-time activation support.

Important internal helpers include `tomoyo_write_profile()`/`tomoyo_read_profile()`, `tomoyo_write_domain()`/`tomoyo_read_domain()`, `tomoyo_write_exception()`/`tomoyo_read_exception()`, `tomoyo_write_manager()`/`tomoyo_read_manager()`, `tomoyo_select_domain()`, `tomoyo_print_entry()`, and `tomoyo_print_condition()`. The local `struct tomoyo_query` backs `/sys/kernel/security/tomoyo/query` and records a domain, text query, serial, retry count, timer, and administrator answer.

## Control flow

Securityfs open selects an operation table based on the `enum tomoyo_securityfs_interface_index`: domain policy, exception policy, audit, process status, stat, version, profile, query, or manager. Reads take `head->io_sem`, acquire `tomoyo_read_lock()` over `tomoyo_ss`, flush queued strings, then call the selected reader until the userspace buffer fills or the namespace/domain/list cursor reaches EOF. Writes also hold `io_sem` and the SRCU read lock, collect complete newline-delimited lines into `head->write_buf`, normalize each line, handle `reset`, selection, and manager authorization, then call `tomoyo_parse_policy()` to route the line to the selected writer.

Domain policy writes either create/select/delete a domain, adjust `use_profile`, adjust `use_group`, toggle domain flags, or dispatch to `tomoyo_write_file()`, network writers, `tomoyo_write_misc()`, or task policy parsing. Exception policy writes dispatch to aggregators, transition controls, path/number/address groups, or numbered `acl_group` entries. Profile writes parse `PROFILE_VERSION`, `COMMENT`, `PREFERENCE`, and `CONFIG`/`CONFIG::category::operation` settings. Reads mirror these structures through resumable cursors stored in `struct tomoyo_io_buffer::r`.

`tomoyo_supervisor()` always writes an audit log first. If access was granted it returns success. For learning mode it may synthesize a new policy line through `tomoyo_add_entry()`. For permissive mode it logs and permits. For enforcing mode it returns `-EPERM` unless a userspace query observer exists; when observed, it enqueues a `struct tomoyo_query`, wakes query readers, waits up to roughly ten seconds for an `Aserial=answer` response, then returns allow, retry, or deny.

## State and persistence behavior

Most persistent policy state lives in lists owned by `struct tomoyo_policy_namespace`, domain ACL lists, shared name/condition/group objects, and profile pointers declared in `common.h` and allocated in other files. `common.c` mutates that state through update helpers while holding `tomoyo_policy_lock` indirectly. Per-open state is in `struct tomoyo_io_buffer`, including read/write buffers, cursors, selected namespace/domain, pending queued strings, and query index. The query list, query observer count, memory quotas, and stat counters are process-wide kernel state. Policy is not persisted to disk here; it is loaded from built-in arrays or from userspace via securityfs.

## Dependencies and integration points

This file depends heavily on `common.h`, `audit.c` for log read/write helpers, `domain.c` for domain and policy update helpers, `file.c`, `network.c`, `environ.c`, `group.c`, `condition.c`, `memory.c`, `securityfs_if.c`, and `util.c` parsing/matching helpers. It integrates with Linux primitives including `copy_to_user`, `get_user`, mutexes, spinlocks, wait queues, atomics, SRCU, RCU list iteration, process credential checks, `call_usermodehelper`-fed built-in policy, and securityfs file operations.

## Risks

The highest-risk areas are parser compatibility with TOMOYO userspace tools, lock ordering between `io_sem`, `tomoyo_policy_lock`, SRCU, and query spinlocks, cursor safety while GC reclaims policy nodes, and semantics of enforcing-mode query timeouts. `tomoyo_manager()` gates policy modification on root credentials, current executable path, and manager entries; mistakes here can either lock out legitimate policy tooling or permit unauthorized policy writes. Learning-mode policy synthesis rewrites volatile proc/socket/pipe path components, argv0, exec realpath, and symlink target strings; bugs here can generate overbroad policy or fail to learn useful rules.

## Test signals

Useful signals include securityfs read/write round trips for profile/domain/exception/manager/stat/query files, manager authorization tests for root and non-root paths/domains, policy reload tests with built-in and userspace loader paths, query-answer timeout/retry/allow/deny tests, learning-mode rule generation from representative audit lines, namespace-prefixed policy parsing, partial read cursor tests, and concurrency tests that read policy while deleting entries and running GC.
