<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bootinfo.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/bootinfo.h

**Purpose:** Declares MIPS machine IDs, global boot state, PROM/platform hooks, command-line storage, firmware arguments, and FDT discovery helpers.

**Important APIs/types/functions:** Defines `MACH_*` constants/enums for DEC, Mikrotik, Loongson, and Ingenic. Declares `system_type`, `mips_machtype`, `prom_init`, `prom_free_prom_memory`, `plat_mem_setup`, `arcs_cmdline`, `fw_arg0..fw_arg3`, and `get_fdt()`.

**Control flow:** `get_fdt()` checks appended DTB, UHI `fw_arg0 == -2`, and built-in DTB in order when OF is enabled.

**State, dependencies, integration:** Central contract between firmware entry, platform setup, generic FDT boot, memory init, and proc reporting.

**Risks and test signals:** Boot argument conventions vary widely; FDT source priority affects boot behavior. Test appended/raw/ELF DTB, UHI, built-in DTB, and no-DTB fallback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bootinfo.h -->
