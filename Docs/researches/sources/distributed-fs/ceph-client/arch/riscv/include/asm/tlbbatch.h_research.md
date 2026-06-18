<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/tlbbatch.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/tlbbatch.h

Purpose: Defines RISC-V architecture-specific TLB unmap batch state.

Important APIs/types/functions: Defines `struct arch_tlbflush_unmap_batch` with CPU mask/range fields used by deferred flush support.

Control flow: MM code records CPUs/ranges in the batch and flushes them together through `arch_tlbbatch_flush()`.

State and persistence: Transient batch cpumask/range state attached to unmap operations.

Dependencies and integration points: Works with `tlbflush.h`, MM unmap batching, ASID/mm context, and SMP IPI flush code.

Risks: Lost CPU bits or stale ranges cause use-after-free through stale TLB entries.

Test signals: TLB batching stress, reclaim, munmap on SMP, KCSAN/lockdep, and ASID rollover tests.

Source read size: 15 lines, 273 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/tlbbatch.h -->
