<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_fdt.h -->
# sources/distributed-fs/ceph-client/include/linux/of_fdt.h

## Purpose
This header declares flattened Devicetree (FDT) boot-time and unflattening interfaces used before the live `device_node` tree exists.

## Important APIs, types, and functions
It defines `OF_DT_HEADER`, global early DT cell counts (`dt_root_addr_cells`, `dt_root_size_cells`), boot parameter pointers (`initial_boot_params`, physical address, `__dtb_start`, `__dtb_end`), and unflattening via `of_fdt_unflatten_tree()`. Early scan APIs include `of_scan_flat_dt()`, subnode scans, property lookup, address/size helpers, compatibility checks, phandle lookup, chosen/memory/stdout scans, reserved-memory reservation, root scan, verification, node scan, machine-name/match helpers, `unflatten_device_tree()`, `unflatten_and_copy_device_tree()`, `early_init_devtree()`, and `early_get_first_memblock_info()`.

## Control flow
Boot code verifies an FDT blob, scans flat nodes for root/chosen/memory/reserved-memory data, adds memory to architecture/memblock state, picks machine compatibility, and later unflattens the blob into `struct device_node` objects. Arbitrary FDT scans use callback iteration over node offsets. Disabled early-flat-tree support provides small no-op or `-ENODEV` stubs.

## State and persistence
Early global DT pointers and root cell widths persist through boot. Reserved-memory and memblock changes become system memory-management state. After unflattening, state moves into the live OF tree.

## Dependencies and integration points
It depends on init annotations, errno/types, FDT layout, architecture memory setup, memblock/reserved-memory code, and OF live-tree creation.

## Risks and test signals
Risks include invalid FDT headers, wrong physical/virtual pointer handling, cell-width misdecoding, memory range truncation, reserved memory being missed, and boot-order bugs before allocators are ready. Test early boot on DT platforms, malformed FDT rejection, `/chosen` cmdline/stdout parsing, memory node parsing, reserved-memory reservation, built-in DTB ranges, and `!CONFIG_OF_EARLY_FLATTREE` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_fdt.h -->
