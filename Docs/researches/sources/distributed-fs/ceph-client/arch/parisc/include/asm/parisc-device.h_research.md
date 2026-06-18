# sources/distributed-fs/ceph-client/arch/parisc/include/asm/parisc-device.h

Purpose: defines the PA-RISC firmware-discovered device model used by architecture bus drivers.

Important APIs/types/functions: provides `struct parisc_device`, `struct parisc_driver`, `struct parisc_device_id`, matching helpers, and registration declarations.

Control flow: firmware inventory creates `parisc_device` objects; drivers register ID tables and probe matching devices.

State and persistence: device and driver records persist in the Linux device model. Dependencies and integration: used by native PA-RISC bus, PDC inventory, SBA/LBA/CPU/platform drivers.

Risks and test signals: ID matching or resource fields must remain ABI-stable for in-tree drivers. Test with boot inventory, driver binding logs, and module autoload/probe coverage.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
