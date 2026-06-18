# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_hmc.c

## Purpose
`i40e_hmc.c` implements low-level Host Memory Cache backing-store management for i40e. It allocates, reference-counts, invalidates, and frees segment descriptors, page descriptor tables, page descriptors, and backing pages used by higher-level LAN HMC code.

## Important APIs, types, and functions
- `i40e_add_sd_table_entry()` allocates and initializes a segment descriptor in direct or paged mode, including DMA backing memory and paged-mode software PD bookkeeping.
- `i40e_add_pd_table_entry()` allocates or attaches a 4 KiB backing page for a page descriptor, writes the physical page descriptor value into the PD page, and updates PD/BP reference counts.
- `i40e_remove_pd_bp()` decrements and, when the reference count reaches zero, invalidates and frees a paged backing page.
- `i40e_prep_remove_sd_bp()` and `i40e_remove_sd_bp_new()` split direct SD removal into software reference-count/validity preparation and PF hardware invalidation/free.
- `i40e_prep_remove_pd_page()` and `i40e_remove_pd_page_new()` split paged SD PD-page removal into software preparation and PF hardware invalidation/free.

## Control flow and behavior
The add path first validates the HMC software tables and index bounds. Direct mode allocates one DMA memory range sized by the caller, records it as `sd_entry->u.bp`, and increments the SD and BP reference counts. Paged mode allocates a 4 KiB PD page, allocates a 512-entry virtual `struct i40e_hmc_pd_entry` array for software bookkeeping, records the PD page DMA memory, and increments the SD reference count. The segment is not marked hardware-valid here; the LAN HMC layer marks it valid and writes PFHMC SD registers.

Paged backing-page creation computes `sd_idx` and `rel_pd_idx` from a global PD index. It only operates if the containing SD is paged. It either uses a caller-supplied resource page or allocates a new DMA page, stores `page->pa | 0x1` into the PD page, marks the PD entry valid, increments the PD table reference count, and increments the backing-page reference count.

Removal is reference-count based. `i40e_remove_pd_bp()` decrements the BP reference count and exits early while still referenced. On final release it clears the software valid bit, decrements the PD table refcount, zeros the 64-bit PD entry in the PD page, writes `I40E_PFHMC_PDINV`, frees the backing DMA page unless it was caller-owned, and frees PD-entry virtual bookkeeping when the table refcount reaches zero. Direct SD removal similarly refuses early removal with `-EBUSY` while the BP refcount is nonzero, clears `valid`, writes `I40E_CLEAR_PF_SD_ENTRY`, and frees the DMA backing page.

## State and persistence
This file owns transient driver/HMC state in `struct i40e_hmc_info`: `sd_table.ref_cnt`, `sd_entry[].valid`, `sd_entry[].entry_type`, `pd_table.ref_cnt`, `pd_entry[].valid`, `pd_entry[].rsrc_pg`, and backing `struct i40e_dma_mem`/`struct i40e_virt_mem` allocations. It also mutates hardware-visible PFHMC SD/PD registers through macros from `i40e_hmc.h`; there is no disk persistence.

## Dependencies and integration points
The code depends on `i40e_allocate_dma_mem`, `i40e_free_dma_mem`, `i40e_allocate_virt_mem`, `i40e_free_virt_mem`, HMC structures/macros from `i40e_hmc.h`, register writes via `i40e_io.h`, and debug logging through `hw_dbg`. It is called by `i40e_lan_hmc.c` while creating and deleting LAN HMC objects.

## Risks and edge cases
- Reference-count macros are raw increments/decrements with no underflow guard; callers must balance add/remove operations.
- `i40e_remove_sd_bp_new()` and `i40e_remove_pd_page_new()` assume `idx` is valid and only reject non-PF callers; prep functions must run first.
- Error cleanup in `i40e_add_sd_table_entry()` frees only DMA memory allocated before failure; paged-mode virtual memory allocation failures rely on this path before assigning hardware validity.
- Caller-owned resource pages (`rsrc_pg`) are not freed by `i40e_remove_pd_bp()`, so ownership must be explicit.
- Hardware invalidation and memory free ordering matters; freeing before clearing PFHMC entries would risk device DMA to freed memory.

## Test signals
Useful signals are successful PF probe/configure/shutdown cycles, fault-injection of DMA/virtual allocation failures, repeated create/delete of paged and direct HMC objects, absence of leaks from HMC DMA/virt allocations, no `bad sd_index`/`bad pd_index` debug logs, and stable queue-context operation after PD invalidation.
