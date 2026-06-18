# sources/distributed-fs/ceph-client/security/ipe/audit.h

Purpose: Declares the IPE audit interface used by evaluation, policy, and securityfs code.

Important APIs/types/functions: Prototypes `ipe_audit_match()`, `ipe_audit_policy_load()`, `ipe_audit_policy_activation()`, and `ipe_audit_enforce()`.

Control flow: No runtime logic. The declarations encode where audit side effects occur around policy evaluation and configuration changes.

State and persistence: No state.

Dependencies and integration: Includes `policy.h` for policy/evaluation types; referenced by `eval.c`, `fs.c`, `policy.c`, and `policy_fs.c`.

Risks and test signals: Interface risks are type drift and audit calls being skipped by future code paths. Build coverage and audit-event tests are the main signals.
