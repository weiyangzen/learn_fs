# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/msix.h

## Purpose
`msix.h` declares the HFI1 MSI-X interrupt-management API used by device setup, receive contexts, SDMA engines, and netdev receive contexts.

## Important APIs, types, and functions
- Core lifecycle: `msix_initialize()`, `msix_request_irqs()`, and `msix_clean_up_interrupts()`.
- Per-source request/free helpers: `msix_request_general_irq()`, `msix_request_rcd_irq()`, `msix_request_sdma_irq()`, and `msix_free_irq()`.
- Netdev-specific helpers: `msix_netdev_request_rcd_irq()` and `msix_netdev_synchronize_irq()`.

## Control flow
The expected order is initialize PCI MSI-X capacity, request general/SDMA/kernel receive interrupts, request netdev receive interrupts as netdev contexts are allocated, synchronize netdev IRQs before disabling their queues, and clean up all interrupts during device teardown or probe failure.

## State and persistence
The header declares functions that mutate `struct hfi1_devdata`, `struct hfi1_ctxtdata`, and `struct sdma_engine` interrupt fields. It declares no state of its own.

## Dependencies and integration points
It includes `hfi.h` for core HFI1 types and is included by receive, SDMA, and device initialization code. It abstracts Linux PCI IRQ details away from those users.

## Risks
- Callers must pair successful request helpers with `msix_free_irq()` or full cleanup.
- Netdev callers must synchronize IRQs before freeing or disabling NAPI contexts.
- Any signature change affects several HFI1 subsystems.

## Test signals
- Compile users across HFI1 device, SDMA, receive, and netdev paths.
- Probe and teardown tests should check that each requested interrupt is freed exactly once.
