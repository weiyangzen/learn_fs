# sources/distributed-fs/ceph-client/arch/s390/kernel/entry.S

## Purpose
Implements core s390 low-level entry and exit paths: context switch assembly, KVM SIE entry/exit, syscall entry, program checks, external and I/O interrupts, machine checks, restart interrupts, early program checks, invalid-stack panic setup, and branch-prediction isolation toggles.

## Important APIs, Types, And Functions
Global symbols include `__switch_to_asm`, `__WARN_trap`, `__sie64a`, `sie_exit`, `system_call`, `ret_from_fork`, `pgm_check_handler`, `ext_int_handler`, `io_int_handler`, `mcck_int_handler`, `restart_int_handler`, `early_pgm_check_handler`, and `stack_invalid`. Macros include `STBEAR`, `LBEAR`, `LPSWEY`, `MBEAR`, `CHECK_VMAP_STACK`, `TSTMSK`, `BPOFF`, `BPON`, `BPENTER`, `BPEXIT`, and `SIEEXIT`.

## Control Flow
Entry paths save volatile state into lowcore or stack frames, switch to the correct task or per-CPU stack, sanitize user-controlled registers for speculation safety, build `pt_regs`, call C handlers, restore PSWs/registers, and exit through lowcore LPSWE sequences. KVM SIE saves host state, loads guest registers/asce, enters SIE, handles exits and machine-check races, then restores host state. Machine-check handling validates available state, may stop all CPUs on severe damage, or calls `s390_do_machine_check`.

## State And Persistence
Mutates lowcore save areas, current task pointers, stack frames, SIE flags, per-CPU control flags, branch-prediction state, and machine-check stop-lock data. No filesystem persistence.

## Dependencies And Integration Points
Depends on generated asm offsets, lowcore layout, alternative patching, nospec branch support, KVM SIE block layout, stack protector, irq/trap C handlers, restart infrastructure, and ftrace/kprobes section placement.

## Risks And Edge Cases
This is one of the highest-risk files. Stack selection, PSW bits, SIE race windows, machine-check validity masks, branch-prediction isolation, VMAP stack validation, and speculation register clearing must be exact. A wrong offset or alternative patch can prevent boot.

## Test Signals
Signals include boot, syscall stress, signal return, interrupts, KVM guest tests, machine-check injection, restart IPI paths, ftrace/kprobe interactions, VMAP stack fault tests, and objdump/ORC-style inspection of generated entry code.
