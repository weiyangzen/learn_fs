<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/init.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/init.c

Purpose: Implements Loongson64 early boot initialization, memory discovery entry points, early bridge configuration, legacy ISA PIO reservation, IRQ init, and NMI setup.

Important APIs/types/functions: `prom_init()`, `szmem(node)`, `ls7a_early_config()`, `rs780e_early_config()`, `virtual_early_config()`, `reserve_pio_range()`, `arch_init_irq()`, and `arch_dynirq_lower_bound()`.

Control flow: `prom_init()` initializes command line, selects DTB vs LEFI env parsing, sets IO base, runs bridge early config to compute `node_id_offset`, initializes NUMA or node-0 memory, sets early 8250 UART by CPU type, registers Loongson SMP ops, and installs the NMI setup hook. IRQ init reserves ISA IO ranges from device tree then calls `irqchip_init()`.

State and persistence: Writes `node_id_offset`, memblock regions/reservations, logic PIO ranges, early serial config, and SMP ops.

Dependencies and integration: Calls `prom_lefi_init_env()`/`prom_dtb_init_env()`, `prom_init_numa_memory()`, `szmem()`, `logic_pio_register_range()`, and OF range parsing.

Risks: LEFI memory parsing is skipped in DTB mode. Legacy ISA mapping requires IO range start zero. Early UART address is hard-coded by CPU implementation.

Test signals: DTB and LEFI boots should both populate memory; ISA IO ranges should appear in logic PIO; dynamic IRQ lower bound should not overlap legacy IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/init.c -->
