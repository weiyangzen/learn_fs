<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/inode_backtrace.h -->
## sources/distributed-fs/ceph/src/mds/inode_backtrace.h

`inode_backtrace.h` declares two ancestry types: `inode_backpointer_t`, a single parent directory/dentry/version pointer, and `inode_backtrace_t`, a complete standalone chain for one inode. The header frames backtraces as metadata backpointers that can outlive cache context, for example as xattrs on objects.

`inode_backpointer_t` exports encode/decode, legacy decode, formatter dump, generated instances, equality, and stream output. Its durable fields are `dirino`, `dname`, and `version`. `inode_backtrace_t` exports encode/decode/dump/test, `compare`, `clear`, equality, and stream output. Its durable fields are `ino`, ordered `ancestors`, current `pool`, and `old_pools`.

State behavior is simple but critical to recovery. The ancestor order and versions are the evidence used to decide which of two namespace histories is newer or divergent. `old_pools` lets backtrace repair/update account for objects that previously lived outside the current pool. The `clear` method intentionally leaves `ino` and `pool` untouched while clearing ancestry and old pools.

Dependencies are Ceph buffer types, formatter forward declaration, `inodeno_t`, `version_t`, strings, and vectors. Integration points include `CInode` backtrace commit operations, journal segment expiry, metadata scrub, data-pool migration, and damage repair.

Risks: callers must compare only backtraces for the same inode; missing or stale ancestors can make repair choose the wrong namespace location; and old-pool information must be kept in sync with inode pool state. Test signals are equality and encode/decode round trips, old-format decode, compare divergence/equivalence matrices, and object backtrace updates during journal trimming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/inode_backtrace.h -->
