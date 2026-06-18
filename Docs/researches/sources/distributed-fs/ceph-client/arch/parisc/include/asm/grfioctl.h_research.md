# sources/distributed-fs/ceph-client/arch/parisc/include/asm/grfioctl.h

Purpose: defines PA-RISC graphics framebuffer/graphics device ioctl numbers and small ABI structures.

Important APIs/types/functions: exports graphics ioctl constants and data layouts used by legacy PA-RISC graphics drivers and userspace tools.

Control flow: userspace issues ioctl calls; drivers decode these command numbers and copy the associated structures to or from userspace.

State and persistence: ioctl data may expose or update device mode/state; this header only defines ABI layouts. Dependencies and integration: consumed by graphics drivers and user-facing uapi compatibility code.

Risks and test signals: ioctl number or structure layout changes break legacy userspace. Test with header install checks, graphics driver build coverage, and ioctl ABI comparison.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
