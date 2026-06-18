## sources/distributed-fs/ipfs-kubo/test/sharness/t0082-repo-gc-auto.sh

Purpose: stress-tests automatic garbage collection triggered by datastore storage limits and GC watermarks.

Important APIs and helpers: defines `check_ipfs_storage` and `test_gc`, uses `random-data`, `test_config_set Datastore.StorageMax`, `Datastore.StorageGCWatermark`, `Datastore.GCPeriod`, `disk_usage`, `ipfs add`, `ipfs pin rm`, and daemon lifecycle helpers.

Control flow and state: generates fixed-size data, configures a small `StorageMax` and aggressive GC period, adds and unpins data below and above the watermark, waits for periodic GC, and repeats the GC scenario multiple times to surface timing failures. Storage state is the blockstore size under `$IPFS_PATH/blocks`.

Dependencies and integration points: covers daemon background GC scheduling, datastore accounting, pin removal, blockstore cleanup, and platform-specific disk usage tolerances.

Risks and test signals: catches auto-GC that never fires, fires too early, or leaves storage above watermark. The pass signal is disk usage below expected thresholds after unpinned data crosses configured limits.
