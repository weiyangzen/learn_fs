# sources/distributed-fs/openafs/src/rx/DARWIN/rx_kmutex.c

Purpose: Darwin/macOS Rx kernel lock setup/teardown implementation for Darwin 8+ lock groups.

Important APIs/types/functions: global `openafs_lck_grp`, static `openafs_lck_grp_attr`, `rx_kmutex_setup`, and `rx_kmutex_finish`.

Control flow: setup allocates a lock-group attribute, enables lock statistics, creates the `openafs` lock group, frees the attribute, and optionally initializes sockproxy support. Finish optionally tears down sockproxy and frees the lock group.

State/persistence: maintains a kernel lock group pointer used by all Darwin 8+ Rx mutex allocations.

Dependencies/integration: Darwin `<kern/locks.h>` through the header, OpenAFS sysincludes, and optional `AFS_SOCKPROXY_ENV` hooks.

Risks: every `MUTEX_INIT` depends on setup having run; teardown while locks exist would be unsafe; sockproxy setup/finish ordering shares this lifecycle. Test signals are kext startup/shutdown, lock leak checks, and macOS sockproxy-enabled builds.
