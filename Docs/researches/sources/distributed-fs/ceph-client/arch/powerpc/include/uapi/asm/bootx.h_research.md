<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/bootx.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/bootx.h

Purpose: Documents the legacy BootX-to-Linux boot information structure used by old Macintosh PowerPC systems.

Important APIs/types/functions: Boot magic/register contract, `BOOT_INFO_VERSION`, architecture flags, `MAX_MEM_MAP_SIZE`, `boot_info_map_entry_t`, and `boot_infos_t` with framebuffer, device tree, ramdisk, command line, memory map, and total parameter fields.

Control flow: BootX enters the kernel with r3 magic and r4 pointing to `boot_infos`; early boot parses appended device tree/arguments/ramdisk and may use framebuffer fields for early text.

State and persistence: The structure is persistent boot-time handoff state supplied by firmware/loader and consumed before normal device discovery.

Dependencies and integration points: Depends on Linux integer types and optional MacOS headers. Integrated by old PowerMac boot and early display code.

Risks: Layout and alignment are ABI-sensitive. Offsets are relative to the structure and invalid values can mislocate the device tree or ramdisk.

Test signals: Old PowerMac/BootX boot tests, structure layout checks, and early framebuffer/device-tree parsing smoke tests.

Source read size: 133 lines, 4416 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/bootx.h -->
