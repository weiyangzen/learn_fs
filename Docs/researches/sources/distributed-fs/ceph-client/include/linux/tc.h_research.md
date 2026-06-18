<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tc.h -->
# sources/distributed-fs/ceph-client/include/linux/tc.h

## Purpose
declares TURBOchannel bus, device, driver, ROM-offset, and PROM-access interfaces for legacy DEC/MIPS systems.

## Important APIs, Types, and Functions
The file is 143 lines and exports these visible symbol families: types/enums `tcinfo`, `tc_bus`, `tc_dev`, `tc_device_id`, `tc_driver`; macros/constants `TC_OLDCARD`, `TC_NEWCARD`, `TC_ROM_WIDTH`, `TC_ROM_STRIDE`, `TC_ROM_SIZE`, `TC_SLOT_SIZE`, `TC_PATTERN0`, `TC_PATTERN1`, `TC_PATTERN2`, `TC_PATTERN3`, `TC_FIRM_VER`, `TC_VENDOR`, `TC_MODULE`, `TC_FIRM_TYPE`, and 2 more; function-like macros `to_tc_dev`, `to_tc_driver`; inline helpers `tc_get_speed`, `tc_register_driver`, `tc_unregister_driver`; external prototypes `tc_register_driver`, `tc_unregister_driver`, `tc_preadb`, `tc_bus_get_info`, `tc_device_get_irq`.

## Control Flow
Architecture code obtains bus info through PROM helpers, scans slot ROMs using the defined offsets, creates `tc_dev` instances, and binds `tc_driver` instances registered on `tc_bus_type`. `tc_get_speed()` derives bus frequency from PROM clock period.

## State and Persistence Behavior
Runtime state is in `tc_bus` device lists/resources and `tc_dev` resources, DMA masks, slot IDs, and interrupt numbers. CONFIG_TC=n leaves driver registration as no-op stubs.

## Dependencies and Integration Points
It depends on the Linux device model, resources, list handling, and architecture-provided PROM/IRQ helpers. Direct includes are `linux/compiler.h`, `linux/device.h`, `linux/ioport.h`, `linux/types.h`.

## Risks and Edge Cases
ROM parsing offsets and fixed-size vendor/name strings are ABI-like. Bad slot resource or DMA-mask setup can make legacy drivers access the wrong bus window.

## Test Signals
Compile MIPS/TURBOchannel configs, scan representative ROM images or hardware, verify driver match tables, and check resource/IRQ assignment during probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tc.h -->
