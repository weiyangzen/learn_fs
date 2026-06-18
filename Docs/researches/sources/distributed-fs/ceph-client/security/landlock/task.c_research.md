<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/task.c -->
# sources/distributed-fs/ceph-client/security/landlock/task.c

## Purpose

`task.c` registers Landlock LSM hooks for task-to-task and IPC interactions. It enforces domain ordering for ptrace, scoped access to abstract Unix sockets, and scoped signal delivery so Landlock policies can restrict cross-domain process interaction beyond filesystem and network port access.

## Important APIs, Types, and Functions

- `domain_scope_le()` checks whether a parent domain is an ancestor of, or equal to, a child domain.
- `domain_ptrace()` turns the domain ordering check into `0` or `-EPERM`.
- `hook_ptrace_access_check()` and `hook_ptrace_traceme()` enforce ptrace constraints and emit Landlock denial audit records.
- `domain_is_scoped()` compares client/server hierarchies and layer scope bits for abstract Unix socket and signal restrictions.
- `hook_unix_stream_connect()` and `hook_unix_may_send()` restrict cross-domain access to abstract Unix sockets.
- `hook_task_kill()` and `hook_file_send_sigiotask()` restrict direct signals and SIGIO/SIGURG-style file-owner signals.
- `landlock_add_task_hooks()` registers the hook table with `security_add_hooks()`.

## Control Flow

Ptrace enforcement is based on hierarchy ancestry. A non-Landlocked tracer is allowed. A Landlocked tracer can access only a target with a domain that is at least as restrictive as the tracer's domain. `ptrace_traceme` applies the same rule from the proposed parent tracer to the current task and logs the parent domain when denied.

Scoped IPC checks first locate an applicable subject and the layer that handles the relevant scope bit. Abstract Unix socket hooks ignore non-Landlocked tasks, non-abstract sockets, already-connected datagram peers, and sockets whose peer domain is not scoped relative to the requester. Denials log network audit data for the target socket.

Signal checks allow same-thread-group kernel credential-change signals when `cred` is null, then evaluate the subject domain against the target task's domain under RCU. File-owner signals use the saved Landlock subject in `landlock_file(fown->file)->fown_subject`, protected by the caller-held `fown->lock`, instead of recomputing from current credentials.

## State and Persistence Behavior

The file maintains no global mutable state. It reads domain hierarchies from credentials and saved file-owner Landlock state. Domain comparisons are stable through referenced credential and socket/file state, with task domains read under RCU. Scope semantics depend on each layer's `LANDLOCK_SCOPE_ABSTRACT_UNIX_SOCKET` and `LANDLOCK_SCOPE_SIGNAL` bits.

## Dependencies and Integration Points

The hooks depend on Landlock credential/domain/ruleset helpers, `landlock_log_denial()`, Unix socket internals from `net/af_unix.h`, generic LSM task/socket hooks, and common audit structures. They integrate with Landlock ruleset creation through scope bits accepted in `landlock_create_ruleset()` and with file-owner state populated elsewhere in the Landlock file hooks.

## Risks and Edge Cases

Hierarchy walking in `domain_is_scoped()` is subtle because client and server may have different domain depths or no server domain. It must preserve the rule that a scoped client can interact only with domains in the allowed ancestry relationship. Abstract Unix sockets are singled out; pathname Unix sockets are left to filesystem policy. Signal exceptions for same thread group are necessary for POSIX credential changes and must not be widened.

## Test Signals

Tests should cover ptrace from unconstrained to constrained tasks, constrained to less-constrained tasks, sibling domains, and child domains; abstract stream connect and datagram send across same and different domains; pathname socket non-enforcement here; normal `kill`, `tgkill`, and SIGIO delivery; audit records for denied ptrace/socket/signal operations; and behavior when `PTRACE_MODE_NOAUDIT` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/task.c -->
