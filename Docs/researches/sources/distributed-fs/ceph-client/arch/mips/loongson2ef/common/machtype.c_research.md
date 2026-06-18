<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/machtype.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/machtype.c

Purpose: Determines and exposes the Loongson2EF machine type string used by board selection, serial setup, reset, suspend, and platform drivers.

Important APIs/types/functions: `get_system_type()` returns `system_types[mips_machtype]`. Weak `mach_prom_init_machtype()` lets board code infer machine type. `prom_init_machtype()` parses `machtype=` from `arcs_cmdline`.

Control flow: Starts from `LOONGSON_MACHTYPE`, optionally lets board code refine it, then if `machtype=` is present compares the argument as a substring against supported system type names.

State and persistence: Writes global `mips_machtype` once during early boot.

Dependencies and integration: `serial.c`, `uart_base.c`, `lemote-2f/reset.c`, and suspend logic switch on `mips_machtype`.

Risks: Substring matching can accept ambiguous fragments. `get_system_type()` assumes the machine type index is in range.

Test signals: Passing `machtype=` should select the expected board; boot logs and `/proc/cpuinfo` system type should match hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/machtype.c -->
