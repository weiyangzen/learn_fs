# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/masklog.h

## Purpose
`masklog.h` defines OCFS2/O2CB logging mask bits, compile-time filtering, bitset helpers, logging macros, and sysfs initialization declarations.

## Important APIs, types, and functions
It defines mask constants such as `ML_TCP`, `ML_HEARTBEAT`, `ML_DLM`, `ML_QUORUM`, `ML_ERROR`, `ML_NOTICE`, and `ML_KTHREAD`; `struct mlog_bits`; architecture-specific `__mlog_test_u64`, set, clear, and initializer macros; and user macros `mlog`, `mlog_ratelimited`, `mlog_errno`, and `mlog_bug_on_msg`. It declares `__mlog_printk`, `mlog_sys_init`, and `mlog_sys_shutdown`.

## Control flow
Call sites pass mask bits to `mlog`. The macro adds `MLOG_MASK_PREFIX`, applies `ML_ALLOWED_BITS`, then calls `__mlog_printk` only when runtime masks permit. `mlog_errno` suppresses common expected errors, and `mlog_bug_on_msg` logs before `BUG()`.

## State and persistence behavior
The header declares global allow/deny bitsets but stores no state itself. Mask choices affect runtime diagnostics only and are not persistent.

## Dependencies and integration points
It depends on scheduler/task state, kobject/sysfs declarations, ratelimit helpers, and compile-time options such as `CONFIG_OCFS2_DEBUG_MASKLOG`. Cluster modules can define `MLOG_MASK_PREFIX` before including it to prefix subsystem masks.

## Risks and test signals
Risks include forgetting to update `masklog.c` when adding a bit, architecture-specific bitset bugs, and assuming disabled debug logs have side effects. Test signals include 32-bit and 64-bit builds, ratelimited error paths, prefixed TCP/quorum logging, and sysfs table consistency.
