# sources/distributed-fs/ceph-client/arch/parisc/include/asm/eisa_bus.h

Purpose: declares PA-RISC EISA bus discovery and device representation hooks.

Important APIs/types/functions: defines or declares EISA bus structures and initialization functions used by platform bus code.

Control flow: platform initialization probes firmware-described EISA hardware, creates bus/device records, and lets EISA drivers bind.

State and persistence: discovered bus/device data persists in kernel device structures. Dependencies and integration: integrates with firmware inventory, EISA EEPROM parsing, and legacy device drivers.

Risks and test signals: firmware parsing or resource mistakes break old expansion devices. Test with EISA-enabled build configs and boot on systems with/without EISA slots.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
