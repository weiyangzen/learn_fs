# sources/distributed-fs/ceph-client/arch/parisc/include/asm/mmu.h

Purpose: defines the PA-RISC MMU context type used by each process address space.

Important APIs/types/functions: provides `mm_context_t`, primarily carrying the PA-RISC space ID and related context data.

Control flow: context allocation assigns a space ID; context switch and TLB flush code loads that ID into space registers and TLB purge operations.

State and persistence: `mm_context_t` persists in `mm_struct` for the life of an address space. Dependencies and integration: used by `mmu_context.h`, `pgtable.h`, processor setup, and fault/TLB handlers.

Risks and test signals: incorrect context state causes cross-process address aliasing. Test with fork/exec stress, ASID/space-ID recycling, and TLB flush tests.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
