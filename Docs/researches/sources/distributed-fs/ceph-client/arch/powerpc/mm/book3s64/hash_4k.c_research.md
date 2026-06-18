<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hash_4k.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hash_4k.c

## Purpose
This file implements 4 KiB hash page insertion/update for 64-bit Book3S hash MMUs.

## Important APIs, types, and functions
`int __hash_page_4K(...)` is the central function. It uses `pte_xchg`, `check_pte_access`, `htab_convert_pte_flags`, `__real_pte`, `hash_page_do_lazy_icache`, `hpt_vpn`, `pte_get_hash_gslot`, `mmu_hash_ops.hpte_updatepp`, `hpt_hash`, `mmu_hash_ops.hpte_insert`, `mmu_hash_ops.hpte_remove`, `pte_set_hidx`, `stress_hpt`, and `hpt_do_stress`.

## Control flow
The function atomically locks the Linux PTE with `H_PAGE_BUSY`, verifies access permissions, sets accessed/dirty as needed, converts PTE flags to HPTE flags, and tries to update an existing HPTE if `H_PAGE_HASHPTE` is set. If no valid HPTE remains, it computes VPN/hash, tries primary insertion, then secondary insertion, evicts a random-ish primary/secondary group when both are full, and retries. Hypervisor insertion failure restores the old PTE and returns `-1`; permission miss returns `1`; busy PTE returns `0` for retry.

## State and persistence behavior
It mutates the PTE busy/accessed/dirty/hash-index bits, inserts/updates/removes HPTEs through `mmu_hash_ops`, may perform lazy icache state changes, and optionally triggers hash stress behavior.

## Dependencies and integration points
Integrated with Book3S64 hash page fault handling for 4K pages, page-table flag conversion, MMU hash operation backend, lazy icache coherency, and stress/debug infrastructure.

## Risks and edge cases
Risks include leaving `H_PAGE_BUSY` set on unusual exits, stale HPTE index data, races with concurrent faults/unmaps, hypervisor failure recovery, primary/secondary full-group eviction choice, and correct dirty/access permission handling.

## Test signals
Signals include successful hash faults, correct permission faults, no PTE busy hangs, expected HPTE insertion/update behavior, and stress-hash robustness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hash_4k.c -->
