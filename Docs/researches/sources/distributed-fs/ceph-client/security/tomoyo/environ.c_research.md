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
