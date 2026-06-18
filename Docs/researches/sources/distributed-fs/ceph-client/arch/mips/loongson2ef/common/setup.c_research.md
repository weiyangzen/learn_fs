<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/setup.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/setup.c

Purpose: Supplies Loongson2EF memory setup and write-buffer flush hook.

Important APIs/types/functions: `wbflush_loongson()` issues a MIPS3 `sync`; exported `__wbflush` points to it. `plat_mem_setup()` calls `loongson2ef_pcibios_init()`.

Control flow: At platform memory setup, PCI resources and mappings are initialized. The write-buffer flush pointer is initialized statically.

State and persistence: Exports a global function pointer used by MIPS write-buffer flush paths.

Dependencies and integration: Integrates Loongson PCI setup with the generic MIPS platform setup sequence.

Risks: The inline assembly mode changes must be accepted by all configured assemblers/CPUs.

Test signals: PCI initialization should happen during `plat_mem_setup`; drivers using `wbflush()` should execute a sync without fault.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/setup.c -->
