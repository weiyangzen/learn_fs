# sources/distributed-fs/ceph-client/arch/parisc/include/asm/mman.h

Purpose: defines PA-RISC memory-management flags and maps generic mmap/mprotect constants to architecture ABI expectations.

Important APIs/types/functions: includes uapi mman definitions and architecture overrides such as executable/read implementation details.

Control flow: syscall code validates and applies mmap/mprotect flags using these constants.

State and persistence: mappings persist in process VMAs and page tables. Dependencies and integration: userspace ABI, mm subsystem, ELF loader, and signal stack setup.

Risks and test signals: ABI flag changes break userspace. Test mmap/mprotect syscall suites, executable mappings, and header ABI comparisons.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
