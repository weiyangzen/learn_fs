# sources/distributed-fs/ceph-client/arch/mips/econet/init.c

Purpose: provides minimal EcoNet EN75xx platform bring-up: early UART, reset hook, device-tree memory discovery, IRQ chip initialization, SMP_UP registration, and timer setup.

Important APIs: `prom_init()` configures early 8250 printk at `0x1fbf0003` with register shift 2 and installs `_machine_restart`. `plat_mem_setup()` sets I/O port base, obtains the FDT via `get_fdt()`, calls `__dt_setup_arch()`, and scans memory. `device_tree_init()` unflattens the DT and registers UP SMP ops. `arch_init_irq()` calls `irqchip_init()`. `plat_time_init()` initializes OF clocks and probes timers. `get_system_type()` returns `"EcoNet-EN75xx"`.

State and integration: runtime state comes from the device tree and generic IRQ/timer/clock subsystems. Hardware reset writes bit 31 to AHB reset control at `0x1fb00040`.

Risks and test signals: boot requires a valid appended or supplied DTB; missing DTB panics. UART base uses byte offset `...0003`, so register mapping must match SoC endianness/stride. Test early console, DT memory map, IRQ controller probe, timer probe, and restart.
