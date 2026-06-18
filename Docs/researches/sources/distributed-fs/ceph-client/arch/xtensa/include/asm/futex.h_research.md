<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/futex.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/futex.h

## Purpose
Implements Xtensa futex atomic operations on user memory, including atomic op and cmpxchg primitives with exception-table based fault handling.

## Important APIs, Types, And Functions
Defines `arch_futex_atomic_op_inuser`, `futex_atomic_cmpxchg_inatomic`, and internal `__futex_atomic_op` for exclusive or S32C1I cores.

## Control Flow
Operations first validate `access_ok`. On capable cores, inline assembly performs atomic load/modify/store loops over user memory and routes faults through `.fixup` and `__ex_table` entries to return `-EFAULT`. Unsupported atomic hardware falls back to generic local futex helpers.

## State And Persistence
Mutates user futex words and returns old values. No kernel persistent state.

## Dependencies And Integration Points
Depends on uaccess, futex generic code, Xtensa atomic instructions, exception tables, and user memory fault handling.

## Risks And Edge Cases
Fault fixups must cover every faultable load/store. S32C1I and exclusive loops must not corrupt `uval` on failed compare. Fallback local operations may not be suitable for SMP hardware lacking atomic instructions.

## Test Signals
Run futex selftests, pthread mutex/condvar stress, userfault/fault-injection around futex pages, and SMP contention tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/futex.h -->
