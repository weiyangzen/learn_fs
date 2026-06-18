<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/generic.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/generic.h

Purpose: internal PXA machine declarations shared by SoC, IRQ, DT, reset, and board files.

Important APIs/macros: declares map, timer, IRQ init, SoC map/init functions, `pxa_restart()`, syscore objects for IRQ and MFP suspend, UART info setters, and `pxa2xx_clear_reset_status()`. Defines `ARRAY_AND_SIZE()`, `SET_BANK()`, and handle-IRQ aliases for PXA25x, PXA27x, and PXA3xx.

Control flow and integration: machine descriptors and initcalls use these prototypes to wire boot hooks; syscore declarations are registered by SoC init.

State and persistence: header only; it exposes persistent syscore structures and reset functions implemented elsewhere.

Dependencies: includes `linux/reboot.h` and relies on `struct irq_data`.

Risks and test signals: macro aliases must track actual interrupt controller handlers. Compile all SoC variants and boot both DT and ATAGS paths to validate declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/generic.h -->
