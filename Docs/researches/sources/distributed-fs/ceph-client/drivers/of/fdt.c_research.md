# sources/distributed-fs/ceph-client/drivers/of/fdt.c

## Purpose
`fdt.c` handles flattened devicetree boot-time processing and conversion to live `struct device_node` trees. It verifies and stores the boot FDT, scans early memory and `/chosen` metadata, reserves FDT and memreserve regions, unflattens nodes/properties, publishes raw FDT sysfs data, and supports built-in empty-root fallback.

## Important APIs, types, and functions
Important APIs include `of_fdt_limit_memory()`, `of_fdt_device_is_available()`, `__unflatten_device_tree()`, `of_fdt_unflatten_tree()`, `early_init_fdt_scan_reserved_mem()`, `early_init_fdt_reserve_self()`, `of_scan_flat_dt()`, `of_scan_flat_dt_subnodes()`, `of_get_flat_dt_prop()`, `of_flat_dt_get_addr_size()`, `of_flat_dt_match_machine()`, `early_init_dt_scan_root()`, `dt_mem_next_cell()`, `early_init_dt_scan_memory()`, `early_init_dt_scan_chosen()`, `early_init_dt_verify()`, `early_init_dt_scan_nodes()`, `early_init_dt_scan()`, `unflatten_device_tree()`, and `unflatten_and_copy_device_tree()`.

## Control flow and state
`early_init_dt_verify()` validates the FDT header, records `initial_boot_params` and physical address, computes a CRC, and reads root cell counts. `early_init_dt_scan_nodes()` reads `/chosen`, memory nodes, usable-memory ranges, and kexec handover metadata before the live tree exists. Memory parsing adds page-aligned regions to memblock and marks hotpluggable memory.

Unflattening is two-pass: `unflatten_dt_nodes()` first sizes allocations, then populates `device_node` and `property` structures from FDT offsets. Missing `name` properties are synthesized from unit names. Child lists are reversed after creation to restore `.dts` order. `unflatten_device_tree()` runs reserved-memory late initialization first, unflattens into `of_root`, scans aliases/chosen/stdout, and initializes unittest overlay base data.

## Dependencies and integration
The file integrates with libfdt, memblock, initrd, crash dump, dm-crypt crash keys, random seed consumption, earlycon, kexec handover, sysfs firmware files, and reserved-memory scanning in `of_reserved_mem.c`.

## Risks and test signals
Risks include invalid FDT headers, property size mismatches, depth overflows, skipped disabled nodes when `CONFIG_OF_KOBJ` is off, CRC mismatch preventing `/sys/firmware/fdt`, early memory alignment truncation, and security-sensitive seed wiping. KUnit `of_dtb` root tests, boot logs, memblock maps, earlycon startup, and raw-FDT sysfs presence are key signals.
