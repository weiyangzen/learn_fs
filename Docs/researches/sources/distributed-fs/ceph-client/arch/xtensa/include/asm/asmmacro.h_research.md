<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/asmmacro.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/asmmacro.h

## Purpose
Provides common Xtensa assembly macros for loops, exception-table annotations, unaligned word extraction, bit-scan/absolute-value fallbacks, ABI-neutral call/argument names, and exception-text section placement.

## Important APIs, Types, And Functions
Key macros include `__loopi`, `__loops`, `__loopt`, `__loop`, `__endl`, `__endla`, `EX`, `__src_b`, `__ssa8`, `do_nsau`, `do_abs`, `abi_entry`, `abi_ret`, `abi_call`, `abi_callx`, `abi_arg*`, `abi_saved*`, `KABI_*`, `UABI_*`, and `__XTENSA_HANDLER`.

## Control Flow
Loop macros choose zero-overhead `loop` instructions when available and branch-based loops otherwise. ABI macros map the same assembly source to windowed or call0 register conventions. `EX` emits exception-table entries for faultable instructions.

## State And Persistence
No runtime data is owned; macros shape generated assembly and exception table contents.

## Dependencies And Integration Points
Depends on Xtensa core feature macros and is used across low-level string, cache, boot, trap, and syscall assembly.

## Risks And Edge Cases
ABI register mappings must match compiler flags. Loop fallbacks must preserve end labels and scratch registers. Endianness-sensitive unaligned extraction must match memory layout. Exception-table entries must reference the right faulting label.

## Test Signals
Build both windowed and call0 kernels, run string/uaccess/cache routines, verify exception fixups, and test cores with and without zero-overhead loops, NSA, and ABS instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/asmmacro.h -->
