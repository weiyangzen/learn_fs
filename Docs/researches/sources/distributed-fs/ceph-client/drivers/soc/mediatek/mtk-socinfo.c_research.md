# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-socinfo.c

## Purpose
This driver reads MediaTek efuse/nvmem cells to identify SoC variant and marketing name, then registers a Linux `soc_device` for userspace-visible SoC metadata.

## Important APIs, Types, and Functions
Key types are `struct mtk_socinfo` and `struct socinfo_data`. The lookup table `socinfo_data_table[]` maps up to two cell values to SoC name, segment name, and marketing name. Important functions are `mtk_socinfo_read_cell()`, `mtk_socinfo_get_socinfo_data()`, `mtk_socinfo_create_socinfo_node()`, `mtk_socinfo_probe()`, and `mtk_socinfo_remove()`.

## Control Flow and State
Probe allocates state, reads `socinfo-data1` and optional `socinfo-data2` from the parent nvmem device, matches the values against the static table, registers a `soc_device_attribute`, stores drvdata, and unregisters the soc device on remove. Persistent state is the registered soc device and pointer to static table data.

## Dependencies and Integration Points
The driver depends on being created as an nvmem child device, `nvmem_device_find()`, OF child cell nodes with `reg` offsets, the SoC bus API, and platform driver registration. Userspace consumes the result through the standard SoC device sysfs hierarchy.

## Risks and Test Signals
Risks include incomplete table coverage, partial-cell matching when fewer cells are present, ignoring `nvmem_device_read()` return status, and unused `segment_name` in registered attributes. Test signals include known efuse values on supported chips, unknown-ID warnings, soc bus sysfs content, nvmem read failure injection, and remove/reprobe cleanup.
