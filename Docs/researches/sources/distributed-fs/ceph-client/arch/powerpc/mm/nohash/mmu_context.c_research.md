# sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/mmu_context.c

## Purpose
This file manages address-space context IDs for non-hash PowerPC MMUs such as 8xx, 4xx/47x, and BookE. It allocates, switches, steals, and destroys per-`mm_struct` PID/context numbers that hardware TLB entries use to distinguish user address spaces. It also maintains per-CPU stale context state for SMP so stolen context IDs are invalidated before reuse on a CPU that may still have old translations.

## Important APIs, Types, And Functions
The exported lifecycle hooks are `mmu_context_init()`, `init_new_context()`, `destroy_context()`, and `switch_mmu_context()`. `set_context()` programs `SPRN_M_TWB`/`SPRN_M_CASID` on 8xx or `SPRN_PID` on other nohash parts, gated by `kuap_is_disabled()`. Internal state is global: `context_map`, `stale_map[NR_CPUS]`, `context_mm`, `next_context`, `nr_free_contexts`, and `context_lock`. `steal_context_smp()`, `steal_context_up()`, and `steal_all_contexts()` implement replacement under different CPU-count and 8xx constraints.

## Control Flow
`mmu_context_init()` allocates context maps with `memblock`, reserves IDs below `FIRST_CONTEXT`, initializes `init_mm.context.active`, and registers CPU hotplug callbacks for stale-map allocation. `switch_mmu_context()` takes `context_lock`, updates `active` counts on SMP, reuses an existing `mm->context.id` when valid, otherwise allocates the next clear bit or steals a victim. Stolen SMP contexts are marked stale on CPUs and sibling threads from the victim `mm_cpumask()`. Before installing a context, the current CPU checks `stale_map[cpu]`, flushes that mm locally, clears sibling stale bits, updates optional `abatron_pteptrs`, and writes the hardware context.

## State And Persistence
Context IDs persist in `mm->context.id` until `destroy_context()` or stealing resets them to `MMU_NO_CONTEXT`. `context_mm[id]` links a PID back to its owning `mm`, while `context_map` is the allocation bitmap. `stale_map` is per-CPU transient invalidation debt and survives until the target CPU switches back to that context and flushes. CPU-hotplug teardown frees non-boot CPU stale maps and clears task `mm_cpumask` bits.

## Dependencies And Integration Points
This code depends on `asm/mmu_context.h`, `asm/tlbflush.h`, CPU sibling helpers, CPU hotplug, `memblock`, `mm_cpumask()`, `local_flush_tlb_mm()`, `_tlbil_all()`, and KUAP behavior. It is called by the scheduler's address-space switch path and feeds the low-level TLB flush assembly through PID values.

## Risks And Test Signals
Primary risks are stale TLB reuse, incorrect `active` accounting, CPU-hotplug stale-map lifetime, and global-lock scalability. SMP tests should stress process migration, CPU hotplug, context exhaustion, and workloads with more active address spaces than hardware PIDs. 8xx needs extra coverage because it can flush all contexts and programs `M_CASID` as `id - 1`.
