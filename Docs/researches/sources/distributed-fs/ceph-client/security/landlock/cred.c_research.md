# sources/distributed-fs/ceph-client/security/landlock/cred.c

## Purpose

`cred.c` installs Landlock credential LSM hooks. It copies domain state across credential changes, releases domain references when credentials are freed, and resets audit execution tracking on exec.

## Important APIs, Types, and Functions

`hook_cred_transfer()` copies the Landlock credential blob and increments the domain reference. `hook_cred_prepare()` delegates to transfer during credential preparation. `hook_cred_free()` schedules deferred ruleset release. Under audit, `hook_bprm_creds_for_exec()` clears `domain_exec` for each execution. `landlock_add_cred_hooks()` registers the hook list.

## Control Flow

When credentials are prepared or transferred, Landlock pins the old domain and copies the blob into the new credentials. When credentials are freed, the domain is dropped through deferred freeing to avoid sleeping constraints. During exec credential setup, audit execution-origin bits are reset.

## State and Persistence Behavior

The credential blob persists with each `struct cred`. Domain pointers are reference-counted rulesets. Audit `domain_exec` is per-credential and reset by exec.

## Dependencies and Integration Points

The file integrates with LSM credential hooks, binary execution hooks, ruleset lifetime management, and `setup.c` hook registration.

## Risks and Test Signals

Reference leaks or missed increments can free active domains or leak rulesets. Exec reset affects audit filtering. Test with fork, exec, setuid, thread credential changes, domain dropping after process exit, and audit logs across exec.
