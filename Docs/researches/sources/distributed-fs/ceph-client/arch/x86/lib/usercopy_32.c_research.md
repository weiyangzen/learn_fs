# sources/distributed-fs/ceph-client/arch/x86/lib/usercopy_32.c

## Purpose
This file implements 32-bit x86 low-level user memory copy and clear helpers, including generic string-instruction copies and optional Intel-tuned unrolled/non-temporal paths.

## Important APIs, Types, and Functions
Exported APIs include `clear_user()`, `__clear_user()`, `__copy_user_ll()`, and `copy_from_user_inatomic_nontemporal()`. Optional Intel helpers are `__copy_user_intel()` and `__copy_user_intel_nocache()`, with global `struct movsl_mask movsl_mask`. Core macros are `__do_clear_user()` and `__copy_user()`, both using exception table fixups with remaining-byte accounting.

## Control Flow
`clear_user()` checks `access_ok()` before zeroing; `__clear_user()` assumes the caller checked. The clear macro enables user access, zeros longwords with `rep stosl`, handles trailing bytes with `rep stosb`, and uses exception fixups to leave the uncleared count in the return variable. `__copy_user_ll()` begins nospec uaccess, chooses the generic or Intel path based on alignment/size heuristics, and ends uaccess. `copy_from_user_inatomic_nontemporal()` uses `user_access_begin()`, optionally selects non-temporal Intel copies for larger XMM2-capable transfers, then ends access.

## State and Persistence
Persistent state is optional `movsl_mask`, configured elsewhere for Intel copy heuristics. Runtime state is limited to AC/user-access windows, destination memory, and remaining byte counts.

## Dependencies and Integration Points
It depends on 32-bit uaccess infrastructure, SMAP access macros, exception-table types such as `EX_TYPE_UCOPY_LEN4`, CPU feature detection, `might_fault()`, and symbol exports. It underpins generic `copy_{to,from}_user()` and clear-user paths on i386.

## Risks and Test Signals
Risks include incorrect uncopied-byte accounting after faults, missing access window closure, stale CPU-specific copy heuristics, non-temporal copy ordering, and alignment bugs. Test signals include LKDTM/usercopy checks, invalid pointer fault tests, short-copy count validation, SMAP builds, 32-bit boot, and performance tests across Intel and non-Intel configurations.
