# sources/distributed-fs/ceph-client/arch/parisc/include/asm/mmu_context.h

Purpose: implements PA-RISC MMU context lifecycle and space-ID switching.

Important APIs/types/functions: defines `init_new_context`, `destroy_context`, `switch_mm`, `activate_mm`, `enter_lazy_tlb`, and related helpers around `alloc_sid`/`free_sid`.

Control flow: new address spaces receive a space ID; context switches update current CPU state and space registers; teardown returns IDs for reuse.

State and persistence: process `mm->context.space_id` and CPU active-mm state persist across scheduling decisions. Dependencies and integration: depends on cache/SID management, TLB flush routines, scheduler, and generic mm.

Risks and test signals: stale or reused space IDs without proper flushes can expose another process's memory. Test with context-switch stress, fork/exit loops, and TLB shootdown validation.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
