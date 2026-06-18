<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_types.h

## Purpose

`xe_tile_types.h` defines `struct xe_tile`, the central per-tile hardware/software state container.

## Important APIs, Types, and Functions

The `tile_to_xe()` generic helper returns the parent device. `struct xe_tile` stores tile ID, parent Xe device, primary/media GTs, MMIO, memory substructure (kernel/user VRAM, GGTT, kernel BB pool, reclaim pool), SR-IOV PF LMTT or VF self-config union, memory IRQ state, CSC error work, PCODE lock, migration helper, sysfs kobject, debugfs dentry, and MERT data.

## Control Flow

Probe fills the structure in stages: early backpointer/ID/allocation, VRAM/noalloc setup, full runtime resource setup, then debugfs/sysfs and GT initialization.

## State and Persistence Behavior

The structure persists for the device lifetime and owns or references most per-tile resources. SR-IOV substate is mode-dependent: PF uses LMTT, VF uses self-config.

## Dependencies and Integration Points

The header includes MMIO, LMEM translation, memory IRQ, MERT, and VF tile SR-IOV types. It is included throughout GT, tile, VRAM, SVM, debugfs, sysfs, and SR-IOV code.

## Risks and Test Signals

Because this is shared state, ownership changes can affect many subsystems. Tests should cover multi-tile initialization, PF/VF union use, root versus remote tile behavior, and teardown ordering for sysfs/debugfs/migrate/VRAM resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_types.h -->
