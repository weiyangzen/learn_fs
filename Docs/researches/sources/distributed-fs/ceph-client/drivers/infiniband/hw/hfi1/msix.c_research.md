# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/msix.c

## Purpose
`msix.c` allocates, requests, maps, frees, and synchronizes HFI1 MSI-X interrupt vectors. It covers general device interrupts, SDMA engines, kernel receive contexts, and accelerated netdev receive contexts.

## Important APIs, types, and functions
- `msix_initialize()` computes the required vector count, allocates PCI MSI-X vectors, allocates `dd->msix_info.msix_entries`, initializes the vector bitmap, and records capacity.
- `msix_request_irq()` is the central allocator: it reserves a free vector bit, calls `pci_request_irq()`, records IRQ metadata, and requests affinity.
- `msix_request_general_irq()`, `msix_request_sdma_irq()`, `msix_request_rcd_irq()`, and `msix_netdev_request_rcd_irq()` build names, choose handlers, and remap hardware interrupt sources to vectors.
- `msix_request_irqs()` requests the general vector, all SDMA vectors, and all kernel receive context vectors, enabling SDMA interrupt sources as it goes.
- `msix_free_irq()` releases affinity and PCI IRQ state for one vector and clears the in-use bit.
- `msix_clean_up_interrupts()` frees all requested IRQs, metadata, and PCI vectors.
- `msix_netdev_synchronize_irq()` waits for all netdev receive-context IRQ handlers to finish before queue disable.

## Control flow
Device setup calls `msix_initialize()` before individual IRQ requests. The total vector count is `1 + num_sdma + n_krcv_queues + num_netdev_contexts`, and must be below the hardware vector limit. Later request helpers reserve vectors from the bitmap and remap HFI1 interrupt source indexes to the allocated MSI-X number.

The general IRQ is required to be vector zero; if allocation returns any other vector, it is freed and setup fails. SDMA requests enable SDMA, progress, idle, and error interrupt sources. Kernel receive contexts are requested during `msix_request_irqs()`, while netdev receive contexts use the exported netdev-specific request helper from `netdev_rx.c`.

Cleanup iterates all possible requested vectors, frees those with non-null `arg`, clears metadata, frees the entry array, resets max count, and calls `pci_free_irq_vectors()`.

## State and persistence
MSI-X runtime state lives in `dd->msix_info`: allocated entry array, in-use bitmap, spinlock, and max requested count. Individual receive contexts and SDMA engines store their assigned `msix_intr`; receive contexts also store interrupt register/mask fields. State is runtime-only and tied to PCI device lifetime.

## Dependencies and integration points
This file depends on Linux PCI MSI-X APIs, HFI1 affinity helpers, interrupt handlers from receive and SDMA code, HFI1 hardware remap functions, and netdev receive queue lifecycle. It is a prerequisite for receive and SDMA interrupt-driven operation.

## Risks
- `msix_request_irq()` sets a bitmap bit before validating `type`; an invalid type returns `-EINVAL` without clearing the bit. Current callers pass constants, but future callers should preserve that invariant or fix the ordering.
- Partial failures in `msix_request_irqs()` return immediately; higher-level probe code must call cleanup to release already requested vectors.
- General IRQ must be vector zero, so changes to allocation order can break initialization.
- Netdev IRQ synchronization assumes netdev contexts have valid `msix_intr` entries.

## Test signals
- Probe tests with different SDMA, kernel receive, and netdev context counts, including vector-limit failure.
- Fault-injection for PCI vector allocation, metadata allocation, individual `pci_request_irq()`, and affinity failures.
- Verify interrupt remapping for general, SDMA, kernel receive, and netdev receive contexts.
- Exercise cleanup after partial request failure and after netdev contexts are allocated/freed.
