# sources/distributed-fs/ceph-client/drivers/iommu/riscv/iommu.c

## Purpose
This is the shared RISC-V IOMMU core. It manages hardware queues, device-directory tables, device contexts, generic RISC-V page-table backed domains, PSCID allocation, IOTLB invalidation, fault-queue reporting, device attach/detach, and registration with the Linux IOMMU core.

## Important APIs, Types, And Functions
The public entry points used by bus glue are `riscv_iommu_init()`, `riscv_iommu_remove()`, and `riscv_iommu_disable()`. Internal queue management is handled by `riscv_iommu_queue_alloc()`, `riscv_iommu_queue_enable()`, `riscv_iommu_queue_disable()`, `riscv_iommu_queue_send()`, `riscv_iommu_queue_wait()`, `riscv_iommu_queue_consume()`, and `riscv_iommu_queue_release()`. Command helpers are wrapped by `riscv_iommu_cmd_send()` and `riscv_iommu_cmd_sync()`. Fault handling is in `riscv_iommu_fltq_process()` and `riscv_iommu_fault()`.

Device-directory management centers on `riscv_iommu_iodir_alloc()`, `riscv_iommu_iodir_set_mode()`, `riscv_iommu_get_dc()`, `riscv_iommu_iodir_update()`, and `riscv_iommu_iodir_iotinval()`. Domain state is `struct riscv_iommu_domain`, embedding a generic page-table domain (`pt_iommu_riscv_64`) plus an RCU-protected bond list and PSCID. Device private state is `struct riscv_iommu_info`. Generic IOMMU hooks include paging, identity, and blocking attach paths plus `riscv_iommu_probe_device()`, `riscv_iommu_release_device()`, `riscv_iommu_device_group()`, and `riscv_iommu_of_xlate()`.

## Control Flow
Initialization configures command/fault queues, validates the initial DDTP state, fixes byte order if supported, programs interrupt vector routing, allocates the DDT root, allocates queue backing memory or maps fixed queue memory, enables command and fault queues with threaded IRQ handlers, switches DDTP to the maximum supported DDT mode, registers sysfs, optionally registers ACPI RIMT state, and registers the IOMMU core device.

Device probe obtains fwspec IDs, resolves the IOMMU from the fwnode device, rejects fail-over OFF/BARE mode, preallocates invalid device-context entries for every device ID, and stores private info. Paging-domain allocation chooses Sv39/Sv48/Sv57 based on capabilities, allocates a PSCID, initializes the generic RISC-V 64-bit page table with sign-extension, flush-range, and Svnapot 64 KiB features, and returns a domain with page-table ops. Attach verifies hardware page-table mode support, computes FSC and translation attributes, links the device into the domain bond list, updates device-context entries, unlinks the previous tracked domain, and records the new domain in private device info. Blocking and identity attach update the device context to invalid or BARE respectively and unlink any tracked paging domain.

IOTLB invalidation walks the domain bond list under RCU, sends one invalidation per IOMMU for the domain PSCID, optionally emits per-page invalidations for ranges below the current threshold, then sends IOFENCE.C commands and waits. Device-context updates first invalidate any existing valid context, synchronize, then write FSC/TA and TC.V last with a DMA write barrier, followed by IODIR and IOTINVAL commands.

## State And Persistence
Persistent state includes command and fault queue ring buffers, DDT root/pages, device contexts, PSCID namespace allocations, generic page tables, and domain bond lists. Queue indices are tracked with atomic unbounded producer/head/tail counters and hardware head/tail registers. Device-directory pages are devres-managed and freed with the device. Domain page tables and PSCIDs are freed in `riscv_iommu_free_paging_domain()`.

## Dependencies And Integration Points
The core depends on the RISC-V IOMMU register/data definitions, Linux IOMMU core, generic page-table IOMMU namespace, PCI group helpers for PCI devices, OF fwspec IDs, ACPI RIMT registration, devres, IDA PSCID allocation, threaded IRQs, RCU, and DMA/MMIO ordering primitives.

## Risks
Fault handling is currently report-only and does not recover beyond queue CSR clearing. Queue error recovery is explicitly incomplete. IOTLB range invalidation falls back to page-by-page commands below a threshold or whole-PSCID invalidation above it because range invalidations are not yet available. Attach updates valid device contexts and notes that doing so while a device is not quiesced may be disruptive. PASID/SVA, ATS, page-request queue, and second-stage support are mostly not implemented despite data definitions. Timeouts log hardware errors but many flows continue, so hardware non-response can leave stale translations.

## Test Signals
Boot/probe on platform and PCI RISC-V IOMMU implementations, attach/detach paging/identity/blocking domains, DMA map/unmap through generic page-table ops, PSCID reuse/free, DDT mode fallback, command/fault queue interrupts, injected fault queue records, kdump boot with previously enabled DDTP, big-endian FCTL handling, ACPI RIMT registration, and stress tests with concurrent map/unmap/attach.
