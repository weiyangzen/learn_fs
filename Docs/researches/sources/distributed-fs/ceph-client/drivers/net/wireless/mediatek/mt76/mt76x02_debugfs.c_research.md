<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_debugfs.c

Purpose: debugfs surface for mt76x02 runtime diagnostics and EDCCA control. It exposes queue, AMPDU, DFS, power, rate-power, AGC, temperature, TPC, and watchdog counters.

Important APIs/types/functions: `mt76x02_init_debugfs()`, show helpers for AMPDU/DFS/rate power/AGC/txpower, and `fops_edcca` backed by `mt76_edcca_get()`/`mt76_edcca_set()`.

Control flow: initialization registers the common mt76 debugfs directory, then adds seqfiles and scalar debugfs entries. EDCCA writes take the mt76 mutex, update `ed_monitor_enabled`, enable actual monitoring only for ETSI DFS region, and reinitialize EDCCA hardware state.

State and persistence: debugfs reflects live kernel memory only. Mutable knobs are `enable_tpc` and `ed_monitor_enabled`; counters read calibration, DFS, aggregate, and watchdog state.

Dependencies/integration: depends on Linux debugfs/seq_file, mt76 debugfs registration, mt76 queue readers, mt76x02 DFS/EDCCA/calibration state, and device driver data on the dentry.

Risks: debugfs writes race with channel/regulatory transitions if locking is incomplete; EDCCA behavior is region-dependent; stats can be misleading after reset. Test signals include debugfs file creation, read stability during traffic, EDCCA toggling in ETSI vs non-ETSI regions, and watchdog reset counter visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_debugfs.c -->
