<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/uv/uv_irq.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/uv/uv_irq.c

## Purpose
Provides a UV-specific IRQ domain that programs UV hub MMR route entries for platform interrupts.

## Important APIs, Types, And Functions
`struct uv_irq_2_mmr_pnode` stores MMR offset and pnode. `uv_setup_irq()` allocates an IRQ/vector for a target CPU and programs the hub route; `uv_teardown_irq()` frees it. `uv_set_irq_affinity()` retargets parent vector affinity and updates the MMR.

## Control Flow
The domain is created lazily under a mutex as a child of `x86_vector_domain`. Allocation validates UV type, allocates chip data, allocates a parent vector, sets `IRQ_NO_BALANCING` if requested, and installs `uv_irq_chip`. Activation and affinity changes call `uv_program_mmr()` to write vector/destination fields into the hub MMR.

## State And Persistence
Per-IRQ chip data persists until domain free. Hardware MMR route entries persist until deactivation/teardown masks them.

## Dependencies And Integration Points
Integrates x86 vector IRQ domain, APIC destination mode, UV blade-to-pnode mapping, global MMR writes, and UV platform users needing MSI-like interrupts.

## Risks And Edge Cases
Route programming must match vector allocation exactly. Deactivation constructs a masked entry but relies on `uv_program_mmr()` semantics. CPU affinity changes need vector cleanup scheduling to avoid stale delivery.

## Test Signals
Successful `uv_setup_irq()` users, correct interrupt delivery to requested CPUs, affinity retargeting, and no leaked vectors after teardown validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/uv/uv_irq.c -->
