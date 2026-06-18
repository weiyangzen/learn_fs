# sources/distributed-fs/ceph-client/drivers/iommu/riscv/iommu-bits.h

## Purpose
This header is the RISC-V IOMMU hardware contract. It defines MMIO register offsets, bit fields, queue record layouts, device/process context layouts, MSI page-table entries, fault causes, transaction types, and inline command builders based on the RISC-V IOMMU architecture specification.

## Important APIs, Types, And Functions
Register definitions include capabilities, feature control, device directory table pointer, command/fault/page-request queue base/head/tail/CSR registers, interrupt pending/status/vector registers, performance-monitoring registers, translation request registers, and MSI configuration table registers. Capability fields advertise supported address-translation modes, MSI formats, endianness control, ATS, performance monitoring, process-directory widths, and interrupt generation mode.

Important data structures are `struct riscv_iommu_dc` for device contexts, `struct riscv_iommu_pc` for process contexts, `struct riscv_iommu_command` for command queue entries, `struct riscv_iommu_fq_record` for fault/event queue entries, `struct riscv_iommu_pq_record` for page-request queue entries, and `struct riscv_iommu_msipte` for MSI translation entries. Enums encode interrupt-generation settings, DDTP modes, HPM event IDs, first/second stage translation modes, fault causes, and fault transaction types.

Inline builders include `riscv_iommu_cmd_inval_vma()`, `riscv_iommu_cmd_inval_set_addr()`, `riscv_iommu_cmd_inval_set_pscid()`, `riscv_iommu_cmd_inval_set_gscid()`, `riscv_iommu_cmd_iofence()`, `riscv_iommu_cmd_iofence_set_av()`, `riscv_iommu_cmd_iodir_inval_ddt()`, `riscv_iommu_cmd_iodir_inval_pdt()`, `riscv_iommu_cmd_iodir_set_did()`, and `riscv_iommu_cmd_iodir_set_pid()`.

## Control Flow
The header has no standalone flow, but `iommu.c` depends on its command builders for IOTLB invalidation, IODIR invalidation, and IOFENCE synchronization. Probe code uses capability and FCTL fields to select interrupt mode and byte order. Queue code uses common queue CSR bits and index masks.

## State And Persistence
It defines the binary layout of persistent in-memory structures shared with hardware: DDT nodes, device contexts, process contexts, command queues, fault queues, page-request queues, and MSI page-table entries. It also defines hardware register state layout.

## Dependencies And Integration Points
The file uses Linux bitfield helpers and architecture page definitions. It is included by all RISC-V IOMMU implementation files and must remain synchronized with the RISC-V IOMMU spec and generic page-table code.

## Risks
A wrong field mask or command encoding can corrupt device-context setup or invalidate the wrong translations. The header includes future-facing definitions for features not fully implemented by `iommu.c` yet, such as PASID/SVA, ATS, page-request queue, and second-stage handling; users of those fields must add full invalidation and state-management support. Duplicated or misspelled symbolic definitions in this source should be caught by compile and style checks.

## Test Signals
Compile tests across 64-bit RISC-V and `COMPILE_TEST`, queue command encoding unit-style checks if available, hardware/QEMU boot with command/fault queue traffic, attach/detach with PSCID invalidation, and MSI/WSI interrupt-mode probe coverage.
