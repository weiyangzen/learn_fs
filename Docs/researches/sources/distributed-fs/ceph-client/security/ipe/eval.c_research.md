# sources/distributed-fs/ceph-client/security/ipe/eval.c

Purpose: Maintains active IPE policy state, builds evaluation contexts, evaluates policy properties/rules/defaults, audits results, and enforces deny decisions.

Important APIs/types/functions: Exports `ipe_active_policy`, `success_audit`, `enforce`, `ipe_build_eval_ctx()`, and `ipe_evaluate_event()`. Property evaluators cover boot-verified, dm-verity root hash/signature, fs-verity digest, and fs-verity builtin signature depending on config.

Control flow: Hook code builds `struct ipe_eval_ctx` with file, op, hook, initramfs flag, optional block-device blob, inode, and inode blob. `ipe_evaluate_event()` RCU-loads the active policy, handles invalid ops through global default, scans rules for the operation in insertion order and requires all rule properties to match, then falls back to operation default or global default. It audits before leaving the RCU section, returns `-EACCES` for deny, and suppresses enforcement when `enforce` is false.

State and persistence: Active policy pointer is RCU-protected. `success_audit` and `enforce` are module parameters/securityfs-controlled booleans.

Dependencies and integration: Integrates with LSM blob accessors, fs-verity digest API, dm-verity integrity data stored by hooks, policy parser structures, and audit.

Risks and test signals: Risks include NULL active policy allowing all, missing global default causing warning/allow for invalid ops, RCU lifetime of policy/rule pointers during audit, and config-gated properties evaluating false. Tests should evaluate ordered rule matching, default precedence, permissive mode, no-policy mode, and each provider property.
