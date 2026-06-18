# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctvmem.c

## Purpose

This file implements the device virtual-memory allocator and page-table population used by ctxfi transport DMA.

## Important APIs, types, and functions

Public APIs are `ct_vm_create()` and `ct_vm_destroy()`. The `ct_vm` object installs `map`, `unmap`, and `get_ptp_phys` callbacks implemented by `ct_vm_map()`, `ct_vm_unmap()`, and `ct_get_ptp_phys()`. Internal `get_vm_block()` and `put_vm_block()` allocate and merge logical address blocks.

## Control flow

Creation allocates page-table pages, initializes unused/used block lists with one free block spanning the virtual address space, and returns callbacks. Mapping finds a page-aligned free block, moves or splits it into the used list, then fills page table entries from `snd_pcm_sgbuf_get_addr()`. Unmapping returns the block to the free list and coalesces neighbors. Destroy frees all list nodes and DMA page-table pages.

## State and persistence behavior

Persistent state is the page-table DMA buffer, logical address-space size, used/unused block lists, and mutex. Hardware sees the page-table physical address through `ct_get_ptp_phys()` and `hw_trn_init()` in the hardware backend. Individual blocks retain original requested size after page-table population.

## Dependencies and integration points

It depends on `ctvmem.h`, `ctatc.h`, ALSA PCM SG buffers, ALSA DMA allocation, and PCI devices. ATC stream preparation maps PCM buffers into this virtual space before transport setup.

## Risks and test signals

Risks include using `CT_PAGE_MASK` based on `PAGE_SIZE` rather than `CT_PAGE_SIZE`, silent failure when initial free block allocation fails, page-table bounds mistakes for large buffers, and lack of hardware TLB invalidation on unmap. Tests should map/unmap varied buffer sizes, check coalescing, validate page-table entries for SG buffers, and run playback/capture after repeated hw_params changes.
