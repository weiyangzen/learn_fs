# sources/distributed-fs/ceph-client/fs/xfs/xfs_dahash_test.c

Purpose: Provides an init-time regression test for XFS directory/attribute name hashing, covering normal and ASCII case-insensitive hash functions.

Important APIs, types, and functions: Contains a 4096-byte `__initdata` random buffer, 100 `struct dahash_test` vectors, and `xfs_dahash_test()`.

Control flow: The test hashes each byte slice with `xfs_da_hashname()`, then hashes the same slice as an `xfs_name` with `xfs_ascii_ci_hashname()`. Any mismatch increments an error count; nonzero errors are logged and return `-ERANGE`.

State and persistence: All vectors are init-only and discarded after init. No filesystem state is mutated.

Dependencies and integration points: Depends on `xfs_dir2_priv.h` hash helpers and the declaration in `xfs_dahash_test.h`.

Risks and test signals: Risks are accidental hash ABI changes, endian or char signedness issues, and fixed-vector blind spots. Test on multiple architectures and verify intentional hash changes fail.
