# sources/distributed-fs/ceph-client/arch/parisc/include/asm/hardware.h

Purpose: defines PA-RISC hardware inventory abstractions and constants used to describe firmware-discovered devices.

Important APIs/types/functions: provides hardware type/version constants, `enum cpu_type`, device ID/class helpers, and declarations tying firmware inventory to Linux device structures.

Control flow: boot firmware probing records hardware identity; platform and bus drivers match these IDs to initialize CPUs, buses, I/O adapters, and legacy devices.

State and persistence: discovered hardware records persist in `struct parisc_device` and CPU information. Dependencies and integration: used by PDC probing, processor setup, parisc-device bus code, and platform drivers.

Risks and test signals: wrong ID classification causes driver binding failures or wrong CPU capability selection. Test by comparing boot inventory logs across PA-RISC models.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
