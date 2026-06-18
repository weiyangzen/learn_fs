# sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/wakeup_32.S

## Purpose
`wakeup_32.S` implements the 32-bit protected-mode return path and low-level suspend entry for x86 ACPI S3. It saves CPU register context before sleep, calls into ACPI sleep state entry, and restores state after firmware wakes the system.

## Important APIs, Types, and Functions
- `wakeup_pmode_return` is the protected-mode resume entry programmed into the real-mode wakeup header by `sleep.c`.
- `do_suspend_lowlevel` saves processor/register state and calls `x86_acpi_enter_sleep_state(3)`.
- Local helpers `save_registers` and `restore_registers` save IDT/LDT/TSS, stack, callee-saved registers, flags, and the resume EIP.
- Data symbols include `saved_magic`, `saved_eip`, `saved_idt`, `saved_ldt`, and `saved_tss`.

## Control Flow
Before entering S3, `do_suspend_lowlevel()` calls `save_processor_state()`, saves registers, pushes state `3`, and calls `x86_acpi_enter_sleep_state()`. If entry fails or after wakeup, control reaches `ret_point`, restores registers and processor state, and returns to C. On a successful resume through firmware, `wakeup_pmode_return` reloads segment registers and descriptor tables, flushes CR3, executes `wbinvd`, restores the saved stack, checks `saved_magic == 0x12345678`, and jumps to `saved_eip`.

## State and Persistence Behavior
The assembly stores resume-critical CPU state in static data symbols and relies on `sleep.c` setting `saved_magic`. A magic mismatch loops forever at `bogus_magic`, preventing return into a corrupted context.

## Dependencies and Integration Points
This file integrates with `sleep.c`, `sleep.h`, `save_processor_state()`, `restore_processor_state()`, real-mode wakeup trampoline setup, x86 segment constants, and ACPI sleep state entry.

## Risks
- Resume correctness depends on exact descriptor, stack, CR3, and magic state.
- The infinite `bogus_magic` loop is deliberate but produces a hard hang when resume state is wrong.
- Assembly/C symbol and calling-convention mismatches can break S3 only on 32-bit builds, making coverage easy to miss.

## Test Signals
- Build `CONFIG_X86_32` with ACPI sleep enabled.
- Run S3 suspend/resume and verify return from `do_suspend_lowlevel()` without magic mismatch.
- Fault-injection or instrumentation can validate the failure path by corrupting `saved_magic` in a controlled debug build.
