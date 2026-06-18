# sources/distributed-fs/ceph-client/arch/parisc/include/asm/parport.h

Purpose: provides PA-RISC parallel-port discovery hooks for the generic parport subsystem.

Important APIs/types/functions: declares architecture parport initialization or maps to generic no-op behavior depending on platform support.

Control flow: parport core calls architecture probing to register available parallel ports, often through SuperIO/legacy resources.

State and persistence: registered parport devices persist in the device model. Dependencies and integration: integrates with SuperIO, PCI/legacy I/O, and printer/parallel drivers.

Risks and test signals: resource or IRQ mismatch breaks legacy parallel devices. Test with parport build/probe and SuperIO systems.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
