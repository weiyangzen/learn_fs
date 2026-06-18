# sources/distributed-fs/ceph-client/arch/m68k/coldfire/firebee.c

Purpose: FireBee board-specific NOR flash registration. It describes the board's 8 MiB physical flash at `0xe0000000` and partitions it for bootloader, FPGA image, and kernel/image storage.

Important APIs and data: `firebee_flash_parts[]` defines `dBUG`, `FPGA`, and `image` MTD partitions; `firebee_flash_data` passes width and partition table to the physmap driver; `firebee_flash_resource` covers the physical memory window; `firebee_flash` is a `physmap-flash` platform device. `init_firebee()` registers the device through `arch_initcall()`.

Control flow and state: no dynamic probing occurs. Boot-time init registers one platform device; MTD/physmap later maps and manages the flash. Persistent behavior belongs to NOR contents and MTD consumers, not this file.

Dependencies and integration: Linux platform bus, MTD physmap, ColdFire IO resource definitions, and FireBee board memory map. It depends on the selected board config matching the actual flash bus width and address decode.

Risks and test signals: partition offsets are hard-coded; an incorrect map can expose bootloader or FPGA storage for accidental erase/write. The resource end is `addr + size`, not `addr + size - 1`, which is a boundary detail worth auditing against resource conventions. Test by booting FireBee, inspecting `/proc/mtd`, verifying partition sizes/offsets, and performing read-only MTD probe checks before write tests.
