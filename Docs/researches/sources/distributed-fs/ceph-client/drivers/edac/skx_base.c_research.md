# sources/distributed-fs/ceph-client/drivers/edac/skx_base.c

Purpose: `skx_base.c` is the Skylake Xeon server EDAC front-end. It discovers the Skylake memory-controller PCI topology, registers each integrated memory controller with the EDAC core, provides the Skylake-specific physical-address decoder, and hooks the shared SKX MCE handler from `skx_common.c`.

Important APIs/types/functions: `skx_cfg` describes Skylake resources; `struct munit` and `skx_all_munits[]` describe required PCI functions; `get_all_munits()` populates `struct skx_dev`; `skx_get_dimm_config()` fills DIMM/NVDIMM metadata; `skx_show_retry_rd_err_log()` appends retry-log data; `skx_sad_decode()`, `skx_tad_decode()`, `skx_rir_decode()`, and `skx_mad_decode()` implement address translation.

Control flow: init rejects GHES ownership, conflicting EDAC ownership, hypervisors, and non-Skylake CPUs. It reads TOLM/TOHM, builds socket bus mappings, scans all required PCI units, registers one EDAC MC per IMC, sets manual and/or ADXL decode callbacks, initializes opstate/debugfs, and registers the MCE notifier. Exit unregisters notifier/debugfs, releases ADXL if needed, and calls `skx_remove()`.

State and persistence: module globals track `skx_edac_list`, TOLM/TOHM, socket count, and NVDIMM count. Per-IMC/channel/DIMM state is stored in shared `struct skx_dev` objects and rebuilt at probe; no disk persistence exists.

Dependencies/integration: x86 CPU matching, Intel PCI config registers, EDAC core, MCE notifier chain, GHES arbitration, common SKX helpers, and optional ADXL/debugfs.

Risks: PCI topology counts are strict, decode math is register-layout-sensitive, hidden controllers require mapping care, `nvdimm_count` is global across failures, and retry-log reporting assumes error-channel PCI devices are present.

Test signals: successful MC registration and DIMM labels on Skylake-X, ECC-disabled rejection, NVDIMM fallback behavior, hardware or debugfs-injected MCE decode, and failure-path cleanup.
