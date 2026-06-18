# sources/distributed-fs/ceph-client/kernel/dma/remap.c

## Purpose

`remap.c` provides generic remapping helpers for coherent DMA allocations. It can create vmalloc-style coherent mappings from an array of pages or a contiguous page range, find the page array backing a coherent mapping, and free such remaps.

## Important APIs, Types, And Functions

- `dma_common_find_pages()` looks up a `vm_struct` with `find_vm_area()`, verifies `VM_DMA_COHERENT`, warns on unexpected flags, and returns the stored page array.
- `dma_common_pages_remap()` calls `vmap()` with `VM_DMA_COHERENT` and stores the caller-provided `pages` array in the resulting vm_area for later discovery.
- `dma_common_contiguous_remap()` builds a temporary array of consecutive `struct page *` entries with `kvmalloc_objs()`, maps them with `vmap()`, and frees the temporary array.
- `dma_common_free_remap()` validates that the address refers to a coherent vm_area and releases it with `vunmap()`.

## Control Flow

Remapping an arbitrary page array is direct: call `vmap()` with the requested protection and coherent flag, then attach the page list to the vm_area. Remapping a contiguous allocation first materializes a page pointer array from the starting page and page count. Freeing performs defensive validation before calling `vunmap()`.

## State And Persistence Behavior

The persistent runtime state is the `vm_struct` created by `vmap()`, including the `VM_DMA_COHERENT` flag and page-array pointer. That state exists until `dma_common_free_remap()` unmaps it. The file does not maintain global state.

## Dependencies And Integration Points

The helpers depend on `vmap()`, `vunmap()`, `find_vm_area()`, vmalloc flags, `pgprot_t`, and kernel allocation helpers. They are used by coherent DMA implementations and the atomic pool code when direct remapping is enabled.

## Risks And Edge Cases

- `dma_common_pages_remap()` stores the caller's `pages` pointer in the vm_area; the caller must keep that page array valid if later discovery is expected.
- `dma_common_contiguous_remap()` frees its temporary page array after `vmap()`, so `dma_common_find_pages()` is not useful for that path unless the vmalloc internals retain their own page list.
- Freeing an address that is not a coherent remap triggers a warning and returns without unmapping.
- These helpers cannot be used from non-sleeping contexts.

## Test Signals

Exercise coherent remap allocation/free, invalid free warnings, `VM_DMA_COHERENT` flag checks, page-array discovery for page-array remaps, and `CONFIG_DMA_DIRECT_REMAP` users such as atomic pool expansion.
