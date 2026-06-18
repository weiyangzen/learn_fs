# sources/distributed-fs/ceph-client/security/ipe/eval.h

Purpose: Declares IPE evaluation state, LSM blob data, match enums, and evaluation APIs.

Important APIs/types/functions: Defines `IPE_EVAL_CTX_INIT`, externs `ipe_active_policy`, `success_audit`, and `enforce`, and declares `struct ipe_superblock`, optional `struct ipe_bdev`, optional `struct ipe_inode`, `struct ipe_eval_ctx`, `enum ipe_match`, `ipe_build_eval_ctx()`, and `ipe_evaluate_event()`.

Control flow: No logic, but config guards mirror Kconfig provider selection and determine which context fields exist.

State and persistence: Structures model persistent LSM blob data: initramfs superblock flag, dm-verity root hash/signature state, and fs-verity signature state.

Dependencies and integration: Shared by LSM registration, hooks, policy, audit, and fs code.

Risks and test signals: Risk is config mismatch between blob sizing and context accessors. Build matrix and provider-specific evaluation tests are key signals.
