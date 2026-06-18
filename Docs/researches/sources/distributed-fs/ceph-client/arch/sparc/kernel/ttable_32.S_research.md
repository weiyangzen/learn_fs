<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/ttable_32.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/ttable_32.S

## Purpose
Defines the SPARC32 trap table starting at `_start`, including boot entry, hardware traps, interrupt levels, syscall traps, register-window traps, compatibility traps, and optional SMP per-CPU trap tables.

## Important APIs, Types, And Functions
Primary exported labels are `_start`, `_stext`, `trapbase`, `trapbase_cpu0` through `trapbase_cpu3` under SMP, `t_nmi`, and `end_traptable`. The table is built with macros including `TRAP_ENTRY`, `TRAP_ENTRY_INTERRUPT`, `BAD_TRAP`, `SRMMU_TFAULT`, `SRMMU_DFAULT`, `WINDOW_SPILL`, `WINDOW_FILL`, `BREAKPOINT_TRAP`, `LINUX_SYSCALL_TRAP`, `GETCC_TRAP`, `SETCC_TRAP`, `GETPSR_TRAP`, and `KGDB_TRAP`.

## Control Flow
Hardware vectors index directly into fixed-width trap-table slots. The reset vector branches to `gokernel`; memory-management faults enter SRMMU handlers; window overflow and underflow branch to the dedicated window assembly; interrupts dispatch by level; trap `0x90` enters the Linux syscall path; selected software traps implement breakpoint, flush-window, get/set condition codes, and get-PSR behavior. Most unused vectors explicitly land in `BAD_TRAP`.

## State And Persistence
The file defines static boot and trap-table code rather than mutable runtime state. Under SMP, duplicate trap tables persist for secondary CPUs so each CPU can use the same vector layout.

## Dependencies And Integration Points
It depends on SPARC32 trap macros and handlers from entry, fault, syscall, IRQ, KGDB, SRMMU, and window-management code. Link placement is controlled by the kernel linker script and the `__HEAD` section.

## Risks And Edge Cases
Trap slots are architectural ABI: instruction count, alignment, and vector number must be exact. SMP duplicate tables must stay semantically equivalent to the boot CPU table. Misrouting trap `0x90` or register-window traps would break basic process execution.

## Test Signals
Signals include SPARC32 boot to `gokernel`, syscall smoke tests, timer and device IRQ handling, page faults, illegal instruction and divide-by-zero traps, register-window spill/fill paths, KGDB/breakpoint traps, and SMP secondary CPU bring-up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/ttable_32.S -->
