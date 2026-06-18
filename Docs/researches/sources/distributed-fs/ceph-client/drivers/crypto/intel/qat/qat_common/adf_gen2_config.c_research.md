## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_config.c

Purpose: Builds default kernel configuration sections for Gen2 QAT devices, including crypto and compression ring instances, ring sizes, ring numbers, coalescing timers, heartbeat settings, and configured status.

Important APIs/functions: `adf_gen2_dev_config()` is the exported entry point. It creates `ADF_KERNEL_SEC`, `Accelerator0`, and `ADF_GENERAL_SEC`, then calls `adf_gen2_crypto_dev_config()` and `adf_gen2_comp_dev_config()`. Crypto instances are limited by `min(num_online_cpus(), GET_MAX_BANKS())` when crypto capability exists; compression uses the same limit for compression-capable hardware. The generated keys include `ADF_NUM_CY`, `ADF_NUM_DC`, ring bank numbers, ring sizes, TX/RX ring ids, core affinity, and coalescing timer entries.

Control flow and state: All configuration is persisted through `adf_cfg_add_key_value_param()` in the device configuration database. On success the file saves the heartbeat timer default and sets `ADF_STATUS_CONFIGURED` in `accel_dev->status`. Any failure aborts with an error log and leaves partially-added config to the surrounding config cleanup path.

Dependencies/integration: Depends on `adf_cfg`, config key strings, crypto/compression capability helpers, transport ring macros, and heartbeat configuration. It is invoked by Gen2-specific device setup before service instances are created.

Risks and test signals: Ring ids are hard-coded for the Gen2 ring layout, so regressions appear as failed service instance creation or broken request routing. Tests should verify crypto-only, compression-only, combined, and no-capability devices; CPU count greater/less than bank count; key insertion failures; and that `ADF_STATUS_CONFIGURED` is only set after all sections and keys succeed.
