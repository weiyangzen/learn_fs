# sources/distributed-fs/ceph-client/drivers/uio/uio_dmem_genirq.c

## Purpose
`uio_dmem_genirq.c` is a platform UIO driver that combines generic non-shared interrupt handling with fixed platform memory resources and dynamically allocated DMA-coherent memory regions. It is intended for devices whose detailed interrupt acknowledgement and device policy live in userspace.

## Important APIs, Types, And Functions
Private state is `struct uio_dmem_genirq_platdata`, containing the UIO info pointer, interrupt lock/flags, platform device, dynamic-region start/count, allocation mutex, and open refcount. The key callbacks are `uio_dmem_genirq_open()`, `uio_dmem_genirq_release()`, `uio_dmem_genirq_handler()`, `uio_dmem_genirq_irqcontrol()`, and `uio_dmem_genirq_probe()`.

## Control Flow And State
Probe accepts platform data or creates basic DT-derived `uio_info`, rejects provider-supplied handlers/shared IRQs, sets a 32-bit coherent DMA mask, discovers the first platform IRQ, converts memory resources to `UIO_MEM_PHYS` maps, appends dynamic `UIO_MEM_DMA_COHERENT` maps with `DMEM_MAP_ERROR` placeholder addresses, installs generic IRQ/open/release callbacks, enables runtime PM, and registers the UIO device with devres.

On first open, dynamic regions are allocated with `dma_alloc_coherent()`, their CPU and DMA addresses are stored in `uio_mem`, the refcount is incremented, and runtime PM resumes the device. On release, runtime PM idles the device and the last close frees all dynamic regions and restores `DMEM_MAP_ERROR`. The IRQ handler disables the IRQ once and sets `UIO_IRQ_DISABLED`; userspace writes call `irqcontrol` to enable or disable while preserving IRQ depth.

## Dependencies And Integration Points
The driver depends on platform resources or `uio_dmem_genirq_pdata`, DMA coherent allocation, runtime PM, IRQ trigger metadata, UIO core, and optional OF naming. It uses `IRQ_DISABLE_UNLAZY` for level-triggered IRQs because hardware acknowledgement happens in userspace.

## Risks And Edge Cases
The code assumes platform data exists for dynamic-region sizes even when a DT node creates `uioinfo`; DT users without pdata can hit invalid access depending on how the platform device is constructed. Dynamic allocation failures set map addresses to `DMEM_MAP_ERROR`, and userspace must not mmap before successful open. Shared interrupts are rejected. Refcounting protects allocation lifetime, but multiple users share the same dynamic buffers while open.

## Test Signals
Test fixed-only and fixed-plus-dynamic devices, first-open allocation, multi-open refcounting, last-close free, DMA mmap, runtime PM get/put pairing, level IRQ lazy-disable behavior, userspace irqcontrol toggling, nonblocking UIO reads, and invalid shared IRQ configuration.
