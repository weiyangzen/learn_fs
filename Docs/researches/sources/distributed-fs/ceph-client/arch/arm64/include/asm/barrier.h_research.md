## sources/distributed-fs/ceph-client/arch/arm64/include/asm/barrier.h

Purpose: defines arm64 CPU, SMP, DMA, IO, speculation, and acquire/release barrier primitives. These are foundational memory-ordering contracts for the entire kernel.

Important APIs/types/functions: exports `sev`, `wfe`, `wfi`, `isb`, `dmb`, `dsb`, `psb_csync`, `tsb_csync`, `csdb`, `dgh`, `spec_bar`, `pmr_sync`, `__mb/__rmb/__wmb`, DMA barriers, SMP barriers, `array_index_mask_nospec`, `arch_counter_enforce_ordering`, `__smp_store_release`, `__smp_load_acquire`, and conditional load helpers.

Control flow: most macros emit one instruction. `spec_bar` and `pmr_sync` use alternative patching based on CPU capabilities. Store-release/load-acquire switch on operand size to emit `stlr*`/`ldar*`. Conditional loads spin, read, test the caller expression, then sleep with `__cmpwait_relaxed`.

State and persistence: no persistent state, but it controls visibility and ordering of all shared state. `tsb_csync` consults finalized CPU capabilities for erratum handling.

Dependencies and integration: depends on KASAN access checks, alternatives, cpufeature finalization, `asm-generic/barrier.h`, and cmpwait from cmpxchg. Used by atomics, locking, MMIO, scheduler, RCU, and timekeeping.

Risks: weakening one barrier can create rare data corruption or security bugs. Tests are LKMM litmus runs, lock/RCU stress, KCSAN, speculative-execution hardening tests, tracing barrier tests, and hardware validation on erratum-affected systems.
