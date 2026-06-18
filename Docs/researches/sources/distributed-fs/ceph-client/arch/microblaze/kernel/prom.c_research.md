# sources/distributed-fs/ceph-client/arch/microblaze/kernel/prom.c

Purpose: performs early device-tree scanning for MicroBlaze boot.

Important APIs and state: `early_init_devtree(void *params)` calls `early_init_dt_scan(params, __pa(params))`, copies `cmd_line` into `boot_command_line` when needed, and enables memblock resizing.

Control flow: called after early BSS clearing and FDT staging. It logs entry/exit and physical memory size for debugging.

State and persistence: initializes global OF/memblock boot state and possibly `boot_command_line`.

Dependencies and integration: called from `machine_early_init()` in setup; depends on `_fdt_start` or a bootloader-provided FDT having been copied by `head.S`.

Risks and test signals: invalid FDT pointer breaks memory discovery and all OF probing. Test external and linked DTB boot, boot command line fallback, and memblock memory region discovery.
