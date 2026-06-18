
# sources/distributed-fs/ceph-client/drivers/crypto/virtio/virtio_crypto_mgr.c

Purpose: global manager for virtio crypto devices and algorithm registration notifications.

Important APIs, types, and functions: file-static `virtio_crypto_table`, `num_devices`, and `table_lock` track up to `VIRTIO_CRYPTO_MAX_DEVICES`. `virtcrypto_devmgr_add_dev()` / `virtcrypto_devmgr_rm_dev()` add and remove devices. `virtcrypto_dev_get()` / `virtcrypto_dev_put()` manage per-device reference counts and module references. `virtcrypto_get_dev_node()` finds the least-used compatible started device near a NUMA node. `virtcrypto_dev_start()` and `virtcrypto_dev_stop()` register/unregister skcipher and akcipher algorithms. `virtcrypto_algo_is_supported()` checks service/algo bitmaps.

Control flow: probe adds devices to the table before queue setup. When hardware status becomes ready, `virtcrypto_dev_start()` registers algorithm families if supported. Algorithm setkey paths call `virtcrypto_get_dev_node()`, which scans same-node devices, falls back to any started compatible device, unlocks, then bumps references. Stop unregisters algorithms for the device.

State and persistence: the global list and device count persist for module lifetime. Each device stores an atomic user count and module owner pointer. Algorithm tables in separate files retain active device counts.

Dependencies and integration points: depends on mutex/list/module APIs, virtio crypto UAPI service constants, and common header structures. It is the bridge between core device status and crypto API algorithm availability.

Risks and test signals: `virtcrypto_dev_get()` increments the atomic before `try_module_get()` and does not roll back on failure, which is a refcount consistency risk. `virtcrypto_get_dev_node()` calls `virtcrypto_dev_get()` after dropping `table_lock`, so removal concurrency relies on higher-level algorithm/device lifetime constraints. Algorithm bit checking shifts `1u << algo` after subtracting 32 for high algorithms and needs bounds validation. Test signals are max-device limit, duplicate add, NUMA selection, fallback selection, module refcount failure injection, hot-unplug while transforms hold refs, and high-number algorithm masks.
