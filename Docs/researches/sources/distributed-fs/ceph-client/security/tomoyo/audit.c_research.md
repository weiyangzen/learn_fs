# sources/distributed-fs/ceph-client/security/tomoyo/audit.c

## Purpose

`audit.c` implements TOMOYO audit log formatting, filtering, storage, reading, and polling. It turns `tomoyo_request_info` decisions into structured text logs that include timestamps, task credentials, object metadata, exec arguments/environment, symlink targets, domain names, and operation-specific messages, then queues those logs for `/sys/kernel/security/tomoyo/audit`.

## Important APIs, types, and functions

The main exported functions are `tomoyo_init_log()`, `tomoyo_write_log2()`, `tomoyo_write_log()`, `tomoyo_read_log()`, and `tomoyo_poll_log()`. Formatting helpers include `tomoyo_print_bprm()` for `linux_binprm` argv/envp dumps, `tomoyo_filetype()` for mode-to-type keywords, and `tomoyo_print_header()` for the audit header. Queue state is represented by `struct tomoyo_log`, `tomoyo_log` list head, `tomoyo_log_lock`, `tomoyo_log_count`, and `tomoyo_log_wait`. Filtering is centralized in `tomoyo_get_audit()`, which consults policy loaded state, profile preferences, function/category config, default config, and per-ACL grant-log overrides.

## Control flow

Callers first compute the formatted operation-specific length and call `tomoyo_write_log()` or `tomoyo_write_log2()`. `tomoyo_write_log()` performs a sizing `vsnprintf()`, restarts the varargs, and delegates. `tomoyo_write_log2()` asks `tomoyo_get_audit()` whether the granted or rejected request should be logged and whether the profile audit queue is below its configured max. If logging is enabled, it builds the text via `tomoyo_init_log()`, allocates a `tomoyo_log`, accounts memory quota, appends to the queue under `tomoyo_log_lock`, and wakes readers.

`tomoyo_init_log()` first prints the common header. For exec requests it obtains the executable realpath and argv/envp dump; for symlink operations it records the symlink target. It then emits the header, optional exec or symlink block, the current domain name, and the caller-supplied formatted details. `tomoyo_read_log()` supports one queued record per read buffer: it removes the oldest log from the list, decrements audit memory accounting, and hands ownership of the log string to the securityfs read buffer. `tomoyo_poll_log()` reports readable status if the queue is non-empty before or after wait-queue registration.

## State and persistence behavior

Audit logs are in-memory queue entries only. They persist until read from TOMOYO securityfs or dropped due to max audit log count or memory quota. Memory accounting uses `tomoyo_memory_used[TOMOYO_MEMORY_AUDIT]` and `tomoyo_memory_quota[TOMOYO_MEMORY_AUDIT]`; profile count limiting uses `TOMOYO_PREF_MAX_AUDIT_LOG`. `tomoyo_print_bprm()` uses a bounded 8 KiB buffer and truncates argv/envp with an ellipsis marker when near capacity.

## Dependencies and integration points

This file depends on TOMOYO policy/profile structures and helpers from `common.h`, including profile lookup, config arrays, condition grant-log settings, object attribute collection, time conversion, page dumping, realpath resolution, memory accounting, and mode/category keyword tables. It uses kernel wait queues, spinlocks, linked lists, poll flags, process credentials, namespace uid/gid conversion through `init_user_ns`, and `linux_binprm` inspection. It is consumed by the broader TOMOYO permission-checking code whenever a decision needs audit emission.

## Risks and test signals

Risks include log truncation around argv/envp boundaries, allocation failure under `GFP_NOFS`, buffer sizing mistakes from caller-provided format lengths, dropped logs when profile or memory quota is reached, stale object metadata if validation is skipped, and concurrency around queue count and memory accounting. Useful tests cover granted/rejected audit mode selection, per-ACL grant-log overrides, max audit log count, audit memory quota exhaustion, exec log formatting with long argv/envp and page dump failures, symlink target logging, object stat fields for regular files, directories, device nodes, and FIFOs, FIFO ordering on reads, poll wakeups, and behavior before `tomoyo_policy_loaded` becomes true.
