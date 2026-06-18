# sources/distributed-fs/ceph-client/include/linux/raid/detect.h

Purpose: declares Linux MD RAID autodetection hooks used by block-device discovery and early setup.

Important APIs and types: `md_autodetect_dev(dev_t dev)` records a block device for MD autodetection. `md_run_setup()` is available when `CONFIG_BLK_DEV_MD` is enabled and becomes an inline no-op otherwise.

Control flow: early block-device probing can call `md_autodetect_dev()` for candidate devices; later setup calls `md_run_setup()` to assemble detected arrays when MD support is built.

State and persistence: this header stores no state. The MD subsystem owns any autodetect lists and assembled array state; persistence is on-disk RAID metadata.

Dependencies and integration points: integrates device-number based block discovery with the MD driver and init/setup paths.

Risks and test signals: risks include no-op behavior in non-MD builds, duplicate/autodetect ordering issues, and stale device-number assumptions during early boot. Test builds with and without `CONFIG_BLK_DEV_MD`, boot-time autodetection of legacy MD arrays, duplicate candidates, and degraded arrays.
