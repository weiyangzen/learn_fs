# sources/distributed-fs/ceph-client/arch/sh/boards/of-generic.c



Source read size: 174 lines, 3562 bytes.



Purpose: generic SH board support for booting from a flattened device tree instead of a board-specific machine vector.

Important APIs/types/functions: `sh_of_generic_mv`, `sh_of_setup()`, `sh_of_smp_probe()`, dummy SMP callbacks, `sh_of_mem_reserve()`, `sh_of_init_irq()`, `sh_of_clk_init()`, weak `arch_init_clk_ops()` and `plat_irq_setup()` fallbacks, and `__cpu_method_of_table` matching.

Control flow: early memory reservation reserves the FDT and `/reserved-memory`; setup reads the root `model`, scans CPU nodes, selects SMP operations from `enable-method`, or installs dummy SMP operations; interrupt setup delegates to `irqchip_init()` and common-clock setup optionally calls `of_clk_init()`.

State and persistence: mutates `sh_mv.mv_name`, CPU possible/present masks and logical maps, and reserved-memory state. It has no disk persistence.

Dependencies and integration points: integrates Open Firmware parsing, irqchip drivers, clock providers, SH machine vectors, SMP registration, RTC/clock hooks, and DT CPU enable-method tables.

Risks and test signals: missing or mismatched `enable-method` silently falls back to dummy SMP; the IRQ demux is a temporary identity function; common clock probing is compiled but disabled pending framework migration. Test with DT boot logs, reserved-memory nodes, CPU hotplug/SMP, irqchip interrupts, and clock provider probing.
