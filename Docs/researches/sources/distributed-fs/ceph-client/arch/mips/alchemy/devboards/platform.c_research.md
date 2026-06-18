## sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/platform.c

Purpose: provides shared DB/PB1xxx platform utilities: early console character output, board power-off/reset hooks, RTC device registration, PCMCIA socket platform-device creation, and NOR flash/partition registration.

Important APIs and functions: `prom_putchar()` writes to UART2 on Au1300 and UART0 otherwise. `db1x_late_setup()` installs `_machine_restart`, `_machine_halt`, and `pm_power_off` callbacks and registers `rtc-au1xxx`. `db1x_register_pcmcia_socket()` allocates a `db1xxx_pcmcia` platform device with memory and IRQ resources. `db1x_register_norflash()` allocates a `physmap-flash` device and a five-partition layout around YAMON, raw kernel, and environment regions.

Control flow: late device init installs power/reset behavior and RTC. Board files call the PCMCIA helper with physical ranges and card/insert/status/eject IRQs; the helper conditionally adds optional resources and registers the device. NOR registration calculates a flash window ending at `0x20000000`, builds partitions differently depending on swapboot, fills `physmap_flash_data`, and registers the platform device.

State and persistence: allocations for resources, partitions, and platform data are intentionally retained after successful platform registration. BCSR writes in reset/power-off alter board hardware state. MTD partitions expose persistent flash regions but this code only describes them.

Dependencies and integration: depends on BCSR, Alchemy UART, MTD physmap, platform device core, MIPS reboot hooks, and board-specific calls from DB1000/1200/1300/1550 setup.

Risks: allocation failure paths must free partially allocated objects; successful paths intentionally leak to device lifetime. NOR partition math assumes YAMON placement and a minimum 8 MiB flash. Power-off loops in `cpu_wait()` indefinitely after BCSR writes.

Test signals: early printk should appear on the expected UART. `rtc-au1xxx`, `db1xxx_pcmcia`, and `physmap-flash` devices should register. MTD partition names/order should reflect swapboot, and poweroff/restart should assert the CPLD reset/system bits.
