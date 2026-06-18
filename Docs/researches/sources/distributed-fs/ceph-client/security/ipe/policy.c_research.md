# sources/distributed-fs/ceph-client/security/ipe/policy.c

Purpose: Allocates, verifies, parses, updates, activates, and frees IPE policies.

Important APIs/types/functions: Provides global `ipe_policy_lock`, `ipe_free_policy()`, `ipe_update_policy()`, `ipe_new_policy()`, and `ipe_set_active_pol()`. Internal `ver_to_u64()` compares major/minor/revision, and `set_pkcs7_data()` extracts signed policy plaintext from PKCS#7 verification.

Control flow: `ipe_new_policy()` accepts either plaintext or PKCS#7 data. For signed data it copies the blob, verifies against secondary and optionally platform keyrings, captures plaintext via callback, and parses. Plaintext is duplicated directly. `ipe_update_policy()` requires inode lock, parses a new policy, enforces same name and strictly newer version, swaps policyfs ownership, updates active policy if replacing the active one under `ipe_policy_lock`, synchronizes RCU, and frees old policy. `ipe_set_active_pol()` forbids activating a policy older than the current active version.

State and persistence: Policies hold PKCS#7 blob, plaintext pointer/length, parsed policy, and securityfs dentry. Active policy is RCU-protected; writer serialization uses `ipe_policy_lock` plus policyfs inode locks.

Dependencies and integration: Integrates with system data verification, trusted keyrings, policy parser, policyfs nodes, audit, RCU, and securityfs.

Risks and test signals: Risks include unsigned/signed text ownership subtleties, version comparison rules, policyfs swap correctness, RCU lifetime, and keyring fallback semantics. Tests should cover signed verification failures, same-name enforcement, stale update rejection, active policy replacement, and freeing policies with/without PKCS#7.
