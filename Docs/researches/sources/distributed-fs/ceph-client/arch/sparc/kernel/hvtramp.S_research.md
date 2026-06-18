# sources/distributed-fs/ceph-client/arch/sparc/kernel/hvtramp.S

## Purpose
`hvtramp.S` is the sun4v hypervisor secondary-CPU startup trampoline. It runs with physical addressing, installs required permanent mappings and fault areas, enables the MMU, initializes CPU-local kernel state, and enters SMP bring-up.

## Important APIs, Types, and Functions
Global symbols are `hv_cpu_startup` and `hv_cpu_startup_end`. It consumes a descriptor in `%o0` using `HVTRAMP_DESCR_*` and `HVTRAMP_MAPPING_*` offsets and calls hypervisor traps for permanent mapping, fault-area configuration, and MMU enablement.

## Control Flow and State
The trampoline initializes privileged CPU registers, trap table base, scratchpad CPU ID and fault-info virtual address, iterates descriptor mappings with `HV_FAST_MMU_MAP_PERM_ADDR`, configures the fault area, sets privileged PSTATE, loads the thread register, enables the MMU and branches to a virtual continuation. After MMU enable it clears FPRS/ASI, zeros primary/secondary contexts, sets `%g6`, current task, and stack, initializes IRQ work, registers mondo queues, initializes current CPU trap state, enables interrupts, calls `smp_callin()`, and panics if it returns. Any HV failure loops forever.

## Persistence and Dependencies
State includes CPU privileged registers, scratchpad registers, MMU permanent mappings, trap table base, thread register, stack pointer, and per-CPU mondo queues. Dependencies include descriptor layout, hypervisor ABI, trap block state, `init_cur_cpu_trap()`, and SMP bring-up.

## Integration Points, Risks, and Test Signals
Integration is with sun4v SMP CPU start (`sun4v_cpu_start()`), irq mondo setup, and trap initialization. Risks include descriptor mismatch, no diagnostics on failure loops, mapping order errors before MMU enable, and calling routines that rely on not-yet-initialized CPU state. Test signals are secondary CPU online success, correct hard CPU IDs, registered mondo queues, working IPIs on hotplugged CPUs, and no early trap-table faults.
