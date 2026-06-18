# sources/distributed-fs/ceph-client/security/ipe/policy.h

Purpose: Defines IPE policy model types and policy lifecycle APIs.

Important APIs/types/functions: Enumerates operations (`EXEC`, firmware, module, kexec image/initramfs, policy, X.509), actions (`ALLOW`, `DENY`), and properties (boot verified, dm-verity root hash/signature, fs-verity digest/signature). Defines `struct ipe_prop`, `ipe_rule`, `ipe_op_table`, `ipe_parsed_policy`, and `ipe_policy`, plus lifecycle/update/activation prototypes and `ipe_policy_lock`.

Control flow: No logic, but the structure layout drives parser output, evaluator traversal, audit formatting, and securityfs reads.

State and persistence: `struct ipe_policy` is the persistent runtime policy object and contains both source text/blob and parsed decision tables.

Dependencies and integration: Shared by all IPE subsystems.

Risks and test signals: Risks include enum order coupling to parser/audit arrays and property config support. Compile-time and parser/evaluator tests should catch drift.
