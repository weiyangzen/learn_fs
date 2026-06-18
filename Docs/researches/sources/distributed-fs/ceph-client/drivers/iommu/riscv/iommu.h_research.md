# sources/distributed-fs/ceph-client/drivers/iommu/riscv/iommu.h

## Purpose
This header defines the shared RISC-V IOMMU core data structures and MMIO access wrappers used by PCI and platform bus glue plus the core implementation.

## Important APIs, Types, And Functions
`struct riscv_iommu_queue` stores queue producer/consumer shadows, mask, IRQ, active IOMMU pointer, base virtual address, physical address, register offsets, and queue ID. `struct riscv_iommu_device` embeds `struct iommu_device`, records the backing Linux device, MMIO register base, capabilities, FCTL state, interrupt vectors, command/fault queues, and device-directory table mode/root. The header declares `riscv_iommu_init()`, `riscv_iommu_remove()`, and `riscv_iommu_disable()`.

Access macros `riscv_iommu_readl()`, `riscv_iommu_readq()`, `riscv_iommu_writel()`, `riscv_iommu_writeq()`, `riscv_iommu_readq_timeout()`, and `riscv_iommu_readl_timeout()` provide relaxed MMIO reads/writes and polling wrappers over the mapped register window.

## Control Flow
The header does not implement flow, but it fixes the interface between `iommu-pci.c`, `iommu-platform.c`, and `iommu.c`: bus glue fills `struct riscv_iommu_device`, then calls `riscv_iommu_init()`; remove/shutdown call `riscv_iommu_remove()` or `riscv_iommu_disable()`.

## State And Persistence
The queue and device structs hold all persistent shared state across bus drivers and core operations: queue buffers, IRQ routing, capabilities, FCTL mode, and DDT root configuration.

## Dependencies And Integration Points
It includes Linux IOMMU types, fixed-width types, I/O polling helpers, and `iommu-bits.h`. It is the narrow internal ABI between transport-specific drivers and the common RISC-V IOMMU core.

## Risks
The MMIO helpers are relaxed; ordering must be added explicitly at call sites where hardware-visible memory updates precede doorbells or context-valid bits. The transport drivers must fully initialize capabilities, FCTL, IRQs, register base, and device pointer before calling init.

## Test Signals
Compile all RISC-V IOMMU objects together and test both platform and PCI paths, ensuring each initializes the struct fields required by the core.
