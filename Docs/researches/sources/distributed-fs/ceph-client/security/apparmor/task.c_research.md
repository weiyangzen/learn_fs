# sources/distributed-fs/ceph-client/security/apparmor/task.c

Purpose: handles AppArmor task label access/replacement, hat/on-exec context state, ptrace mediation, and user namespace creation mediation.

Important APIs, types, and functions: public functions are `aa_get_task_label()`, `aa_replace_current_label()`, `aa_set_current_onexec()`, `aa_set_current_hat()`, `aa_restore_previous_label()`, `aa_may_ptrace()`, and `aa_profile_ns_perm()`. Internal mediation helpers include `profile_ptrace_perm()`, `profile_tracee_perm()`, `profile_tracer_perm()`, `audit_ptrace_cb()`, `get_current_exe_path()`, and `audit_ns_cb()`.

Control flow: label replacement prepares new credentials, updates stale NNP labels, clears task transition state when moving unconfined or across namespaces, then commits the new label. Hat switching stores/restores prior labels guarded by a token. Ptrace mediation checks both tracer and tracee label views through `xcheck_labels()`, falling back to `CAP_SYS_PTRACE` for old-style profiles. User namespace mediation looks up class policy state and checks `AA_USERNS_CREATE`.

State and persistence: mutates current task credentials and `aa_task_ctx` fields (`previous`, `onexec`, `token`, `nnp`). It reads peer task creds under RCU and emits audit records, including executable path when available.

Dependencies and integration: tied to Linux credential commit flow, AppArmor label/ruleset APIs, ptrace LSM hooks, namespace creation hooks, path rendering, and audit logging.

Risks and test signals: credential replacement must preserve label refs correctly while racing label replacement. Hat token checks are security-critical. `get_current_exe_path()` has an error path that must release acquired file/path refs. Test signals include self/peer ptrace allow/deny, stale label replacement, change_hat/restore token behavior, on-exec clearing, and userns audit output.
