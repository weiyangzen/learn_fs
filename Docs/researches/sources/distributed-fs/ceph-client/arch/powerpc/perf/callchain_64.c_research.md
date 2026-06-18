
# sources/distributed-fs/ceph-client/arch/powerpc/perf/callchain_64.c

## Purpose

This file implements 64-bit PowerPC user-space perf callchain unwinding, including signal frame recovery.

## Important APIs, Types, And Functions

- `read_user_stack_64()` wraps `__read_user_stack()` for 64-bit words.
- `struct signal_frame_64` models the 64-bit signal frame including ucontext, trampoline, siginfo, and ABI gap.
- `is_sigreturn_64_address()` detects frame-local or VDSO `sigtramp_rt64` return trampolines.
- `sane_signal_64_frame()` verifies `pinfo` and `puc` pointers point to the signal frame's embedded `info` and `uc`.
- `perf_callchain_user_64()` walks frame records and restarts unwinding from signal frame saved registers.

## Control Flow

The unwinder reads the next stack pointer from the frame and, after level zero, reads saved IP from `fp[2]`. It treats a sufficiently large frame with a recognized sigreturn address and sane embedded pointers as a signal frame, then loads saved NIP/LR/R1 from `uc.uc_mcontext.gp_regs`, emits a user context marker, stores the resumed IP, and continues. Normal frames store LR at level zero and saved frame IP thereafter.

## State And Persistence

Only per-sample local variables and the perf callchain entry are modified. User memory is accessed through nofault copies.

## Dependencies And Integration Points

It depends on 64-bit PowerPC ABI frame layout, VDSO `sigtramp_rt64`, signal/ucontext structures, `PT_*` register indexes, and common callchain helpers.

## Risks And Edge Cases

The saved return address slot differs from 32-bit (`fp[2]`). Alternate signal stack transitions rely on unsigned size arithmetic. Bad user memory terminates the unwind safely. Signal-frame pointer sanity protects against mistaking arbitrary frames for signal frames.

## Test Signals

Run `perf record -g` on 64-bit processes with nested calls, signal handlers, alternate stacks, and VDSO trampolines. Include tests for invalid stack alignment and unreadable user pages.
