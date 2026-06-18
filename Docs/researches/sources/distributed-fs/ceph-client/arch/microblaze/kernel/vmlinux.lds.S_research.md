# sources/distributed-fs/ceph-client/arch/microblaze/kernel/vmlinux.lds.S

Purpose: defines the MicroBlaze kernel image layout, entry symbol, section placement, FDT staging area, init vector table, small-data anchors, and BSS boundaries.

Important symbols and state: `ENTRY(microblaze_start)`, `_text/_stext/_etext`, `_fdt_start/_fdt_end`, `_KERNEL_SDA2_BASE_`, `_KERNEL_SDA_BASE_`, `__ivt_start/__ivt_end`, `__bss_start/__bss_stop`, `_end`, and endian-dependent `jiffies` alias.

Control flow: linker script only. Runtime code in `head.S` and `setup.c` relies on these addresses for early FDT copy, BSS clearing, vector copying, SDA setup, and kernel mapping.

State and persistence: determines final persistent memory layout of the kernel image.

Dependencies and integration: includes generic vmlinux linker macros and architecture cache/page/thread constants.

Risks and test signals: section alignment affects MMU mappings, percpu layout, exception table alignment, and small-data ABI. The FDT area is fixed at 64 KiB. Test link map, boot with linked DTB, BSS clearing, initramfs placement, and exception vector copy boundaries.
