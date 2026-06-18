# sources/distributed-fs/ceph-client/arch/microblaze/kernel/misc.S

Purpose: implements low-level TLB invalidation helpers for MicroBlaze MMU.

Important symbols and state: `_tlbia` invalidates all non-pinned TLB entries starting at `tlb_skip`; `_tlbie` invalidates a single virtual address by searching with `rtlbsx` and clearing `rtlbhi` if found.

Control flow: `_tlbia` loops over TLB indices through `MICROBLAZE_TLB_SIZE - 1`, skipping entries pinned by boot. `_tlbie` loads the search address into `rtlbsx`, reads the resulting `rtlbx`, and clears valid state for hits.

State and persistence: mutates hardware TLB entries. No memory allocation or data persistence except using `tlb_skip`.

Dependencies and integration: called by MMU/page-table and context code through tlbflush helpers. Depends on `tlb_skip` from hardware exception handling.

Risks and test signals: invalidating pinned entries would unmap the kernel; not invalidating enough leaves stale translations. Test `flush_tlb_all`, `flush_tlb_page`, context stealing, ioremap/unmap, and page permission changes.
