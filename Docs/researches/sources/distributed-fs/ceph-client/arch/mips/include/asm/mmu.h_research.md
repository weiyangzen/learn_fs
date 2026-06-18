# sources/distributed-fs/ceph-client/arch/mips/include/asm/mmu.h

Purpose: Defines the MIPS `mm_context_t` structure stored in each `mm_struct`.

Important APIs/types/functions: `mm_context_t` contains either per-CPU ASIDs (`u64 asid[NR_CPUS]`) or a global `atomic64_t mmid`, a `vdso` pointer, and delay-slot emulation page tracking: `bd_emupage_lock`, `bd_emupage_allocmap`, and `bd_emupage_queue`.

Control flow, state, and persistence: No functions. The state persists for the lifetime of a process address space and is initialized/cleaned by `mmu_context.h` helpers.

Dependencies and integration: Depends on atomic, spinlock, and waitqueue types. Integrated with ASID/MMID allocation, context switching, VDSO mapping, and branch-delay-slot emulation.

Risks and test signals: The union means code must choose ASID vs MMID paths consistently based on `cpu_has_mmid`. Test process creation/destruction, ASID rollover, MMID-capable CPUs, VDSO access, and branch-delay emulation allocation contention.
