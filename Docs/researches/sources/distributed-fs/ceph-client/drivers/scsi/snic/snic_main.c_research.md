# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_main.c

Purpose: this is the SNIC PCI/SCSI driver entry point. It registers the PCI driver, creates global state, probes/removes adapters, configures the SCSI host template, and orchestrates vNIC, firmware, interrupt, mempool, debugfs, and discovery lifecycle.

Important APIs, types, and functions: `snic_host_template` wires queuecommand, SCSI EH abort/device reset/host reset callbacks, device init/configure callbacks, queue depth changes, host attributes, and command private size. `snic_probe()` is the main initialization path. `snic_remove()` performs teardown. `snic_global_data_init()` creates global request slab caches, event workqueue, and optional debugfs/trace. Module init/exit register and unregister the PCI driver.

Control flow: probe allocates `Scsi_Host`, enables PCI, requests BARs, sets DMA mask, maps BAR0, discovers vNIC resources, initializes devcmd2, opens and initializes the vNIC, reads vNIC config, configures queue limits and resource counts, sets MSI-X, allocates rings/interrupts, initializes locks and mempools, sets notify buffer, adds the adapter to the global list, enables WQs and vNIC, requests/unmasks interrupts, exchanges firmware version, adds the SCSI host, marks online, and starts discovery. Remove marks offline, stops link events, drains work, marks `in_remove`, cleans queues and SCSI commands, removes targets, removes debugfs and host, unregisters notify/interrupt/resources/vNIC/BAR/PCI, and drops the host.

State and persistence: global runtime state is `snic_glob`; per-adapter runtime state is `struct snic`. Module parameters include `snic_log_level`, `snic_max_qdepth`, and optional `snic_trace_max_pages`. No persistent storage is written.

Dependencies and integration: integrates Linux PCI, SCSI mid-layer, block queue timeout configuration, vNIC devcmd/resources, SNIC discovery/SCSI/control/ISR files, mempools/slab caches, workqueues, and debugfs.

Risks: the probe path is long with many cleanup labels; ordering mistakes can leak resources or use uninitialized debugfs handles. Debugfs per-host init happens before PCI enable, so early probe failures rely on cleanup. `snic_del_host()` returns early if `work_q` is null and then does not call `scsi_remove_host()`, which matters for partially added hosts. The driver taints non-x86_64 instead of refusing load. Only one hardware shape and MSI-X mode are effectively supported.

Test signals: test successful probe/remove, every probe failure label via fault injection, module unload with active I/O, firmware exchange timeout, discovery failure after host add, sysfs/debugfs lifetime, non-default queue depth, and SCSI EH host reset.
