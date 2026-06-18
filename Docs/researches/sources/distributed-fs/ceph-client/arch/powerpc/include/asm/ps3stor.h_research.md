# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ps3stor.h

Purpose: This header defines the common PS3 storage-device structure and command helpers used by disk, ROM, and flash storage drivers.

Important APIs/types/functions: `struct ps3_storage_region` records a region id, start, and size. `struct ps3_storage_device` embeds a `ps3_system_bus_device`, DMA region, IRQ, block size, async tag/status/completion, bounce buffer metadata, region count, accessible region bitmap, selected region index, and a flexible array of regions. `to_ps3_storage_device` converts from core `struct device`. Public functions are `ps3stor_setup`, `ps3stor_teardown`, `ps3stor_read_write_sectors`, and `ps3stor_send_command`.

Control flow: A PS3 storage driver allocates a device with region records, registers it on the system bus, calls setup with an IRQ handler, uses bounce/DMA memory to submit LV1 storage commands, waits on `done`, checks `lv1_status`, and tears down IRQ/DMA state during removal.

State and persistence: Device state persists across I/O: DMA mapping, IRQ number, block size, command tag/status, completion, bounce buffer LPAR/DMA addresses, accessible regions, and the current region index.

Dependencies and integration points: It depends on Linux interrupts and PS3 system bus/DMA declarations from `ps3.h`. It integrates block/flash/ROM drivers with PS3 LV1 storage commands, the PS3 system bus, DMA bounce buffering, and interrupt completion.

Risks and test signals: Flexible-array allocation must include all regions. Bounce buffer size/alignment and DMA lifetime are critical. Region selection must respect `accessible_regions`. Tests include setup/teardown, read/write sector commands, command timeout/error status paths, IRQ completion, multi-region devices, and suspend/remove during outstanding I/O.
