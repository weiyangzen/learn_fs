# sources/distributed-fs/ceph-client/security/ipe/policy_fs.c

Purpose: Implements per-policy securityfs directories and files for reading policy metadata/content, activating, updating, and deleting deployed IPE policies.

Important APIs/types/functions: File handlers include `read_pkcs7()`, `read_policy()`, `read_name()`, `read_version()`, `setactive()`, `getactive()`, `update_policy()`, and `delete_policy()`. Exports `ipe_new_policyfs_node()` and `ipe_del_policyfs_node()`.

Control flow: Each policy directory contains `pkcs7`, `policy`, `name`, `version`, `active`, `update`, and `delete`. Reads take the parent inode shared lock and return `-ENOENT` when deleted/initializing; `pkcs7` also returns `-ENOENT` for unsigned policies. Writes require `CAP_MAC_ADMIN`. Activation only accepts true, locks the parent inode, and calls `ipe_set_active_pol()`. Update copies signed policy data and delegates to `ipe_update_policy()`. Delete refuses active policies under `ipe_policy_lock`, clears `i_private`, synchronizes RCU, and frees the policy.

State and persistence: Policy directories keep `root->i_private` as the owning policy pointer and `p->policyfs` as the dentry. Active state is derived from `ipe_active_policy`.

Dependencies and integration: Uses securityfs, inode locking, RCU, policy lifecycle functions, capability checks, and audit on update failures.

Risks and test signals: Risks include active pointer comparison outside locks in `getactive()`, policy deletion races, partial directory creation cleanup, update ownership swap, and refusing deletion of active policies. Tests should cover read-after-delete, update version/name errors, activation of older policies, duplicate names, and cleanup on file creation failure.
