# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-bus.h

## Purpose

This header defines the IPU7 auxiliary bus device model shared by the base PCI driver and subsystem drivers.

## Important APIs, Types, and Functions

`enum ipu7_subsys` identifies IS and PS. `struct ipu7_bus_device` embeds `auxiliary_device` and stores subsystem, pdata, MMU, parent IPU device, buttress control, firmware SGT/entry, syscom, and boot config fields. `struct ipu7_auxdrv_data` provides ISR callbacks and threaded-IRQ wake policy. Conversion macros map between devices and bus devices.

## Control Flow

No implementation flow. The structs support bus creation, IRQ demux, firmware boot, DMA, and subsystem driver binding.

## State and Persistence Behavior

State persists for each auxiliary child lifetime. The bus device is also the anchor for subsystem DMA/syscom/boot allocations.

## Dependencies and Integration Points

It includes auxiliary bus, device/list/scatterlist/types, firmware boot ABI, and syscom declarations. Buttress IRQ code uses `auxdrv_data`.

## Risks and Edge Cases

Fields are shared across modules, so initialization order is critical. `auxdrv_data` must be valid before buttress IRQ dispatch. DMA mask and firmware SGT must match MMU setup.

## Test Signals

Compile users, auxiliary driver binding, IRQ dispatch with and without threaded handlers, and firmware boot using bus-device fields.
