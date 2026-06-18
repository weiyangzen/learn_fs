# sources/distributed-fs/ceph-client/kernel/seccomp.c

## Purpose

`kernel/seccomp.c` implements Linux secure computing mode. It supports strict mode, BPF-filter mode, filter chaining and thread synchronization, syscall-time filter evaluation, ptrace and user-notification actions, listener file descriptors, seccomp addfd injection, checkpoint/restore metadata access, audit logging, and sysctl controls for action logging.

## Important APIs, Types, and Functions

Key types include `struct seccomp_filter`, `struct notification`, `struct seccomp_knotif`, `struct seccomp_kaddfd`, and `struct action_cache`. `struct seccomp_filter` carries reference counts, user counts, a BPF program, previous filter pointer, optional notification state, a mutex, wait queue, logging flags, and cached always-allow bitmaps where supported.

Core filter APIs include `populate_seccomp_data()`, `seccomp_check_filter()`, `seccomp_prepare_filter()`, `seccomp_prepare_user_filter()`, `seccomp_attach_filter()`, `seccomp_run_filters()`, `seccomp_cache_prepare()`, `get_seccomp_filter()`, `seccomp_filter_release()`, `__put_seccomp_filter()`, and `__seccomp_filter_release()`. Mode and syscall APIs include `seccomp_assign_mode()`, `seccomp_set_mode_strict()`, `seccomp_set_mode_filter()`, `do_seccomp()`, `SYSCALL_DEFINE3(seccomp)`, `prctl_set_seccomp()`, `prctl_get_seccomp()`, `secure_computing_strict()`, and `__secure_computing()`.

User-notification APIs are implemented by `seccomp_do_user_notification()`, `init_listener()`, `seccomp_notify_recv()`, `seccomp_notify_send()`, `seccomp_notify_addfd()`, `seccomp_notify_id_valid()`, `seccomp_notify_poll()`, `seccomp_notify_release()`, and `seccomp_notify_detach()`. Sysctl/logging support centers on `seccomp_log()`, `seccomp_actions_logged_handler()`, and the `kernel/seccomp/actions_avail` and `actions_logged` tables.

## Control Flow

Filter installation starts through `seccomp()` or `prctl()`. Strict mode verifies the current task can transition, optionally disables TSC on architectures that support that hook, then assigns mode under `sighand->siglock`. Filter mode validates flags, copies and verifies the user BPF program, optionally creates a notification listener fd, optionally takes `cred_guard_mutex` for TSYNC, attaches the new filter under `siglock`, prepares the allow cache, and finally sets `SYSCALL_WORK_SECCOMP`.

At syscall entry, `__secure_computing()` checks checkpoint/restore suspension, fetches the syscall number, and dispatches by mode. Strict mode only allows read, write, exit, sigreturn, and uprobe exceptions. Filter mode populates `struct seccomp_data`, runs all filters from newest to oldest, and chooses the lowest action value ignoring data. `SECCOMP_RET_ERRNO` sets an errno return, `TRAP` rolls back registers and sends SIGSYS, `TRACE` notifies ptrace and may recheck if the tracer changes the syscall, `USER_NOTIF` blocks for a listener response, `LOG` audits and allows, `ALLOW` returns normally, and kill actions mark mode dead and deliver SIGSYS or exit.

Thread synchronization first validates every live sibling with `seccomp_can_sync_threads()`. `seccomp_sync_threads()` then attaches the caller's filter tree to each eligible thread, updates filter counts, propagates `no_new_privs`, and assigns filter mode if a thread was disabled. Filter lifetime is tree-shaped through `prev`; `refs` owns memory lifetime and `users` owns orphan/HUP notification semantics.

User notification creates a listener backed by anon inode file operations. When a syscall returns `USER_NOTIF`, the task creates a stack `seccomp_knotif`, links it under the matching filter, wakes pollers, then sleeps until the listener replies, dies, or injects addfd work. Listener `RECV` transitions notifications from INIT to SENT and copies syscall data to userspace. `SEND` transitions SENT to REPLIED and completes the target. `ADDFD` queues a `seccomp_kaddfd` for the blocked task to install with `receive_fd()` or `receive_fd_replace()`.

## State and Persistence

Per-task persistent state lives in `task_struct.seccomp`: mode, filter pointer, and filter count. Filters persist as refcounted chained objects; attached filters are never mutated except for reference counts and notification data protected by `notify_lock`. Notification listener state persists while its fd is open. Logging state persists globally in `seccomp_actions_logged`. Caches persist in each filter and are inherited from previous filters so a cached allow remains valid only if every filter in the path constantly allows that syscall/arch pair.

## Dependencies and Integration Points

This file integrates with syscall entry work flags, BPF classic verifier/runtime, audit, ptrace events, signals (`force_sig_seccomp()`), task credentials and `no_new_privs`, user namespaces and `CAP_SYS_ADMIN`, `cred_guard_mutex` and `sighand->siglock`, anon inode files, poll/wait queues, fd installation helpers, checkpoint/restore ptrace APIs, sysctl, architecture syscall accessors, and architecture-specific speculative-execution mitigation hooks.

## Risks and Edge Cases

Security-sensitive risks include fail-open filter behavior, incorrect action precedence, unsafe ptrace rechecks after syscall mutation, listener lifetime races, and addfd injection before a notification is valid. TSYNC must avoid races with exec and exiting threads. Reference accounting is subtle because each attached task, dependent filter, and listener fd contributes differently to `refs` and `users`. The BPF cache must only mark constant allow decisions; anything depending on non-constant args cannot be cached. `SECCOMP_USER_NOTIF_FLAG_CONTINUE` is dangerous if userspace relies on the listener as a privilege boundary because the tracee resumes the original syscall. `SECCOMP_MODE_DEAD` exists to make survival after kill actions impossible.

## Test Signals

Important tests include strict-mode allowed and denied syscall behavior, invalid BPF programs and invalid flags, no-new-privs and `CAP_SYS_ADMIN` permission checks, filter chaining precedence, TSYNC success and failure pid reporting, ptrace trace action with syscall rewrite and fatal-signal races, user-notification receive/send/poll/HUP paths, listener close while tasks wait, addfd success/failure/interruption, sysctl parsing and audit messages, checkpoint/restore filter export and metadata, compat filter copying, and cache debug output when enabled.
