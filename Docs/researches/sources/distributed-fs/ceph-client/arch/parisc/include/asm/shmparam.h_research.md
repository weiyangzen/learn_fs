# sources/distributed-fs/ceph-client/arch/parisc/include/asm/shmparam.h

Purpose: defines PA-RISC System V shared-memory alignment requirements for aliasing caches.

Important APIs/types/functions: exports `SHMLBA` and `SHM_COLOUR`.

Control flow: SysV shared-memory attach code aligns requested addresses according to these constants to avoid cache aliasing problems.

State and persistence: shared-memory mappings persist in process VMAs and page tables. Dependencies and integration: used by IPC shm code and mmap layout.

Risks and test signals: insufficient alignment causes incoherent shared mappings. Test SysV shm attach at varied addresses and aliasing-cache data consistency.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
