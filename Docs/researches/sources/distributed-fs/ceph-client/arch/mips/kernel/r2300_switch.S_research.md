# sources/distributed-fs/ceph-client/arch/mips/kernel/r2300_switch.S

## Purpose
Implements R2300-specific low-level task switching through the `resume` assembly entry.

## Important APIs, Types, and Functions
- `resume(prev, next, next_ti)` saves non-scratch CPU state in `prev`, restores `next`, updates kernel stack tracking, status, and returns `prev`.

## Control Flow
`resume` saves CP0 status, non-scratch registers, and RA into the previous task. It updates the stack protector canary on non-SMP stack-protector builds, moves `$28` to the next thread_info pointer, restores non-scratch registers from `next`, calculates the saved kernel stack pointer, writes `kernelsp`, merges preserved interrupt/status bits with `next` saved status, writes CP0 status, returns `prev` in `v0`, and jumps to the restored RA.

## State and Persistence
State is task context in `thread_struct`, `thread_info`, `kernelsp`, CP0 status, and optional `__stack_chk_guard`.

## Dependencies and Integration Points
Called by the scheduler's architecture switch path. Depends on `cpu_save_nonscratch`, `cpu_restore_nonscratch`, stackframe offsets, and R2300/MIPS I register conventions.

## Risks
The ordering around `$28`, `$29`, and `kernelsp` is intentional to avoid races without disabling interrupts. Incorrect status-bit masking can leak privilege or interrupt state. Stack protector update is only for !SMP and must match task canary storage.

## Test Signals
Context-switch stress should preserve callee-saved registers, stack pointer, status, and kernel stack tracking. Scheduler/fork tests on R2300 builds should return through `ret_from_fork` correctly.
