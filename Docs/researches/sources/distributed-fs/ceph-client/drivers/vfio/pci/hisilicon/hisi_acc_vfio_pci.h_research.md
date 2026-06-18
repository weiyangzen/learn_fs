# sources/distributed-fs/ceph-client/drivers/vfio/pci/hisilicon/hisi_acc_vfio_pci.h

## Purpose

This header defines HiSilicon ACC VFIO PCI migration register constants, migration payload layout, migration file state, and per-device private state.

## Important APIs, Types, and Functions

It defines QM mailbox timeouts, cache writeback registers, interrupt status registers, VFT registers, queue context register offsets, migration version/magic constants, and migration region offsets/sizes. `enum hw_drv_mode` distinguishes VF-controlled and PF-controlled migration register placement. `struct acc_vf_data` is the migration stream payload and includes match metadata, saved QM registers, and queue context DMA addresses. `struct hisi_acc_vf_migration_file` wraps anonymous migration file state. `struct hisi_acc_vf_core_device` extends `vfio_pci_core_device` with migration, PF/VF QM, reset, open, and debug state.

## Control Flow

The header has no executable flow but defines the data consumed by save/restore and BAR filtering in the implementation.

## State and Persistence Behavior

`acc_vf_data` is the transient migration state serialized through VFIO migration file descriptors. Device private state persists for the lifetime of the VFIO device registration and open sessions.

## Dependencies and Integration Points

It depends on `linux/hisi_acc_qm.h` for QM definitions and on VFIO PCI core through the embedding implementation. The magic/version fields provide compatibility between migration stream versions.

## Risks and Edge Cases

The layout of `struct acc_vf_data` is ABI-relevant for migration. `QM_MATCH_SIZE` controls when resume has enough data to validate source/destination compatibility; changing field order before that offset changes compatibility behavior. Register constants must match hardware generation and old/new migration-control placement.

## Test Signals

Validate `sizeof(struct acc_vf_data)`, `QM_MATCH_SIZE`, V1/V2 magic handling, BAR2 size constants, and old/new hardware mode register offsets in migration tests.
