# sources/distributed-fs/ceph-client/arch/sparc/kernel/smp_64.c

Purpose: implements sparc64 SMP boot, cross-call delivery, TLB/cache shootdowns, CPU topology masks, CPU hotplug, scheduler pokes, CPU capture, and per-CPU allocator setup.

Important APIs/types/functions: exports `cpu_sibling_map`, `cpu_core_map`, `cpu_core_sib_map`, and `cpu_core_sib_cache_map`. Key routines are `smp_callin()`, `__cpu_up()`, `smp_setup_processor_id()`, `xcall_deliver()`, Spitfire/Cheetah/sun4v deliverers, `arch_send_call_function_*_ipi()`, `smp_flush_tlb_*()`, `smp_flush_dcache_folio_impl()`, `flush_dcache_folio_all()`, `smp_tsb_sync()`, `smp_capture()`/`smp_release()`, hotplug hooks, `arch_smp_send_reschedule()`, `smp_init_cpu_poke()`, `smp_send_stop()`, and `setup_per_cpu_areas()`.

Control flow: secondary CPUs register per-CPU offsets and sun4v KTSB data, flush TLBs, initialize timers, enable forced P-cache if needed, set `callin_flag`, attach `init_mm`, notify hotplug, wait in `smp_commenced_mask`, then enter idle. Boot uses OBP or sun4v hypervisor startup, then synchronizes `%tick` on non-hypervisor systems. Cross calls populate the current CPU `trap_block` mondo block and CPU list under local IRQ disable; delivery is selected for Spitfire ASI dispatch, Cheetah pipelined dispatch, or sun4v hypervisor `cpu_mondo_send()` with retry/error handling. TLB/cache functions use xcalls or generic `smp_call_function_many()` plus local flushes.

State and persistence: runtime state spans CPU masks, per-CPU `trap_block`, mondo queues, topology masks, `smp_commenced_mask`, CPU poke flags, capture atomics, and per-CPU offsets. No persistent storage is touched.

Dependencies and integration points: depends on PROM/hypervisor CPU lifecycle, trap-block layout, TLB/cache assembly xcall handlers, MM context IDs, cpumasks, clock/tick code, CPU hotplug, kgdb, Starfire translation, LDOMs, and NUMA-aware percpu allocation.

Risks: mondo delivery runs with interrupts disabled and shares per-CPU buffers, so reentrancy or timeout mistakes can panic or corrupt xcalls. Hypervisor error handling intentionally skips some faulty/offline CPUs but panics on no progress. Hotplug must remove topology and IRQ targeting before offlining. There is a visible missing semicolon in the non-aliasing `__local_flush_dcache_folio()` branch in this snapshot, which is a compile-risk if that branch is built.

Test signals: multi-CPU boot on Spitfire/Cheetah/sun4v, xcall stress, TLB shootdowns under mmap/munmap/fork, D-cache flushes for aliasing mappings, CPU hotplug, LDOM stop/start, scheduler IPI poke fallback, kgdb roundup, CPU capture around PROM calls, and percpu allocator initialization.
