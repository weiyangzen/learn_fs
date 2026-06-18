# sources/distributed-fs/ceph-client/arch/parisc/defpalo.conf

Purpose: default PALO bootloader configuration for PA-RISC. It documents the expected kernel image path, partition selection, boot command line, and recovery comments used when preparing boot media.

Important APIs/types/functions: not executable code; key fields are the PALO directives and commented examples that set the boot partition, kernel image, optional initrd, root device, and console/kernel parameters.

Control flow: PALO consumes this declarative file at bootloader install or boot time to find and pass arguments to the kernel. Kernel control flow begins only after the bootloader loads the configured image.

State and persistence: values persist in the installed bootloader configuration or filesystem file. Dependencies and integration: integrates with PA-RISC PALO tooling, disk partition layout, and kernel command-line parsing.

Risks and test signals: stale device names or image paths can make a system unbootable even though the kernel builds. Test by running PALO config validation where available and checking that documented paths match packaged PA-RISC boot artifacts.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
