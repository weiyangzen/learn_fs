<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/uaccess.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/uaccess.h

## Purpose
Implements OpenRISC user-memory access primitives with exception-table fixups.

## Important APIs, Types, And Functions
Provides `get_user`, `put_user`, unchecked variants, size dispatch for 1/2/4/8 byte accesses, inline assembly load/store fixup blocks, `raw_copy_from_user()`, `raw_copy_to_user()`, `clear_user()`, `strncpy_from_user()`, and `strnlen_user()`.

## Control Flow
Checked forms call `access_ok()` first, then size-specific inline assembly emits faulting access labels and fixup labels. If a fault happens, the exception table redirects to code setting `-EFAULT` and zeroing destination for reads. Bulk copy and clear call assembly routines in `lib/string.S`.

## State And Persistence
Mutates user or kernel buffers. Fault state is not persisted, but return values report bytes not copied or `-EFAULT`.

## Dependencies And Integration Points
Depends on `asm/extable.h`, generic `access_ok`, OpenRISC instructions, and exception handling in `mm/fault.c`. Used by signals, ptrace, syscall argument/result paths, and drivers.

## Risks
Inline asm constraints and exception-table entries are correctness-critical. 64-bit accesses split into two 32-bit operations, so partial fault behavior must be acceptable to callers. Unchecked variants require prior validation.

## Test Signals
Usercopy selftests, signal-frame copy faults, ptrace regset copy faults, bad user pointer handling, and KASAN/usercopy hardening builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/uaccess.h -->
