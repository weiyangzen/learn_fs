<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa3xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa3xx.c

Purpose: PXA3xx SoC support for PM, external wake IRQs, IO mapping, reset/watchdog status, and shared PXA3xx initialization.

Important APIs/functions: PM code maps ISRAM, copies standby code into SRAM, programs AD* wake registers, sets OBM resume handoff, and calls `pxa3xx_finish_suspend()`. `pxa3xx_set_wake()` maps internal IRQs to ADXER wake bits. External wakeup IRQ chip methods ack/mask/unmask/type through PECR/PWER plus internal IRQ masking. `pxa3xx_init_irq()` enables CP6 access and initializes wake IRQs.

Control flow: DT or legacy IRQ init calls `__pxa3xx_init_irq()` then `pxa_dt_irq_init()` or `pxa_init_irq()`. `postcore_initcall(pxa3xx_init)` gates on CPU family, registers watchdog status from ARSR, clears ASCR RDH/D-state bits, disables NAND DFI arbitration, initializes PM, enables wake IRQs, and registers IRQ/MFP syscore ops.

State and persistence: static `sram` mapping and `wakeup_src` bitmask persist. Power manager, ASCR, NAND NDCR, and clock registers are mutated during init and suspend.

Dependencies and integration: depends on IRQ core, PM assembly, generic MFP syscore, PXA clocks, `devices.c`, NAND address map, and CPU detection.

Risks and test signals: suspend refuses if no wake sources are configured. Resume protocol depends on OBM expectation at SDRAM base and PSPR value. Test PXA300/PXA310/PXA320 boot, external wake IRQ0/1, mem/standby suspend, NAND clock/arbitration behavior, and DFI bus stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa3xx.c -->
