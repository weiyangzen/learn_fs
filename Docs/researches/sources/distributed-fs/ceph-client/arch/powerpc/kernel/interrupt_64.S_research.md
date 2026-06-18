# sources/distributed-fs/ceph-client/arch/powerpc/kernel/interrupt_64.S

## Purpose
Contains 64-bit PowerPC low-level syscall entry/exit, interrupt return, restart-table protected return sequences, fork return trampolines, and register sanitization/restoration paths.

## Important APIs, Types, And Functions
Defines `system_call_common_real`, `system_call_common`, `system_call_vectored_common`, `system_call_vectored_sigill`, `fast_interrupt_return_srr`, generated `interrupt_return_srr`, generated `interrupt_return_hsrr`, `ret_from_fork_scv`, `ret_from_fork`, `ret_from_kernel_user_thread`, and `start_kernel_thread`. Macros include `DEBUG_SRR_VALID`, `system_call_vectored`, and `interrupt_return_macro`. It uses PACA fields for save areas, IRQ soft masks, pending IRQs, SRR validity, and restart save state.

## Control Flow
System call entry saves user state into the kernel stack frame, sets up PACA/TOC, records syscall arguments and `pt_regs`, soft-disables IRQs, enables hard interrupts where appropriate, sanitizes volatile user registers, and calls `system_call_exception`. Exit calls `syscall_exit_prepare`, enters a restart-protected sequence that checks pending soft-masked interrupts, restores SRR/LR/CTR/XER/CR/GPRs, optionally restores all registers, and returns via `rfid` or `rfscv`. Generic interrupt return calls C user/kernel prepare helpers, saves restart R1, reconciles PACA soft-mask state, restores SRR or HSRR, clears reservations, restores registers, handles emulated stack-store update, and returns to user or kernel. Restart labels reload PACA/TOC and re-enter C prepare functions when an interrupt arrives during a return sequence.

## State And Persistence
State is the interrupt frame on the kernel stack, PACA save slots (`PACAKSAVE`, `PACA_EXIT_SAVE_R1`, `PACAIRQSOFTMASK`, `PACAIRQHAPPENED`, SRR-valid flags), architectural SRR/HSRR/LR/CTR/XER/CR/GPRs, and optional PPR. It is transient return-path state and not durable.

## Dependencies And Integration Points
Depends on exception-64s/64e macros, `syscall_exit_prepare`, `syscall_exit_restart`, `interrupt_exit_user_prepare`, `interrupt_exit_kernel_prepare`, restart and soft-mask table machinery, KUAP macros, register sanitization configuration, SCV support, and schedule tail for fork/thread return. It integrates directly with the C code in `interrupt.c`.

## Risks And Edge Cases
Return paths are extremely sensitive to register ordering, PACA soft-mask atomics, SRR validity, speculative execution barriers, clearing load/store reservations, and not restoring sensitive kernel register contents to user state. Restart tables must exactly cover windows where pending interrupts can redirect control. The emulated `stdu` stack-store path must avoid clobbering the frame before all registers are restored.

## Test Signals
Signals include syscall ABI tests for `sc` and `scv`, signal and ptrace register restoration, fork/kernel-thread startup, interrupt storm tests during syscall/interrupt return, KUAP debug checks, RFI SRR debug warnings, register-sanitization builds, KASAN/lockdep IRQ tracing, and Book3S HSRR interrupt return coverage.
