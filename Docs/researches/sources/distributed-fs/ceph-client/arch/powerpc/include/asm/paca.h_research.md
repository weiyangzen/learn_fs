<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/paca.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/paca.h

## Purpose
This header defines the per-CPU PACA structure for 64-bit PowerPC, a low-level control block accessed through register `r13` for current task, exception, MMU, idle, accounting, KVM, and platform state.

## Important APIs, Types, And Functions
It declares `local_paca`, `get_paca()`, `get_slb_shadow()`, `struct paca_struct`, `copy_mm_to_paca()`, `paca_ptrs`, `initialise_paca()`, `setup_paca()`, `allocate_paca_ptrs()`, `allocate_paca()`, and `free_unused_pacas()`. The structure includes lppaca pointers, lock token/index, TOC/kernelbase/MSR, emergency stacks, per-CPU data offset, exception save areas, SLB and Book3E TLB data, current task, stack saves, soft IRQ mask state, idle state, accounting, KVM host state, speculation flush state, MCE/HMI state, stack canary, and MMIO write-barrier state.

## Control Flow
Early CPU setup allocates and installs PACA records. Exception entry/exit, scheduling, RTAS, idle, KVM, and low-level locking paths read and update PACA fields directly, often before normal per-CPU access is available.

## State And Persistence Behavior
PACA is long-lived per logical CPU kernel state. Some fields are read-mostly after boot; many are hot exception-path mutable state. Alignment and cacheline placement are part of the performance and correctness contract.

## Dependencies And Integration Points
It depends on PPC64, exception layout headers, MMU/page definitions, accounting, HMI/MCE, KVM, lppaca, and generic mmiowb types. It integrates with almost every low-level 64-bit PowerPC path.

## Risks And Edge Cases
Field layout is assembly-sensitive. `lock_token` and `paca_index` must stay paired. Preemption around `local_paca` access is debug-checked. Cacheline sharing can hurt interrupt and lock paths.

## Test Signals
Boot SMP PPC64, CPU hotplug, KVM, RTAS, idle, NMI/MCE/HMI handling, lock primitives, stack protector, and debug-preempt PACA access checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/paca.h -->
