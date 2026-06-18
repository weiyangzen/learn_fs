# sources/distributed-fs/ceph-client/arch/mips/ralink/of.c

Purpose: Ralink/MediaTek MIPS device-tree bootstrap glue. It remaps the system-controller and memory-controller nodes, establishes the I/O port base, parses the built-in FDT, discovers RAM, and registers platform buses for the selected SoC.

Important APIs and control flow: `mtmips_of_remap_node()` finds a matching DT node, converts its first address resource, claims the memory region, and returns an `ioremap()`. `ralink_of_remap()` stores the exported `rt_sysc_membase` and local `rt_memc_membase`. `plat_mem_setup()` calls `get_fdt()`, `__dt_setup_arch()`, then chooses memory from DT, SoC-specific `mem_detect`, fixed `mem_size`, or `detect_memory_region()`. `plat_of_setup()` uses `__dt_register_buses()` for `soc_info.compatible` and `palmbus`.

State, persistence, and integration: state is early global register mappings and memblock RAM entries. It depends on `soc_info` filled by the SoC-specific `prom_soc_init()`, matching DT compatible strings, `ralink_regs` helpers, and Linux OF/memblock initialization. Risks include hard panics for missing core DT nodes, resource leaks if `ioremap()` fails after `request_mem_region()`, and boot failure when `soc_info.compatible` is wrong. Test signals are early boot logs, successful sysc/memc mapping, visible RAM size, and palmbus child device creation.
