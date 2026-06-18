# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_eq.c

## Purpose
`mthca_eq.c` implements event queues, interrupt handlers, event decoding, EQ creation/free, EQ register mapping, and optional MSI-X vector setup for mthca.

## Important APIs, types, and functions
Important layouts are `struct mthca_eq_context` and `struct mthca_eqe`. Public APIs include `mthca_init_eq_table()`, `mthca_cleanup_eq_table()`, `mthca_map_eq_icm()`, and `mthca_unmap_eq_icm()`. Internal handlers include `mthca_eq_int()`, Tavor/Arbel legacy and MSI-X interrupt handlers, `mthca_create_eq()`, `mthca_free_eq()`, EQ CI update helpers, notification request helpers, and `port_change()`.

## Control flow
Initialization allocates an EQ number allocator, maps interrupt/EQ registers, creates completion, async, and command EQs with spare entries, requests either one shared IRQ or three MSI-X IRQs, maps async and command event masks to their EQs, and arms all queues. Interrupt handlers clear interrupt state, process software-owned EQEs, dispatch completion, QP, SRQ, CQ, command, port, and warning events, return EQEs to hardware, update consumer indexes, and rearm notifications. Cleanup frees IRQs, unmaps event masks, transitions EQs back to software, frees DMA pages/MRs, unmaps registers, and destroys the allocator.

## State and persistence
State includes EQ arrays in `dev->eq_table`, EQ numbers/masks, page-list DMA buffers, MR registrations, consumer indexes, IRQ names/vectors, mapped clear/ECR/arm/set-CI registers, ICM page mapping for mem-free EQ contexts, and arm masks. Hardware persists EQ contexts, event masks, owner bits, and interrupt routing.

## Dependencies and integration points
It depends on command wrappers, CQ/QP/SRQ event callbacks, command completion callbacks, memfree ICM mapping, PCI IRQ/MSI-X APIs, MMIO register constants, doorbell helpers, and RDMA event dispatch.

## Risks
Interrupt handling must update owner bits and consumer indexes with strict barriers or hardware can overwrite entries incorrectly. Event mask mapping failures are logged but not fatal, reducing observability. CQ disarm only applies to Tavor. MSI-X fallback is coordinated by main through a NOP interrupt test. Free paths must quiesce IRQs before releasing EQ memory.

## Test signals
Test legacy INTx and MSI-X modes, Tavor and Arbel interrupt handlers, command event completion, CQ completion storms, async QP/CQ/SRQ/port events, EQ overflow warnings, MAP_EQ failures, mem-free EQ ICM mapping/unmapping, IRQ request failure unwind, and cleanup with pending interrupts.
