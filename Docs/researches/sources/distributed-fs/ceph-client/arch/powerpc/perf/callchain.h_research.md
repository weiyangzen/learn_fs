
# sources/distributed-fs/ceph-client/arch/powerpc/perf/callchain.h

## Purpose

This header shares declarations and helpers for PowerPC perf user callchain unwinding.

## Important APIs, Types, And Functions

- Declares `perf_callchain_user_64()` and `perf_callchain_user_32()`.
- `invalid_user_sp()` validates nonzero user stack pointer, architecture-specific alignment, and an upper bound below `STACK_TOP`.
- `__read_user_stack()` checks task address range and alignment before using `copy_from_user_nofault()`.

## Control Flow

The user unwind implementations call `invalid_user_sp()` before frame reads and `__read_user_stack()` for each nofault user memory access. The helper returns `-EFAULT` for out-of-range or misaligned pointers before attempting a copy.

## State And Persistence

No state is stored. The helpers read user memory only for the current sample.

## Dependencies And Integration Points

It depends on `is_32bit_task()`, `STACK_TOP`, `TASK_SIZE`, and Linux nofault copy APIs. It is included by common, 32-bit, and 64-bit callchain files.

## Risks And Edge Cases

The alignment mask differs between 32-bit and 64-bit tasks. Because callchains can be collected at interrupt level, the nofault copy path is mandatory. Bounds checks must avoid wraparound via `addr > TASK_SIZE - size`.

## Test Signals

Test 32-bit compat and 64-bit user callchains, invalid stack pointers, alternate signal stacks, and sampling at interrupt level where page faults cannot be handled normally.
