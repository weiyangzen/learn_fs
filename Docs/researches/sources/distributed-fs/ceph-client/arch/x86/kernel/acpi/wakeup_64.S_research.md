# sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/wakeup_64.S

## Purpose
`wakeup_64.S` implements the 64-bit x86 ACPI S3 low-level suspend entry and long-mode wakeup return. It saves general-purpose and control-register state, enters ACPI sleep state S3, and restores enough state after wake to jump back to the saved kernel instruction pointer.

## Important APIs, Types, and Functions
- `wakeup_long64` is the 64-bit wakeup entry set through `initial_code` by `sleep.c`.
- `do_suspend_lowlevel` saves processor state and register context, calls `x86_acpi_enter_sleep_state(3)`, and restores state at `.Lresume_point`.
- Data symbols include saved callee-saved registers, saved RIP/RSP, `saved_magic`, and `saved_context` fields populated through `asm-offsets.h`.
- The function is marked `STACK_FRAME_NON_STANDARD` because it has non-standard suspend/resume control flow.

## Control Flow
`do_suspend_lowlevel()` creates a small frame, calls `save_processor_state`, stores a `pt_regs`-like context plus resume RIP/RSP and callee-saved registers, calls `x86_acpi_enter_sleep_state(3)`, and jumps to `.Lresume_point` if sleep entry returns. On wake, `wakeup_long64` checks `saved_magic == 0x123456789abcdef0`, reloads segment registers, restores saved stack and callee-saved registers, then jumps to the saved RIP. `.Lresume_point` restores CR4/CR3/CR2/CR0, flags, general registers, optionally unpoisons the task stack for KASAN stack mode, clears `eax`, and jumps to `restore_processor_state`.

## State and Persistence Behavior
The file persists resume state in static data and in the `saved_context` structure. `saved_magic` is a guard against jumping into stale or corrupted resume data; mismatch enters an infinite diagnostic loop with a marker in `rcx`.

## Dependencies and Integration Points
It depends on `sleep.c`, `sleep.h`, saved processor-state helpers, x86 segment constants, MSR/page-table definitions, retpoline annotations, frame macros, KASAN stack unpoisoning, and ACPI sleep entry.

## Risks
- Control register restoration order and saved context layout must match `asm-offsets.h`; drift can crash resume.
- The path intentionally bypasses normal C call/return expectations, so tracing, unwinding, and sanitizers need special handling.
- Magic mismatch or wrong wake vector produces a hard hang during resume.

## Test Signals
- Run S3 suspend/resume on `CONFIG_X86_64`, including SMP systems.
- Build with KASAN stack mode to exercise the unpoison call.
- Check objtool warnings for the non-standard stack frame annotation.
