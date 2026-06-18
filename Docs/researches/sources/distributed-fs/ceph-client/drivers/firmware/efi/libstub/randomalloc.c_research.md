
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/randomalloc.c

Purpose: chooses a randomized aligned EFI memory allocation slot from suitable conventional memory, preferring mirrored/more-reliable memory when available.

Important APIs/types/functions: exports `efi_random_alloc()`. Internal `get_entry_num_slots()` counts candidate aligned placements per EFI descriptor, with descriptor `virt_addr` reused as a temporary slot-count field via `MD_NUM_SLOTS()`.

Control flow: the function retrieves the memory map, normalizes alignment and size, avoids address zero, counts eligible slots across conventional, non-hotplug, non-soft-reserved memory bounded by min/max, optionally restricts selection to `EFI_MEMORY_MORE_RELIABLE` descriptors, maps a 32-bit seed into a target slot, walks descriptors again to find the selected slot, and allocates it with `EFI_ALLOCATE_ADDRESS`.

State and persistence behavior: mutates the temporary memory-map copy only. The chosen allocation persists to the caller as EFI pages of the requested memory type.

Dependencies and integration points: depends on EFI memory-map helpers, soft-reserve policy, `ilog2()`, and EFI page allocation. Used for physical KASLR and zboot decompressed-image placement.

Risks and test signals: if no eligible slots exist, seed multiplication with zero slots must yield an out-of-resources path. Reusing `virt_addr` is safe only on the private map copy. Test signals include mirrored memory preference, min/max bounds, alignment larger than EFI page, SP/hotplug exclusion, deterministic placement for fixed seeds, and failed exact-address allocation.
