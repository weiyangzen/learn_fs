
# sources/distributed-fs/ceph-client/arch/powerpc/perf/callchain.c

## Purpose

This file provides common PowerPC perf callchain collection. It handles kernel stack frame walking and dispatches user stack unwinding to 32-bit or 64-bit implementations.

## Important APIs, Types, And Functions

- `valid_next_sp()` validates 16-byte alignment, current-task stack validity, monotonic frame growth, and legitimate interrupt-stack-to-process-stack transitions.
- `perf_callchain_kernel()` stores the current instruction pointer, walks kernel frame records, detects interrupt frames using `STACK_FRAME_REGS_MARKER`, switches context back to kernel after interrupt frames, and records LR-derived caller addresses.
- `perf_callchain_user()` stores the current IP, checks `current->mm`, and dispatches to `perf_callchain_user_64()` or `perf_callchain_user_32()`.

## Control Flow

Kernel unwinding starts from `regs->gpr[1]` and `regs->link`. Each frame yields `next_sp`; interrupt frames replace `regs`, `next_ip`, and `lr` from saved registers. Normal frames use LR for the first caller and saved LR for later callers, filtering suspicious first frames to zero rather than deleting them. User unwinding is architecture-width-specific.

## State And Persistence

The file stores callchain entries into the perf-provided `perf_callchain_entry_ctx`. It does not persist data beyond the sample. It reads current task stack state and `pt_regs`.

## Dependencies And Integration Points

It depends on PowerPC stack frame layout constants, `validate_sp()`, `validate_sp_size()`, perf callchain APIs, `perf_arch_instruction_pointer()`, and the user unwind functions declared in `callchain.h`.

## Risks And Edge Cases

Stack validation is the safety boundary. Interrupt-frame detection must match actual stack layout. Early frame LR ambiguity is handled conservatively by recording zero for obviously invalid addresses. Kernel unwinding is marked `__no_sanitize_address` because it inspects raw stack frames.

## Test Signals

Use `perf record -g` in kernel-heavy workloads, interrupt-heavy workloads, and mixed user/kernel samples. Validate callchains around interrupt entry/exit, task stacks, and stack overflow guards. KASAN builds should confirm the sanitizer exclusion remains sufficient.
