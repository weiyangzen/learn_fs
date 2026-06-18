# sources/distributed-fs/ceph-client/arch/sparc/kernel/prom_32.c

Purpose: supplies SPARC32-specific Open Firmware device-tree path construction, early allocation, console discovery, and stub CPU/IRQ device-tree hooks.

Important APIs/functions: implements `prom_early_alloc()`, `build_path_component()`, `of_console_init()`, `of_fill_in_cpu_data()`, and `irq_trans_init()`. Path helpers format node names for platform, SBUS, PCI, EBus, and LEON AMBA bus children.

Control flow: early allocation uses `memblock_alloc_or_panic()` and increments `prom_early_allocated`. `build_path_component()` dispatches by parent bus type and falls back to platform naming. `of_console_init()` handles PROM V0, V2, and V3 differently: V0 maps stdout enum values to display or serial nodes; V2 resolves stdout instance to package and appends tty suffixes; V3 uses root `stdout-path`. Fatal console discovery failures halt via PROM.

State and persistence: creates boot-time strings for `of_console_path` and records `of_console_device` and `of_console_options`. These are runtime device-tree/console state, not disk-persistent.

Dependencies and integration points: depends on `romvec`, PROM versioned callbacks, `prom_lock`, `restore_current()`, OF property helpers, LEON AMBA register formats, memblock, and shared globals from `prom_common.c`.

Risks: PROM versions have incompatible stdout interfaces. Path formatting relies on PROM `reg` property layouts and fixed temporary buffer sizes. Console failures are fatal very early in boot. The SPARC32 `irq_trans_init()` is intentionally empty, so platform IRQ setup must not assume the SPARC64 translator exists.

Test signals: boot on PROM V0/V2/V3 systems, serial and display console discovery, correct `/proc/device-tree` full names for SBUS/PCI/EBus/AMBA devices, and early boot halt on malformed stdout data.
