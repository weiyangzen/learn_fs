# sources/distributed-fs/ceph-client/drivers/virt/acrn/mm.c

## Purpose
Manages ACRN User VM memory mappings. It translates userspace or MMIO memory descriptors into hypervisor memory-region batches and keeps enough Service VM-side state to unpin and unmap RAM later.

## APIs, Types, and Functions
Exports `acrn_mm_region_add()`, `acrn_mm_region_del()`, `acrn_vm_memseg_map()`, `acrn_vm_memseg_unmap()`, `acrn_vm_ram_map()`, and `acrn_vm_all_ram_unmap()`. Internal `modify_region()` wraps a single `vm_memory_region_op` inside `vm_memory_region_batch` for `hcall_set_memory_regions()`. State uses `struct vm_memory_mapping` entries stored in `vm->regions_mapping`.

## Control Flow and State
MMIO maps are direct `ACRN_MEM_TYPE_UC` add/delete operations. RAM maps first handle `VM_PFNMAP` VMAs by validating contiguous, writable, reserved PFNs and mapping them directly. Normal userspace memory is pinned with `pin_user_pages_fast(FOLL_WRITE | FOLL_LONGTERM)`, `vmap()`ed into the Service VM, recorded under `regions_mapping_lock`, coalesced by compound-page order into region operations, and submitted to the hypervisor. On hypercall failure, the code unwinds the mapping count, vmap, and page pins. `acrn_vm_all_ram_unmap()` walks recorded mappings and releases all kernel mappings and page references.

## Dependencies and Integration
Depends on Linux mm primitives, GUP long-term pins, `vmap()/vunmap()`, PFNMAP helpers, and ACRN memory hypercall definitions. It is invoked from ACRN ioctl handling and VM destruction.

## Risks and Test Signals
Risks include long-term pin accounting, `regions_mapping_count` slot exhaustion, partial rollback after hypervisor add failure, PFNMAP validation accepting only safe reserved contiguous memory, and lack of reset of `regions_mapping_count` after full unmap. Tests should cover RAM and MMIO map/unmap, PFNMAP success/failure, non-page-aligned lengths, compound pages, exceeding `ACRN_MEM_MAPPING_MAX`, and destroy after partially failed mapping.
