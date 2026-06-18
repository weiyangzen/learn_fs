# sources/distributed-fs/ceph-client/arch/mips/kernel/scall64-n32.S

## Purpose
Implements n32 compatibility syscall entry on 64-bit MIPS kernels and falls through to n64 handling for non-n32 syscall numbers.

## Important APIs, Types, and Functions
- `handle_sysn32` is the n32 syscall entry.
- `sysn32_call_table` is exported from `asm/syscall_table_n32.h`.

## Control Flow
When o32 is not configured, the entry performs the initial exception save and EPC advance itself; otherwise it can be reached after shared entry setup. It checks whether `v0` is in the n32 syscall range, saves `a3`, records `TI_SYSCALL`, optionally calls `syscall_trace_enter()`, dispatches through `sysn32_call_table`, applies MIPS error flag/negation convention, stores the return value, and exits. If the number is not n32, it jumps to `handle_sys64`.

## State and Persistence
Mutates pt_regs and thread-info syscall state only.

## Dependencies and Integration Points
Integrates with 64-bit syscall entry chaining, ptrace/seccomp/audit trace hook, n32 syscall table generation, and shared `syscall_exit_partial`.

## Risks
The entry must coordinate with o32/n64 files so register save/EPC advance happens exactly once. Tracing can modify the syscall number, requiring revalidation before dispatch. Table offset arithmetic subtracts the n32 base and scales by 8.

## Test Signals
n32 ABI syscall tests should pass for normal, traced, seccomp-rejected, invalid, and modified syscall-number cases. Mixed o32/n32/n64 builds should route non-n32 calls correctly.
