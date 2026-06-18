# sources/distributed-fs/ceph-client/drivers/edac/x38_edac.c

Purpose: `x38_edac.c` is a legacy Intel X38 memory hub EDAC driver. It maps MCHBAR, derives rank/channel topology from DRB registers, polls ECC status/logs, and reports DDR2 CE/UE events.

Important APIs/types/functions: `how_many_channel()` detects channel mode; `x38_map_mchbar()` maps the MMR window; `x38_get_drbs()`, `x38_is_stacked()`, and `drb_to_nr_pages()` compute DIMM pages; polling is `x38_check()` through `x38_get_and_clear_error_info()` and `x38_process_error_info()`; lifecycle is `x38_probe1()`, `x38_init_one()`, `x38_remove_one()`, `x38_init()`, and `x38_exit()`.

Control flow: init sets opstate, registers PCI driver, and has a fallback manual probe. Probe enables PCI, maps MCHBAR, reads DRBs, allocates chip-select/channel EDAC layers, fills DIMM sizes, clears stale status, and registers the MC. Polling snapshots status/logs, handles CE-overwritten-by-UE races, clears status, and emits EDAC events.

State and persistence: global channel count and fallback PCI state coordinate one controller. The MCHBAR mapping is stored in `mci->pvt_info`. Runtime state is rebuilt at probe and freed at unload.

Dependencies/integration: Intel X38 PCI ID, PCI config access, non-atomic 64-bit MMIO read helper, EDAC polling, and `edac_op_state` module parameter.

Risks: global channel count limits multi-controller assumptions; `pvt_info` is used unconventionally; fallback binding complicates references; error registers cannot be atomically captured; DIMM type/mode metadata is approximate.

Test signals: X38 hardware load, channel detection, DRB size calculations, polling CE/UE reports, overwrite-race path, MCHBAR failure, and normal/fallback unload.
