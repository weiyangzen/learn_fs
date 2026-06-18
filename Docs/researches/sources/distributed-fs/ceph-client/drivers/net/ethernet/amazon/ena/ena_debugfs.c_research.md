# sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_debugfs.c

Purpose: this optional file creates ENA debugfs entries when `CONFIG_DEBUG_FS` is enabled. It currently exposes PHC statistics for a netdev under a debugfs directory named after the PCI device.

Important APIs, types, and functions: `phc_stats_show()` prints PHC counters from `adapter->ena_dev->phc.stats` if PHC is active. `DEFINE_SHOW_ATTRIBUTE(phc_stats)` creates file operations. `ena_debugfs_init()` creates the per-device directory and `phc_stats` file. `ena_debugfs_terminate()` removes the directory recursively.

Control flow: the netdev layer calls init during adapter setup and terminate during teardown. Reading `phc_stats` enters the seq-file show callback, checks `ena_phc_is_active()`, and prints `phc_cnt`, `phc_exp`, `phc_skp`, `phc_err_dv`, and `phc_err_ts`.

State and persistence: debugfs state is `adapter->debugfs_base`, which points to the created directory. The displayed counters live in `ena_com_phc_info.stats` and persist for the adapter lifetime. Debugfs files are runtime-only and disappear on teardown or unmount.

Dependencies and integration points: the file is compiled into `ena.o` but only emits code under `CONFIG_DEBUG_FS`. It depends on Linux debugfs/seq_file/Pci headers, `ena_debugfs.h`, `ena_netdev.h`, and PHC helpers from `ena_phc.h`.

Risks: `debugfs_create_dir()` and `debugfs_create_file()` errors are not checked, which is conventional for debugfs but means missing entries may be silent. Counter reads are not locked, so values are best-effort snapshots. If terminate is skipped, debugfs dentries could outlive adapter state; the recursive remove path should be paired with all teardown paths.

Test signals: with debugfs enabled and PHC active, `/sys/kernel/debug/<pci-dev>/phc_stats` should show all five counters. With PHC inactive, the file should read empty. Repeated probe/remove or devlink reload should create and remove entries without stale dentries.
