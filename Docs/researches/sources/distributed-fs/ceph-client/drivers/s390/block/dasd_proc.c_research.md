# sources/distributed-fs/ceph-client/drivers/s390/block/dasd_proc.c

Purpose: provides the legacy `/proc/dasd` interface, listing DASD devices and exposing global profiling statistics controls/output when profiling is configured.

Important APIs/types/functions: `dasd_devices_show()` is the seq-file renderer for `/proc/dasd/devices`; `dasd_devices_seq_ops` iterates devindices; profile helpers switch all block profiles on/off/reset; `dasd_stats_proc_show()` prints histograms; `dasd_stats_proc_write()` parses `set on`, `set off`, and `reset`; `dasd_proc_init()`/`exit()` create/remove proc entries.

Control flow: proc init creates `/proc/dasd`, `devices`, and `statistics`. Device listing iterates up to `dasd_max_devindex`, obtains referenced devices, prints ccw name, discipline, major/minor, disk name, features, and state/capacity. Statistics reads snapshot the global profile under lock; writes parse a bounded copied string and update global plus per-block profile state.

State and persistence behavior: proc files are runtime-only. Writing statistics toggles in-memory profiling and resets counters; it does not persist configuration across boot. Device listing reflects live DASD state and devmap configuration.

Dependencies and integration points: integrates with DASD devmap lookup, profile support in `dasd.c`, procfs/seq_file, user-copy helpers, and the global `dasd_probeonly`/`dasd_max_devindex` knobs.

Risks and test signals: profile writes can partially enable block profiles before a later failure, so rollback behavior matters. Device iteration must drop references on every path. Test with holes in devindex space, devices without `block`/`gdp`, `CONFIG_DASD_PROFILE=n`, oversized writes, parse errors, and concurrent online/offline while reading proc files.
