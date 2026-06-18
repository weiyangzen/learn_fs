<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/init.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/init.c

Purpose: Implements the Loongson2EF `prom_init()` boot hook and NMI vector setup.

Important APIs/types/functions: `_loongson_addrwincfg_base` stores optional address-window config mapping. `mips_nmi_setup()` copies `except_vec_nmi` to `CAC_BASE + 0x380`. `prom_init()` initializes command line, machine type, environment, IO space, memory, UART base, and board NMI hook.

Control flow: Optional `LOONGSON_ADDRWINCFG_BASE` is ioremapped first. Firmware command line and machine type are parsed before environment and memory, then PCI IO is mapped and early serial base is initialized.

State and persistence: Establishes early global mappings and registers `board_nmi_handler_setup`. No dynamic teardown exists.

Dependencies and integration: Calls common firmware helpers plus Loongson local `prom_init_machtype`, `prom_init_env`, `prom_init_memory`, and `prom_init_uart_base`.

Risks: Early ioremap failures are not checked. UART and memory initialization depend on prior machtype and env parsing.

Test signals: Early console should work, memblock should contain firmware memory, and NMI setup should install a copied vector at the expected cacheable address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/init.c -->
