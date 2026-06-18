# sources/distributed-fs/ceph-client/fs/xfs/xfs_dahash_test.h

Purpose: Declares the XFS directory/attribute hash self-test entry point.

Important APIs, types, and functions: Exposes `int xfs_dahash_test(void);`.

Control flow: Callers invoke the self-test and treat nonzero return values as failures.

State and persistence: No state or persistence.

Dependencies and integration points: Paired with `xfs_dahash_test.c` and included by self-test wiring.

Risks and test signals: Risk is stale declaration if self-test integration changes. Test builds that include the hash test.
