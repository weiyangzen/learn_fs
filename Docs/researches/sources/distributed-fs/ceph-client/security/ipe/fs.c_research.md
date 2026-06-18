# sources/distributed-fs/ceph-client/security/ipe/fs.c

Purpose: Creates top-level IPE securityfs controls for success auditing, enforcement mode, policy directory, and new policy submission.

Important APIs/types/functions: Exports `policy_root` and `ipe_init_securityfs()`. File operations implement `setaudit/getaudit`, `setenforce/getenforce`, and `new_policy`.

Control flow: Writes require `CAP_MAC_ADMIN` in the initial user namespace. Audit/enforce writes parse booleans and update global variables, with enforce changes audited. `new_policy` copies user data, treats it as PKCS#7 policy data, creates a new policy via `ipe_new_policy(NULL, 0, copy, len)`, creates policyfs nodes, and audits load success/failure. Init creates `/sys/kernel/security/ipe`, `success_audit`, `enforce`, `policies`, existing active policy node if present, and `new_policy`.

State and persistence: Securityfs dentries are retained for the lifetime of IPE. Global booleans and policyfs directory state are exposed through files.

Dependencies and integration: Depends on securityfs, capability checks, policy parser/signature verifier, policyfs node creation, and audit.

Risks and test signals: Risks include partial securityfs creation cleanup, unsigned boot policy node creation, user-data length/memory handling, and CAP namespace policy. Tests should verify permissions, bool parsing, policy upload errors, existing active policy exposure, and cleanup on init failure.
