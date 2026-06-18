# sources/distributed-fs/ceph-client/arch/sparc/kernel/leon_smp.c

Purpose: Provides SPARC32 LEON SMP bringup, cache-snooping setup, IPI routing, cross-call handling, and CPU startup synchronization.

Important APIs/types/functions: `leon_configure_cache_smp()` validates D-cache snooping and disables caches when unsupported. `leon_boot_cpus()`, `leon_boot_one_cpu()`, `leon_cpu_pre_starting()`, `leon_cpu_pre_online()`, and `leon_smp_done()` implement bringup. IPI support uses per-CPU `struct leon_ipi_work`, `leon_ipi_init()`, `leon_send_ipi()`, `leon_ipi_single()`, `leon_ipi_mask_one()`, `leon_ipi_resched()`, `leonsmp_ipi_interrupt()`, and `leon_ipi_ops`. Cross calls use global aligned `ccall_info`, `cross_call_lock`, `leon_cross_call()`, and `leon_cross_call_irq()`.

Control flow: Boot initializes IPI trap routing, enables cross-call/ticker/IPI IRQs on the boot CPU, sets ticker broadcast, and configures caches. Each secondary CPU is assigned an idle thread, gets the SRMMU context table, is woken through IRQMP `mpstatus`, signals `cpu_callin_map`, adopts `init_mm`, and waits for `smp_commenced_mask`. Runtime IPIs set per-CPU work flags and force the configured IRQ; the interrupt drains single, mask, and reschedule work.

State and persistence: Persistent runtime state includes `leon_ipi_irq`, `smp_processors_ready`, per-CPU work flags, `current_set`, CPU callin/online masks, trap table patches, and `ccall_info`. Hardware state is IRQMP mask/force/broadcast registers and cache snooping configuration.

Dependencies and integration points: It depends on LEON IRQMP/GPTIMER state initialized elsewhere, OF `/ambapp0`, SPARC trap tables, SRMMU context table, cache/TLB local ops, generic SMP call-function APIs, and SPARC32 IPI ops.

Risks and test signals: Broadcast IRQMP support is mandatory for multi-CPU operation. Cross-call serialization relies on a single global structure and busy-wait completion. Tests include multi-CPU boot, cache snoop-disabled systems, IPI reschedule/call-function stress, CPU startup timeout handling, trap table patch correctness, and freeing unused per-CPU trap tables.
