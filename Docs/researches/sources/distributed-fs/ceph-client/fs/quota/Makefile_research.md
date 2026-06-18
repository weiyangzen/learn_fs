# sources/distributed-fs/ceph-client/fs/quota/Makefile

## Purpose
The quota Makefile maps quota Kconfig symbols to subsystem object files.

## Important APIs, types, and functions
It builds `dquot.o` for `CONFIG_QUOTA`, old and v2 format handlers for `QFMT_V1`/`QFMT_V2`, `quota_tree.o`, quota syscall/control helpers `quota.o` and `kqid.o`, and optional `netlink.o`.

## Control flow
Kbuild composes the quota subsystem according to selected features.

## State and persistence
No runtime state exists here; build composition determines which quota formats and notification paths are available.

## Dependencies and integration points
It integrates VFS quota core, quota format handlers, quota tree support, quotactl ABI, kernel quota IDs, and netlink warnings.

## Risks and test signals
Risks include object omission for selected symbols or link dependency drift between `QFMT_V2` and `QUOTA_TREE`. Test signals are all quota configuration combinations and module/builtin link tests.
