<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_gtm.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_gtm.c

Purpose: Freescale general-purpose 16-bit timer support, exporting a small allocation/configuration API for other drivers.

Important APIs/types/functions: exported `gtm_get_timer16()`, `gtm_get_specific_timer16()`, `gtm_put_timer16()`, `gtm_set_timer16()`, `gtm_set_exact_timer16()`, `gtm_stop_timer16()`, `gtm_ack_timer16()`, plus `gtm_set_ref_timer16()`, `gtm_set_shortcuts()`, and `fsl_gtm_init()`.

Control flow: arch init scans `fsl,gtm` nodes, allocates one `gtm` per node, reads `clock-frequency`, maps four IRQs, maps registers, assigns per-timer register shortcuts, stores the `gtm` in `np->data`, and links it globally. Consumers reserve any or a specific timer, configure interval/reload by computing prescaler settings, reset/stop the timer, program mode/reference/event registers under a spinlock, and release it after stopping.

State and persistence: state is a global list of GTM blocks and per-timer `requested` flags, IRQ numbers, register pointers, and parent pointer. Hardware timer mode, prescale, counter, reference, and event registers persist while programmed.

Dependencies and integration points: depends on OF timers with `clock-frequency`, four interrupts per block, endian MMIO helpers, the exported `asm/fsl_gtm.h` API, and consumers that request IRQs separately using `timer->irq`.

Risks: timer allocation is global and non-devm; no module removal exists. Prescaler math rejects intervals beyond hardware capacity and reduces precision in `gtm_set_timer16()`. CPM2 GTMs lack primary prescalers, narrowing the supported range.

Test signals: successful GTM discovery, reservation/release behavior, timer IRQ firing at approximate/exact intervals, reload vs free-run behavior, and event acknowledgment in interrupt handlers validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_gtm.c -->
