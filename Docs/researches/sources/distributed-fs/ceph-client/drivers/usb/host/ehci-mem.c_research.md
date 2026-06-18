<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-mem.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-mem.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/ehci-mem.c` is included by `ehci-hcd.c` and owns EHCI schedule memory allocation and cleanup. It creates DMA pools for queue transfer descriptors, queue heads, high-speed isochronous descriptors, split isochronous descriptors, the coherent periodic frame list, and the software shadow table. The source was read as a complete 224-line file.

## Important APIs, Types, and Functions

Key helpers are `ehci_qtd_init()`, `ehci_qtd_alloc()`, `ehci_qtd_free()`, `ehci_qh_alloc()`, `qh_destroy()`, `ehci_mem_init()`, and `ehci_mem_cleanup()`. They allocate and initialize hardware-facing `struct ehci_qtd`, `struct ehci_qh_hw`, `struct ehci_itd`, and `struct ehci_sitd` storage with the alignment and 4 KiB boundary constraints required by EHCI hardware.

## Control Flow

`ehci_mem_init()` creates qTD and QH DMA pools, allocates the async QH and its dummy qTD, creates ITD and SITD pools, allocates the coherent periodic schedule, optionally creates a dummy QH for every periodic entry, initializes periodic entries to either the dummy QH or list-end markers, and allocates the software shadow table. Any failure jumps to cleanup and returns `-ENOMEM`. `ehci_mem_cleanup()` destroys async/dummy QHs, all DMA pools, the coherent periodic table, and the shadow table.

## State and Persistence Behavior

All state is in DMA-coherent memory, DMA pools, and kernel allocations tied to the HCD lifetime. It persists only while the EHCI controller instance is initialized. Hardware reads QHs, qTDs, ITDs, SITDs, and periodic entries directly from these allocations.

## Dependencies and Integration Points

The file depends on EHCI internal types, DMA pool APIs, coherent DMA allocation, endian conversion helpers, and `ehci_to_hcd(ehci)->self.sysdev`. Queue and scheduler files consume the allocation helpers for transfer submission.

## Risks and Edge Cases

EHCI descriptor alignment and 4 KiB crossing constraints are mandatory; changing pool sizes/alignments risks DMA hardware faults. `qh_destroy()` BUGs if a QH is still linked or has qTDs. `ehci_qh_alloc()` uses `GFP_ATOMIC` for the software QH regardless of supplied flags, which matches interrupt-context allocation expectations but can fail under pressure. Cleanup must remain in sync with every allocation added to init.

## Test Signals

Test memory-allocation failure injection at each allocation step, HCD probe/remove leak checks, DMA API debug, high-volume control/bulk/interrupt/isochronous submissions, dummy-QH periodic mode, and endpoint disable paths that destroy QHs only when unlinked and empty.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-mem.c -->
