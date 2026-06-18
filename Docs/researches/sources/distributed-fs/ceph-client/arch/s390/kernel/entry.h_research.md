# sources/distributed-fs/ceph-client/arch/s390/kernel/entry.h

## Purpose
Declares internal s390 entry, trap, syscall, interrupt, restart, AMODE31, stack, and architecture syscall interfaces shared between assembly and C files.

## Important APIs, Types, And Functions
Declares assembly symbols such as `system_call`, interrupt handlers, `early_pgm_check_handler`, and `__switch_to_asm`; C handlers such as `__do_pgm_check`, `__do_syscall`, `do_ext_irq`, `do_io_irq`, and `die`; architecture syscalls such as `sys_s390_guarded_storage`, `sys_s390_runtime_instr`, and PCI MMIO helpers; stack allocation helpers; and AMODE31 section symbols. It defines `__amode31_data` and `__amode31_ref`.

## Control Flow
No executable flow. It provides prototypes so entry assembly and C code agree on call targets and calling conventions.

## State And Persistence
No state is owned. It declares external symbols that refer to runtime stacks, AMODE31 ranges, and entry points.

## Dependencies And Integration Points
Depends on percpu, signal, ptrace, idle, extable, and s390 type headers. It connects `entry.S`, trap handling, guarded storage, signal handling, AMODE31 diagnose code, and syscall implementations.

## Risks And Edge Cases
Prototype drift can create subtle ABI bugs between assembly and C. AMODE31 section annotations must remain correct so references are placed in the expected sections.

## Test Signals
Signals include full s390 build with warnings enabled, boot of entry paths, syscall tests, AMODE31 diagnose users, and link-time symbol resolution.
