# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_64_mmu_host.c

## Purpose
Manages host shadow hash-MMU mappings for 64-bit Book3S PR KVM. It maps translated guest PTEs into host HPTEs, manages guest-to-host VSID mappings and shadow SLB entries, flushes segments, and initializes/destroys PR MMU context state.

## Important APIs, Types, And Functions
Exports `kvmppc_mmu_invalidate_pte`, `kvmppc_mmu_map_page`, `kvmppc_mmu_unmap_page`, `kvmppc_mmu_map_segment`, `kvmppc_mmu_flush_segment`, `kvmppc_mmu_flush_segments`, `kvmppc_mmu_destroy_pr`, and `kvmppc_mmu_init_pr`. Helpers include `kvmppc_sid_hash`, `find_sid_vsid`, `create_sid_map`, and `kvmppc_mmu_next_segment`.

## Control Flow
Page mapping snapshots `mmu_invalidate_seq`, faults in the GPA to a host PFN, ensures a host VSID/SLB mapping exists, computes VPN/hash, allocates an HPTE cache record, and inserts a primary or secondary HPTE using `mmu_hash_ops`. On collisions it retries secondary and may remove old entries after repeated attempts. Segment mapping chooses or allocates a shadow SLB slot, translates guest ESID to VSID, creates a scrambled host VSID, and writes an SLB entry with optional 64K page-size encoding. Context init allocates a hash context ID and derives a proto-VSID range.

## State And Persistence
Per-vCPU state includes context ID, proto-VSID cursor/range, SID map array, shadow SLB entries, and HPTE cache entries. Per-VM state includes the host hash table and invalidation sequence. Dirty pages are marked when writable mappings are installed.

## Dependencies And Integration Points
Depends on `mmu_hash_ops`, hash context allocation, VSID scrambling, pkey-to-HPTE permission bits, HPTE cache helpers, `kvmppc_gpa_to_pfn`, KVM MMU notifier sequencing, and shadow-vCPU accessors. It pairs with `book3s_64_mmu.c` for guest translation.

## Risks And Edge Cases
MMU invalidation races are controlled by sequence checks under `kvm->mmu_lock`; missing a retry risks installing stale PFNs. 64K host-page handling must preserve low guest real-address bits when the guest segment is not 64K-capable. SID-map collisions and proto-VSID exhaustion flush segments and PTEs. The source snapshot contains a duplicated `if (backwards_map)` line, a compile/logic risk if active.

## Test Signals
Signals include 64-bit PR guest boot, host page invalidation under memory pressure, dirty logging, 64K-page kernels, NX mappings, writable-to-readonly downgrade, SLB exhaustion, VSID wraparound, HPTE insertion collisions, and vCPU teardown freeing contexts.
