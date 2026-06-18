# sources/distributed-fs/ceph-client/include/linux/pstore_blk.h

Purpose: declares the pstore block-device backend interface and configuration structure built on top of pstore/zone.

Important APIs and types: `struct pstore_device_info` carries supported frontend flags and embedded `pstore_zone_info`. `register_pstore_device()` and `unregister_pstore_device()` manage a pstore block backend device. `struct pstore_blk_config` stores target device name, max kmsg reason, and per-frontend storage sizes. `pstore_blk_get_config()` returns the active configuration.

Control flow: a block-oriented backend fills zone operations and registers a `pstore_device_info`; pstore/blk code uses the zone layer to divide storage among kmsg, pmsg, console, and ftrace areas. Configuration can be queried by other code for diagnostics.

State and persistence: persistent records live on the configured block device/zone area. Runtime config records device name and partition sizes.

Dependencies and integration points: depends on pstore core and pstore_zone. It integrates block devices with persistent crash logging.

Risks and test signals: risks include mis-sized zones, wrong frontend flags, device path changes, and config query races during unregister. Test registration/unregistration, storage layout for each frontend size, block device removal, and config reporting.
