<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/dev.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/dev.h

## Purpose

`dev.h` is the central internal host1x device contract. It defines operation tables for each hardware block, SoC capability descriptors, the main `struct host1x`, MMIO helpers, and inline dispatch wrappers used by generic code.

## Important APIs, Types, And Functions

- Operation tables: `host1x_channel_ops`, `host1x_cdma_ops`, `host1x_pushbuffer_ops`, `host1x_debug_ops`, `host1x_syncpt_ops`, and `host1x_intr_ops`.
- SoC descriptors: `struct host1x_sid_entry`, `struct host1x_table_desc`, and `struct host1x_info`.
- `struct host1x`: persistent controller state including MMIO regions, IRQs, clock/reset, IOMMU domain/IOVA, operation pointers, syncpoints, channel/context lists, debugfs, device list, DMA parameters, and BO cache.
- Inline wrappers dispatch generic calls to the active generation's operation table for syncpoints, interrupts, channels, CDMA, pushbuffer, and debug.

## Control Flow

The header is not executable beyond inlines. Generation init code installs operation table pointers into `struct host1x`; generic code calls the wrappers without knowing which register layout is active.

## State And Persistence Behavior

`struct host1x` persists for the controller lifetime and is the root of almost all host1x state. Its operation pointers must be initialized before any channel/syncpoint/CDMA code runs.

## Dependencies And Integration Points

It includes Linux device/IOMMU/IOVA/IRQ/platform/reset headers and host1x internal headers. It is included by nearly every file in this subset and by generation include units.

## Risks And Test Signals

A missing operation pointer can crash through an inline wrapper. Capability fields must match DT and silicon. Build coverage across all generations, probe smoke tests, and static checks for initialized operation tables are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/dev.h -->
