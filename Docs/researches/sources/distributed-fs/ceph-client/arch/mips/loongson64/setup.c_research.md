<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/setup.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/setup.c

Purpose: Performs Loongson64 platform memory setup from the selected FDT blob.

Important APIs/types/functions: Global `loongson_fdt_blob`; `plat_mem_setup()` calls `__dt_setup_arch()` when the blob is present.

Control flow: The FDT blob is selected during firmware env init; memory setup hands it to the OF/DT architecture setup code.

State and persistence: Publishes the device tree to the generic kernel DT subsystem.

Dependencies and integration: Depends on `env.c` selecting or fixing `loongson_fdt_blob`.

Risks: If no blob is selected, DT setup is skipped and later OF drivers may lack hardware descriptions.

Test signals: `/proc/device-tree` should exist on successful boot and reflect the selected Loongson64 built-in or firmware DTB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/setup.c -->
