# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/spinlock.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/spinlock.h

Purpose: minimal arm64 guest spinlock interface for KVM selftests. It exposes a one-word `struct spinlock` and external `spin_lock`/`spin_unlock` routines implemented elsewhere, typically in guest-support assembly or library code.

Important APIs/types/functions: `struct spinlock { uint32_t v; }`, `spin_lock(struct spinlock *)`, and `spin_unlock(struct spinlock *)`.

Control flow and state: all state is contained in the lock word. The header does not specify memory ordering directly; the implementation must provide atomic acquire/release behavior suitable for concurrent guest vCPUs.

Dependencies and integration: consumed by arm64 guest test code that needs in-guest synchronization. It relies on an architecture implementation being linked into the selftest binary.

Risks: since the header provides no inline semantics, callers depend completely on the linked implementation. ABI changes to `struct spinlock` would break guest code compiled against this header.

Test signals: multi-vCPU arm64 guest tests that share guest memory and use spinlocks are the meaningful validation path; linker failures catch missing implementations.
