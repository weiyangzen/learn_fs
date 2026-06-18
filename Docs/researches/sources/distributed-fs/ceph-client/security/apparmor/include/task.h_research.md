# sources/distributed-fs/ceph-client/security/apparmor/include/task.h

Purpose: declares per-task AppArmor state, task label transition helpers, ptrace mediation constants, signal feature strings, and user-namespace mediation entry points.

Important APIs/types: `task_ctx()` locates AppArmor's task blob. `struct aa_task_ctx` stores `nnp`, `onexec`, `previous`, and `token` for no-new-privs and procattr transitions. Helpers include `aa_replace_current_label()`, `aa_set_current_onexec()`, `aa_set_current_hat()`, `aa_restore_previous_label()`, `aa_get_task_label()`, `aa_free_task_ctx()`, `aa_dup_task_ctx()`, and `aa_clear_task_ctx_trans()`. Permission masks define ptrace, signal, and user-namespace create mediation.

Control flow: task allocation duplicates current transition state with label refs; task free drops refs; exec commit clears transitional fields; procattr and domain code modify `previous`/`onexec`/token.

State and persistence: task context persists for task lifetime and is copied on fork. Label refs are explicitly managed to survive RCU profile replacement.

Dependencies and integration: depends on LSM blob sizing, label refs, domain transition, ptrace hooks, signal hooks, and userns hooks. Risks include token mishandling, leaked labels on clone/free, and stale onexec transitions after exec. Test fork/exec, changehat restore, ptrace permissions, signal send/receive, no-new-privs interactions, and user namespace creation policy.
