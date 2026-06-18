# sources/distributed-fs/ceph-client/security/apparmor/audit.c

## Purpose
`audit.c` centralizes AppArmor audit event formatting, audit-mode decision logic, kill/complain behavior, and audit rule integration. It converts AppArmor-specific `apparmor_audit_data` into Linux audit records via `common_lsm_audit`.

## Important APIs and functions
- `audit_mode_names`, `aa_audit_type`, and `aa_class_names` provide stable string representations.
- `audit_pre` emits common fields: AppArmor audit type, operation, class, info/error, profile/label, namespace, and object name.
- `aa_audit_msg` sends an event with an explicit type.
- `aa_audit` maps `AUDIT_APPARMOR_AUTO` into audit, allowed, denied, or kill based on profile mode and error status.
- `aa_audit_rule_init`, `aa_audit_rule_known`, `aa_audit_rule_match`, and `aa_audit_rule_free` integrate AppArmor labels with kernel audit rules.

## Control flow
Callers populate `apparmor_audit_data` and optional type-specific callback. `aa_audit` suppresses successful events unless `AUDIT_ALL` or explicit audit bits require logging, maps complain-mode denials to `ALLOWED`, suppresses quiet modes, converts kill-mode denials to `KILL`, fills `ad->subj_label`, and invokes `aa_audit_msg`. Kill events send the configured signal to the audited task/current task.

## State and persistence
No durable state is stored. The audit rule helper allocates and retains a parsed `aa_label` in an `aa_audit_rule` object until audit frees it. Audit output enters the kernel audit subsystem and system logs according to external audit configuration.

## Dependencies and integration
The file depends on Linux audit, AppArmor label printing/parsing, profile namespaces, secid/LSM properties, and profile mode macros from policy code. It is called from file, capability, network, domain, mount, IPC, and policy-management mediation paths.

## Risks
Audit suppression can hide expected diagnostics when quiet modes or quiet permission bits apply. Class-name tables must remain aligned with `AA_CLASS_*` constants. Audit rule parsing currently treats rules as root-namespace labels, which can surprise namespaced policy users. Kill-mode side effects must only occur for true `AUDIT_APPARMOR_KILL` records.

## Test signals
Check enforce, complain, kill, quiet, quiet_denied, noquiet, and audit_all modes. Verify audit records contain namespace/profile/label formatting for single and stacked labels. Test audit rules with `AUDIT_SUBJ_ROLE` equality and inequality against AppArmor labels.
