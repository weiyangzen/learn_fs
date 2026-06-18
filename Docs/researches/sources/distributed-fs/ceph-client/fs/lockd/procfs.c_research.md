# sources/distributed-fs/ceph-client/fs/lockd/procfs.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/procfs.c` implements lockd's optional procfs control file `/proc/fs/lockd/nlm_end_grace`. It lets privileged users inspect and force the end of a lockd grace period for the current network namespace. The source was read as a complete 92-line file.

## Important APIs, Types, and Functions

Important functions are `nlm_end_grace_write`, `nlm_end_grace_read`, `lockd_create_procfs`, and `lockd_remove_procfs`. `lockd_end_grace_proc_ops` wires read, write, llseek, and release operations.

## Control Flow

Reads get `struct lockd_net` from `current->nsproxy->net_ns`, report `Y\n` when the lock manager grace list is empty, and `N\n` otherwise. Writes use `simple_transaction_get` to accept one buffer per open and only strings starting with `Y`, `y`, or `1` call `locks_end_grace`; other input returns `-EINVAL`. Creation builds `/proc/fs/lockd` and then `nlm_end_grace`; removal deletes both entries.

## State and Persistence Behavior

The file owns no persistent lockd state. Transaction write buffers are per-open and released via `simple_transaction_release`. Grace state lives in `lockd_net->lockd_manager`.

## Dependencies and Integration Points

It depends on procfs, net namespace lookup, `netns.h`, libfs transaction and buffer helpers, and VFS lock manager grace APIs. It is compiled only with `CONFIG_PROC_FS`.

## Risks and Edge Cases

The proc directory is global while operations act on current net namespace, so tests must verify namespace expectations. `simple_transaction_get` permits only one write per open. Invalid or empty writes fail. Creation must unwind the directory if file creation fails.

## Test Signals

Signals include procfs creation/removal tests, read values before/during/after grace, write parsing for accepted and rejected prefixes, per-net namespace behavior, and transaction release leak checks.
