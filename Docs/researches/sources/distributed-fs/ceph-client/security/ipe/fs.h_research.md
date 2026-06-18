# sources/distributed-fs/ceph-client/security/ipe/fs.h

Purpose: Declares IPE policy securityfs node helpers and shared policy root dentry.

Important APIs/types/functions: Externs `policy_root` and declares `ipe_new_policyfs_node()` and `ipe_del_policyfs_node()`.

Control flow: No logic; it exposes policyfs lifecycle functions to top-level fs and policy cleanup code.

State and persistence: `policy_root` points to the securityfs policies directory once initialized.

Dependencies and integration: Included by `fs.c`, `policy.c`, and `policy_fs.c`.

Risks and test signals: Build-time interface drift and NULL `policy_root` use before securityfs init are the main risks. Init-order tests cover this.
