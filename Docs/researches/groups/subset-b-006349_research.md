# subset-b-006349 TOMOYO policy core research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/common.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/common.h -->
# sources/distributed-fs/ceph-client/security/tomoyo/common.h

## Purpose

`common.h` is the shared TOMOYO internal contract. It defines constants, enumerations, policy object layouts, request payloads, namespace/profile/domain state, securityfs I/O cursors, exported globals, function prototypes, reference helpers, and SRCU lock helpers used by all TOMOYO source files in this directory.

## Important APIs, types, and functions

The main enums define condition operands, path stat slots, profile modes, policy IDs, domain flags, group IDs, ACL entry types, path/network/mount operations, MAC indexes, MAC categories, policy stats, and preference indexes. `struct tomoyo_request_info` is the per-check object passed from LSM hooks into checkers and audit logic; its union carries operation-specific parameters for path, path2, mkdev, path-number, env, inet, unix, mount, and task checks. `struct tomoyo_path_info`, `tomoyo_name_union`, `tomoyo_number_union`, and `tomoyo_ipaddr_union` are the reusable pattern/range/group operands.

Persistent policy layouts include `tomoyo_domain_info`, `tomoyo_policy_namespace`, `tomoyo_profile`, `tomoyo_acl_info`, `tomoyo_path_acl`, `tomoyo_path_number_acl`, `tomoyo_mkdev_acl`, `tomoyo_path2_acl`, `tomoyo_mount_acl`, `tomoyo_env_acl`, network ACLs, `tomoyo_group`, transition controls, aggregators, managers, and packed `tomoyo_condition`. Runtime-only support types include `tomoyo_execve`, `tomoyo_page_dump`, `tomoyo_obj_info`, and `tomoyo_io_buffer`. Inline helpers include `tomoyo_read_lock()`, `tomoyo_read_unlock()`, PID helpers, `tomoyo_pathcmp()`, reference drops for names/conditions/groups, `tomoyo_task()`, union equality helpers, `tomoyo_current_namespace()`, and `list_for_each_cookie()`.

## Control flow

The header does not implement policy decisions, but it shapes all control flow. Checkers initialize `tomoyo_request_info`, fill the operation-specific union, set `param_type`, call `tomoyo_check_acl()`, and audit through `tomoyo_supervisor()`. Writers fill `tomoyo_acl_param` with a mutable policy line, target list, namespace, and delete flag, then call parser/update functions. Readers store resumable list cursors in `tomoyo_io_buffer::r` and rely on `list_for_each_cookie()` with SRCU dereference to survive partial reads.

## State and persistence behavior

The header declares global policy state: `tomoyo_policy_loaded`, `tomoyo_enabled`, condition/domain/name/namespace lists, `tomoyo_policy_lock`, `tomoyo_ss`, kernel domain/namespace objects, memory quotas/usage, and LSM blob sizes. It models lifecycle with `tomoyo_acl_head::is_deleted`, `TOMOYO_GC_IN_PROGRESS`, and shared-object reference counts. Names, groups, and conditions are interned/shared by reference count; domain objects are also referenced from task security blobs.

## Dependencies and integration points

`common.h` includes Linux filesystem, credential, binfmt, networking, mount, list, poll, LSM, and socket headers. It is included by TOMOYO implementation files and is the bridge to LSM hooks in `tomoyo.c`, audit/securityfs helpers, realpath utilities, and network/file/mount/env/domain enforcement. The `tomoyo_task()` inline depends on `tomoyo_blob_sizes.lbs_task` matching LSM blob registration.

## Risks

Because this file fixes enum ordering and packed object layout, changes can break policy text compatibility, profile index mapping, condition binary layout, GC cleanup, and audit rendering. The variable-size `tomoyo_condition` tail layout is especially sensitive to count and alignment mistakes. Request union fields are reused by many checkers; a wrong `param_type` or uninitialized union member can produce incorrect access decisions. Inline reference drops must stay paired with parser/update ownership rules.

## Test signals

Compile coverage across all TOMOYO files is the first signal because most contracts are type-level. Runtime tests should exercise every ACL type, condition operand, profile mode, namespace, group type, securityfs interface, task-domain transition, and GC deletion path. Static analysis should focus on packed struct access, reference ownership, SRCU annotations, and `tomoyo_task()` blob offset assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/condition.c -->
# sources/distributed-fs/ceph-client/security/tomoyo/condition.c

## Purpose

`condition.c` parses and evaluates optional TOMOYO ACL conditions. Conditions can constrain access by task credentials and PIDs, exec argc/envc, executable realpath, symlink target, path inode attributes, file type and mode bits, numeric ranges/groups, name groups, and specific `exec.argv[]`/`exec.envp[]` entries.

## Important APIs, types, and functions

`tomoyo_get_condition()` parses the condition suffix of a policy line into a shared packed `struct tomoyo_condition`. `tomoyo_condition()` evaluates a condition against a `struct tomoyo_request_info`. `tomoyo_get_attributes()` lazily snapshots inode metadata into `struct tomoyo_obj_info`. `tomoyo_del_condition()` is implemented in `gc.c`, but this file owns the allocation layout that it later frees. The global `tomoyo_condition_list` interns duplicate condition objects.

Important internal helpers include `tomoyo_scan_bprm()` for walking `linux_binprm` argv/env pages, `tomoyo_argv()` and `tomoyo_envp()` for pattern checks, `tomoyo_scan_exec_realpath()`, quoted-name parsers, argv/envp condition parsers, `tomoyo_condition_type()`, `tomoyo_commit_condition()`, and `tomoyo_get_transit_preference()` for optional exec domain transition preferences.

## Control flow

Parsing is a two-pass process. The first dry run scans space-delimited `left[!]=right` atoms, counts condition elements and trailing arrays, recognizes `grant_log`, argv/envp clauses, numeric literals, name unions, and transition preferences. It then allocates one `struct tomoyo_condition` large enough for `condition[]`, number unions, name unions, argv entries, and envp entries, restores delimiters overwritten during the dry run, and reruns to populate the packed tail. `tomoyo_commit_condition()` merges identical conditions under `tomoyo_policy_lock` and increments shared references.

Evaluation iterates each condition element. String conditions compare `exec.realpath` or `symlink.target` against a name union. Numeric conditions compute current task IDs/PIDs, binprm argc/envc, constants for file type/mode, or lazily fetched inode stats, then compare ranges, number groups, or permission-bit intersections. `exec.argv[]` and `exec.envp[]` conditions are deferred until the numeric/string pass succeeds; `tomoyo_scan_bprm()` then reads argument pages from `linux_binprm` and verifies all required positive/negative matches.

## State and persistence behavior

Conditions are persistent shared policy objects with atomic user counts. A condition may hold references to interned names, groups, and optional transition preference strings. `tomoyo_get_attributes()` caches path and parent stat data in the request-local `tomoyo_obj_info`, setting `validate_done` and `stat_valid[]`. `tomoyo_scan_bprm()` uses request-local page dumps and temporary buffers without persisting scanned argv/env data.

## Dependencies and integration points

The parser depends on `tomoyo_parse_number_union()`, `tomoyo_parse_name_union()`, `tomoyo_get_name()`, `tomoyo_get_domainname()`, `tomoyo_correct_word()`, `tomoyo_correct_path()`, and domain update code. Evaluation depends on Linux credential helpers, PID helpers, inode/dentry access, `tomoyo_realpath_from_path()`, group and name matching from `file.c`/`group.c`, and `tomoyo_dump_page()` from `domain.c`. `tomoyo_update_domain()` calls this parser when a policy line has remaining condition text.

## Risks

The packed allocation layout is fragile: count mismatches or restoration mistakes can corrupt subsequent arrays or leak references. The parser modifies the input line in place and relies on strict token grammar, so userspace grammar drift can cause rejection. Exec argument scanning truncates at `TOMOYO_EXEC_TMPSIZE - 10` and escapes bytes into TOMOYO string syntax; tests must cover long and non-printable values. Attribute conditions can fail closed when a relevant path/object is absent. Operator precedence in expressions such as symlink target comparison should be reviewed carefully because boolean negation around pointer-returning match helpers is easy to misread.

## Test signals

Strong tests include parse/render/evaluate round trips for each condition keyword, equality and deduplication tests, `grant_log` and transition preference parsing, argv/envp positive and negative matches, absent argv/envp behavior, inode metadata conditions for files/directories/devices/parents, bit-permission comparisons, numeric range overlap and number-group checks, and exec realpath/symlink target conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/condition.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/domain.c -->
# sources/distributed-fs/ceph-client/security/tomoyo/domain.c

## Purpose

`domain.c` owns TOMOYO domain lifecycle, generic policy insertion/deletion, ACL matching across domains and ACL groups, transition controls, aggregators, namespace creation, exec-time domain transition, and exec environment enforcement. It is the main bridge between `bprm_check_security` style hooks and persistent TOMOYO domain state.

## Important APIs, types, and functions

`tomoyo_update_policy()` updates exception/global policy lists. `tomoyo_update_domain()` updates domain ACL lists and numbered ACL groups, including condition parsing and duplicate merging. `tomoyo_check_acl()` scans the current domain and enabled ACL groups for a matching ACL. `tomoyo_assign_namespace()`, `tomoyo_assign_domain()`, and `tomoyo_find_next_domain()` implement namespace/domain creation and exec transition. `tomoyo_write_transition_control()` and `tomoyo_write_aggregator()` parse exception-policy directives. `tomoyo_dump_page()` reads argv/env pages from a `linux_binprm`.

Important globals are `tomoyo_kernel_domain` and `tomoyo_domain_list`. Internal helpers include transition duplicate checks, transition scanning, `tomoyo_transition_type()`, `tomoyo_namespace_jump()`, `tomoyo_environ()`, and `tomoyo_last_word()`.

## Control flow

Policy updates lock `tomoyo_policy_lock`, scan for non-GC duplicate entries, toggle `is_deleted` on delete/undelete, optionally merge permission bitmasks, and commit new objects through `tomoyo_commit_ok()`. Domain ACL updates first parse an optional condition and reject transition preferences unless the entry is exactly a `file execute` ACL.

`tomoyo_check_acl()` scans the domain ACL list for matching `param_type`, type-specific predicate success, and condition success. If no domain ACL matches, it walks each enabled `use_group` bit and retries against namespace ACL groups.

At exec time, `tomoyo_find_next_domain()` builds a `tomoyo_execve` request, resolves the executable name, applies matching aggregator rules, checks execute permission, records any matched transition preference, calculates the destination domain using explicit preferences or transition control policy, assigns or finds that domain, updates the current task TOMOYO blob, and then checks environment variable permissions in the new domain. Transition failures can reject exec in enforcing mode or when an explicit transition preference requires a defined target; otherwise they log `transition_failed` once per old domain.

## State and persistence behavior

Domains are persistent list entries with ACL lists, namespace pointers, profile IDs, ACL group bitsets, deletion flags, transition failure flags, and task reference counts. Namespaces persist profile pointers, policy lists, group lists, and ACL group lists. `tomoyo_find_next_domain()` mutates the current task security blob by saving `old_domain_info`, setting `domain_info`, and incrementing the new domain reference count. Aggregators and transition controls are persistent namespace policy entries.

## Dependencies and integration points

This file depends on `common.h`, `condition.c`, `file.c`, `environ.c`, `memory.c`, `realpath.c`, `util.c`, and audit/stat helpers. It integrates with Linux exec internals through `struct linux_binprm`, `get_user_pages_remote()`, `kmap_local_page()`, and `put_page()`. The LSM hook wrapper in `tomoyo.c` calls `tomoyo_find_next_domain()` on exec.

## Risks

Exec transition semantics are security-critical and depend on subtle ordering: aggregator rewrite before execute check, matched wildcard path reuse for domain name construction, explicit transition preference handling, and namespace jump restrictions. Incorrect reference accounting for task domain pointers can block GC or free active domains. `tomoyo_update_domain()` must always release parsed conditions and operand references on both success and failure. `tomoyo_environ()` parses environment pages manually and can fail open outside enforcing mode, so policy authors need accurate mode coverage.

## Test signals

Tests should cover domain creation, deletion, undelete, duplicate ACL merging, ACL group fallback, transition controls (`reset`, `initialize`, `keep`, negative forms), explicit transition preferences (`keep`, `child`, `parent`, absolute namespace), aggregator rewrites, undefined target behavior in each profile mode, namespace creation boundaries, environment checks during exec, and MMU/non-MMU `tomoyo_dump_page()` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/domain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/environ.c -->
# sources/distributed-fs/ceph-client/security/tomoyo/environ.c

## Purpose

`environ.c` implements TOMOYO's `misc env` ACL type. It checks whether an environment variable name is permitted during exec and parses/writes environment ACL entries in domain policy.

## Important APIs, types, and functions

`tomoyo_env_perm()` is the enforcement entry point. `tomoyo_write_misc()` dispatches `misc env` policy writes. Internally, `tomoyo_check_env_acl()` matches a request environment name against a `struct tomoyo_env_acl`, `tomoyo_audit_env_log()` emits the audit/supervisor line, `tomoyo_same_env_acl()` detects duplicate entries, and `tomoyo_write_env()` parses and stores an ACL.

## Control flow

`tomoyo_env_perm()` ignores empty names, fills a temporary `tomoyo_path_info`, sets `r->param_type` to `TOMOYO_TYPE_ENV_ACL`, and loops over `tomoyo_check_acl()` plus `tomoyo_supervisor()` until the supervisor no longer returns `TOMOYO_RETRY_REQUEST`. `tomoyo_write_misc()` recognizes the `env ` subkeyword and delegates to `tomoyo_write_env()`, which rejects invalid words and names containing `=`, interns the name, updates the target domain ACL list, and releases the temporary reference.

## State and persistence behavior

Environment ACLs are stored as `struct tomoyo_env_acl` entries in a domain or ACL group list. Each entry holds a reference to an interned `tomoyo_path_info` name. Enforcement state is request-local; it reuses the request object prepared by exec-domain code.

## Dependencies and integration points

`domain.c` calls `tomoyo_env_perm()` from `tomoyo_environ()` while scanning `linux_binprm` environment strings after exec domain selection. The code depends on common ACL scanning, pattern matching, string validation, name interning, domain update, and supervisor/audit handling.

## Risks

Environment policy matches only variable names, not values. A policy writer may assume value filtering exists because condition support can inspect `exec.envp[]`, but `misc env` itself gates names. Manual env parsing in `domain.c` replaces `=` with NUL before calling this function; malformed env strings without names are skipped by the early empty-name check. Retry loops rely on `tomoyo_supervisor()` eventually returning a non-retry result.

## Test signals

Useful tests include parsing valid/invalid `misc env` entries, rejecting names containing `=`, wildcard name matching, duplicate insertion/deletion, enforcing/permissive/learning behavior for denied environment names, and exec tests combining `misc env` ACLs with `exec.envp[]` conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/environ.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/file.c -->
# sources/distributed-fs/ceph-client/security/tomoyo/file.c

## Purpose

`file.c` implements TOMOYO file-related ACL parsing and enforcement for path operations, two-path operations, path-plus-number operations, device node creation, and mount ACL storage. It translates Linux VFS hook inputs into TOMOYO policy tokens and request parameters, checks matching ACLs, and audits through the common supervisor path.

## Important APIs, types, and functions

Exported enforcement functions include `tomoyo_execute_permission()`, `tomoyo_check_open_permission()`, `tomoyo_path_perm()`, `tomoyo_path_number_perm()`, `tomoyo_mkdev_perm()`, and `tomoyo_path2_perm()`. `tomoyo_write_file()` parses file policy lines and dispatches to ACL update helpers. Shared operand helpers include `tomoyo_put_name_union()`, `tomoyo_compare_name_union()`, `tomoyo_put_number_union()`, and `tomoyo_compare_number_union()`.

The file defines operation-to-MAC mapping arrays: internal `tomoyo_p2mac` plus exported `tomoyo_pnnn2mac`, `tomoyo_pp2mac`, and `tomoyo_pn2mac`. Internal checkers include `tomoyo_check_path_acl()`, `tomoyo_check_path_number_acl()`, `tomoyo_check_path2_acl()`, and `tomoyo_check_mkdev_acl()`. Update helpers parse name/number unions, detect duplicates, and merge permission bitmasks for ACLs with the same operands.

## Control flow

For enforcement, each public checker initializes `tomoyo_request_info`, acquires `tomoyo_read_lock()`, resolves one or two paths with `tomoyo_realpath_from_path()`, normalizes directory names with trailing slash where TOMOYO policy expects directories, fills `tomoyo_obj_info` for condition evaluation, sets the appropriate `param_type`, calls `tomoyo_check_acl()`, and audits through a type-specific audit helper. Non-enforcing modes generally force the final return to success after logging/learning.

`tomoyo_execute_permission()` is special: it checks execute ACLs even when the execute profile mode is disabled so that a matched `file execute` condition can still provide a domain transition preference. Write parsing first tries single-path operation names, then two-path MAC names, path-number MAC names, mkdev MAC names, and finally mount.

## State and persistence behavior

File ACLs persist in domain ACL lists or namespace ACL groups as `tomoyo_path_acl`, `tomoyo_path2_acl`, `tomoyo_path_number_acl`, `tomoyo_mkdev_acl`, and `tomoyo_mount_acl` objects. These entries hold references to interned names, groups, and number unions. Enforcement allocates temporary encoded realpath strings and frees them before returning; matched execute ACL state is stored in the request so `domain.c` can reuse wildcard policy names for transition construction.

## Dependencies and integration points

This file depends on realpath encoding, TOMOYO pattern matching, name/number/group parsing from `util.c`/`group.c`, domain ACL update and scanning from `domain.c`, condition evaluation, and common audit/profile mode handling. LSM hook wrappers in `tomoyo.c` call these functions for open, getattr, truncate, unlink, mkdir, mknod, symlink, rename, link, chmod/chown/chgrp, ioctl-like number checks, chroot, unmount, and pivot root paths. Mount enforcement runtime is implemented in `mount.c`, while mount ACL parsing/storage is here.

## Risks

Path canonicalization and trailing slash rules are critical because policy matching is string based. Directory operations that forget `tomoyo_add_slash()` can miss intended directory ACLs. Permission-bit merging must be atomic enough for lockless readers; this file uses `READ_ONCE()`/`WRITE_ONCE()` while updates hold the policy mutex. Execute checks affect domain transitions beyond simple allow/deny. Non-enforcing modes returning success after errors can hide policy/parser issues unless audit signals are inspected.

## Test signals

Tests should cover every file operation token, slash normalization for directories, open read/write/append combinations, symlink target conditions, mknod major/minor/mode checks, chmod/chown/chgrp/ioctl radix rendering, rename/link/pivot-root directory handling, duplicate ACL merge/delete behavior, path groups and number groups, wildcard execute transition matching, and enforcement-mode return differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/gc.c -->
# sources/distributed-fs/ceph-client/security/tomoyo/gc.c

## Purpose

`gc.c` reclaims deleted TOMOYO policy objects and closed securityfs I/O buffers. It implements deferred cleanup for entries protected by SRCU readers, active securityfs cursors, shared reference counts, and task security blobs.

## Important APIs, types, and functions

`tomoyo_notify_gc()` is the exported registration/unregistration hook used by securityfs open/close paths. `tomoyo_del_condition()` releases all references held by a packed `struct tomoyo_condition`. Internal cleanup helpers release object-specific references for transition controls, aggregators, managers, ACLs, domains, names, groups, and group members. `tomoyo_try_to_gc()` is the central removal/reinject/free path. `tomoyo_collect_entry()` scans all domains, namespaces, conditions, groups, and interned names. `tomoyo_gc_thread()` runs collection from a kernel thread.

## Control flow

Policy deletion only marks entries as deleted. The collector later takes `tomoyo_policy_lock`, finds deleted or unreferenced objects, marks them `TOMOYO_GC_IN_PROGRESS`, unlinks them, drops the policy lock, waits for an SRCU grace period, checks whether securityfs readers/writers still hold list cursors or queued string pointers, releases object-specific references, then frees memory and subtracts from TOMOYO policy memory usage. If an entry is still visible to an I/O buffer or active task reference, it is reinserted at its previous list position.

`tomoyo_notify_gc()` adds open `tomoyo_io_buffer` objects to a protected list with a users count. On close it either frees the buffer immediately or, if writes occurred and cleanup may be needed, starts `tomoyo_gc_thread()`. The GC thread serializes itself with `tomoyo_gc_mutex`, collects policy entries, then frees any I/O buffers whose temporary users count reached zero.

## State and persistence behavior

The file maintains `tomoyo_io_buffer_list` under `tomoyo_io_buffer_list_lock`. It mutates global policy lists, shared reference counts, `is_deleted` markers, `TOMOYO_GC_IN_PROGRESS` states, and `tomoyo_memory_used[TOMOYO_MEMORY_POLICY]`. It intentionally delays freeing objects that remain reachable through securityfs read cursors, write-domain selections, queued read strings, condition/group/name references, or domain task references.

## Dependencies and integration points

GC relies on the object layouts declared in `common.h`, reference drop helpers from other files, `tomoyo_policy_lock`, `tomoyo_ss`, namespace/domain/name/group/condition lists, and Linux kthreads, spinlocks, mutexes, and SRCU. `common.c` calls `tomoyo_notify_gc()` when opening and closing control files. Update paths in `domain.c` and related parsers mark entries deleted rather than freeing directly.

## Risks

The main risk is use-after-free through partial securityfs reads, active write selections, or task domain pointers. `tomoyo_struct_used_by_io_buffer()` inspects `&head->w.domain->list`; if a writer buffer ever has a NULL domain while this expression is evaluated, that path must be protected by call context or it could fault. Reinjecting after failed reclamation depends on the saved list linkage remaining valid enough for `list_add_rcu(element, element->prev)`. Reference drops must match parser ownership exactly or GC can leak shared names/groups/conditions.

## Test signals

Useful tests include deleting policy while a reader is paused mid-read, deleting a selected domain while a writer is open, closing writers to trigger GC, deleting domains still referenced by tasks, removing group members and then groups, condition dedup/refcount release, repeated create/delete cycles with memory usage returning to baseline, and KASAN/RCU torture runs for concurrent readers and GC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/gc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/group.c -->
# sources/distributed-fs/ceph-client/security/tomoyo/group.c

## Purpose

`group.c` implements TOMOYO path, number, and address group member policy. Groups let ACLs refer to reusable sets through `@group` operands instead of duplicating many path patterns, numeric ranges, or IP address ranges.

## Important APIs, types, and functions

`tomoyo_write_group()` parses and updates `path_group`, `number_group`, and `address_group` directives. `tomoyo_path_matches_group()`, `tomoyo_number_matches_group()`, and `tomoyo_address_matches_group()` are exported matchers used by file, network, and condition checks. Duplicate helpers compare path group names by interned pointer, number groups by full `tomoyo_number_union`, and address groups by `tomoyo_same_ipaddr_union()`.

## Control flow

Policy writing first obtains or creates the named `struct tomoyo_group` through `tomoyo_get_group()`, switches `param->list` to the group's member list, parses the member appropriate for the group type, then updates the member list via `tomoyo_update_policy()`. Matching iterates active group members under SRCU, skips deleted entries, and returns on the first pattern/range match.

## State and persistence behavior

Groups persist under `ns->group_list[type]` and each group owns a `member_list`. Group objects and group names are reference-counted shared objects. Path members hold interned path names, number members hold numeric range unions, and address members hold IPv4/IPv6 range unions. Deleted members are marked and later reclaimed by `gc.c`.

## Dependencies and integration points

The file depends on `tomoyo_get_group()` from `memory.c`, `tomoyo_update_policy()` from `domain.c`, name/number/IP parsers, path pattern matching, IP comparison helpers, and SRCU list traversal. File ACLs use path and number groups, network ACLs use address groups and port number groups, and conditions can compare against number/name groups.

## Risks

Group matching is linear in group size, so very large groups can affect hot permission checks. Number group writing intentionally rejects `@` nested groups; address group writing also rejects group indirection, limiting recursion but requiring clear userspace diagnostics. Address comparisons use `memcmp()` over big-endian byte ranges, so parser correctness and IPv4-vs-IPv6 flags are essential. Path group matching returns the matched member path, which can feed wildcard execute transition behavior.

## Test signals

Tests should include member insertion/deletion, duplicate detection, path wildcard matches, numeric overlap edge cases, IPv4 and IPv6 range boundaries, group references from file/network/condition ACLs, deletion while ACLs still reference groups, and performance checks for large groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/group.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/load_policy.c -->
# sources/distributed-fs/ceph-client/security/tomoyo/load_policy.c

## Purpose

`load_policy.c` optionally invokes the TOMOYO userspace policy loader during early boot. When userspace loading is enabled, it waits until a configured activation trigger program is executed, runs the configured loader, and validates loaded profiles before MAC activation.

## Important APIs, types, and functions

`tomoyo_load_policy()` is the exported entry point. Boot parameters are parsed by `tomoyo_loader_setup()` for `TOMOYO_loader=` and `tomoyo_trigger_setup()` for `TOMOYO_trigger=`. `tomoyo_policy_loader_exists()` verifies the loader path with `kern_path()`. All code is compiled out when `CONFIG_SECURITY_TOMOYO_OMIT_USERSPACE_LOADER` is set.

## Control flow

`tomoyo_load_policy()` returns immediately if policy is already loaded, if it has already attempted loading, if the current executable is not the activation trigger, or if the loader path does not exist. On the first matching trigger it marks `done`, logs the loader call, builds a minimal argv/envp, invokes `call_usermodehelper(..., UMH_WAIT_PROC)`, then calls `tomoyo_check_profile()` to validate and activate policy.

## State and persistence behavior

The file stores static loader and trigger path pointers populated from boot parameters or Kconfig defaults. A static `done` flag prevents repeated loader invocation. It mutates global policy activation indirectly through `tomoyo_check_profile()`, which sets `tomoyo_policy_loaded` after validating profiles.

## Dependencies and integration points

The file depends on Kconfig symbols `CONFIG_SECURITY_TOMOYO_POLICY_LOADER` and `CONFIG_SECURITY_TOMOYO_ACTIVATION_TRIGGER`, kernel path lookup, `call_usermodehelper`, and `tomoyo_check_profile()`. It is invoked from exec-domain flow when an executable name is available for trigger comparison.

## Risks

If the trigger path does not match the resolved executable name used by callers, policy loading never runs. If the loader is absent, TOMOYO logs and does not activate MAC through this path. The `done` flag is set before the helper result is checked, so a failed helper invocation is not retried. Boot environments without `/sbin`-style paths or with custom init systems need correct kernel parameters.

## Test signals

Tests should cover default and boot-parameter loader/trigger paths, missing loader behavior, single invocation despite multiple trigger execs, helper failure handling, `CONFIG_SECURITY_TOMOYO_OMIT_USERSPACE_LOADER` builds, and successful loader-to-profile-validation activation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/load_policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/memory.c -->
# sources/distributed-fs/ceph-client/security/tomoyo/memory.c

## Purpose

`memory.c` provides TOMOYO policy memory accounting, quota checks, allocation commit helpers, group object creation, interned string storage, and initial kernel namespace/domain setup.

## Important APIs, types, and functions

`tomoyo_warn_oom()` logs quota/allocation failures and panics if MAC initialization has not completed. `tomoyo_memory_ok()` charges allocated policy memory against `tomoyo_memory_quota[TOMOYO_MEMORY_POLICY]`. `tomoyo_commit_ok()` allocates and copies committed policy objects. `tomoyo_get_group()` finds or creates named group containers. `tomoyo_get_name()` interns strings as shared `struct tomoyo_name` entries. `tomoyo_mm_init()` initializes name hash buckets, the kernel namespace, and the initial `<kernel>` domain.

## Control flow

Most callers allocate a temporary stack object, then call `tomoyo_commit_ok()` while holding `tomoyo_policy_lock`; successful commit copies the object to heap storage, zeroes the source object to transfer references, and returns the heap pointer. `tomoyo_get_name()` hashes the string, searches the intern table under the policy mutex, increments the users count on a live match, or allocates and initializes a new `tomoyo_name`. `tomoyo_get_group()` similarly interns group containers by group name within a namespace/type list.

## State and persistence behavior

The file defines `tomoyo_memory_used[]`, `tomoyo_memory_quota[]`, `tomoyo_name_list[]`, and `tomoyo_kernel_namespace`. It initializes `tomoyo_kernel_domain` fields declared in `domain.c`. Interned names and group containers are shared, reference-counted, and reclaimed later by GC when users drop to zero. Memory use is adjusted on allocation here and on free in `gc.c`.

## Dependencies and integration points

It depends on Linux slab `ksize()`, hashing, TOMOYO path-info filling, namespace initialization from `common.c`, and global lists declared in `common.h`. Nearly every parser uses `tomoyo_get_name()`, and group policy uses `tomoyo_get_group()`. Boot initialization calls `tomoyo_mm_init()` before policy loading and enforcement.

## Risks

`tomoyo_memory_ok()` charges based on allocator size, not requested size, so quota behavior can vary by slab allocator. It assumes callers hold `tomoyo_policy_lock` where required. `tomoyo_commit_ok()` zeroes the source object on success to prevent double puts; callers must follow that ownership convention. If initialization fails before `tomoyo_policy_loaded`, `tomoyo_warn_oom()` can panic the system.

## Test signals

Signals include memory quota boundary tests, repeated intern/get/put/GC cycles, duplicate group and name reuse, allocation failure injection, boot initialization of `<kernel>` namespace/domain, and accounting returning to baseline after deleting policy objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/memory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/mount.c -->
# sources/distributed-fs/ceph-client/security/tomoyo/mount.c

## Purpose

`mount.c` implements runtime enforcement for TOMOYO `file mount` permissions. It normalizes Linux mount syscall variants into TOMOYO device, mount point, filesystem type, and flag operands, then checks those operands against mount ACLs stored by `file.c`.

## Important APIs, types, and functions

`tomoyo_mount_permission()` is the exported enforcement entry point. Internal `tomoyo_mount_acl()` performs path/type/device normalization and ACL checking. `tomoyo_check_mount_acl()` matches a request against `struct tomoyo_mount_acl`, and `tomoyo_audit_mount_log()` formats supervisor/audit output. The static `tomoyo_mounts[]` table maps special mount operations to policy pseudo-filesystem strings such as `--bind`, `--move`, `--remount`, and propagation changes.

## Control flow

`tomoyo_mount_permission()` initializes a request for `TOMOYO_MAC_FILE_MOUNT`, strips legacy `MS_MGC_*`, converts remount/bind/move/shared/private/slave/unbindable flag combinations into TOMOYO pseudo-types, validates incompatible propagation flag combinations, defaults missing type to `<NULL>`, then calls `tomoyo_mount_acl()` under `tomoyo_read_lock()`.

`tomoyo_mount_acl()` encodes the filesystem type, resolves the mount point realpath, determines whether the device operand is ignored, a directory path, a block device path, or a raw encoded string, fills request operands and object paths, calls `tomoyo_check_acl()`, and audits through `tomoyo_supervisor()` until no retry is requested. It releases encoded strings, filesystem type references, and `kern_path()` references before returning.

## State and persistence behavior

This file stores no persistent policy besides the static special-operation string table. Runtime state is request-local: encoded device/type strings, resolved mount point strings, optional `struct file_system_type` reference, optional `struct path` for the device/source, and `tomoyo_obj_info` paths for condition checks.

## Dependencies and integration points

It depends on Linux mount flags, `get_fs_type()`/`put_filesystem()`, `kern_path()`, path reference management, TOMOYO realpath/encoding helpers, number/name union matchers, domain ACL scanning, and supervisor/audit logic. `tomoyo.c` calls `tomoyo_mount_permission()` from the mount LSM hook. Mount ACL parsing is handled in `file.c` through `tomoyo_update_mount_acl()`.

## Risks

Special mount flag normalization must track kernel mount API semantics. Incorrect `need_dev` classification can require a device when policy should ignore it or ignore a device/source path that policy expects to constrain. Device path lookup with `LOOKUP_FOLLOW` may differ from userspace textual input, so policy must be based on resolved TOMOYO realpaths. Error handling before policy mode checks returns lookup/type errors such as `-ENODEV` or `-ENOENT`; enforcement mode handling is delegated through the supervisor result rather than a final non-enforcing override in this file.

## Test signals

Tests should cover normal block-device mounts, pseudo filesystems with no device, bind and move mounts with directory sources, remount and propagation operations, incompatible propagation flags, missing type/device behavior, flag masking, mount ACL group/range matching, condition checks on path1/path2 attributes, and enforcing/permissive/learning responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/tomoyo/mount.c -->
