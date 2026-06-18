# sources/distributed-fs/ceph-client/security/ipe/hooks.c

Purpose: Implements IPE LSM hook handlers and integrity blob update hooks that feed evaluation context state.

Important APIs/types/functions: Hook handlers include `ipe_bprm_check_security()`, `ipe_bprm_creds_for_exec()`, `ipe_mmap_file()`, `ipe_file_mprotect()`, `ipe_kernel_read_file()`, `ipe_kernel_load_data()`, `ipe_unpack_initramfs()`, optional `ipe_bdev_free_security()`, `ipe_bdev_setintegrity()`, and optional `ipe_inode_setintegrity()`.

Control flow: Exec hooks evaluate `IPE_OP_EXEC` for normal binary checks and AT_EXECVE_CHECK script checks. mmap/mprotect evaluate executable mappings only when gaining execute permission. Kernel read/load hooks map kernel ids to IPE operations for firmware, modules, kexec image/initramfs, policy, and X.509 certs, warning and using invalid op for unknown ids. Initramfs hook marks the root superblock. Integrity hooks store dm-verity root hashes/signature booleans on block-device blobs and fs-verity builtin signature booleans on inode blobs.

State and persistence: LSM blobs persist on superblocks, block devices, and inodes; block-device root hash allocations are freed by `ipe_bdev_free_security()`.

Dependencies and integration: Tied to LSM hook registration, kernel_read/load ids, dm-verity/fs-verity integrity events, digest helpers, and evaluation.

Risks and test signals: Risks include NULL file handling for mmap/mprotect, incorrect id-to-op mapping, stale root hash replacement, and provider config behavior. Tests should cover all hook mappings, permissive/enforce decisions, executable transition checks, and integrity blob lifecycle.
