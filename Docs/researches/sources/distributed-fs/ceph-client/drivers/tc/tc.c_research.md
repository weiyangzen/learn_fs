# sources/distributed-fs/ceph-client/drivers/tc/tc.c

## Purpose
Implements TURBOchannel bus discovery and device registration. It obtains platform bus geometry, reserves slot memory ranges, probes each slot for a ROM signature, extracts module metadata, sets DMA masks and resources, obtains IRQs, and registers `struct tc_dev` devices on the TC bus.

## Important APIs, Types, and Functions
The static `tc_bus` object represents the root TURBOchannel bus. `tc_init()` is the subsystem initializer. `tc_bus_add_devices()` scans slots and creates `struct tc_dev` instances. It uses platform helpers such as `tc_bus_get_info()`, `tc_get_speed()`, `tc_preadb()`, and `tc_device_get_irq()` declared by the TC subsystem/architecture.

## Control Flow
`tc_init()` asks the platform for bus info, registers the root bus device, reserves standard and optional extended slot memory resources, prints bus revision/speed/parity, and calls `tc_bus_add_devices()`. Each slot is ioremapped, old-card and then new-card ROM offsets are checked for the `55 00 aa ff` pattern, metadata strings are read at four-byte spacing, device size determines standard versus extended slot resource assignment, IRQ is filled, and `device_register()` publishes the device.

## State and Persistence Behavior
The root `tc_bus` and registered `tc_dev` objects persist for kernel lifetime. Each device stores firmware/vendor/name strings, slot number, memory resource, DMA mask, parent bus pointer, and list node. There is no removal path in this file, matching the mostly static platform bus model.

## Dependencies and Integration Points
Depends on architecture-specific TC probing/IRQ helpers, `iomem_resource`, MMIO mapping, DMA mask support, and `tc_bus_type` from `tc-driver.c`. TC device drivers bind via exact vendor/name matching.

## Risks and Test Signals
The slot ioremap uses `BUG_ON(!module)`, so mapping failure is fatal. `tc_init()` returns success even after several setup failures, which can hide missing TC hardware/resource reservation failures. Device allocation/register failures skip the slot but continue. Test signals include correct ROM pattern detection for old/new card offsets, resource reservation conflicts, extended slot sizing, IRQ assignment, DMA mask propagation, and driver binding by firmware strings.
