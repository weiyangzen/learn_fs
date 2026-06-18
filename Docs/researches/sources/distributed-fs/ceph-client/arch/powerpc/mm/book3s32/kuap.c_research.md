<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/kuap.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/kuap.c

## Purpose
This file enables or disables Kernel Userspace Access Protection for Book3S32 segment registers.

## Important APIs, types, and functions
`void setup_kuap(bool disabled)` updates segment register KS state and CPU MMU feature flags.

## Control flow
When KUAP is enabled, it sets `SR_KS` in current user segments, synchronizes with `isync`, and updates `init_mm.context.sr0` and `current->thread.sr0`. On non-boot CPUs it returns after local setup; on the boot CPU it either clears `MMU_FTR_KUAP` when disabled or logs activation.

## State and persistence behavior
It mutates segment registers, initial/current thread segment context, and `cur_cpu_spec->mmu_features`.

## Dependencies and integration points
Used during PowerPC KUAP setup and interacts with hash fault permission filtering in `hash_low.S`.

## Risks and edge cases
Segment register synchronization is required after updates. Boot CPU versus secondary CPU behavior must avoid global feature churn on secondary bring-up.

## Test signals
Signals include activation log, enforced blocked kernel user access when KUAP is enabled, and no KUAP feature when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/kuap.c -->
