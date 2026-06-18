<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/lpddr/qinfo_probe.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/lpddr/qinfo_probe.c

Purpose: registers an MTD chip probe named `qinfo_probe` for LPDDR devices that expose QINFO records through a PFOW overlay window.

Important APIs, types, and functions: `struct mtd_chip_driver lpddr_chipdrv` calls `lpddr_probe()`. Helpers `lpddr_pfow_present()`, `lpddr_info_query()`, `lpddr_get_qinforec_pos()`, `lpddr_chip_setup()`, and `lpddr_probe_chip()` verify PFOW and populate `struct lpddr_private` and `struct qinfo_chip`.

Control flow: `lpddr_probe()` calls `lpddr_probe_chip()`, which bounds-checks `pfow_base`, reads the `PFOW` signature, allocates QINFO storage, reads manufacturer/device IDs and size/timing/features records, calculates virtual chip count from hardware partitions, and returns private chip state. The map's `fldrv_priv` is then passed to `lpddr_cmdset()` to create the MTD.

State and persistence: runtime state is the allocated `lpddr_private`, its QINFO table, chip count, chip shift, manufacturer ID, and device ID. No persistent state is written.

Dependencies and integration points: depends on map accessors, PFOW command/status registers, QINFO definitions, and the exported `lpddr_cmdset()` from `lpddr_cmds.c`. It registers/unregisters through `register_mtd_chip_driver()`.

Risks: query polling has a fixed 20-attempt microdelay loop and does not return an explicit timeout error. Unknown QINFO strings call `BUG()`. Allocation cleanup is incomplete on some early failure paths after `qinfo` allocation. Test signals are successful PFOW signature reads, correct QINFO-derived MTD size/erase/write sizes, visibility reduction when map size is smaller than chip size, and module unload unregistering the chip driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/lpddr/qinfo_probe.c -->
