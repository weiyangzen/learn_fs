# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/flock.c

## Purpose
This formatter decodes `flock` operation bitmasks for `perf trace`.

## Important APIs, Types, And Functions
It defines fallback values for `LOCK_MAND`, `LOCK_READ`, `LOCK_WRITE`, and `LOCK_RW`, then implements `syscall_arg__scnprintf_flock()`. It uses standard `LOCK_SH`, `LOCK_EX`, `LOCK_NB`, and `LOCK_UN` from `linux/fcntl.h` plus the fallback mandatory-locking values.

## Control Flow
The formatter returns `NONE` for zero. It then emits matching known commands with optional `LOCK_` prefix, clears handled bits, and appends leftover bits as hex. It checks compound `LOCK_RW` before separate read/write handling in the declared macro order.

## State, Dependencies, And Integration
No persistent state and no masks are modified. The function is declared as `SCA_FLOCK` in `beauty.h` and used by perf trace syscall tables.

## Risks And Test Signals
There is a minor macro cleanup typo (`#undef P_OP` instead of `P_CMD`), but it is local to preprocessing and generally harmless unless included in a context that reuses the macro name. Tests should cover zero, shared/exclusive/nonblock/unlock, mandatory modes, combined flags, and unknown bits.
