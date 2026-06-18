<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/hw-consumer.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/hw-consumer.h

Purpose: Declares a small consumer API for enabling and disabling hardware-backed IIO consumers.

Important APIs/types/functions: Opaque `struct iio_hw_consumer`; allocation/free APIs `iio_hw_consumer_alloc()`, `iio_hw_consumer_free()`, and managed `devm_iio_hw_consumer_alloc()`; runtime control APIs `iio_hw_consumer_enable()` and `iio_hw_consumer_disable()`.

Control flow: Consumers allocate a handle for a device, enable the associated hardware route when needed, then disable and release it. Managed allocation ties cleanup to device lifetime.

State/persistence: State is hidden behind the opaque handle; this header owns no fields. Enabled hardware state persists until disabled or devres cleanup.

Dependencies/integration: Integrates with the device model and IIO consumer/provider mapping internals.

Risks: Enable/disable imbalance may leave hardware active or consumers unavailable.

Test signals: Probe/remove with devm cleanup, repeated enable/disable, and error injection for missing provider mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/hw-consumer.h -->
