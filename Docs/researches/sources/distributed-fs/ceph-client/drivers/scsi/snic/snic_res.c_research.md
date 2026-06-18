# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_res.c

Purpose: this file reads SNIC vNIC configuration, discovers resource counts, allocates/frees WQ/CQ/interrupt resources, initializes rings and interrupt controls, clears stats, and logs queue errors.

Important APIs, types, and functions: `snic_get_vnic_config()` reads fields from firmware using `svnic_dev_spec()` and clamps descriptor counts, MTU, throttle, timeout, retry, LUN, and interrupt timer values. `snic_get_res_counts()` reads WQ/CQ/INTR resource counts. `snic_alloc_vnic_res()` allocates WQs, WQ CQs, firmware CQs, and interrupt controls, initializes each, dumps/clears stats, and rolls back on failure. `snic_free_vnic_res()` and `snic_log_q_error()` free resources and report WQ error status.

Control flow: probe calls config read, resource count discovery, MSI-X setup, then resource allocation. Allocation first creates WQ rings, then CQs, then INTR controls, then initializes hardware registers. On any failure, it frees all resources allocated so far.

State and persistence: runtime state includes `snic->config`, `wq_count`, `cq_count`, `intr_count`, `wq[]`, `cq[]`, `intr[]`, `stats`, and queue error MMIO registers. No persistent state exists.

Dependencies and integration: depends on vNIC resource/control headers, WQ/CQ/INTR allocation APIs, firmware-specific config structure `vnic_snic_config`, and stats dump/clear devcmds.

Risks: the code asserts exactly MSI-X mode and `cq_count == 2 * wq_count`. It assumes one WQ and one firmware CQ in other files. Firmware config values are clamped, but resource counts are trusted after nonzero assertions. Stats dump failure aborts resource allocation.

Test signals: probe against minimum/maximum config values, insufficient CQ/INTR resources, descriptor allocation failure, stats dump failure, queue error injection, and ring cleanup after partial allocation.
