# sources/distributed-fs/ceph-client/arch/parisc/include/asm/kexec.h

Purpose: defines PA-RISC kexec limits and hooks for loading and entering a replacement kernel.

Important APIs/types/functions: declares architecture memory limits, page constraints, and machine_kexec-related structures or prototypes.

Control flow: kexec validates target segments, prepares control code, shuts down devices/interrupts, and transfers execution to the new kernel image.

State and persistence: loaded kexec segments persist in reserved memory until executed or replaced. Dependencies and integration: generic kexec, crash dump, firmware/boot ABI, and cache/TLB shutdown paths.

Risks and test signals: address or cache mistakes fail only during reboot/crash paths. Test with `kexec -l/-e`, crash kernel loading if supported, and segment-boundary validation.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
