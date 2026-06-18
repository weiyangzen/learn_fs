## sources/distributed-fs/openafs/src/afs/LINUX/osi_sysctl.c

Purpose: exposes selected OpenAFS runtime tuning and statistics variables through Linux `sysctl` when `CONFIG_SYSCTL` is enabled.

Important APIs and state: defines `osi_sysctl_init(void)` and `osi_sysctl_clean(void)`. The central table `afs_sysctl_table[]` maps integer variables such as `hm_retry_RO`, `hm_retry_RW`, `hm_retry_int`, `afs_gcpags`, `afs_rx_deadtime`, `afs_bkvolpref`, cache block counters, cache percentage watermarks, `afs_cacheBlocks`, `afs_md5inum`, and `afs_usednlc`. The macros `AFS_SYSCTL_INT`, `AFS_SYSCTL_INT2`, `AFS_SYSCTL_NAME`, and `AFS_SYSCTL_SENTINEL` hide kernel API differences, including numbered vs unnumbered ctl tables and the Linux 6.8 no-sentinel convention.

Control flow: initialization registers either an `"afs"` subtree with `register_sysctl("afs", ...)` or a legacy `fs/afs` table with `register_sysctl_table`. On failure it returns `-1`; on success it stores the `ctl_table_header` in `afs_sysctl`. Cleanup unregisters that header once and clears the pointer.

Dependencies and integration: depends on Linux `<linux/sysctl.h>`, OpenAFS global cache/stat variables, and compile-time kernel feature probes. It integrates with administrator observability and runtime tuning via `/proc/sys`/sysctl.

State and persistence: sysctl entries directly expose live kernel variables; writes mutate in-memory OpenAFS behavior and do not persist across module unload or reboot unless userspace reapplies them.

Risks: permissions matter because many entries are `0644`; writable sysctl values can change cache behavior and retry policy. Kernel API drift is also a risk, handled here with feature macros and the Linux 6.8 sentinel branch. Missing cleanup would leave stale sysctl entries.

Test signals: verify table registration on supported kernels, read-only vs writable permissions, successful updates of writable knobs, cleanup after module unload, and builds across `HAVE_LINUX_REGISTER_SYSCTL`, `REGISTER_SYSCTL_TABLE_NOFLAG`, and Linux 6.8+ configurations.
