# sources/distributed-fs/ceph-client/security/ipe/ipe.c

Purpose: Registers IPE as an LSM, reserves LSM blob sizes, exposes blob accessors, installs hooks, and loads the built-in boot policy.

Important APIs/types/functions: Defines `ipe_enabled`, `ipe_blobs`, `ipe_lsmid`, blob accessors `ipe_sb()`, optional `ipe_bdev()`, optional `ipe_inode()`, hook array `ipe_hooks`, and `ipe_init()` registered through `DEFINE_LSM(ipe)`.

Control flow: During LSM init, hooks are added, IPE is marked enabled, and if generated `ipe_boot_policy` is non-empty, it is parsed as plaintext and assigned to `ipe_active_policy`. Securityfs initialization is registered as `initcall_fs`.

State and persistence: LSM blob offsets/sizes persist after init. Active boot policy persists as the initial RCU policy until replaced.

Dependencies and integration: Depends on LSM framework, generated boot policy object, policy parser, evaluation globals, hooks, and securityfs init.

Risks and test signals: Risks include blob offset arithmetic, boot policy parse failure aborting init, and hook registration despite later policy failure. Tests should include boot with/without built-in policy and provider config blob sizing.
