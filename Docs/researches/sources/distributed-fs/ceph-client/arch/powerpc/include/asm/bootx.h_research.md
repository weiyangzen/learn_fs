# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/bootx.h

Purpose: describes the legacy BootX bootloader interface used by MacOS-era PowerPC systems to pass display and device-tree information to Linux.

Important APIs/types/functions: defines `BOOTX_COLORTABLE_SIZE`, `struct bootx_dt_prop`, `struct bootx_dt_node`, and `bootx_init(unsigned long r4, unsigned long phys)`. It includes UAPI BootX definitions.

Control flow: early boot code calls `bootx_init()` with BootX register/physical address inputs; this header only provides the data layout.

State and persistence: BootX-provided device tree and framebuffer metadata are boot-time state consumed during early initialization.

Dependencies and integration points: integrates with old PowerMac boot paths, early device-tree parsing, and boot text/framebuffer setup.

Risks: structures use 32-bit offsets from an old flattened format, not modern OF/FDT layout. Incorrect interpretation can lose device tree properties or display setup.

Test signals: boot legacy BootX-supported PowerMac systems or emulation, validate parsed device tree nodes/properties, and confirm early framebuffer colormap/display setup.
