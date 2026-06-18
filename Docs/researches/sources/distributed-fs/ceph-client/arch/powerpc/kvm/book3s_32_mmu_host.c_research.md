# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_32_mmu_host.c

## Purpose
Creates and manages host shadow hash-page-table entries for 32-bit Book3S PR KVM. It maps translated guest PTEs to host physical pages, maintains guest-VSID to host-VSID mappings, flushes shadow segments, and initializes/destroys PR MMU host context state.

## Important APIs, Types, And Functions
Exports `kvmppc_mmu_invalidate_pte`, `kvmppc_mmu_map_page`, `kvmppc_mmu_unmap_page`, `kvmppc_mmu_map_segment`, `kvmppc_mmu_flush_segments`, `kvmppc_mmu_destroy_pr`, and `kvmppc_mmu_init_pr`. Helpers include `kvmppc_sid_hash`, `find_sid_vsid`, `kvmppc_mmu_get_pteg`, and `create_sid_map`. File-level globals `htab` and `htabmask` mirror the host SDR1 hash table.

## Control Flow
Initialization allocates multiple MMU context IDs, fills a pool of host VSIDs, records the host HTAB base/mask from SDR1, and initializes the HPTE cache. Segment mapping converts a guest ESID to a guest VSID using the active MMU callback, finds or creates a host VSID, and writes a shadow segment register. Page mapping faults in a host PFN, ensures a shadow segment exists, computes the host PTEG, picks a free or evicted slot, writes a 32-bit HPTE pair with interrupts disabled, and records it in the HPTE cache. Invalidations zero the HPTE and issue `tlbie`.

## State And Persistence
Persistent runtime state is per-vCPU context IDs, VSID pool cursors, SID map entries, shadow segment registers, HPTE cache entries, and host HTAB entries. Dirty pages are marked when writable mappings are created. All state is in-memory and is destroyed with the vCPU.

## Dependencies And Integration Points
Depends on 32-bit hash MMU definitions, context allocation/destruction, `kvmppc_gpa_to_pfn`, HPTE cache helpers, shadow-vCPU accessors, host SDR1, and local IRQ/TLB primitives. It is paired with `book3s_32_mmu.c` for guest translation.

## Risks And Edge Cases
The file explicitly rejects SMP and 64-bit PTE builds, so configuration coverage matters. Shadow HTAB insertion can evict entries after primary/secondary scans. Host VSID pool exhaustion flushes all mappings. Page references must be released correctly on HPTE cache exhaustion. Local IRQ disabling protects HPTE writes but broader hash-locking is unavailable in the supported uniprocessor configuration.

## Test Signals
Run 32-bit PR guests through hash faults, segment remaps, writable/read-only mappings, HPTE eviction, VSID pool wraparound, vCPU teardown, and TLB invalidation. Build tests should verify the SMP and PTE_64BIT exclusions remain enforced.
