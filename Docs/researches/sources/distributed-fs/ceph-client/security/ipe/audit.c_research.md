# sources/distributed-fs/ceph-client/security/ipe/audit.c

Purpose: Emits audit records for IPE access decisions, policy loads, policy activations, and enforcement-mode changes.

Important APIs/types/functions: Provides `ipe_audit_match()`, `ipe_audit_policy_load()`, `ipe_audit_policy_activation()`, and `ipe_audit_enforce()`. Internal helpers format rules, dm-verity/fs-verity digest properties, policy metadata, and SHA-256 policy digest.

Control flow: Access auditing skips allowed decisions unless `success_audit` is enabled, then logs operation, hook, enforcing state, pid, command, path/dev/ino, and matched rule/default. Policy load/activation logs names, versions, SHA-256 digest of PKCS#7 data, session/audit uid, result, and errno. Enforcement changes log old/new mode through audit.

State and persistence: Reads global `success_audit` and `enforce`; no local persistent state. Audit records persist externally in audit logs.

Dependencies and integration: Uses audit subsystem, current task identity, IPE policy/eval structures, digest formatting helpers, and SHA-256 library.

Risks and test signals: Risks include NULL file/path handling, digesting NULL `pkcs7` for unsigned policies, audit format drift, and calling `audit_log_start()` with atomic allocation in hook paths. Tests should inspect records for rule/table/global matches, deny/allow with success audit, policy load failure, activation from no boot policy, and enforce toggles.
