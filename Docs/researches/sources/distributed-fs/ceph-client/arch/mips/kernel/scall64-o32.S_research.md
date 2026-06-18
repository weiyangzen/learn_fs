# sources/distributed-fs/ceph-client/arch/mips/kernel/scall64-o32.S

## Purpose
Implements o32 compatibility syscall entry on 64-bit MIPS kernels and routes non-o32 calls to n32 or n64 handlers.

## Important APIs, Types, and Functions
- `handle_sys` is the shared 64-bit-kernel syscall entry for o32 compatibility.
- `sys32_syscall` implements the o32 indirect syscall helper using 64-bit registers.
- `sys32_call_table` exports compat entries from `asm/syscall_table_o32.h`.

## Control Flow
The entry saves pt_regs, enables interrupts, advances EPC, checks whether `v0` is in the o32 range, sign-clears upper halves of a0-a3 for o32 semantics, saves `a3`, loads stack arguments 5-8 as 32-bit values with exception-table fixups, records `TI_SYSCALL`, optionally traces via `syscall_trace_enter()`, dispatches through the compat table, applies errno/error-flag convention, and exits. If the number is not o32, it jumps to `handle_sysn32` when configured or `handle_sys64` otherwise. `sys32_syscall` range-checks indirect syscalls and shifts arguments before jumping to the real entry.

## State and Persistence
Mutates pt_regs, thread-info syscall field, and return/error registers only.

## Dependencies and Integration Points
Depends on o32 compat syscall table, n32/n64 handlers, ptrace syscall hooks, MIPS stackframe/user exception table support, and ABI-specific sign/argument-width rules.

## Risks
o32-on-64 argument translation is easy to break: upper halves must be discarded and stack args loaded as words. Bad stack fixups must zero only failed trailing args. Routing to n32/n64 must preserve the already-saved exception frame. Tracing can change syscall numbers and requires revalidation.

## Test Signals
o32 compat tests on 64-bit kernels should cover six/eight-argument calls, indirect syscall, bad stack, invalid syscall, tracing-modified syscall number, and fallback to n32/n64 handlers.
