<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/asm-uaccess.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/asm-uaccess.h

## Purpose
Defines assembly macros for validating user-space memory access ranges on Xtensa.

## Important APIs, Types, And Functions
Macros are `user_ok aa, as, at, error` and `access_ok aa, as, at, sp, error`.

## Control Flow
`user_ok` compares the requested size against `TASK_SIZE`, subtracts size from the task limit, and branches to the supplied error label if the range is too large or starts beyond the last valid address. `access_ok` currently wraps `user_ok` and falls through on success.

## State And Persistence
No persistent state. It only uses registers supplied by assembly callers.

## Dependencies And Integration Points
Depends on `TASK_SIZE`, generated offsets, current/thread headers, and assembly uaccess routines that use exception tables.

## Risks And Edge Cases
Range arithmetic must avoid overflow and preserve documented registers. The macro is optimized for fall-through success; callers must provide correct error labels and scratch registers.

## Test Signals
Run uaccess selftests, fault-injection tests for boundary addresses near `TASK_SIZE`, and build assembly callers with both MMU/noMMU layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/asm-uaccess.h -->
