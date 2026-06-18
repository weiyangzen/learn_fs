# sources/distributed-fs/ceph-client/arch/mips/include/asm/mmiowb.h

Purpose: MIPS implementation of the MMIO write barrier hook.

Important APIs/types/functions: Defines `mmiowb()` as `wmb()` and then includes `asm-generic/mmiowb.h`.

Control flow, state, and persistence: The macro emits a write memory barrier where generic locking/MMIO code requests ordering of prior MMIO writes. No persistent software state is introduced here.

Dependencies and integration: Depends on `asm/barrier.h` and the generic mmiowb framework. It integrates with driver spinlock-unlock paths and architectures needing explicit posted-write ordering.

Risks and test signals: If `wmb()` is too weak for a platform’s MMIO ordering, drivers can observe device register writes out of order. Test with driver MMIO ordering stress, SMP device access under locks, and architecture barrier litmus tests.
