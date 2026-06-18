<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/context.c -->
# sources/distributed-fs/ceph-client/arch/riscv/mm/context.c

## Purpose
`context.c` implements RISC-V MM context switching, ASID allocation/rollover, and deferred instruction-cache flushing for tasks.

## Important APIs, Types, And Functions
Global ASID state includes `use_asid_allocator`, `num_asids`, `current_version`, `context_lock`, `context_tlb_flush_pending`, `context_asid_map`, per-CPU `active_context`, and `reserved_context`. Key functions are `asids_init()`, `set_mm_asid()`, `set_mm_noasid()`, `set_mm()`, `flush_icache_deferred()`, and `switch_mm()`.

## Control Flow
Boot probes writable SATP ASID bits, enables ASID allocation only when enough ASIDs exist, and initializes the bitmap. Context switch marks CPU membership, assigns an ASID with versioning or flushes with ASID 0, writes SATP, and performs queued TLB flushes. Rollover preserves per-CPU reserved contexts and queues all CPUs for local flush. Deferred icache flush runs when a CPU switches into an mm marked stale.

## State And Persistence
Per-mm state is `mm->context.id` and icache masks/flags. Per-CPU active/reserved contexts cache ASID usage. Runtime-only state is reset at boot.

## Dependencies And Integration Points
It depends on SATP CSR, TLB flush helpers, mm cpumasks, membarrier, task switch hooks, and cacheflush stale-mask logic.

## Risks
ASID rollover races require strict locking and cmpxchg behavior. Missing TLB flushes can expose stale translations. With ASIDs enabled, CPUs remain in `mm_cpumask` until mm reset, which differs from no-ASID behavior.

## Test Signals
Fork/exec/mmap stress, ASID rollover under many address spaces, membarrier tests, SMP migration with self-modifying code, and TLB shootdown tests are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/context.c -->
