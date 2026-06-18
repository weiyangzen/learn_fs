# sources/distributed-fs/ceph-client/arch/mips/cobalt/setup.c

Purpose: installs Cobalt machine hooks, reserves unused legacy I/O ranges, initializes memory from firmware arguments, and sets up early serial printk.

Important APIs: `get_system_type()` maps `cobalt_board_id` to human-readable board names. `plat_mem_setup()` installs restart/halt/power-off hooks, sets GT64120 I/O port base, expands `ioport_resource`, and reserves DMA/keyboard resource ranges unused by Cobalt. `prom_init()` decodes memory size and argument count from `fw_arg0`, appends firmware arguments to `arcs_cmdline`, adds memblock RAM, and configures early 8250 printk.

State and integration: persistent state includes command line, memblock RAM, reserved I/O resources, reboot hooks, and early printk mapping.

Risks and test signals: `fw_arg0` packing must match firmware; wrong mem size can expose invalid RAM. Boot should report correct system type, memory size, command line, and early serial output.
