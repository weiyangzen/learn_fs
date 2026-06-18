<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/generic.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/generic.c

### Purpose
Provides common SA1100 platform support: CPU speed table, restart/poweroff, common platform devices, MTD/LCD/MCP/PCMCIA registration helpers, fixed regulators, static I/O maps, timer, IRQ, memory-bus control, and wake helpers.

### Important APIs, Types, And Functions
Exports `sa11x0_freq_table`, `sa11x0_getspeed()`, `sa11x0_restart()`, `sa11x0_ppc_configure_mcp()`, `sa11x0_register_mcp()`, `sa11x0_register_lcd()`, `sa11x0_register_pcmcia()`, `sa11x0_register_mtd()`, `sa11x0_init_late()`, `sa11x0_register_fixed_regulator()`, `sa1100_map_io()`, `sa1100_timer_init()`, `sa1100_init_irq()`, `sa1110_mb_disable()`, `sa1110_mb_enable()`, `sa11x0_gpio_set_wake()`, and `sa11x0_sc_set_wake()`.

### Control Flow
`arch_initcall(sa1100_init)` registers poweroff, regulator constraints, watchdog, and common platform devices. Board machine descriptors call common map/timer/IRQ helpers and then board init. Late init initializes PM. Helper functions let board files attach platform data to common devices before drivers probe.

### State, Persistence, And Dependencies
State includes common platform devices/resources, DMA masks, cpufreq table, fixed-regulator init data, static I/O maps, and wake register bits. Dependencies include SA1100 register macros, platform devices, PXA timer, SA11x0 IRQ/GPIO init, clocks, regulators, MTD, framebuffer, MCP, PCMCIA, and PM.

### Integration Points
All SA1100 board files in this subset call these helpers for common hardware and machine descriptors.

### Risks
Raw register writes affect global CPU pin, wake, and memory bus state. Fixed regulator helper allocates init data and does not check platform registration failure. Static maps reserve high virtual regions.

### Test Signals
Board boot, common device probes, cpufreq speed reporting, watchdog/RTC/DMA/UART/MCP/LCD registration, IRQ delivery, timer ticks, and wake-source tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/generic.c -->
