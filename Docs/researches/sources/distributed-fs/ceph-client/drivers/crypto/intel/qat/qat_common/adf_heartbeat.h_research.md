# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_heartbeat.h

Purpose: defines heartbeat constants, status enum, DMA counter pair structure, driver heartbeat state, and public heartbeat APIs with debugfs/config build fallbacks.

Important types and APIs: `enum adf_device_heartbeat_status` reports unresponsive, alive, or unsupported. `struct hb_cnt_pair` stores response/request counters. `struct adf_heartbeat` stores counters, configured timer, last check/reset timestamps, DMA addresses, and debugfs dentries. Function declarations cover init/start/shutdown, timer conversion/config persistence, status checks, counter initialization, and optional error injection.

Control flow and state: state is per-`adf_accel_dev` through `accel_dev->heartbeat`. When `CONFIG_DEBUG_FS` is off, heartbeat init/start/save/check become no-ops, so callers can remain unconditional.

Dependencies and integration: used by lifecycle code in `adf_init.c`, heartbeat debugfs, error injection, and platform hooks that prefill/check counter memory.

Risks and test signals: build-configuration fallbacks can hide heartbeat coverage in non-debugfs builds. Test compile with and without `CONFIG_DEBUG_FS` and `CONFIG_CRYPTO_DEV_QAT_ERROR_INJECTION`, verify dentry lifecycle, and ensure `struct adf_heartbeat` fields are initialized before debugfs reads.
