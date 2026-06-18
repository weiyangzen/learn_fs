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
