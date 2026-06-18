# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_compression.h

Purpose: declares the per-instance state used by the QAT compression service and provides a capability helper for devices that expose compression.

Important APIs and types: `QAT_COMP_MAX_SKID` fixes the shared overflow/skid buffer size at 4096 bytes. `struct qat_compression_instance` contains DC TX/RX rings, owning `adf_accel_dev`, list linkage, state/id/refcount fields, per-instance backlog, and shared `adf_dc_data`. `adf_hw_dev_has_compression()` tests `accel_capabilities_mask` for `ADF_ACCEL_CAPABILITIES_COMPRESSION`.

Control flow and integration: this header is consumed by `qat_compression.c` and compression algorithm code. Algorithms obtain a `qat_compression_instance`, use its `dc_tx`/`dc_rx` rings and backlog, then return it through the exported put path. The capability helper is intended for higher-level service/config checks before enabling compression algorithms.

State and persistence: the header does not allocate state, but it defines the fields that survive across compression requests for an accelerator service lifetime. The `dc_data` pointer is shared from `accel_dev->dc_data`; the per-instance backlog is protected by its own spinlock.

Dependencies: includes Linux list/types, `adf_accel_devices.h`, and `qat_algs_send.h` for backlog definitions. It assumes ADF hardware capability masks use set bits for unavailable capabilities after inverting the mask.

Risks and test signals: callers must not assume the helper checks extended ZSTD/LZ4S capabilities; that filtering lives in `qat_compression_get_instance_node()`. Tests should validate capability-mask polarity and ensure users of `qat_compression_instance` respect refcount and backlog locking rules.
