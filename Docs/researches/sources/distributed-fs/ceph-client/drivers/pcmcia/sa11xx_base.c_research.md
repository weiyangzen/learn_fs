# sources/distributed-fs/ceph-client/drivers/pcmcia/sa11xx_base.c

Purpose: Provides SA-1100/SA-1110 PCMCIA base support: MECR timing calculation, static resource assignment, common SoC socket registration, and CPU-frequency timing updates.

Important APIs and functions: Exports `sa11xx_drv_pcmcia_add_one()`, `sa11xx_drv_pcmcia_ops()`, and `sa11xx_drv_pcmcia_probe()`. Internal helpers include `sa1100_pcmcia_default_mecr_timing()`, `sa1100_pcmcia_set_mecr()`, `sa1100_pcmcia_set_timing()`, and `sa1100_pcmcia_show_timing()`.

Control flow: `sa11xx_drv_pcmcia_ops()` supplies default `get_timing` when absent and installs SA11xx `set_timing`, `show_timing`, and optional cpufreq callbacks. Probe gets a clock, allocates `skt_dev_info`, initializes each common socket with the requested first/nr range, then calls `sa11xx_drv_pcmcia_add_one()`. Timing updates compute max requested I/O/memory/attribute speeds, convert them through board-specific or default BS calculations, update socket fields in MECR under local IRQ disable, and expose requested/effective timing through the SoC status sysfs file.

State and persistence: Socket resources are fixed SA11xx PCMCIA physical regions; MECR holds persistent timing state. Per-socket requested speeds live in `soc_pcmcia_socket` arrays managed by `soc_common.c`.

Dependencies and integration points: Depends on `mach/hardware.h` MECR accessors/macros from `sa11xx_base.h`, common SoC PCMCIA, Linux clocks, and optional cpufreq.

Risks: Direct MECR register updates are architecture-specific and interrupt-protected but not otherwise serialized. Timing math depends on clock units and board-provided overrides. Resource windows assume two classic SA11xx sockets.

Test signals: Socket probe on SA1100/SA1110 boards, timing visible in sysfs status, card operation across I/O/attribute/common memory, CPU-frequency changes, and resource cleanup on remove.
