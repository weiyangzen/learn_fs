<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/init.c -->
# sources/distributed-fs/ceph-client/fs/verity/init.c

Purpose: Performs fs-verity subsystem initialization and provides rate-limited logging helpers.

Important APIs, types, and functions: Defines optional sysctl table for `/proc/sys/fs/verity/require_signatures`, `fsverity_init_sysctl()`, exported-style internal `fsverity_msg()`, and `late_initcall(fsverity_init)`.

Control flow: At late init, fs-verity checks hash algorithms, initializes the `fsverity_info` cache/hash table, allocates the verification workqueue, registers sysctls, initializes builtin signature support if configured, and registers BPF kfuncs if configured. Logging uses a static ratelimit state and prefixes messages with superblock id and inode number when available.

State and persistence: Creates global in-memory subsystem state: info cache, rhashtable, workqueue, optional sysctl, keyring, and BPF registration. The sysctl changes runtime policy for requiring builtin signatures but does not persist across boot by itself.

Dependencies and integration points: Depends on tracepoint creation, sysctl, ratelimit, hash/open/verify/signature/measure initialization paths, and kernel initcall ordering.

Risks and test signals: Risks are init ordering failures, panic paths for cache/workqueue/keyring allocation, missing sysctl when signatures are configured, and excessive or suppressed corruption logging. Test boot with fs-verity enabled, sysctl visibility, signature config on/off, BPF config on/off, and forced allocation failure where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/init.c -->
