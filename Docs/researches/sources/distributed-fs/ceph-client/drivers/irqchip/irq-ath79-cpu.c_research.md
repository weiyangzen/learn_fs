# sources/distributed-fs/ceph-client/drivers/irqchip/irq-ath79-cpu.c

Purpose: Provides Atheros/QCA AR71xx/AR724x/AR913x CPU interrupt dispatch with optional DDR write-buffer flush mapping before invoking MIPS CPU IRQ handlers.

Important APIs/types/functions: `irq_wb_chan[]`, `plat_irq_dispatch()`, `ar79_cpu_intc_of_init()`, and `IRQCHIP_DECLARE(ar79_cpu_intc, "qca,ar7100-cpu-intc", ...)`.

Control flow: Platform dispatch reads MIPS status/cause pending bits, reports spurious interrupts if none are pending, then handles pending IP lines from highest to lowest. For mapped lines, it flushes the configured DDR write-buffer channel before calling `do_IRQ()`. OF init fills the IRQ-to-write-buffer-channel table from `qca,ddr-wb-channels` and optional `qca,ddr-wb-channel-interrupts`, then delegates to `mips_cpu_irq_of_init()`.

State and persistence: Global `irq_wb_chan` records optional write-buffer channel IDs per CPU interrupt line for the boot lifetime.

Dependencies/integration: Uses MIPS CP0 status/cause registers, ATH79 DDR write-buffer flush API, OF phandle parsing, and generic MIPS CPU IRQ domain initialization.

Risks and test signals: Test missing/default DDR write-buffer mappings, invalid IRQ indexes, phandle parse failures, ordering of write-buffer flush before device driver handling, spurious interrupt accounting, and multi-pending dispatch order.
