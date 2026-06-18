# sources/distributed-fs/ceph-client/arch/mips/lantiq/prom.c

Purpose: provides generic Lantiq PROM/platform initialization, command-line extraction, DT setup, system type reporting, and MIPS MT SMP override.

Important APIs/functions: exports `ebu_lock`; implements `get_system_type`, `ltq_soc_type`, `prom_init_cmdline`, `plat_mem_setup`, and `prom_init`.

Control flow: `prom_init()` calls SoC-specific `ltq_soc_detect()`, formats the system type, initializes firmware command line from `fw_arg0/fw_arg1`, and optionally registers SMP ops with a custom secondary init. `plat_mem_setup()` configures IO resources, sets KSEG1 IO port base, obtains FDT, and calls `__dt_setup_arch()`.

State and persistence: static `soc_info` holds detected platform data; `arcs_cmdline` is populated from firmware arguments; `ebu_lock` coordinates EBU users.

Dependencies and integration: depends on SoC-specific PROM code in XWAY/Falcon, MIPS bootinfo/prom APIs, memblock/OF FDT parsing, and clock/timer init.

Risks: missing DTB panics. Firmware command-line pointers are assumed valid after KSEG1 translation. SMP interrupt enabling is broad via `ST0_IM`.

Test signals: boot command line contents, system type string, DT memory discovery, and SMP secondary CPU startup on MIPS MT systems.
