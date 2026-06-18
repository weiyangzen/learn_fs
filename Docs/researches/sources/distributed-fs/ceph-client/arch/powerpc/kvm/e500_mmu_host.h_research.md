
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/e500_mmu_host.h

## Purpose
Declares the small host-shadow MMU interface consumed by guest-side e500 MMU code and e500 vCPU setup. It is the boundary between software guest TLB emulation and hardware host TLB shadowing.

## Important APIs, Types, And Functions
The header exposes `inval_gtlbe_on_host(struct kvmppc_vcpu_e500 *, int tlbsel, int esel)`, `e500_mmu_host_init(struct kvmppc_vcpu_e500 *)`, and `e500_mmu_host_uninit(struct kvmppc_vcpu_e500 *)`. It relies on `struct kvmppc_vcpu_e500` being declared by including e500-specific headers before or around this header.

## Control Flow
`e500_mmu.c` calls `inval_gtlbe_on_host()` before invalidating or overwriting guest TLB entries that may have host shadow mappings. `e500mc.c`/e500 setup indirectly call `e500_mmu_host_init()` during TLB initialization and `e500_mmu_host_uninit()` during teardown.

## State And Persistence
The header owns no state. Its implementation allocates per-vCPU reverse-map state and reads global host TLB geometry.

## Dependencies And Integration Points
Included by both `e500_mmu.c` and `e500_mmu_host.c`; it prevents either side from reaching through implementation details. It forms part of the BookE/e500 KVM private interface rather than a userspace ABI.

## Risks
Because only targeted invalidation and lifecycle hooks are declared here, callers must still separately call broader flush APIs such as `kvmppc_core_flush_tlb()` when they invalidate all software TLB state. Incorrect call ordering around guest TLB writes can leave stale host shadow mappings.

## Test Signals
Build coverage catches signature drift. Runtime evidence comes from e500 TLB invalidation tests or guest workloads that overwrite TLB entries and verify stale translations are not observed.
